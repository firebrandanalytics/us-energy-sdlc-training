# Session 3 — Reading What You Didn't Write

U.S. Energy AI Training · Session 3 of 5 · 2 hours, online

**Theme: using the agent to understand unfamiliar SQL, query plans, and a schema
that fights back.**

---

## Where this sits in the course

Sessions 1 and 2 built the mindset and the controls: you direct, the agent
executes, and you review its work like a junior engineer's. Today we point that
skill at the thing data and integration teams actually spend their days on —
**code and data someone else wrote, with no one left to ask.**

This is the first session on the **running dataset** — a realistic U.S. Energy
fuel-movements database we'll use for the rest of the course. Everything from here
is hands-on against real(istic) data.

The through-line from Session 1 carries straight in:

> **Infer intent, not just literal behavior. Treat the behavior of the code and
> the contents of the data as the source of truth — not the column names, not the
> comments, and not the lookup table.**

That stance is the whole point of this session. The dataset is built so you
*can't* solve it by reading column names: the codes are bare integers, one column
means two different things, the lookup table is out of date, and a legacy script's
comments describe what it used to do, not what it does now.

---

## What you'll be able to do by the end

- Point the agent at a query you didn't write and get back **what it does and why
  each filter is there** — the intent, not just a paraphrase.
- Reverse-engineer a **"magic value"** (a bare code like `status = 8`) from the
  data when the lookup table is silent or wrong.
- Read an **`EXPLAIN QUERY PLAN`**, recognise a slow full-table scan, and fix it
  with an index — with the agent explaining the plan in plain language.
- Catch a **lying comment** by checking the code's behavior against what it claims.
- Apply the basics of **working safely with real data**: scoped, read-only access
  and keeping credentials and sensitive data out of the agent's reach.

---

## Agenda (2 hours)

1. **Share-back from Homework #1** (~10 min) — one win, one snag from running
   Claude Code on a real task.
2. **Meet the dataset** (~15 min) — a tour of the fuel-movements database
   (terminals, lifts, RIN credits) and how to open it.
3. **Comprehending a query you didn't write** (~25 min) — the agent explains
   *what* an opaque query does and, harder, *why* each magic filter is there.
4. **When the schema fights back** (~20 min) — generic column names and magic
   values; getting the agent to reverse-engineer their meaning from the data.
5. **Reading the machine** (~20 min) — `EXPLAIN QUERY PLAN`, spotting a full
   scan, and fixing it with an index.
6. **Don't trust the comments** (~10 min) — why stale comments lead you astray,
   and treating behavior as the source of truth.
7. **Working safely with real data** (~10 min) — scoping access; keeping
   connection strings and PII out of the agent.
8. **Wrap and Homework #2** (~10 min) — build an "intent dossier" for a legacy
   script: what it truly computes, and which comments are lying.

The hands-on **Exercise 1** runs through beats 3–6: you point the agent at an
opaque query over the dataset and have it explain the intent and the execution
plan. The step-by-step is in **[`LAB-GUIDE.md`](LAB-GUIDE.md)** — start there when
we reach the lab.

---

## Before the session

- Have **Claude Code** installed and launching. Today is hands-on.
- Have the **student repository cloned**, and confirm the sample database opens on
  your machine. We'll verify live, but it's smoother if you've checked first:

  ```bash
  # from the repo root
  sqlite3 data/us_energy.sqlite ".tables"
  ```

  You should see seven tables. If `sqlite3` isn't installed, the Python path in
  [`../../data/README.md`](../../data/README.md) works with no extra installs.
- Come having done **Homework #1** (run Claude Code on one real task) — we open
  with a short share-back.

No need to study the data beforehand. Coming to it cold is part of the exercise.

---

## What's in this folder

| File | What it is |
|---|---|
| `README.md` | This file — the session overview. |
| `LAB-GUIDE.md` | The Exercise 1 walkthrough. Open it when we reach the lab. |

The dataset itself lives in [`../../data/`](../../data/): the database
(`us_energy.sqlite`), a deliberately partial data dictionary, and the legacy
script (`vol_report.py`) you'll meet today and dissect for homework.

---

## Reference cards you'll want open

These are in [`../../handouts/`](../../handouts/). Pull them up as we go:

| Card | For |
|---|---|
| **D1 — Data Glossary** | Fuel-data terms (lift, mode, prod_cd, RIN/D-code, gross vs. net, dyed diesel) and the agentic terms you apply to data. Skim it before the lab. |
| **D2 — Query-Plan Cheat Sheet** | Reading `EXPLAIN QUERY PLAN`, spotting a `SCAN`, knowing when an index helps. Open during beat 5. |
| **D3 — Magic Values & Intent** | The method for decoding cryptic codes and distrusting comments. Open during beats 4 and 6. |
| **CC — Claude Code Commands Card** | The high-frequency commands and approval keys. Keep it handy every session. |

---

## Homework after this session

**Homework #2 — the intent dossier.** Point Claude Code at the legacy script
`data/vol_report.py`, work out what it *truly* computes against the dataset, and
document which of its comments are lying. The full brief is in
[`../../homework/homework-2-brief.md`](../../homework/homework-2-brief.md);
we hand it out at the end of the session.

---

## Looking ahead

Session 4 turns comprehension into construction: you'll take a vague stakeholder
request — *"give me clean monthly volumes by terminal"* — sharpen it into a real
data spec, and start building a pipeline. The intent dossier you build for
homework is the raw material for that session, so do it on the real script.
