# Homework #3 — Finish a Pipeline Slice and Prove It Against the Legacy Numbers

**Assigned after:** Session 4 (From Vague Ask to Working Pipeline)
**Due before:** Session 5
**Time budget:** 45–60 minutes

---

## The Assignment

In Session 4 you sharpened the vague ask into a data spec and started a clean
`pipeline.py` that replaces the legacy `data/vol_report.py`. Most people left with
**physical volume** working and reconciling.

For this homework you finish one more **slice** of the pipeline and — the part a
classroom can't rush — write a **test that proves your number is right**: that it
matches the legacy figure, *or* correctly improves on it for a reason you can
state. The test is the deliverable. A number you can defend with a passing test is
worth ten that "look about right."

Work in `sessions/session-4/` against `../../data/us_energy.sqlite`, continuing the
pipeline you started in class.

---

## Pick Your Slice

Choose **one** measure to finish and prove (or do both if you have time):

- **Taxable volume.** Physical minus tax-exempt dyed off-road diesel
  (`prod_cd = 6`), keeping everything else. This one **must reconcile exactly** to
  the legacy number — the legacy script is correct on taxable, even though its
  "clear diesel only" comment lies about how.
- **RIN credit gallons.** This is the *interesting* one. The legacy
  `rin_eligible_gallons` multiplies every renewable gallon by a flat `RVO = 1.6`.
  Your Homework 2 dossier almost certainly flagged that constant — the data implies
  a **per-product** equivalence (renewable diesel and biodiesel are not the same).
  So your RIN number should **not** match the legacy figure: it should *correctly
  improve on it*. Pull the credit gallons from the `rin_transactions` ledger rather
  than re-multiplying by a constant, and let your test assert the improvement.

If you didn't get physical fully reconciling in class, finishing **physical** is a
legitimate slice too — just make sure your test pins it against the legacy number.

---

## What to Produce

### 1. The finished slice in `pipeline.py`

Extend your pipeline so the chosen measure is computed correctly, to your spec.
Keep the disciplines from class:

- Name the magic values — no bare `6` / `8` in the SQL.
- Sum **`net_gal`**, not `gross_gal`.
- Bound the month with a **range predicate**, not `substr(lift_ts, 1, 7)`.
- State which exclusions apply to which measure (they differ).

### 2. A reconciliation test

Write a test — `pytest` is fine, or a plain `assert` script if your team can't run
pytest — that compares your pipeline's output to the legacy `vol_report.py` for a
known month (use **2025-08**) and **fails loudly** if they disagree in a way you
didn't intend.

Two shapes, depending on your slice:

- **A "must match" test** (physical, taxable): assert your number equals the legacy
  number for the top terminals.
- **A "correctly improves" test** (RIN): assert your number is the *corrected*
  figure and is **not** the legacy figure — and leave a comment saying why.

A minimal skeleton to adapt (it imports your pipeline and shells out to the legacy
script — wire it to whatever interface your `pipeline.py` actually exposes):

```python
# test_reconcile.py  —  run from sessions/session-4/
import sqlite3, subprocess, sys
import pipeline   # your module from Session 4

DB = "../../data/us_energy.sqlite"

# Legacy top-6 physical / taxable for 2025-08 (from `python vol_report.py 2025-08`
# run inside data/). These are the numbers your slice reconciles against.
LEGACY_2025_08 = {
    "DAL": (1_517_103, 1_371_642), "OMA": (1_435_379, 1_245_951),
    "APP": (1_367_376, 1_264_810), "FAR": (1_339_984, 1_198_102),
    "DSM": (1_323_169, 1_207_528), "HOU": (1_282_704, 1_165_897),
}

def test_taxable_matches_legacy():
    con = sqlite3.connect(DB)
    rows = {r.term_cd: r for r in pipeline.build(con, "2025-08")}   # adapt to your API
    con.close()
    for term, (phys, tax) in LEGACY_2025_08.items():
        assert round(rows[term].taxable_gal) == tax, f"{term} taxable diverged"

def test_rin_correctly_improves_on_legacy():
    # Legacy uses a flat RVO = 1.6 and reports 8,906,150 for 2025-08.
    # The corrected figure (per-product equivalence, from rin_transactions) is
    # 9,077,485. Our pipeline should produce the corrected number, NOT the legacy one.
    con = sqlite3.connect(DB)
    rin_total = round(sum(r.rin_gal for r in pipeline.build(con, "2025-08")))
    con.close()
    assert rin_total != 8_906_150, "still reproducing the stale 1.6 constant"
    assert rin_total == 9_077_485, "RIN does not match the corrected ledger figure"
```

> You don't have to use these exact numbers blindly — **regenerate them yourself**.
> Run `python vol_report.py 2025-08` from inside `data/` for the legacy figures,
> and query `rin_transactions` for the corrected RIN total. The point of the
> homework is that *you* establish the ground truth and pin it.

### 3. A one-line note next to any intended difference

Wherever your number deviates from the legacy script on purpose (the RIN case),
write a single line — in the test or in `pipeline.py` — saying what the correction
is and why. An undocumented gap is a bug; a documented one is an improvement.

---

## The Standout Move — Make the Test Catch a Real Regression

After your test passes, **break the pipeline on purpose** and confirm the test
fails:

- Swap `net_gal` for `gross_gal` and watch the "must match" test go red.
- Or drop the `prod_cd = 6` exclusion from taxable and watch the taxable test fail.
- Or restore the flat `1.6` factor and watch the RIN test catch it.

Then put it back. A test that never fails isn't proving anything. Seeing it fail
on the exact mistake it's meant to catch is how you know it's load-bearing — and
it's the difference between "I think it's right" and "I can prove it's right."

---

## Reflection — Bring These to Session 5

After you finish, write short answers to these four prompts:

1. **Which slice did you finish, and does it reconcile?** Match exactly, or
   improve-with-a-reason? State the number and the legacy number.
2. **What did writing the test surface?** Did pinning the expected number force a
   decision you'd left fuzzy?
3. **Did your test actually catch the broken version?** Which mistake did you
   inject, and did it go red?
4. **One failure or frustration** — a moment where the agent was confidently
   wrong, reproduced the legacy bug, or led you somewhere you had to back out of.

Keep each answer to two or three sentences. You're capturing the experience while
it's fresh, not writing a report.

---

## What to Bring to Session 5

- Your extended `pipeline.py` and your reconciliation test.
- Your four reflection answers.

Session 5 opens with the share-back, then scales the rest of the pipeline across
parallel agents working against your spec as a shared contract. The cleaner your
slice and the sharper your spec, the more the parallel build just works.

You don't need slides — just be ready to say, in two minutes, which slice you
finished, whether it matched or improved, and what your test caught.

---

*Reference: the spec template is **D4 — Data Spec Template**; the review discipline
is **C10 — Review Rubric**. The pipeline and spec you started are from the Session
4 lab guide. Questions? Session 5 opens with the share-back.*
