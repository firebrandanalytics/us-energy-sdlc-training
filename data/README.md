# `data/` — the U.S. Energy course dataset

This folder holds the working dataset for Sessions 3–5: a small, self-contained
SQLite database of fuel **lifts** (terminal movements), renewable **RIN**
credits, and monthly **rack prices**. Everything runs locally — there are no
external services and nothing to install beyond `sqlite3` (and Python, which you
already have).

## What's in here

| File | What it is |
|---|---|
| `us_energy.sqlite` | The database (~50k rows in the `lifts` fact table). This is the file you query. |
| `DATA-DICTIONARY.md` | A working reference for the tables and the common codes. **Partial and slightly stale on purpose** — confirm anything important against the data itself. |
| `vol_report.py` | A legacy reporting script (see below). |
| `README.md` | This file. |

> The data is **synthetic** and generated for training. It is deterministic, so
> everyone in the class is looking at exactly the same rows.

---

## Opening the database

You can use any of these — pick whatever you're comfortable with.

### Option A — `sqlite3` command-line

From inside this `data/` folder:

```bash
sqlite3 us_energy.sqlite
```

Useful first commands once you're at the `sqlite>` prompt:

```sql
.tables                      -- list the tables
.schema lifts                -- see the full DDL for a table
.mode column                 -- nicer, aligned output
.headers on                  -- show column names
SELECT COUNT(*) FROM lifts;  -- ~50,000

-- peek at a few rows
SELECT * FROM lifts LIMIT 5;
```

Type `.quit` to exit.

> Tip: `.mode box` (or `.mode markdown`) gives cleaner output than the default
> pipe-delimited mode.

### Option B — Python (standard library, no installs)

```python
import sqlite3

con = sqlite3.connect("us_energy.sqlite")
con.row_factory = sqlite3.Row          # access columns by name
cur = con.cursor()

cur.execute("SELECT term_id, COUNT(*) AS n FROM lifts GROUP BY term_id ORDER BY n DESC")
for row in cur.fetchall():
    print(row["term_id"], row["n"])

con.close()
```

If you prefer dataframes and have pandas available:

```python
import sqlite3, pandas as pd

con = sqlite3.connect("us_energy.sqlite")
df = pd.read_sql_query("SELECT * FROM lifts LIMIT 1000", con)
print(df.head())
con.close()
```

> When you run a script that hard-codes the database name (like `vol_report.py`,
> below), run it from **inside this `data/` folder** so it can find
> `us_energy.sqlite`.

### Option C — a GUI

If you'd rather click around, any SQLite browser works. A common free one is
**DB Browser for SQLite** (<https://sqlitebrowser.org>): open the app, choose
**Open Database**, and point it at `us_energy.sqlite`. The **Browse Data** tab
lets you page through rows and the **Execute SQL** tab lets you run queries.
VS Code SQLite extensions and JetBrains DataGrip work too.

---

## The tables (quick map)

A realistic, lightly messy schema:

- `terminals`, `carriers`, `channels` — small dimension tables.
- `code_ref` — a small (and intentionally incomplete) lookup of what some of the
  numeric codes mean.
- `lifts` — the fact table: one row per fuel movement, with coded columns for
  transport mode, product, status, and more.
- `rin_transactions` — renewable credits linked back to individual lifts.
- `rack_prices` — monthly posted price per terminal and product.

Foreign keys connect them (`lifts.term_id → terminals.term_id`, and so on). See
`DATA-DICTIONARY.md` for the column-by-column reference — and remember that
dictionary is deliberately partial, so plan to verify against the data.

---

## About `vol_report.py`

`vol_report.py` is a **legacy reporting script** the energy desk has used to roll
up monthly volumes by terminal. It originated years ago for an older feed and has
been extended a few times since. It still runs:

```bash
# from inside this data/ folder
python vol_report.py 2025-08
```

It prints monthly physical and taxable volumes for the top terminals, plus a
RIN-eligible gallons figure. You'll be reading this script closely later in the
course — your job will be to figure out what it *actually* computes today and
whether its comments still tell the truth. For now, it's enough to know it exists
and that you can run it.

---

## Ground rule for the whole dataset

Column names are generic, several values are bare integer codes, and the
documentation here is intentionally incomplete. Throughout these sessions, treat
the **behavior of the code and the contents of the data as the source of
truth** — not the column names, not the comments, and not even this README.
