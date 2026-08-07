from electrical_kaoyan.models import FieldFact
from electrical_kaoyan.validators import validate_candidate_ids, validate_counts, validate_facts


def test_count_relationships_are_flagged_not_corrected():
    issues = validate_counts({"retest_candidates": 20, "admitted_candidates": 21,
                              "planned_total": 10, "recommended_exempt": 11})
    assert {issue.code for issue in issues} == {"retest_below_admitted", "exempt_above_total"}


def test_duplicate_candidate_detection():
    assert validate_candidate_ids(["a", "b", "a"])[0].code == "duplicate_candidate"


def test_social_fact_promotion_is_rejected():
    fact = FieldFact(entity_type="program", entity_id="P", field_path="planned_total",
                     admission_year=2027, value=10, evidence_ids=["C1"],
                     scope={"source_kind": "social", "assertion_kind": "official_fact"})
    issues = validate_facts([fact], {"C1"})
    assert issues[0].code == "social_promoted_to_official"
