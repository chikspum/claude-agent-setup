"""Tests for tools/python/pagination_tool.py."""

from pagination_tool import get_next_page_url, get_prev_page_url
from skills import SkillInput

# ── fixtures ──────────────────────────────────────────────────────────────────

LINK_REL_HTML = """
<html><head>
  <link rel="next" href="/page/3">
  <link rel="prev" href="/page/1">
</head><body></body></html>
"""

A_REL_HTML = """
<html><body>
  <a rel="next" href="/page/3">Next</a>
  <a rel="prev" href="/page/1">Prev</a>
</body></html>
"""

ARIA_HTML = """
<html><body>
  <a aria-label="Next page" href="/page/3">›</a>
  <a aria-label="Previous page" href="/page/1">‹</a>
</body></html>
"""

CLASS_HTML = """
<html><body>
  <div class="pagination">
    <a class="pagination-prev" href="/page/1">Prev</a>
    <a class="pagination-next" href="/page/3">Next</a>
  </div>
</body></html>
"""

TEXT_HTML = """
<html><body>
  <nav>
    <a href="/page/1">«</a>
    <a href="/page/3">»</a>
  </nav>
</body></html>
"""

NO_PAGINATION_HTML = "<html><body><p>No pagination here.</p></body></html>"

RELATIVE_BASE = "https://example.com/blog/"


# ── next page ─────────────────────────────────────────────────────────────────


def test_next_via_link_rel():
    out = get_next_page_url(SkillInput(data=LINK_REL_HTML, options={"base_url": RELATIVE_BASE}))
    assert out.success is True
    assert out.result == "https://example.com/page/3"


def test_next_via_a_rel():
    out = get_next_page_url(SkillInput(data=A_REL_HTML, options={"base_url": RELATIVE_BASE}))
    assert out.success is True
    assert out.result == "https://example.com/page/3"


def test_next_via_aria_label():
    out = get_next_page_url(SkillInput(data=ARIA_HTML, options={"base_url": RELATIVE_BASE}))
    assert out.success is True
    assert out.result == "https://example.com/page/3"


def test_next_via_css_class():
    out = get_next_page_url(SkillInput(data=CLASS_HTML, options={"base_url": RELATIVE_BASE}))
    assert out.success is True
    assert out.result == "https://example.com/page/3"


def test_next_via_text_symbol():
    out = get_next_page_url(SkillInput(data=TEXT_HTML, options={"base_url": RELATIVE_BASE}))
    assert out.success is True
    assert out.result == "https://example.com/page/3"


def test_next_no_pagination():
    out = get_next_page_url(SkillInput(data=NO_PAGINATION_HTML))
    assert out.success is True
    assert out.result == ""
    assert out.error == "no next page found"


def test_next_absolute_href_no_base():
    html = '<html><body><a rel="next" href="https://site.com/page/5">Next</a></body></html>'
    out = get_next_page_url(SkillInput(data=html))
    assert out.result == "https://site.com/page/5"


def test_next_empty_html_graceful():
    out = get_next_page_url(SkillInput(data=""))
    assert out.success is True
    assert out.result == ""


# ── prev page ─────────────────────────────────────────────────────────────────


def test_prev_via_link_rel():
    out = get_prev_page_url(SkillInput(data=LINK_REL_HTML, options={"base_url": RELATIVE_BASE}))
    assert out.success is True
    assert out.result == "https://example.com/page/1"


def test_prev_via_a_rel():
    out = get_prev_page_url(SkillInput(data=A_REL_HTML, options={"base_url": RELATIVE_BASE}))
    assert out.success is True
    assert out.result == "https://example.com/page/1"


def test_prev_via_aria_label():
    out = get_prev_page_url(SkillInput(data=ARIA_HTML, options={"base_url": RELATIVE_BASE}))
    assert out.success is True
    assert out.result == "https://example.com/page/1"


def test_prev_via_css_class():
    out = get_prev_page_url(SkillInput(data=CLASS_HTML, options={"base_url": RELATIVE_BASE}))
    assert out.success is True
    assert out.result == "https://example.com/page/1"


def test_prev_via_text_symbol():
    out = get_prev_page_url(SkillInput(data=TEXT_HTML, options={"base_url": RELATIVE_BASE}))
    assert out.success is True
    assert out.result == "https://example.com/page/1"


def test_prev_no_pagination():
    out = get_prev_page_url(SkillInput(data=NO_PAGINATION_HTML))
    assert out.success is True
    assert out.result == ""
    assert out.error == "no previous page found"


def test_prev_empty_html_graceful():
    out = get_prev_page_url(SkillInput(data=""))
    assert out.success is True
    assert out.result == ""
