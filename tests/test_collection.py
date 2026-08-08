from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from electrical_kaoyan.collection import (
    EvidenceTier,
    SearchAttempt,
    diagnose_collection,
    evidence_tier,
)
from electrical_kaoyan.social import (
    MediaTarget,
    Platform,
    SocialPost,
    analyze_heat,
    load_heat_rules,
)

TARGET = MediaTarget(school="南京师范大学", college="南瑞电气与自动化学院", major_code="085801")
RULES = load_heat_rules(Path("config/heat_rules.yaml"))


def post(number: int, platform: Platform, *, method: str = "agent_browser",
         published: bool = True, exact: bool = True) -> SocialPost:
    return SocialPost(
        post_id=f"P{number}", target_id=TARGET.target_id, platform=platform,
        url=f"https://example.com/{number}", title=f"独立内容{number}", text=str(number) * 40,
        author_id=f"A{number}", published_at=datetime(2026, 8, number, tzinfo=UTC) if published else None,
        extraction_method=method, exact_target_match=exact, content_hash=f"{number:064d}",
        intent_markers=["085801"], verified_fields=["title", "published_at"] if published else ["title"],
    )


def attempt(number: int, platform: Platform, outcome: str, *, new: int = 0) -> SearchAttempt:
    return SearchAttempt(
        attempt_id=f"Q{number}-{platform}", target_id=TARGET.target_id, platform=platform,
        query=f"query-{number}", method="public_search",
        attempted_at=datetime(2026, 8, number, tzinfo=UTC), outcome=outcome,
        new_exact_matches=new,
    )


def test_search_snippet_is_proxy_not_heat():
    snippet = post(1, Platform.BILIBILI, method="search_snippet", published=True)
    report = analyze_heat([snippet], target_id=TARGET.target_id, as_of=date(2026, 8, 8),
                          expected_platforms=[Platform.BILIBILI], rules=RULES)
    assert report.organic_posts == 0
    assert report.proxy_posts == 1
    assert report.proxy_signal > 0
    assert report.heat_level == "insufficient_data"


def test_access_failures_are_not_misreported_as_low_heat():
    attempts = [attempt(i, Platform.XIAOHONGSHU, "access_limited") for i in range(1, 4)]
    result = diagnose_collection(target_id=TARGET.target_id, posts=[], attempts=attempts,
                                 expected_platforms=[Platform.XIAOHONGSHU])
    assert result.status == "access_limited"
    assert result.access_failure_count == 3
    assert "signed-in Agent browser" in result.next_actions[0]


def test_repeated_zero_yield_queries_can_support_low_observed_attention():
    attempts = [attempt(i, Platform.ZHIHU, "no_results") for i in range(1, 4)]
    result = diagnose_collection(target_id=TARGET.target_id, posts=[], attempts=attempts,
                                 expected_platforms=[Platform.ZHIHU])
    assert result.status == "low_observed_attention"
    assert result.saturation == 1.0


def test_snippet_without_full_page_is_diagnosed_as_indexing_gap():
    snippet = post(1, Platform.BILIBILI, method="search_snippet", published=True)
    attempts = [attempt(1, Platform.BILIBILI, "success", new=1)]
    result = diagnose_collection(target_id=TARGET.target_id, posts=[snippet], attempts=attempts,
                                 expected_platforms=[Platform.BILIBILI])
    assert result.status == "indexing_gap"
    assert result.proxy_observations == 1


def test_ambiguous_entities_are_not_counted_as_target_heat():
    ambiguous = post(1, Platform.ZHIHU, exact=False)
    attempts = [attempt(1, Platform.ZHIHU, "success")]
    result = diagnose_collection(target_id=TARGET.target_id, posts=[ambiguous], attempts=attempts,
                                 expected_platforms=[Platform.ZHIHU])
    assert result.status == "target_ambiguity"
    assert result.eligible_observations == 0


@pytest.mark.parametrize(("method", "tier"), [
    ("public_html", EvidenceTier.FULL),
    ("user_export", EvidenceTier.FULL),
    ("agent_browser", EvidenceTier.VISIBLE),
    ("screenshot", EvidenceTier.VISIBLE),
    ("search_snippet", EvidenceTier.SNIPPET),
    ("historical_snapshot", EvidenceTier.SNIPPET),
    ("cross_platform_corroboration", EvidenceTier.CORROBORATION),
])
def test_all_collection_paths_have_an_explicit_evidence_tier(method, tier):
    assert evidence_tier(method) is tier


def test_one_query_remains_collection_incomplete():
    attempts = [attempt(1, Platform.WECHAT, "no_results")]
    result = diagnose_collection(target_id=TARGET.target_id, posts=[], attempts=attempts,
                                 expected_platforms=[Platform.WECHAT])
    assert result.status == "collection_incomplete"


def test_direct_browser_login_limit_is_not_diluted_by_public_index_queries():
    attempts = [
        SearchAttempt(
            attempt_id="public-1", target_id=TARGET.target_id,
            platform=Platform.XIAOHONGSHU, query="site query 1", method="public_web_search",
            attempted_at=datetime(2026, 8, 1, tzinfo=UTC), outcome="no_results",
        ),
        SearchAttempt(
            attempt_id="public-2", target_id=TARGET.target_id,
            platform=Platform.XIAOHONGSHU, query="site query 2", method="public_web_search",
            attempted_at=datetime(2026, 8, 2, tzinfo=UTC), outcome="no_results",
        ),
        SearchAttempt(
            attempt_id="browser-1", target_id=TARGET.target_id,
            platform=Platform.XIAOHONGSHU, query="南京师范大学 电气考研",
            method="user_session_browser", attempted_at=datetime(2026, 8, 3, tzinfo=UTC),
            outcome="access_limited", access_reason="login_required",
        ),
    ]
    result = diagnose_collection(
        target_id=TARGET.target_id, posts=[], attempts=attempts,
        expected_platforms=[Platform.XIAOHONGSHU],
    )
    assert result.status == "access_limited"


def test_three_eligible_observations_are_adequate():
    posts = [post(i, Platform.BILIBILI) for i in range(1, 4)]
    result = diagnose_collection(target_id=TARGET.target_id, posts=posts, attempts=[],
                                 expected_platforms=[Platform.BILIBILI])
    assert result.status == "adequate"
