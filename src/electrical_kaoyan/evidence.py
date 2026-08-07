from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from .models import EvidenceConflict, EvidenceRecord, FieldFact, SourceGrade

GRADE_RANK = {SourceGrade.S: 0, SourceGrade.A: 1, SourceGrade.B: 2, SourceGrade.C: 3}


def preferred_evidence(records: Iterable[EvidenceRecord]) -> EvidenceRecord:
    items = list(records)
    if not items:
        raise ValueError("at least one evidence record is required")
    return min(
        items,
        key=lambda record: (
            GRADE_RANK[record.source_grade],
            -(record.publication_date.toordinal() if record.publication_date else 0),
            -record.revision,
        ),
    )


def detect_conflicts(facts: list[FieldFact]) -> list[EvidenceConflict]:
    grouped: dict[tuple[str, str, int, str], list[int]] = defaultdict(list)
    for index, fact in enumerate(facts):
        scope = json.dumps(fact.scope, ensure_ascii=False, sort_keys=True)
        grouped[(fact.entity_id, fact.field_path, fact.admission_year, scope)].append(index)

    conflicts: list[EvidenceConflict] = []
    for (entity_id, field_path, year, _), indexes in grouped.items():
        values = {json.dumps(facts[i].value, ensure_ascii=False, sort_keys=True) for i in indexes}
        if len(values) > 1:
            conflicts.append(EvidenceConflict(
                conflict_id=f"conflict-{year}-{len(conflicts) + 1:04d}",
                entity_id=entity_id,
                field_path=field_path,
                admission_year=year,
                fact_indexes=indexes,
            ))
    return conflicts


class EvidenceLedger:
    def __init__(self) -> None:
        self.records: dict[str, EvidenceRecord] = {}
        self.facts: list[FieldFact] = []

    def add_record(self, record: EvidenceRecord) -> None:
        existing = self.records.get(record.evidence_id)
        if existing and existing != record:
            raise ValueError(f"evidence ID collision: {record.evidence_id}")
        self.records[record.evidence_id] = record

    def add_fact(self, fact: FieldFact) -> None:
        missing = set(fact.evidence_ids + fact.input_evidence_ids) - self.records.keys()
        if missing:
            raise ValueError(f"fact refers to missing evidence: {sorted(missing)}")
        self.facts.append(fact)

    def export(self, path: Path) -> None:
        payload = {
            "evidence": [record.model_dump(mode="json") for record in self.records.values()],
            "facts": [fact.model_dump(mode="json") for fact in self.facts],
            "conflicts": [item.model_dump(mode="json") for item in detect_conflicts(self.facts)],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
