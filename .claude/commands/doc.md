# /doc $ARGUMENTS

Documentation generator — reads a target file or module and generates or updates its documentation in the appropriate style.

`$ARGUMENTS` should be a file path, directory, or module name.

## Routing

Before starting, identify which directory the target lives in:

- `tools/python/` or `*.py` → delegate to **python-agent**
- `tools/go/` or `*.go` → delegate to **go-agent**
- `tools/cpp/` or `*.cpp` / `*.h` / `*.hpp` → delegate to **cpp-agent**
- Spans multiple languages → **orchestrator** delegates each language separately
- Agent profiles, CLAUDE.md → handle directly (no delegation)

---

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

6. **Report what was added:**
   - List each function/type that received new or updated docs
   - Note any functions skipped and why
