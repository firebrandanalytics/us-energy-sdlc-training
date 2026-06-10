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
vague ask → user stories → spec + contract → capture knowledge (a skill)
        → tests FIRST → plan → build until green → validate (data + tests)
        → commit + PR  →  [Session 5: review by a clean-context agent,
                            merge, close the ticket, repeat in parallel]
```

**Session 4** runs the loop from the vague ask through a committed, PR-ready
service. **Session 5** finishes it the way real teams do: work items on an Azure
DevOps board, parallel agents each taking a story, an *unbiased* agent reviewing
each PR, merge, ticket closed. If we don't finish everything today, that's fine —
it rolls into Session 5's opening. The loop is the lesson.

> **Script vs. service — the one distinction the build turns on.** The legacy
> `vol_report.py` *prints* a report and exits; its numbers are trapped inside a
> `print()`. A service *returns* the numbers as data (`monthly_volumes("2025-08")`
> hands back a list of rows). Same query underneath — but a service is something
> you can call, test, and build a UI on.

---

## Environment

You will work in **`sessions/session-4/`** (this folder). From here, the committed
database is at **`../../data/us_energy.sqlite`** — that two-levels-up path is the
one to use everywhere in this lab.

### Set up

```bash
cd sessions/session-4
python3 -m venv venv
source venv/bin/activate            # Windows Git Bash: source venv/Scripts/activate
pip install pytest                  # required today — we write tests FIRST
```

(No other packages — `sqlite3` ships with Python. FastAPI comes in Homework 3.
If `python3` isn't found on your machine, use `py -3` or `python` — whichever
worked for you in Homework 2 — consistently throughout.)

> **One ground rule for the whole session:** until your Session 4 commit exists,
> **don't open or let the agent read anything under `sessions/session-5/`** —
> that's next week's folder, and peeking at it skips the only part that
> transfers.

### Confirm the database opens from here

```bash
python3 -c "import sqlite3; print(sqlite3.connect('../../data/us_energy.sqlite').execute('SELECT COUNT(*) FROM lifts').fetchone())"
# -> (50025,)
```

### See what you're replacing

> You created `data/vol_report.py` during Homework #2. If you skipped HW2, grab the
> listing from `homework/homework-2-brief.md` and save it to `data/vol_report.py`
> before running the command below.

```bash
# The legacy script hard-codes its DB name, so run it from inside data/:
( cd ../../data && python3 vol_report.py 2025-08 )
```

Keep that output handy — it's your reconciliation target, and your tests will
encode it.

---

## Step 1 — Sharpen the vague ask into a spec (20 min)

### The ask

This is what lands in your queue:

> "Hey — can you get me clean monthly volumes by terminal? The old
> `vol_report.py` sort of does it but I don't trust the numbers and nobody
> remembers how it works. I just want something I can pull each month and hand to
> the desk. Should be quick — the data's all there."

That's the entire ask. It sounds clear. It is not buildable. *Clean* how?
*Monthly* by which timestamp? *Volume* in which gallons — as-metered or
temperature-corrected? Does a voided ticket count? A non-physical book adjustment?
Tax-exempt dyed diesel? Every one of those is a decision that **changes the
number**, and if you don't make it, the agent will — silently, from a
training-data default — and hand you a confident, wrong answer that runs.

### Interrogate it first (~5 min)

Open Claude Code in this folder. Have it surface the decisions before you write
anything:

```
Read ../../data/vol_report.py, ../../data/DATA-DICTIONARY.md, and the schema of
../../data/us_energy.sqlite (run: .schema lifts). I have a vague request: "clean
monthly volumes by terminal." Before I write any spec or code, list every
decision this ask leaves implicit — the questions an engineer would have to
answer before the numbers are well-defined. Group them: grain, filters/
exclusions, units, edge cases. Do not propose a design yet.
```

Read its list. Add your own. Your Homework 2 dossier already holds most of the
answers — that's why we did it.

### Write the spec — and the output contract (~15 min)

Open **`handouts/D4-data-spec-template.md`** and fill it in. D4 forces the four
things that decide whether the numbers are right — **grain, filters/exclusions,
units, edge cases** — into the open. Use **C7** for the surrounding sections.
(D4 ends with a worked example — **draft your own answers from your dossier
first**, then compare. Copying the example skips the decision-making, which is
the exercise.)

Then add the section a one-off script wouldn't need but a *service* must have —
the **output contract** (the shape of one returned row; **D5** is the card):

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
> precisely, the ask is still vague. And if you can't say what one returned row
> looks like, you can't build the app on it — or write a test for it. The
> contract becomes your tests in Step 5, almost word for word.

---

## Step 2 — Capture what you know as a *skill* (13 min)

Your HW2 dossier decoded the codes, caught the lying comments, and found the bad
constant. Right now that knowledge lives in a document only *you* will read. Turn
it into a **skill** — a file the agent itself loads — and every future session
(yours, a teammate's, and the parallel agents in Session 5) starts already knowing
the rules.

A skill is a folder with a `SKILL.md` file: **YAML frontmatter** (a `name` and a
one-line `description` that tells the agent *when to use it*), then the knowledge
as plain markdown. Claude Code auto-discovers skills in your repo's
`.claude/skills/` folder.

**Prompt Claude Code:**

```
Create a skill at .claude/skills/us-energy-volume-rules/SKILL.md capturing the
verified rules of this dataset from my Homework 2 dossier, which I'll paste below.
Format: YAML frontmatter with `name: us-energy-volume-rules` and a one-line
`description` saying when to use it (computing, reviewing, or testing volume
numbers from the lifts table). Body: the meaning of each magic code and how each
measure treats it; which gallon column and why; the physical-vs-taxable
asymmetry; the RIN correction (what's wrong in the legacy script and where the
right values live); the reconciliation anchor numbers; and the query-hygiene
rules (sargable month filter, named constants). Keep it under a page — it's an
operating card for an agent, not an essay.

MY DOSSIER:
<paste the relevant parts of your HW2 dossier>
```

**Review it like a PR.** The two failure modes: it parrots a *comment* instead of
the verified behavior (your dossier is the truth — check against it), and it's too
long (an agent skims; a page beats five). One thing to add if the agent doesn't:
`mode = 8`'s meaning wasn't derivable from the data — Session 3's open question.
**Treat it as confirmed now** (the feed owner says: book adjustment, non-physical)
and record it that way — *flag the unknown, get it confirmed by a human, then
write down the confirmed fact*. That's the normal arc for tribal knowledge.

**Prove it loads — with specifics, not vibes.** Start a fresh Claude Code session
at the repo root and ask:

> Read only `.claude/skills/us-energy-volume-rules/SKILL.md`. Summarize the
> monthly volume rules from that skill — including the exact status / mode /
> prod_cd codes and which measures exclude each. If you can't name all three
> codes and their scope, say the skill didn't load.

The bar: it names **status 8 and mode 8 (excluded from every measure)** and
**prod_cd 6 (excluded from taxable only)** — facts that live in your skill's
*body*, not its description, so a generic answer can't fake it. That fresh-session
test is exactly why this matters: **in Session 5, agents that have never seen your
dossier will build on these rules.**

> If your HW2 dossier is thin, run the extraction first and feed *that* to the
> skill prompt: *"Read ../../data/vol_report.py. Treat the code's behavior as
> truth and the comments as suspect. For each output it computes, give me the real
> rules — filters, gallon column, constants — verified against
> ../../data/us_energy.sqlite, flagging every place a comment lies."*

---

## Step 3 — User stories (7 min)

A spec says what *right* means; **stories** slice it into shippable, checkable
pieces of *work*. In Session 5 these become Azure DevOps work items — one parallel
agent per story. Today the agent drafts them and you edit.

**Prompt Claude Code:**

```
From the spec below, draft user stories as stories.md in this folder. Slice them
so each is independently shippable and testable: (1) the volumes service
(monthly_volumes + months, honoring the output contract), (2) a thin reconcile
CLI that calls the service, (3) [stretch] a corrected RIN measure from the
rin_transactions ledger, and (4) one story per Session-5 dashboard extension
(month filter, chart, terminal detail, JSON API) — short, we build those next
week. Each story: "As <who> I want <what> so that <why>" plus 3-5 acceptance
criteria that are CHECKABLE — a test that can pass or a query that can prove it,
not vibes. The service story's criteria must include: returns (not prints),
reconciles to vol_report.py 2025-08 to the gallon, the invariants hold, and unit
tests written before the implementation pass.

THE SPEC:
<paste your spec>
```

**Edit pass (2 min):** delete any acceptance criterion you couldn't check
mechanically. "Works correctly" is not a criterion; "DAL 2025-08 physical =
1,517,103" is.

> **Already have Azure DevOps handy?** (USV folks: you live there.) A stretch for
> later — these stories become work items with
> `az boards work-item create --type "User Story" --title "..."`. We do it
> properly, board and all, in Session 5; `stories.md` is today's deliverable.

---

## Step 4 — Plan before building (10 min)

Switch Claude Code into planning mode so it can't start editing:

```bash
claude --permission-mode plan
```

(Or open normally and `Shift+Tab` into plan mode.)

Hand it everything — and require a **tests-first** sequence:

```
I'm building story 1 from stories.md: a clean volumes service in this folder — a
SERVICE, not a script: it must RETURN data (a web app calls it next week), not
print it. You have the spec, the stories, and the skill (load
us-energy-volume-rules). Plan the implementation. The plan must:

1. Sequence TESTS FIRST: test_service.py is written and failing BEFORE service.py
   exists. Tests must encode the output contract (field names and types), the
   invariants (physical >= taxable >= 0; one row per terminal-month), and the
   reconciliation anchor (the exact 2025-08 numbers from vol_report.py).
2. Name the functions — at least monthly_volumes(month) and months() — and
   exactly what each RETURNS (a list of dicts in the contract shape).
3. Give the exact SQL for physical and taxable, naming every filter and the
   gallon column — and bound the month with a RANGE on lift_ts (sargable), never
   substr()/strftime() wrapped around the column.
4. Include a thin CLI entry point that CALLS the service (a consumer, not the
   service) so I can reconcile from the terminal.
5. End with the validation gate: what you will run (pytest, the reconcile, which
   DB checks) before declaring it done.

Do not write any code yet. Wait for my approval.
```

**Read the plan. Push back.** Be especially picky about:

- **Tests before code.** If the plan writes `service.py` first "to know what to
  test," that's backwards — the contract and the legacy numbers already define the
  tests. Send it back.
- **Return, don't print.** If `monthly_volumes()` prints a table, it's a script in
  disguise.
- **The exclusions.** Physical keeps dyed diesel; taxable drops it. One filter set
  for "the volume" is *the* classic miss.
- **net vs gross.** The plan should name `net_gal` and say why.
- **The month boundary.** A half-open range (`lift_ts >= '2025-08-01' AND
  lift_ts < '2025-09-01'`). A function wrapped around the column defeats any index
  — Session 3's lesson.

Approve only when the plan is concrete enough that you'd trust the build.

---

## Step 5 — Tests first, then build until green (35 min)

### 5a. Red: write the tests (~10 min)

> **STOP — get the real anchors first.** Run
> `( cd ../../data && python3 vol_report.py 2025-08 )` **now** and keep that exact
> output in front of you. The test prompt below has the agent copy those values
> in — if you skip the run, the agent will *invent* plausible numbers, and every
> step after that converges on a confidently wrong answer. (And use the integers
> the script **prints** — don't recompute anchors with SQLite's `ROUND()`, which
> rounds differently and lands one gallon off on some terminals.)

Exit plan mode and have it write **only** the tests:

```
Write test_service.py per the approved plan — BEFORE service.py exists. Encode:
the contract (monthly_volumes('2025-08') returns a non-empty list of dicts with
exactly the fields terminal, month, physical_gal, taxable_gal; gallons are ints);
the reconciliation anchor (assert the exact top numbers from
"cd ../../data && python3 vol_report.py 2025-08" — run it and copy the real
values in); the invariants (physical >= taxable >= 0 on every row; no duplicate
(terminal, month)); and months() returning sorted "YYYY-MM" strings. Then run
pytest and show me the output — every test should FAIL with an import error,
because service.py doesn't exist yet. That's correct.
```

**Read the tests before you bless them** — they are the spec, executable. Is the
anchor the *real* legacy number? Do the invariants match your contract? A wrong
test is worse than no test: the build will faithfully converge on the wrong
answer.

### 5b. Green: build the service (~20 min)

```
Now implement service.py per the plan. Requirements: monthly_volumes(month=None)
and months() RETURN data honoring the contract; named constants for the magic
values (no bare 6 / 8 in the SQL); a sargable month range; a thin
__main__ CLI that calls the service. Work in this folder only — do NOT read or
copy from sessions/session-5/ (next week's folder). After each change run pytest;
you're done only when every test passes. Then show me the green run and the
2025-08 CLI output.
```

Approve actions as they come up — **`Ctrl+E` on anything you're not sure about**
(Session 2 muscle). The loop you want to see: *test → fail → fix → re-run* until
green. If the agent declares success without showing a green pytest run, that's
the catch: *"show me the test output."*

### 5c. The done-gate: validate against the data (~5 min)

Green tests are necessary, not sufficient — make the agent prove it against the
**database and the legacy output**, not just its own tests:

```
Before we call this done, validate it: (1) run the full pytest suite and show the
output; (2) run "cd ../../data && python3 vol_report.py 2025-08" and your CLI
side by side and confirm physical + taxable match to the gallon for the top
terminals; (3) run one direct DB check of your choice that could catch a wrong
filter (e.g. a COUNT of excluded rows) and explain what it proves. Report the
evidence, then say done or not done.
```

That habit — **the agent shows evidence from the real artifacts before claiming
done** — is the single most transferable thing in this lab.

```bash
# the 30-second proof it's a service, not a script:
python3 -c "import service; rows = service.monthly_volumes('2025-08'); print(rows[0]); print(len(rows), 'rows')"
# -> {'terminal': 'DAL', 'month': '2025-08', 'physical_gal': 1517103, 'taxable_gal': 1371642}
```

### When it doesn't match

That's normal and it's the work. Read the disagreement with Claude Code:

- **Physical off:** usually a missing exclusion (`status = 8` or `mode = 8`), or
  `gross_gal` instead of `net_gal` (~1–1.5% high and *looks* fine).
- **Taxable off:** the dyed-diesel asymmetry — dropped from both measures, or
  neither.
- **Off by exactly one gallon on a terminal or two:** a rounding-method mismatch —
  SQLite's `ROUND()` rounds half away from zero; the legacy script accumulates
  floats and rounds in Python. Sum raw in SQL, round in Python, and compare to the
  numbers the legacy script *prints*.
- **Slow query:** `EXPLAIN QUERY PLAN`; if it shows `SCAN lifts`, the month filter
  is probably wrapped in a function — rewrite to the range, and use an index on
  the timestamp in *your* copy: `CREATE INDEX idx_lifts_ts ON lifts(lift_ts);`
  (you likely created exactly this one in Session 3's lab — it's still there) →
  the plan should flip to `SEARCH lifts USING INDEX idx_lifts_ts`.

### Stretch (only if you're green and reconciled)

- **The corrected RIN measure** (story 3): the legacy script multiplies renewable
  gallons by a flat constant — your HW2 dossier knows why that's wrong and where
  the real per-product values live (`rin_transactions`). Build the measure from
  the **ledger**. Your number **should not match** the legacy print — expect
  roughly 2% higher — and your story's acceptance criterion is documenting *why
  yours is right*. (We compare exact numbers in the wrap.)
- **Taste the app a day early:** a five-line script that imports your service and
  prints an HTML `<table>` of one month — proof the service is consumable by a UI,
  which is exactly what Homework 3 turns into a real page.

---

## Step 6 — Ship it: commit + PR (10 min)

Real work ends in a reviewable unit, not a folder of files. The agent writes the
commit and the PR description; you review both like everything else.

```
Stage and commit today's work in this repo on a new branch s4/<your-initials>:
the spec, stories.md, the skill, test_service.py, and service.py. Write the
commit message(s) yourself: a one-line subject in imperative mood naming the
story it implements, and a body that says WHY (the decisions: net_gal, the
exclusions, the asymmetry) and the EVIDENCE (tests green; reconciles to legacy
2025-08 to the gallon). Don't push — there's no remote for this yet. Then draft
PR.md in this folder: the pull-request description for this change — title,
summary of decisions, test evidence, and which story it closes.
```

Read the commit message the way a reviewer six months from now will. Does it say
*why*, or just *what*? Does the PR description give a reviewer everything needed
to judge it — including the test evidence?

> **Where this goes:** in Session 5 this branch becomes a real **Azure DevOps pull
> request** — pushed to a repo, reviewed by a **clean-context agent** (one that
> didn't write the code and has no stake in liking it), merged, and the work item
> **closed**. Today's commit is the input to that pipeline. If you already have
> `az devops` set up and time to spare: `az repos pr create` is the move — but
> don't burn lab time on auth; Session 5 starts there.

---

## Pacing (elapsed from the start of the session)

The first ~13 minutes are the HW2 share-back and the framing — the lab starts
after that.

| Elapsed | Where you should be |
|---:|---|
| 33 min | Spec drafted — sharp on grain, units, exclusions, and the contract |
| 46 min | Skill written, reviewed, and loading in a fresh session |
| 53 min | stories.md drafted with checkable acceptance criteria |
| 63 min | Plan approved (tests-first sequence) |
| 73 min | Tests written and **failing** (red) |
| 98 min | Tests **green**; physical + taxable reconcile; done-gate evidence shown |
| 108 min | Committed on `s4/<initials>` with a real message; PR.md drafted |

**If you fall behind:** a green, reconciled service with its tests and a real
commit is a complete slice — the skill and stories can be finished async, and
anything unfinished is Session 5's warm-up. If you only get to *red* tests today,
even that is a win: the build-to-green is a clean place to resume.

---

## What you'll take from this

The loop you just ran is the real workflow, whatever the deliverable:

1. **Sharpen** the ask into a spec with a contract — before any code.
2. **Capture** the tribal knowledge as a skill the *agent* can load — not a doc
   only humans read.
3. **Slice** it into stories with checkable acceptance criteria.
4. **Plan** with everything in context; tests sequenced first; review before
   building.
5. **Red → green**: the agent builds until *your* tests pass, then **proves it
   against the data** before claiming done.
6. **Ship** a reviewable unit: a branch, a commit that says why, a PR description
   with evidence.

Session 5 closes the loop: the board, the parallel agents (each loading your
skill, each building against your contract), the unbiased review, the merge, the
closed ticket. **Homework 3** keeps you moving — the dashboard skeleton on your
service.
