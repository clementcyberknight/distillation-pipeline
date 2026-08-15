"""Integration tests for the synthetic distillation pipeline."""

import json
import os
import tempfile
from pathlib import Path
import pytest

from config.schemas_and_seeds import SYSTEM_PROMPT, OutputSchemaType
from src.generator import BatchDistillationEngine, MockGenerator
from src.utils import DatasetWriter
from src.validator import DatasetValidator


def test_full_pipeline_mock_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "test_distillation_dataset.jsonl"
        quarantine_file = Path(tmpdir) / "test_quarantine.jsonl"

        writer = DatasetWriter(
            output_filepath=str(output_file),
            quarantine_filepath=str(quarantine_file),
            system_prompt=SYSTEM_PROMPT,
        )
        validator = DatasetValidator(fuzzy_threshold=0.85)
        generator = MockGenerator()

        engine = BatchDistillationEngine(
            generator=generator,
            validator=validator,
            samples_per_schema=3,
            batch_size=5,
            min_temp=0.75,
            max_temp=0.85,
        )

        target_schemas = [
            OutputSchemaType.GENERATIVE_CHART.value,
            OutputSchemaType.DOCUMENT_OUTPUT.value,
            OutputSchemaType.RED_FLAG_ALERT.value,
        ]

        for schema_type in target_schemas:
            for val_res in engine.run_schema_generation(schema_type, target_count=3):
                if val_res.is_valid:
                    writer.write_sample(
                        user_query=val_res.cleaned_user_query,
                        response=val_res.cleaned_response,
                    )
                else:
                    writer.write_rejected(
                        raw_output=val_res.cleaned_response or val_res.error_reason,
                        error_code=val_res.error_code,
                        error_reason=val_res.error_reason,
                        expected_type=schema_type,
                    )

        assert output_file.exists()
        lines = output_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 9  # 3 per schema * 3 schemas

        # Verify each line adheres to exact fine-tuning structure
        for line in lines:
            data = json.loads(line)
            assert "system_prompt" in data
            assert data["system_prompt"] == SYSTEM_PROMPT
            assert "user_query" in data
            assert isinstance(data["user_query"], str)
            assert "response" in data
            assert "output_type" in data["response"]
            assert data["response"]["output_type"] in target_schemas
