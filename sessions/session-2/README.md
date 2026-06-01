# Session 2 — Operating the Agent + Claude Code as Your Shell

**Date:** 6/4 · **Format:** 2 hours, online (Teams) · **Hands-on:** yes

Session 1 was about the mindset. This session is about the controls. You'll
learn the handful of levers you actually turn day to day when you operate an
agent, you'll start using Claude Code as a replacement for routine command-line
work, and you'll do your first end-to-end rep — bootstrapping a small project by
directing the agent instead of typing the commands yourself.

This is the first hands-on session. Have Claude Code installed and launching
before we start. If it isn't working, flag it at the top — we'll verify live.

---

## What this session covers

- **The control surface.** The five levers you adjust to operate an agent: how
  much it does before checking in (approval modes), planning before it acts,
  splitting work across parallel sessions (subagents), managing its working
  memory (context), and picking the right model for the job.
- **How those choices drive cost** — and why cost is downstream of good habits,
  not a separate thing you optimise later.
- **Ownership and governance.** Code the agent writes is yours to ship. You
  review it the way you'd review a new junior engineer's pull request.
- **Claude Code as your shell.** Files, git, packages, environment — described as
  outcomes, not typed as commands. Plus reaching Microsoft 365 (email, Teams,
  SharePoint) from the same place.
- **Live walk-through:** planning mode, the approval flow, and letting the agent
  run on low-risk steps.
- **Hands-on rep:** each of you bootstraps a small project end to end by
  directing the agent.

This session does **not** use the course dataset. That arrives in Session 3.
Today you work with a throwaway project and, in the homework, with one real task
from your own work.

---

## In this folder

- `README.md` — this file. Read it before the session.
- `HANDS-ON-bootstrap.md` — the in-session rep: bootstrap a small Python project
  end to end by directing Claude Code. We'll do this together, then you'll
  finish it on your own.

Keep these reference cards open from here on (they live in the course handouts):

- **C5 — Approval Mode Decision Matrix.** When to use Manual, Auto Mode, or run
  unsandboxed. The middle column is your default.
- **C6 — Model Selection Cheat Sheet.** Haiku / Sonnet / Opus trade-offs and the
  "Plan/Execute split" pattern.
- **CC — Claude Code Commands Card.** The ~20 commands and shortcuts worth
  memorising. `Ctrl+E` is the one to build muscle memory for.
- **C9 — Microsoft Graph CLI Quick Reference.** Reaching email, Teams, and
  SharePoint from the command line.

---

## The five levers, in one paragraph each

You don't need to memorise these before the session — we'll walk through each
one. This is so the vocabulary is familiar when we get there.

**1. Approval modes — how much the agent does before it checks in.**
Three modes, cycled with `Shift+Tab`. *Manual* stops and asks before every file
write or command. *Auto Mode* lets edits through automatically and still asks
before shell commands. *Plan mode* writes nothing — it only plans. You start in
Manual on anything unfamiliar and step up to Auto Mode once you trust the
direction. (Card: **C5**.)

**2. Planning mode — plan before you act.**
Cycle into plan mode and the agent does exactly one thing: it reads the relevant
code, writes a structured plan for what you asked, and stops. No edits, no
commands. You read the plan like you'd read a diff, push back on anything wrong,
and tell it to `proceed` only when you're satisfied. Mistakes caught in the plan
are free; mistakes that reach the code cost a re-run.

**3. Subagents — split work that's genuinely parallel.**
A subagent is a subordinate session the main session spawns to handle a scoped
piece of work in parallel. The parent delegates, the subagent executes, the
parent reviews and integrates. Worth it when the pieces don't depend on each
other — for example, one auditing your loader while another audits your
validation rules. Not worth it for small or sequential work.

**4. Context — manage the agent's working memory.**
Every session accumulates context: files read, edits made, output produced. Long
sessions drift — the agent forgets a constraint or re-proposes something you
rejected. `/compact` summarises the conversation and keeps going; `/clear` wipes
it and starts fresh; a brand-new `claude` session is the cleanest reset. A
`CLAUDE.md` file at the project root gives the agent the project context it would
otherwise guess. (We work with `CLAUDE.md` for real in later sessions.)

**5. Model selection — match the model to the task.**
*Haiku* for fast, mechanical work (boilerplate, reformatting, simple
search-and-replace). *Sonnet* for the everyday workhorse jobs (building from a
clear spec, navigating a codebase, writing tests, reviewing code). *Opus* for
genuinely hard reasoning (sharpening contradictory requirements, tricky
architecture, a subtle bug other tiers keep getting wrong). "Use the best model
every time" is not a strategy — it's slow and expensive for work the cheaper
tiers do as well or better. (Card: **C6**.)

---

## Claude Code is also a shell

In the morning of Session 1, Claude Code looked like an editor — it read code,
explained code, changed code. The second thing it is, is a **shell**. It runs
commands. Anything your terminal can do, it can do: `mkdir`, `git init`,
`pip install`, run a SQL query, call a CLI. You describe the outcome; it types
the commands.

That's the upside. The downside is the same thing: anything your terminal can do
includes the things you don't want it to. `rm -rf`. `git push --force`. A
`DROP TABLE` against the wrong connection. **The agent is exactly as powerful as
the credentials it holds** — which is why the approval modes and the
least-permission habits from Session 1's risk discussion matter here.

Two practical examples we'll touch on today:

- **Everyday CLI work.** "Create a `data/` directory, drop a small sample CSV of
  terminal lifts in it, initialise a git repo, and make the first commit." That's
  six commands you didn't type.
- **Reaching Microsoft 365.** From the same prompt, you can have the agent draft
  an email, post a status to a Teams channel, or pull a spreadsheet from
  SharePoint — via Microsoft Graph (card **C9**). The discipline is the same as
  any other tool: give it scoped access, and review before it sends.

---

## Ownership and governance — the one rule

Code the agent writes is code **you** commit and **you** own. "The AI wrote it"
is not an incident explanation and not a code-review answer.

The practical version of this is simple: **review the agent's work the way you'd
review a new junior engineer's pull request.** Check it against what you actually
asked for — not just that it runs. A query that runs and returns a number can
still be returning the *wrong* number. (That's the whole of Session 3.)

Architecture decisions the agent makes implicitly — a library it reached for, a
schema assumption it baked in — are decisions you've delegated. Surface them and
own them. U.S. Energy has its own AI-use policies; those take precedence over
anything in this course.

---

## Pre-session prep

**Come with one real task from your actual work in mind.** Not a toy problem. A
real one — something you'd normally do by hand in a terminal. We'll use it to set
up your Homework #1, and you'll want a concrete task you care about rather than
something invented on the spot.

Good candidates:

- A report or data pull you normally script by hand
- Generating boilerplate for a new loader, transform, or test suite
- Refactoring a query or script you've been meaning to clean up
- Scripting a repetitive git workflow (branch, commit, open a PR)
- A small helper or wrapper for something your team does often

Avoid anything that needs production access you can't safely sandbox, or where a
mistake would be hard to reverse. The point is to learn the tool, not to
introduce risk.

---

## Readiness checklist

- [ ] Laptop with you
- [ ] Claude Code installed and launching — this session is hands-on, so flag it
      now if it isn't working
- [ ] Access to the student repository confirmed
- [ ] One real task from your work in mind to direct the agent on

---

## After this session

**Homework #1** is assigned at the end — run Claude Code end to end on that one
real task before Session 3. The brief is in
`../../homework/homework-1-brief.md`.

**Looking ahead:** Session 3 introduces the working dataset — a realistic U.S.
Energy fuel-movements database — and turns the agent loose on reading SQL and a
schema you didn't write. The planning-mode and subagent levers you meet today
get used for real across Sessions 3–5.
