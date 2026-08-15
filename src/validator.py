"""Validation and Data Cleaning Engine for Synthetic Distillation Dataset.

Provides:
- Robust JSON extraction and linting (handles code blocks, whitespace, minor LLM syntax glitches).
- Strict Pydantic schema validation for all 10 target business output formats.
- Exact and Fuzzy deduplication on generated user queries.
- Non-blocking error reporting and malformed record quarantine.
"""

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union
from pydantic import BaseModel, Field, ValidationError, field_validator

from config.schemas_and_seeds import OutputSchemaType

logger = logging.getLogger("distillation.validator")

# Fuzzy matching support (RapidFuzz with difflib fallback)
try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    import difflib
    HAS_RAPIDFUZZ = False


# ============================================================================
# PYDANTIC VALIDATION MODELS (Strict 10 Schemas)
# ============================================================================

class ChartDataset(BaseModel):
    label: str = Field(..., min_length=1)
    values: List[Union[int, float]] = Field(..., min_length=1)


class ChartData(BaseModel):
    labels: List[Union[str, int]] = Field(..., min_length=1)
    datasets: List[ChartDataset] = Field(..., min_length=1)

    @field_validator("labels")
    @classmethod
    def convert_labels_to_strings(cls, v: List[Any]) -> List[str]:
        return [str(item) for item in v]


class GenerativeChartPayload(BaseModel):
    output_type: Literal["GENERATIVE_CHART"] = "GENERATIVE_CHART"
    chart_type: Literal["bar", "line", "pie", "doughnut", "radar", "scatter", "area"]
    title: str = Field(..., min_length=2)
    summary: str = Field(..., min_length=10)
    data: ChartData


class DocumentOutputPayload(BaseModel):
    output_type: Literal["DOCUMENT_OUTPUT"] = "DOCUMENT_OUTPUT"
    doc_title: str = Field(..., min_length=2)
    format: Literal["markdown", "plain_text", "html"] = "markdown"
    content: str = Field(..., min_length=15)


class ConversationalChatPayload(BaseModel):
    output_type: Literal["CONVERSATIONAL_CHAT"] = "CONVERSATIONAL_CHAT"
    message: str = Field(..., min_length=5)


class ResearchSource(BaseModel):
    title: str = Field(..., min_length=2)
    type: str = Field(..., min_length=2)
    record_id: str = Field(..., min_length=1)
    relevance: str = Field(..., min_length=2)


class DeepResearchPayload(BaseModel):
    output_type: Literal["DEEP_RESEARCH"] = "DEEP_RESEARCH"
    target_sources: List[str] = Field(..., min_length=1)
    search_queries: List[str] = Field(..., min_length=1)
    sources: List[ResearchSource] = Field(..., min_length=1)
    response: str = Field(..., min_length=15)


class ShiftEntry(BaseModel):
    staff_id: str = Field(..., min_length=2)
    name: str = Field(..., min_length=2)
    role: str = Field(..., min_length=2)
    day: str = Field(..., min_length=3)
    shift: str = Field(..., min_length=3)


class ShiftSchedulePayload(BaseModel):
    output_type: Literal["SHIFT_SCHEDULE"] = "SHIFT_SCHEDULE"
    week_starting: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    schedule: List[ShiftEntry] = Field(..., min_length=1)


class ProductivityChartPayload(BaseModel):
    output_type: Literal["PRODUCTIVITY_CHART"] = "PRODUCTIVITY_CHART"
    employee_name: str = Field(..., min_length=2)
    period: str = Field(..., min_length=2)
    chart_type: Literal["bar", "line", "pie", "radar", "area"] = "line"
    data: ChartData
    summary: str = Field(..., min_length=10)


class RedFlagAlertPayload(BaseModel):
    output_type: Literal["RED_FLAG_ALERT"] = "RED_FLAG_ALERT"
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    flagged_module: str = Field(..., min_length=2)
    anomaly_type: str = Field(..., min_length=3)
    transaction_id: Optional[str] = None
    reasoning: str = Field(..., min_length=10)
    recommended_action: str = Field(..., min_length=10)


class AutoTaskPayload(BaseModel):
    output_type: Literal["AUTO_TASK"] = "AUTO_TASK"
    task_title: str = Field(..., min_length=3)
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = "MEDIUM"
    assignee_role: str = Field(..., min_length=2)
    due_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    subtasks: List[str] = Field(..., min_length=1)


class ToolCallPayload(BaseModel):
    output_type: Literal["TOOL_CALL"] = "TOOL_CALL"
    module: str = Field(..., min_length=2)
    endpoint: str = Field(..., min_length=2)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ActionConfirmationPayload(BaseModel):
    output_type: Literal["ACTION_CONFIRMATION"] = "ACTION_CONFIRMATION"
    action_name: str = Field(..., min_length=3)
    target_module: str = Field(..., min_length=2)
    impact_summary: str = Field(..., min_length=10)
    requires_auth: bool = True


SCHEMA_MODELS = {
    OutputSchemaType.GENERATIVE_CHART.value: GenerativeChartPayload,
    OutputSchemaType.DOCUMENT_OUTPUT.value: DocumentOutputPayload,
    OutputSchemaType.CONVERSATIONAL_CHAT.value: ConversationalChatPayload,
    OutputSchemaType.DEEP_RESEARCH.value: DeepResearchPayload,
    OutputSchemaType.SHIFT_SCHEDULE.value: ShiftSchedulePayload,
    OutputSchemaType.PRODUCTIVITY_CHART.value: ProductivityChartPayload,
    OutputSchemaType.RED_FLAG_ALERT.value: RedFlagAlertPayload,
    OutputSchemaType.AUTO_TASK.value: AutoTaskPayload,
    OutputSchemaType.TOOL_CALL.value: ToolCallPayload,
    OutputSchemaType.ACTION_CONFIRMATION.value: ActionConfirmationPayload,
}


# ============================================================================
# ROBUST JSON PARSER & EXTRACTOR
# ============================================================================

def clean_and_extract_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extract and repair JSON objects from raw LLM output."""
    if not raw_text or not isinstance(raw_text, str):
        return None

    cleaned = raw_text.strip()

    # 1. Try markdown code block extraction
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if code_block_match:
        extracted = code_block_match.group(1).strip()
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            cleaned = extracted

    # 2. Try direct parsing
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Locate outer braces { ... }
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        json_candidate = cleaned[first_brace : last_brace + 1]
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError:
            # Try minor JSON repairs (e.g. trailing commas before } or ])
            repaired = re.sub(r",\s*([\]}])", r"\1", json_candidate)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass

    return None


# ============================================================================
# DEDUPLICATION MANAGER
# ============================================================================

class DeduplicationManager:
    """Manages exact and fuzzy deduplication on generated queries."""

    def __init__(self, fuzzy_threshold: float = 0.85):
        self.fuzzy_threshold = fuzzy_threshold
        self.exact_seen: Set[str] = set()
        self.corpus: List[str] = []

    def _normalize(self, text: str) -> str:
        """Lowercases, removes extra punctuation, and strips whitespace."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        return re.sub(r"\s+", " ", text)

    def is_duplicate(self, query: str) -> Tuple[bool, Optional[str]]:
        """Check if query is duplicate (exact or fuzzy).

        Returns: (is_dup, reason_or_matched_query)
        """
        norm = self._normalize(query)
        if not norm or len(norm) < 5:
            return True, "Query too short or empty"

        if norm in self.exact_seen:
            return True, "Exact duplicate"

        # Check fuzzy match against stored corpus
        for existing in self.corpus:
            similarity = self._compute_similarity(norm, existing)
            if similarity >= self.fuzzy_threshold:
                return True, f"Fuzzy match ({similarity:.2f} >= {self.fuzzy_threshold}): '{existing}'"

        return False, None

    def add(self, query: str) -> None:
        """Register query in deduplication indexes."""
        norm = self._normalize(query)
        self.exact_seen.add(norm)
        self.corpus.append(norm)

    def _compute_similarity(self, s1: str, s2: str) -> float:
        if HAS_RAPIDFUZZ:
            return fuzz.ratio(s1, s2) / 100.0
        return difflib.SequenceMatcher(None, s1, s2).ratio()


# ============================================================================
# MAIN VALIDATOR
# ============================================================================

@dataclass
class ValidationResult:
    is_valid: bool
    cleaned_user_query: Optional[str] = None
    cleaned_response: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_reason: Optional[str] = None


class DatasetValidator:
    """Validates raw LLM generation items against strict schemas & duplicate rules."""

    def __init__(self, fuzzy_threshold: float = 0.85):
        self.dedup_manager = DeduplicationManager(fuzzy_threshold=fuzzy_threshold)

    def validate_item(
        self,
        raw_output: Union[str, Dict[str, Any]],
        expected_output_type: Optional[str] = None,
        check_dedup: bool = True,
    ) -> ValidationResult:
        """Validate a single generated pair (user_query + response)."""
        # 1. Parse JSON if string
        if isinstance(raw_output, str):
            parsed = clean_and_extract_json(raw_output)
            if not parsed or not isinstance(parsed, dict):
                return ValidationResult(
                    is_valid=False,
                    error_code="JSON_PARSE_ERROR",
                    error_reason="Could not extract valid JSON object from model output",
                )
        elif isinstance(raw_output, dict):
            parsed = raw_output
        else:
            return ValidationResult(
                is_valid=False,
                error_code="INVALID_TYPE",
                error_reason=f"Expected string or dict, got {type(raw_output).__name__}",
            )

        # 2. Extract user_query and response
        user_query = parsed.get("user_query")
        response = parsed.get("response")

        # Sometimes the model returns response directly at top-level
        if response is None and "output_type" in parsed:
            response = parsed
            user_query = parsed.get("prompt") or parsed.get("query")

        if not user_query or not isinstance(user_query, str) or len(user_query.strip()) < 5:
            return ValidationResult(
                is_valid=False,
                error_code="MISSING_USER_QUERY",
                error_reason="Generated item lacks a valid non-empty 'user_query' string",
            )

        user_query = user_query.strip()

        if not response or not isinstance(response, dict):
            return ValidationResult(
                is_valid=False,
                error_code="MISSING_RESPONSE_OBJECT",
                error_reason="Generated item lacks a valid 'response' JSON dictionary",
            )

        # 3. Check output_type
        output_type = response.get("output_type")
        if not output_type:
            return ValidationResult(
                is_valid=False,
                error_code="MISSING_OUTPUT_TYPE",
                error_reason="Response JSON object missing 'output_type' key",
            )

        if expected_output_type and output_type != expected_output_type:
            return ValidationResult(
                is_valid=False,
                error_code="MISMATCHED_OUTPUT_TYPE",
                error_reason=f"Expected output_type '{expected_output_type}', but got '{output_type}'",
            )

        model_cls = SCHEMA_MODELS.get(output_type)
        if not model_cls:
            return ValidationResult(
                is_valid=False,
                error_code="UNKNOWN_OUTPUT_TYPE",
                error_reason=f"Unrecognized output_type: '{output_type}'",
            )

        # 4. Strict Pydantic Schema Validation
        try:
            validated_obj = model_cls.model_validate(response)
            cleaned_response = validated_obj.model_dump()
        except ValidationError as e:
            error_details = "; ".join(f"{err['loc']}: {err['msg']}" for err in e.errors())
            return ValidationResult(
                is_valid=False,
                error_code="SCHEMA_VALIDATION_ERROR",
                error_reason=f"Schema violation for {output_type}: {error_details}",
            )

        # 5. Deduplication check
        if check_dedup:
            is_dup, reason = self.dedup_manager.is_duplicate(user_query)
            if is_dup:
                return ValidationResult(
                    is_valid=False,
                    error_code="DUPLICATE_QUERY",
                    error_reason=reason,
                )

        return ValidationResult(
            is_valid=True,
            cleaned_user_query=user_query,
            cleaned_response=cleaned_response,
        )

    def register_seed_examples(self, seeds: Dict[str, List[Dict[str, Any]]]) -> int:
        """Populate deduplication index with existing seeds."""
        count = 0
        for _, seed_list in seeds.items():
            for seed in seed_list:
                q = seed.get("user_query")
                if q:
                    self.dedup_manager.add(q)
                    count += 1
        return count
