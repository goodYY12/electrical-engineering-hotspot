from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import httpx


@dataclass(frozen=True)
class FetchResult:
    canonical_url: str
    status_code: int
    media_type: str
    accessed_at: str
    content_hash: str
    raw_path: str
    from_cache: bool


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", parts.query, ""))


class CachedHttpFetcher:
    def __init__(self, cache_dir: Path, *, user_agent: str, delay_seconds: float = 2.0,
                 retries: int = 3, backoff_base: float = 1.5, timeout: float = 30.0) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.delay_seconds = delay_seconds
        self.retries = retries
        self.backoff_base = backoff_base
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent}
        self._last_fetch: dict[str, float] = {}

    def _key(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def fetch(self, url: str, *, refresh: bool = False) -> FetchResult:
        canonical = canonicalize_url(url)
        key = self._key(canonical)
        metadata_path = self.cache_dir / f"{key}.json"
        if metadata_path.exists() and not refresh:
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            payload["from_cache"] = True
            return FetchResult(**payload)

        domain = urlsplit(canonical).netloc
        wait = self.delay_seconds - (time.monotonic() - self._last_fetch.get(domain, 0.0))
        if wait > 0:
            time.sleep(wait)
        error: Exception | None = None
        for attempt in range(self.retries):
            try:
                with httpx.Client(headers=self.headers, follow_redirects=True, timeout=self.timeout) as client:
                    response = client.get(canonical)
                    response.raise_for_status()
                self._last_fetch[domain] = time.monotonic()
                content = response.content
                digest = hashlib.sha256(content).hexdigest()
                suffix = _extension(response.headers.get("content-type", ""))
                raw_path = self.cache_dir / f"{key}-{digest[:12]}{suffix}"
                if not raw_path.exists():
                    raw_path.write_bytes(content)
                result = FetchResult(
                    canonical_url=str(response.url), status_code=response.status_code,
                    media_type=response.headers.get("content-type", "application/octet-stream").split(";")[0],
                    accessed_at=datetime.now(UTC).isoformat(), content_hash=digest,
                    raw_path=str(raw_path), from_cache=False,
                )
                payload = asdict(result)
                payload["from_cache"] = False
                metadata_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                return result
            except (httpx.HTTPError, OSError) as exc:
                error = exc
                if attempt + 1 < self.retries:
                    time.sleep(self.backoff_base ** attempt)
        raise RuntimeError(f"failed to fetch {canonical} after {self.retries} attempts") from error


def _extension(content_type: str) -> str:
    content_type = content_type.lower()
    if "pdf" in content_type:
        return ".pdf"
    if "html" in content_type:
        return ".html"
    if "json" in content_type:
        return ".json"
    if "spreadsheet" in content_type or "excel" in content_type:
        return ".xlsx"
    if "word" in content_type:
        return ".docx"
    return ".bin"
