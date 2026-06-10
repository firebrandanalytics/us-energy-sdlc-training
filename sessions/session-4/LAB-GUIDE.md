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
        → documentation → ship: commit, push, PR
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

## Environment — your own repo, next to the course repo

Today you build in **your own repository**, not inside the course repo. Two git
repos, side by side — never one inside the other:

```
<some folder>/
  us-energy-sdlc-training/        ← the course repo (READ-ONLY reference today)
  <initials>-volume-service/      ← YOUR repo — everything you build lives here
```

You'll **start Claude Code inside your repo**. It can still *read* the course
repo next door (approve the read when it asks — that's our data); it *writes*
only in yours.

### Set up (the az pieces were the pre-session email)

```bash
# 0) DevOps plumbing (from the email — one minute if already done):
az extension add --name azure-devops
az login
az devops configure --defaults organization=https://dev.azure.com/<your-org> project=<your-project>

# 1) Go to the PARENT folder — the one the course clone sits INSIDE.
#    Most terminals open inside the course repo, so usually this is just:
cd ..
ls
#    ^ you should SEE "us-energy-sdlc-training" in that listing. If you don't,
#      you're in the wrong place — never run the clone from inside the course
#      repo, or you'll nest one repo inside another.

# 2) Create YOUR repo in Azure DevOps, and clone it HERE — beside the course clone:
az repos create --name <initials>-volume-service --query "remoteUrl" -o tsv
git clone <the URL it printed>            # "cloned an empty repository" = correct
cd <initials>-volume-service
git branch -M main                        # guard: some gits default to "master" — we use main

# 3) pytest (the one package today — install it once, no venv needed):
python3 -m pip install pytest
#    (if pip says "externally-managed-environment", add: --user --break-system-packages)

# 4) Start Claude Code HERE (in your repo):
claude
```

(If `python3` isn't found, use `py -3` or `python` — whichever worked for you in
Homework 2 — consistently throughout.)

> **If DevOps fights you** (permissions, tenant policy, anything): **don't burn
> lab time on it.** The fallback is one command from the same parent folder —
> `mkdir <initials>-volume-service && cd <initials>-volume-service && git init -b main`
> — a plain local repo (it's *outside* the course repo, so `git init` is fine
> here). Everything below works identically except the pushes; we sort DevOps
> access before Session 5.

### Confirm the database and the legacy script (from inside your repo)

```bash
python3 -c "import sqlite3; print(sqlite3.connect('../us-energy-sdlc-training/data/us_energy.sqlite').execute('SELECT COUNT(*) FROM lifts').fetchone())"
# -> (50025,)
( cd ../us-energy-sdlc-training/data && python3 vol_report.py 2025-08 )
# (you created vol_report.py in HW2; the listing is in the course repo's homework/homework-2-brief.md if missing)
```

**Keep that legacy output on screen** — it is your reconciliation anchor all
session, and you'll check the agent's tests against it.

> **Ground rule: the course repo is read-only reference today.** The only
> course-repo path the agent may read is
> **`../us-energy-sdlc-training/data/`** (the database, the dictionary,
> `vol_report.py`) — never `../us-energy-sdlc-training/sessions/session-5/`
> (next week's folder; peeking at it skips the only part that transfers).

---

## Step 1 — The spec, drafted from your dossier (~4 min)

### The ask

> "Hey — can you get me clean monthly volumes by terminal? The old
> `vol_report.py` sort of does it but I don't trust the numbers and nobody
> remembers how it works. I just want something I can pull each month and hand to
> the desk. Should be quick — the data's all there."

It sounds clear. It is not buildable. *Clean* how? Which gallons? Does a voided
ticket count? A book adjustment? Tax-exempt dyed diesel? Every one of those is a
decision that **changes the number** — and what you don't decide, the agent
decides for you.

**Here's the thing: you already made these decisions — in Homework 2.** That was
the point of the dossier. So don't hand-craft a spec; have the agent assemble it
*from* your decisions, and spend your minutes **checking** it:

```
Here is my Homework 2 intent dossier for the legacy script (it lives in the course repo at ../us-energy-sdlc-training/data/vol_report.py):
<paste the relevant parts>

Draft SPEC.md in this folder from it, using the D4 shape — grain, filters/
exclusions (per measure), units, edge cases — plus an OUTPUT CONTRACT section:
the exact shape of one returned row (terminal str, month "YYYY-MM",
physical_gal int, taxable_gal int) and the invariants a caller can rely on
(physical_gal >= taxable_gal >= 0; exactly one row per terminal-month). Take
every decision from my dossier — but VERIFY each one against the database as
you go: where my dossier disagrees with the data, flag the disagreement instead
of copying it, and FLAG anything my dossier doesn't settle rather than deciding
it yourself.
```

**Your read (2 minutes, four checks):** `net_gal` with the why · the two
exclusions on *both* measures · dyed diesel **kept in physical, dropped from
taxable** · the contract row shape (it becomes your tests, almost word for word).

If a check fails, **your dossier was wrong there** — that's fine and it's why we
verify: the share-back just gave you the right answers, so fix the spec now and
move. (Dossiers vary; the data doesn't.) Don't polish. Move.

---

## Step 2 — Capture what you know as a *skill* (~6 min)

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
constants). Verify every rule against the database before writing it down — the
skill must carry what the DATA says, not what my dossier or any comment claims.

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

## Step 3 — Stories on the board · foundation on main · your branch (~10 min)

A spec says what *right* means; **stories** slice it into shippable, checkable
work — and today they go on the **real Azure DevOps board**, because that's
where work lives at U.S. Energy. Then everything so far lands on `main` as the
**foundation commit**, and the build gets its **story branch** — all before any
code exists, because that's the order real work happens in.

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
doesn't have "User Story", use --type Issue. DevOps renders descriptions as
HTML — use <br/> for line breaks so the board stays readable.) Then list the
created IDs and put each ID back into stories.md next to its story.
```

Note your **service story's work-item ID** — a change request is going to land on
it later, and Session 5 closes it.

**Now the foundation commit and the branch.** (One GitHub habit to unlearn: in
Azure DevOps, work items don't live *inside* a repo the way GitHub issues do —
they live at the **project** level, and get tied to your repo through **branch
and pull-request links**. The branch you're about to make, named for your story,
is half of that linkage; Session 5's PR is the other half.)

```
Lay the project foundation on main, then cut the story branch:
1. Write README.md for this repo: what the volumes service is, plus a short
   "working with Azure DevOps from the CLI" section — install the extension
   (az extension add --name azure-devops), az login, az devops configure
   --defaults — so a teammate can clone and work the board.
2. Write a .gitignore: venv/, __pycache__/, logs/, .env, *.sqlite.
3. Commit everything so far on main — README, .gitignore, SPEC.md, stories.md,
   and the .claude/skills folder — with a sensible message, and push main.
4. Create and switch to branch story/<my-service-story-ID>-volume-service and
   push it. The build happens there.
```

> **Why this shape:** `main` carries the project's scaffolding and knowledge;
> the **story branch** carries the change. When Session 5's PR merges the branch,
> the diff *is* the story — nothing more, nothing less. (And your repo stays a
> **sibling** of the course repo — if a `.git` ever shows up nested inside
> another repo, something ran `git init` in the wrong place: delete the inner
> `.git` only and re-stage.)

> **Fallback (no DevOps yet):** `stories.md` *is* the stories artifact, and
> `git switch -c story/volume-service` gives you the same branch locally — the
> remote arrives in Session 5. Nothing else changes. Keep moving.

---

## Step 4 — Plan it, read the plan, approve — and let it run (~15 min, green included)

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
   "cd ../us-energy-sdlc-training/data && python3 vol_report.py 2025-08", not from memory.
2. The functions — monthly_volumes(month=None) (one month, or every month when
   omitted) and months() — and exactly what each RETURNS (list of dicts in the
   contract shape).
3. The exact SQL for physical and taxable: every filter named, the gallon column
   named, the month bounded by a RANGE on lift_ts (never substr/strftime around
   the column).
3b. The DB path is CONFIGURABLE, not hard-coded: read it from a DB_PATH
   environment variable, defaulting to
   ../us-energy-sdlc-training/data/us_energy.sqlite (the course repo sits next
   to this one). Next week this service runs from a different folder — the env
   var is what makes that a non-event.
4. LOGGING: every run writes a separate log file (logs/run-<timestamp>.log —
   timestamp precise enough that two runs in the same second never collide) with
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

> **If it stalls** (stops after the tests, or asks what to do next), paste this
> and it keeps moving:
> *"Continue from the approved plan. Run the failing tests if they haven't run,
> then implement service.py, run pytest, and iterate until green. Ask me only
> for permissions, or if the evidence contradicts the spec."*

**When it lands on green: read the tests** (5 quiet minutes). They are your spec,
executable — the contract fields, the invariants, the anchors. If a test asserts
something your spec didn't say, one of them is wrong. Fix that now.

---

## Step 5 — Validate: the tests, the log, and the database (~10 min)

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
this course. (And note the run-log filename this step printed — Step 6 diffs
against it as the "before".)

```bash
# the 30-second proof it's a service, not a script (ordering-agnostic — pick DAL out):
python3 -c "import service; rows = service.monthly_volumes('2025-08'); print([r for r in rows if r['terminal']=='DAL'][0]); print(len(rows), 'rows')"
# -> {'terminal': 'DAL', 'month': '2025-08', 'physical_gal': 1517103, 'taxable_gal': 1371642}
```

**If something doesn't match:** missing exclusion (`status = 8` / `mode = 8`),
`gross_gal` instead of `net_gal` (~1–1.5% high, *looks* fine), the dyed-diesel
asymmetry applied to both measures or neither — or, if you're off by exactly one
gallon somewhere, a rounding-method mismatch (sum raw in SQL, round in Python,
compare to what the legacy script *prints*).

---

## Step 6 — A change request lands (~10 min)

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
each row's totals; count the PHYSICAL qualifying set, i.e. dyed-diesel tickets
still count — they're real tickets, just tax-exempt) to every returned row. This is a CONTRACT change, so do it
tests-first: update the contract test deliberately (the exact-fields assertion
must now include lift_count) and add one anchor for it, then implement, then run
to green. Then run the CLI again and COMPARE the new run log with the previous
run's log: show me that every existing physical and taxable value is identical
line by line, and that only lift_count is new. Report exactly what you compared.
```

**The check you can run yourself** (the new field makes every row line differ,
so normalize it away before diffing — existing values must be byte-identical):

```bash
diff <(grep '^row ' logs/<old-run>.log) \
     <(grep '^row ' logs/<new-run>.log | sed -E 's/ lift_count=[0-9]+//')
# no output = nothing moved; then eyeball the new field separately
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

## Step 7 — Documentation, while it's true (~10 min)

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

## Step 8 — Ship it: commit + PR (~10 min)

Your repo and branch have existed since Step 3 — now the work lands on them, as
a reviewable unit:

```
Ship today's work on our story branch:
1. Stage today's artifacts: the spec, stories.md, the skill, PLAN.md,
   test_service.py, service.py, your CLI if it's a separate file, and
   ARCHITECTURE.md — not logs/ (it's in .gitignore).
2. DRAFT the commit message and SHOW IT TO ME for approval BEFORE running git
   commit: an imperative subject naming the story, and a body with the WHY (the
   decisions) and the EVIDENCE (tests green; reconciles 2025-08 to the gallon;
   change verified by run-log comparison).
3. After I approve the message: commit, and push the branch (origin is your repo).
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

The agent's work in every step takes a minute or two — the step budgets below are
mostly **your reading time**. Move briskly: your dossier already made the hard
decisions.

| Elapsed | What's happening |
|---:|---|
| 0–15 | Share-back + the walkthrough of Steps 1–4 |
| **15–55** | **Work block 1 — Steps 1–4** (~40 min): spec from your dossier (~4) → the skill (~6) → stories + board + foundation commit + branch (~10) → plan: read, push back, approve, let it run to green (~15) |
| 55–60 | **Break** (5 min) |
| 60–65 | Walkthrough of Steps 5–8 |
| **65–105** | **Work block 2 — Steps 5–8** (~10 min each): validate (tests + log ↔ DB) → the change request (ticket comment, log-vs-log diff) → ARCHITECTURE.md read → ship (approved commit, push, PR.md) |
| 105–115 | The conversation (how did that actually feel?) |
| 115–120 | Homework 3 |

**Pace markers, block 1:** spec + skill done by ~25 · board + foundation + branch by
~35 · plan approved and flowing by ~45 · green by ~55. **Block 2:** validated by
~75 · change landed by ~85 · docs read by ~95 · shipped by ~105.

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
