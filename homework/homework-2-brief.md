# Homework #2 — Build an Intent Dossier for `vol_report.py`

**Assigned after:** Session 3
**Due before:** Session 4
**Time budget:** 45–60 minutes

---

## The Assignment

In Session 3 you ran the comprehension move on an opaque *query*. Now run the full
version on an opaque *script*.

`data/vol_report.py` is a legacy reporting script the energy desk relies on. It
runs. It reconciles "to within rounding" to an old AS/400 job. And it is **full of
comments — several of which lie.** Your job is to produce an **intent dossier**:
a written account of what the script *truly* computes against the dataset, the
decoded meaning of every magic value it filters on, and exactly which comments no
longer tell the truth.

The agent will draft this fast. **You verify every claim against the database.**
That verification is the homework — a meaning, or an "intent," with no query
behind it is a guess, and this script is built to punish guesses.

> The through-line, one more time: **the behavior of the code and the contents of
> the data are the source of truth — not the comments, not the column names, not
> the lookup table.**

---

## Setup

- Work at the **repo root** in a Claude Code session (so the agent can read both
  `data/vol_report.py` and `data/us_energy.sqlite`).
- Confirm the script runs, so you have its real output to anchor against:

  ```bash
  # from inside the data/ folder (the script hard-codes the db name)
  cd data
  python vol_report.py 2025-08
  ```

  It prints physical and taxable volumes for the top terminals plus a
  RIN-eligible gallons figure. Keep that output — you'll check claims against it.
- Have **D3 (Magic Values & Intent)** open. It is the method for this whole
  assignment. **D1** (glossary) and **D2** (query plans) are useful backup.

---

## What to Produce — The Intent Dossier

Work through the script **function by function** (`load`, `physical_by_term`,
`taxable_by_term`, `rin_eligible_gallons`) and the module-level constants. For each
function, capture five things:

**1. Literal behavior.** What the function does, mechanically — its inputs, what it
filters, what it returns. No interpretation yet.

> Prompt idea: *"Read `data/vol_report.py`. For `physical_by_term`, describe
> literally what it computes — what it filters in and out, and what one entry in
> its result represents. Don't interpret the comments yet; just the code."*

**2. Decoded magic values.** Every bare integer the function filters on
(`status`, `mode`, `prod_cd`, …), decoded **from the data** — not from `code_ref`
or the data dictionary, both of which are deliberately incomplete. Back each decode
with the query you ran.

> Prompt idea: *"This function filters on `status`, `mode`, and `prod_cd`. Decode
> each value it tests against by profiling `data/us_energy.sqlite`. Check whether
> `code_ref` even covers them, then prove each meaning from the rows."*

**3. Stated vs. real intent.** For each filter and each comment: what the comment
*claims*, what the code *actually does*, and the **gap** between them. Name every
lie. (There are several. Some comments name the wrong code; at least one describes
behavior the script no longer performs.)

> Prompt idea: *"Don't trust the comments. For each filter, tell me (a) what the
> line literally does, (b) what the comment claims, and (c) which one the data
> supports — run a query to settle it. Flag every place they disagree."*

**4. Evidence.** The `COUNT`, sample, or comparison query that settles each claim.
A dossier without queries is just a paraphrase of the comments — exactly what we're
trying to get past.

**5. Open questions.** Anything the data **can't** resolve — take it to a human.
(For example: if a number looks off, is the constant wrong, or is the report
*meant* to be approximate? The data can show the discrepancy; it can't always tell
you which side is the mistake.)

---

## The Standout Move — Find Where the Script Is Quietly Wrong

Most of this script *behaves* correctly — credit that. But not all of it. One of
its outputs **does not match the data**, because of a stale constant that nobody
updated.

Compare the script's `RIN-eligible gallons` figure to what the dataset's own
renewable-credit records say it should be. Decode the equivalence factor the
script applies, then find the equivalence values actually stored in the data and
check whether they agree.

> Prompt idea: *"`vol_report.py` reports a RIN-eligible gallons number using a
> constant. Find that constant and what it's multiplied against. Then compute the
> equivalent figure from the `rin_transactions` table in `data/us_energy.sqlite`.
> Do they match? If not, explain precisely why — which number is faithful to the
> data, and what the script got wrong."*

Note in your dossier: **which number is right, which is stale, and by how much.**
This is the difference between "the script runs" and "the script is correct" —
and it's the kind of thing that hides for years because nothing visibly breaks.

> Separate "lying comment" from "wrong behavior." Most of the comments are wrong
> while the code is right; the RIN constant is the opposite — flag both kinds, and
> don't over-correct the parts that are actually fine.

---

## Reflection — Bring These to Session 4

After you finish, write short answers to these four prompts:

1. **How accurate was the AI's reconstruction?** Where did it correctly decode a
   value or catch a lying comment, and where did it go astray — or repeat a
   comment back to you as if it were fact?
2. **What did verifying against the data reveal?** Name one claim that only held
   up — or only fell apart — once you ran the query.
3. **How did your guidance change what the AI produced?** What would the dossier
   have gotten wrong if you'd just let the agent summarise the script's comments?
4. **One failure or frustration** — a moment the AI was confidently wrong,
   unhelpfully vague, or sent you down a path you had to back out of.

Keep each answer to two or three sentences. You're capturing the experience while
it's fresh, not writing a report.

---

## What to Bring to Session 4

- Your **intent dossier** (the five-part write-up, with the queries that back it).
- Your **reflection** answers.

We'll hear from a few people at the start of Session 4. Bring the real dossier —
rough edges and open questions included. The places where the comments lied and
the data set you straight are exactly where the interesting discussion is.

This dossier is not throwaway: Session 4 takes the rules you extracted here and
turns them into a clean data spec and the start of a pipeline. The better you
understand what `vol_report.py` *truly* does, the easier that build will be.

---

## Tips

- **Run the script first, then read it.** Having the real output in front of you
  turns every claim into something you can check, not just believe.
- **Make the agent prove it from the rows.** The single highest-value habit. When
  it states a meaning, ask for the query. Comments read like authority; the rows
  are the authority.
- **Don't stop at "8 = void."** State the *intent*: *"excludes voided tickets so
  the rollup counts only real transactions."* The meaning is the value; the intent
  is why someone filtered on it.
- **It's fine to use Claude Code to draft the dossier itself.** Describe the
  structure, let it draft, then correct it against the data. The corrections are
  the valuable part — they're where your judgment shows up.

---

*Reference cards: **D3** (magic values & intent — the method), **D1** (data
glossary), **D2** (query plans). Questions? Session 4 opens with the share-back.*
