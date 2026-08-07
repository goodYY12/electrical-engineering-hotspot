from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from electrical_kaoyan.media import platform_from_url, post_from_html, post_from_observation
from electrical_kaoyan.social import (
    MediaTarget,
    Platform,
    SocialPost,
    analyze_heat,
    deduplicate_posts,
    load_heat_rules,
)

RULES = load_heat_rules(Path("config/heat_rules.yaml"))
TARGET = MediaTarget(school="重庆大学", college="电气工程学院", major_code="085801",
                     admission_year=2027)


def make_post(number: int, *, days_ago: int = 1, platform: Platform = Platform.ZHIHU,
              author: str | None = None, text: str | None = None, commercial: bool = False) -> SocialPost:
    body = text or f"重庆大学 085801 择校 专业课讨论 {number}"
    markers = ["咨询"] if commercial else []
    published = datetime(2026, 8, 8, tzinfo=UTC) - timedelta(days=days_ago)
    return SocialPost(
        post_id=f"P{number}", target_id=TARGET.target_id, platform=platform,
        url=f"https://example.com/{number}", title=f"帖子{number}", text=body,
        author_id=author or f"A{number}", published_at=published,
        likes=10, collects=5, comments=3, content_hash=f"{number:064d}",
        commercial_markers=markers, intent_markers=["择校", "专业课"],
    )


def test_public_html_extracts_markers_and_platform():
    html = """<html><head><meta property="og:title" content="重大电气择校">
    <meta name="description" content="085801专业课资料，一对一咨询"></head><body></body></html>"""
    post = post_from_html(url="https://www.zhihu.com/question/1", html=html,
                          target=TARGET, rules=RULES)
    assert post.platform is Platform.ZHIHU
    assert "咨询" in post.commercial_markers
    assert "专业课" in post.intent_markers
    assert platform_from_url("https://www.bilibili.com/video/BV1") is Platform.BILIBILI


def test_browser_observation_is_traceable_and_classified():
    post = post_from_observation(
        url="https://www.xiaohongshu.com/explore/public", target=TARGET,
        platform=Platform.XIAOHONGSHU, title="重大电气择校",
        text="085801专业课怎么复习，不卖资料", rules=RULES,
        author_id="anonymous-1", likes=4, collects=6, comments=2,
        extraction_method="agent_browser",
    )
    assert post.extraction_method == "agent_browser"
    assert post.collects == 6
    assert "择校" in post.intent_markers
    assert post.content_hash


def test_near_duplicates_do_not_inflate_heat():
    posts = [make_post(1, text="重庆大学085801择校专业课怎么准备"),
             make_post(2, text="重庆大学 085801 择校，专业课怎么准备？")]
    result = deduplicate_posts(posts)
    assert sum(item.duplicate_of is not None for item in result) == 1


def test_one_prolific_author_is_capped():
    many = [make_post(i, author="same-author") for i in range(10)]
    report = analyze_heat(many, target_id=TARGET.target_id, as_of=date(2026, 8, 8),
                          expected_platforms=[Platform.ZHIHU], rules=RULES)
    assert report.organic_signal <= RULES["author_contribution_cap"]
    assert report.unique_authors == 1
    assert report.heat_level == "insufficient_data"


def test_commercial_heat_is_separate_and_confidence_reflects_coverage():
    topics = [
        "重庆大学085801择校时应该如何评估统考名额",
        "今年重大电气专业课840电路原理参考书怎么选",
        "本科自动化跨考重庆大学电气工程复习经验",
        "重大电气学硕和专硕研究方向有什么区别",
        "重庆大学电气学院推免人数会不会影响统考",
        "距离初试四个月更换到重大电气是否来得及",
    ]
    posts = [make_post(i, platform=Platform.ZHIHU, text=text) for i, text in enumerate(topics, 1)]
    commercial_topics = [
        "重大电气一对一咨询领取内部资料",
        "重庆大学电气上岸班课程加微信",
        "085801专业课押题资料包购买",
        "电气考研择校咨询课程限时领取",
        "重大840电路原理内部资料一对一",
    ]
    posts.extend(make_post(i, platform=Platform.XIAOHONGSHU, commercial=True, text=text)
                 for i, text in enumerate(commercial_topics, 7))
    report = analyze_heat(posts, target_id=TARGET.target_id, as_of=date(2026, 8, 8),
                          expected_platforms=[Platform.ZHIHU, Platform.XIAOHONGSHU,
                                              Platform.BILIBILI], rules=RULES)
    assert report.organic_posts == 6
    assert report.commercial_posts == 5
    assert report.commercial_signal > 0
    assert report.platform_coverage == 0.667
    assert "applicant count" in report.notes[0]


def test_old_posts_decay_and_missing_platform_is_not_zero_heat():
    recent = [make_post(i, days_ago=1) for i in range(1, 5)]
    old = [make_post(i + 10, days_ago=90) for i in range(1, 5)]
    recent_report = analyze_heat(recent, target_id=TARGET.target_id,
                                 as_of=date(2026, 8, 8), expected_platforms=[Platform.ZHIHU],
                                 rules=RULES)
    old_report = analyze_heat(old, target_id=TARGET.target_id,
                              as_of=date(2026, 8, 8), expected_platforms=[Platform.ZHIHU,
                                                                          Platform.BILIBILI],
                              rules=RULES)
    assert recent_report.organic_signal > old_report.organic_signal
    assert old_report.platform_coverage == 0.5
    assert any("not treated as zero" in note for note in old_report.notes)
