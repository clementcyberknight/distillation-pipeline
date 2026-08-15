"""Utility functions for dataset I/O, logging, and metrics tracking."""

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from config.schemas_and_seeds import SYSTEM_PROMPT

console = Console()


def setup_logger(log_dir: str = "logs", level: int = logging.INFO) -> logging.Logger:
    """Set up structured application logging with file and Rich console handlers."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(log_dir) / "generation.log"

    logger = logging.getLogger("distillation")
    logger.setLevel(level)

    # Avoid duplicate handlers if re-initialized
    if logger.handlers:
        return logger

    # File Handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    # Console Handler (Rich)
    rh = RichHandler(console=console, rich_tracebacks=True, show_path=False)
    rh.setLevel(level)
    logger.addHandler(rh)

    return logger


@dataclass
class GenerationStats:
    """Tracks running statistics for synthetic distillation generation."""
    start_time: float = field(default_factory=time.time)
    total_requested: int = 0
    total_generated: int = 0
    total_valid: int = 0
    total_rejected: int = 0
    schema_counts: Dict[str, int] = field(default_factory=dict)
    rejection_reasons: Dict[str, int] = field(default_factory=dict)

    def record_valid(self, output_type: str) -> None:
        self.total_valid += 1
        self.schema_counts[output_type] = self.schema_counts.get(output_type, 0) + 1

    def record_rejection(self, error_code: str) -> None:
        self.total_rejected += 1
        self.rejection_reasons[error_code] = self.rejection_reasons.get(error_code, 0) + 1

    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    @property
    def validity_rate(self) -> float:
        total = self.total_valid + self.total_rejected
        return (self.total_valid / total * 100) if total > 0 else 0.0

    @property
    def samples_per_minute(self) -> float:
        mins = self.elapsed_seconds / 60.0
        return (self.total_valid / mins) if mins > 0 else 0.0


class DatasetWriter:
    """Manages appending validated training samples to JSONL dataset and quarantine logs."""

    def __init__(
        self,
        output_filepath: str = "distillation_dataset.jsonl",
        quarantine_filepath: str = "logs/rejected_samples.jsonl",
        system_prompt: str = SYSTEM_PROMPT,
    ):
        self.output_path = Path(output_filepath)
        self.quarantine_path = Path(quarantine_filepath)
        self.system_prompt = system_prompt

        # Ensure parent directories exist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.quarantine_path.parent.mkdir(parents=True, exist_ok=True)

        self.stats = GenerationStats()
        self.output_file_handle = open(self.output_path, "a", encoding="utf-8")
        self.quarantine_file_handle = open(self.quarantine_path, "a", encoding="utf-8")

    def get_existing_records_and_populate(self, validator: Any) -> Dict[str, int]:
        """Reads existing output file and returns counts while populating deduplication index."""
        counts: Dict[str, int] = {}
        if not self.output_path.exists():
            return counts

        try:
            with open(self.output_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        q = obj.get("user_query")
                        if q:
                            validator.dedup_manager.add(q)
                        resp = obj.get("response", {})
                        out_type = resp.get("output_type")
                        if out_type:
                            counts[out_type] = counts.get(out_type, 0) + 1
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.warning(f"Could not parse existing dataset for resume: {e}")

        return counts

    def write_sample(self, user_query: str, response: Dict[str, Any]) -> None:
        """Write a single validated item in the unified fine-tuning format."""
        entry = {
            "system_prompt": self.system_prompt,
            "user_query": user_query,
            "response": response,
        }
        self.output_file_handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.output_file_handle.flush()

        output_type = response.get("output_type", "UNKNOWN")
        self.stats.record_valid(output_type)

    def write_rejected(
        self,
        raw_output: Any,
        error_code: Optional[str],
        error_reason: Optional[str],
        expected_type: Optional[str] = None,
    ) -> None:
        """Record discarded or malformed output to quarantine log."""
        entry = {
            "timestamp": time.time(),
            "expected_type": expected_type,
            "error_code": error_code or "UNKNOWN",
            "error_reason": error_reason or "Unspecified error",
            "raw_output": raw_output,
        }
        self.quarantine_file_handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.quarantine_file_handle.flush()

        self.stats.record_rejection(error_code or "UNKNOWN")

    def close(self):
        if hasattr(self, "output_file_handle") and self.output_file_handle:
            self.output_file_handle.close()
        if hasattr(self, "quarantine_file_handle") and self.quarantine_file_handle:
            self.quarantine_file_handle.close()

    def display_summary_table(self) -> None:
        """Render a formatted summary table of the generation run."""
        table = Table(title="[bold green]Synthetic Distillation Pipeline Summary[/bold green]")
        table.add_column("Output Schema", style="cyan", no_wrap=True)
        table.add_column("Valid Samples", justify="right", style="green")

        for schema_type, count in sorted(self.stats.schema_counts.items()):
            table.add_row(schema_type, str(count))

        table.add_section()
        table.add_row("[bold]Total Valid[/bold]", f"[bold green]{self.stats.total_valid}[/bold green]")
        table.add_row("[bold]Total Discarded[/bold]", f"[bold red]{self.stats.total_rejected}[/bold red]")
        table.add_row("[bold]Pass Rate[/bold]", f"{self.stats.validity_rate:.1f}%")
        table.add_row("[bold]Elapsed Time[/bold]", f"{self.stats.elapsed_seconds:.1f}s")
        table.add_row("[bold]Throughput[/bold]", f"{self.stats.samples_per_minute:.1f} samples/min")

        console.print(table)

        if self.stats.rejection_reasons:
            rej_table = Table(title="[bold yellow]Rejection Reasons Breakdown[/bold yellow]")
            rej_table.add_column("Error Code", style="yellow")
            rej_table.add_column("Count", justify="right", style="red")
            for code, cnt in sorted(self.stats.rejection_reasons.items(), key=lambda x: x[1], reverse=True):
                rej_table.add_row(code, str(cnt))
            console.print(rej_table)
