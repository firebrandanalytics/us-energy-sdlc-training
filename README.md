# U.S. Energy AI Software-Development Training — Student Materials

> **Note:** These materials are being finalized for online delivery — session structure and exercises are still being updated.

Hands-on materials for the Firebrand-led AI software-development training for
U.S. Energy's data and engineering teams — a multi-session online course on
agentic development with Claude Code.

## How this repo is organised

- **`sessions/`** — one folder per segment, prefixed with the day and segment
  number so they sort in the order they're run: `day1-01-...`, `day1-02-...`,
  `day2-01-...` through `day2-06-...`. Each folder has a `README.md` describing
  what's covered, plus that segment's exercise / lab guide and any handouts
  needed. During a segment, open its folder — everything is in one place.
- **`handouts/`** — the full set of reference cards: glossary, CLAUDE.md and
  SKILL.md templates, cheat sheets, the Claude Code commands card. The copies
  inside each segment folder are drawn from here; this is the canonical set.
- **`cli-utility/`** — the IFTA fuel-tax CLI. In day-2 segment 5 we extract a
  calculations "skill" from it and feed that to the web-app build. Self-study
  for whatever else you'd like to learn from it.
- **`sessions/zz-archived/`** — material from the original 10-hour design that
  isn't part of the delivered two-day session. Kept for self-study.

## The two starter codebases you extend

You extend these by directing Claude Code:

- `sessions/day2-05-web-app-build/` — the Mileage Logbook web app
  (FastAPI + SQLite + Jinja2). Day 2 segment 5 builds an apportionment-summary
  feature here using planning mode + parallel subagents.
- `sessions/day2-01-legacy-comprehension/` — `bounded_cache.py`, the unfamiliar
  module you learn to read and change safely in day 2 segment 1.

## Using this repo

Clone it before day 1. During each segment, work inside its folder, directing
Claude Code. Worked solutions are kept separately and are not in this repo.
