# Session 4 — From Vague Ask to Working Pipeline

U.S. Energy AI Software-Development Training · Session 4 of 5 · 2 hours, online

**Theme: turning a fuzzy data request into a specification the agent can build
against — then building it.** Session 3 was about *reading* what you didn't
write. This session turns comprehension into construction: you take a vague
stakeholder ask, sharpen it into a real data spec, direct the agent to lift the
true business rules out of the crusty legacy script and the ambiguous schema, and
start a clean Python pipeline against the course dataset.

This is **Exercise 2, part 1**. You start the pipeline here; you finish and scale
it with parallel agents in Session 5.

---

## In this folder

- `README.md` — this orientation.
- `LAB-GUIDE.md` — the hands-on reference for the whole session. The instructor
  walks the room through each step live; this guide lets you keep moving if you
  fall behind or pick up from any step if you arrive late.

You'll also use, from elsewhere in the repo:

- `data/us_energy.sqlite` — the working database.
- `data/vol_report.py` — the legacy rollup script you're replacing.
- `handouts/D4-data-spec-template.md` — the data-spec template you'll fill in.
- `handouts/C7-ai-ready-spec-template.md` — the general AI-ready spec template
  (D4's companion for the surrounding work).
- `handouts/C10-what-good-looks-like-review-rubric.md` — for reviewing the
  agent's output against the spec, not just that it ran.

---

## What you'll do this session

1. **Take the vague ask.** A realistic request — *"give me clean monthly volumes
   by terminal"* — and see why, as written, it isn't buildable.
2. **Sharpen it into a data spec.** Pin the four things that decide whether the
   numbers are right: **grain, filters/exclusions, units, edge cases.** Make
   "done" concrete.
3. **Extract the real rules.** Direct the agent to lift the actual business logic
   out of `vol_report.py` and the schema — and to distrust the comments while it
   does it (the Session 3 skill, applied).
4. **Plan before building.** Hand the spec to planning mode; review and approve a
   step-by-step plan before any code is written.
5. **Build it.** Start a clean `pipeline.py` — you directing, the agent executing.
6. **Review like a new engineer's PR.** Check the output against the spec, and
   reconcile against the legacy numbers.

---

## What you'll leave with

- A **sharpened data spec** for the monthly-volume rollup.
- A **running `pipeline.py`** that computes at least physical volume correctly,
  reconciled against the legacy script for a known month.
- The habit that makes all of this work: **decide the ambiguous things in writing
  before the agent decides them for you.**

You don't need to finish the whole pipeline today. A correct, reconciled slice
plus a clear spec is the goal. Session 5 scales the rest.

---

## Before the session

- Have your laptop, Claude Code installed and working, and the student repository
  on your machine.
- Confirm the database opens (see `data/README.md`).
- Bring your **Homework 2 intent dossier** for `vol_report.py` — you'll reuse what
  you learned about which comments lie.
- Come ready to build, not just discuss.

---

## The through-line (same as every session)

Column names are generic, several values are bare integer codes, and the
documentation is intentionally incomplete. Treat the **behavior of the code and
the contents of the data as the source of truth** — not the column names, not the
comments, not even the spec until you've checked it against the data. A spec is a
hypothesis about the right number; reconciliation is how you test it.
