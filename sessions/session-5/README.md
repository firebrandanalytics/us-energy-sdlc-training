# Session 5 — Extend the Dashboard, and What's Next

U.S. Energy AI Software-Development Training · Session 5 of 5 · 2 hours, online

**Theme: scaling a real build with parallel agents, making it trustworthy, and
seeing where this pays off in your work.** Session 4 turned a vague ask into a
sharpened spec and a clean **service** that returns reconciled monthly volumes. In
Homework 3 you put a one-view dashboard skeleton on top of it. This session
finishes the job the way a team actually ships a feature: you confirm the
**contract** between the app and the service, **split the remaining work across
parallel subagents**, wire it together, and then make the result *trustworthy* with
tests and a short README. Then we step back: where does this loop earn its keep in
your day-to-day, and what comes next.

This is **Exercise 2, part 2** — the close of the full-stack arc you've been
building: comprehend the legacy code (S3) → build the service (S4) → **build and
extend the app on it (HW3 + today)**.

---

## In this folder

- `README.md` — this orientation.
- `LAB-GUIDE.md` — the hands-on reference for the whole session. The instructor
  walks the room through each step live; this guide lets you keep moving if you
  fall behind or pick up from any step if you arrive late.
- `starter/` — a working dashboard starter. If your Homework 3 build isn't running,
  `cp -r starter/* .` and you're caught up. **Nobody is blocked today.**

You'll also use, from elsewhere in the repo:

- `data/us_energy.sqlite` — the working database (read through the service).
- Your **`service.py`** from Session 4 and your **dashboard** from Homework 3 — the
  foundation you extend here.
- `handouts/D5-output-contract-and-dashboard.md` — the contract pattern and FastAPI
  reference.
- `handouts/C10-what-good-looks-like-review-rubric.md` — for reviewing the agents'
  output against the contract, not just that it ran.
- `handouts/C5-approval-mode-decision-matrix.md` — for deciding when to let the
  agents run and when to gate them.

---

## What you'll do this session

1. **Share back Homework 3.** Your dashboard skeleton — one win, one snag. (Didn't
   finish it? Pull the starter — see above — and you're in.)
2. **Confirm the contract.** The app and the service already meet at one seam: the
   shape of a row the service returns. You'll pin that contract in a few lines —
   it's what lets two agents extend different parts at once without colliding.
3. **Split the work across parallel subagents.** One subagent grows the **main
   view** (a month filter and a simple chart); another adds **new routes** (a
   terminal-detail page and a JSON API). They work in parallel against the
   contract; the main session integrates.
4. **Wire it together and verify end to end** — click through it, confirm the
   numbers still reconcile to Session 4, and check the JSON API returns the
   contract.
5. **Make it trustworthy.** Direct the agent to generate the tests and short
   documentation that let someone else trust this app.
6. **The art of the possible.** Where this loop pays off in your real work —
   legacy comprehension, building internal tools fast, migrations, automation — and
   a short look beyond the terminal.
7. **Course close.** The loop you ran end to end, the habits to keep, and Q&A.

---

## What you'll leave with

- A **working dashboard** with a month filter, a simple chart, a terminal-detail
  page, and a JSON API — all reading clean, reconciled numbers through your service.
- A small **test suite** the agent built against the contract — including a check
  that the app's numbers still match the Session 4 service.
- The pattern that scales all of it: **a written contract is what lets you split
  work across parallel agents and trust that the pieces fit.**
- A concrete sense of where to point this at your own backlog on Monday.

You don't need a flawless, fully featured app to get the value. A dashboard whose
numbers you trust, extended by a split you understand, is the deliverable. Variance
across the room is expected and fine.

---

## Before the session

- Have your laptop, Claude Code installed and working, and the student repository
  on your machine.
- Have your **Homework 3** dashboard running — `uvicorn app:app --reload` should
  serve a table at `http://localhost:8000`. **If it isn't running, that's fine:**
  `cd sessions/session-5 && cp -r starter/* .` gets you a working skeleton.
- Bring **one example from your own work** where you'd build a small internal tool
  or read-only view over data you own.

---

## The through-line (same as every session)

Column names are generic, several values are bare integer codes, and the
documentation is intentionally incomplete. Treat the **behavior of the code and
the contents of the data as the source of truth** — not the column names, not the
comments, not even the spec until you've checked it against the data. Scaling the
build does not change that discipline: a contract two agents agree on is still only
a hypothesis until the app's numbers reconcile against a figure you trust. The
service made the numbers right; the contract is what lets the app stay right while
two agents grow it at once.
