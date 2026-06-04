# U.S. Energy AI Software-Development Training — Student Materials

Hands-on materials for the Firebrand-led AI software-development training for
U.S. Energy — a **5 × 2-hour online** course on agentic development with Claude
Code, delivered over two weeks.

The back half of the course runs one continuous, full-stack arc on a realistic
U.S. Energy fuel-movements dataset: **comprehend** the legacy code and data you
didn't write → build a clean **service** on it → build and extend a **web
dashboard** on that service.

## The five sessions

| # | Session | What you walk away able to do |
|---|---------|-------------------------------|
| 1 | From Autocomplete to Agentic | Direct an agent instead of typing for it; calibrate trust by risk |
| 2 | Operating the Agent + Claude Code as your shell | Run real work through Claude Code; the day-to-day control levers |
| 3 | Reading What You Didn't Write | Use the agent to comprehend unfamiliar SQL, a query plan, and a schema that fights back |
| 4 | From Vague Ask to a Working Service | Sharpen a fuzzy request into a spec (with an output contract) and build a clean service |
| 5 | Extend the Dashboard, and What's Next | Extend a web app on the service with parallel agents; verify; where this earns its keep |

## How this repo is organised

- **`sessions/`** — one folder per session (`session-1` … `session-5`). Each has a
  `README.md` (the session overview) and, from Session 1 on, a hands-on guide
  (`HANDS-ON-*.md` or `LAB-GUIDE.md`). During a session, open its folder — the
  overview and the step-by-step are both there.
- **`data/`** — the **running dataset** used from Session 3 on:
  `us_energy.sqlite` (a fuel-movements database), a deliberately partial
  `DATA-DICTIONARY.md`, and `vol_report.py` — a crusty legacy reporting script
  (with comments that lie) you comprehend, then replace.
- **`homework/`** — the three between-session homework briefs (HW1 after Session 2,
  HW2 after Session 3, HW3 after Session 4). Each is small and feeds the next
  session.
- **`handouts/`** — reference cards (see `handouts/README.md`): the **C\*** cards
  (agentic practices — approval modes, model selection, spec template, review
  rubric, Claude Code commands) and the **D\*** cards (the dataset and the build —
  data glossary, query plans, magic values, the data spec, and the output
  contract + dashboard quickstart).

## What you build

Across Sessions 4–5 (and Homework 3) you build, on the committed dataset:

- a clean **service** (`service.py`) that returns reconciled monthly volumes by
  terminal — the data layer, replacing the legacy `vol_report.py`; and
- a read-only **dashboard** (FastAPI + Jinja2) on top of that service — a table, a
  month filter, a simple chart, a per-terminal page, and a JSON API.

If you fall behind on the Homework 3 dashboard skeleton, a working starter is
committed at `sessions/session-5/starter/` so you're never blocked.

## Using this repo

Clone it before Session 2. During each session, work inside that session's folder,
directing Claude Code. The homework briefs tell you what to do between sessions.
Worked instructor solutions are kept separately and are not in this repo.

> Sessions 3–5 run on the dataset in `data/`. You don't need to study it in
> advance — coming to it cold is part of the Session 3 exercise.
