"""Synthetic Data Generator Engine using llama-cpp-python.

Orchestrates:
- CPU-optimized Llama-cpp initialization (n_threads=5, n_ctx=4096).
- Format-by-format batch generation with dynamic temperature variation (0.75 - 0.85).
- ChatML prompt synthesis with domain injection and few-shot seed exemplars.
- Built-in Mock Generator for offline testing and verification without weights.
"""

import json
import logging
import random
import time
from typing import Any, Dict, Generator, List, Optional

from config.schemas_and_seeds import (
    BUSINESS_VERTICALS,
    DOMAIN_CONTEXTS,
    OUTPUT_SCHEMAS,
    SEED_EXAMPLES,
    SYSTEM_PROMPT,
    OutputSchemaType,
)
from src.validator import DatasetValidator, ValidationResult

logger = logging.getLogger("distillation.generator")

try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False
    Llama = None


class BaseGenerator:
    """Base interface for synthetic data generators."""

    def generate_single(
        self,
        output_type: str,
        domain_context: Dict[str, str],
        seed_examples: List[Dict[str, Any]],
        temperature: float,
    ) -> str:
        raise NotImplementedError

    def close(self) -> None:
        pass


class LlamaCppGenerator(BaseGenerator):
    """Engine orchestrating llama-cpp-python execution on CPU / VPS hardware."""

    def __init__(
        self,
        model_path: str,
        n_threads: int = 5,
        n_ctx: int = 4096,
        n_batch: int = 512,
        n_gpu_layers: int = 0,
        verbose: bool = False,
    ):
        if not HAS_LLAMA_CPP:
            raise RuntimeError(
                "llama-cpp-python is not installed. Please run `pip install llama-cpp-python` "
                "or run the pipeline with `--mock`."
            )

        logger.info(
            f"Initializing Llama model from '{model_path}' with n_threads={n_threads}, "
            f"n_ctx={n_ctx}, n_batch={n_batch}, n_gpu_layers={n_gpu_layers}"
        )
        self.llm = Llama(
            model_path=model_path,
            n_threads=n_threads,
            n_ctx=n_ctx,
            n_batch=n_batch,
            n_gpu_layers=n_gpu_layers,
            verbose=verbose,
        )

    def _build_prompt(
        self,
        output_type: str,
        domain_context: Dict[str, str],
        seed_examples: List[Dict[str, Any]],
    ) -> str:
        """Constructs ChatML formatted generation prompt with few-shot seeds and schema definitions."""
        schema_def = OUTPUT_SCHEMAS.get(output_type, {})

        # Select 2 distinct seed examples for few-shot guidance
        sample_seeds = random.sample(seed_examples, min(2, len(seed_examples)))

        few_shot_text = ""
        for i, seed in enumerate(sample_seeds, 1):
            seed_json = json.dumps(
                {
                    "user_query": seed["user_query"],
                    "response": seed["response"],
                },
                indent=2,
            )
            few_shot_text += f"\nExample {i} ({seed.get('domain', 'Business')}):\n```json\n{seed_json}\n```\n"

        system_instruction = (
            "You are an expert AI Data Engineering teacher. Your task is to generate high-quality, "
            "realistic synthetic training data pairs for an offline desktop business assistant.\n"
            "Each generated sample MUST be a single valid JSON object containing exactly two keys:\n"
            "1. 'user_query': A natural, authentic question or command a business user would ask.\n"
            "2. 'response': A structured JSON object matching the exact target schema with 'output_type'.\n"
            "Do NOT include markdown conversational commentary outside the JSON object."
        )

        user_content = (
            f"Target Schema Output Type: {output_type}\n"
            f"Target Business Domain: {domain_context['domain']} - {domain_context['description']}\n\n"
            f"Target JSON Schema Definition:\n{json.dumps(schema_def, indent=2)}\n\n"
            f"High-Quality Seed Examples:\n{few_shot_text}\n\n"
            f"TASK: Generate 1 NEW, creative, highly realistic, non-duplicate query and response pair for "
            f"a business in '{domain_context['domain']}' matching the '{output_type}' schema.\n"
            f"Respond with ONLY the raw JSON object:"
        )

        prompt = (
            f"<|im_start|>system\n{system_instruction}<|im_end|>\n"
            f"<|im_start|>user\n{user_content}<|im_end|>\n"
            f"<|im_start|>assistant\n```json\n"
        )
        return prompt

    def generate_single(
        self,
        output_type: str,
        domain_context: Dict[str, str],
        seed_examples: List[Dict[str, Any]],
        temperature: float = 0.80,
    ) -> str:
        """Invokes Llama.cpp with dynamic temperature and context."""
        prompt = self._build_prompt(output_type, domain_context, seed_examples)

        output = self.llm(
            prompt,
            max_tokens=1024,
            temperature=temperature,
            top_p=0.90,
            repeat_penalty=1.1,
            stop=["<|im_end|>", "```\n\n", "<|im_start|>"],
            echo=False,
        )

        text = output["choices"][0]["text"].strip()
        # Add back json fence if needed for cleaner extraction
        if not text.startswith("```json") and not text.startswith("{"):
            text = "```json\n" + text
        if text.endswith("```"):
            pass
        return text

    def close(self) -> None:
        if hasattr(self, "llm") and self.llm:
            del self.llm


class MockGenerator(BaseGenerator):
    """Simulates realistic synthetic generation for local development, CI tests, and verification."""

    def __init__(self):
        logger.info("Initialized MockGenerator for offline testing without model weights.")
        self.counter = 0

    def generate_single(
        self,
        output_type: str,
        domain_context: Dict[str, str],
        seed_examples: List[Dict[str, Any]],
        temperature: float = 0.80,
    ) -> str:
        self.counter += 1
        # Pick a base seed example and synthesize variations
        seed = random.choice(seed_examples)
        base_query = seed["user_query"]
        base_response = json.loads(json.dumps(seed["response"]))  # deepcopy

        domain_name = domain_context["domain"].split("&")[0].strip()

        # Dynamic variation injection
        varied_query = f"[{domain_name} #{self.counter}] {base_query} (Ref: {random.randint(100, 999)})"

        if output_type == OutputSchemaType.GENERATIVE_CHART.value:
            base_response["title"] = f"{domain_name} Breakdown #{self.counter}"
            for ds in base_response.get("data", {}).get("datasets", []):
                ds["values"] = [v + random.randint(10, 500) for v in ds["values"]]

        elif output_type == OutputSchemaType.DOCUMENT_OUTPUT.value:
            base_response["doc_title"] = f"{domain_name} Operational Summary #{self.counter}"
            base_response["content"] = f"# {base_response['doc_title']}\n\nGenerated audit metrics for {domain_name} with ref {self.counter}.\n\n- Reconciled units\n- Verified balance."

        elif output_type == OutputSchemaType.CONVERSATIONAL_CHAT.value:
            base_response["message"] = f"Regarding {domain_name}: {base_response['message']} (Run index {self.counter})"

        elif output_type == OutputSchemaType.SHIFT_SCHEDULE.value:
            base_response["week_starting"] = "2026-09-21"
            for item in base_response.get("schedule", []):
                item["staff_id"] = f"STAFF_{random.randint(100, 999)}"

        elif output_type == OutputSchemaType.RED_FLAG_ALERT.value:
            base_response["transaction_id"] = f"TXN_{random.randint(10000, 99999)}"

        elif output_type == OutputSchemaType.AUTO_TASK.value:
            base_response["task_title"] = f"[{domain_name}] {base_response['task_title']} #{self.counter}"

        elif output_type == OutputSchemaType.TOOL_CALL.value:
            base_response["parameters"]["batch_id"] = self.counter

        synthetic_payload = {
            "user_query": varied_query,
            "response": base_response,
        }

        # Simulate 2% malformed generation to test validator error logging
        if self.counter % 45 == 0:
            return "Malformed text output with invalid json { "

        return f"```json\n{json.dumps(synthetic_payload, indent=2)}\n```"


class BatchDistillationEngine:
    """Coordinates batching, dynamic temperature variation, format iteration, and validation."""

    def __init__(
        self,
        generator: BaseGenerator,
        validator: DatasetValidator,
        samples_per_schema: int = 50,
        batch_size: int = 15,
        min_temp: float = 0.75,
        max_temp: float = 0.85,
        max_retries_per_batch: int = 3,
    ):
        self.generator = generator
        self.validator = validator
        self.samples_per_schema = samples_per_schema
        self.batch_size = max(1, min(batch_size, 50))
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.max_retries_per_batch = max_retries_per_batch

    def run_schema_generation(
        self,
        output_type: str,
        target_count: Optional[int] = None,
    ) -> Generator[ValidationResult, None, None]:
        """Generates valid items for a specific schema format using batched passes."""
        needed = target_count or self.samples_per_schema
        valid_collected = 0
        seeds = SEED_EXAMPLES.get(output_type, [])
        if not seeds:
            logger.error(f"No seeds found for schema {output_type}")
            return

        batch_idx = 0
        total_attempts = 0
        max_allowed_attempts = needed * 4  # Prevent infinite loops

        logger.info(f"Starting generation for schema '{output_type}' (Target: {needed} valid items)")

        while valid_collected < needed and total_attempts < max_allowed_attempts:
            batch_idx += 1
            # Vary temperature across batches between min_temp and max_temp
            batch_temp = round(random.uniform(self.min_temp, self.max_temp), 2)
            current_batch_size = min(self.batch_size, needed - valid_collected + 3)

            logger.debug(
                f"Batch #{batch_idx} for '{output_type}': generating {current_batch_size} samples "
                f"with temp={batch_temp} (Progress: {valid_collected}/{needed})"
            )

            for _ in range(current_batch_size):
                if valid_collected >= needed:
                    break

                total_attempts += 1
                domain = random.choice(DOMAIN_CONTEXTS)

                try:
                    raw_text = self.generator.generate_single(
                        output_type=output_type,
                        domain_context=domain,
                        seed_examples=seeds,
                        temperature=batch_temp,
                    )
                except Exception as e:
                    logger.warning(f"Generator exception on {output_type}: {e}")
                    yield ValidationResult(
                        is_valid=False,
                        error_code="GENERATION_EXCEPTION",
                        error_reason=str(e),
                    )
                    continue

                # Run multi-stage validation
                val_result = self.validator.validate_item(
                    raw_output=raw_text,
                    expected_output_type=output_type,
                    check_dedup=True,
                )

                if val_result.is_valid:
                    # Register valid query to prevent duplicate in future batches
                    self.validator.dedup_manager.add(val_result.cleaned_user_query)
                    valid_collected += 1

                yield val_result

        logger.info(f"Completed '{output_type}': {valid_collected}/{needed} valid samples generated.")
