# Extra Credit: Extend the Dashboard with Parallel Agents

**Self-paced. For after your loop is closed** — PR merged, tickets closed,
Homework 3's one-table dashboard running. This was originally planned as the
Session 5 group lab; it works just as well solo, and the ambitious version of
you that's reading this is exactly who it was written for. Budget roughly **90
minutes** end to end, in four moves of ~15/~40/~20/~15 — or do one move per
coffee break across a week. Pair it with handout **C11 — Advanced Claude Code**:
the parallel split you run by hand here is the gateway to the orchestration
features described there.

---

## What you're building

A read-only **volumes dashboard**, grown from Homework 3's one-table skeleton
into something you'd actually hand to the desk:

- the main view gains a **month filter** and a **simple bar chart**;
- a **terminal-detail page** (`/terminal/DAL`) shows one terminal across all months;
- a **JSON API** (`/api/volumes?month=2025-08`) exposes the same contract for any
  other consumer.

Every byte of it reads through the **service** you built in Session 4 — the app
never queries the database. That seam is what lets two agents build different
parts *at the same time* without colliding.

---

## Environment

Work where Homework 3 left you: **`sessions/session-5/`** of the course repo,
with *your* `service.py` copied in and `app.py` serving one table. Catching up
from zero:

```bash
cd sessions/session-5                       # in the course repo
cp ../../../<initials>-volume-service/service.py ./service.py   # YOUR service
cp -r starter/* . 2>/dev/null || true       # the one-table skeleton, if you don't have your own
python3 -m pip install fastapi uvicorn jinja2 pytest httpx
# (if pip says "externally-managed-environment", add: --user --break-system-packages)
export DB_PATH=../../data/us_energy.sqlite  # your service reads this — set it once per shell
uvicorn app:app --reload                    # http://localhost:8000 shows the table
```

> **Keep what you build:** this folder is scratch space in the course clone.
> When you're happy with the result, copy the dashboard files into your own
> repo (`cp -r app.py templates static test_app.py ../../../<initials>-volume-service/dashboard/`),
> commit it there — on a story branch, against your dashboard stories, the way
> you now do these things.

### Re-establish your reconciliation anchor

The numbers must still match your Session 4 service after every extension:

```bash
( cd ../../data && python3 vol_report.py 2025-08 )   # DAL 1,517,103 / 1,371,642
python3 -c "import service; print(service.monthly_volumes('2025-08')[0])"
```

---

## Move 1 — Confirm the contract (~15 min)

When you split work across two agents, the **only** thing they have to agree on
is the boundary between them. Here the boundary already exists: the shape of a
row your service returns and your app renders. Make it explicit before you grow
either side, so the two agents can't drift apart.

In Claude Code (this folder):

```
Read service.py and app.py. I'm about to extend this dashboard by splitting the
work in two: one agent grows the main view (month filter + a chart), another
adds new routes (a terminal-detail page and a JSON API). Before either is built,
write the CONTRACT they both build against — the exact shape of one row the
service returns and the app consumes — as a short markdown block. Include:

- the row's fields, names and types (terminal, month, physical_gal, taxable_gal,
  lift_count);
- what each measure means in one line (which gallons, which exclusions);
- the invariants a consumer can rely on;
- the service functions that produce it: monthly_volumes(month=None) and months().

Keep it to something I can read in 30 seconds. Do not write code yet.
```

Read what it produces and tighten it. Your contract should pin at least:

- **The fields:** `terminal` (text), `month` (`YYYY-MM`), `physical_gal`,
  `taxable_gal` (integer gallons), `lift_count` (int — the Session 4 change
  request, now part of the contract).
- **What each measure is:** physical = `SUM(net_gal)` over real movements;
  taxable = physical minus dyed off-road diesel (`prod_cd = 6`).
- **The invariants** — what makes the split safe *and* what a test can check:
  - `physical_gal >= taxable_gal >= 0` (taxable is a *subset* of physical);
  - exactly **one row per (`terminal`, `month`)** — the grain;
  - every `terminal` resolves to a real terminal;
  - `lift_count >= 1` on every emitted row.
- **The functions:** `monthly_volumes(month=None)` and `months()`.

> **Why this is the whole game:** the contract is the interface. Once it's
> written, the main-view agent and the routes agent never have to talk to each
> other — they each just honor the contract. That's what makes the parallel
> split safe. (It's the same discipline as an API contract between a frontend
> and a backend — here you own both sides.)

Save it as `CONTRACT.md`. You hand it to both subagents next.

---

## Move 2 — Build in parallel with subagents (~40 min)

Now split the work. Same Claude Code session — but you delegate the two halves
to subagents so they run side by side, and the main session integrates.

```
Use subagents to extend this dashboard in parallel. Both work against this
CONTRACT and must honor it exactly — the app always reads data via
service.monthly_volumes() and service.months(); neither subagent queries the
database directly:

<paste your CONTRACT.md>

- Subagent A — MAIN VIEW: extend the GET / route and its template so the user
  can (1) pick a month from a dropdown (use service.months() to populate it;
  default to the latest), and (2) see a simple horizontal bar per terminal
  showing physical volume relative to the largest that month. Pure CSS bars —
  no JavaScript charting library. Keep the table; add the filter and the bars.

- Subagent B — NEW ROUTES: add two routes. (1) GET /terminal/{terminal} — an
  HTML page showing that one terminal's physical and taxable volumes across ALL
  months, ordered by month; link the terminal names in the main table to it.
  (2) GET /api/volumes?month=YYYY-MM — return the service rows as JSON (the
  contract, as a machine-readable endpoint). Both call the service; neither
  touches sqlite.

When both are done, integrate them in app.py and the templates, and report what
each subagent changed. Do not run yet — I'll review the diff first.
```

Review the diff before you run it — the way you'd review a teammate's PR (C10).

### What to watch for as the agents work

- **An agent queries the database directly** (`sqlite3.connect` in `app.py` or
  a template). That breaks the contract *and* the split. Send it back: *"read
  through service.py; the app doesn't know SQL."*
- **The two agents disagree on field names** — one writes `r.physical`, the
  service returns `physical_gal`. The contract exists to prevent exactly this;
  point both at its field names.
- **The chart math breaks on an empty month** (division by zero when no rows).
  A guard (`max(values, default=1)`) is the fix.
- **`TemplateResponse` errors.** This FastAPI wants the **request first**:
  `templates.TemplateResponse(request, "name.html", {...})`.
- **Subagents may run sequentially, not truly in parallel.** Fine. The *work
  split against a contract* is the point; the parallelism is the bonus.

---

## Move 3 — Wire it together and verify end to end (~20 min)

```bash
uvicorn app:app --reload
```

Click through it like a user:

- [ ] The **month dropdown** changes the table and the bars.
- [ ] A terminal name **links** to `/terminal/<code>` and that page shows the
      terminal across months.
- [ ] `http://localhost:8000/api/volumes?month=2025-08` returns **JSON** rows.

### Reconcile — the verification that matters

A prettier page is worthless if the numbers drifted. For **2025-08** the top
terminals must still read:

| term | physical | taxable |
|---|---:|---:|
| DAL | 1,517,103 | 1,371,642 |
| OMA | 1,435,379 | 1,245,951 |
| APP | 1,367,376 | 1,264,810 |

Check three ways and confirm they tell the same story:

```bash
( cd ../../data && python3 vol_report.py 2025-08 )                  # legacy target
python3 -c "import service; [print(r) for r in service.monthly_volumes('2025-08')[:3]]"
curl -s "http://localhost:8000/api/volumes?month=2025-08" | head    # the app's API
```

If the page disagrees with the service, an agent broke the contract — usually
by querying the DB itself or recomputing in a template. The numbers were proven
correct **once**, in Session 4; as long as the app only reads through the
service, it inherits that correctness for free.

---

## Move 4 — Make it trustworthy (~15 min)

```
Write a pytest module (test_app.py) for this dashboard using FastAPI's
TestClient. Include at least:
- a route test: GET /, GET /terminal/DAL, and GET /api/volumes?month=2025-08
  all return 200;
- a reconciliation test: the /api/volumes?month=2025-08 JSON matches the
  Session 4 anchors exactly — DAL 1,517,103 physical / 1,371,642 taxable —
  derived from the service, NOT copied from the current API output;
- a contract test: every API row honors the invariants (physical_gal >=
  taxable_gal >= 0, lift_count >= 1, one row per terminal for a month).
Then a short README: what it shows, why the app never touches the database,
how to run it, the routes, and the reconciliation result.
```

`pytest -v`, then read the tests with the usual question: *could these pass
while the app is wrong?*

> **Why "derive expected values from the service, not the API output":** the
> easiest fake test hits the endpoint, sees what comes back, and asserts that.
> It passes even when the app lies. Anchor tests to numbers proven elsewhere.

---

## Stretch goals — pick what's interesting

- **A data-quality view.** A `/data-quality` page (or banner) flagging any
  terminal-month whose **void rate** is well above the ~8% baseline — point the
  agent at `status = 8` by terminal-month. There's a real one in this data
  (GRB, 2025-08, ~18%). Session 3's "the data is the source of truth," turned
  into a feature that *tells you* when a number is suspect.
- **A RIN column.** Add RIN credit gallons to the service — from the
  `rin_transactions` ledger, *not* the legacy flat `1.6` factor (Session 4's
  stretch correction). The contract grows by one field, tests first; the app
  renders it.
- **Sort, search, or a total row.** Server-side is fine. (A totals row isn't a
  terminal — keep it out of the data, add it in the template.)
- **Make it real.** `requirements.txt`, a health route, a one-paragraph "how
  we'd deploy this internally" note.
- **Test it like a user.** Your `test_app.py` never opened a browser — nothing
  proves the chart renders, the dropdown filters, or the DAL link lands where
  it should. How would you check those the way a user would? That's browser
  automation: Playwright, written and run by the agent as plain test code, or
  wired in via MCP — **C11 §5**, including the idea it leads to (one
  natural-language test plan, executed against the API *or* the GUI).
- **Then go meta — C11.** Re-run Move 2 as a `/agents`-defined reviewer, or put
  the reconcile check on a schedule. The handout has the map.

Whatever you add, keep the discipline: **read through the service, honor the
contract, reconcile the numbers.**

---

## Where this pattern earns its keep

The contract-first parallel split you just ran is how you put two agents — or
two engineers — on one feature without collisions. The same shape covers the
backlog that never gets staffed: the internal read-only tool everyone asks for,
the legacy script that needs a trustworthy successor (extract the real rules,
contract, build, reconcile — exactly Sessions 3→4, scaled up), the migration
where old and new must agree to the gallon. None of it needed the classroom.
