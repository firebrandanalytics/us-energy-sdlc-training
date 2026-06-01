# C7 — "AI-Ready Spec" Prompt Template

U.S. Energy AI Training · the general task-spec template. For a **data deliverable**, pair this with **D4 (Data Spec Template)**.

Copy this template. Fill in every section before handing the task to Claude Code. Delete sections that genuinely don't apply, but be honest about whether they apply — most of them do.

---

## Why This Template Exists

Vague prompts produce confident but wrong output. The agent doesn't have your intuition, your knowledge of the codebase, or your understanding of the business context. This template makes that implicit knowledge explicit — turning a vague ask into a structured spec the agent can execute reliably.

"I want a script that pulls last month's terminal volumes and flags anything that looks off" is a starting point. The template below turns it into an instruction set.

---

## The Template

```
## Task
<!-- One to three sentences. What do you want done? Be concrete.
     "Add a --terminal filter to the volume report" beats "improve the report." -->

## Context
<!-- What does the agent need to know about the data, team conventions,
     or business domain that it can't read from the source files?
     Examples: "We report on net (temperature-corrected) gallons, not gross,"
     "This script runs in a nightly job," "Voided records have status 8." -->

## Constraints
<!-- What must be true about the solution?
     Technical: must use Python 3.12 + the stdlib sqlite3, must not add dependencies.
     Functional: must handle a month with zero rows for a terminal gracefully.
     Style: must follow the existing query/transform split in the pipeline. -->

## Anti-Goals
<!-- What does the solution explicitly NOT need to do?
     Examples: "Don't build a dashboard — a printed table is enough."
     "Don't compute pricing or credit math — volumes only."
     "Don't change the schema — read-only against the database." -->

## Acceptance Criteria
<!-- Bullet list of verifiable pass/fail statements.
     Each criterion should be checkable without judgment calls:
     - Running `pytest tests/` passes with zero failures.
     - Voided rows (status 8) are excluded from every total.
     - The August total for DAL reconciles to the known figure within rounding.
     - No row is double-counted when a terminal has a book adjustment. -->

## Files to Read First
<!-- List the files the agent should read before writing any code.
     Saves time; prevents the agent from inventing a schema it could have read.
     Examples: data/vol_report.py, the schema (run .schema in sqlite3). -->

## Files to Modify (expected)
<!-- Best guess at what changes. The agent will deviate if needed, but this
     anchors scope and surfaces surprises.
     Examples: pipeline.py (add the rollup), tests/test_pipeline.py (add a check). -->

## Dos
<!-- Optional. Explicit "prefer X" instructions:
     - Prefer early returns over deeply nested if-blocks.
     - Prefer named constants over magic numbers (no bare `8` or `6` in the code). -->

## Don'ts
<!-- Optional. Explicit prohibitions beyond constraints and anti-goals:
     - Don't trust the comments in the legacy script — verify against the data.
     - Don't rename existing columns or output headers — downstream jobs depend on them. -->

## Glossary (for this task)
<!-- Terms that mean something specific in this context that the agent might misread.
     Examples: "net" = temperature-corrected gallons (net_gal), the figure we report on;
     "gross" (gross_gal) is the raw meter reading and is NOT what we total.
     "physical volume" excludes voids and non-physical book adjustments. -->

## Definition of Done
<!-- One clear statement: when is this task complete and ready for review?
     Example: "When all acceptance criteria pass, the code is committed on a feature branch,
     and I have reviewed the diff and the reconciled numbers." -->
```

---

## Quick-Fill Tips

**Start with Acceptance Criteria.** If you can't write testable acceptance criteria, the task is still vague. Write those first, then fill in the rest — the other sections almost write themselves. (For data work, a reconciliation target — "ties to last month's known number" — is the strongest criterion you can give.)

**Anti-Goals earn their keep.** The agent optimises for "good" as defined by training data. Without anti-goals, it will add a chart, add pagination, add a config flag — because that's what a "finished" deliverable should have. Anti-goals redirect that energy.

**Context ≠ re-paste the data.** Tell the agent *where* to find the schema, not what it contains. "Run `.schema lifts` and read `data/vol_report.py`" is better than pasting rows into the prompt.

**Glossary is underused.** Domain terms — net vs. gross, dyed (tax-exempt) diesel, a voided record — mean specific things on your desk that differ from general usage, and the codes (status 8, mode 8, prod 6) aren't self-explaining. A two-line glossary prevents a category of wrong answer.

---

## Before-and-After Example

**Before (vague):**
> Give me a way to flag suspicious lifts.

**After (AI-ready):**
> **Task:** Add a query that flags suspicious `lifts` rows. A lift is suspicious if `net_gal` is non-positive, or if its `term_id` has no match in `terminals`. Return the flagged rows; don't modify the table.
>
> **Context:** Data is in `data/us_energy.sqlite`, table `lifts` (see the schema with `.schema lifts`). We report on `net_gal` (temperature-corrected). Voided rows have `status = 8` and should be excluded from this check — a void isn't "suspicious," it's already handled.
>
> **Constraints:** Read-only — no `INSERT`/`UPDATE`/`ALTER`. Python 3.12 + stdlib `sqlite3` only; no new dependencies.
>
> **Anti-Goals:** Don't build a UI or write results back to the database — printing the flagged rows is enough for this version.
>
> **Acceptance Criteria:**
> - A row with `net_gal <= 0` is flagged.
> - A row whose `term_id` is not in `terminals` is flagged.
> - A normal billed row (positive `net_gal`, known terminal, `status` 7) is NOT flagged.
> - Voided rows (`status = 8`) are never flagged.
> - `pytest tests/` passes.
>
> **Files to Read First:** `data/vol_report.py` (for how the legacy code treats status/mode), the schema via `.schema`.
>
> **Definition of Done:** Acceptance criteria pass; change committed on a feature branch; I've reviewed the diff.
