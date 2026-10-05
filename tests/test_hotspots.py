from datetime import UTC, datetime

from electrical_kaoyan.hotspots import (
    DiscoveryItem,
    HotspotTarget,
    cluster_items,
    parse_search_rss,
)

TARGET = HotspotTarget(
    school="重庆大学", college="电气工程学院", major_code="085801", admission_year=2027,
)


def test_search_rss_keeps_only_exact_target_matches_and_deduplicates_urls():
    rss = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0"><channel>
      <item><title>重庆大学 085801 电气工程考研专业课调整</title>
        <link>https://example.com/a?utm_source=test</link><description>2027 招生信息</description></item>
      <item><title>重庆大学 085801 电气工程考研专业课调整</title>
        <link>https://example.com/a</link><description>重复结果</description></item>
      <item><title>某大学计算机考研</title>
        <link>https://example.com/b</link><description>无关结果</description></item>
    </channel></rss>"""
    items = parse_search_rss(rss, query="重庆大学 085801", target=TARGET)
    assert len(items) == 1
    assert items[0].url == "https://example.com/a"
    assert items[0].evidence_tier == "search_snippet"


def test_similar_reports_become_one_event_with_independent_sources():
    now = datetime(2026, 10, 5, tzinfo=UTC)
    items = [
        DiscoveryItem(
            item_id="a", title="重庆大学2027电气工程专业课调整", summary="考试科目发生变化",
            url="https://one.example/a", platform="院校官网", source_host="one.example",
            query="q", observed_at=now, evidence_tier="visible_observation",
            exact_target_match=True,
        ),
        DiscoveryItem(
            item_id="b", title="重庆大学2027电气专业课调整说明", summary="专业课调整说明",
            url="https://two.example/b", platform="知乎", source_host="two.example",
            query="q", observed_at=now, exact_target_match=True,
        ),
    ]
    events = cluster_items(items)
    assert len(events) == 1
    assert events[0].source_count == 2
    assert events[0].category == "专业课变化"
    assert events[0].evidence_tier == "visible_observation"


def test_unrelated_college_is_not_an_exact_target_match():
    from electrical_kaoyan.hotspots import _exact_match

    target = TARGET.model_copy(update={"college": ""})
    assert not _exact_match("计算机学院2027年招生通知", "硕士研究生招生", target)

