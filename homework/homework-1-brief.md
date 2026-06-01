# Homework #1 — Run Claude Code on One Real Task

**Assigned after:** Session 2
**Due before:** Session 3
**Time budget:** 30–60 minutes

---

## The Assignment

Pick one small, concrete task from your current work — something you'd normally
do by hand in a terminal. Not a toy problem. A real one.

Then complete it end to end using Claude Code, the way we practised in Session 2:
you describe the task, the agent plans and executes, you review and approve, you
own the result.

This is the same move as the in-class bootstrap, but pointed at real work instead
of a throwaway project. It's also your first chance to feel the control surface —
approval modes, planning, model choice — on a task you actually care about.

---

## Requirements

**1. Use Claude Code to complete the task — not to assist while you do the typing.**
The goal is a full agentic pass: you describe the task, the agent plans and
executes, you review and approve. No tab-completing your way through with the
agent watching. If you find yourself typing the commands, stop and hand them back
to the agent.

**2. Use planning mode at least once.**
Before a substantive step, ask Claude Code to write a plan (cycle in with
`Shift+Tab`, or launch with `claude --permission-mode plan`). Read the plan before
you let it proceed. Even if the plan looks obvious, practise the habit — and watch
for a decision the plan surfaces that you hadn't actually made.

**3. Try one short Auto Mode stretch.**
Switch to Auto Mode (`Shift+Tab`) for part of the task and let the agent make a
few decisions without stopping at every step. Note one moment where Auto Mode
approved an action you'd have paused to review manually — or note that nothing
surprised you, which is also a finding.

**4. Review before you accept — every file.**
This is the governance habit from Session 2: glance at each change before you
approve it, and check the result against what you actually asked for, not just
that it ran. Press `Ctrl+E` on at least one approval prompt to see the exact
action first.

---

## Reflection — Three Bullets

After the session, write three short bullets:

1. **One thing that worked better than expected.**
2. **One thing that surprised you** — good, bad, or just unexpected.
3. **One question you want answered in Session 3.**

Keep each to two or three sentences. You're not writing an essay — you're
capturing the thing freshest in your memory while it's still fresh.

---

## Choosing a Task

Good candidates for this homework:

- Running a report or data pull you normally script by hand (e.g., a monthly
  volume or RIN-transaction extract)
- Generating boilerplate for a new loader, transform, or test suite
- Refactoring a query or script you've been meaning to clean up
- Scripting a repetitive git workflow (branch, commit, open a PR)
- Writing a small helper or wrapper for something your team does often (e.g., a
  CLI that formats a recurring export)

**Not recommended:** tasks that need access to production systems you can't safely
sandbox, or where a mistake would be hard to reverse. The point of this homework
is to learn the tool, not to introduce risk. If the only realistic version of
your task touches prod, scope a smaller, safe slice of it instead.

> **Tip.** If your in-class bootstrap project was a real-task scaffold, this is
> the natural place to push it one step further — turn that stub into something
> that actually does the job.

---

## What to Bring to Session 3

Your three bullets. We'll open Session 3 with a few of them — 2–3 people will
share briefly, and we'll use them to surface the themes we build on next.

You don't need slides or a write-up. Just bring the bullets — and if you hit
something interesting, be ready to describe what happened in two minutes.

---

## Looking Ahead

Session 3 introduces the course dataset — a realistic U.S. Energy fuel-movements
database — and turns the agent loose on reading SQL and a schema you didn't
write. The homework that follows (Homework #2) is an **intent dossier** on a
crusty legacy script: what it *truly* computes, and which of its comments are
lying. This homework is the warm-up for that — getting comfortable directing the
agent end to end, so that next time you can point it at code you don't trust and
make it earn the explanation.

---

*Questions? Bring them to Session 3 — that's what the opening minutes are for.*
