from datetime import date

import pytest
from pydantic import ValidationError

from electrical_kaoyan.evidence import detect_conflicts, preferred_evidence
from electrical_kaoyan.models import (
    DegreeType,
    EvidenceRecord,
    FieldFact,
    NumericValue,
    ProgramIdentity,
    SourceGrade,
    StudyMode,
    SubjectProfile,
    UnknownReason,
)
from electrical_kaoyan.quotas import estimate_unified_quota
from electrical_kaoyan.statistics import score_distribution
from electrical_kaoyan.subjects import detect_subject_change, user_migration_cost
from electrical_kaoyan.years import cycle_from_admission_year, infer_admission_year


def identity(**updates):
    values = {
        "school": "重庆大学", "college": "电气工程学院", "major_code": "085801",
        "major_name": "电气工程", "degree_type": DegreeType.PROFESSIONAL,
        "study_mode": StudyMode.FULL_TIME, "admission_year": 2027,
    }
    values.update(updates)
    return ProgramIdentity(**values)


def evidence(evidence_id: str, grade: SourceGrade, publication_date: date | None = None):
    return EvidenceRecord(evidence_id=evidence_id, source_url="https://example.edu.cn/a",
                          source_title="notice", source_type="college_official",
                          source_grade=grade, publication_date=publication_date,
                          raw_text_snippet="招生计划", extraction_method="html_text",
                          confidence="high", content_hash="a" * 64)


def test_year_conversion_and_explicit_inference():
    cycle = cycle_from_admission_year(2027)
    assert cycle.exam_year == 2026
    assert infer_admission_year("2027年硕士研究生招生专业目录") == 2027
    assert infer_admission_year("公告发布于2026年9月") is None


def test_program_id_is_stable_and_separates_entities():
    assert identity().program_id == identity().program_id
    assert identity(college="卓越工程师学院").program_id != identity().program_id
    assert identity(study_mode=StudyMode.PART_TIME).program_id != identity().program_id


def test_unknown_is_not_zero_and_negative_is_invalid():
    assert NumericValue(unknown_reason=UnknownReason.MISSING).value is None
    assert NumericValue(value=0).value == 0
    with pytest.raises(ValidationError):
        NumericValue(value=-1)


def test_quota_calculation_preserves_formula_and_unknown():
    result = estimate_unified_quota(100, 55, 8, ("E1", "E2", "E3"), compatible_scope=True)
    assert result.value == 37
    assert result.formula == "100 - 55 - 8 = 37"
    unknown = estimate_unified_quota(100, None, 8, ("E1", "E3"), compatible_scope=True)
    assert unknown.value is None and unknown.unknown_reason == "missing_input"


def test_source_priority_and_recency():
    selected = preferred_evidence([
        evidence("B", SourceGrade.B, date(2026, 9, 1)),
        evidence("S-old", SourceGrade.S, date(2026, 8, 1)),
        evidence("S-new", SourceGrade.S, date(2026, 9, 2)),
    ])
    assert selected.evidence_id == "S-new"


def test_conflict_requires_same_scope_and_keeps_both_values():
    facts = [FieldFact(entity_type="program", entity_id="P", field_path="planned_total",
                       admission_year=2027, value=value, scope={"study_mode": "full_time"},
                       evidence_ids=[f"E{value}"]) for value in (40, 50)]
    conflicts = detect_conflicts(facts)
    assert len(conflicts) == 1
    assert conflicts[0].fact_indexes == [0, 1]


def test_score_distribution_uses_population_std_and_ignores_missing():
    result = score_distribution([300, 320, None, 340])
    assert result["sample_size"] == 3
    assert result["median"] == 320
    assert result["minimum"] == 300 and result["maximum"] == 340


def test_subject_code_only_change_is_not_major():
    old = SubjectProfile(admission_year=2026, code="813", name="电路", topics={"circuits"},
                         syllabus_hash="same")
    new = SubjectProfile(admission_year=2027, code="811", name="电路", topics={"circuits"},
                         syllabus_hash="same")
    change = detect_subject_change(old, new)
    assert change.change_level == "A" and change.migration_cost == "low"


def test_subject_replacement_and_user_migration_cost():
    old = SubjectProfile(admission_year=2026, code="811", name="电路", topics={"circuits"})
    new = SubjectProfile(admission_year=2027, code="840", name="电气综合",
                         topics={"power_system_steady", "power_electronics"})
    assert detect_subject_change(old, new).change_level == "F"
    cost, missing = user_migration_cost({"circuits"}, new.topics)
    assert cost == "high" and missing == new.topics
