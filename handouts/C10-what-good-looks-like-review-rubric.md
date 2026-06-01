# C10 — "What Good Looks Like" — Review Rubric for AI-Assisted Code

U.S. Energy Developer AI Training · Used in Hours 7, 8, and 9

Your job when AI writes the code: **review**, not rubber-stamp. This rubric gives you a consistent checklist. Run through it before approving any diff that AI generated.

---

## How to Use This Rubric

Read through the diff once to understand what changed. Then scan each category below. A single "fail" is a reason to send the code back. Not every item applies to every change — use judgment on which categories are relevant.

---

## 1. Correctness — Does It Actually Do What Was Asked?

- [ ] **Re-read the acceptance criteria.** Does each criterion pass — not just "the tests pass" but the specific behaviour stated in the spec?
- [ ] **Check the boundary conditions.** Empty input, zero, null, maximum value, the thing that shouldn't be allowed. Are they handled?
- [ ] **Trace the happy path manually.** Can you follow the code from entry point to output and confirm the logic is right?
- [ ] **Look for off-by-one errors.** Loops, slice indexes, date ranges. These are the most common subtle errors in AI-generated code.
- [ ] **Verify rounding and arithmetic.** In financial or tax contexts (IFTA, fuel tax) — is rounding applied at the right point? Is integer arithmetic used where float would produce drift?

---

## 2. Hallucinated Dependencies and Invented APIs

- [ ] **Check every import.** Does each imported module actually exist? Run a clean `pip install -r requirements.txt` and verify — the agent sometimes invents plausible library names.
- [ ] **Check method and attribute names.** Does `trip.jurisdiction_code` exist on the `Trip` dataclass, or did the agent invent the attribute name?
- [ ] **Check function signatures.** If the agent calls an existing function, do the argument names and types match the actual definition?
- [ ] **Verify SQL column names.** SQL queries against a schema the agent partially inferred can reference columns that don't exist. Run the query.

---

## 3. Tests That Don't Actually Test

- [ ] **Do the tests exercise the behaviour, or just exercise the code path?** A test that passes without checking the return value is not a test.
- [ ] **Are assertions present?** Check that each test has at least one `assert` (or equivalent) that would fail if the implementation were wrong.
- [ ] **Are the expected values correct?** The agent sometimes writes a test, runs the broken implementation to see what it returns, and uses that as the expected value. Check that expected values are derived from the spec, not from the output.
- [ ] **Are edge cases tested?** The agent gravitates toward happy-path tests. Verify that boundary and error cases from the acceptance criteria have tests.
- [ ] **Do the tests clean up after themselves?** Tests that leave rows in a shared database, or files on disk, can interfere with each other. Look for `teardown` / fixture cleanup.

---

## 4. Security

- [ ] **No secrets in source.** No API keys, passwords, tokens, or connection strings hardcoded. All environment-specific values come from `.env` / `os.environ`.
- [ ] **No user input passed directly to SQL.** Check for string interpolation into query strings — even in SQLite. Look for `f"SELECT * FROM trips WHERE id = {trip_id}"` and replace with parameterized queries.
- [ ] **No user input passed to shell commands.** `subprocess.run(f"rm {filename}", shell=True)` is a shell-injection risk. Verify shell=False or that the input is sanitized.
- [ ] **File paths from user input are validated.** Path traversal is an easy mistake to make when the agent generates file-serving code.
- [ ] **No excessive permissions.** If a SKILL.md or runbook opens a port, starts a service, or requests a scope, confirm it's only what's needed.

---

## 5. Style and Maintainability

- [ ] **Does it follow the project's existing conventions?** Check CLAUDE.md conventions. Naming, formatting, where logic lives (service vs. route), commit-message style.
- [ ] **Is the scope right?** AI sometimes adds "helpful" extras — pagination, logging, caching — that weren't asked for. Is everything in the diff in scope?
- [ ] **Is the code readable?** A future developer (or future AI session) needs to understand it. Long functions, deeply nested conditionals, and cryptic variable names are red flags.
- [ ] **Are new constants named, not magic-numbered?** `MAX_MILES_PER_DAY = 800` beats `if miles > 800` everywhere.
- [ ] **Was an existing pattern reused, or did the agent reinvent it?** If there's a service layer, did the agent add business logic to the route instead? Look for duplication of patterns that already exist.

---

## 6. Scope and Side Effects

- [ ] **Did the agent modify files it wasn't asked to touch?** Review the full list of changed files — not just the ones you expected.
- [ ] **Did it change existing behaviour?** If a function was edited, does it still satisfy existing callers? Read the tests for that function, not just the new ones.
- [ ] **Did it rename anything public?** Renaming a public API, class name, or column name has ripple effects. Check for unreferenced old names and updated references.
- [ ] **Did it delete anything?** Deletions are easy to miss in a large diff. Search for `deleted file` or red lines in the diff.

---

## 7. Execution Verification

- [ ] **Run the full test suite.** `pytest tests/ -v` — not just the new tests.
- [ ] **Run the linter.** `ruff check .` (or whichever linter the project uses).
- [ ] **Start the app and exercise the new behaviour manually.** For web app changes: open the browser, hit the endpoint, confirm the response.
- [ ] **Run the SQL query by hand.** For any new SQL: execute it against the dev database and confirm the result is what you expect.

---

## One-Line Summary

> Re-read the spec. Check the imports. Verify the assertions. Look for secrets. Confirm scope. Run the tests.