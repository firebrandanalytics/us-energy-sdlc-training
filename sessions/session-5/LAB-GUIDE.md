# Lab Guide: Scaling the Build, and What's Next — Session 5

U.S. Energy AI Software-Development Training · Session 5 (120 min)

This is your reference for the session. The instructor walks the room through each
step live; this guide is here so you can keep moving if you fall behind, or pick
up from any step if you arrived late.

This is **Exercise 2, part 2** — you finish the pipeline you started in Session 4
and extended in Homework 3, this time by **splitting the work across parallel
agents** and making the result trustworthy.

---

## What you're building

A **finished** monthly-volume pipeline: the clean replacement for
`data/vol_report.py` that produces, per terminal per month, the **physical**
volume, the **taxable** volume, and the **RIN credit gallons** — plus a
**validation and data-quality layer** that proves the numbers are trustworthy and
flags anything suspicious.

You'll do it in four moves:

1. **Write the contract** (~15 min) — pin the shape of the data that flows between
   the transformation and the checks. This is the boundary your two subagents
   build against.
2. **Build in parallel with subagents** (~45 min) — one subagent finishes the
   transformation; another builds validation + a data-quality report; both against
   the contract. The main session integrates.
3. **Wire it together and verify end to end** (~25 min) — run it, reconcile
   against the legacy numbers, chase any disagreement.
4. **Make it trustworthy** (~20 min) — direct the agent to generate the tests,
   data-quality checks, and a short data-quality note someone else could read.

The final ~15 min is the art of the possible and the course close — no keyboard
needed for that part.

---

## Environment

You will work in **`sessions/session-5/`** (this folder). From here, the committed
database is at **`../../data/us_energy.sqlite`** — that two-levels-up path is the
one to use everywhere in this lab, the same as Session 4.

### Set up

```bash
cd sessions/session-5
python3 -m venv venv
source venv/bin/activate            # Windows Git Bash: source venv/Scripts/activate
pip install pytest                  # for the reconciliation + validation tests
```

### Bring your Session 4 / Homework 3 pipeline into this folder

Start from what you already built. Copy your `pipeline.py` here so this session
has a clean working directory:

```bash
cp ../session-4/pipeline.py ./pipeline.py     # or wherever your HW3 version lives
```

If you don't have a working `pipeline.py` to carry in, that's fine — there's a
checkpoint starter at the bottom of this guide (**"If you're starting cold"**) so
you can join the parallel build anyway.

### Confirm the database opens from here, and re-establish your reconciliation target

```bash
python3 -c "import sqlite3; print(sqlite3.connect('../../data/us_energy.sqlite').execute('SELECT COUNT(*) FROM lifts').fetchone())"
# -> (50025,)

# The legacy script hard-codes its DB name, so run it from inside data/:
( cd ../../data && python3 vol_report.py 2025-08 )
```

Keep that legacy output on screen — it's your reconciliation target again today.

---

## Step 1 — Write the contract (15 min)

When you split work across two agents, the **only** thing they have to agree on is
the shape of the data that crosses the boundary between them. Get that wrong and
you get an integration bug; get it explicit and the two halves snap together. So
before any code, write the contract down.

For this pipeline the boundary is simple: the **transformation** produces rows,
and the **validation/reporting** layer consumes them. The contract is *what one
row is*.

Open Claude Code in this folder and have it draft the contract from your spec and
your existing code:

```
Read pipeline.py in this folder and ../../data/vol_report.py. I'm about to split
the remaining work in two: one agent finishes the transformation (the volume
measures by terminal and month), another builds validation and a data-quality
report on top of it. Before either is built, write the CONTRACT between them — the
exact shape of a single output row — as a short markdown block. Include:

- the row's fields, with names and types (term_cd, month, and the measures);
- what each measure means in one line (which gallons, which exclusions);
- the invariants the validator can rely on (e.g. the ordering between physical
  and taxable, the grain / uniqueness rule, value ranges).

Keep it to something I can read in 30 seconds. Do not write code yet.
```

Read what it produces and tighten it. Your contract should pin at least:

- **The fields:** `term_cd` (text), `month` (`YYYY-MM`), `physical_gal`,
  `taxable_gal`, `rin_gal` (all numeric).
- **What each measure is:** physical = `SUM(net_gal)` over real movements;
  taxable = physical minus dyed off-road diesel (`prod_cd = 6`); RIN = credit
  gallons from the `rin_transactions` ledger.
- **The invariants** — these are what make a validator possible:
  - `physical_gal >= taxable_gal >= 0` (taxable is a *subset* of physical, so it
    can never exceed it — a great cheap check);
  - exactly **one row per (`term_cd`, `month`)** — the grain;
  - every `term_cd` resolves to a real terminal.

> **Why this is the whole game:** the contract is the interface. Once it's
> written, the transformation agent and the validation agent never have to talk to
> each other — they each just honor the contract. That's what makes the parallel
> split safe. (It's the same discipline as an API contract; here the "API" is a
> row shape.)

Save the contract somewhere you can paste it (a `CONTRACT.md`, your notes,
anywhere). You'll hand it to both subagents next.

---

## Step 2 — Build in parallel with subagents (45 min)

Now split the work. Same Claude Code session — but you delegate the two halves to
subagents so they run side by side, and the main session integrates.

State the split clearly and hand both subagents the contract:

```
Use subagents to finish this pipeline in parallel. Both work against this CONTRACT
and must honor it exactly:

<paste your contract here>

- Subagent A — TRANSFORMATION: make sure pipeline.py produces the full set of
  measures per the contract: physical_gal, taxable_gal, and rin_gal, one row per
  terminal per calendar month present. Volume basis is net_gal (temperature-
  corrected), never gross_gal. Exclude status = 8 (void) and mode = 8 (book
  adjustment) from every measure; taxable additionally drops dyed off-road diesel
  (prod_cd = 6) and nothing else. Pull rin_gal from the rin_transactions ledger
  (rin_qty), NOT a flat factor. Use named constants for the magic values, and a
  range predicate for the month (>= first-of-month AND < first-of-next), not
  substr on the timestamp.

- Subagent B — VALIDATION + DATA QUALITY: add a validation layer that checks every
  output row against the contract's invariants (physical >= taxable >= 0, one row
  per terminal-month, term_cd is real, month well-formed). Add a data-quality scan
  that computes the void rate by terminal and month and flags any terminal-month
  whose void rate is abnormally high. Expose a single function I can call that runs
  all checks and returns a structured pass/fail result, and a --check CLI flag that
  prints it.

When both are done, integrate them in pipeline.py and report what each subagent
changed. Do not run yet — I'll review the diff first.
```

Approve actions as they come up. **`Ctrl+E` on anything you're not sure about** —
see the action before approving (Session 2 muscle). Auto-accept the obvious ones.

### What to watch for as the agents work

The same things that bit people in Sessions 3 and 4 come back here — keep an eye
out and push back:

- **The transformation agent grabs `gross_gal`** because the name reads "more
  total." It must be `net_gal`. If the diff sums `gross_gal`, send it back.
- **An exclusion goes missing or goes too far.** Physical *keeps* dyed diesel;
  taxable *drops* it. If both measures drop `prod_cd = 6`, or neither does, that's
  the bug — name it.
- **RIN gets re-multiplied by a flat factor** instead of summing the ledger. The
  legacy `RVO = 1.6` is wrong; the ledger already carries the right per-product
  equivalence. If you see a constant times gallons, point at the contract.
- **The validation agent invents a different row shape** than the transformation
  produces (e.g. expects `taxable` but the field is `taxable_gal`). The contract
  is there to prevent exactly this — if it happens, that's the integration bug the
  contract was supposed to catch. Make them both honor the contract's field names.
- **Subagents may run sequentially, not truly in parallel.** That's fine. The
  *work split* is the point; the parallelism is the bonus.

> Review the diff before you run it — the way you'd review a new engineer's PR. Use
> **C10**. It's much cheaper to catch "you summed gross" in the diff than to debug
> a reconciliation gap later.

---

## Step 3 — Wire it together and verify end to end (25 min)

Now run it and prove it.

```bash
python3 pipeline.py --month 2025-08         # the transformation output
python3 pipeline.py --check                 # the validation + data-quality report
```

(Your CLI flags may differ slightly depending on how your plan shaped them — use
whatever your build chose.)

### Reconcile against the legacy numbers

This is the verification that matters. Physical and taxable **must** match the
legacy script for a known month; RIN **must** differ (the documented correction
from Session 4):

```bash
( cd ../../data && python3 vol_report.py 2025-08 )   # legacy target
python3 pipeline.py --month 2025-08                  # yours
```

Top-6 by physical for 2025-08 should match the legacy script to the gallon:

| term | physical | taxable |
|---|---:|---:|
| DAL | 1,517,103 | 1,371,642 |
| OMA | 1,435,379 | 1,245,951 |
| APP | 1,367,376 | 1,264,810 |
| FAR | 1,339,984 | 1,198,102 |
| DSM | 1,323,169 | 1,207,528 |
| HOU | 1,282,704 | 1,165,897 |

And the RIN total should be the *corrected* figure, **not** the legacy one:

| 2025-08 RIN-eligible gallons | value |
|---|---:|
| Legacy `vol_report.py` (flat 1.6) | 8,906,150 |
| Your pipeline (`rin_transactions` ledger) | **9,077,485** |

> **Rounding note:** if a per-terminal figure is off by a gallon or two, that's a
> rounding-policy difference, not a bug — the physical/taxable totals reconciling and
> the RIN total landing on **9,077,485** are the authoritative checks.

### When something doesn't match

That's normal and it's the work. Read the disagreement with Claude Code:

- **Physical off:** usually a missing exclusion (`status = 8` / `mode = 8`) or
  `gross_gal` sneaking in.
- **Taxable off:** the dyed-diesel asymmetry — dropped from both or from neither.
- **RIN matches the legacy 8,906,150:** the agent re-applied a flat factor instead
  of summing the ledger. That's a bug *because* it matches.
- **A query feels slow:** check it with `EXPLAIN QUERY PLAN`. A `substr(lift_ts,
  1,7) = '2025-08'` filter forces a full `SCAN`; a range predicate plus an index
  in your own copy turns it into a `SEARCH`:
  ```sql
  CREATE INDEX ix_lifts_term_ts ON lifts(term_id, lift_ts);
  ```
  (Session 3's query-plan lesson, paid off in the finished build. The index lives
  in *your* copy of the DB; it doesn't change anyone else's.)

### Read the data-quality report

Run the check and read what it flags:

```bash
python3 pipeline.py --check --month 2025-08
```

There is **one real anomaly** in this dataset, and a good data-quality scan finds
it: an abnormal cluster of voided lifts at **one terminal in one month**. Don't
take our word for which — let your check surface it, then confirm by hand:

```bash
sqlite3 ../../data/us_energy.sqlite \
  "SELECT t.term_cd, COUNT(*) AS total,
          SUM(CASE WHEN l.status=8 THEN 1 ELSE 0 END) AS voids
   FROM lifts l JOIN terminals t ON t.term_id=l.term_id
   WHERE substr(l.lift_ts,1,7)='2025-08'
   GROUP BY t.term_cd
   ORDER BY 1.0*voids/total DESC LIMIT 5;"
```

The terminal at the top of that list is carrying a void rate roughly double the
dataset-wide ~8%. Your pipeline should **flag** it — not silently absorb it. That
flag is exactly why excluding voids correctly *moves* that terminal's August
physical number; the anomaly is real, not a rounding artifact.

---

## Step 4 — Make it trustworthy (20 min)

A pipeline someone else can trust needs three things the agent is good at
generating once you've verified the numbers: **tests**, **data-quality checks**
(done in Step 2), and **documentation**.

### Tests that pin the result

```
Write a pytest test module for this pipeline against ../../data/us_energy.sqlite.
Include at least:
- a reconciliation test: physical_gal and taxable_gal for 2025-08 match the legacy
  vol_report.py figures exactly (top-6 terminals, by the gallon);
- a correction test: the 2025-08 RIN total is the ledger figure (9,077,485) and is
  NOT the legacy flat-1.6 figure (8,906,150);
- an invariant test: for every output row, physical_gal >= taxable_gal >= 0, and
  there is exactly one row per terminal-month;
- a data-quality test: the void-rate scan flags the abnormal terminal-month.
Derive every expected value from the spec or the legacy script, not from running
the current implementation and copying its output.
```

Then run them:

```bash
pytest -v
```

> **Why "derive expected values from the spec, not the output":** the easiest way
> to write a fake test is to run the code, see what it returns, and assert that.
> That test passes even when the code is wrong. Your reconciliation numbers come
> from the legacy script and Session 4 — anchor the tests to those.

### Documentation the next person can read

```
Write a short README for this pipeline (half a page): what it computes, the exact
exclusions and why each one, which gallon column and why, how a month is bounded,
how to run it and run the checks, and the reconciliation result — including the one
place we intentionally differ from the legacy script (RIN) and why. Treat the
code's behavior as the source of truth; if any comment in the code disagrees with
what the code does, flag it rather than repeating it.
```

Review what it writes against your own understanding. A doc that repeats a stale
comment is worse than no doc — you spent all of Session 3 learning that.

### Final review against the spec

Don't stop at "it ran and the tests are green." Run **C10** over the whole thing:

- [ ] Physical and taxable **reconcile** to the legacy numbers for 2025-08.
- [ ] RIN is the **corrected** figure, and the difference is **documented**.
- [ ] Volumes use **`net_gal`**; no scaling factor anywhere.
- [ ] Physical excludes `status = 8` and `mode = 8`; taxable **additionally**
      excludes `prod_cd = 6`.
- [ ] Exactly **one row per terminal per month** present in the data.
- [ ] The magic values are **named**, not bare integers.
- [ ] The validation layer's invariants actually **fail** on bad input (try it:
      hand it a row where taxable > physical and confirm it complains).
- [ ] The data-quality scan **flags** the abnormal terminal-month.
- [ ] The tests derive expected values from the spec, not from the output.

---

## Pacing (rough markers from the start of the session)

| Elapsed | Where you should be |
|---:|---|
| 20 min | Homework 3 share-back done; contract written |
| 40 min | Both subagents reporting done; integrating |
| 65 min | Pipeline runs; physical + taxable reconcile or you're chasing the gap |
| 85 min | Validation + DQ report working; the anomaly is flagged |
| 105 min | Tests green or close; reviewing against the spec |

If you fall behind: a finished **transformation** that reconciles, plus a
validation layer that runs its invariants, is a complete, shippable result. The
tests and the README can be finished asynchronously. A pipeline that reconciles
for reasons you understand beats ten that "look about right."

---

## The art of the possible — where this earns its keep

(No keyboard for this part — watch and think about your own backlog.)

The loop you just ran end to end isn't a classroom toy. It's the workflow for the
work that actually piles up on a data team:

- **Legacy comprehension** — the move from Session 3, on every undocumented script
  and view you've inherited. *What does this really compute, and which comments
  lie?*
- **Migrations** — extract the true rules from the old system, write the contract,
  build the new path against it, reconcile to the old numbers. Exactly what you did
  here, scaled to a warehouse table or a whole feed.
- **Data-quality triage** — point the agent at a feed and have it propose the
  invariants and anomaly scans, the way Subagent B did. The GRB void cluster is a
  stand-in for the real anomalies in your data.
- **Documentation and lineage** — generate the data dictionary, the column
  meanings, the "what feeds what," grounded in the code and data rather than in
  someone's stale wiki.

And a quick look beyond the terminal — the same Claude Code shows up in more places
than the one we used all course:

- in the **terminal** (what we've used),
- in the **web app** (claude.ai),
- as **IDE extensions** (VS Code, JetBrains),
- on **remote / cloud machines** for long-running, server-side work,
- via **scheduled agents** that run on a clock — e.g. this pipeline's `--check`
  on a nightly schedule.

Pick the corner that matches your workflow and explore it.

---

## What you'll take from this

The full loop, in order, is the course:

1. **Comprehend** — read the code and data you didn't write (Session 3).
2. **Scope and operate** — least-permission, the operator levers (Session 2).
3. **Sharpen the ask** — vague request to data spec (Session 4).
4. **Extract, plan, build** — lift the real rules, plan, build the pipeline
   (Session 4).
5. **Scale and verify** — contract, parallel agents, reconcile, make it
   trustworthy (this session).

Not all five every time — but the moves are the same. Run a variant of this for the
next pipeline, migration, or data-quality problem on your plate. Then own the
outcome: review it, calibrate your trust by the risk, and know when to let the
agent run.

---

## If you're starting cold

If you don't have a working `pipeline.py` to carry in from Session 4 / Homework 3,
you can still do today's lab. Create a minimal starter so the parallel build has
something to extend:

```bash
cd sessions/session-5
python3 -m venv venv && source venv/bin/activate
pip install pytest
```

Then open Claude Code here and run:

```
I need a checkpoint starter for a monthly-volume pipeline before I split the
remaining work across subagents. Read ../../data/vol_report.py and the schema of
../../data/us_energy.sqlite (.schema lifts). Write a minimal pipeline.py in this
folder that computes ONLY physical_gal (SUM(net_gal), excluding status = 8 and
mode = 8) by terminal for one month, as a half-open range predicate, with named
constants. Just that one measure, runnable, reconciling to vol_report.py's
physical numbers for 2025-08. We'll add taxable, RIN, and the validation layer via
subagents next.
```

Verify it reconciles physical for 2025-08 against the legacy script, then rejoin at
**Step 1 — Write the contract**.
