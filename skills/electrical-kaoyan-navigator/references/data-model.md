# Data model

## Identity and time

`program_id` is a deterministic digest of normalized school, college, major code, major name, degree type, study mode, research direction, special program, campus, and admission year. Preserve the human-readable identity alongside the digest. Missing dimensions use an explicit unknown sentinel; they never disappear from the identity tuple.

Use `admission_year` as the cycle key. Normally `exam_year = admission_year - 1`, but keep both fields because nonstandard cycles and document wording require evidence. `announcement_date` is publication time; `effective_from` is the first admission year affected by a change.

## Core tables

- `schools`, `colleges`, `programs`, `admission_cycles`
- `quota_records`: typed quota kind, value/range/unknown, scope and evidence
- `exam_subjects`, `exam_syllabi`, `reference_books`, `subject_changes`
- `retest_rules`, `score_lines`, `retest_candidates`, `admitted_candidates`, `admission_statistics`
- `research_directions`, `labs_and_platforms`, `employment_evidence`
- `social_posts`, `social_claims`
- `evidence_records`, `field_facts`, `source_documents`, `source_revisions`, `evidence_conflicts`
- `user_profiles`, `analysis_snapshots`, `data_quality_issues`, `reevaluation_triggers`

## Unknown values

A numeric fact is one of: exact value, closed/open interval, or unknown with reason. `0` is a known value and must have evidence. Missing, withheld, inaccessible, ambiguous-scope, and not-applicable are distinct reasons.

## Quotas

Do not collapse these concepts:

- `planned_total`
- `academic_planned`, `professional_planned`
- `full_time_planned`, `part_time_planned`
- `recommended_exempt_planned`, `recommended_exempt_actual`
- `unified_exam_planned`
- `estimated_unified_quota`
- `actual_unified_admitted`
- `special_quota` with subtype such as minority, retired-soldier, military, excellent-engineer, industry-joint, institute, or international-joint.

An estimated unified quota is only computed when scopes are compatible. It retains the formula and every input evidence ID.

## Candidate data

Hash candidate identifiers with a case-specific salt. Do not persist names in normalized tables. Keep subject scores, preliminary total, retest score, composite score, category, direction, transfer/special flags only when officially published. Missing columns remain missing.

Statistics include count, minimum, Q1, median, mean, Q3, maximum, and population standard deviation, with the exact included cohort and exclusion rules. Retest-to-admission analysis must keep first-choice, transfer, special plan, degree type, and study mode cohorts separate.

## Evidence fact shape

Every structured value is a `field_fact` with entity type/id, field path, admission year, typed value, unit, scope, evidence ID, derivation metadata, and confidence. This supports multiple competing facts without overwriting history.
