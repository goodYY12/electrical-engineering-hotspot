from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from datetime import UTC, date, datetime
from difflib import SequenceMatcher
from enum import StrEnum
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, HttpUrl


class Platform(StrEnum):
    XIAOHONGSHU = "xiaohongshu"
    ZHIHU = "zhihu"
    BILIBILI = "bilibili"
    WECHAT = "wechat"
    WEIBO = "weibo"
    FORUM = "forum"
    NEWS = "news"
    OTHER = "other"


class MediaTarget(BaseModel):
    school: str
    college: str | None = None
    major_code: str | None = Field(default=None, pattern=r"^\d{6}$")
    major_name: str | None = None
    admission_year: int | None = None

    @property
    def target_id(self) -> str:
        raw = json.dumps(self.model_dump(), ensure_ascii=False, sort_keys=True)
        return "target-" + hashlib.sha256(raw.encode()).hexdigest()[:16]


class SocialPost(BaseModel):
    post_id: str
    target_id: str
    platform: Platform
    url: HttpUrl
    title: str
    text: str
    author_id: str | None = None
    author_self_description: str | None = None
    published_at: datetime | None = None
    captured_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    likes: int | None = Field(default=None, ge=0)
    collects: int | None = Field(default=None, ge=0)
    comments: int | None = Field(default=None, ge=0)
    query: str | None = None
    extraction_method: str = "public_html"
    content_hash: str
    access_limited: bool = False
    commercial_markers: list[str] = Field(default_factory=list)
    intent_markers: list[str] = Field(default_factory=list)
    duplicate_of: str | None = None

    @property
    def is_commercial(self) -> bool:
        return bool(self.commercial_markers)


class HeatReport(BaseModel):
    target_id: str
    as_of: date
    observation_start: date | None
    observation_end: date | None
    heat_level: Literal["very_low", "low", "medium", "high", "very_high", "insufficient_data"]
    momentum: Literal["falling", "stable", "rising", "unknown"]
    confidence: Literal["low", "medium", "high"]
    organic_signal: float
    commercial_signal: float
    total_posts: int
    unique_posts: int
    duplicate_posts: int
    organic_posts: int
    commercial_posts: int
    unique_authors: int
    observed_platforms: list[Platform]
    expected_platforms: list[Platform]
    platform_coverage: float
    notes: list[str]


def load_heat_rules(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]+", "", text.lower())


def classify_markers(text: str, rules: dict) -> tuple[list[str], list[str]]:
    commercial = [marker for marker in rules["commercial_markers"] if marker in text]
    intent = [marker for marker in rules["intent_markers"] if marker in text]
    return commercial, intent


def deduplicate_posts(posts: list[SocialPost], *, threshold: float = 0.9) -> list[SocialPost]:
    representatives: list[tuple[str, str]] = []
    output: list[SocialPost] = []
    seen_urls: dict[str, str] = {}
    for post in sorted(posts, key=lambda item: (item.published_at or item.captured_at, item.post_id)):
        url = str(post.url)
        normalized = normalize_text(post.title + post.text)
        duplicate_of = seen_urls.get(url)
        if duplicate_of is None:
            for representative_id, representative_text in representatives:
                if normalized and SequenceMatcher(None, normalized, representative_text).ratio() >= threshold:
                    duplicate_of = representative_id
                    break
        updated = post.model_copy(update={"duplicate_of": duplicate_of})
        output.append(updated)
        if duplicate_of is None:
            seen_urls[url] = post.post_id
            representatives.append((post.post_id, normalized))
    return output


def _engagement(post: SocialPost, rules: dict) -> float:
    weights = rules["engagement_weights"]
    weighted = (
        (post.likes or 0) * weights["like"]
        + (post.collects or 0) * weights["collect"]
        + (post.comments or 0) * weights["comment"]
    )
    return 1.0 + math.log1p(weighted)


def _recency(post: SocialPost, as_of: date, half_life: float) -> float:
    source_date = (post.published_at or post.captured_at).date()
    age = max((as_of - source_date).days, 0)
    return math.pow(0.5, age / half_life)


def _level(signal: float, authors: int, organic_posts: int) -> str:
    if organic_posts < 3 or authors < 2:
        return "insufficient_data"
    if signal < 3:
        return "very_low"
    if signal < 7:
        return "low"
    if signal < 15:
        return "medium"
    if signal < 30:
        return "high"
    return "very_high"


def analyze_heat(posts: list[SocialPost], *, target_id: str, as_of: date,
                 expected_platforms: list[Platform], rules: dict) -> HeatReport:
    relevant = [post for post in posts if post.target_id == target_id]
    deduped = deduplicate_posts(relevant)
    unique = [post for post in deduped if post.duplicate_of is None and not post.access_limited]
    half_life = float(rules["recency_half_life_days"])
    author_cap = float(rules["author_contribution_cap"])
    commercial_weight = float(rules["commercial_weight"])
    author_organic: dict[str, float] = defaultdict(float)
    commercial_signal = 0.0
    dated_signals: list[tuple[date, float]] = []
    for post in unique:
        signal = _engagement(post, rules) * _recency(post, as_of, half_life)
        if not post.intent_markers:
            signal *= 0.5
        if post.is_commercial:
            commercial_signal += signal * commercial_weight
        else:
            author = post.author_id or f"unknown:{post.post_id}"
            before = author_organic[author]
            author_organic[author] = min(before + signal, author_cap)
            dated_signals.append(((post.published_at or post.captured_at).date(), signal))
    organic_signal = sum(author_organic.values())
    organic = [post for post in unique if not post.is_commercial]
    commercial = [post for post in unique if post.is_commercial]
    observed = sorted({post.platform for post in unique})
    expected = sorted(set(expected_platforms))
    coverage = len(set(observed) & set(expected)) / len(expected) if expected else 1.0
    authors = len(author_organic)
    heat_level = _level(organic_signal, authors, len(organic))

    momentum: str = "unknown"
    if len(dated_signals) >= 4:
        start = min(item[0] for item in dated_signals)
        end = max(item[0] for item in dated_signals)
        midpoint = start + (end - start) / 2
        earlier = sum(value for day, value in dated_signals if day <= midpoint)
        later = sum(value for day, value in dated_signals if day > midpoint)
        if earlier > 0:
            ratio = later / earlier
            momentum = "rising" if ratio >= 1.25 else "falling" if ratio <= 0.8 else "stable"

    commercial_share = len(commercial) / len(unique) if unique else 0.0
    high_confidence = (
        coverage >= 0.9 and authors >= 8 and len(organic) >= 12 and commercial_share < 0.35
    )
    medium_confidence = (
        coverage >= 0.5 and authors >= 5 and len(organic) >= 8 and commercial_share < 0.7
    )
    confidence = "high" if high_confidence else "medium" if medium_confidence else "low"
    notes = ["Heat is an attention signal, not an applicant count or admission forecast."]
    if coverage < 1:
        notes.append("Platform coverage is incomplete; absent platforms are not treated as zero heat.")
    if commercial_share >= 0.5:
        notes.append("Commercial content is at least half of unique observations; confidence is reduced.")
    if heat_level == "insufficient_data":
        notes.append("Too few independent organic observations for an ordinal heat level.")
    dates = [(post.published_at or post.captured_at).date() for post in unique]
    return HeatReport(
        target_id=target_id, as_of=as_of,
        observation_start=min(dates) if dates else None,
        observation_end=max(dates) if dates else None,
        heat_level=heat_level, momentum=momentum, confidence=confidence,
        organic_signal=round(organic_signal, 2), commercial_signal=round(commercial_signal, 2),
        total_posts=len(relevant), unique_posts=len(unique),
        duplicate_posts=sum(post.duplicate_of is not None for post in deduped),
        organic_posts=len(organic), commercial_posts=len(commercial), unique_authors=authors,
        observed_platforms=observed, expected_platforms=expected,
        platform_coverage=round(coverage, 3), notes=notes,
    )
