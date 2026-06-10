# C8 — "Make Correctness Easy" Checklist

U.S. Energy Developer AI Training · Session 3 (Hour 5) reference

The principle: take work away from the AI that you don't need it to manage. Bake correctness into the environment so the agent doesn't have to be careful — it just runs the right thing because the right thing is the only thing available.

Scan this list and check what you have in place for your project. Each row names a pattern, what it removes from the agent's working burden, and a concrete example.

---

## Environment Setup Patterns

| Pattern | What it removes from the agent | Concrete example |
|---------|-------------------------------|-----------------|
| `.env` file with all environment-specific values | Agent never hard-codes a DB path or API key into source | `DB_PATH=./data/logbook.db` in `.env`; agent reads `os.environ["DB_PATH"]` |
| `.env.example` committed to the repo | Agent (and new developers) know what variables exist without being told | Lists `DB_PATH=`, `APP_ENV=`, `AZURE_CLIENT_ID=` with no real values |
| `CLAUDE.md` with stack details, commands, and anti-goals | Agent stops asking what framework, Python version, or test command you use | `## How to Test: pytest tests/ -v` in CLAUDE.md |
| `requirements.txt` or `pyproject.toml` fully up to date | Agent installs exactly what you use rather than guessing at versions | Pinned dependencies; agent runs `pip install -r requirements.txt` without guessing |

---

## Command Wrappers and Aliases

| Pattern | What it removes from the agent | Concrete example |
|---------|-------------------------------|-----------------|
| Bash function wrapping a curl command with 8 flags | Agent calls `api-post /endpoint data.json` instead of reconstructing a 200-character curl command | `function api-post() { curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $API_TOKEN" "$BASE_URL$1" -d @"$2"; }` |
| Git alias enforcing a commit-message convention | Agent can't produce a non-conforming commit message if the alias validates before committing | `git config alias.cm '!./scripts/commit.sh'` where `commit.sh` validates prefix |
| Helper script hiding repetitive flags | Agent calls the helper; flags can't be wrong or forgotten | `scripts/seed-db.sh` runs `python scripts/seed.py --db $DB_PATH --rows 10` |
| `Makefile` or `justfile` with named targets | Agent types `make test` instead of remembering the full pytest invocation | `make test`, `make seed`, `make run` each expand to the right commands |

---

## Validation and Schema Tools

| Pattern | What it removes from the agent | Concrete example |
|---------|-------------------------------|-----------------|
| Input validation at the API boundary (Pydantic, TypedDict) | Agent-generated code that passes the wrong type fails immediately with a clear error, not silently | FastAPI + Pydantic model for trip creation rejects `miles="twelve"` at the route level |
| Database constraints (NOT NULL, UNIQUE, CHECK) | Agent can't insert bad data even if it tries | `CHECK (miles > 0)` in the SQLite schema; bad inserts fail at the DB layer |
| A schema migration script | Agent runs the migration; can't forget a column or run out of order | `scripts/migrate.py` applies numbered migrations in sequence |
| Linter / formatter in CI | Agent can't land code that violates style, even if it forgot to run the linter | `ruff check .` in the CI pipeline; PR fails on lint errors |

---

## Test Infrastructure

| Pattern | What it removes from the agent | Concrete example |
|---------|-------------------------------|-----------------|
| A test suite the agent can run after every change | Agent verifies its own work without you running the tests manually | `pytest tests/ -v` wired into CLAUDE.md's How to Test section |
| Fixture data the agent can use | Agent doesn't invent test data that doesn't match production shapes | `tests/fixtures/sample_trips.json` with realistic rows |
| Tests that cover the boundary conditions | Agent can't silently break edge cases that aren't tested | Test for `miles = 0`, empty jurisdiction list, duplicate trip IDs |
| Test names that document intent | Agent reads failing test names and understands what broke | `test_delete_trip_returns_404_for_unknown_id` beats `test_delete_3` |

---

## Skills as a Correctness Device

A **skill** is a folder holding a `SKILL.md` the agent loads on demand: **YAML
frontmatter** (a `name`, and a one-line `description` that tells the agent *when
to reach for it*), then the knowledge as plain markdown. Claude Code discovers
them in your repo's `.claude/skills/` folder:

```
.claude/skills/us-energy-volume-rules/SKILL.md

---
name: us-energy-volume-rules
description: Verified rules for the fuel-lifts dataset — code meanings,
  measure definitions, reconciliation anchors. Use when computing, reviewing,
  or testing volume numbers.
---
# US Energy volume rules
...the rules, one page, verified against the data...
```

| Pattern | What it removes from the agent | Concrete example |
|---------|-------------------------------|-----------------|
| A skill for domain rules | Agent doesn't re-derive (or hallucinate) hard-won facts | `us-energy-volume-rules`: the code meanings, the physical-vs-taxable asymmetry, the reconciliation anchors — your Session 4 build |
| Decision trees in the skill | Agent follows your logic rather than guessing at branch conditions | "If the measure is taxable, additionally exclude the tax-exempt product. If physical, keep it." |
| Verification steps in the skill | Agent confirms completion against concrete criteria | "Reconcile 2025-08 against the legacy script to the gallon before reporting done." |

The test of a good skill: **a fresh agent session answers your domain question
correctly without being told anything** — because it loaded the skill.

---

## Quick Diagnostic

If the agent is asking you something it should already know, it's probably in one of these states:

1. **No CLAUDE.md** — add one with the missing information.
2. **CLAUDE.md exists but is vague** — tighten the relevant section.
3. **A recurring task has no SKILL.md** — write one.
4. **Hardcoded values in source** — move them to `.env`.
5. **Test suite doesn't cover the thing that's failing** — add the test.
6. **Command is long and error-prone** — wrap it in a bash function or Makefile target.

> The goal is an environment where the agent almost can't get it wrong — not an agent that never gets it wrong.
