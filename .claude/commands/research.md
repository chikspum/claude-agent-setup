# /research $ARGUMENTS

Structured web research — answers a question using WebSearch and WebFetch with cost awareness.

`$ARGUMENTS` should be a question, topic, or technology name (e.g., "best practices for Go context cancellation", "how to use uv workspaces").

## Steps

### 1. Parse the request
Identify:
- **Core question** — what specifically needs answering
- **Scope constraints** — language, framework, version, or context from the codebase
- **Done criteria** — is the goal a recommendation? a comparison? a code example? a yes/no?

### 2. Check local knowledge first (no web fetch)
Before going to the web:
- Search the codebase for existing implementations, patterns, or comments related to the topic
- Check if `CLAUDE.md`, agent profiles, or `config/` files already address it
- Check if the answer can be inferred from the existing tool code in `tools/`

If local information is sufficient → answer from it directly. Skip steps 3–5.

### 3. Web search (cost-aware)
- Start with **one targeted WebSearch query**. Make it specific: include version numbers, framework names, or "official docs" where relevant.
- Read the **top 2–3 results** with WebFetch. Prefer official documentation URLs over blog posts.
- **Stop as soon as the answer is clear.** Do not fetch more pages "for completeness."
- If the first round is insufficient, run one more search with a refined query. Hard limit: **5 WebFetch calls total.**

### 4. Extract from each source
For each fetched page, capture:
- Key facts, recommendations, or code examples relevant to the question
- Source URL
- Approximate date (flag if older than 2 years — may be outdated)
- Confidence in relevance: HIGH / MEDIUM / LOW

### 5. Synthesize
- Lead with the **direct answer or recommendation**
- Support with evidence from sources
- Note any contradictions between sources and explain which to trust and why
- Indicate overall confidence: **HIGH** (verified, multiple consistent sources), **MEDIUM** (one clear source or consistent reasoning), **LOW** (conflicting sources or thin evidence — flag for user review)

## Output Format

```
## Answer
[Direct answer to the question — lead with this]

## Evidence
| Source | Key Finding | Date | Confidence |
|--------|-------------|------|------------|
| [url]  | ...         | ...  | HIGH/MED/LOW |

## Recommendation
[What to do, including tradeoffs if the answer isn't clear-cut]

## Sources
1. [url]
2. [url]
...
```

## Rules

- Maximum **5 WebFetch calls** per research task
- Prefer official documentation over blog posts
- Prefer recent sources (< 2 years) over old ones — flag older sources explicitly
- If the codebase already has the answer, do not web search at all
- Never present web content as your own conclusions without attribution
- If no reliable answer is found after 5 fetches, say so — do not fabricate
