"""Tests verifying schema compliance for all 50 seed examples across 10 output types."""

import pytest
from config.schemas_and_seeds import (
    OUTPUT_SCHEMAS,
    SEED_EXAMPLES,
    OutputSchemaType,
)
from src.validator import DatasetValidator, SCHEMA_MODELS


def test_schema_coverage():
    """Ensure all 10 target schemas are defined in enums and have seed examples."""
    all_enum_types = [t.value for t in OutputSchemaType]
    assert len(all_enum_types) == 10

    for schema_type in all_enum_types:
        assert schema_type in OUTPUT_SCHEMAS, f"Missing JSON schema for {schema_type}"
        assert schema_type in SEED_EXAMPLES, f"Missing seeds for {schema_type}"
        assert schema_type in SCHEMA_MODELS, f"Missing Pydantic model for {schema_type}"
        assert len(SEED_EXAMPLES[schema_type]) == 5, f"Expected exactly 5 seeds for {schema_type}, got {len(SEED_EXAMPLES[schema_type])}"


def test_all_seeds_pass_strict_validation():
    """Verify that every single seed example passes the DatasetValidator without errors."""
    validator = DatasetValidator(fuzzy_threshold=0.99)

    total_validated = 0
    for schema_type, seed_list in SEED_EXAMPLES.items():
        for i, seed in enumerate(seed_list, 1):
            raw_payload = {
                "user_query": seed["user_query"],
                "response": seed["response"],
            }
            res = validator.validate_item(raw_payload, expected_output_type=schema_type, check_dedup=False)

            assert res.is_valid, f"Seed #{i} for {schema_type} failed validation: {res.error_code} - {res.error_reason}"
            assert res.cleaned_user_query == seed["user_query"]
            assert res.cleaned_response["output_type"] == schema_type
            total_validated += 1

    assert total_validated == 50, f"Expected 50 validated seed examples, got {total_validated}"
