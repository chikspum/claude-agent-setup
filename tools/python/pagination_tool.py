"""
Pagination detection tool.

Detects next/previous page URLs from HTML content.
Works on static HTML and on already-rendered JS pages (caller provides rendered HTML).
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from skills import SkillInput, SkillOutput

log = logging.getLogger(__name__)

# ── helpers ──────────────────────────────────────────────────────────────────

# Text patterns that signal "next page" / "prev page" links (case-insensitive).
_NEXT_TEXTS = re.compile(
    r"^\s*(next(\s*page)?|older(\s*posts)?|›|»|>>|→|▶)\s*$",
    re.IGNORECASE,
)
_PREV_TEXTS = re.compile(
    r"^\s*(prev(ious)?(\s*page)?|newer(\s*posts)?|‹|«|<<|←|◀)\s*$",
    re.IGNORECASE,
)

# CSS class / id fragments that hint at next/prev controls.
_NEXT_CLASS = re.compile(
    r"(^|\b)(next|page-?next|pagination-?next|nav-?next)(\b|$)",
    re.IGNORECASE,
)
_PREV_CLASS = re.compile(
    r"(^|\b)(prev(ious)?|page-?prev|pagination-?prev|nav-?prev)(\b|$)",
    re.IGNORECASE,
)

# aria-label patterns
_NEXT_ARIA = re.compile(r"next(\s*page)?", re.IGNORECASE)
_PREV_ARIA = re.compile(r"prev(ious)?(\s*page)?", re.IGNORECASE)


def _resolve(href: str | None, base_url: str) -> str | None:
    """Return absolute URL, or None if href is empty/unusable."""
    if not href or href.startswith(("#", "javascript:")):
        return None
    return urljoin(base_url, href) if base_url else href


def _find_url(soup: BeautifulSoup, base_url: str, direction: str) -> str | None:
    """
    Try each strategy in priority order; return the first URL found.

    direction: "next" | "prev"
    """
    text_re = _NEXT_TEXTS if direction == "next" else _PREV_TEXTS
    class_re = _NEXT_CLASS if direction == "next" else _PREV_CLASS
    aria_re = _NEXT_ARIA if direction == "next" else _PREV_ARIA
    rel_val = direction  # HTML rel="next" / rel="prev"

    # 1. <link rel="next|prev"> in <head>
    link = soup.find("link", rel=rel_val)
    if link:
        url = _resolve(link.get("href"), base_url)
        if url:
            log.debug("pagination found via <link rel=%s>: %s", direction, url)
            return url

    # 2. <a rel="next|prev">
    anchor = soup.find("a", rel=rel_val)
    if anchor:
        url = _resolve(anchor.get("href"), base_url)
        if url:
            log.debug("pagination found via <a rel=%s>: %s", direction, url)
            return url

    # 3. aria-label on <a>
    for tag in soup.find_all("a", attrs={"aria-label": True}):
        if aria_re.search(tag["aria-label"]):
            url = _resolve(tag.get("href"), base_url)
            if url:
                log.debug("pagination found via aria-label=%s: %s", tag["aria-label"], url)
                return url

    # 4. CSS class / id hints on <a> or its parent
    for tag in soup.find_all(["a", "li", "span", "div"]):
        classes = " ".join(tag.get("class", []))
        tag_id = tag.get("id", "")
        if class_re.search(classes) or class_re.search(tag_id):
            anchor = tag if tag.name == "a" else tag.find("a")
            if anchor:
                url = _resolve(anchor.get("href"), base_url)
                if url:
                    log.debug("pagination found via class/id hint: %s", url)
                    return url

    # 5. Text content heuristic on <a>
    for tag in soup.find_all("a"):
        visible = tag.get_text(strip=True)
        if text_re.match(visible):
            url = _resolve(tag.get("href"), base_url)
            if url:
                log.debug("pagination found via text heuristic '%s': %s", visible, url)
                return url

    return None


# ── public skills ─────────────────────────────────────────────────────────────


def get_next_page_url(input: SkillInput) -> SkillOutput:
    """Return the URL of the next page detected in the provided HTML.

    input.data     — raw HTML string (static or JS-rendered)
    input.options  — optional dict:
        "base_url" (str): used to resolve relative hrefs (e.g. "https://example.com/blog/")
    """
    base_url: str = (input.options or {}).get("base_url", "")
    try:
        soup = BeautifulSoup(input.data, "lxml")
        url = _find_url(soup, base_url, "next")
        if url:
            return SkillOutput(result=url, success=True)
        return SkillOutput(result="", success=True, error="no next page found")
    except Exception as exc:
        log.exception("get_next_page_url failed")
        return SkillOutput(result="", success=False, error=str(exc))


def get_prev_page_url(input: SkillInput) -> SkillOutput:
    """Return the URL of the previous page detected in the provided HTML.

    input.data     — raw HTML string (static or JS-rendered)
    input.options  — optional dict:
        "base_url" (str): used to resolve relative hrefs (e.g. "https://example.com/blog/")
    """
    base_url: str = (input.options or {}).get("base_url", "")
    try:
        soup = BeautifulSoup(input.data, "lxml")
        url = _find_url(soup, base_url, "prev")
        if url:
            return SkillOutput(result=url, success=True)
        return SkillOutput(result="", success=True, error="no previous page found")
    except Exception as exc:
        log.exception("get_prev_page_url failed")
        return SkillOutput(result="", success=False, error=str(exc))
