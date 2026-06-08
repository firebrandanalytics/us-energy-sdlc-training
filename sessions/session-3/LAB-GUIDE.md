# Lab Guide — Exercise 1: Reading an Opaque Query

U.S. Energy AI Training · Session 3 · Hands-on (~60 min)

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
month-end.** Your job today is to find out.

That's the exercise. Everything below is the method — and the method has a spine:

> **Read the data first, the documentation second, and know which of your answers
> came from where.** The behavior of the code and the contents of the data are the
> source of truth. The schema doc and the lookup table are *clues* — useful, but
> partial and, in places, out of date. And some things the data simply can't tell
> you: part of the skill is naming those and taking them to a human.

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

**Open a Claude Code session at the repo root.** Everything below is run through
that session.

> **Who runs the queries? The agent does — you direct and review.** You won't be
> typing SQL by hand. You tell Claude Code what to find — *"run a COUNT of each
> status value and show me the rows"* — and it runs the query (it uses `sqlite3`
> or Python under the hood) and shows you the result. Your job is to read what
> comes back and decide whether it actually proves the claim.
> *(Want to poke the data yourself? Optional — `data/README.md` has three ways.)*

Keep **D2** (query plans) handy for Step 3. **Hold off on D1 and D3 until Step 2b** —
they name some of the codes, and the whole point of Steps 0–2a is to read the data
cold first. (If a fuel *term* is unfamiliar mid-lab, ask the agent rather than
reaching for the glossary — that keeps the answers out of sight until you've earned
them.)

---

## Step 0 — Your own first pass (no agent, ~5 min)

Before you let the agent near it, read the query yourself. **Agent closed.** You
have the query and the data dictionary (`data/DATA-DICTIONARY.md`).

In five minutes, get as far as you can on one question: **what does this query
return?** But the more valuable output is the opposite — **what can't you tell?**

- Which filters are obvious, and which are just bare numbers you can't pin down?
- Does the dictionary actually explain `status = 8`, `mode = 8`, `prod_cd = 6`?
- Write down every question mark.

Don't look anything up beyond the dictionary; don't ask the agent. The point is to
feel the opacity directly — that's what makes the next part land. **Keep your list
of question marks.** It's about to become the agent's to-do list, and you'll know
exactly which answers to check hardest.

---

## Step 1 — Literal behavior (8 min)

Now bring in the agent. Before you can ask *why*, you need *what* — mechanically,
no interpretation yet.

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

## Step 2 — Decode the magic values

This is the heart of the lab: `status <> 8`, `mode <> 8`, `prod_cd <> 6` — three
bare integers. We'll decode them in **two deliberate passes**, because *where* an
answer comes from matters as much as the answer.

### Step 2a — Data only, no documentation (12 min)

**Most of the time in the real world, you don't get a data dictionary.** So start
without one. Tell the agent to ignore the docs and reason purely from the rows:

> For `status`, `mode`, and `prod_cd`, work **only from the data** in
> `data/us_energy.sqlite` — the fact tables `lifts`, `rin_transactions`,
> `rack_prices`. **Do not read `DATA-DICTIONARY.md`, do not query `code_ref`, and
> do not read any `.py` file.** For each of the three excluded values
> (`status = 8`, `mode = 8`, `prod_cd = 6`): show its distribution, how it differs
> from the other values of that column (size, related columns, pricing, anything),
> and — crucially — tell me what you **cannot** determine about its *meaning* from
> the data alone.

**Keep it honest:** after it answers, ask it to **list every file and table it
read.** If `DATA-DICTIONARY.md`, `code_ref`, or any `.py` shows up, it broke the
rule — have it redo the pass from the rows only. (Agents reach for the docs by
reflex; catching that is part of the point.)

Direct the agent toward evidence like this, and read each result yourself:

```sql
-- which values actually occur, and how big are they?
SELECT status, COUNT(*), ROUND(AVG(net_gal)) FROM lifts GROUP BY status ORDER BY status;
SELECT mode,   COUNT(*), ROUND(AVG(net_gal)) FROM lifts GROUP BY mode   ORDER BY mode;
SELECT prod_cd, d_code, COUNT(*) FROM lifts GROUP BY prod_cd, d_code ORDER BY prod_cd;

-- do the renewables-looking products carry a RIN d_code? does prod 6?
SELECT prod_cd, COUNT(*) AS n, COUNT(d_code) AS with_dcode FROM lifts GROUP BY prod_cd;

-- does prod 6 price like gasoline or like diesel? (a clue, not a verdict)
SELECT prod_cd, ROUND(AVG(rack_price),2) FROM rack_prices GROUP BY prod_cd ORDER BY prod_cd;
```

**What the data can — and can't — give you.** Be honest about the line:

- **`status = 8`:** the data shows three status values (`1`, `7`, `8`) — the
  counts differ, but the *average ticket* is uniform (~7,500 net gal), so you
  can't pick `8` out by size. It's a meaningful minority (~8%) with an odd August
  cluster at one terminal (see the stretch). **What it can't tell you:** that `8`
  *means* "void." That's a label, and no row carries it.
- **`mode = 8`:** the data shows modes `1–4` plus a small `8` (~2%). Profile it and
  it cuts *across* products and channels with ordinary-looking volumes — which
  already argues it's **not a transport category**. (Some mode-8 rows even carry a
  renewable `d_code` — more evidence it's a cross-cutting flag, not a transport
  mode.) **What it can't tell you:** what `8` actually *is*. Nothing in the rows
  names it.
- **`prod_cd = 6`:** the data shows `7` and `9` carry a `d_code` (and a pathway
  tag) — they're clearly a different *kind* of product — while `6` carries no
  `d_code`, like gasoline/ULSD/NGL/propane. It moves real, sizeable volume, and it
  prices **between gasoline and clear diesel, leaning diesel** (a clue, not a
  verdict). **What it can't tell you:** the exact product name.

**Checkpoint 2a:** For each code you can state (a) what the data shows
structurally and (b) one honest sentence on what the data *can't* settle. You have
hypotheses, not yet conclusions.

### Step 2b — Now bring in the schema, and read it critically (10 min)

Now let the agent use the documentation — but treat it as a *witness*, not an
oracle. It's known to be partial and, in places, stale.

> Now you may read `DATA-DICTIONARY.md` and query `code_ref`. For each of
> `status = 8`, `mode = 8`, `prod_cd = 6`: does the documentation even cover the
> value? Where does it agree or **disagree** with what the data showed in 2a?
> The lookup is known to be out of date — point out exactly where. Then give me
> your best decoded meaning, your confidence, and anything that **neither the data
> nor the docs** can settle — flag those as questions for a human.

```sql
-- the lookup, where it exists, and where it's wrong:
SELECT * FROM code_ref WHERE code_type = 'status';   -- lists 1, 9 — but the data has 1,7,8
SELECT COUNT(*) FROM lifts WHERE status = 9;          -- 0: the lookup's "void" is a ghost
```

Here's where each code lands — and notice they land in three *different* places:

- **`status = 8` — the stale lookup cracks it.** `code_ref` documents `9 = Void
  (DEPRECATED – pre-2021 migration)`, but `9` never appears and `8` is
  undocumented. Read critically, the *drift itself* is the evidence: the void
  convention moved, the old code retired, and `8` is the current void. Data +
  a skeptically-read lookup ⇒ **"8 = void/reversed."** Exclude reversed tickets so
  the rollup counts only real transactions.
- **`mode = 8` — nothing names it. Take it to a human.** `code_ref` lists modes
  `1–4`; the dictionary says "other modes exist — investigate." Neither names
  `8`. The data already told you it's a small, non-`1–4` value. The honest
  deliverable is: *"`mode = 8` is an undocumented, non-transport code; it's
  excluded from a movement total, but I can't prove its meaning from anything we
  have — confirm with whoever owns this feed."* Resist the urge to invent
  "book adjustment" or "barge"; you can't show either from the data.
- **`prod_cd = 6` — the data gives you the finding, the label needs a human.** The
  dictionary documents `1–4` and says more exist. From 2a you already know `6` is
  a conventional product (no `d_code`) that moves real volume and prices like a
  diesel. So the load-bearing conclusion is **behavioral and data-proven**:
  *dropping `prod_cd = 6` removes a whole class of real fuel, which makes this
  query a **taxable-leaning** view, not a clean physical-volume total* (see the
  next box). The specific name ("dyed / off-road diesel, tax-exempt") is a
  reasonable hypothesis to confirm with a human — not something the rows prove.

> **Push the agent if it overclaims.** If it states "mode 8 = book adjustment" or
> "prod 6 = dyed diesel" as fact, ask: *"Show me the row that proves that."* It
> can't — and getting it to say *"I can't prove this from the data"* is the win.
> An honest "ask a human" beats a confident guess every time.

**The `prod_cd <> 6` finding — prove the behavior.** Dyed-or-not, `prod_cd = 6` is
real fuel that physically moved, and this query drops it. So a query labelled
"monthly volumes" is quietly measuring something narrower. Prove it from the data:

> With the `prod_cd <> 6` filter, this is the opaque query. **Without** it, you get
> all physical product. Run both for one terminal and show me the gap — then tell
> me whether "monthly volumes" is an honest label.

That gap is the headline: behavior labelled "volumes" actually behaves like
"taxable." **Note it as an open question for a human** ("should this be physical or
taxable?") — the data proves the discrepancy; it can't tell you which side is the
mistake.

**Checkpoint 2b:** For each of the three codes you can say *where your answer came
from* — `status` from the stale lookup read critically, `mode` from nowhere (a
flagged unknown), `prod` a data-proven behavioral finding plus a to-confirm label.

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
USE TEMP B-TREE FOR ORDER BY
```

(Two `TEMP B-TREE` lines are normal — one for the `GROUP BY`, one for the
`ORDER BY`. They're the aggregation and the sort, not the row lookup; only the
`SCAN`/`SEARCH` line is what we're about to change.) `SCAN lifts` means SQLite
reads **every one of the ~50,000 rows** and checks the
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
USE TEMP B-TREE FOR ORDER BY
```

`SCAN` became `SEARCH ... USING INDEX`. The engine now jumps to the August rows
instead of reading the whole table. (Both temp B-trees — GROUP BY and ORDER BY —
stay; they're the aggregation and the sort, expected. Only the first line
changed.)

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

## Step 4 — Don't trust the comments (10 min)

The query had no comments at all — you had to infer everything. Code with
*comments* has the opposite hazard: the comments can be confidently wrong. There's
a tiny desk helper in your repo, `sessions/session-3/retail_gas_report.py`, that
makes the point. It runs fine; its comments are another matter.

**Point the agent at it:**

> Read `sessions/session-3/retail_gas_report.py`. For each comment in
> `retail_gas_by_term`, tell me (a) what the line literally does, (b) what the
> comment claims, and (c) which one the data in `data/us_energy.sqlite` supports —
> run a query to settle each. Flag every place they disagree.

There are **three** gaps to catch — make the agent prove each from the rows:

| The comment says | What the line does | Settle it with the data |
|---|---|---|
| `# wholesale customers only (channel 1)` | keeps `channel_id == 1` | `SELECT * FROM channels;` → **1 = Branded Retail**. Channel 1 is *retail*; the comment names the wrong thing (the function is even called `retail_gas`). |
| `# all grades of gasoline (product codes 1 and 2)` | keeps only `prod_cd == 1` | The code never keeps `2` — and `2 = ULSD (clear diesel)`, not gasoline. The comment over-claims the set *and* misnames the product. |
| `# voided tickets are already filtered out upstream` | there is **no** status filter | `... WHERE channel_id=1 AND prod_cd=1 AND status=8 AND substr(lift_ts,1,7)='2025-08'` returns a non-zero count — voids are being summed. The comment claims a behavior the code doesn't have. |

**The method, in one line:** for each comment, ask *"if this line did what the
comment says, what would the data look like?"* — then check. Comments lie in two
directions: **naming the wrong thing** (lies 1–2) and **claiming a behavior that
isn't there** (lie 3). Catch both.

**Checkpoint 4:** You've caught all three comment/behaviour gaps, each with a
query that proves it. (This is the warm-up. Homework #2 runs the full version on a
real legacy script — `vol_report.py` — that ships with the homework brief.)

---

## If you have time — find the anomaly (stretch)

Back in Step 2a you grouped status values by size. Group the voids (`status = 8`)
by terminal and month instead, and look at the top:

> Among `status = 8` lifts, is any single terminal-and-month unusually high
> relative to the others? Quantify it: that terminal's void rate that month versus
> the dataset-wide void rate.

```sql
SELECT term_id, substr(lift_ts,1,7) AS ym, COUNT(*)
FROM lifts WHERE status = 8
GROUP BY term_id, ym ORDER BY COUNT(*) DESC LIMIT 5;
```

One terminal-month sticks out far above the rest. This is a **data-quality anomaly
to find, not be told** — exactly the kind of thing legacy comprehension surfaces.
Note what you find as an open question for a human ("why the spike?"), the way
you'd flag it on a real handoff.

**Not spotting it live is fine** — it's a bonus that rewards thorough profiling.

---

## Wrap-up (5 min)

**Your evidence ledger** — the one-glance summary of the lab. Where did each answer
come from? (Notice the last column is never empty.)

| Code | What the data alone showed | What the docs added | The human question |
|---|---|---|---|
| `status = 8` | undocumented status, ~8%, normal-sized ticket, an Aug cluster | stale lookup: void was `9` (now gone) ⇒ `8` is the live void | "why the GRB August void spike?" |
| `mode = 8` | small (~2%), cuts across products — not a transport category | docs cover only 1–4; nothing names `8` | **"what *is* mode 8?" — ask the feed owner** |
| `prod_cd = 6` | a real product (no d_code), real volume, dropped by the query | docs cover only 1–4; nothing names `6` | "is dropping it right — is this physical or taxable?" |

Quick reflection before we debrief:

1. For each magic value, **where did your answer come from** — the data, the
   (stale) lookup read critically, or "couldn't tell, ask a human"? Notice they
   weren't all the same.
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
| A data-only read | What the rows alone establish about `8`/`8`/`6` — and what they can't |
| A schema cross-check | Where the lookup/dictionary confirm, drift, or stay silent |
| Honest meanings | `status` (lookup, read critically), `mode` (unknown → human), `prod` (data-proven taxable-leaning finding + a label to confirm) |
| A faster, equivalent query | Non-sargable filter rewritten; index added; plan flipped SCAN → SEARCH |
| Comment-rot findings | Three lying comments in a helper script, caught against behaviour |

That's the comprehension move end to end: **read the data, cross-check the docs,
read the machine, distrust the comments — and know which answers you can't settle.**
Homework #2 runs the full version on `vol_report.py`.

---

## Appendix — Quick troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `sqlite3: command not found` | CLI not installed | Use the Python snippet in `../../data/README.md` — standard library, no installs. |
| In Step 2a the agent reads the dictionary anyway | It defaulted to the docs | Re-issue: *"Ignore `DATA-DICTIONARY.md` and `code_ref` for now. Use only queries against `lifts`. What can the rows alone tell us?"* |
| The agent states a meaning as fact ("mode 8 = book adjustment") | It's guessing past the evidence | *"Show me the row that proves it. If you can't, say so and flag it for a human."* |
| `EXPLAIN QUERY PLAN` still shows `SCAN` after you added the index | You left the `substr(...)` filter in place (non-sargable) | Rewrite the date filter to the half-open range first, *then* the index engages. |
| The agent "added an index" but didn't prove it | It asserted instead of showing | Make it paste the before/after `EXPLAIN QUERY PLAN`. The proof is the line flipping to `SEARCH`. |
| You're not sure the index changed the answer | Reasonable doubt — check it | Run the query before and after and diff. An index changes the plan, never the result. |
| You accidentally indexed and want a clean slate | — | `DROP INDEX IF EXISTS idx_lifts_ts;` — or just re-clone the `data/` folder. |
