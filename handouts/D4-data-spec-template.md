# D4 — Data Spec Template

U.S. Energy AI Training · Session 4 (Exercise 2) reference card

Copy this template. Fill in every section before you let the agent build a pipeline or write a query. Delete sections that genuinely don't apply — but be honest, because for data work nearly all of them do.

This is the **data-deliverable** companion to **C7 — AI-Ready Spec**. C7 frames a general engineering task; D4 frames a dataset/pipeline output. Use C7's structure for the surrounding work (constraints, anti-goals, acceptance criteria, files to read) and D4 for the four things that decide whether the numbers are right: **grain, filters, units, edge cases.**

---

## Why this template exists

A request like *"give me clean monthly volumes by terminal"* sounds clear and is not buildable. Clean how? Monthly by what timestamp? Which gallons — metered or temperature-corrected? Does a voided ticket count? Does dyed off-road diesel? Does a non-physical book adjustment?

Every one of those is a decision that changes the number. If you don't make the decision, the agent will — silently, from training-data defaults — and you'll get a confident, wrong answer that *runs*. This template forces the decisions into the open before any code exists.

> **The discipline:** if you can't fill in **Grain** and **Filters / Exclusions** precisely, the ask is still vague. Sharpen those two first; the rest follows.

---

## The template

```
## Deliverable
<!-- One or two sentences. What is the output and who consumes it?
     "A monthly physical and taxable volume rollup by terminal, for the energy desk."
     Name the output shape: a table? a CSV? a function returning a dict? -->

## Grain
<!-- The level of one output row. Be exact.
     "One row per terminal per calendar month."
     If there are multiple measures per row (physical AND taxable gallons),
     say so here. Grain mismatches are the #1 cause of "the numbers are wrong." -->

## Source(s)
<!-- Which tables/files, and how they join.
     "lifts (fact), joined to terminals on term_id for the terminal code."
     Note the grain of the source too — one row per lift ticket. -->

## Measures
<!-- What you are summing/counting, and the exact column.
     "Physical volume = SUM(net_gal). Taxable volume = SUM(net_gal) over the
     taxable subset." Name the column explicitly (net_gal, not 'gallons'). -->

## Units
<!-- The unit decision, stated, with the reason.
     "Gallons, temperature-corrected: use net_gal, NOT gross_gal, because
     volume reporting standardises to 60°F."
     If any legacy scaling factor exists, say whether it applies (here: it
     does NOT — the 'stored in hundreds' scale-up comment is dead code; sum
     gallons as-is). -->

## Filters / Exclusions
<!-- Every row that must be dropped, and WHY (the intent, not just the code).
     - Exclude status = 8 (void/reversed) -> count only real transactions.
     - Exclude mode = 8 (book adjustment, non-physical — the S3 open question,
       since confirmed with the feed owner) -> physical volume only.
     - For TAXABLE only: also exclude prod_cd = 6 (dyed/off-road, tax-exempt).
     State which filters apply to which measure -- they differ here. -->

## Dimensions / Grouping
<!-- The GROUP BY. "Group by term_id and month (substr(lift_ts,1,7) or a
     half-open date range). Resolve term_id -> term_cd for display." -->

## Time handling
<!-- Which timestamp defines the period, and the boundary rule.
     "Month = the lift_ts month. Use a half-open range
     [first-of-month, first-of-next-month) so an index can be used and no
     row is double-counted at the boundary." -->

## Edge cases
<!-- The rows that break naive code. Spell out the expected handling.
     - A terminal with zero qualifying lifts in a month: omit, or emit 0?
     - NULL custom_text1 / NULL d_code: expected for non-renewables — not an error.
     - The overloaded custom_text1 (blend grade vs LCFS pathway): if you read
       it, branch on prod_cd.
     - A terminal-month with an unusual void cluster: flag for review, don't
       silently absorb it. -->

## Acceptance criteria
<!-- Verifiable pass/fail statements, derived from the spec — not from output.
     - Physical volume excludes all status=8 and mode=8 rows.
     - Taxable volume additionally excludes all prod_cd=6 rows.
     - Volumes use net_gal.
     - Output has exactly one row per terminal per month present in the data.
     - Result reconciles to vol_report.py for a known month, OR every
       difference is an intended correction with a one-line reason. -->

## Reconciliation / source of truth
<!-- What you check against, and how to treat differences.
     "Compare to data/vol_report.py for 2025-08. Any difference must be a
     KNOWN correction (e.g. fixing the dyed-diesel exclusion), documented —
     never an unexplained gap." -->

## Anti-goals
<!-- What this deliverable explicitly does NOT do.
     - No pricing/revenue join (rack_prices) in this version.
     - No RIN credit calculation here — separate deliverable.
     - No charting/dashboard — a clean table/CSV is the output. -->

## Definition of done
<!-- One statement. "All acceptance criteria pass, the pipeline runs against
     the course database (from your Session-4 repo: ../us-energy-sdlc-training/data/us_energy.sqlite) producing correct physical and taxable monthly
     volumes by terminal, reconciliation to the legacy numbers is explained,
     and I've reviewed the output against this spec — not just that it ran." -->
```

---

## Worked example — the Session 4 ask

**Before (the vague ask):**
> Give me clean monthly volumes by terminal.

**After (a fillable data spec):**

> **Deliverable:** A monthly volume rollup by terminal for the energy desk — physical and taxable gallons — as a table written to CSV.
>
> **Grain:** One row per terminal per calendar month, with two measures (physical, taxable).
>
> **Source(s):** `lifts` (fact, ~50k rows), joined to `terminals` on `term_id` for the display code.
>
> **Measures:** Physical = `SUM(net_gal)` over qualifying rows. Taxable = `SUM(net_gal)` over the taxable subset.
>
> **Units:** Gallons, temperature-corrected — `net_gal`, not `gross_gal`. No legacy scaling (the "stored in hundreds" scale-up comment is dead code, do not apply it). The `RVO` constant is a different problem — it's live code in the RIN measure with a stale value; if you build RIN, take the factors from the `rin_transactions` ledger instead.
>
> **Filters / Exclusions:**
> - Both measures: exclude `status = 8` (void/reversed) and `mode = 8` (book adjustment, non-physical).
> - Taxable only: additionally exclude `prod_cd = 6` (dyed off-road diesel, tax-exempt). Physical volume **keeps** dyed diesel — it is real fuel that moved.
>
> **Dimensions / Grouping:** Group by `term_id` and month; resolve `term_id` → `term_cd` for output.
>
> **Time handling:** Month = the `lift_ts` month, via a half-open range `[YYYY-MM-01, next-month-01)` so an index applies and no boundary row is double-counted.
>
> **Edge cases:** Terminal-months with no qualifying lifts are omitted (not emitted as 0). NULL `d_code`/`custom_text1` on non-renewables is expected, not an error. A terminal-month with an abnormal void count (e.g. one terminal spiking in one month) is flagged for review, not silently absorbed.
>
> **Acceptance criteria:**
> - Physical excludes every `status=8` and `mode=8` row; taxable also excludes every `prod_cd=6` row.
> - Both measures use `net_gal`.
> - Exactly one output row per terminal per month present in the data.
> - Reconciles to `vol_report.py` for `2025-08`, or each difference is a documented, intended correction.
>
> **Reconciliation:** Compare to `data/vol_report.py` for `2025-08`. Differences are acceptable only as known corrections (e.g. correctly excluding dyed diesel from taxable), each with a one-line reason.
>
> **Anti-goals:** No `rack_prices`/revenue join; no RIN calculation; no dashboard — a clean CSV is the deliverable.
>
> **Definition of done:** All acceptance criteria pass; the pipeline runs against the course database (path configurable — `DB_PATH`); reconciliation to the legacy numbers is explained; I've reviewed the output against this spec.

---

## Quick-fill tips

- **Grain and Filters first.** They decide the number. If those two aren't crisp, nothing downstream can be.
- **Filters differ per measure — say so.** Physical and taxable share two exclusions but diverge on dyed diesel. A spec that states one filter set for "the volume" hides that divergence and the agent will pick one.
- **Name the exact column, never "gallons."** `net_gal` vs `gross_gal` is a real decision with a real number behind it. "Gallons" lets the agent choose.
- **Write intent next to every exclusion.** "Exclude `mode=8` (book adjustment, non-physical)" travels; "exclude `mode=8`" is a magic number the next reader has to re-derive.
- **Make reconciliation a pass/fail line.** "Matches the legacy numbers, or every difference is an intended correction with a reason" turns *correctness* into something you can actually check (see **C10 — Review Rubric**).

---

> **One-line summary:** pin the **grain**, list every **filter** with its intent, name the exact **unit** column, enumerate the **edge cases**, and make reconciliation a checkable line — then hand it to the agent.
