# D2 — Query-Plan Cheat Sheet

U.S. Energy AI Training · Session 3 (Exercise 1) reference card

How to read `EXPLAIN QUERY PLAN`, recognise a slow full scan, and decide when an index actually helps. Every example here runs against `data/us_energy.sqlite` and produces the output shown.

---

## The 30-second version

1. Put `EXPLAIN QUERY PLAN` in front of any `SELECT`.
2. Read the plan top to bottom. **`SCAN` = reads every row. `SEARCH` = jumps to matching rows.**
3. `SCAN` on a big table (here that's `lifts`, ~50k rows) with a selective filter is the smell.
4. Add an index on the filtered column; re-run the plan; confirm `SCAN` became `SEARCH`.
5. Only then time it. The plan tells you *what* changed; a timing tells you *whether it mattered*.

---

## Reading a plan, line by line

A query plan is a short tree. Each line is a step. The words that carry the most signal:

| Plan keyword | What it means | Good or bad? |
|---|---|---|
| `SCAN <table>` | Read **every row** of the table | Fine on tiny dim tables; a red flag on `lifts` |
| `SEARCH <table> USING INDEX <name> (...)` | Use an index to **jump** to matching rows | What you want for a selective filter |
| `SEARCH <table> USING INTEGER PRIMARY KEY (rowid=?)` | Direct lookup by primary key | Best case — a point lookup |
| `USE TEMP B-TREE FOR ORDER BY` / `FOR GROUP BY` | Build a throwaway sort/group structure in memory | Often unavoidable; only worry if it dominates a large result |
| `USE TEMP B-TREE FOR DISTINCT` | Same, to de-duplicate | As above |
| `SCAN <table> USING COVERING INDEX <name>` | Read straight from the index, never touching the table | Excellent — the index alone answers the query |

> "Selective" = the filter keeps a small fraction of rows. A date filter that keeps one month out of twelve is selective; `status <> 8` (which keeps ~99% of rows) is not — an index won't help the latter.

---

## The worked example (Exercise 1)

A monthly-volume query over `lifts`, with the Exercise 1 filters:

```sql
EXPLAIN QUERY PLAN
SELECT term_id, SUM(net_gal)
FROM lifts
WHERE lift_ts >= '2025-08-01' AND lift_ts < '2025-09-01'
  AND status <> 8 AND mode <> 8 AND prod_cd <> 6
GROUP BY term_id;
```

### Before any index — the plan

```
SCAN lifts
USE TEMP B-TREE FOR GROUP BY
```

`SCAN lifts` means SQLite reads **all ~50,000 rows** and checks the date on each, even though only one month qualifies. There is no index on `lifts`, on purpose — this is the lesson.

### Add the index

```sql
CREATE INDEX idx_lifts_ts ON lifts(lift_ts);
```

### After the index — the plan

```
SEARCH lifts USING INDEX idx_lifts_ts (lift_ts>? AND lift_ts<?)
USE TEMP B-TREE FOR GROUP BY
```

`SCAN` became `SEARCH ... USING INDEX`. The engine now jumps straight to the August rows via the index instead of reading the whole table. (The `GROUP BY` temp B-tree stays — that's the aggregation, not the row lookup, and it's expected.)

> **Note for the lab:** the shipped database has **no** index by design, so your first plan will show `SCAN`. Adding the index is part of the exercise.

---

## When an index helps — and when it doesn't

An index pays off when **a selective filter** can use it. It does little or nothing otherwise.

**Helps:**
- A **date/range** filter that keeps a small slice — `lift_ts >= ... AND lift_ts < ...`. (This is the Exercise 1 win.)
- A **single-terminal** lookup — `WHERE term_id = 1`.
- A **combined** filter you run constantly — e.g. `(term_id, lift_ts)` for "this terminal, this month." A multi-column index on the columns you filter together, in the order you filter them.

**Doesn't help (or barely):**
- `status <> 8`, `mode <> 8`, `prod_cd <> 6` — **inequality filters that keep almost every row.** The engine still visits nearly everything, so an index just adds overhead. Keep these filters for *correctness*; don't expect them to speed anything up.
- A filter wrapped in a function — `WHERE substr(lift_ts,1,7) = '2025-08'` can't use a plain index on `lift_ts`. Rewrite as a half-open range (`>= '2025-08-01' AND < '2025-09-01'`) so the index applies.
- Tiny tables — indexing `terminals` (25 rows) or `channels` (3 rows) is pointless; a scan of 25 rows is already instant.

**Rule of thumb:** index the column(s) in the **selective** part of the `WHERE` (and in `JOIN`/`ORDER BY`/`GROUP BY` keys when those dominate). Leave the low-selectivity exclusion filters alone.

---

## Directing the agent on a query plan

Good prompts for Exercise 1 and beyond:

```
Run EXPLAIN QUERY PLAN on this query against data/us_energy.sqlite and
explain each line in plain English. Tell me which table is scanned and
roughly how many rows that is.
```

```
This plan shows SCAN lifts. Propose the single index most likely to turn
that into a SEARCH, write the CREATE INDEX statement, then re-run
EXPLAIN QUERY PLAN to prove the plan changed. Do not change the query's
results — only its plan.
```

```
Which of the WHERE filters in this query are selective enough to benefit
from an index, and which only affect correctness? Justify each from the
data (run a COUNT to back it up).
```

> **Review like a PR:** make the agent *show* the before-and-after plan, not just assert it added an index. The proof is the plan line flipping from `SCAN` to `SEARCH`. And confirm the index didn't change the **result set** — same rows, same totals, faster path.

---

## Quick checks you can run yourself

```sql
-- Is there an index on lifts yet?
SELECT name, sql FROM sqlite_master
WHERE type = 'index' AND tbl_name = 'lifts';

-- After CREATE INDEX, make SQLite gather stats so the planner chooses well
ANALYZE;

-- How selective is a filter, really? (low count = index-worthy)
SELECT COUNT(*) FROM lifts
WHERE lift_ts >= '2025-08-01' AND lift_ts < '2025-09-01';   -- one month
SELECT COUNT(*) FROM lifts WHERE status <> 8;                -- almost everything
```

---

> **One-line summary:** `SCAN` reads everything, `SEARCH` jumps; index the **selective** filter (the date range), leave the keep-almost-all exclusions alone, and prove the win by re-reading the plan.
