from __future__ import annotations

import hashlib
import html
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, quote_plus, urlencode, urljoin, urlsplit, urlunsplit

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, HttpUrl

SEARCH_ENDPOINT = "https://www.bing.com/search?q={query}&format=rss&setlang=zh-CN"
USER_AGENT = "electrical-kaoyan-navigator/0.4 (+public academic research)"


class HotspotTarget(BaseModel):
    school: str = Field(min_length=2, max_length=40)
    college: str = Field(default="", max_length=60)
    major_code: str = Field(default="085801", pattern=r"^\d{6}$")
    admission_year: int = Field(ge=2020, le=2100)
    seed_urls: list[HttpUrl] = Field(default_factory=list, max_length=5)


class DiscoveryItem(BaseModel):
    item_id: str
    title: str
    summary: str
    url: str
    platform: str
    source_host: str
    query: str
    observed_at: datetime
    published_at: datetime | None = None
    evidence_tier: str = "search_snippet"
    exact_target_match: bool = False


class HotspotEvent(BaseModel):
    event_id: str
    title: str
    summary: str
    category: str
    platforms: list[str]
    source_count: int
    item_count: int
    signal_score: float
    trend: str
    latest_at: datetime
    evidence_tier: str
    exact_target_match: bool
    items: list[DiscoveryItem]


class CollectionAttempt(BaseModel):
    query: str
    method: str
    outcome: str
    results_seen: int = 0
    exact_matches: int = 0
    reason: str | None = None


class HotspotSnapshot(BaseModel):
    generated_at: datetime
    target: HotspotTarget
    status: str
    status_label: str
    events: list[HotspotEvent]
    attempts: list[CollectionAttempt]
    metrics: dict[str, int | float]
    limitations: list[str]


def query_plan(target: HotspotTarget) -> list[tuple[str, str]]:
    core = " ".join(part for part in (
        target.school, target.college, target.major_code, str(target.admission_year), "电气 考研"
    ) if part)
    return [
        ("全网", f"{core} 招生目录 专业课 复试"),
        ("知乎", f"site:zhihu.com {core}"),
        ("哔哩哔哩", f"site:bilibili.com {core}"),
        ("小红书", f"site:xiaohongshu.com {core}"),
    ]


def _canonical_url(url: str) -> str:
    parts = urlsplit(url)
    query = urlencode([
        (key, value) for key, value in parse_qsl(parts.query)
        if not key.lower().startswith(("utm_", "spm", "from"))
    ])
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", query, ""))


def _plain_text(value: str | None) -> str:
    return BeautifulSoup(html.unescape(value or ""), "html.parser").get_text(" ", strip=True)


def _platform(url: str) -> str:
    host = urlsplit(url).netloc.lower()
    if "zhihu.com" in host:
        return "知乎"
    if "bilibili.com" in host:
        return "哔哩哔哩"
    if "xiaohongshu.com" in host:
        return "小红书"
    if "weixin.qq.com" in host:
        return "公众号"
    return "公开网页"


def _exact_match(title: str, summary: str, target: HotspotTarget) -> bool:
    text = f"{title} {summary}".lower()
    school = re.sub(r"大学$", "", target.school.lower())
    school_match = target.school.lower() in text or (len(school) >= 2 and school in text)
    program_match = target.major_code in text or "电气" in text
    return school_match and program_match


def _parse_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        value = parsedate_to_datetime(raw)
    except (TypeError, ValueError, OverflowError):
        return None
    return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)


def parse_search_rss(xml: str, *, query: str, target: HotspotTarget,
                     observed_at: datetime | None = None) -> list[DiscoveryItem]:
    observed = observed_at or datetime.now(UTC)
    root = ET.fromstring(xml)
    items: list[DiscoveryItem] = []
    seen: set[str] = set()
    for node in root.findall(".//item"):
        title = _plain_text(node.findtext("title"))
        summary = _plain_text(node.findtext("description"))
        url = _canonical_url((node.findtext("link") or "").strip())
        if not title or not url or url in seen:
            continue
        seen.add(url)
        exact = _exact_match(title, summary, target)
        if not exact:
            continue
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        items.append(DiscoveryItem(
            item_id=f"search-{digest}", title=title, summary=summary, url=url,
            platform=_platform(url), source_host=urlsplit(url).netloc.lower(), query=query,
            observed_at=observed, published_at=_parse_date(node.findtext("pubDate")),
            exact_target_match=True,
        ))
    return items


def search_public_web(query: str, *, target: HotspotTarget,
                      client: httpx.Client | None = None) -> list[DiscoveryItem]:
    owned = client is None
    session = client or httpx.Client(
        headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=20,
    )
    try:
        response = session.get(SEARCH_ENDPOINT.format(query=quote_plus(query)))
        response.raise_for_status()
        return parse_search_rss(response.text, query=query, target=target)
    finally:
        if owned:
            session.close()


def crawl_seed_page(url: str, *, target: HotspotTarget,
                    client: httpx.Client | None = None) -> list[DiscoveryItem]:
    owned = client is None
    session = client or httpx.Client(
        headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=20,
    )
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        observed = datetime.now(UTC)
        items: list[DiscoveryItem] = []
        seen: set[str] = set()
        page_title = soup.title.get_text(" ", strip=True) if soup.title else ""
        page_heading = soup.find("h1").get_text(" ", strip=True) if soup.find("h1") else ""
        description_node = soup.find("meta", attrs={"name": "description"})
        page_description = str(description_node.get("content", "")) if description_node else ""
        page_text = soup.get_text(" ", strip=True)
        if page_title and _exact_match(page_title, f"{page_heading} {page_description}", target):
            page_url = _canonical_url(str(response.url))
            digest = hashlib.sha256(page_url.encode("utf-8")).hexdigest()[:16]
            items.append(DiscoveryItem(
                item_id=f"page-{digest}", title=page_title, summary=page_text[:280],
                url=page_url, platform="院校官网",
                source_host=urlsplit(page_url).netloc.lower(), query=str(response.url),
                observed_at=observed, evidence_tier="public_html", exact_target_match=True,
            ))
            seen.add(page_url)
        for anchor in soup.find_all("a", href=True):
            title = anchor.get_text(" ", strip=True)
            context = anchor.parent.get_text(" ", strip=True) if anchor.parent else title
            if not title or not _seed_link_match(title, context, target):
                continue
            item_url = _canonical_url(urljoin(str(response.url), str(anchor["href"])))
            if item_url in seen:
                continue
            seen.add(item_url)
            digest = hashlib.sha256(item_url.encode("utf-8")).hexdigest()[:16]
            items.append(DiscoveryItem(
                item_id=f"seed-{digest}", title=title, summary=context[:280], url=item_url,
                platform="院校官网", source_host=urlsplit(item_url).netloc.lower(),
                query=str(response.url), observed_at=observed,
                evidence_tier="visible_observation", exact_target_match=_exact_match(title, context, target),
            ))
            if len(items) >= 20:
                break
        return items
    finally:
        if owned:
            session.close()


def _seed_link_match(title: str, context: str, target: HotspotTarget) -> bool:
    text = f"{title} {context}"
    year_tokens = {str(target.admission_year), str(target.admission_year - 1)}
    intent = any(term in text for term in (
        "招生", "目录", "考试大纲", "专业课", "推免", "复试", "拟录取", "调剂",
    ))
    target_term = (
        target.major_code in text or "电气" in text
        or bool(target.college and target.college in text)
    )
    return intent and (target_term or any(year in text for year in year_tokens))


def _title_terms(value: str) -> set[str]:
    compact = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", value.lower())
    return {compact[index:index + 2] for index in range(max(len(compact) - 1, 0))}


def _similar(left: str, right: str) -> bool:
    first, second = _title_terms(left), _title_terms(right)
    if not first or not second:
        return left == right
    return len(first & second) / len(first | second) >= 0.38


def _category(items: list[DiscoveryItem]) -> str:
    text = " ".join(item.title for item in items)
    for label, terms in (
        ("专业课变化", ("专业课", "考试大纲", "科目", "改考")),
        ("招生政策", ("招生", "目录", "计划", "推免")),
        ("复试录取", ("复试", "拟录取", "调剂", "分数线")),
        ("备考讨论", ("经验", "备考", "真题", "择校")),
    ):
        if any(term in text for term in terms):
            return label
    return "其他动态"


def cluster_items(items: list[DiscoveryItem], *, previous: HotspotSnapshot | None = None) -> list[HotspotEvent]:
    groups: list[list[DiscoveryItem]] = []
    for item in sorted(items, key=lambda entry: entry.published_at or entry.observed_at, reverse=True):
        group = next((candidate for candidate in groups if _similar(candidate[0].title, item.title)), None)
        if group is None:
            groups.append([item])
        else:
            group.append(item)
    previous_scores = {event.event_id: event.signal_score for event in previous.events} if previous else {}
    events = []
    for group in groups:
        platforms = sorted({item.platform for item in group})
        hosts = {item.source_host for item in group}
        exact = all(item.exact_target_match for item in group)
        visible = any(item.evidence_tier != "search_snippet" for item in group)
        score = round(len(hosts) * 10 + len(platforms) * 6 + min(len(group), 5) * 2.5, 1)
        fingerprint = "|".join(sorted(re.sub(r"\W+", "", item.title.lower()) for item in group))
        event_id = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]
        old_score = previous_scores.get(event_id)
        trend = "new" if old_score is None else "up" if score > old_score else "flat"
        lead = group[0]
        events.append(HotspotEvent(
            event_id=event_id, title=lead.title, summary=lead.summary,
            category=_category(group), platforms=platforms, source_count=len(hosts),
            item_count=len(group), signal_score=score, trend=trend,
            latest_at=max(item.published_at or item.observed_at for item in group),
            evidence_tier=(
                "public_html" if any(item.evidence_tier == "public_html" for item in group)
                else "visible_observation" if visible else "search_snippet"
            ),
            exact_target_match=exact, items=group,
        ))
    return sorted(events, key=lambda event: (event.signal_score, event.latest_at), reverse=True)


def collect_hotspots(target: HotspotTarget, *, previous: HotspotSnapshot | None = None) -> HotspotSnapshot:
    attempts: list[CollectionAttempt] = []
    all_items: list[DiscoveryItem] = []
    with httpx.Client(headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=20) as client:
        for label, query in query_plan(target):
            try:
                found = search_public_web(query, target=target, client=client)
                all_items.extend(found)
                attempts.append(CollectionAttempt(
                    query=query, method=f"public_search:{label}",
                    outcome="success" if found else "no_results",
                    results_seen=len(found), exact_matches=len(found),
                ))
            except (httpx.HTTPError, ET.ParseError, OSError, ValueError) as exc:
                attempts.append(CollectionAttempt(
                    query=query, method=f"public_search:{label}", outcome="error",
                    reason=str(exc)[:300],
                ))
        for seed in target.seed_urls:
            url = str(seed)
            try:
                found = crawl_seed_page(url, target=target, client=client)
                all_items.extend(found)
                attempts.append(CollectionAttempt(
                    query=url, method="official_seed", outcome="success" if found else "no_results",
                    results_seen=len(found), exact_matches=sum(item.exact_target_match for item in found),
                ))
            except (httpx.HTTPError, OSError, ValueError) as exc:
                attempts.append(CollectionAttempt(
                    query=url, method="official_seed", outcome="error", reason=str(exc)[:300],
                ))
    unique = {item.url: item for item in all_items}
    exact_observations = [item for item in unique.values() if item.exact_target_match]
    events = cluster_items(exact_observations, previous=previous)
    failures = sum(attempt.outcome == "error" for attempt in attempts)
    exact_items = sum(item.exact_target_match for item in unique.values())
    visible_items = sum(
        item.evidence_tier != "search_snippet" for item in exact_observations
    )
    if events and visible_items:
        status, label = "mixed_evidence", "已获得官网观察与公开线索"
    elif events:
        status, label = "indexing_gap", "已获得搜索线索，原页仍待核验"
    elif failures == len(attempts):
        status, label = "access_limited", "采集通道暂时不可用"
    else:
        status, label = "collection_incomplete", "本轮未发现精确匹配"
    platform_counts: dict[str, int] = defaultdict(int)
    for item in unique.values():
        platform_counts[item.platform] += 1
    limitations = [
        "线索指数只描述公开网页中的可见度，不能换算报名人数、报录比或录取概率。",
        "搜索摘要属于代理证据；请打开原页核验发布时间、目标学院与专业范围。",
    ]
    if not target.seed_urls:
        limitations.append("未提供院校官方入口，本轮主要依赖公开搜索索引。")
    return HotspotSnapshot(
        generated_at=datetime.now(UTC), target=target, status=status, status_label=label,
        events=events, attempts=attempts,
        metrics={
            "events": len(events), "items": len(unique), "exact_items": exact_items,
            "visible_items": visible_items, "platforms": len(platform_counts), "failures": failures,
        },
        limitations=limitations,
    )

