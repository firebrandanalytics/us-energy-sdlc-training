# Session 5 — Scaling the Build, and What's Next

U.S. Energy AI Software-Development Training · Session 5 of 5 · 2 hours, online

**Theme: scaling the build with parallel agents, making it trustworthy, and
seeing where this pays off in your real work.** Session 4 turned a vague ask into
a sharpened spec and a running pipeline that got physical and taxable volumes
right. This session finishes the job the way a data team actually ships one: you
write a small **contract**, split the remaining work across **parallel
subagents**, wire it together, and then make the result *trustworthy* with
validation, data-quality checks, and documentation the agent generates for you.
Then we step back: where does this loop earn its keep in your day-to-day, and what
comes next.

This is **Exercise 2, part 2** — the close of the running pipeline you started in
Session 4 and extended in Homework 3.

---

## In this folder

- `README.md` — this orientation.
- `LAB-GUIDE.md` — the hands-on reference for the whole session. The instructor
  walks the room through each step live; this guide lets you keep moving if you
  fall behind or pick up from any step if you arrive late.

You'll also use, from elsewhere in the repo:

- `data/us_energy.sqlite` — the working database.
- `data/vol_report.py` — the legacy rollup script you've been replacing; still
  your reconciliation target.
- Your **`pipeline.py`** from Session 4 / Homework 3 — the foundation you finish
  here.
- `handouts/D4-data-spec-template.md` — the data spec you sharpened in Session 4;
  the contract you write today is a slice of it.
- `handouts/C10-what-good-looks-like-review-rubric.md` — for reviewing the
  agents' output against the spec, not just that it ran.
- `handouts/C5-approval-mode-decision-matrix.md` — for deciding when to let the
  agents run and when to gate them.

---

## What you'll do this session

1. **Share back Homework 3.** Your pipeline slice and its reconciliation test —
   one win, one snag.
2. **Write the contract.** The remaining work splits cleanly only if both halves
   agree on one thing: the shape of the data that passes between them. You'll pin
   that contract in a few lines before any code.
3. **Split the work across parallel subagents.** One subagent finishes the
   **transformation** (the volume measures); another builds **validation and a
   data-quality report**. They work in parallel against the contract; the main
   session integrates.
4. **Wire it together and verify end to end** against the dataset — including the
   reconciliation against the legacy numbers from Session 4.
5. **Make it trustworthy.** Direct the agent to generate the tests, data-quality
   checks, and short documentation that let someone else trust this pipeline.
6. **The art of the possible.** Where this loop pays off in your real work —
   legacy comprehension, migrations, data-quality triage, documentation and
   lineage — and a short look beyond the terminal.
7. **Course close.** The loop you ran end to end, the habits to keep, and Q&A.

---

## What you'll leave with

- A **finished pipeline** that produces physical, taxable, and RIN credit gallons
  by terminal-month, reconciled against the legacy script and with the RIN
  correction documented.
- A **validation + data-quality layer** the agent built against your contract —
  including a check that flags the one real anomaly hiding in this dataset.
- The pattern that scales all of it: **a written contract is what lets you split
  work across parallel agents and trust that the pieces fit.**
- A concrete sense of where to point this at your own backlog on Monday.

You don't need a flawless, fully green build to get the value. A pipeline that
reconciles for reasons you understand, plus a validation layer you can read, is
the deliverable. Variance across the room is expected and fine.

---

## Before the session

- Have your laptop, Claude Code installed and working, and the student repository
  on your machine.
- Confirm the database opens (see `data/README.md`).
- Bring your **Homework 3** pipeline slice and its test. We start from where you
  left it.
- Bring **one example from your own work** where you'd apply this loop — a legacy
  script, a migration, a data-quality problem, a pipeline you own.

---

## The through-line (same as every session)

Column names are generic, several values are bare integer codes, and the
documentation is intentionally incomplete. Treat the **behavior of the code and
the contents of the data as the source of truth** — not the column names, not the
comments, not even the spec until you've checked it against the data. Scaling the
build does not change that discipline: a contract two agents agree on is still
only a hypothesis until the output reconciles against a number you trust.
