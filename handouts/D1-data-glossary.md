# D1 — Data Glossary

U.S. Energy AI Training · Quick reference for the **fuel-data** and **agentic** terms used in Sessions 3–5.
Two to three sentences per term. Scan when a word comes up in session and you want a fast definition.

This card covers the running dataset (`data/us_energy.sqlite`) and the agent skills you apply to it. For the broader course/tooling vocabulary (agent, approval mode, CLAUDE.md, planning mode, subagent, validate-and-correct loop, etc.), see **C1 — Course Glossary**.

---

## The dataset, at a glance

`data/us_energy.sqlite` models fuel **lifts** (terminal loadings/movements), the renewable-fuel credits they generate, and rack prices. One fact table, a handful of dimensions, foreign keys throughout. The numbers are synthetic but the *shapes* mirror a real fuel-distribution warehouse.

| Table | Grain (one row =) | Approx. rows |
|---|---|---|
| `lifts` | one fuel-movement ticket | ~50,000 |
| `rin_transactions` | one renewable-fuel credit tied to a lift | ~8,300 |
| `rack_prices` | one terminal × product × month price | ~2,100 |
| `terminals` | one loading terminal | 25 |
| `carriers` | one hauling company | 12 |
| `channels` | one sales channel | 3 |
| `code_ref` | one code-meaning lookup row (**partial / stale**) | 10 |

> The fact table is the only "big" one. When a query over `lifts` feels slow, that is the table to think about (see **D2**).

---

## Domain terms (fuel distribution & trading)

**Barge**
A river/marine vessel used to move fuel in bulk. In this dataset barge is **transport mode 4** — not to be confused with mode 8 (see *Book adjustment*). A comment in the legacy script claims it drops "barge"; read the code, it drops mode 8.

**Biodiesel**
A renewable diesel made from fats/oils (FAME), product code **9** here. Generates RIN credits; its blend/pathway tag lives in `custom_text1` (e.g. `OR-BD-1`).

**Blend grade**
For gasoline, how much ethanol is blended in: **E0** (none), **E10** (10%), **E15** (15%). Stored in `custom_text1` *for gasoline rows only* — that same column means something different for renewables (see *Overloaded column*).

**Book adjustment**
A non-physical accounting entry — a correction on the books, not fuel that actually moved. It is **transport mode 8**, and for *any* physical-volume question it must be **excluded**. This is the value the legacy script's "barge" comment is really filtering.

**Clear diesel (ULSD)**
Ultra-low-sulfur on-road diesel, product code **2**. It is taxable. Contrast with *dyed diesel*.

**Dyed diesel**
Off-road diesel dyed red to mark it as **tax-exempt**, product code **6**. It is real, physical fuel — so it counts in *physical* volume — but it is excluded from *taxable* volume. Getting this distinction wrong is the single most common volume error.

**Gross vs. net gallons**
`gross_gal` is the metered volume; `net_gal` is **temperature-corrected** to a 60°F standard. Fuel expands and contracts with temperature, so the same physical load reports a different gross depending on conditions. **Correct volume reporting uses `net_gal`.**

**LCFS pathway**
A Low Carbon Fuel Standard pathway identifier — a code (e.g. `CA-RD-T1`) describing the carbon-intensity certification of a renewable fuel. Stored in `custom_text1` *for renewable rows*, where gasoline would store a blend grade instead.

**Lift**
A single fuel-movement ticket: product X left terminal Y on carrier Z at a timestamp, with a volume and a status. The `lifts` table is the fact table — everything else describes or rolls up these rows.

**Mode (transport mode)**
How the fuel moved: **1** pipeline, **2** truck/rack, **3** rail, **4** barge, **8** book adjustment (non-physical). Modes 1–4 are physical; **8 must be excluded** from volume.

**Net gallons** — see *Gross vs. net gallons*.

**Product code (`prod_cd`)**
What the fuel is: **1** gasoline, **2** ULSD clear diesel, **3** NGL, **4** propane, **6** dyed diesel (off-road, tax-exempt), **7** renewable diesel, **9** biodiesel. Codes 6/7/9 are the ones the partial `code_ref` table leaves out.

**Rack price**
The posted wholesale price at a terminal "rack" for a product in a given month. Lives in `rack_prices`, keyed by terminal × product × month.

**Renewable diesel**
A drop-in renewable diesel (hydrotreated, not FAME), product code **7**. Generates RIN credits and carries an LCFS pathway in `custom_text1`.

**RIN (Renewable Identification Number)**
A tradable credit generated when a renewable fuel is produced/blended, used to demonstrate compliance with a renewable-volume obligation. In this dataset each eligible lift can spawn a row in `rin_transactions`.

**RIN D-code**
The category of a RIN, recorded in `d_code`. Renewable rows here carry **D4 or D7**; everything else is NULL. **Nesting matters:** a higher-value D-code can satisfy a lower obligation — a **D4 can be used against a D5 or D6 obligation**, but not vice versa.

**Status**
The lifecycle state of a lift: **1** open, **7** billed (a completed, real transaction — **keep**), **8** void/reversed (**exclude**). Note `code_ref` lists a stale "9 = void" that no longer matches the data.

**Terminal**
A facility where fuel is stored and loaded out. Identified by a short code (`term_cd`, e.g. `GRB` = Green Bay) and joined from `lifts` via `term_id`.

---

## "Magic value" terms (why this schema fights back)

**Magic value**
A bare integer in a column whose meaning lives **outside the database** — in someone's head, a wiki, or stale code. `mode`, `prod_cd`, `status`, and `d_code` are all magic-value columns. You cannot read intent from `WHERE status <> 8` without knowing what 8 means. **D3** is the method for recovering those meanings.

**Overloaded column**
One physical column that stores **different things depending on the row**. `custom_text1` is overloaded: it holds a gasoline *blend grade* on gasoline rows and an *LCFS pathway* on renewable rows. A query or pipeline that treats it as one consistent field will mis-handle half the data.

**Partial / stale lookup**
A reference table that documents *some* codes and is out of date on others. `code_ref` here documents the easy modes/products, **omits** the tricky codes (mode 8; products 6/7/9; statuses 7/8; all d_codes), and carries a **stale** `status 9 = void` line. Treat it as a hint, never as ground truth.

**Intent (vs. literal behavior)**
*What the author meant the code to accomplish*, as opposed to *what the characters on the line do*. The through-line of Sessions 3–5: infer intent from behavior + data, and never trust a comment or a lookup table over what the code and the rows actually do.

---

## Agentic terms you'll use on the data

**EXPLAIN QUERY PLAN**
A SQLite statement that shows *how* the engine will run a query — which tables it scans, which indexes it uses, whether it builds a temp structure. The fast way to see a full-table scan before it costs you. Full treatment in **D2**.

**Full scan (SCAN)**
The engine reading **every row** of a table to satisfy a query, because nothing lets it jump straight to the rows it needs. In a plan it shows as `SCAN <table>`. On `lifts` (~50k rows with no index) a date filter does exactly this.

**Index (and SEARCH)**
A side structure that lets the engine **jump** to matching rows instead of scanning all of them. After the right index exists, the plan line changes from `SCAN` to `SEARCH <table> USING INDEX ...`. Adding one is the fix in Exercise 1.

**Intent dossier**
The Homework #2 deliverable: a written account of what a legacy script (`data/vol_report.py`) *truly* computes, which of its comments are lying, and the decoded meaning of each magic filter. The agent drafts it from behavior; you verify it against the data.

**Data spec**
A precise statement of a data deliverable — its **grain**, **filters/exclusions**, **units**, and **edge cases** — written before any pipeline code. It turns a vague ask ("clean monthly volumes by terminal") into something the agent can build against and you can check. Template in **D4**.

**Grain**
The level of detail of one output row — e.g. "one row per terminal per month." Pinning the grain first is the highest-leverage line in any data spec; most "the numbers are wrong" bugs are really grain mismatches.

**Reconcile**
To check a new result against a trusted reference (here, the legacy `vol_report.py` numbers) and explain every difference — confirming each gap is a *correction* you intended, not an accident. The Homework #3 bar: match the legacy numbers, or improve on them *on purpose*.

---

> **One-line summary:** the dataset hides its meaning in magic codes, an overloaded text column, a partial lookup, and lying comments — D2 helps you read the machine, D3 helps you decode the values, D4 helps you pin the deliverable.
