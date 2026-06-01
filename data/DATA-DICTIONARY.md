# Data Dictionary — `us_energy.sqlite`

> Working reference for the U.S. Energy fuel-movements dataset.
>
> **Status: partial.** This file documents the tables and the codes we use most
> often. It was last touched a while ago and a few of the lookup tables in the
> database have drifted since — so treat this as a *starting point*, not gospel.
> When the data disagrees with this document, **the data wins.** Confirm anything
> load-bearing against `code_ref` and against the actual values in `lifts`.

The database models fuel **lifts** (terminal liftings / movements), the renewable
**RIN** credits some lifts generate, and monthly **rack prices**. There are three
small dimension tables (`terminals`, `carriers`, `channels`), one small lookup
table (`code_ref`), and one large fact table (`lifts`, ~50k rows).

---

## Tables at a glance

| Table | Grain | Rows (approx) | Notes |
|---|---|---|---|
| `terminals` | one row per terminal | 25 | dimension |
| `carriers` | one row per carrier | 12 | dimension |
| `channels` | one row per sales channel | 3 | dimension |
| `code_ref` | one row per (code_type, code_val) | small | **partial** lookup of code meanings |
| `lifts` | one row per lift / movement | ~50,000 | the fact table |
| `rin_transactions` | one row per RIN credit | ~8,000 | child of `lifts` |
| `rack_prices` | terminal × product × month | ~2,100 | monthly posted rack price |

---

## `terminals`

| Column | Type | Meaning |
|---|---|---|
| `term_id` | INTEGER PK | surrogate key, referenced by `lifts.term_id` and `rack_prices.term_id` |
| `term_cd` | TEXT (unique) | short terminal code, e.g. `GRB`, `HOU`, `ORD` |
| `name` | TEXT | display name, e.g. "Green Bay Terminal" |
| `state` | TEXT | two-letter state |
| `region` | TEXT | sales/operating region |

## `carriers`

| Column | Type | Meaning |
|---|---|---|
| `carrier_id` | INTEGER PK | surrogate key, referenced by `lifts.carrier_id` |
| `carrier_cd` | TEXT (unique) | short carrier code, e.g. `CR01` |
| `name` | TEXT | carrier display name |

## `channels`

| Column | Type | Meaning |
|---|---|---|
| `channel_id` | INTEGER PK | surrogate key, referenced by `lifts.channel_id` |
| `channel_cd` | TEXT (unique) | `RET`, `COM`, `WHL` |
| `name` | TEXT | Branded Retail / Commercial Fleet / Wholesale Supply |

---

## `lifts` (fact table)

One row per fuel lift / movement. This is where the real work — and the real
ambiguity — lives. Several columns are integer **codes** whose meanings are *not*
stored in the row; see the code sections below and `code_ref`.

| Column | Type | Meaning |
|---|---|---|
| `lift_id` | INTEGER PK | surrogate key |
| `lift_ts` | TEXT (NOT NULL) | timestamp, `YYYY-MM-DD HH:MM:SS`. There is **no index** on this column. |
| `term_id` | INTEGER FK | → `terminals.term_id` |
| `carrier_id` | INTEGER FK | → `carriers.carrier_id` |
| `channel_id` | INTEGER FK | → `channels.channel_id` |
| `mode` | INTEGER | transport mode — see **Mode codes** |
| `prod_cd` | INTEGER | product — see **Product codes** |
| `d_code` | INTEGER (nullable) | RIN "D-code" for renewable products; NULL for non-renewables |
| `gross_gal` | REAL (NOT NULL) | gross gallons (as measured) |
| `net_gal` | REAL (NOT NULL) | net gallons (temperature-corrected) |
| `custom_text1` | TEXT (nullable) | free-text tag — meaning **depends on the product** (see below) |
| `status` | INTEGER | record status — see **Status codes** |

### Gross vs. net gallons

`gross_gal` is volume as measured at the rack; `net_gal` is the same volume
**temperature-corrected** to a standard reference temperature. For most
reporting the net figure is the right one — confirm which your task needs.

### Mode codes (`lifts.mode`)

| Code | Meaning |
|---|---|
| 1 | Pipeline |
| 2 | Truck / Rack |
| 3 | Rail |
| 4 | Barge |

> Other `mode` values exist in the data beyond the four above. If you hit one
> that isn't in this table, don't assume — investigate it before you include or
> exclude those rows.

### Product codes (`lifts.prod_cd`)

| Code | Meaning |
|---|---|
| 1 | Gasoline |
| 2 | ULSD (clear / on-road diesel) |
| 3 | Natural gas liquids (NGL) |
| 4 | Propane |

> The product codes above are the common ones. The dataset contains additional
> `prod_cd` values (renewable and specialty products) that are **not** documented
> here yet. Decode anything unfamiliar from the values themselves before treating
> a number as final.

### Status codes (`lifts.status`)

| Code | Meaning |
|---|---|
| 1 | Open |
| 9 | Void / reversed |

> Heads-up: the void/reversal convention has changed over the life of this
> system. The line above reflects the **older** scheme. Check what value voided
> records actually carry in *this* dataset before you rely on it for an exclusion.

### `custom_text1` (overloaded free-text)

This single column carries **different meanings for different products**:

- For **gasoline**, it records the **blend grade** (e.g. `E10`, `E15`, `E0`).
- For **renewable** products, it records a **regulatory pathway identifier**
  (e.g. an LCFS pathway code) rather than a blend grade.

Because the same column is reused, never interpret `custom_text1` without first
checking the row's `prod_cd`.

---

## `rin_transactions`

Renewable Identification Number (RIN) credits generated by renewable lifts.
Each row is the child of a lift.

| Column | Type | Meaning |
|---|---|---|
| `rin_id` | INTEGER PK | surrogate key |
| `lift_id` | INTEGER FK | → `lifts.lift_id` (the lift that generated the credit) |
| `d_code` | INTEGER (NOT NULL) | RIN D-code for this credit |
| `rin_qty` | REAL | RIN quantity (credit gallons after the equivalence factor) |
| `equiv_value` | REAL | equivalence value applied to convert physical gallons to RIN gallons |
| `status` | INTEGER | record status |

> RIN accounting has its own rules (D-codes, equivalence values, and how one
> category can satisfy another). This table is included so you can join lifts to
> the credits they generate; the credit *rules* are out of scope for this
> dictionary.

---

## `rack_prices`

Monthly posted rack price per terminal and product.

| Column | Type | Meaning |
|---|---|---|
| `price_id` | INTEGER PK | surrogate key |
| `term_id` | INTEGER FK | → `terminals.term_id` |
| `prod_cd` | INTEGER | product (same code set as `lifts.prod_cd`) |
| `price_month` | TEXT | `YYYY-MM` |
| `rack_price` | REAL | posted rack price for that terminal/product/month |

---

## Using this with `code_ref`

`code_ref` is a small in-database lookup of code meanings
(`code_type`, `code_val`, `meaning`). It is **deliberately incomplete** and, in
at least one place, **out of date** relative to the current data. Use it as a
convenience, cross-check it against this document, and where the two disagree,
verify against the actual `lifts` rows. Reverse-engineering the codes the lookup
*doesn't* cover is part of the exercise.
