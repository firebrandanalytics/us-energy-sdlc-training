# Lab Guide — Exercise 1: Reading an Opaque Query

U.S. Energy AI Training · Session 3 · Hands-on (~55 min)

---

## The scenario

A colleague has left. In a shared notebook you find this query, labelled only
"monthly volumes — DO NOT CHANGE":

```sql
SELECT term_id, SUM(net_gal) AS net
FROM lifts
WHERE substr(lift_ts, 1, 7) = '2025-08'
  AND status <> 8
  AND mode  <> 8
  AND prod_cd <> 6
GROUP BY term_id
ORDER BY net DESC;
```

It runs. It returns numbers the desk relies on. **Nobody can tell you what the
three magic filters are for, whether they're still correct, or why it's slow at
month-end.** Your job today is to find out — using the agent to do the reading,
and the data to settle every claim.

That's the exercise. Everything below is the method.

> **The discipline for the whole lab:** the agent will happily *paraphrase* the
> query and *repeat the comments back* as if they were fact. That is not the goal.
> For every claim — what a code means, what a filter is for — make the agent
> **prove it from the rows.** A meaning without a query behind it is a guess.

---

## Setup (5 min)

The dataset is at `data/us_energy.sqlite` from the repo root. No installs beyond
`sqlite3` (and Python, which you have). Confirm it opens:

```bash
# from the repo root
sqlite3 data/us_energy.sqlite ".tables"
```

You should see seven tables, including `lifts` (the ~50k-row fact table),
`code_ref` (a lookup), and `terminals`. If `sqlite3` isn't available, the Python
snippet in [`../../data/README.md`](../../data/README.md) works with no installs.

**Open a Claude Code session at the repo root** (so it can read both the database
and the data dictionary). Everything below is run through that session.

Have these handouts open: **D2** (query plans) and **D3** (magic values). Skim
**D1** (data glossary) if the fuel terms are unfamiliar.

> **One ground rule for the lab:** point the agent at the **database file** and
> ask it to run real queries. Don't let it answer from the column names or from
> `DATA-DICTIONARY.md` alone — both are deliberately incomplete and, in places,
> out of date. The rows are the truth.

---

## Step 1 — Literal behavior (8 min)

Before you can ask *why*, you need *what* — mechanically, no interpretation yet.

**Prompt Claude Code:**

> Read this query (paste it). Against `data/us_energy.sqlite`, describe in plain
> English exactly what it returns: the grain of one output row, what's summed,
> how rows are grouped and ordered, and — literally — which rows the three
> `WHERE` filters keep and drop. Stay literal. Save *why* each filter exists for
> the next step. Don't trust column names; run the query and a `COUNT(*)` to
> confirm what you tell me.

Read the answer. Your bar: **could you explain to a colleague, in two minutes and
without looking at the query, what one row of the output represents and what got
excluded?** If not, ask follow-ups until you can.

**Checkpoint 1:** You can state the grain ("one row per terminal, August 2025,
summed net gallons") and name the three filters mechanically — without yet
claiming what they *mean*.

---

### Grounded-learning beat — don't skip this

Is there anything in the answer you didn't fully follow? `net_gal` vs `gross_gal`?
What `substr(lift_ts, 1, 7)` does? `GROUP BY`?

If yes — stop and ask the agent to explain it **using this query and this data**
as the example, not in the abstract:

> Explain what `substr(lift_ts, 1, 7) = '2025-08'` actually matches, using real
> values from `lifts.lift_ts`. Show me three sample timestamps it keeps and three
> it drops.

One concept you actually understand beats five you nodded past. This move —
"explain it grounded in *this* code" — is the one you'll reuse all course.

---

## Step 2 — Decode the magic values (15 min)

This is the heart of the lab. `status <> 8`, `mode <> 8`, `prod_cd <> 6` — three
bare integers. The query's author knew what they meant; the schema doesn't say.

**First, check the lookup — and watch it fail you.**

```sql
SELECT * FROM code_ref WHERE code_type = 'status';
```

You'll get `1 = Open` and `9 = Void (DEPRECATED ...)`. Notice what's **missing**:
there is no row for `8`. The query filters out `status = 8`, but the lookup
doesn't even list it. **A code the data uses but the lookup never mentions is a
flashing sign the lookup is stale.** This is exactly why you can't stop at the
dictionary.

**Now make the agent decode each value from the data.**

> For each of the three filters — `status <> 8`, `mode <> 8`, `prod_cd <> 6` —
> figure out what the excluded value means by profiling the data in
> `data/us_energy.sqlite`. Don't rely on `code_ref` or `DATA-DICTIONARY.md`;
> check whether they even cover these codes, then prove the meaning from the
> rows. For each, tell me (a) the value's meaning, (b) the evidence query you
> ran, and (c) *why* a volume rollup would exclude it.

The agent should run something like these (run them yourself too — verifying *is*
the skill):

```sql
-- Distribution: which status codes actually occur? (8 appears; the lookup's 9 doesn't)
SELECT status, COUNT(*) FROM lifts GROUP BY status ORDER BY status;

-- Does status 9 — the value the lookup calls "void" — exist at all?
SELECT COUNT(*) FROM lifts WHERE status = 9;          -- 0: a ghost code

-- Where do status-8 rows cluster? Reversals/voids often clump.
SELECT term_id, substr(lift_ts,1,7) AS ym, COUNT(*)
FROM lifts WHERE status = 8
GROUP BY term_id, ym ORDER BY COUNT(*) DESC LIMIT 5;

-- mode: only 1-4 are documented. What else is in the data?
SELECT mode, COUNT(*) FROM lifts GROUP BY mode ORDER BY mode;   -- an 8 appears

-- prod_cd: tie the code to something readable. Renewables carry a d_code; do these?
SELECT prod_cd, d_code, COUNT(*) FROM lifts GROUP BY prod_cd, d_code ORDER BY prod_cd;
```

**What you're working toward** (let the data lead you here — don't just take it
from us):

- **`status = 8`** is the **current void/reversed** code. The lookup's "9 = void"
  is stale — `status 9` doesn't appear in the data at all. Excluding 8 keeps the
  rollup to real, non-reversed tickets.
- **`mode = 8`** is **not a transport mode**. Modes 1–4 are pipeline/truck/rail/
  barge; `8` is a **non-physical book adjustment** (an accounting entry). It must
  be excluded from any physical-volume figure.
- **`prod_cd = 6`** is **dyed (off-road) diesel** — real, physical fuel, but
  **tax-exempt**. Whether you exclude it depends on the report (see the "why this
  is subtle" note below).

> **Push the agent if it's vague.** If it says "8 probably means void," reply:
> *"Don't guess. Show me from the data why 8 behaves like a void and 9 doesn't
> exist."* An intent reconstruction is a dialogue, not a hand-off.

**Why `prod_cd <> 6` is the subtle one.** Dyed diesel is physically real, so it
*belongs* in a physical-volume number — yet this query drops it. Ask the agent:

> This query excludes `prod_cd = 6` (dyed diesel). Is that correct for a
> *physical* volume rollup? When would excluding it be right, and when wrong?
> Answer from what dyed diesel is, not from the column name.

The honest answer: for **taxable** volume, dropping dyed diesel is right (it's
tax-exempt). For a pure **physical** movement total, dyed diesel should arguably
be **kept**. So this query — labelled just "monthly volumes" — is quietly a
*taxable-ish* view, not a clean physical one. **That ambiguity is a finding.**
Note it as an open question for a human, not something the data alone can settle.

**Checkpoint 2:** You can state, in one sentence each, what `status = 8`,
`mode = 8`, and `prod_cd = 6` mean **and** why each is excluded — each backed by a
query you ran yourself. You've also flagged that `prod_cd <> 6` makes this a
taxable-leaning view, not a pure physical one.

---

## Step 3 — Read the machine: the query plan (15 min)

The query "is slow at month-end." Let's see why — and fix it. Keep **D2** open.

**Get the plan and have the agent translate it.**

> Run `EXPLAIN QUERY PLAN` on the query against `data/us_energy.sqlite` and
> explain each line in plain English. Which table is scanned, and roughly how
> many rows is that? Is that the efficient way to answer this query?

You'll see something like:

```
SCAN lifts
USE TEMP B-TREE FOR GROUP BY
```

`SCAN lifts` means SQLite reads **every one of the ~50,000 rows** and checks the
date on each — even though only one month qualifies. There is no index on
`lifts`; that's deliberate, and that's the lesson. (`SCAN` = read everything;
`SEARCH` = jump to the rows you need. See D2.)

**Now the catch — the date filter as written can't use an index.** The query
wraps the column in a function: `substr(lift_ts, 1, 7) = '2025-08'`. A function
on the column **defeats an index** (it's "non-sargable"). Have the agent fix the
predicate *first*, then add the index:

> The date filter `substr(lift_ts,1,7) = '2025-08'` wraps the column in a
> function, so no index on `lift_ts` can help it. Rewrite it as an equivalent
> half-open range on `lift_ts`, confirm it returns the identical rows, then
> propose the single index most likely to turn the `SCAN` into a `SEARCH`. Write
> the `CREATE INDEX`, and re-run `EXPLAIN QUERY PLAN` to prove the plan changed.
> Do not change the query's results — only its plan.

The rewrite is a half-open range (keeps every August timestamp, including times
of day):

```sql
-- equivalent, and index-friendly:
WHERE lift_ts >= '2025-08-01' AND lift_ts < '2025-09-01'
```

Then the index and the re-check:

```sql
CREATE INDEX idx_lifts_ts ON lifts(lift_ts);

EXPLAIN QUERY PLAN
SELECT term_id, SUM(net_gal) AS net
FROM lifts
WHERE lift_ts >= '2025-08-01' AND lift_ts < '2025-09-01'
  AND status <> 8 AND mode <> 8 AND prod_cd <> 6
GROUP BY term_id ORDER BY net DESC;
```

The plan line should flip to:

```
SEARCH lifts USING INDEX idx_lifts_ts (lift_ts>? AND lift_ts<?)
USE TEMP B-TREE FOR GROUP BY
```

`SCAN` became `SEARCH ... USING INDEX`. The engine now jumps to the August rows
instead of reading the whole table. (The `GROUP BY` temp B-tree stays — that's
the aggregation, expected.)

**Two things to verify, like a reviewer:**

1. **The result didn't change** — same terminals, same totals, faster path. Ask
   the agent to run the query before and after and diff the output. (An index
   changes the *plan*, never the *answer*.)
2. **Which filters actually benefit.** Ask:

   > Of the four filters, which are selective enough to benefit from an index, and
   > which only affect correctness? Back it up with a `COUNT` for each.

   The date range keeps ~4,400 of 50k rows — **selective**, worth indexing. The
   `<> 8` / `<> 6` exclusions keep almost everything (e.g. `status <> 8` keeps
   ~46k rows) — they're for **correctness**, not speed; an index won't help them.

> **A note on timing in this lab.** Our dataset is small, so wall-clock times are
> tiny either way. That's fine — the *plan* is the lesson. The plan tells you
> *what* changed (SCAN → SEARCH); a timing tells you *whether it mattered*, and it
> matters most when the table is large. On your real warehouse it's the
> difference between seconds and minutes.

**Checkpoint 3:** Your plan shows `SCAN` before and `SEARCH ... USING INDEX`
after; you rewrote the non-sargable `substr(...)` filter to a range so the index
could engage; and you confirmed the result set is unchanged.

> The index lives only in **your** copy of the database — it doesn't affect anyone
> else, and leaving it there is fine.

---

## Step 4 — Don't trust the comments (8 min)

The query had no comments. The script you'll meet for homework — `data/vol_report.py`
— is the opposite: it's *full* of them, and several **lie**. A quick taste now, so
the homework starts from a clear stance.

**Point the agent at it:**

> Read `data/vol_report.py`. Don't trust the comments. Pick two filters and, for
> each, tell me (a) what the line literally does, (b) what the comment claims, and
> (c) which one the data in `data/us_energy.sqlite` supports — run a query to
> settle it.

You'll find gaps like these (don't take our word — make the agent prove each):

| The comment says | What the line does | The reality |
|---|---|---|
| `# skip test + voided tickets (status 9)` | filters `status == 8` | Voids are `8`, not the `9` the comment names. The comment is a fossil. |
| `# barge loads are reconciled upstream ... drop them` (on `mode == 8`) | filters `mode == 8` | Mode 8 is a **book adjustment**, not barge. Barge is mode **4** — and it's *kept*. The comment names the wrong thing entirely. |

**The method, in one line:** for each filter, ask *"if I deleted this line, which
rows would change?"* — then name those rows from the data. That is the true
intent, and it is frequently **not** what the comment says.

**Checkpoint 4:** You've caught at least one — ideally several — of the comments in
`vol_report.py` that contradict the code's actual behavior, with a query that proves
each gap. (There are five lying comments in all; the full hunt is Homework #2.)

---

## If you have time — find the anomaly (stretch)

In Step 2 you grouped `status = 8` rows by terminal and month. Look again at the
top of that list. **One terminal-month sticks out far above the rest.** Ask:

> Among voided (`status = 8`) lifts, is any single terminal-and-month unusually
> high relative to the others? Quantify it: that terminal's void rate that month
> versus the dataset-wide void rate.

This is a **data-quality anomaly** to *find*, not be told — exactly the kind of
thing legacy comprehension surfaces. Note what you find as an open question for a
human ("why the spike?"), the same way you'd flag it on a real handoff.

**Not spotting it live is fine** — it's a bonus that rewards thorough profiling, not a required finding.

---

## Wrap-up (5 min)

Quick reflection before we debrief:

1. Which magic value took the longest to pin down, and what finally settled it —
   the lookup, or the data?
2. The query was labelled just "monthly volumes." After decoding `prod_cd <> 6`,
   is that label honest? What would you rename it?
3. If you handed the next engineer one sentence about this query before they
   touched it, what would it be?

---

## What you built

By the end of Exercise 1 you have, for a query you'd never seen:

| Artifact | What it is |
|---|---|
| Literal description | What one output row is and what each filter mechanically does |
| Decoded magic values | What `8`/`8`/`6` mean, each proven from the rows |
| Intent per filter | *Why* each exclusion is there — including the taxable-vs-physical ambiguity |
| A faster, equivalent query | Non-sargable filter rewritten; index added; plan flipped SCAN → SEARCH |
| Comment-rot findings | Lying comments in `vol_report.py` caught against behavior (there are five) |

That's the comprehension move end to end: **literal → decode → intent → read the
machine → distrust the comments.** Homework #2 runs the full version on
`vol_report.py`.

---

## Appendix — Quick troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `sqlite3: command not found` | CLI not installed | Use the Python snippet in `../../data/README.md` — standard library, no installs. |
| The agent answers from column names / the dictionary, not the data | It skipped running a query | Reply: *"Don't infer from the name or `DATA-DICTIONARY.md`. Run a query against the database and show me the rows."* |
| `EXPLAIN QUERY PLAN` still shows `SCAN` after you added the index | You left the `substr(...)` filter in place (non-sargable) | Rewrite the date filter to the half-open range first, *then* the index engages. |
| The agent "added an index" but didn't prove it | It asserted instead of showing | Make it paste the before/after `EXPLAIN QUERY PLAN`. The proof is the line flipping to `SEARCH`. |
| You're not sure the index changed the answer | Reasonable doubt — check it | Run the query before and after and diff. An index changes the plan, never the result. |
| The agent confidently restates a comment as fact | Comments read like authority | *"That's the comment. What do the rows say? Run a query."* |
| You accidentally indexed and want a clean slate | — | `DROP INDEX IF EXISTS idx_lifts_ts;` — or just re-clone the `data/` folder. |
