# Lab Guide: From Vague Ask to a Shipped Service — Session 4

U.S. Energy AI Software-Development Training · Session 4 (120 min)

This is your reference for the session. The instructor walks the room through each
step live; this guide is here so you can keep moving if you fall behind, or pick
up from any step if you arrived late.

---

## The loop (this session and the next are one arc)

Today we stop doing *exercises* and run the **actual software development loop**,
end to end, with the agent doing the labor and you directing:

```
vague ask → spec + contract → capture knowledge (a skill) → stories ON THE BOARD
        → plan (tests first) → approve, and let it build to green
        → validate: tests + the run log + the database
        → a change request lands → prove nothing broke (compare the logs)
        → documentation → ship: repo, branch, commit, PR
        → [Session 5: clean-context review, merge, close the tickets, in parallel]
```

**One heads-up about how today feels:** the agent will produce each artifact in a
minute or two. The work — *your* work — is **reading**: the plan before you
approve it, the tests before you trust them, the docs before you'd hand them to a
teammate. The building is fast; the understanding is the job.

> **Script vs. service — the one distinction the build turns on.** The legacy
> `vol_report.py` *prints* a report and exits. A service *returns* the numbers as
> data (`monthly_volumes("2025-08")` hands back rows) — something you can call,
> test, and build a UI on. Ours will also **log** — every run leaves a file.

---

## Environment

You will work in **`sessions/session-4/`** (this folder). From here, the committed
database is at **`../../data/us_energy.sqlite`**.

### Set up (you did most of this in the pre-session email)

```bash
cd sessions/session-4
python3 -m venv venv
source venv/bin/activate            # Windows Git Bash: source venv/Scripts/activate
pip install pytest
```

(If `python3` isn't found, use `py -3` or `python` — whichever worked for you in
Homework 2 — consistently throughout.)

**Azure DevOps** (also from the pre-session email — takes one minute if done):

```bash
az extension add --name azure-devops        # once
az login                                    # browser sign-in
az devops configure --defaults organization=https://dev.azure.com/<your-org> project=<your-project>
az boards work-item list --top 1 -o table   # any output (even "no items") = you're in
```

> **If DevOps fights you** (permissions, tenant policy, anything): **don't burn
> lab time on it.** Note the exact error and keep going — every DevOps step below
> has a 30-second local fallback, and we sort access before Session 5.

### Confirm the database and the legacy script

```bash
python3 -c "import sqlite3; print(sqlite3.connect('../../data/us_energy.sqlite').execute('SELECT COUNT(*) FROM lifts').fetchone())"
# -> (50025,)
( cd ../../data && python3 vol_report.py 2025-08 )    # created in HW2; listing is in homework/homework-2-brief.md if missing
```

**Keep that legacy output on screen** — it is your reconciliation anchor all
session, and you'll check the agent's tests against it.

> **One ground rule for the whole session:** until your Session 4 commit exists,
> **don't open or let the agent read anything under `sessions/session-5/`** —
> that's next week's folder, and peeking at it skips the only part that transfers.

---

## Step 1 — Sharpen the vague ask into a spec (18 min)

### The ask

> "Hey — can you get me clean monthly volumes by terminal? The old
> `vol_report.py` sort of does it but I don't trust the numbers and nobody
> remembers how it works. I just want something I can pull each month and hand to
> the desk. Should be quick — the data's all there."

It sounds clear. It is not buildable. *Clean* how? Which gallons? Does a voided
ticket count? A book adjustment? Tax-exempt dyed diesel? Every one of those is a
decision that **changes the number** — and what you don't decide, the agent
decides for you.

### Interrogate, then write

Open Claude Code in this folder and have it surface the decisions first:

```
Read ../../data/vol_report.py, ../../data/DATA-DICTIONARY.md, and the schema of
../../data/us_energy.sqlite (run: .schema lifts). I have a vague request: "clean
monthly volumes by terminal." Before I write any spec or code, list every
decision this ask leaves implicit, grouped: grain, filters/exclusions, units,
edge cases. Do not propose a design yet.
```

Your Homework 2 dossier holds most of the answers — that's why we did it. Then
fill in **`handouts/D4-data-spec-template.md`** (draft your own answers from your
dossier **before** peeking at D4's worked example), and add the **output
contract** (**D5** is the card):

```
One output row =
  terminal      str    terminal display code, e.g. "DAL"
  month         str    "YYYY-MM"
  physical_gal  int    SUM(net_gal) over real movements
  taxable_gal   int    physical minus dyed off-road diesel (prod_cd 6)

Invariants the caller can rely on:
  - physical_gal >= taxable_gal >= 0   (taxable is a subset of physical)
  - exactly one row per (terminal, month)
```

> **The discipline:** if you can't fill in **Grain** and **Filters / Exclusions**
> precisely, the ask is still vague. The contract becomes your tests, almost word
> for word — and next week the dashboard reads exactly that shape.

---

## Step 2 — Capture what you know as a *skill* (10 min)

Your HW2 dossier lives in a doc only *you* will read. Turn it into a **skill** —
a file the agent itself loads — and every future session (yours, and the parallel
agents in Session 5) starts already knowing the rules.

A skill is a folder with a `SKILL.md`: **YAML frontmatter** (`name`, plus a
one-line `description` saying *when to use it*), then the knowledge as markdown.
Claude Code auto-discovers them in `.claude/skills/`.

```
Create a skill at .claude/skills/us-energy-volume-rules/SKILL.md capturing the
verified rules of this dataset from my Homework 2 dossier, pasted below. Format:
YAML frontmatter with name: us-energy-volume-rules and a one-line description
saying when to use it (computing, reviewing, or testing volume numbers from the
lifts table). Body, one page max: each magic code's meaning and which measures
exclude it; which gallon column and why; the physical-vs-taxable asymmetry; the
RIN correction (what's stale in the legacy script and where the right values
live); the reconciliation anchors; query hygiene (sargable month range, named
constants).

MY DOSSIER:
<paste the relevant parts>
```

**Review it like a PR** — does it carry the *verified* rules (your dossier), not
the comments' claims? Add the line the agent may miss: `mode = 8`'s meaning is
**confirmed with the feed owner** (S3's open question, now settled — flag the
unknown, get it confirmed, write down the fact).

**Prove it loads — with specifics, not vibes.** Fresh Claude Code session at the
repo root:

> Read only `.claude/skills/us-energy-volume-rules/SKILL.md`. Summarize the
> monthly volume rules from that skill — including the exact status / mode /
> prod_cd codes and which measures exclude each. If you can't name all three
> codes and their scope, say the skill didn't load.

The bar: **status 8 and mode 8 (every measure), prod_cd 6 (taxable only)** —
body-only facts a generic answer can't fake.

---

## Step 3 — Stories on the board · the repo · your branch (12 min)

A spec says what *right* means; **stories** slice it into shippable, checkable
work — and today they go on the **real Azure DevOps board**, because that's
where work lives at U.S. Energy. Then the work gets a *home* — repo and branch —
**before any code exists**, because that's the order real work happens in.

**First, draft them:**

```
From the spec below, draft user stories as stories.md in this folder: (1) the
volumes service (monthly_volumes + months honoring the output contract, with
per-run file logging), (2) a thin reconcile CLI that calls the service, (3)
[stretch] a corrected RIN measure from the rin_transactions ledger, and (4) one
short story per Session-5 dashboard extension (month filter, chart, terminal
detail, JSON API). Each story: "As <who> I want <what> so that <why>" plus 3-5
acceptance criteria that are CHECKABLE — a test that can pass or a query that can
prove it, not vibes.

THE SPEC:
<paste your spec>
```

**Edit pass:** delete any criterion you couldn't check mechanically. *"Works
correctly"* is not a criterion; *"DAL 2025-08 physical = 1,517,103"* is.

**Then put them on the board** — the agent drives:

```
For each story in stories.md, create an Azure DevOps work item:
az boards work-item create --type "User Story" --title "<story title>"
--description "<the story + its acceptance criteria>". (If the project's process
doesn't have "User Story", use --type Issue.) Then list the created IDs and put
each ID back into stories.md next to its story.
```

Note your **service story's work-item ID** — a change request is going to land on
it later, and Session 5 closes it.

**Now the repo and the branch.** One GitHub habit to unlearn here: in Azure
DevOps, work items don't live *inside* a repo (the way GitHub issues do) — they
live at the **project** level, and get tied to your repo through **branch and
pull-request links**. So: repo first, then a branch named for your story, and the
linkage builds itself from there.

```
Set up my repo and working branch:
1. Create a repo for me: az repos create --name <initials>-volume-service
2. Add it to this clone as a remote named "devops" and push main to it.
3. Create and switch to a branch named story/<my-service-story-ID>-volume-service
   and push that too.
Show me the remote URL and the branch when done.
```

Everything you build from here happens on that branch — and lands on the board's
radar the moment the PR links it to your story.

> **Fallback (no DevOps yet):** `stories.md` *is* the stories artifact, and
> `git switch -c story/volume-service` gives you the same branch locally — the
> remote arrives in Session 5. Nothing else changes. Keep moving.

---

## Step 4 — Plan it, read the plan, approve — and let it run (12 min + the build)

Switch into planning mode (`claude --permission-mode plan`, or `Shift+Tab`).
Plan mode means the agent **can read everything and touch nothing** — so think it
through with it, freely:

```
Plan story 1 from stories.md: a clean volumes service in this folder — a SERVICE,
not a script (it RETURNS data; a web app calls it next week). Load the
us-energy-volume-rules skill. The plan must include:

1. TESTS FIRST: test_service.py exists and runs (failing) before service.py.
   The tests encode the output contract (field names and types), the invariants
   (physical >= taxable >= 0; one row per terminal-month), and the exact 2025-08
   reconciliation anchors — take them from the printed output of
   "cd ../../data && python3 vol_report.py 2025-08", not from memory.
2. The functions — monthly_volumes(month) and months() — and exactly what each
   RETURNS (list of dicts in the contract shape).
3. The exact SQL for physical and taxable: every filter named, the gallon column
   named, the month bounded by a RANGE on lift_ts (never substr/strftime around
   the column).
4. LOGGING: every run writes a separate log file (logs/run-<timestamp>.log) with
   one deterministic, diffable line per output row — not just stdout. Two runs
   must be comparable with a diff.
5. A thin CLI that CALLS the service (a consumer, not the service) and writes
   that run log.
6. The validation gate you'll finish with: the full pytest run, a side-by-side
   reconcile against vol_report.py, and a cross-check of the run log against the
   database itself.
```

**Now the first real reading beat of the day. Read the plan like a reviewer:**

- Tests before code? With the **real** anchor numbers (cross-check 2–3 against
  the legacy output on your screen — agents *invent* plausible numbers; also use
  the integers the script **prints**, not SQLite `ROUND()` re-computations, which
  land a gallon off on some terminals)?
- Functions **return**? Physical keeps dyed diesel while taxable drops it?
  `net_gal` named, with the why? Month a **range**?
- The **log design** there — one file per run, diffable lines?

**Then approve — and let it go.** When the plan completes, Claude Code asks
whether to proceed: **say yes and watch.** It will write the failing tests, then
the service, run pytest, and iterate to green, asking for approval as it goes.
This is the loop running at its natural speed — your job is the approvals
(**Ctrl+E** anything you're unsure of) and watching for one thing: if it starts
writing `service.py` *before* the failing test run exists, stop it and point at
the plan.

**When it lands on green: read the tests** (5 quiet minutes). They are your spec,
executable — the contract fields, the invariants, the anchors. If a test asserts
something your spec didn't say, one of them is wrong. Fix that now.

---

## Step 5 — Validate: the tests, the log, and the database (8 min)

Green tests are necessary, not sufficient. Make the agent prove the run against
the **real artifacts**:

```
Run the CLI for 2025-08 so it writes a run log. Then validate, showing evidence
for each: (1) the full pytest output; (2) vol_report.py 2025-08 and your CLI
side by side — physical and taxable match to the gallon; (3) cross-check the run
log against the DATABASE: re-derive at least three terminals' physical and
taxable with direct SQL and show they equal the log's lines, and confirm the
log's row count matches a COUNT of qualifying (terminal, month) groups. Report
the evidence, then say done or not done.
```

That habit — **the agent proves "done" from the tests, the log, and the database
before it's allowed to say the word** — is the single most transferable thing in
this course.

```bash
# the 30-second proof it's a service, not a script:
python3 -c "import service; rows = service.monthly_volumes('2025-08'); print(rows[0]); print(len(rows), 'rows')"
# -> {'terminal': 'DAL', 'month': '2025-08', 'physical_gal': 1517103, 'taxable_gal': 1371642}
```

**If something doesn't match:** missing exclusion (`status = 8` / `mode = 8`),
`gross_gal` instead of `net_gal` (~1–1.5% high, *looks* fine), the dyed-diesel
asymmetry applied to both measures or neither — or, if you're off by exactly one
gallon somewhere, a rounding-method mismatch (sum raw in SQL, round in Python,
compare to what the legacy script *prints*).

---

## Step 6 — A change request lands (12 min)

It always does. The desk replies:

> *"This is great — can I also get how many tickets each number came from? Just a
> count per terminal."*

**First, log it where work lives — on the ticket:**

```
Add a comment to my service story's work item:
az boards work-item update --id <your-story-id> --discussion "Change request
from the desk: add lift_count (qualifying tickets per terminal-month) to the
output contract. Implementing tests-first; will verify existing numbers
unchanged by comparing run logs."
```

*(No DevOps? Note it at the top of stories.md and keep going.)*

**Then make the change — contract first, tests first:**

```
Change request: add lift_count (int — the number of qualifying tickets behind
each row's totals) to every returned row. This is a CONTRACT change, so do it
tests-first: update the contract test deliberately (the exact-fields assertion
must now include lift_count) and add one anchor for it, then implement, then run
to green. Then run the CLI again and COMPARE the new run log with the previous
run's log: show me that every existing physical and taxable value is identical
line by line, and that only lift_count is new. Report exactly what you compared.
```

Two things to notice while it works:

- **The contract test fails first.** That's the contract doing its job — you
  can't drift the row shape by accident; extending it is a *deliberate, visible*
  act. (Next week, anything consuming your service inherits this protection.)
- **The log comparison is the verification.** The new column is obvious; whether
  any of the 25 existing numbers moved is **not** eyeball-able. Two run logs and
  a diff settle it in one command. That's why services log.

**Checkpoint:** tests green again, the before/after log diff shows existing
numbers byte-identical, and the ticket carries the comment trail.

---

## Step 7 — Documentation, while it's true (8 min)

Docs written months later describe what someone *remembers*. Yours get written
now, by the agent, from the actual artifacts — and your job is to **read them**.

```
Write ARCHITECTURE.md for this folder, one page: the pieces and the data flow
(database -> service -> consumers: the CLI, the tests, next week's dashboard);
the output contract and where it's enforced (the tests); the run-log design and
what it's for; every load-bearing decision and its WHY (net_gal, the two
exclusions, the dyed-diesel asymmetry, lift_count, the rounding approach, the
sargable month range); and a short "what not to break" list for the next
engineer. Write it from the code and tests as they exist — not from intentions.
```

**Read it end to end** with one question: *would a new teammate, starting Monday,
get it?* If a decision's "why" is missing or wrong, have the agent fix it — wrong
docs are worse than none.

**Stretch — API-doc the code itself:** have the agent ensure every public
function has a real docstring (args, returns, the contract), then generate
HTML docs the way Python does it natively:

```bash
python3 -m pydoc -w service        # writes service.html — open it in a browser
```

*(Session 5 adds the other half: API documentation for the web endpoints.)*

---

## Step 8 — Ship it: commit + PR (8 min)

Your repo and branch have existed since Step 3 — now the work lands on them, as
a reviewable unit:

```
Ship today's work on our story branch:
1. Stage today's artifacts: the spec, stories.md, the skill, test_service.py,
   service.py, ARCHITECTURE.md — not venv/ or logs/.
2. DRAFT the commit message and SHOW IT TO ME for approval BEFORE running git
   commit: an imperative subject naming the story, and a body with the WHY (the
   decisions) and the EVIDENCE (tests green; reconciles 2025-08 to the gallon;
   change verified by run-log comparison).
3. After I approve the message: commit, and push the branch to the devops remote.
4. Draft PR.md: the pull-request description — title, summary of decisions, the
   evidence, and the work items it touches.
```

> **Why "show me the message first":** told simply to commit, the agent writes a
> perfectly reasonable message and runs the commit in one stroke — the message
> flashes by *inside* the approval prompt, where you'd need `Ctrl+E` to even see
> it. Asking for the draft first makes the review explicit. Read it the way the
> reviewer six months out will: does it say **why**, or just *what*?

**Stretch (DevOps working + time to spare):** open the real PR now and leave it
open — `az repos pr create --source-branch story/<id>-volume-service
--target-branch main --title "..." --description "$(cat PR.md)"
--work-items <id>`. **Don't complete it.** Session 5 starts with a clean-context
agent reviewing it, then the merge, then the ticket close.

> **Fallback (no DevOps):** the local branch + approved commit + PR.md is the
> complete deliverable; the push and PR happen at the top of Session 5.

---

## Sidebar — while the agent works: `/btw`, and make it explain (optional, any time)

**The keeping-up tool: `/btw`.** While the agent is mid-build, type
`/btw <question>` — *"what are you doing right now?"*, *"what does sargable
mean?"*, *"why did that test fail?"* — and a quick answer appears in a side
overlay **without touching the main task or the conversation history**. It sees
everything so far but can't run tools, so it's for *understanding* questions, not
new work. Dismiss with `Esc`. (It's the polite version of interrupting — use it
freely; that's what it's for.)

For anything deeper — or anything in the generated code you wouldn't want to
defend in review — turn the agent into the explainer (the Session 3 grounded
move, now on *your* code):

> Walk me through service.py top to bottom — what each function does and why
> it's shaped that way. Point at the lines as you go.

Not fluent in Python? Two prompts that work:

> Explain the Python features this file uses that a newcomer would stumble on —
> the dict comprehension, the context manager, f-strings, `if __name__ ==
> "__main__"` — each with the line it appears on.

> I know C# (or Java / SQL / JavaScript — yours). Explain this file by analogy:
> for each construct, show the equivalent I'd write in my language and what's
> different here.

Understanding the code you ship is not optional just because you didn't type it.

---

## How the session runs (two work blocks)

We talk through the first half of the deck, then **you work Steps 1–4 in one
block (~25–30 min)**. We reconvene for the second half of the deck, then **you
work Steps 5–8 (~25–30 min)**. Then the debrief conversation.

| Elapsed | What's happening |
|---:|---|
| 0–22 | Share-back, the loop, and the walkthrough of Steps 1–4 |
| ~22–50 | **Work block 1 — Steps 1–4:** spec + contract → skill → stories on the board, repo + branch → plan read, approved, and the build flowing (most of you land on green inside this block) |
| 50–62 | Reconvene: validate, the change request, docs, shipping |
| ~62–92 | **Work block 2 — Steps 5–8:** validation evidence → the change (log-vs-log diff, ticket comment) → ARCHITECTURE.md read → commit approved + pushed, PR.md |
| 92–105 | The conversation (how did that actually feel?) |
| 105–110 | Homework 3 |

**Pace markers inside the blocks:** block 1 — spec by ~32, skill by ~40, board +
branch by ~45, plan approved by ~50. Block 2 — validated by ~72, change landed by
~82, docs read by ~88, shipped by ~92.

**If you fall behind:** the slice that matters is *green, validated, committed*.
The change beat and docs can compress; anything unfinished is Session 5's warm-up
— by design.

---

## What you'll take from this

1. **Sharpen** the ask into a spec with a contract — before any code.
2. **Capture** the tribal knowledge as a skill the *agent* loads.
3. **Slice** into stories with checkable criteria — on the board, where work lives.
4. **Plan** with tests first; **read the plan**; then let the loop run at its
   own speed.
5. **Validate with evidence**: the tests, the run log, the database — the agent
   proves "done."
6. **Absorb a change** the safe way: contract-first, then *prove* nothing else
   moved by comparing run logs.
7. **Document while it's true**, and **ship a reviewable unit**.

Session 5 closes the loop: the clean-context review of your open PR, the merge,
the ticket moving to Closed — and the parallel agents building the dashboard
stories against your contract, loading your skill. **Homework 3** keeps you
moving: the dashboard skeleton on your service.
