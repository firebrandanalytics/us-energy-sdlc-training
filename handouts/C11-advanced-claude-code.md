# C11 — Advanced Claude Code: The Power Tools

**Concepts and pointers, not exercises.** Everything in the course so far ran in
one interactive session: you ask, you read, you approve. These five features are
what's past that — and every one of them is the same discipline you already
practice (gates, contracts, review), running with less of you in the room.
Surfaces evolve quickly: treat this card as the map, and check `/help` and
**code.claude.com/docs** in *your* installed version before leaning on anything.

---

## 1 · Make the status line yours

**What it is.** The strip at the bottom of Claude Code is configurable: a
`statusLine` entry in `settings.json` runs a small script whose output is your
status bar — model, git branch, context usage, cost, whatever you decide you
should never have to ask about.

**Why you'd bother.** Session 2's levers (model, context, mode) only help if you
*notice* them. Knowing you're on the expensive model, or that context is nearly
full, **before** the big ask is operator awareness made permanent.

**First step.** Type **`/statusline`** and describe what you want — Claude Code
sets it up for you (it writes the script and the setting). Docs:
*code.claude.com/docs → Settings*.

---

## 2 · Agents on a clock — scheduled runs

**What it is.** Two documented paths:

- **`/schedule`** — recurring or one-off tasks on Anthropic's cloud
  infrastructure ("routines"; manage at *claude.ai/code/routines*). Runs without
  your machine on. *Research preview — expect change.*
- **Headless mode** — `claude -p "<prompt>" --permission-mode acceptEdits`
  prints a result and exits, which means your ordinary OS scheduler (cron, Task
  Scheduler) can run an agent like any other job. Stable, works anywhere.

**Why you'd bother.** Your Session 4 done-gate — *tests, reconcile, log ↔
database* — is a prompt. Scheduled nightly against the volumes service, it's a
monitor: silence when the numbers hold, a morning message when they drift.
Drudge work you don't even have to start.

**First step.** Run your validation prompt once via `claude -p` and read the
output; *then* think about a schedule. Docs: *Routines* and *Headless mode*.

---

## 3 · Loops and goals — iterate without re-prompting

**What it is.**

- **`/loop 10m <prompt>`** re-runs a prompt on an interval inside your session
  (or `/loop <prompt>` and it picks its own pacing). Needs a recent version
  (v2.1.72+); recurring loops expire after 7 days.
- **`/goal <condition>`** keeps the session working **until a condition is
  met** — *"keep going until all tests pass"* is the canonical one.

**Why you'd bother.** You already lived the manual version in Session 4: the
agent iterated to green while you watched. `/goal` is that loop made explicit —
and it's exactly as trustworthy as its gate. A goal of *"until tests pass"*
against tests you never read is automation of a mistake.

**First step.** On a branch with a failing test: `/goal keep working until
pytest is green`, then review the diff like always. Docs: *Scheduled tasks* and
*Goal*.

---

## 4 · Subagents, and orchestrating many of them

**What it is.**

- **Subagents** (stable): scoped workers your session spawns — each with its own
  clean context, returning a summary. You met the pattern twice: Session 4's
  option to split work, and Step 9's **clean-context reviewer**, which is a
  subagent done by hand. Define reusable ones with **`/agents`** (they live in
  `.claude/agents/` — give your reviewer the C10 rubric and your skill).
- **Agent view** (`claude agents`) — dispatch and monitor several independent
  background sessions from one screen. *Research preview.*
- **Dynamic workflows** — script the orchestration itself: fan work out to many
  subagents, cross-check results, run in the background (v2.1.154+; try the
  built-in `/deep-research`). *Research preview.*

**Why you'd bother.** EXTRA-CREDIT.md has you split a dashboard across two
subagents against a contract, by hand. These features are that same move at
scale — ten files to migrate, every query in a repo to audit — where the
contract and the verification step decide whether scale helps or just produces
wrong answers faster.

**First step.** `/agents` → create a `code-reviewer` that loads your
`us-energy-volume-rules` skill, and point it at your own PR. Docs: *Subagents*,
*Agent view*, *Workflows*.

---

## 5 · The browser is a tool too — test it like a user

**What it is.** Your dashboard tests call routes in-process — fast, but no
browser ever opens, so nothing proves the chart renders or the dropdown
actually filters. **Playwright** closes that gap, and two routes are equally
acceptable:

- **Directly, as code** (the way we use it ourselves): the agent installs it
  like any package (`pip install playwright && playwright install chromium`),
  writes a pytest that opens the page, picks a month, clicks DAL, and asserts
  what a *user* would see — then runs it headless like any other test. No new
  plumbing; this is Session 2's "Claude Code is also a shell," pointed at a
  browser.
- **Playwright MCP** (`claude mcp add playwright npx @playwright/mcp@latest`):
  wires the browser in as a tool the agent drives step by step — navigate,
  click, read, screenshot. Especially handy in Claude Desktop, or for
  exploratory "watch it click around" debugging before you ask for durable
  test code.

There's also **Claude in Chrome** — the extension (`claude --chrome`) that
drives the browser you're already logged into. GA on direct Anthropic plans
but beta and Chrome/Edge-only: check your plan and your browser policy first.

**Why you'd bother.** Half of what your team owns has a UI in front of it, and
"click through it like a user" is currently a human's job — Move 3 of the
extra credit is literally you, clicking. This makes that a test that runs
without you.

**The thought to leave with.** Your acceptance criteria were checkable all
course. The step past that — one we're exploring ourselves — is writing the
**test plan itself in natural language** (*"pick 2025-08, open DAL, the
numbers match the service"*) and letting the agent execute the *same plan*
against the JSON API or through the browser against the GUI. One plan, two
surfaces: the plan becomes the artifact, and the executor is fungible. If that
idea grabs you, you're ready for what comes after this course.

**First step.** Ask the agent to write one Playwright test for your
extra-credit dashboard's month filter and run it headless. Docs:
*playwright.dev* · *code.claude.com/docs → MCP, Chrome*.

---

## The rule that doesn't change

Every feature on this card removes a moment where you'd naturally be watching.
None of them removes your ownership. The Session 1 rule scales with the
automation: **an agent is exactly as trustworthy as the gates you put around
it** — least permission, checkable criteria, evidence before "done." Automate
the loop only after you've run it by hand and trust its gates. (You have. You
did. Start small.)
