# Session 5 — Close Your Loop

U.S. Energy AI Software-Development Training · Session 5 of 5 · hour 1 of the
2-hour slot (the second hour is a separate presentation)

**Theme: everyone finishes their own loop, watches the whole thing close, and
sees how five sessions were one idea.** Session 4 ran the real development loop
— spec, skill, stories on the board, a tests-first plan, a validated build, a
change absorbed, docs, a commit and a PR — and almost nobody got through all
eight steps in the room. Good: finishing them is exactly the right homework,
and today is built around wherever you actually are. You'll see the final two
steps — the **clean-context review + merge** and the **ticket close** —
demonstrated live, then spend a 30-minute work block climbing from your own
rung. We close by tying the whole series together.

---

## In this folder

- `README.md` — this orientation.
- `LAB-GUIDE.md` — **today's guide**: the re-entry prompt, the ladder (start
  wherever you are), and the two new steps that close the loop (Step 9: review
  + merge · Step 10: close the tickets).
- `EXTRA-CREDIT.md` — the ambitious track, self-paced: extend the dashboard
  with **parallel subagents** against your contract. (This was the original
  Session 5 group lab; it's now yours to run at your own speed.)
- `starter/` — the working one-table dashboard (Homework 3's safety net).

You'll also use:

- `../session-4/LAB-GUIDE.md` — Steps 1–8 live there; most of the room resumes
  in it today.
- `../../homework/homework-3-brief.md` — the dashboard skeleton (now optional —
  see the note at its top).
- `../../handouts/C11-advanced-claude-code.md` — **new**: status line,
  scheduled runs, `/loop` & `/goal`, subagents & orchestration. Concepts and
  first steps for after the course.

---

## How the hour runs

1. **Share-back (10 min).** Finishing the steps solo, without the room: how far
   did you get, what did you push back on, did the gates catch anything?
2. **The loop closes — live (5 min).** The instructor's Session 4 repo gets the
   clean-context review, the merge, and the ticket close, on the real board —
   plus a 60-second look at where this was all headed (the dashboard).
3. **Work block (30 min).** The ladder in `LAB-GUIDE.md`. Today's target is
   **through Step 5 (the done-gate)** if you're mid-build, **Steps 9–10** if
   you're shipped. Ahead of everyone? Homework 3, then `EXTRA-CREDIT.md`.
4. **The series, tied together (15 min).** Sessions 1–4 revisited through what
   you just did — then what's yours to keep.

---

## What you'll leave with

- **Your own closed loop** — or a validated service plus the exact, demonstrated
  path to close it at your desk (every step works identically outside the
  classroom).
- The **clean-context review** habit: a fresh session, reviewing against the
  spec and running the evidence itself, with no stake in the code it's judging.
- A board that tells the truth: stories Closed because the merge delivered them.
- The map for going further on your own: `EXTRA-CREDIT.md` and handout **C11**.

---

## Before the session

- `git pull` in the course repo (this guide and two new documents landed this
  week).
- Know where your Session 4 repo is (`<initials>-volume-service`, the sibling of
  the course clone) and have Claude Code launching.
- If Azure DevOps fought you in Session 4, bring the exact error — we triage in
  the first ten minutes so the work block isn't spent on auth.

---

## The through-line, one last time

The data hasn't changed: generic column names, bare integer codes, comments
that lie. Neither has the discipline: **behavior and data are the source of
truth; comments are evidence, not authority; a number is right when it
reconciles, not when it looks plausible.** Today adds the last piece — *done*
isn't your own session agreeing with itself; it's fresh eyes, the evidence
re-run, the merge, and the board saying so.
