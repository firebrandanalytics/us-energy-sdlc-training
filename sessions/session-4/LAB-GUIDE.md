# Lab Guide: From Vague Ask to Working Pipeline — Session 4

U.S. Energy AI Software-Development Training · Session 4 (120 min)

This is your reference for the session. The instructor walks the room through each
step live; this guide is here so you can keep moving if you fall behind, or pick
up from any step if you arrived late.

This is **Exercise 2, part 1**. You start a clean pipeline here and finish it with
parallel agents in Session 5.

---

## What you're building

A clean, documented replacement for the legacy `data/vol_report.py`: a Python
**pipeline** that produces **monthly volumes by terminal** from the course
dataset — physical volume, taxable volume, and (if you get that far) RIN credit
gallons. By the end of the session you should have a sharpened spec and a running
pipeline that gets at least **physical volume** right, reconciled against the
legacy numbers for a known month.

You'll do it in five moves:

1. **Sharpen the ask** (~25 min) — turn a vague request into a data spec using the
   D4 template: grain, filters, units, edge cases.
2. **Extract the real rules** (~20 min) — direct the agent to lift the true logic
   out of `vol_report.py` and the schema, distrusting the comments.
3. **Plan** (~15 min) — hand the spec + extracted rules to planning mode; review
   and approve.
4. **Build** (~45 min) — start `pipeline.py`; you direct, the agent executes.
5. **Review and reconcile** (~10 min) — check the output against the spec and the
   legacy numbers.

Final ~5 min is debrief and the handoff to Session 5.

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
# No third-party packages are required — sqlite3 ships with Python.
# If you prefer pandas/pytest, install them now:
pip install pytest                  # optional; used for the reconciliation test
```

### Confirm the database opens from here

```bash
python3 -c "import sqlite3; print(sqlite3.connect('../../data/us_energy.sqlite').execute('SELECT COUNT(*) FROM lifts').fetchone())"
# -> (50025,)
```

### See what you're replacing

```bash
# The legacy script hard-codes its DB name, so run it from inside data/:
( cd ../../data && python3 vol_report.py 2025-08 )
```

Keep that output handy — it's your reconciliation target for the build step.

---

## Step 1 — Sharpen the vague ask into a data spec (25 min)

### The ask

This is what lands in your queue:

> "Hey — can you get me clean monthly volumes by terminal? The old
> `vol_report.py` sort of does it but I don't trust the numbers and nobody
> remembers how it works. I just want something I can pull each month and hand to
> the desk. Should be quick — the data's all there."

That's the entire ask. It sounds clear. It is not buildable. *Clean* how?
*Monthly* by which timestamp? *Volume* in which gallons — as-metered or
temperature-corrected? Does a voided ticket count? Does a non-physical book
adjustment count? Does tax-exempt dyed diesel count? Every one of those is a
decision that **changes the number**, and if you don't make it, the agent will —
silently, from a training-data default — and hand you a confident, wrong answer
that runs.

### Interrogate it first (~7 min)

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

Read its list. Add your own. The decisions you will almost certainly have to make:

- **Grain** — one row per terminal per *what*? Calendar month, presumably — by
  which timestamp column?
- **Units** — `gross_gal` or `net_gal`? They are different numbers. Which is
  "the volume"?
- **Exclusions** — which `status` values are real? Which `mode` values are real
  movements? Is there a product that's physically real but shouldn't be taxed?
- **Edge cases** — a terminal with no movements in a month: omit, or emit 0? A
  month with a weird spike of voids?
- **Output shape** — a printed top-N summary, a full CSV, a function returning a
  table?

> **Watch out:** the dictionary and `code_ref` are deliberately incomplete and a
> little stale. Do **not** treat them as the answer. When the agent cites a code
> meaning, ask it to confirm against the data (`SELECT DISTINCT status FROM
> lifts;` and friends). This is the Session 3 muscle.

### Write the spec (~15 min)

Open **`handouts/D4-data-spec-template.md`** and fill it in. D4 is built for
exactly this: it forces the four things that decide whether the numbers are right
— **grain, filters/exclusions, units, edge cases** — into the open. Use
**C7** for the surrounding sections (constraints, anti-goals, acceptance
criteria, files-to-read).

At minimum your spec must pin:

- **Deliverable** — one or two sentences. The output shape (CSV? function? table?).
- **Grain** — "one row per terminal per calendar month," and the measures per row.
- **Measures + Units** — name the exact column. `SUM(net_gal)`, not "sum the
  gallons." State *why* net, not gross.
- **Filters / Exclusions** — every dropped row, **with its intent**, and **which
  measure it applies to**. (Hint from your Homework 2 dossier: the legacy script
  drops some rows from physical and *additional* rows from taxable. Those are not
  the same set.)
- **Time handling** — how a month is defined, and the boundary rule.
- **Edge cases** — the empty terminal-month; an abnormal void cluster.
- **Acceptance criteria** — at least five pass/fail statements.
- **Reconciliation** — what you check against, and how you treat differences.

> **The discipline:** if you can't fill in **Grain** and **Filters / Exclusions**
> precisely, the ask is still vague. Sharpen those two first; the rest follows.

You don't need a perfect spec to move on — but it must be sharp on grain, units,
and the exclusion asymmetry, because those are what the agent will otherwise get
wrong.

---

## Step 2 — Extract the real rules from the legacy code (20 min)

The legacy `vol_report.py` is the closest thing to a spec that exists today — but
its comments lie (you saw this in Homework 2). Your job now is to direct the agent
to extract what the code **actually does**, treating behavior as truth and the
comments as suspect.

Open Claude Code in this folder and run:

```
Read ../../data/vol_report.py carefully. Treat the CODE'S BEHAVIOR as the source
of truth and the COMMENTS as possibly stale or wrong — flag any comment that
disagrees with what the code does. Produce a short "rules" document capturing,
for each output the script computes (physical, taxable, RIN-eligible):

- exactly which rows it includes and excludes, by column and value;
- which gallon column it sums, and whether any scaling is applied;
- any constant it uses, and whether that constant matches what the data implies;
- the REAL intent behind each filter (not the comment's stated reason).

Verify your claims against ../../data/us_energy.sqlite where you can (e.g. does
the value the comment names actually appear in the data?). List every place the
comment and the behavior diverge.
```

What a good extraction surfaces (push the agent if it misses these):

- The void filter drops `status = 8` — even though a comment says `9`, and `9`
  never appears in the data. (`SELECT COUNT(*) FROM lifts WHERE status = 9;` → 0.)
- The "barge" exclusion actually drops `mode = 8` — which is a **book adjustment**,
  not barge. Barge is `mode = 4`, and it's kept.
- A "scale up, stored in hundreds" comment that the code **does not** act on —
  gallons are summed as-is.
- The taxable rollup drops `prod_cd = 6` (dyed off-road diesel) **but keeps
  everything else** — despite a "clear diesel only" comment. So physical and
  taxable share two exclusions but **diverge** on dyed diesel.
- A RIN factor (`RVO = 1.6`) applied flat to both renewable products — which does
  **not** match what the data implies. Hold that thought for the build.

Fold the confirmed rules into your spec's **Filters / Exclusions** and
**Reconciliation** sections. You now have a spec grounded in real behavior, not
in lying comments.

> **Why this matters:** you are not copying the legacy script. You are recovering
> the *correct* rules it encodes, separating them from the rot, so your clean
> pipeline can keep what's right and fix what's wrong.

---

## Step 3 — Plan before building (15 min)

Switch Claude Code into planning mode so it can't start editing:

```bash
claude --permission-mode plan
```

(Or open normally and `Shift+Tab` into plan mode.)

Hand it both artifacts — your spec and your extracted rules:

```
I'm building a clean replacement for ../../data/vol_report.py as a new pipeline.py
in this folder. Below are TWO artifacts; read both before planning.

ARTIFACT 1 — the data spec (what to compute and the exact rules):
<paste your sharpened spec here>

ARTIFACT 2 — the rules extracted from the legacy script (what today's code really
does, and where its comments lie):
<paste your extracted rules here>

Plan the implementation of pipeline.py. The plan must include:
1. The functions/structure you'll create and what each does.
2. The exact SQL (or query logic) for physical and taxable volume, naming every
   filter and the gallon column, and how a month is bounded.
3. How you'll define a month so an index could be used (a range predicate, not
   substr on the timestamp).
4. How the output is shaped (CSV and/or printed summary).
5. How you'll reconcile the result against vol_report.py, and where you EXPECT to
   differ on purpose.

Do not write any code yet. Wait for my approval.
```

**Read the plan. Push back.** Be especially picky about:

- **The exclusions.** Does physical keep dyed diesel and taxable drop it? If the
  plan applies one filter set to "the volume," that's the bug — call it out.
- **net vs gross.** The plan should name `net_gal` explicitly and say why.
- **The month boundary.** A range predicate (`>= '2025-08-01' AND < '2025-09-01'`)
  is sargable; `substr(lift_ts,1,7) = '2025-08'` is not and forces a full scan.
  (Session 3's query-plan lesson, paid off here.)

Approve only when the plan is concrete enough that you'd trust the build.

---

## Step 4 — Build `pipeline.py` (45 min)

Same session, plan in context. Let the agent build:

```
Implement the plan as pipeline.py in this folder. Read the DB at
../../data/us_energy.sqlite. Use named constants for the magic values (no bare
6 / 8 in the SQL — name them: status void, book-adjustment mode, dyed-diesel
product). Write a function I can call per month and one that does all months,
and a way to print a top-terminals summary and/or write a CSV. After it runs,
show me the 2025-08 output so I can reconcile it.
```

Approve actions as they come up. **`Ctrl+E` on anything you're not sure about** —
see the action before approving (Session 2 muscle). Auto-accept the obvious ones.

### Run it

```bash
python3 pipeline.py --month 2025-08      # or whatever interface your plan chose
```

### When it doesn't match

That's normal and it's the work. Read the disagreement with Claude Code:

- If **physical** is off: usually a missing exclusion (`status = 8` or
  `mode = 8`), or `gross_gal` instead of `net_gal`.
- If **taxable** is off: usually the dyed-diesel asymmetry — either dropped from
  both measures or dropped from neither.
- If a query is **slow**: check the plan with `EXPLAIN QUERY PLAN`; rewrite a
  `substr(...)` month filter as a range, and add an index in *your* copy:
  `CREATE INDEX ix_lifts_term_ts ON lifts(term_id, lift_ts);` then re-check —
  `SCAN` should become `SEARCH ... USING INDEX`.

### Stretch (only if physical + taxable reconcile and you have time)

Add the **RIN credit gallons** measure. Here the legacy script is *wrong* on
purpose: it multiplies every renewable gallon by a flat `RVO = 1.6`. The real
per-product equivalence is already carried in the `rin_transactions` ledger
(`rin_qty`). Pull RIN gallons from that table for non-void lifts in the month
rather than re-multiplying by a constant. This is a case where your pipeline
should **correctly improve on** the legacy number, not match it — and you'll
prove exactly that in Homework 3.

---

## Step 5 — Review and reconcile (10 min)

Don't stop at "it ran." Review it against the spec, the way you'd review a new
engineer's PR. Use **C10 — Review Rubric**.

```bash
# legacy target:
( cd ../../data && python3 vol_report.py 2025-08 )
# your pipeline:
python3 pipeline.py --month 2025-08
```

Check, line by line in your acceptance criteria:

- [ ] **Physical and taxable reconcile** to the legacy numbers for 2025-08 (top
      terminals match to the dollar — er, to the gallon).
- [ ] Volumes use **`net_gal`**.
- [ ] Physical excludes `status = 8` and `mode = 8`; taxable **additionally**
      excludes `prod_cd = 6`.
- [ ] Exactly **one row per terminal per month** present in the data.
- [ ] The magic values are **named**, not bare integers.
- [ ] Any RIN difference is a **documented, intended** correction.

If a number is off, that's a finding — chase it. A pipeline that reconciles for a
reason you understand is worth ten that "look about right."

---

## Pacing (rough markers from the start of the session)

| Elapsed | Where you should be |
|---:|---|
| 25 min | Spec drafted — sharp on grain, units, exclusions |
| 45 min | Rules extracted from the legacy script; folded into the spec |
| 60 min | Plan approved |
| 95 min | Pipeline runs; physical reconciles or you're debugging the gap |
| 110 min | Physical + taxable reconcile; reviewing against the spec |

If you fall behind: a correct **physical-only** pipeline plus a clean spec is a
complete, shippable slice. Taxable and RIN can come in Homework 3 and Session 5.

---

## What you'll take from this

The loop you just ran is the real workflow for any data deliverable:

1. **Sharpen** the ask into a spec — grain, filters, units, edge cases — before
   any code.
2. **Extract** the true rules from the code that already owns them, distrusting
   the comments.
3. **Plan** with both artifacts; review before building.
4. **Build, run, reconcile** against a known number.
5. **Review against the spec**, not just that it runs.

You'll run a variant of this for every pipeline, migration, or report you build
with the agent from here. Not all five steps every time — but the moves are the
same.

**Homework 3** takes your pipeline one slice further and proves it with a test.
**Session 5** scales the rest across parallel agents.
