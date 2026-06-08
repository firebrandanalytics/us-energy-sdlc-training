# Lab Guide: From Vague Ask to a Working Service — Session 4

U.S. Energy AI Software-Development Training · Session 4 (120 min)

This is your reference for the session. The instructor walks the room through each
step live; this guide is here so you can keep moving if you fall behind, or pick
up from any step if you arrived late.

This is **Exercise 2, part 1**. You build a clean **service** here. In Homework 3
you put a tiny dashboard on it; in Session 5 you extend that dashboard with
parallel agents.

---

## What you're building

A clean, documented replacement for the legacy `data/vol_report.py` — but built as
a **service**, not a script. A `service.py` that **returns** monthly volumes by
terminal (physical and taxable net gallons), so anything can consume it: a CLI, a
test, and — next session — a web dashboard. By the end of the session you should
have a sharpened spec (with an output contract), and a running service that gets at
least **physical and taxable** volume right, reconciled against the legacy numbers
for a known month.

> **Script vs. service — the one distinction this session turns on.** The legacy
> `vol_report.py` *prints* a report and exits; its numbers are trapped inside a
> `print()`. A service *returns* the numbers as data (`monthly_volumes("2025-08")`
> hands back a list of rows). Same query underneath — but a service is something
> you can call, test, and build a UI on. That return value, and its shape, is the
> whole point.

You'll do it in five moves:

1. **Sharpen the ask** (~25 min) — turn a vague request into a spec using the D4
   template: grain, filters, units, edge cases — *and* the output contract (the
   shape of one row).
2. **Extract the real rules** (~20 min) — direct the agent to lift the true logic
   out of `vol_report.py` and the schema, distrusting the comments.
3. **Plan** (~15 min) — hand the spec + extracted rules to planning mode; review
   and approve.
4. **Build `service.py`** (~45 min) — a callable service; you direct, the agent
   executes.
5. **Review and reconcile** (~10 min) — check the output against the spec and the
   legacy numbers.

Final ~5 min is debrief and the handoff to Homework 3 / Session 5.

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
# No third-party packages are required for the service itself — sqlite3 ships with
# Python. (FastAPI comes in Homework 3, not today.) If you want the test:
pip install pytest                  # optional; used for the reconciliation test
```

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

Keep that output handy — it's your reconciliation target for the build step.

---

## Step 1 — Sharpen the vague ask into a spec (25 min)

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
- **Output shape** — and here's the new one: what does *one row this service
  returns* look like? Which fields, what types?

> **Watch out:** the dictionary and `code_ref` are deliberately incomplete and a
> little stale. Do **not** treat them as the answer. When the agent cites a code
> meaning, ask it to confirm against the data (`SELECT DISTINCT status FROM
> lifts;` and friends). This is the Session 3 muscle.

### Write the spec — and the output contract (~15 min)

Open **`handouts/D4-data-spec-template.md`** and fill it in. D4 forces the four
things that decide whether the numbers are right — **grain, filters/exclusions,
units, edge cases** — into the open. Use **C7** for the surrounding sections
(constraints, anti-goals, acceptance criteria, files-to-read).

Then add one short, high-leverage section that a one-off script wouldn't need but a
*service* must have — the **output contract**. It's the shape of one row your
service returns. **D5 — Output Contract & Dashboard** is the card for this; the
contract you want looks like:

```
One output row =
  terminal      str    terminal display code, e.g. "DAL"
  month         str    "YYYY-MM"
  physical_gal  int    SUM(net_gal) over real movements
  taxable_gal   int    physical minus dyed off-road diesel (prod_cd 6)

Invariants the caller can rely on:
  - physical_gal >= taxable_gal >= 0   (taxable is a subset of physical)
  - exactly one row per (terminal, month)
  - terminal resolves to a real terminal
```

At minimum your spec must pin:

- **Deliverable** — a *service* (an importable module returning rows), not a print.
- **Grain** — "one row per terminal per calendar month," and the measures per row.
- **Measures + Units** — name the exact column. `SUM(net_gal)`, not "sum the
  gallons." State *why* net, not gross.
- **Filters / Exclusions** — every dropped row, **with its intent**, and **which
  measure it applies to**. (Hint from your Homework 2 dossier: physical and taxable
  share two exclusions but **diverge** on dyed diesel.)
- **Output contract** — the row shape above. This is the seam the dashboard reads.
- **Acceptance criteria** — at least five pass/fail statements.
- **Reconciliation** — what you check against, and how you treat differences.

> **The discipline:** if you can't fill in **Grain** and **Filters / Exclusions**
> precisely, the ask is still vague. Sharpen those two first; the rest follows. And
> if you can't say what one returned row looks like, you can't build the app on it
> — so pin the contract too.

You don't need a perfect spec to move on — but it must be sharp on grain, units,
the exclusion asymmetry, and the row shape, because those are what the agent (and
next week's dashboard) will otherwise get wrong.

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

  > **Bridge from Session 3:** there, the data and the docs couldn't *name* `mode = 8`,
  > so the honest call was "exclude it, but confirm with a human." Treat that as
  > done — for this build, assume the feed owner confirmed `mode = 8` is a
  > non-physical book adjustment. That's the normal arc: flag the unknown, get it
  > confirmed, then build on the confirmed fact (and write it into the spec).
- A "scale up, stored in hundreds" comment that the code **does not** act on —
  gallons are summed as-is.
- The taxable rollup drops `prod_cd = 6` (dyed off-road diesel) **but keeps
  everything else** — despite a "clear diesel only" comment. So physical and
  taxable share two exclusions but **diverge** on dyed diesel.
- A RIN factor (`RVO = 1.6`) applied flat to both renewable products — which does
  **not** match what the data implies. Hold that thought for the stretch.

Fold the confirmed rules into your spec's **Filters / Exclusions** and
**Reconciliation** sections. You now have a spec grounded in real behavior, not
in lying comments.

> **Why this matters:** you are not copying the legacy script. You are recovering
> the *correct* rules it encodes, separating them from the rot, so your clean
> service can keep what's right and fix what's wrong.

---

## Step 3 — Plan before building (15 min)

Switch Claude Code into planning mode so it can't start editing:

```bash
claude --permission-mode plan
```

(Or open normally and `Shift+Tab` into plan mode.)

Hand it both artifacts — your spec and your extracted rules:

```
I'm building a clean replacement for ../../data/vol_report.py as a new service.py
in this folder — a SERVICE, not a script: it must RETURN the data (so a web app can
call it later), not just print it. Below are TWO artifacts; read both before
planning.

ARTIFACT 1 — the spec (what to compute, the exact rules, and the output contract):
<paste your sharpened spec here>

ARTIFACT 2 — the rules extracted from the legacy script (what today's code really
does, and where its comments lie):
<paste your extracted rules here>

Plan the implementation of service.py. The plan must include:
1. The functions you'll expose — at least monthly_volumes(month) and months() —
   and exactly what each RETURNS (the row shape from the output contract: a list of
   dicts, not printed text).
2. The exact SQL for physical and taxable volume, naming every filter and the
   gallon column, and how a month is bounded.
3. How you'll define a month so an index could be used (a range/comparison, not
   substr on the timestamp).
4. A thin command-line entry point (so I can reconcile from the terminal) that
   CALLS the same functions — the CLI is a consumer of the service, not the service.
5. How you'll reconcile the result against vol_report.py, and where you EXPECT to
   differ on purpose.

Do not write any code yet. Wait for my approval.
```

**Read the plan. Push back.** Be especially picky about:

- **Return, don't print.** The core functions must *return* rows. If the plan has
  `monthly_volumes()` printing a table, that's a script in disguise — send it back.
- **The exclusions.** Does physical keep dyed diesel and taxable drop it? If the
  plan applies one filter set to "the volume," that's the bug — call it out.
- **net vs gross.** The plan should name `net_gal` explicitly and say why.
- **The month boundary.** A range predicate (`>= '2025-08-01' AND < '2025-09-01'`,
  or `strftime('%Y-%m', lift_ts) = ?`) over a `substr(lift_ts,1,7)` wrap. (Session
  3's query-plan lesson — a function on the column defeats an index.)

Approve only when the plan is concrete enough that you'd trust the build.

---

## Step 4 — Build `service.py` (45 min)

Same session, plan in context. Let the agent build:

```
Implement the plan as service.py in this folder. Read the DB at
../../data/us_energy.sqlite. Requirements:
- Expose monthly_volumes(month=None) and months() that RETURN data (a list of
  dicts honoring the output contract; months() returns a list of "YYYY-MM"). No
  print() inside these — they return.
- Use named constants for the magic values (no bare 6 / 8 in the SQL — name them:
  status void, book-adjustment mode, dyed-diesel product).
- Add a thin `if __name__ == "__main__"` CLI that CALLS monthly_volumes() and
  prints a top-terminals summary for a month, so I can reconcile.
After it runs, show me the 2025-08 output so I can reconcile it.
```

Approve actions as they come up. **`Ctrl+E` on anything you're not sure about** —
see the action before approving (Session 2 muscle). Auto-accept the obvious ones.

### Run it

```bash
python3 service.py --month 2025-08      # or whatever CLI your plan chose
```

### Prove it really is a service (30-second check)

A service returns data. Confirm yours does — call it directly, no CLI:

```bash
python3 -c "import service; rows = service.monthly_volumes('2025-08'); print(rows[0]); print(len(rows), 'rows')"
# -> {'terminal': 'DAL', 'month': '2025-08', 'physical_gal': 1517103, 'taxable_gal': 1371642}
```

If that prints a row dict, you've built a service — Homework 3's dashboard will call
exactly this.

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

Two good directions for fast finishers — do either or both:

- **Add the RIN credit gallons measure.** Here the legacy script is *wrong* on
  purpose: it multiplies every renewable gallon by a flat `RVO = 1.6`. The real
  per-product equivalence is already carried in the `rin_transactions` ledger
  (`rin_qty`). Pull RIN gallons from that table for non-void lifts in the month
  rather than re-multiplying by a constant. This is a case where your service
  should **correctly improve on** the legacy number (legacy `8,906,150` → correct
  `9,077,485` for 2025-08), not match it — and you document why.
- **Taste the app a day early.** Write a five-line script that imports your service
  and prints an HTML `<table>` of one month's rows. You've just proven the service
  is consumable by a UI — which is exactly what Homework 3 turns into a real page.

---

## Step 5 — Review and reconcile (10 min)

Don't stop at "it ran." Review it against the spec, the way you'd review a new
engineer's PR. Use **C10 — Review Rubric**.

```bash
# legacy target:
( cd ../../data && python3 vol_report.py 2025-08 )
# your service:
python3 service.py --month 2025-08
```

Check, line by line in your acceptance criteria:

- [ ] **Physical and taxable reconcile** to the legacy numbers for 2025-08 (top
      terminals match to the gallon).
- [ ] The core functions **return** rows (they don't just print) — and the row
      matches your **output contract**.
- [ ] Volumes use **`net_gal`**.
- [ ] Physical excludes `status = 8` and `mode = 8`; taxable **additionally**
      excludes `prod_cd = 6`.
- [ ] Exactly **one row per terminal per month** present in the data.
- [ ] The magic values are **named**, not bare integers.
- [ ] (If you did RIN) any RIN difference is a **documented, intended** correction.

If a number is off, that's a finding — chase it. A service that reconciles for a
reason you understand is worth ten that "look about right."

---

## Pacing (rough markers from the start of the session)

| Elapsed | Where you should be |
|---:|---|
| 25 min | Spec drafted — sharp on grain, units, exclusions, and the output contract |
| 45 min | Rules extracted from the legacy script; folded into the spec |
| 60 min | Plan approved |
| 95 min | Service runs; physical reconciles or you're debugging the gap |
| 110 min | Physical + taxable reconcile; reviewing against the spec |

If you fall behind: a correct **physical + taxable** service that returns rows and
reconciles, plus a clear contract, is a complete, shippable slice. RIN is a
stretch; the dashboard is Homework 3.

---

## What you'll take from this

The loop you just ran is the real workflow for any deliverable, data or app:

1. **Sharpen** the ask into a spec — grain, filters, units, edge cases, and the
   output contract — before any code.
2. **Extract** the true rules from the code that already owns them, distrusting
   the comments.
3. **Plan** with both artifacts; review before building.
4. **Build, run, reconcile** against a known number.
5. **Review against the spec**, not just that it runs.

You built a *service* — something callable, with a contract. **Homework 3** puts a
dashboard skeleton on it (small — a page and a table). **Session 5** extends that
dashboard with parallel agents, all of them building against the contract you wrote
today.
