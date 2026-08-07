from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from .fetchers import CachedHttpFetcher
from .social import (
    HeatReport,
    MediaTarget,
    Platform,
    SocialPost,
    classify_markers,
    deduplicate_posts,
)

PLATFORM_DOMAINS = {
    "xiaohongshu.com": Platform.XIAOHONGSHU,
    "zhihu.com": Platform.ZHIHU,
    "bilibili.com": Platform.BILIBILI,
    "weixin.qq.com": Platform.WECHAT,
    "weibo.com": Platform.WEIBO,
}


def platform_from_url(url: str) -> Platform:
    host = urlsplit(url).netloc.lower().removeprefix("www.")
    for domain, platform in PLATFORM_DOMAINS.items():
        if host == domain or host.endswith("." + domain):
            return platform
    return Platform.OTHER


def _meta(soup: BeautifulSoup, *names: str) -> str | None:
    for name in names:
        node = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
        if node and node.get("content"):
            return str(node["content"]).strip()
    return None


def _published_at(soup: BeautifulSoup) -> datetime | None:
    raw = _meta(soup, "article:published_time", "datePublished", "publishdate")
    if raw:
        try:
            parsed = datetime.fromisoformat(raw)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            pass
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            payload = json.loads(script.string or "null")
        except json.JSONDecodeError:
            continue
        nodes = payload if isinstance(payload, list) else [payload]
        for node in nodes:
            if isinstance(node, dict) and node.get("datePublished"):
                try:
                    parsed = datetime.fromisoformat(str(node["datePublished"]))
                    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
                except ValueError:
                    continue
    return None


def post_from_html(*, url: str, html: str, target: MediaTarget, rules: dict,
                   query: str | None = None, content_hash: str | None = None) -> SocialPost:
    soup = BeautifulSoup(html, "html.parser")
    title = _meta(soup, "og:title", "twitter:title") or (soup.title.get_text(strip=True) if soup.title else "")
    description = _meta(soup, "og:description", "description") or ""
    article = soup.find("article") or soup.find("main") or soup.body
    body = article.get_text(" ", strip=True) if article else ""
    text = description if len(description) >= len(body) else body
    combined = f"{title}\n{text}"
    commercial, intent = classify_markers(combined, rules)
    digest = content_hash or hashlib.sha256(html.encode("utf-8")).hexdigest()
    post_id = f"post-{digest[:20]}"
    author = _meta(soup, "author", "article:author")
    return SocialPost(
        post_id=post_id, target_id=target.target_id, platform=platform_from_url(url),
        url=url, title=title, text=text, author_id=author, published_at=_published_at(soup),
        query=query, content_hash=digest, commercial_markers=commercial, intent_markers=intent,
    )


def collect_public_url(*, url: str, target: MediaTarget, output: Path, cache: Path,
                       rules: dict, query: str | None = None, refresh: bool = False) -> SocialPost:
    fetcher = CachedHttpFetcher(cache, user_agent="electrical-kaoyan-navigator/0.2",
                                delay_seconds=2.0)
    result = fetcher.fetch(url, refresh=refresh)
    raw = Path(result.raw_path)
    if result.media_type not in {"text/html", "application/xhtml+xml"}:
        raise ValueError(f"media collector currently expects public HTML, got {result.media_type}")
    html = raw.read_text(encoding="utf-8", errors="replace")
    post = post_from_html(url=result.canonical_url, html=html, target=target, rules=rules,
                          query=query, content_hash=result.content_hash)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as stream:
        stream.write(post.model_dump_json() + "\n")
    return post


def post_from_observation(*, url: str, target: MediaTarget, platform: Platform, title: str,
                          text: str, rules: dict, author_id: str | None = None,
                          published_at: datetime | None = None, likes: int | None = None,
                          collects: int | None = None, comments: int | None = None,
                          query: str | None = None,
                          extraction_method: str = "agent_browser") -> SocialPost:
    combined = f"{title}\n{text}"
    commercial, intent = classify_markers(combined, rules)
    fingerprint = json.dumps({
        "url": url, "title": title, "text": text, "author_id": author_id,
        "published_at": published_at.isoformat() if published_at else None,
    }, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
    return SocialPost(
        post_id=f"post-{digest[:20]}", target_id=target.target_id, platform=platform,
        url=url, title=title, text=text, author_id=author_id, published_at=published_at,
        likes=likes, collects=collects, comments=comments, query=query,
        extraction_method=extraction_method, content_hash=digest,
        commercial_markers=commercial, intent_markers=intent,
    )


def append_post(path: Path, post: SocialPost) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(post.model_dump_json() + "\n")


def read_posts(path: Path) -> list[SocialPost]:
    return [SocialPost.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_media_evidence(*, path: Path, target: MediaTarget, posts: list[SocialPost],
                         report: HeatReport, rules: dict) -> None:
    """Write the inputs and method behind a heat report as a reproducible ledger."""
    rules_json = json.dumps(rules, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "target": target.model_dump(mode="json"),
        "rules_sha256": hashlib.sha256(rules_json.encode("utf-8")).hexdigest(),
        "report": report.model_dump(mode="json"),
        "observations": [post.model_dump(mode="json") for post in deduplicate_posts(posts)],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
