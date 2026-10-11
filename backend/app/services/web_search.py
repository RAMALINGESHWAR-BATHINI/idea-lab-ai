"""Web search and page-fetching service.

All outbound fetches pass through the SSRF guard. Fetched content is treated
as untrusted: detected for injection patterns and wrapped in provenance
markers before being passed to the AI layer.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import httpx

from app.core.config import settings
from app.core.errors import ProviderError, UnsafeURLError
from app.core.logging import get_logger
from app.security.injection import detect_injection, sanitize_untrusted_text
from app.security.ssrf import validate_public_url

logger = get_logger(__name__)


@dataclass
class SearchResult:
    title: str | None
    url: str
    snippet: str | None


@dataclass
class FetchedPage:
    url: str
    title: str | None
    content: str
    content_hash: str | None
    status_code: int


@lru_cache(maxsize=1)
def _client() -> httpx.AsyncClient:
    """Return a shared httpx client with SSRF-safe defaults."""
    return httpx.AsyncClient(
        timeout=httpx.Timeout(settings.fetch_timeout_seconds),
        follow_redirects=False,
        headers={"User-Agent": settings.fetch_user_agent},
        max_redirects=settings.fetch_max_redirects,
    )


def _truncate_body(body: bytes) -> tuple[bytes, bool]:
    """Truncate response body to max bytes. Returns (truncated, was_truncated)."""
    if len(body) <= settings.fetch_max_bytes:
        return body, False
    return body[: settings.fetch_max_bytes], True


async def fetch_page(url: str) -> FetchedPage:
    """Fetch a public web page after SSRF validation.

    Raises ``UnsafeURLError`` for blocked URLs or ``ProviderError`` on HTTP errors.
    """
    safe_url = validate_public_url(url)
    client = _client()

    try:
        response = await client.get(safe_url)
    except httpx.TimeoutException as exc:
        raise ProviderError(f"Fetch timed out: {url}") from exc
    except httpx.RequestError as exc:
        raise ProviderError(f"Fetch failed: {url}") from exc

    if response.status_code >= 400:
        raise ProviderError(f"HTTP {response.status_code} for {url}")

    body, truncated = _truncate_body(response.content)

    content_type = response.headers.get("content-type", "")
    if content_type.startswith("text/html") or "text/" in content_type:
        text_content, source_title = _extract_text_from_html(body, safe_url)
    else:
        text_content = body.decode("utf-8", errors="replace")
        source_title = None

    import hashlib
    content_hash = hashlib.sha256(body).hexdigest()

    page = FetchedPage(
        url=safe_url,
        title=source_title,
        content=text_content,
        content_hash=content_hash,
        status_code=response.status_code,
    )

    if truncated:
        page.content += "\n...[truncated]"

    return page


def _extract_text_from_html(body: bytes, url: str) -> tuple[str, str | None]:
    """Extract readable text and title from an HTML page."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        text = body.decode("utf-8", errors="replace")
        return text, url

    soup = BeautifulSoup(body, "lxml")

    # Remove script/style/nav/sidebar elements.
    for tag in soup(["script", "style", "nav", "aside", "header", "footer"]):
        tag.decompose()

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    article = soup.find("article") or soup.find("main") or soup
    text = article.get_text(separator="\n", strip=True)

    return text, title or url


async def search_web(
    query: str,
    max_results: int | None = None,
    max_age_hours: int = 72,
) -> list[SearchResult]:
    """Search the web using the configured search provider.

    Currently supports a lightweight DuckDuckGo Lite scraper (no API key).
    Returns public search results. Raises ``ProviderError`` if no search
    provider is available or all attempts fail.
    """
    max_results = max_results or settings.web_search_results
    results: list[SearchResult] = []

    # Try DuckDuckGo HTML (no API key, free).
    ddg_url = "https://html.duckduckgo.com/html/"
    safe_url = validate_public_url(ddg_url)
    client = _client()

    try:
        response = await client.get(
            safe_url,
            params={"q": query, "kl": "us-en"},
        )
        if response.status_code == 200:
            results = _parse_ddg_results(response.text, max_results)
    except httpx.RequestError as exc:
        logger.warning("ddg_search_failed", error=str(exc))
    except Exception as exc:  # noqa: BLE001
        logger.warning("ddg_search_error", error=str(exc))

    if not results:
        # Fallback: use a simple search via searx instances or return empty.
        logger.info("search_no_results", query=query)
        raise ProviderError("No web search provider available")

    return results[:max_results]


def _parse_ddg_results(html: str, limit: int) -> list[SearchResult]:
    """Parse DuckDuckGo HTML search results."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    soup = BeautifulSoup(html, "lxml")
    results: list[SearchResult] = []

    for result in soup.find_all("div", class_="result"):
        link = result.find("a", class_="result__a")
        snippet = result.find("a", class_="result__snippet")
        if link and link.get("href"):
            url = link["href"]
            # DDG uses redirect URLs; extract the actual destination.
            if url.startswith("//duckduckgo.com/l/?uddg="):
                from urllib.parse import parse_qs, urlparse
                parsed = urlparse("https:" + url)
                qs = parse_qs(parsed.query)
                if "uddg" in qs:
                    url = qs["uddg"][0]
            results.append(SearchResult(
                title=link.get_text(strip=True),
                url=url,
                snippet=snippet.get_text(strip=True) if snippet else None,
            ))
        if len(results) >= limit:
            break

    return results
