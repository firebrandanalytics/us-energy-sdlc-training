# Lab Guide: Extend the Dashboard, and What's Next — Session 5

U.S. Energy AI Software-Development Training · Session 5 (120 min)

This is your reference for the session. The instructor walks the room through each
step live; this guide is here so you can keep moving if you fall behind, or pick
up from any step if you arrived late.

This is **Exercise 2, part 2** — you extend the dashboard you started in Homework 3
by **splitting the work across parallel agents** against your service's contract,
then make the result trustworthy.

---

## What you're building

A read-only **volumes dashboard**, grown from the one-table skeleton into something
you'd actually hand to the desk:

- the main view gains a **month filter** and a **simple bar chart**;
- a **terminal-detail page** (`/terminal/DAL`) shows one terminal across all months;
- a **JSON API** (`/api/volumes?month=2025-08`) exposes the same contract for any
  other consumer.

Every byte of it reads through the **service** you built in Session 4 — the app
never queries the database. That seam is what lets two agents build different parts
at the same time.

You'll do it in four moves:

1. **Confirm the contract** (~15 min) — pin the row shape the app and service meet
   at. This is the boundary your two subagents build against.
2. **Build in parallel with subagents** (~45 min) — one grows the main view;
   another adds the new routes; both against the contract. The main session
   integrates.
3. **Wire it together and verify end to end** (~25 min) — click through it,
   reconcile the numbers to Session 4, check the API.
4. **Make it trustworthy** (~20 min) — direct the agent to generate tests and a
   short README.

The final ~15 min is the art of the possible and the course close — no keyboard
needed for that part.

---

## Environment

You will work in **`sessions/session-5/`** (this folder). From here the committed
database is at **`../../data/us_energy.sqlite`** — the service already knows that
path.

### Set up — or catch up

If your Homework 3 dashboard is running, just activate it:

```bash
cd sessions/session-5
source venv/bin/activate            # the venv from Homework 3
uvicorn app:app --reload            # confirm it serves at http://localhost:8000
```

**If you didn't finish Homework 3, or it won't run — pull the starter. You will not
be left behind:**

```bash
cd sessions/session-5
cp -r starter/* .                   # app.py, service.py, templates/, static/, requirements.txt
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload            # http://localhost:8000 shows the one-view table
```

Either way, you start today with a running one-view dashboard. That's the baseline
everyone extends.

### Re-establish your reconciliation target

The numbers must still match Session 4's service after you extend the app. Keep the
legacy figure on screen as the anchor:

> `data/vol_report.py` is the script you created in Homework #2. If you don't have
> it, grab the listing from `homework/homework-2-brief.md` and save it to
> `data/vol_report.py` first — or just use the service figures below as your anchor.

```bash
( cd ../../data && python3 vol_report.py 2025-08 )   # DAL 1,517,103 / 1,371,642
python3 -c "import service; print(service.monthly_volumes('2025-08')[0])"
```

---

## Step 1 — Confirm the contract (15 min)

When you split work across two agents, the **only** thing they have to agree on is
the boundary between them. Here the boundary already exists: it's the shape of a row
your service returns and your app renders. Make it explicit before you grow either
side, so the two agents can't drift apart.

Open Claude Code in this folder and have it state the contract from your code:

```
Read service.py and app.py in this folder. I'm about to extend this dashboard by
splitting the work in two: one agent grows the main view (month filter + a chart),
another adds new routes (a terminal-detail page and a JSON API). Before either is
built, write the CONTRACT they both build against — the exact shape of one row the
service returns and the app consumes — as a short markdown block. Include:

- the row's fields, names and types (terminal, month, physical_gal, taxable_gal);
- what each measure means in one line (which gallons, which exclusions);
- the invariants a consumer can rely on (the ordering between physical and taxable,
  one row per terminal-month, terminal is real);
- the service functions that produce it: monthly_volumes(month) and months().

Keep it to something I can read in 30 seconds. Do not write code yet.
```

Read what it produces and tighten it. Your contract should pin at least:

- **The fields:** `terminal` (text), `month` (`YYYY-MM`), `physical_gal`,
  `taxable_gal` (integer gallons).
- **What each measure is:** physical = `SUM(net_gal)` over real movements; taxable
  = physical minus dyed off-road diesel (`prod_cd = 6`).
- **The invariants** — these are what make the split safe *and* what a test can
  check:
  - `physical_gal >= taxable_gal >= 0` (taxable is a *subset* of physical, so it can
    never exceed it — a great cheap check);
  - exactly **one row per (`terminal`, `month`)** — the grain;
  - every `terminal` resolves to a real terminal.
- **The functions:** `monthly_volumes(month=None)` and `months()`.

> **Why this is the whole game:** the contract is the interface. Once it's written,
> the main-view agent and the routes agent never have to talk to each other — they
> each just honor the contract. The app calls `service.monthly_volumes(...)`; the
> service guarantees the row shape. That's what makes the parallel split safe. (It's
> the same discipline as an API contract between a frontend and a backend — here you
> own both sides.)

Save the contract somewhere you can paste it (a `CONTRACT.md`, your notes,
anywhere). You'll hand it to both subagents next.

---

## Step 2 — Build in parallel with subagents (45 min)

Now split the work. Same Claude Code session — but you delegate the two halves to
subagents so they run side by side, and the main session integrates.

State the split clearly and hand both subagents the contract:

```
Use subagents to extend this dashboard in parallel. Both work against this CONTRACT
and must honor it exactly — the app always reads data via service.monthly_volumes()
and service.months(); neither subagent queries the database directly:

<paste your contract here>

- Subagent A — MAIN VIEW: extend the GET / route and its template so the user can
  (1) pick a month from a dropdown (use service.months() to populate it; default to
  the latest), and (2) see a simple horizontal bar per terminal showing physical
  volume relative to the largest that month. Pure CSS bars are fine — no JavaScript
  charting library. Keep the table; add the filter and the bars.

- Subagent B — NEW ROUTES: add two routes. (1) GET /terminal/{terminal} — an HTML
  page showing that one terminal's physical and taxable volumes across ALL months,
  ordered by month; link the terminal names in the main table to it. (2) GET
  /api/volumes?month=YYYY-MM — return the service rows as JSON (the contract, as a
  machine-readable endpoint). Both call the service; neither touches sqlite.

When both are done, integrate them in app.py and the templates, and report what each
subagent changed. Do not run yet — I'll review the diff first.
```

Approve actions as they come up. **`Ctrl+E` on anything you're not sure about** —
see the action before approving (Session 2 muscle). Auto-accept the obvious ones.

### What to watch for as the agents work

The disciplines from Sessions 3–5 come back here — keep an eye out and push back:

- **An agent queries the database directly** (you see `sqlite3.connect` in `app.py`
  or a template). That breaks the contract and the split. Send it back: *"read
  through `service.py`; the app doesn't know SQL."*
- **The two agents disagree on field names** — one writes `r.physical`, the service
  returns `physical_gal`. The contract exists to prevent exactly this. If it
  happens, that's the integration bug the contract was supposed to catch — point
  both at the contract's field names.
- **The chart math breaks on an empty month** (division by zero when no rows). A
  guard (`max(physical, default=1)`) is the fix.
- **`TemplateResponse` errors.** This FastAPI wants the **request first**:
  `templates.TemplateResponse(request, "name.html", {...})`. If you see a
  `TypeError` about an unhashable dict, that's the old argument order — flip it.
- **Subagents may run sequentially, not truly in parallel.** That's fine. The
  *work split against a contract* is the point; the parallelism is the bonus.

> Review the diff before you run it — the way you'd review a new engineer's PR. Use
> **C10**. It's much cheaper to catch "this template runs its own SQL" in the diff
> than to debug a divergent number later.

---

## Step 3 — Wire it together and verify end to end (25 min)

Now run it and prove it.

```bash
uvicorn app:app --reload
# open http://localhost:8000
```

Click through it like a user:

- [ ] The **month dropdown** changes the table and the bars.
- [ ] A terminal name **links** to `/terminal/<code>` and that page shows the
      terminal across months.
- [ ] `http://localhost:8000/api/volumes?month=2025-08` returns **JSON** rows.

### Reconcile — the verification that matters

A prettier page is worthless if the numbers drifted. Confirm the app still shows
exactly what the service computes and the legacy script reconciles to. For
**2025-08**, the top terminals must read:

| term | physical | taxable |
|---|---:|---:|
| DAL | 1,517,103 | 1,371,642 |
| OMA | 1,435,379 | 1,245,951 |
| APP | 1,367,376 | 1,264,810 |
| FAR | 1,339,984 | 1,198,102 |
| DSM | 1,323,169 | 1,207,528 |
| HOU | 1,282,704 | 1,165,897 |

Check it three ways and confirm they agree:

```bash
( cd ../../data && python3 vol_report.py 2025-08 )           # legacy target
python3 -c "import service; [print(r) for r in service.monthly_volumes('2025-08')[:6]]"   # the service
curl -s "http://localhost:8000/api/volumes?month=2025-08" | head    # the app's API
```

The legacy script, the service, and the app's JSON should tell the **same story**.
If the page shows different numbers than the service, an agent broke the contract
(usually by querying the DB itself, or summing the wrong column in a template).

### When something doesn't match

That's normal and it's the work. Read the disagreement with Claude Code:

- **The page number differs from the service:** the app stopped going through the
  service. Find where it queries the DB or recomputes, and route it back through
  `service.monthly_volumes()`.
- **A terminal page is empty:** the detail route is filtering by the wrong field or
  value — check it calls the service with no month and filters by `terminal`.
- **The API shape is off:** it's returning template strings or renamed fields
  instead of the contract dicts. Point at the contract.

> The whole point of routing everything through the service: the numbers were proven
> correct **once**, in Session 4, against the legacy script. As long as the app only
> ever reads through the service, it inherits that correctness for free. Verifying
> here is confirming you kept that discipline.

---

## Step 4 — Make it trustworthy (20 min)

A dashboard someone else can trust needs two things the agent is good at generating
once you've verified it works: **tests** and **documentation**.

### Tests that pin it

```bash
pip install pytest httpx     # httpx lets pytest drive the FastAPI app in-process
```

```
Write a pytest module for this dashboard. Use FastAPI's TestClient. Include at
least:
- a route test: GET /, GET /terminal/DAL, and GET /api/volumes?month=2025-08 all
  return 200;
- a reconciliation test: the /api/volumes?month=2025-08 JSON, for the top
  terminals, matches the Session 4 figures exactly — DAL 1,517,103 physical /
  1,371,642 taxable (derive these from vol_report.py / the service, not by copying
  the current API output);
- a contract test: for every row the API returns, physical_gal >= taxable_gal >= 0,
  and there is exactly one row per terminal for a given month.
Then tell me how to run them.
```

Then run them:

```bash
pytest -v
```

> **Why "derive expected values from the service, not the API output":** the easiest
> way to write a fake test is to hit the endpoint, see what it returns, and assert
> that. That test passes even when the app is wrong. Your reconciliation numbers
> come from Session 4 and the legacy script — anchor the tests to those.

### Documentation the next person can read

```
Write a short README for this dashboard (half a page): what it shows, that it reads
everything through service.py (and why the app never touches the database), how to
run it, the routes it exposes (/, /terminal/{code}, /api/volumes), and the
reconciliation result (the app's numbers match the Session 4 service / the legacy
vol_report.py for 2025-08). Keep it accurate to what the code actually does.
```

### Final review against the contract

Don't stop at "it ran and the tests are green." Run **C10** over the whole thing:

- [ ] Every view reads through **`service.py`**; no SQL in `app.py` or templates.
- [ ] The app's numbers **reconcile** to the Session 4 service for 2025-08.
- [ ] All three routes work (`/`, `/terminal/{code}`, `/api/volumes`).
- [ ] The JSON API returns the **contract** (the documented fields and types).
- [ ] `physical_gal >= taxable_gal` holds on every row (the chart and the data
      agree).
- [ ] The tests derive expected values from the service/legacy numbers, not from
      the current output.

---

## Pacing (rough markers from the start of the session)

| Elapsed | Where you should be |
|---:|---|
| 20 min | Homework 3 share-back done; contract confirmed |
| 40 min | Both subagents reporting done; integrating |
| 65 min | App runs; the three routes work; numbers reconcile or you're chasing a gap |
| 85 min | Tests green or close; reviewing against the contract |
| 105 min | Trustworthy: tests + README done; into the close |

If you fall behind: a dashboard with the **month filter and the detail page**,
reading through the service and reconciling, is a complete, shippable result. The
JSON API, the chart polish, and the tests can be finished asynchronously. A
dashboard whose numbers you trust beats ten that look slick and lie.

---

## Stretch goals (for fast finishers)

The room moves at different speeds — if you're ahead, pick one. Each is a small,
self-contained extension that uses something from the course:

- **A data-quality view.** Add a `/data-quality` page (or a banner on the main
  view) that flags any terminal-month whose **void rate** is abnormally high.
  There's a real one in this data — point the agent at the void column (`status =
  8`) and have it compute void rate by terminal for a month, flagging anything well
  above the ~8% baseline. (You'll find **GRB, 2025-08, ~18%**.) This is S3's "data
  is the source of truth" turned into a feature: the app *tells you* when a number
  is suspect.
- **A RIN column.** Add RIN credit gallons to the service (from the
  `rin_transactions` ledger, *not* the legacy flat `1.6` factor — that's the
  correction from Session 4's stretch) and surface it as a column. The contract
  grows by one field; the app renders it.
- **Sort or search.** Let the user sort the table by physical/taxable, or filter
  terminals by name. Pure server-side is fine.
- **A total row** — sum the column at the bottom of the table for the selected
  month. (Watch the contract: a totals row isn't a terminal — keep it out of the
  data and add it in the template.)
- **Make it real.** Add a `requirements.txt`, a one-paragraph "how to deploy this
  internally" note, and a `--check` style health route. Think about what it would
  take to actually run this for the desk.

Whatever you add, keep the discipline: **read through the service, honor the
contract, reconcile the numbers.**

---

## The art of the possible — where this earns its keep

(No keyboard for this part — watch and think about your own backlog.)

The loop you just ran end to end isn't a classroom toy. It's the workflow for the
work that actually piles up:

- **Internal tools, fast.** The read-only view over data you own that everyone asks
  you for and nobody has time to build. You just built one in two sessions.
- **Legacy comprehension** — the move from Session 3, on every undocumented script,
  query, and service you've inherited. *What does this really do, and which comments
  lie?*
- **Migrations** — extract the true rules from the old system, write the contract,
  build the new path against it, reconcile to the old numbers. Exactly what you did
  here, scaled to a real service or feed.
- **Splitting work that's actually parallel** — the contract-first split you ran
  today is how you put two agents (or two engineers) on one feature without them
  colliding.

And a quick look beyond the terminal — the same Claude Code shows up in more places
than the one we used all course:

- in the **terminal** (what we've used),
- in the **web app** (claude.ai),
- as **IDE extensions** (VS Code, JetBrains),
- on **remote / cloud machines** for long-running, server-side work,
- via **scheduled agents** that run on a clock.

Pick the corner that matches your workflow and explore it.

---

## What you'll take from this

The full loop, in order, is the course:

1. **Comprehend** — read the code and data you didn't write (Session 3).
2. **Scope and operate** — least-permission, the operator levers (Session 2).
3. **Sharpen the ask** — vague request to a spec with a contract (Session 4).
4. **Extract, plan, build the service** — lift the real rules, plan, build a clean
   data layer (Session 4).
5. **Build and scale the app** — a dashboard on the service, extended by parallel
   agents against the contract, verified and trustworthy (Homework 3 + today).

Not all five every time — but the moves are the same. Run a variant of this for the
next service, tool, or migration on your plate. Then own the outcome: review it,
calibrate your trust by the risk, and know when to let the agent run.
