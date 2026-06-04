# Session 4 — From Vague Ask to a Working Service

U.S. Energy AI Software-Development Training · Session 4 of 5 · 2 hours, online

**Theme: turning a fuzzy request into a specification the agent can build against
— then building it as a clean, reusable *service*.** Session 3 was about *reading*
what you didn't write. This session turns comprehension into construction: you take
a vague stakeholder ask, sharpen it into a real spec, direct the agent to lift the
true business rules out of the crusty legacy script and the ambiguous schema, and
build a clean Python **service** — a data layer something else can call.

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
- `data/vol_report.py` — the legacy rollup script you're replacing.
- `handouts/D4-data-spec-template.md` — the data-spec template you'll fill in.
- `handouts/D5-output-contract-and-dashboard.md` — the output-contract pattern and
  a FastAPI quickstart (you'll lean on it for Homework 3 and Session 5).
- `handouts/C7-ai-ready-spec-template.md` — the general AI-ready spec template
  (D4's companion for the surrounding work).
- `handouts/C10-what-good-looks-like-review-rubric.md` — for reviewing the
  agent's output against the spec, not just that it ran.

---

## What you'll do this session

1. **Take the vague ask.** A realistic request — *"give me clean monthly volumes
   by terminal"* — and see why, as written, it isn't buildable.
2. **Sharpen it into a spec — including the output contract.** Pin the four things
   that decide whether the numbers are right (**grain, filters/exclusions, units,
   edge cases**) *and* the shape of one output row — because the dashboard you
   build next consumes exactly that shape.
3. **Extract the real rules.** Direct the agent to lift the actual business logic
   out of `vol_report.py` and the schema — distrusting the comments while it does
   it (the Session 3 skill, applied).
4. **Plan before building.** Hand the spec to planning mode; review and approve a
   step-by-step plan before any code is written.
5. **Build the service.** A clean `service.py` that *returns* clean monthly volumes
   (it doesn't just print them) — you directing, the agent executing.
6. **Review like a new engineer's PR.** Check the output against the spec, and
   reconcile against the legacy numbers.

---

## What you'll leave with

- A **sharpened spec** for the monthly-volume rollup, including a written **output
  contract** (the row shape your app will rely on).
- A **running `service.py`** that returns physical and taxable volume correctly,
  reconciled against the legacy script for a known month — and that you can call
  from a three-line script or, next, from a web app.
- The habit that makes all of this work: **decide the ambiguous things in writing
  before the agent decides them for you.**

You don't need to finish everything today. A correct, reconciled service that
returns physical and taxable volume, plus a clear contract, is the goal. The RIN
measure is a stretch; the dashboard comes next.

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
