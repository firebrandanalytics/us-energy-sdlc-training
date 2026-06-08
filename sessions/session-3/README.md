# Session 3 — Reading What You Didn't Write

U.S. Energy AI Training · Session 3 of 5 · 2 hours, online

**Theme: using the agent to understand unfamiliar SQL, query plans, and a schema
that fights back.**

---

## Where this sits in the course

Sessions 1 and 2 built the mindset and the controls: you direct, the agent
executes, and you review its work like a junior engineer's. Today we point that
skill at the thing every engineer actually spends their days on —
**code and data someone else wrote, with no one left to ask.** Reading an
unfamiliar system and inferring what it really does is the most universal
developer skill there is; this session is that skill, with the agent doing the
reading and the data settling every claim.

This is the first session on the **running dataset** — a realistic U.S. Energy
fuel-movements database we'll use for the rest of the course. Over the next three
sessions you'll run a full arc on it: **comprehend** the legacy code and data
(today), **build a clean service** on it (Session 4), and **build a web dashboard**
on that service (Homework 3 + Session 5). Everything from here is hands-on against
real(istic) data and code.

The through-line from Session 1 carries straight in:

> **Infer intent, not just literal behavior. Treat the behavior of the code and
> the contents of the data as the source of truth — not the column names, not the
> comments, and not the lookup table.**

That stance is the whole point of this session. The dataset is built so you
*can't* solve it by reading column names: the codes are bare integers, one column
means two different things, and the lookup table is out of date — so some codes
can be cracked from the data, some only with the (stale) schema read critically,
and some you can't settle at all and must take to a human. (In your homework
you'll add the next layer: a legacy script whose comments describe what it used to
do, not what it does now.)

---

## What you'll be able to do by the end

- Point the agent at a query you didn't write and get back **what it does and why
  each filter is there** — the intent, not just a paraphrase.
- Reverse-engineer a **"magic value"** (a bare code like `status = 8`) from the
  data and a critically-read (stale) lookup — and recognise when a code **can't**
  be settled from what you have and needs a human.
- Read an **`EXPLAIN QUERY PLAN`**, recognise a slow full-table scan, and fix it
  with an index — with the agent explaining the plan in plain language.
- Catch a **lying comment** by checking the code's behavior against what it claims.
- Apply the basics of **working safely with real data**: scoped, read-only access
  and keeping credentials and sensitive data out of the agent's reach.

---

## Agenda (2 hours)

1. **Share-back from Homework #1** (~10 min) — a new command-line technique you
   learned from the agent: what it does, and when you'd use it.
2. **Meet the dataset** (~18 min) — a guided walk through the schema of the
   fuel-movements database (terminals, lifts, RIN credits) and how to open it.
3. **First pass, no agent** (~12 min) — read the opaque query yourself, then we
   compare what made it hard. (You appreciate the agent more for trying first.)
4. **What the query does** (~12 min) — bring in the agent for the literal read:
   the grain, the sums, and what each filter keeps and drops.
5. **Decode the magic values** (~22 min) — the heart of the session: figure out
   the bare codes **from the data first**, then cross-check the (stale) schema —
   and flag what neither can settle.
6. **Reading the machine** (~16 min) — `EXPLAIN QUERY PLAN`, spotting a full
   scan, and fixing it with an index.
7. **Don't trust the comments** (~10 min) — catch lying comments in a small
   script by checking each claim against the data.
8. **Working safely with real data** (~8 min) — scoping access; keeping
   connection strings and PII out of the agent; a quick secret-the-agent-never-sees demo.
9. **Wrap and Homework #2** (~10 min) — build an "intent dossier" for a legacy
   script: what it truly computes, and which comments are lying.

The hands-on **Exercise 1** runs from your first solo pass (beat 3) through the
comment hunt (beat 7): you decode an opaque query over the dataset — **data first,
schema second** — read its execution plan, and catch a lying comment. The
step-by-step is in **[`LAB-GUIDE.md`](LAB-GUIDE.md)** — start there when we reach
the lab.

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
- Come having done **Homework #1** (learn a command-line technique from the agent) — we open
  with a short share-back.

No need to study the data beforehand. Coming to it cold is part of the exercise.

---

## What's in this folder

| File | What it is |
|---|---|
| `README.md` | This file — the session overview. |
| `LAB-GUIDE.md` | The Exercise 1 walkthrough. Open it when we reach the lab. |
| `retail_gas_report.py` | A tiny helper with lying comments — you'll catch them in the lab's last step. |

The dataset itself lives in [`../../data/`](../../data/): the database
(`us_energy.sqlite`) and a deliberately partial data dictionary. The legacy script
you'll dissect for **Homework #2** ships *with the homework brief*, not in `data/` —
Session 3 is deliberately about reading the data on its own, with no script to lean on.

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

**Homework #2 — the intent dossier.** The brief includes a legacy script; you'll
save it as `data/vol_report.py`, then point Claude Code at it, work out what it
*truly* computes against the dataset, and document which of its comments are lying. The full brief is in
[`../../homework/homework-2-brief.md`](../../homework/homework-2-brief.md);
we hand it out at the end of the session.

---

## Looking ahead

Session 4 turns comprehension into construction: you'll take a vague stakeholder
request — *"give me clean monthly volumes by terminal"* — sharpen it into a real
spec, and build a clean **service** (a data layer something else can call). Then,
across Homework 3 and Session 5, you'll put a **web dashboard** on top of that
service. The intent dossier you build for homework is the raw material for the
service, so do it on the real script.
