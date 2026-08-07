from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuotaEstimate:
    value: int | None
    formula: str | None
    input_evidence_ids: tuple[str, ...]
    unknown_reason: str | None = None


def estimate_unified_quota(
    planned_total: int | None,
    recommended_exempt: int | None,
    special_quota: int | None,
    evidence_ids: tuple[str, ...],
    *,
    compatible_scope: bool,
) -> QuotaEstimate:
    if not compatible_scope:
        return QuotaEstimate(None, None, evidence_ids, "incompatible_scope")
    if planned_total is None or recommended_exempt is None or special_quota is None:
        return QuotaEstimate(None, None, evidence_ids, "missing_input")
    value = planned_total - recommended_exempt - special_quota
    if value < 0:
        return QuotaEstimate(None, None, evidence_ids, "negative_result_requires_review")
    return QuotaEstimate(
        value,
        f"{planned_total} - {recommended_exempt} - {special_quota} = {value}",
        evidence_ids,
    )
