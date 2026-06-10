# Session 4 — From Vague Ask to a Shipped Service

U.S. Energy AI Software-Development Training · Session 4 of 5 · 2 hours, online

**Theme: run the real software-development loop — spec, stories, tests-first,
plan, build, validate, ship — with the agent doing the labor and you directing.**
Session 3 was about *reading* what you didn't write. This session turns
comprehension into construction the way a real team does it: take a vague
stakeholder ask, sharpen it into a spec with an output contract, capture your
Homework-2 knowledge as a **skill** the agent loads, slice the work into **user
stories**, write the **tests first**, plan, build a clean Python **service** until
the tests are green, validate it against the data, and **commit it with a real
message and a PR description**. Session 5 finishes the loop: the Azure DevOps
board, parallel agents, an unbiased review, the merge, the closed ticket.

That last word is the pivot of the back half of the course. You're not building a
one-off script that prints a number and exits. You're building a **service**: an
importable module with a clear **output contract**, so that in Session 5 you can
put a **web dashboard** on top of it. Comprehend the legacy code → build the
service → build the app on the service. This session is the middle step.

This is **Exercise 2, part 1**. You build the service here; in Homework 3 you stand
up a tiny dashboard skeleton on top of it, and in Session 5 you extend that
dashboard.

---

## In this folder

- `README.md` — this orientation.
- `LAB-GUIDE.md` — the hands-on reference for the whole session. The instructor
  walks the room through each step live; this guide lets you keep moving if you
  fall behind or pick up from any step if you arrive late.

You'll also use, from elsewhere in the repo:

- `data/us_energy.sqlite` — the working database.
- `data/vol_report.py` — the legacy rollup script you're replacing. You created this
  during Homework #2. If you skipped HW2, grab the listing from
  `homework/homework-2-brief.md` and save it to `data/vol_report.py` first.
- `handouts/D4-data-spec-template.md` — the data-spec template you'll fill in.
- `handouts/D5-output-contract-and-dashboard.md` — the output-contract pattern and
  a FastAPI quickstart (you'll lean on it for Homework 3 and Session 5).
- `handouts/C7-ai-ready-spec-template.md` — the general AI-ready spec template
  (D4's companion for the surrounding work).
- `handouts/C10-what-good-looks-like-review-rubric.md` — for reviewing the
  agent's output against the spec, not just that it ran.

---

## What you'll do this session

1. **Take the vague ask** — *"give me clean monthly volumes by terminal"* — and
   see why, as written, it isn't buildable.
2. **Sharpen it into a spec — including the output contract** (grain,
   filters/exclusions, units, edge cases, and the exact shape of one returned
   row — which becomes your tests, and next week's dashboard input).
3. **Capture your Homework-2 knowledge as a skill** — a real `SKILL.md` (YAML
   frontmatter + a page of verified rules) the agent auto-loads in every future
   session.
4. **Put user stories on the real board.** The agent drafts them with checkable
   acceptance criteria, then creates them as **Azure DevOps work items**.
5. **Plan in plan mode — tests first, logging required — read the plan, approve,
   and let it run.** The agent writes failing tests, builds the service, and
   iterates to green at its own (fast) speed; your job is the reading and the
   approvals.
6. **Validate with evidence:** the green suite, the legacy reconcile, and the
   service's own **run log cross-checked against the database**.
7. **Absorb a change request, safely.** The desk asks for a new field
   mid-session: comment the ticket, change the contract tests-first, and **prove
   the existing numbers didn't move by diffing the before/after run logs**.
8. **Document while it's true** — the agent writes `ARCHITECTURE.md` from the
   real code; you read it like Monday's new teammate.
9. **Ship it:** a DevOps repo, a branch, agent-written commit messages that say
   *why*, and a PR description with the evidence — Session 5 reviews, merges,
   and closes the tickets.

---

## What you'll leave with

- A **sharpened spec** with a written **output contract** (the row shape your app
  — and your tests — rely on).
- A **skill** (`.claude/skills/us-energy-volume-rules/`) any agent loads — your
  HW2 dossier, made operational.
- **`stories.md`** — the work, sliced into checkable pieces.
- A **green test suite and a running `service.py`** that returns reconciled
  physical and taxable volume — built tests-first.
- A **commit and a PR description** ready for Session 5's review-merge-close.
- The habit that makes all of it work: **decide the ambiguous things in writing
  before the agent decides them for you — and make the agent show evidence
  before it says "done."**

You don't need to finish everything today — the loop deliberately spills into
Session 5. A green, reconciled service with its tests and a real commit is the
complete slice; the RIN measure is a stretch; the dashboard comes next.

---

## The homework that follows (small on purpose)

**Homework 3 — the dashboard starter.** A small, concrete build: stand up a minimal
read-only web page (FastAPI + one table view) that calls your Session 4 service and
renders clean volumes by terminal. Skeleton plus one view — nothing more. Session 5
*extends* it, so this is deliberately light: you arrive with something running, and
we grow it together. If you don't get to it, a starter is committed in the repo so
you're never blocked. The brief is
[`../../homework/homework-3-brief.md`](../../homework/homework-3-brief.md).

---

## Before the session

- Have your laptop, Claude Code installed and working, and the student repository
  on your machine.
- Confirm the database opens (see `data/README.md`).
- Bring your **Homework 2 intent dossier** for `vol_report.py` — you'll reuse what
  you learned about which comments lie and which rules are real.
- Come ready to build, not just discuss.

---

## The through-line (same as every session)

Column names are generic, several values are bare integer codes, and the
documentation is intentionally incomplete. Treat the **behavior of the code and
the contents of the data as the source of truth** — not the column names, not the
comments, not even the spec until you've checked it against the data. A spec is a
hypothesis about the right number; reconciliation is how you test it. And a clean
service is one whose **contract** you can hand to someone else — a teammate, a
future you, or the web app you build next — and trust they'll get it right.
