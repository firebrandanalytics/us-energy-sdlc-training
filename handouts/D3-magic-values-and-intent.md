# D3 — Magic Values & Intent

U.S. Energy AI Training · Sessions 3–4 reference card

How to reverse-engineer cryptic codes, distrust comments, and recover **intent** when the schema fights back. This is the Session 1 skill — *infer what was meant, not just what is written* — applied to SQL and a crusty legacy script.

---

## The core stance

> **Code behavior and the data are the source of truth. Comments, column names, and lookup tables are hints — and hints lie.**

Three things mislead you in this dataset, all on purpose:

1. **Magic values** — bare integers (`mode`, `prod_cd`, `status`, `d_code`) whose meaning lives outside the database.
2. **Comments that lie** — the legacy `vol_report.py` (you build it in Homework #2) has comments that describe what the code *used to* do, or what someone *thought* it did.
3. **A partial, stale lookup** — `code_ref` documents the easy codes, omits the tricky ones, and carries an out-of-date row.

Your job is to treat all three as suspects and let the rows settle the argument. But be honest about reach: the **data shows you the structure and the anomalies**; a **critically-read (stale) schema names some of it**; and **some meanings the data simply can't settle** — those you take to a human. Knowing which bucket a value falls in is itself part of the skill. Sometimes the honest answer is *"this is an undocumented code; confirm it with a domain expert."*

---

## Part 1 — Reverse-engineering a magic value

You hit `WHERE status <> 8` (or `prod_cd = 6`, or `mode <> 8`) and have no idea what the number means. A repeatable method — **profile the data first, bring in the docs second, and be willing to end at "ask a human":**

**Step 1 — Profile the actual distribution first, with no docs.**
```sql
SELECT status, COUNT(*) FROM lifts GROUP BY status ORDER BY status;
```
You see `1`, `7`, and `8` in the data. Before reading any lookup, this already tells you the *structure*: which values exist, how common each is, whether the one in your filter is rare (looks like an exception/flag) or normal-sized (looks like an ordinary category). Establish what's there from the rows before anyone's documentation can bias you.

**Step 2 — Now bring in the lookup, and read it *critically*.**
```sql
SELECT * FROM code_ref WHERE code_type = 'status';
```
You'll find `1 = Open` and a `9 = Void (DEPRECATED ...)`. Cross it against Step 1: the data has `7` and `8`, the lookup documents `1` and `9`. So `9` is a ghost (documented, never used) and `7`/`8` are real but undocumented. A lookup that lists a value the data never uses — and omits values the data uses heavily — is **stale**; treat it as a partial, dated hint, not an answer. When the data and the lookup disagree, **the data wins** — but read the stale entry critically, because it can still *point* you (here, a deprecated "9 = void" with no 9 in the data hints that the live void code inherited that role).

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

**Step 5 — State the meaning and the intent — OR flag it as an open question.** When the rows (and a critically-read lookup) settle it, say what the filter is *for*, not just what the value is: *"`status <> 8` excludes voided/reversed tickets so the rollup counts only real transactions."* The meaning is the value; the intent is why someone filtered on it.

But sometimes the data shows you only structure and **nothing names the value** — not the rows, not the lookup, not a comment. Then the honest deliverable is *not* a confident meaning; it's: *"`mode = 8` is an undocumented code outside the 1–4 transport set; it is clearly not a physical transport mode, so a physical-volume figure should exclude it, but what it actually represents must be confirmed with a domain expert."* Naming what you **can't** settle from the data — and routing it to a human — is a correct outcome, not a failure. Don't let the agent (or yourself) manufacture certainty the evidence doesn't support.

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

The legacy `vol_report.py` (you build it from the Homework #2 brief) is the worked example for this. Its comments are a museum of how the script *used to* behave. The discipline: **read what the line does, then read what the comment claims, and flag every gap** — don't reach for this card as an answer key, because the whole exercise is recovering the answers yourself from the rows.

The *kinds* of comment-rot you should expect to catch (each is a pattern, not a specific answer — prove the real value from the data when you meet it):

- **The comment names the wrong code.** A filter excludes one integer; the comment cites a *different* one (often a deprecated value the data no longer uses). The code is right; the comment is a fossil.
- **The comment names the wrong concept.** A filter drops one category; the comment describes a *different* category entirely (e.g. claiming it drops one transport type when it actually drops a non-transport code). Some of these you'll be able to pin from the data; for an **undocumented code that nothing in the shipped artifacts names, the honest result is an open question for a human** — say so rather than adopting the comment's claim.
- **The comment describes behavior the code no longer performs.** A "scale these values up" note sitting above a line that does no scaling — a leftover from an earlier feed. The real intent is *none*; the comment is dead.
- **The comment narrows more than the code does.** A "<one product> only" comment above a filter that merely *excludes* one product and keeps everything else. The comment implies a whitelist; the code is a blacklist.
- **The comment is stale on scope.** A "<product X> only" comment above a filter that now includes *two* products, because a second was added later and the comment was never updated.

**How to read it:** for each filter, ask "if I deleted this line, which rows would change?" Then name those rows from the data. That is the true intent — and it is frequently *not* what the comment says. And where the data can't name the value at all, that's a finding to escalate, not a blank to fill with a guess.

---

## Part 4 — Putting it together (the intent dossier)

Homework #2 asks for an **intent dossier** on `vol_report.py` (you create the script from the listing in the Homework #2 brief when you start it). For each function and each filter, capture:

- **Literal behavior** — what the line does, mechanically.
- **Decoded values** — what each magic number means, backed by a query.
- **Stated vs. real intent** — what the comment claims vs. what the rows prove, and the gap between them.
- **Evidence** — the COUNT or sample query that settles it.
- **Open questions** — anything the data can't resolve (e.g. *why* the GRB voids spike in one month) to take to a human.

The agent drafts this fast. **You verify every claim against the database** — that verification *is* the skill.

---

## Directing the agent

*(The `vol_report.py` prompts below are for Homework #2 — you'll have created the script from the brief by then. The query-only prompts work anytime against `data/us_energy.sqlite`.)*

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
