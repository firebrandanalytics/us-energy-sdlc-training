# D3 — Magic Values & Intent

U.S. Energy AI Training · Sessions 3–4 reference card

How to reverse-engineer cryptic codes, distrust comments, and recover **intent** when the schema fights back. This is the Session 1 skill — *infer what was meant, not just what is written* — applied to SQL and a crusty legacy script.

---

## The core stance

> **Code behavior and the data are the source of truth. Comments, column names, and lookup tables are hints — and hints lie.**

Three things mislead you in this dataset, all on purpose:

1. **Magic values** — bare integers (`mode`, `prod_cd`, `status`, `d_code`) whose meaning lives outside the database.
2. **Comments that lie** — `data/vol_report.py` has comments that describe what the code *used to* do, or what someone *thought* it did.
3. **A partial, stale lookup** — `code_ref` documents the easy codes, omits the tricky ones, and carries an out-of-date row.

Your job is to treat all three as suspects and let the rows settle the argument.

---

## Part 1 — Reverse-engineering a magic value

You hit `WHERE status <> 8` (or `prod_cd = 6`, or `mode <> 8`) and have no idea what the number means. A repeatable method:

**Step 1 — Check the lookup, but don't trust it.**
```sql
SELECT * FROM code_ref WHERE code_type = 'status';
```
You'll find `1 = Open` and a `9 = Void (DEPRECATED ...)`. Notice what's **missing**: there is no row for `8`. A code the data uses heavily but the lookup never mentions is a flashing sign that the lookup is stale.

**Step 2 — Profile the actual distribution.**
```sql
SELECT status, COUNT(*) FROM lifts GROUP BY status ORDER BY status;
```
You see `1`, `7`, and `8` in the data — but the lookup only documents `1` and `9`. So `9` is a ghost (documented, never used) and `7`/`8` are real but undocumented. The data and the lookup disagree; **the data wins.**

**Step 3 — Compare the populations.** Look at rows *with* the value against rows *without* it and find what's systematically different.
```sql
-- Do status-8 rows behave like reversals/voids?
SELECT status, COUNT(*), ROUND(AVG(net_gal),1) AS avg_net
FROM lifts GROUP BY status;
-- Are status-8 rows clustered anywhere suspicious?
SELECT term_id, substr(lift_ts,1,7) AS ym, COUNT(*)
FROM lifts WHERE status = 8
GROUP BY term_id, ym ORDER BY COUNT(*) DESC LIMIT 5;
```
A status that clusters in one terminal-month, or pairs up with offsetting volumes, behaves like **void/reversed** — which is exactly what `status = 8` is here. (Watch for one terminal-month that spikes far above the rest — that pattern is a story worth asking about.)

**Step 4 — Cross-check against an external anchor.** A magic value rarely lives alone. Tie it to something you *can* read:
```sql
-- d_code only appears on renewable products -> it's a RIN category, not a generic flag
SELECT prod_cd, d_code, COUNT(*) FROM lifts GROUP BY prod_cd, d_code ORDER BY prod_cd;
```
When `d_code` is non-NULL **only** for products 7 and 9 (the renewables), you've learned both that `d_code` is a renewable-fuel concept *and* which product codes are renewable — two meanings recovered from one query.

**Step 5 — State the meaning AND the intent.** Don't stop at "8 = void." Say what the filter is *for*: *"`status <> 8` excludes voided/reversed tickets so the rollup counts only real transactions."* The meaning is the value; the intent is why someone filtered on it.

---

## Part 2 — The overloaded column

`custom_text1` holds **different things on different rows**. Profile it *by the column that disambiguates it*:

```sql
SELECT prod_cd, custom_text1, COUNT(*)
FROM lifts WHERE custom_text1 IS NOT NULL
GROUP BY prod_cd, custom_text1 ORDER BY prod_cd;
```

You'll see, e.g., `E0/E10/E15` on gasoline (prod 1) and `CA-RD-T1..3` / `OR-BD-1..2` on renewables (prod 7, 9). Same column, two meanings: **blend grade** for gasoline, **LCFS pathway** for renewables. Any code that reads `custom_text1` as one consistent field is wrong for half the rows. The tell for an overloaded column: its distinct values fall into clean groups that line up with *another* column.

---

## Part 3 — Don't trust the comments

`data/vol_report.py` is the worked example. Its comments are a museum of how the script *used to* behave. The discipline: **read what the line does, then read what the comment claims, and flag every gap.**

| What the comment says | What the code actually does | The real intent |
|---|---|---|
| `# skip test + voided tickets (status 9)` | filters `status == 8` | Exclude **voids**; the live void code is **8**, not the 9 the comment names |
| `# barge loads are reconciled upstream ... drop them` (on `mode == 8`) | filters `mode == 8` | Drop **book adjustments** (non-physical). Barge is mode **4** and is *not* dropped — the comment names the wrong thing entirely |
| `# gallons in this feed are stored in hundreds -- scale up` | `g = gal` (no scaling) | **None** — the scaling was removed; the comment is a fossil. (`RVO = 1.6` is likewise a leftover, applied only in the RIN path.) |
| `# clear diesel only` (before `if prod == 6: continue`) | drops `prod == 6`, keeps everything else | Drop **dyed/off-road** diesel from *taxable* volume. It does **not** keep "clear diesel only" — gasoline, NGL, etc. are all still counted |
| `# renewable diesel only (prod 7)` | adds **both** `prod == 7` **and** `prod == 9` | Include renewable diesel **and biodiesel**; biodiesel was added later and the comment was never updated |

**How to read it:** for each filter, ask "if I deleted this line, which rows would change?" Then name those rows from the data. That is the true intent — and it is frequently *not* what the comment says.

---

## Part 4 — Putting it together (the intent dossier)

Homework #2 asks for an **intent dossier** on `vol_report.py`. For each function and each filter, capture:

- **Literal behavior** — what the line does, mechanically.
- **Decoded values** — what each magic number means, backed by a query.
- **Stated vs. real intent** — what the comment claims vs. what the rows prove, and the gap between them.
- **Evidence** — the COUNT or sample query that settles it.
- **Open questions** — anything the data can't resolve (e.g. *why* the GRB voids spike in one month) to take to a human.

The agent drafts this fast. **You verify every claim against the database** — that verification *is* the skill.

---

## Directing the agent

```
Don't trust the comments in data/vol_report.py. For each filter, tell me
(a) what the line literally does, (b) what the comment claims, and
(c) which one the data supports — run a query against
data/us_energy.sqlite to back up your answer.
```

```
The column lifts.custom_text1 looks overloaded. Profile its distinct
values grouped by prod_cd and tell me what it means for each product
family. Cite the row counts.
```

```
status = 8 is undocumented in code_ref. Figure out what it means from
the data: distribution, average volume, and any clustering by terminal
and month. State both the meaning and why a query would filter it out.
```

> **The trap to avoid:** the agent will happily *repeat the comment back to you* as if it were fact, because comments read like authority. Always ask it to **prove the claim from the rows.** A meaning without a query behind it is a guess.

---

> **One-line summary:** profile the data, compare populations, and tie each magic value to an anchor — then read every comment as a *claim to be checked*, never a fact, because in this schema the comments lie and the lookup is stale.
