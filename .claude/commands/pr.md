# /pr

Pull request creator — analyzes branch commits, generates a PR title and body, and creates the PR via `gh`.

Steps:
1. Identify the base branch:
   - Try `git symbolic-ref refs/remotes/origin/HEAD` to find the default branch
   - Fall back to `main`, then `master` if not set

2. Get the full commit history for this branch:
   ```
   git log <base-branch>...HEAD --oneline
   git diff <base-branch>...HEAD
   ```

3. Check remote status:
   ```
   git status -sb
   ```
   If the current branch has no upstream or is ahead of remote, push it:
   ```
   git push -u origin HEAD
   ```

4. Analyze all commits and the full diff to understand:
   - What feature/fix/change this PR delivers
   - What files and systems are affected
   - Any migration steps, config changes, or breaking changes

5. Generate PR content:

   **Title** (≤70 chars, imperative, no trailing period):
   - Same conventional-commits style as `/commit`
   - E.g., `feat: add retry logic to Go agent network calls`

   **Body:**
   ```markdown
   ## Summary
   - <bullet: what this PR does and why>
   - <bullet: any notable design decision>
   - <bullet: breaking changes or migration steps, if any>

   ## Test Plan
   - [ ] <how to verify the main change works>
   - [ ] <edge cases or regression scenarios to check>
   - [ ] <any manual testing steps>
   ```

6. Show the proposed title and body to the user and ask: **"Create PR with this content? (yes / edit / cancel)"**

7. If approved, run:
   ```
   gh pr create --title "<title>" --body "<body>"
   ```

8. Output the PR URL from the `gh` response.

If `gh` is not authenticated or not installed, tell the user and show the title + body so they can create the PR manually.
