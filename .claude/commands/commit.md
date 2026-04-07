# /commit

Smart commit helper — generates a conventional commit message and asks for approval before committing.

Steps:
1. Run `git diff --staged` to see what's staged for commit
2. Run `git diff` to see any unstaged changes (mention them but don't include)
3. Run `git diff --staged --name-only` to list staged files

**Safety check — abort if any of these are staged:**
- `.env`, `.env.*` (except `.env.example`, `.env.sample`)
- Files matching: `*secret*`, `*credential*`, `*.pem`, `*.key`, `id_rsa`, `id_ed25519`
- Any file containing patterns like `AKIA`, `ghp_`, `sk-`, `BEGIN PRIVATE KEY`

If any secrets are detected, stop immediately and tell the user which files are problematic. Do not proceed with the commit.

4. Analyze the staged diff to understand the intent of the changes:
   - What problem does this change solve?
   - What behavior changes for the user?
   - Is it a new capability, a fix, cleanup, or docs update?

5. Generate a commit message following [Conventional Commits](https://www.conventionalcommits.org/):
   - Format: `<type>(<optional scope>): <short description>`
   - Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `perf`, `ci`
   - Subject line: imperative mood, ≤72 chars, no trailing period
   - Body (if needed): explain *why*, not *what*; wrap at 72 chars
   - Focus on the reason for the change, not a list of touched files

   Example:
   ```
   feat(go-agent): add retry logic for transient network errors

   Without retries, any network blip caused the agent to fail hard.
   Three retries with exponential backoff cover the common case while
   still surfacing persistent failures quickly.
   ```

6. Show the proposed commit message to the user and ask: **"Commit with this message? (yes / edit / cancel)"**

7. If approved, run:
   ```
   git commit -m "<message>"
   ```
   If the user wants to edit, show the message in a code block and ask them to provide the revised version, then commit with their version.

Do not run `git add` — only commit what is already staged. If nothing is staged, tell the user and suggest running `git add` first.
