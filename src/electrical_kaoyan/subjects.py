from __future__ import annotations

from dataclasses import dataclass

from .models import SubjectProfile


@dataclass(frozen=True)
class SubjectChange:
    change_level: str
    added_topics: frozenset[str]
    removed_topics: frozenset[str]
    migration_cost: str
    effective_year: int
    reason: str


def _migration_cost(old: set[str], new: set[str]) -> str:
    if not new:
        return "unknown"
    overlap = len(old & new) / len(new)
    if overlap >= 0.8:
        return "low"
    if overlap >= 0.4:
        return "medium"
    return "high"


def detect_subject_change(previous: SubjectProfile, current: SubjectProfile) -> SubjectChange:
    if current.admission_year <= previous.admission_year:
        raise ValueError("current subject profile must be from a later admission year")
    added = current.topics - previous.topics
    removed = previous.topics - current.topics
    content_same = not added and not removed and previous.syllabus_hash == current.syllabus_hash
    if previous.code != current.code and previous.name == current.name and content_same:
        level, reason = "A", "subject code changed; verified content is unchanged"
    elif previous.name != current.name and content_same:
        level, reason = "B", "name changed; verified content is substantially equivalent"
    elif previous.topics == current.topics and previous.textbooks != current.textbooks:
        level, reason = "C", "textbook set or edition changed without topic change"
    elif added or removed:
        overlap = len(previous.topics & current.topics) / max(len(previous.topics | current.topics), 1)
        if overlap == 0:
            level, reason = "F", "principal subject content was completely replaced"
        elif overlap < 0.5:
            level, reason = "E", "principal subject content changed"
        else:
            level, reason = "D", "syllabus topics partially changed"
    else:
        level, reason = "D", "syllabus hash changed; topic-level detail is unavailable"
    return SubjectChange(
        change_level=level,
        added_topics=frozenset(added),
        removed_topics=frozenset(removed),
        migration_cost=_migration_cost(previous.topics, current.topics),
        effective_year=current.admission_year,
        reason=reason,
    )


def user_migration_cost(current_topics: set[str], target_topics: set[str]) -> tuple[str, set[str]]:
    missing = target_topics - current_topics
    return _migration_cost(current_topics, target_topics), missing
