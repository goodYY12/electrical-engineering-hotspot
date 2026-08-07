from __future__ import annotations

from collections import Counter
from typing import Any

from .models import DataQualityIssue, FieldFact


def validate_statistics(stats: dict[str, float | int] | None) -> list[DataQualityIssue]:
    if stats is None:
        return []
    issues: list[DataQualityIssue] = []
    if not (stats["minimum"] <= stats["median"] <= stats["maximum"]):
        issues.append(DataQualityIssue(
            code="score_order", severity="error",
            message="minimum <= median <= maximum is violated",
        ))
    if stats["sample_size"] < 1:
        issues.append(DataQualityIssue(
            code="empty_sample", severity="error", message="sample size must be positive",
        ))
    return issues


def validate_counts(data: dict[str, int | None], *, entity_id: str | None = None) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    for field, value in data.items():
        if value is not None and value < 0:
            issues.append(DataQualityIssue(
                code="negative_count", severity="error", entity_id=entity_id,
                field_path=field, message=f"{field} cannot be negative",
            ))
    retest = data.get("retest_candidates")
    admitted = data.get("admitted_candidates")
    if retest is not None and admitted is not None and retest < admitted:
        issues.append(DataQualityIssue(
            code="retest_below_admitted", severity="warning", entity_id=entity_id,
            message="retest count is below admitted count; verify cohort and special cases",
        ))
    planned = data.get("planned_total")
    exempt = data.get("recommended_exempt")
    if planned is not None and exempt is not None and exempt > planned:
        issues.append(DataQualityIssue(
            code="exempt_above_total", severity="warning", entity_id=entity_id,
            message="recommended-exempt count exceeds planned total; verify scope",
        ))
    return issues


def validate_candidate_ids(candidate_ids: list[str]) -> list[DataQualityIssue]:
    duplicates = [key for key, count in Counter(candidate_ids).items() if count > 1]
    return [DataQualityIssue(
        code="duplicate_candidate", severity="warning",
        message=f"duplicate anonymized candidate identifier: {key}",
    ) for key in duplicates]


def validate_facts(facts: list[FieldFact], evidence_ids: set[str]) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    for fact in facts:
        missing = set(fact.evidence_ids + fact.input_evidence_ids) - evidence_ids
        if missing:
            issues.append(DataQualityIssue(
                code="missing_evidence", severity="error", entity_id=fact.entity_id,
                field_path=fact.field_path,
                message=f"missing evidence IDs: {sorted(missing)}",
            ))
        if fact.derived and not fact.calculation_formula:
            issues.append(DataQualityIssue(
                code="derived_without_formula", severity="error", entity_id=fact.entity_id,
                field_path=fact.field_path, message="derived fact lacks a formula",
            ))
        source_kind: Any = fact.scope.get("source_kind")
        assertion_kind: Any = fact.scope.get("assertion_kind")
        if source_kind == "social" and assertion_kind == "official_fact":
            issues.append(DataQualityIssue(
                code="social_promoted_to_official", severity="error", entity_id=fact.entity_id,
                field_path=fact.field_path,
                message="a social source cannot be promoted to an official fact",
            ))
    return issues
