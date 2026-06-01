# Handouts — Reference Cards

U.S. Energy AI Training · printable/scannable reference cards for the 5 × 2-hour course.

These cards are quick references, not lessons — pull the relevant one up during a session or while doing homework. The session READMEs and lab guides point to the specific card when you need it.

Two families live here:

- **C\*** — the **carry-over** cards from the original course. Tool- and practice-oriented (approval modes, model selection, the spec template, Microsoft 365, the review rubric, Claude Code commands). These are domain-neutral and stay useful as-is.
- **D\*** — the **new, data-oriented** cards for the U.S. Energy running dataset. They cover the fuel-data vocabulary, reading query plans, decoding magic values, and writing a data spec — the skills Sessions 3–5 are built on.

> **Why both?** The original cards were written around a web-app / fuel-tax example. The course you're taking is data-and-pipeline focused, so the **D\*** set replaces the *domain examples* while the **C\*** set keeps the *agentic practices* that don't change. Where a C\* card still uses the old domain in its examples (e.g. C1's IFTA/FastAPI entries, or trip/logbook examples), read past the example to the underlying practice — and reach for the matching **D\*** card for the data version.

---

## Carry-over cards (C\*) — use as-is

These six are the ones the course actively uses. They are tool/practice references and are not tied to the dataset.

| Card | What it's for | Used in |
|---|---|---|
| **C5 — Approval Mode Decision Matrix** | Choosing Manual vs. Auto vs. unsandboxed; when to switch | Session 2 |
| **C6 — Model Selection Cheat Sheet** | Picking Haiku / Sonnet / Opus by task; plan-vs-execute split | Session 2 |
| **C7 — AI-Ready Spec (Prompt) Template** | Turning any task into a structured spec the agent can execute | Sessions 2, 4 (general task spec) |
| **C9 — Microsoft Graph CLI Quick Reference** | Reaching email / Teams / SharePoint from Claude Code | Session 2 |
| **C10 — "What Good Looks Like" Review Rubric** | Reviewing AI-generated code before approving — correctness, hallucinated APIs, tests, security, scope | Sessions 4, 5 |
| **CC — Claude Code Commands Card** | The ~20 highest-frequency commands, shortcuts, and approval keys | Every session |

---

## New cards (D\*) — the data set

Written for the running dataset (`../data/us_energy.sqlite`) and the comprehension/build arc.

| Card | What it's for | Used in |
|---|---|---|
| **D1 — Data Glossary** | Fuel-data terms (lift, mode, prod_cd, RIN/D-code, gross vs. net, dyed diesel) **plus** the agentic terms you apply to data (query plan, intent dossier, data spec, grain, reconcile) | Sessions 3–5 |
| **D2 — Query-Plan Cheat Sheet** | Reading `EXPLAIN QUERY PLAN`, spotting a `SCAN`, and when an index turns it into a `SEARCH` | Session 3 (Exercise 1) |
| **D3 — Magic Values & Intent** | Reverse-engineering cryptic codes, handling an overloaded column, and distrusting comments — inferring intent from behavior + data | Sessions 3–4 |
| **D4 — Data Spec Template** | Pinning a data deliverable: grain, filters/exclusions, units (gross vs. net), edge cases, reconciliation | Session 4 (Exercise 2) |

---

## How C\* and D\* pair up

The new cards don't throw the old ones away — they extend them onto the data domain. Use them together:

| If you're doing… | Reach for the C\* card… | …alongside the D\* card |
|---|---|---|
| Writing a spec for a **data deliverable** | C7 (general spec structure) | **D4** (grain / filters / units / edge cases) |
| Looking up a **term** | C1 (course/tooling vocabulary) | **D1** (fuel-data + data-skill terms) |
| **Reviewing** an AI-built query or pipeline | C10 (review rubric) | **D2** (verify the plan), **D3** (verify intent vs. comments) |

> **Rule of thumb:** C7 + D4 is the combination for Session 4's "vague ask → spec." C10 + D2/D3 is the combination for reviewing what the agent produced in Sessions 4–5.

---

## Reference-only cards (C\*) — background, not actively used

These shipped with the original course and remain in the folder for reference. The course's data framing supersedes their examples; you won't be sent to them in a session, but they're here if you want the original treatment.

| Card | Note |
|---|---|
| **C1 — Course Glossary** | General course/tooling vocabulary. Some entries use the old domain (IFTA, FastAPI, Jinja2); for the data vocabulary use **D1**. |
| **C4 — `.env` in Practice** | Keeping secrets/paths out of source. Good general practice; revisit if you wire a `DB_PATH` for the dataset. |
| **C8 — "Make Correctness Easy" Checklist** | Baking correctness into the environment. General practice; examples use the trip/logbook app. |

---

## Conventions

- **Format:** each card opens with a one-line "what this is / when to use it," and most close with a one-line summary you can scan in seconds.
- **Paths:** the dataset is at `../data/us_energy.sqlite`; the legacy script students analyze is `../data/vol_report.py`. Every SQL example in the D\* cards runs against that database as-shipped.
- **Do not edit the C\* cards.** They are shared source. The D\* cards are the course-specific additions; suggest changes to the C\* set through the instructor.
