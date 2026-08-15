#!/usr/bin/env python3
"""Main Entry Point for the Synthetic Data Distillation Engine.

Orchestrates:
1. Schema & Seed data loading.
2. Generator engine initialization (llama.cpp CPU / VPS or Mock).
3. Format-by-format batch distillation loop.
4. Multi-stage validation, deduplication, and quarantine logging.
5. Unified JSONL dataset persistence.
"""

import argparse
import os
import signal
import sys
import time
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeRemainingColumn

from config.schemas_and_seeds import (
    OUTPUT_SCHEMAS,
    SEED_EXAMPLES,
    SYSTEM_PROMPT,
    OutputSchemaType,
)
from src.generator import BatchDistillationEngine, LlamaCppGenerator, MockGenerator
from src.utils import DatasetWriter, setup_logger
from src.validator import DatasetValidator

console = Console()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Offline Synthetic Data Distillation Pipeline (Qwen2.5-7B -> Qwen2.5-1.5B)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Model & Engine Parameters
    parser.add_argument(
        "--model-path",
        type=str,
        default="models/qwen2.5-7b-instruct-q4_k_m.gguf",
        help="Path to downloaded GGUF teacher model weights on VPS.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=5,
        help="Number of CPU threads for llama.cpp (5 out of 6 vCPUs to prevent OS throttling).",
    )
    parser.add_argument(
        "--ctx-size",
        type=int,
        default=4096,
        help="Context window size (n_ctx).",
    )
    parser.add_argument(
        "--gpu-layers",
        type=int,
        default=0,
        help="Number of layers to offload to GPU (0 for pure CPU execution on VPS).",
    )

    # Generation & Batching Parameters
    parser.add_argument(
        "--samples-per-schema",
        type=int,
        default=1000,
        help="Number of valid synthetic examples to generate for each schema format (e.g. 1,000).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Batch size / set size per generation cycle (default: 20).",
    )
    parser.add_argument(
        "--min-temp",
        type=float,
        default=0.75,
        help="Lower bound for batch temperature variation.",
    )
    parser.add_argument(
        "--max-temp",
        type=float,
        default=0.85,
        help="Upper bound for batch temperature variation.",
    )
    parser.add_argument(
        "--fuzzy-threshold",
        type=float,
        default=0.85,
        help="Similarity threshold for fuzzy query deduplication (0.0 - 1.0).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Automatically resume and skip already generated samples in existing dataset file.",
    )
    parser.add_argument(
        "--no-resume",
        dest="resume",
        action="store_false",
        help="Do not resume; start generation from 0 for all schemas.",
    )

    # Output & Target Selection
    parser.add_argument(
        "--output-file",
        type=str,
        default="distillation_dataset.jsonl",
        help="Path to output JSONL dataset file.",
    )
    parser.add_argument(
        "--quarantine-file",
        type=str,
        default="logs/rejected_samples.jsonl",
        help="Path to quarantine log for discarded/malformed outputs.",
    )
    parser.add_argument(
        "--schemas",
        nargs="+",
        default=["all"],
        help="List of specific schema formats to generate, or 'all'.",
    )
    parser.add_argument(
        "--include-seeds",
        action="store_true",
        help="Append all 50 verified few-shot seed examples directly into the output dataset.",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in mock mode without loading GGUF model weights (for local testing/dry run).",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    logger = setup_logger()

    console.print(
        Panel.fit(
            "[bold cyan]Synthetic Data Distillation Engine[/bold cyan]\n"
            "[dim]Distilling Qwen2.5-7B-Instruct -> Qwen2.5-1.5B Training Dataset[/dim]\n"
            f"[yellow]Target Schemas:[/yellow] {', '.join(args.schemas)}\n"
            f"[yellow]Samples / Schema:[/yellow] {args.samples_per_schema} | "
            f"[yellow]Threads:[/yellow] {args.threads} | "
            f"[yellow]Batch Size:[/yellow] {args.batch_size} | "
            f"[yellow]Mock Mode:[/yellow] {'ENABLED' if args.mock else 'DISABLED'}",
            border_style="cyan",
        )
    )

    # 1. Resolve Target Schemas
    all_schemas = [s.value for s in OutputSchemaType]
    if "all" in [s.lower() for s in args.schemas]:
        target_schemas = all_schemas
    else:
        target_schemas = []
        for s in args.schemas:
            s_upper = s.upper()
            if s_upper in all_schemas:
                target_schemas.append(s_upper)
            else:
                console.print(f"[bold red]Unknown schema:[/bold red] '{s}'. Allowed: {', '.join(all_schemas)}")
                sys.exit(1)

    # 2. Initialize Writer & Validator
    writer = DatasetWriter(
        output_filepath=args.output_file,
        quarantine_filepath=args.quarantine_file,
        system_prompt=SYSTEM_PROMPT,
    )
    validator = DatasetValidator(fuzzy_threshold=args.fuzzy_threshold)

    # Pre-register seed queries for deduplication
    registered_seeds = validator.register_seed_examples(SEED_EXAMPLES)
    logger.info(f"Registered {registered_seeds} seed examples into deduplication index.")

    # 3. Resume & Existing Record Inspection
    existing_counts = {}
    if args.resume:
        existing_counts = writer.get_existing_records()
        loaded_existing = writer.populate_validator_from_existing(validator)
        if loaded_existing > 0:
            console.print(f"[bold cyan]Resuming pipeline:[/bold cyan] Detected {loaded_existing} existing records in {args.output_file}")
            for s_name, count in existing_counts.items():
                console.print(f"  - {s_name}: [green]{count}[/green] existing samples")

    # 4. Optionally include seed examples in output dataset if starting fresh
    if args.include_seeds and not existing_counts:
        console.print(f"[bold green]Appending {registered_seeds} seed examples to {args.output_file}...[/bold green]")
        for schema_type, seed_list in SEED_EXAMPLES.items():
            if schema_type in target_schemas:
                for seed in seed_list:
                    writer.write_sample(
                        user_query=seed["user_query"],
                        response=seed["response"],
                    )

    # 5. Initialize Generator Engine
    generator = None
    try:
        if args.mock:
            generator = MockGenerator()
        else:
            if not os.path.exists(args.model_path):
                console.print(
                    f"\n[bold red]ERROR: Model weights not found at '{args.model_path}'.[/bold red]\n"
                    f"Please download the GGUF model onto your VPS using `bash scripts/download_model.sh`\n"
                    f"or run with `--mock` flag for local verification without weights.\n"
                )
                sys.exit(1)

            generator = LlamaCppGenerator(
                model_path=args.model_path,
                n_threads=args.threads,
                n_ctx=args.ctx_size,
                n_gpu_layers=args.gpu_layers,
            )

        # 6. Initialize Batch Engine
        batch_engine = BatchDistillationEngine(
            generator=generator,
            validator=validator,
            samples_per_schema=args.samples_per_schema,
            batch_size=args.batch_size,
            min_temp=args.min_temp,
            max_temp=args.max_temp,
        )

        total_goal = len(target_schemas) * args.samples_per_schema
        total_already = sum(existing_counts.get(s, 0) for s in target_schemas)

        # Graceful Interrupt Handler
        def handle_sigint(signum, frame):
            console.print("\n[bold yellow]Pipeline interrupted by user. Finalizing and saving summary...[/bold yellow]")
            writer.display_summary_table()
            if generator:
                generator.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_sigint)

        # 7. Execute Format-by-Format Generation Loop
        console.print("\n[bold cyan]════════════════════════════════════════════════════════════════════[/bold cyan]")
        console.print(f"[bold green]Starting Automated Pipeline: Generating {args.samples_per_schema} samples per format in sets of {args.batch_size}[/bold green]")
        console.print("[bold cyan]════════════════════════════════════════════════════════════════════[/bold cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            total_task = progress.add_task("[cyan]Overall Progress across all formats[/cyan]", total=total_goal, completed=total_already)

            for schema_idx, schema_type in enumerate(target_schemas, 1):
                existing_for_schema = existing_counts.get(schema_type, 0)
                needed_for_schema = max(0, args.samples_per_schema - existing_for_schema)

                if needed_for_schema == 0:
                    console.print(f"[bold yellow]Format ({schema_idx}/{len(target_schemas)}): {schema_type}[/bold yellow] already has {existing_for_schema} valid samples. Skipping to next format.")
                    continue

                console.print(f"\n[bold magenta]▶ Processing Format ({schema_idx}/{len(target_schemas)}): {schema_type}[/bold magenta] (Target: {args.samples_per_schema}, Remaining: {needed_for_schema})")

                schema_task = progress.add_task(
                    f"[green]Current Format: {schema_type}[/green]",
                    total=args.samples_per_schema,
                    completed=existing_for_schema,
                )

                for val_result in batch_engine.run_schema_generation(schema_type, target_count=needed_for_schema):
                    if val_result.is_valid:
                        writer.write_sample(
                            user_query=val_result.cleaned_user_query,
                            response=val_result.cleaned_response,
                        )
                        progress.update(schema_task, advance=1)
                        progress.update(total_task, advance=1)
                    else:
                        writer.write_rejected(
                            raw_output=val_result.cleaned_response or val_result.error_reason,
                            error_code=val_result.error_code,
                            error_reason=val_result.error_reason,
                            expected_type=schema_type,
                        )

                progress.remove_task(schema_task)
                console.print(f"[bold green]✓ Completed Format {schema_type} ({args.samples_per_schema}/{args.samples_per_schema} valid samples)![/bold green]")
                if schema_idx < len(target_schemas):
                    console.print(f"[dim]Auto-switching to next format: {target_schemas[schema_idx]}...[/dim]\n")

        console.print("\n[bold green]✓ All Formats Successfully Completed and Validated![/bold green]\n")

    finally:
        if generator:
            generator.close()

    # 7. Print Final Metrics Summary
    writer.display_summary_table()
    console.print(f"[bold]Dataset saved to:[/bold] [underline]{os.path.abspath(args.output_file)}[/underline]")
    if writer.stats.total_rejected > 0:
        console.print(f"[bold yellow]Quarantine log:[/bold yellow] {os.path.abspath(args.quarantine_file)}")


if __name__ == "__main__":
    main()
