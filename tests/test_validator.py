"""Unit tests for the validation, JSON extraction, and deduplication engine."""

import pytest
from src.validator import (
    DatasetValidator,
    DeduplicationManager,
    clean_and_extract_json,
)


def test_clean_and_extract_json():
    # 1. Clean fenced JSON
    fenced = "```json\n{\"output_type\": \"CONVERSATIONAL_CHAT\", \"message\": \"Hello world\"}\n```"
    res = clean_and_extract_json(fenced)
    assert res is not None
    assert res["output_type"] == "CONVERSATIONAL_CHAT"

    # 2. Text with preamble and trailing comma
    messy = "Here is the response:\n{\n  \"output_type\": \"CONVERSATIONAL_CHAT\",\n  \"message\": \"Test\",\n}\nHope this helps!"
    res2 = clean_and_extract_json(messy)
    assert res2 is not None
    assert res2["message"] == "Test"

    # 3. Invalid syntax
    invalid = "This is not json at all"
    assert clean_and_extract_json(invalid) is None


def test_validator_valid_and_invalid_chart():
    validator = DatasetValidator()

    # Valid Chart
    valid_payload = {
        "user_query": "Show quarterly profit breakdown for 2026",
        "response": {
            "output_type": "GENERATIVE_CHART",
            "chart_type": "bar",
            "title": "2026 Profit Analysis",
            "summary": "Profits grew 15% across all 4 quarters due to improved margins.",
            "data": {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "datasets": [
                    {"label": "Net Profit ($k)", "values": [120, 145, 160, 185]}
                ]
            }
        }
    }
    val_res = validator.validate_item(valid_payload, expected_output_type="GENERATIVE_CHART")
    assert val_res.is_valid is True

    # Invalid Chart (Missing datasets)
    invalid_payload = {
        "user_query": "Show quarterly profit",
        "response": {
            "output_type": "GENERATIVE_CHART",
            "chart_type": "bar",
            "title": "Profit",
            "summary": "Short summary",
            "data": {
                "labels": ["Q1"]
                # datasets missing
            }
        }
    }
    val_res2 = validator.validate_item(invalid_payload, expected_output_type="GENERATIVE_CHART")
    assert val_res2.is_valid is False
    assert val_res2.error_code == "SCHEMA_VALIDATION_ERROR"


def test_validator_mismatched_output_type():
    validator = DatasetValidator()
    payload = {
        "user_query": "Draft warning letter",
        "response": {
            "output_type": "CONVERSATIONAL_CHAT",
            "message": "Here is some message text."
        }
    }
    res = validator.validate_item(payload, expected_output_type="DOCUMENT_OUTPUT")
    assert res.is_valid is False
    assert res.error_code == "MISMATCHED_OUTPUT_TYPE"


def test_deduplication():
    dedup = DeduplicationManager(fuzzy_threshold=0.85)

    q1 = "Show me the revenue vs expense chart for Q1"
    assert dedup.is_duplicate(q1)[0] is False
    dedup.add(q1)

    # Exact duplicate (different casing & punctuation)
    q1_exact = "show me the revenue vs expense chart for q1."
    is_dup, reason = dedup.is_duplicate(q1_exact)
    assert is_dup is True
    assert "Exact duplicate" in reason

    # Fuzzy duplicate
    q1_fuzzy = "Show me revenue versus expense chart for Q1"
    is_dup_fuzzy, reason_fuzzy = dedup.is_duplicate(q1_fuzzy)
    assert is_dup_fuzzy is True
    assert "Fuzzy match" in reason_fuzzy

    # Distinct query
    q2 = "Who is the shift supervisor scheduled for tonight?"
    assert dedup.is_duplicate(q2)[0] is False
