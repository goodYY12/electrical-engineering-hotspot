from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, model_validator


class DegreeType(StrEnum):
    ACADEMIC = "academic"
    PROFESSIONAL = "professional"


class StudyMode(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"


class SourceGrade(StrEnum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"


class UnknownReason(StrEnum):
    MISSING = "missing"
    WITHHELD = "withheld"
    INACCESSIBLE = "inaccessible"
    AMBIGUOUS_SCOPE = "ambiguous_scope"
    NOT_APPLICABLE = "not_applicable"


class NumericValue(BaseModel):
    value: float | None = None
    lower: float | None = None
    upper: float | None = None
    unknown_reason: UnknownReason | None = None

    @model_validator(mode="after")
    def exactly_one_shape(self) -> NumericValue:
        shapes = [self.value is not None, self.lower is not None or self.upper is not None,
                  self.unknown_reason is not None]
        if sum(shapes) != 1:
            raise ValueError("use exactly one of exact value, interval, or unknown reason")
        if self.value is not None and self.value < 0:
            raise ValueError("numeric admissions values cannot be negative")
        if self.lower is not None and self.lower < 0:
            raise ValueError("interval lower bound cannot be negative")
        if self.upper is not None and self.upper < 0:
            raise ValueError("interval upper bound cannot be negative")
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError("interval lower bound exceeds upper bound")
        return self


class ProgramIdentity(BaseModel):
    school: str
    college: str
    major_code: str = Field(pattern=r"^\d{6}$")
    major_name: str
    degree_type: DegreeType
    study_mode: StudyMode
    research_direction: str | None = None
    special_program: str | None = None
    campus: str | None = None
    admission_year: int = Field(ge=2000, le=2100)

    @property
    def program_id(self) -> str:
        values = {
            key: (value.value if isinstance(value, StrEnum) else value) or "<unknown>"
            for key, value in self.model_dump().items()
        }
        canonical = json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
        return f"program-{self.admission_year}-{digest}"


class AdmissionCycle(BaseModel):
    admission_year: int = Field(ge=2000, le=2100)
    exam_year: int
    announcement_date: date | None = None

    @model_validator(mode="after")
    def plausible_exam_year(self) -> AdmissionCycle:
        if self.exam_year not in {self.admission_year - 1, self.admission_year}:
            raise ValueError("exam_year must be admission_year - 1 or explicitly same-year")
        return self


class EvidenceRecord(BaseModel):
    evidence_id: str
    source_url: HttpUrl
    source_title: str
    source_type: str
    source_grade: SourceGrade
    publication_date: date | None = None
    accessed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    page_number: int | None = Field(default=None, ge=1)
    table_name: str | None = None
    raw_text_snippet: str | None = None
    extraction_method: str
    confidence: Literal["high", "medium", "low"]
    content_hash: str
    archive_path: str | None = None
    revision: int = Field(default=1, ge=1)
    access_limited: bool = False


class FieldFact(BaseModel):
    entity_type: str
    entity_id: str
    field_path: str
    admission_year: int
    value: Any
    unit: str | None = None
    scope: dict[str, Any] = Field(default_factory=dict)
    evidence_ids: list[str] = Field(min_length=1)
    derived: bool = False
    calculation_formula: str | None = None
    input_evidence_ids: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "medium"

    @model_validator(mode="after")
    def derived_has_formula(self) -> FieldFact:
        if self.derived and (not self.calculation_formula or not self.input_evidence_ids):
            raise ValueError("derived facts require a formula and input evidence IDs")
        if not self.derived and (self.calculation_formula or self.input_evidence_ids):
            raise ValueError("direct facts cannot contain derivation metadata")
        return self


class EvidenceConflict(BaseModel):
    conflict_id: str
    entity_id: str
    field_path: str
    admission_year: int
    fact_indexes: list[int] = Field(min_length=2)
    status: Literal["unresolved", "resolved"] = "unresolved"
    preferred_fact_index: int | None = None
    rationale: str | None = None


class SubjectProfile(BaseModel):
    admission_year: int
    code: str
    name: str
    topics: set[str] = Field(default_factory=set)
    textbooks: set[str] = Field(default_factory=set)
    syllabus_hash: str | None = None
    retest_subjects: set[str] = Field(default_factory=set)
    evidence_ids: list[str] = Field(default_factory=list)


class DataQualityIssue(BaseModel):
    code: str
    severity: Literal["error", "warning", "info"]
    message: str
    entity_id: str | None = None
    field_path: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
