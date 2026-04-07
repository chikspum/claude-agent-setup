# /doc $ARGUMENTS

Documentation generator — reads a target file or module, generates or updates inline code documentation, and creates or updates a `DOC.md` agent documentation file for the target directory.

`$ARGUMENTS` should be a file path, directory, or module name.

---

## Routing

Before starting, identify which directory the target lives in:

- `tools/python/` or `*.py` → delegate to **python-agent**
- `tools/go/` or `*.go` → delegate to **go-agent**
- `tools/cpp/` or `*.cpp` / `*.h` / `*.hpp` → delegate to **cpp-agent**
- Spans multiple languages → **orchestrator** delegates each language separately
- Agent profiles, CLAUDE.md → handle directly (no delegation)

---

## Phase 1 — Inline Code Documentation

Steps:

1. **Identify the target.** Resolve the path:
   - If it's a file, read it fully
   - If it's a directory, list files and read the main entry points
   - Detect language from extension: `.py` → Python, `.go` → Go, `.cpp`/`.h`/`.hpp` → C++

2. **Assess existing documentation.** Note:
   - Which public functions/methods/types are already documented
   - Which are missing docs entirely
   - Which have outdated or inaccurate docs (e.g., param names don't match)

3. **Generate or update documentation** using the correct style:

   **Python — Google-style docstrings:**
   ```python
   def function(arg: Type) -> ReturnType:
       """Short one-line summary.

       Longer description if needed. Explain non-obvious behavior,
       edge cases, or performance characteristics here.

       Args:
           arg: Description of the argument.

       Returns:
           Description of return value.

       Raises:
           ValueError: When and why this is raised.
       """
   ```
   Also add module-level docstrings if missing.

   **Go — godoc-compatible comments:**
   ```go
   // FunctionName does X by doing Y.
   // It returns Z, or an error if ...
   //
   // Example:
   //
   //   result, err := FunctionName(arg)
   func FunctionName(arg Type) (ReturnType, error) {
   ```
   Package-level comments go above the `package` declaration.

   **C++ — Doxygen-compatible comments:**
   ```cpp
   /// @brief Short description of what the function does.
   ///
   /// Longer explanation if needed.
   ///
   /// @param arg Description of the parameter.
   /// @return Description of the return value.
   /// @throws std::invalid_argument When and why.
   ```
   For class-level docs, use `/// @class` above the class declaration.

4. **Apply the documentation** by editing the file(s) in place.

5. **Rules — what NOT to document:**
   - Getters/setters whose name already says everything (`GetName() → returns the name`)
   - Test helper functions that are only called from tests
   - One-liner functions where the code is clearer than a doc would be
   - Internal unexported/private symbols unless they have non-obvious behavior

---

## Phase 2 — DOC.md Agent Documentation

After completing inline documentation, generate or update a `DOC.md` file in the target directory.

**When to create DOC.md:**
- The target is a directory (create `<target>/DOC.md`)
- The target is a file inside a directory that has no `DOC.md` yet (create one for the parent directory)
- An existing `DOC.md` is present but stale — update it

**When NOT to create DOC.md:**
- The target is a single isolated file deep in a large subtree and the directory already has an up-to-date `DOC.md`
- The directory is a test fixture, generated output, or runtime artifact directory (e.g., `.data/sessions/`, `__pycache__/`, `build/`)

### DOC.md Structure

Use exactly this section order. Every section is required. Omit sections only if they genuinely do not apply (e.g., no invariants for a pure config directory), and replace with a one-liner explaining why.

```markdown
# <Directory Name>

## About
One paragraph. What does this module/directory do? What problem does it solve?
State the purpose, not the contents.

## Read This When
Bullet list. When should an agent (or human) open this file?
Be specific: "You are changing X", "You need to debug Y", "You are adding Z".

## Related Docs
Bullet list of relative paths to sibling or parent DOC.md files and their one-line purpose.
- `../doc.md` — parent module overview
- `../domain/doc.md` — canonical contracts used here

## Key Files
Bullet list. Each entry: `filename.ext` — one-line purpose.
List only source files, not generated artifacts or test fixtures.
Mark the most important entry point with ← primary.

## Invariants
Bullet list. What must always be true? What must never happen?
These are rules that agents and humans must not violate.
Focus on structural invariants (data shape, ownership boundaries, ordering) not style rules.

## Workflow
Numbered steps. How should an agent approach work in this directory?
Include: what to read first, what to update together, what order matters.

## Verification
Bullet list. How do you confirm a change here is correct?
Include: tests to run, checks to perform, diffs to inspect.

## Body
Prose narrative. 2–5 paragraphs.
Explain the design rationale, key decisions, and non-obvious behavior.
This is where you explain *why*, not *what*.
Cross-reference Key Files by name when relevant.
```

### DOC.md Rules

- Write for an agent reading this file cold, with no prior context
- Every section should answer a concrete question an agent might have
- Do not repeat information already in `CLAUDE.md` — link to it instead
- Do not invent invariants or workflows that aren't reflected in the code
- Keep Key Files list honest — only files that actually exist in the directory
- Related Docs paths must be relative and point to files that exist
- The Body section is prose, not bullet points — use full sentences

### DOC.md — Checking for Existing File

Before writing:
1. Check if `DOC.md` already exists in the target directory
2. If yes: read it, identify which sections are stale or missing, update in place
3. If no: create it from scratch using the structure above

---

## Phase 3 — Report

After both phases are complete, output:

**Inline docs added/updated:**
- List each function/type that received new or updated docs
- Note any functions skipped and why

**DOC.md:**
- State whether it was created, updated, or already up-to-date
- List any sections that were added or changed
