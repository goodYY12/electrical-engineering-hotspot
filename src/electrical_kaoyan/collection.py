from __future__ import annotations

import json
from collections import defaultdict
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

from .social import Platform, SocialPost


class ObservationMethod(StrEnum):
    PUBLIC_HTML = "public_html"
    SEARCH_SNIPPET = "search_snippet"
    AGENT_BROWSER = "agent_browser"
    USER_EXPORT = "user_export"
    SCREENSHOT = "screenshot"
    HISTORICAL_SNAPSHOT = "historical_snapshot"
    CROSS_PLATFORM = "cross_platform_corroboration"


class EvidenceTier(StrEnum):
    FULL = "full_content"
    VISIBLE = "visible_observation"
    SNIPPET = "search_snippet"
    CORROBORATION = "corroboration_only"


class SearchAttempt(BaseModel):
    attempt_id: str
    target_id: str
    platform: Platform
    query: str
    method: str
    attempted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    outcome: Literal["success", "no_results", "access_limited", "parse_failed", "error"]
    results_seen: int = Field(default=0, ge=0)
    new_exact_matches: int = Field(default=0, ge=0)
    access_reason: str | None = None
    result_url: HttpUrl | None = None
    notes: str | None = None


class PlatformDiagnosis(BaseModel):
    platform: Platform
    status: Literal[
        "adequate", "low_observed_attention", "access_limited", "indexing_gap",
        "target_ambiguity", "collection_incomplete",
    ]
    attempts: int
    successful_queries: int
    access_failures: int
    exact_observations: int
    proxy_observations: int
    saturation: float
    explanation: str


class CollectionAssessment(BaseModel):
    target_id: str
    status: Literal[
        "adequate", "low_observed_attention", "access_limited", "indexing_gap",
        "target_ambiguity", "collection_incomplete",
    ]
    saturation: float
    attempted_platform_coverage: float
    access_failure_count: int
    eligible_observations: int
    proxy_observations: int
    platforms: list[PlatformDiagnosis]
    next_actions: list[str]


def evidence_tier(method: str) -> EvidenceTier:
    mapping = {
        ObservationMethod.PUBLIC_HTML: EvidenceTier.FULL,
        ObservationMethod.USER_EXPORT: EvidenceTier.FULL,
        ObservationMethod.AGENT_BROWSER: EvidenceTier.VISIBLE,
        ObservationMethod.SCREENSHOT: EvidenceTier.VISIBLE,
        ObservationMethod.HISTORICAL_SNAPSHOT: EvidenceTier.SNIPPET,
        ObservationMethod.SEARCH_SNIPPET: EvidenceTier.SNIPPET,
        ObservationMethod.CROSS_PLATFORM: EvidenceTier.CORROBORATION,
    }
    try:
        return mapping[ObservationMethod(method)]
    except ValueError:
        return EvidenceTier.VISIBLE


def eligible_for_heat(post: SocialPost) -> bool:
    return (
        post.exact_target_match
        and post.published_at is not None
        and evidence_tier(post.extraction_method) in {EvidenceTier.FULL, EvidenceTier.VISIBLE}
        and not post.access_limited
    )


def _platform_saturation(attempts: list[SearchAttempt]) -> float:
    if len(attempts) < 2:
        return 0.0
    tail = attempts[-3:]
    zero_yield = sum(item.new_exact_matches == 0 for item in tail) / len(tail)
    breadth = min(len({item.query.strip().lower() for item in attempts}) / 3, 1.0)
    return round(0.5 * zero_yield + 0.5 * breadth, 3)


def diagnose_collection(*, target_id: str, posts: list[SocialPost], attempts: list[SearchAttempt],
                        expected_platforms: list[Platform]) -> CollectionAssessment:
    relevant_posts = [post for post in posts if post.target_id == target_id]
    relevant_attempts = [item for item in attempts if item.target_id == target_id]
    by_platform_attempt: dict[Platform, list[SearchAttempt]] = defaultdict(list)
    by_platform_post: dict[Platform, list[SocialPost]] = defaultdict(list)
    for item in relevant_attempts:
        by_platform_attempt[item.platform].append(item)
    for post in relevant_posts:
        by_platform_post[post.platform].append(post)

    expected = sorted(set(expected_platforms))
    diagnoses: list[PlatformDiagnosis] = []
    for platform in expected:
        platform_attempts = sorted(by_platform_attempt[platform], key=lambda item: item.attempted_at)
        platform_posts = by_platform_post[platform]
        exact = sum(eligible_for_heat(post) for post in platform_posts)
        proxy = sum(not eligible_for_heat(post) and post.exact_target_match for post in platform_posts)
        access_failures = sum(item.outcome == "access_limited" for item in platform_attempts)
        browser_access_failures = sum(
            item.outcome == "access_limited"
            and item.method in {"agent_browser", "user_session_browser"}
            for item in platform_attempts
        )
        successful = sum(item.outcome in {"success", "no_results"} for item in platform_attempts)
        saturation = _platform_saturation(platform_attempts)
        ambiguous = any(not post.exact_target_match for post in platform_posts)
        if exact >= 3:
            status = "adequate"
            explanation = "At least three date-verifiable, exact-target observations are available."
        elif ambiguous and not exact:
            status = "target_ambiguity"
            explanation = "Discoveries exist, but exact school/program identity is not verified."
        elif browser_access_failures or (access_failures and access_failures >= max(successful, 1)):
            status = "access_limited"
            explanation = "The platform's direct browser path is access-limited or access failures dominate collection."
        elif proxy and not exact:
            status = "indexing_gap"
            explanation = "Only snippets or indirect traces are visible; full dated observations are absent."
        elif saturation >= 0.8 and successful >= 3:
            status = "low_observed_attention"
            explanation = "Several diverse public queries reached diminishing returns with few exact observations."
        else:
            status = "collection_incomplete"
            explanation = "Too few diverse successful queries exist to diagnose low attention or invisibility."
        diagnoses.append(PlatformDiagnosis(
            platform=platform, status=status, attempts=len(platform_attempts),
            successful_queries=successful, access_failures=access_failures,
            exact_observations=exact, proxy_observations=proxy, saturation=saturation,
            explanation=explanation,
        ))

    status_priority = [
        "target_ambiguity", "access_limited", "indexing_gap", "collection_incomplete",
        "low_observed_attention", "adequate",
    ]
    statuses = {item.status for item in diagnoses}
    overall = next((status for status in status_priority if status in statuses), "collection_incomplete")
    attempted = sum(bool(by_platform_attempt[item]) for item in expected)
    coverage = attempted / len(expected) if expected else 1.0
    saturation = sum(item.saturation for item in diagnoses) / len(diagnoses) if diagnoses else 0.0
    eligible = sum(eligible_for_heat(post) for post in relevant_posts)
    proxy = sum(not eligible_for_heat(post) and post.exact_target_match for post in relevant_posts)
    actions: list[str] = []
    if "access_limited" in statuses:
        actions.append("Use an allowed signed-in Agent browser, user export, or screenshot; do not bypass controls.")
    if "indexing_gap" in statuses:
        actions.append("Verify snippet dates and identity through another public index, archive, or user-supplied view.")
    if "target_ambiguity" in statuses:
        actions.append("Add college, major code, subject code, and exclusion terms to the query set.")
    if "collection_incomplete" in statuses:
        actions.append("Run at least three distinct query formulations per missing platform and log every attempt.")
    if overall == "low_observed_attention":
        actions.append("Report low observable attention only; do not infer zero discussion or applicant demand.")
    return CollectionAssessment(
        target_id=target_id, status=overall, saturation=round(saturation, 3),
        attempted_platform_coverage=round(coverage, 3),
        access_failure_count=sum(item.outcome == "access_limited" for item in relevant_attempts),
        eligible_observations=eligible, proxy_observations=proxy,
        platforms=diagnoses, next_actions=actions,
    )


def append_attempt(path: Path, attempt: SearchAttempt) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(attempt.model_dump_json() + "\n")


def read_attempts(path: Path | None) -> list[SearchAttempt]:
    if path is None or not path.exists():
        return []
    return [
        SearchAttempt.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def attempt_id(target_id: str, platform: Platform, query: str, attempted_at: datetime) -> str:
    import hashlib

    raw = json.dumps([target_id, platform, query, attempted_at.isoformat()], ensure_ascii=False)
    return "attempt-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
