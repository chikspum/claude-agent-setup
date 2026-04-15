# Skill: pagination_tool

Detects pagination controls on a web page and returns the next or previous page URL.

Works on **static HTML** and on **JS-rendered HTML** (the caller is responsible for
rendering the page — e.g. via Playwright — before passing the HTML string to this skill).

---

## Functions

### `get_next_page_url(input: SkillInput) -> SkillOutput`

Returns the URL of the **next** page.

### `get_prev_page_url(input: SkillInput) -> SkillOutput`

Returns the URL of the **previous** page.

---

## Input

```python
SkillInput(
    data: str,            # full HTML string of the page to inspect
    options: dict | None  # optional — see below
)
```

### `options` keys

| Key        | Type | Default | Description                                                              |
|------------|------|---------|--------------------------------------------------------------------------|
| `base_url` | str  | `""`    | Base URL used to resolve relative hrefs, e.g. `"https://example.com/"`. |

---

## Output

```python
SkillOutput(
    result:  str,        # absolute URL of next/prev page, or "" if not found
    success: bool,       # True even when no URL is found (see error field)
    error:   str | None  # "no next page found" / "no previous page found" / exception message
)
```

`success=False` is returned **only** when an unexpected exception occurs (e.g. the parser crashes).

---

## Detection strategy (priority order)

1. `<link rel="next|prev">` in `<head>` — most reliable; used by major CMSes and Google
2. `<a rel="next|prev">` — semantic anchor attribute
3. `aria-label` containing "next" / "previous" on `<a>` elements
4. CSS class or `id` hints: `next`, `prev`, `pagination-next`, `page-prev`, etc.
5. Visible text heuristic: anchors whose text is `Next`, `»`, `›`, `→`, `Prev`, `«`, `‹`, `←`, etc.

JS-rendered pages are supported because the detection operates purely on the HTML string.
The caller must render the page first and pass the resulting HTML.

---

## Usage examples

### Static HTML (requests)

```python
import requests
from skills import SkillInput
from pagination_tool import get_next_page_url, get_prev_page_url

resp = requests.get("https://example.com/blog/page/2/")
html = resp.text

next_out = get_next_page_url(SkillInput(
    data=html,
    options={"base_url": resp.url},
))
prev_out = get_prev_page_url(SkillInput(
    data=html,
    options={"base_url": resp.url},
))

print(next_out.result)   # e.g. "https://example.com/blog/page/3/"
print(prev_out.result)   # e.g. "https://example.com/blog/page/1/"
```

### JS-rendered page (Playwright)

```python
from playwright.sync_api import sync_playwright
from skills import SkillInput
from pagination_tool import get_next_page_url

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://spa-blog.com/posts?page=2")
    page.wait_for_load_state("networkidle")
    html = page.content()          # fully rendered DOM
    browser.close()

out = get_next_page_url(SkillInput(
    data=html,
    options={"base_url": "https://spa-blog.com/posts"},
))
print(out.result)
```

---

## Notes for the openclaw agent

- Always pass `base_url` when you have the page URL — relative hrefs are common.
- If `result` is `""` and `success` is `True`, there is no detected pagination in that direction.
- If `success` is `False`, inspect `error` for the exception message and retry or skip.
- For JS-heavy pages, render first (Playwright / Puppeteer) and pass the rendered HTML.
