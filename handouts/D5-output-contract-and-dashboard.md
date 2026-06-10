# D5 — Output Contract & Dashboard

A reference card for the back half of the course: how to give a service a clear
**output contract**, and how to stand up a minimal **FastAPI dashboard** that
consumes it. Used in Session 4 (write the contract), Homework 3 (build the
skeleton), and Session 5 (extend it with parallel agents).

---

## Part 1 — The output contract

### What it is

The **output contract** is the shape of one row your service returns — field names,
types, and the guarantees a caller can rely on. It is the seam between the thing
that *produces* data (your `service.py`) and the things that *consume* it (a CLI, a
test, a web page, another teammate's code).

A one-off script doesn't need one — its output dies in a `print()`. A **service**
does, because something else reads it. Write the contract down *before* you build
on top, and the producer and consumer can evolve independently — even at the same
time, in parallel, by two different agents.

### The contract for our volumes service

```
One output row =
  terminal      str    terminal display code, e.g. "DAL"
  month         str    "YYYY-MM"
  physical_gal  int    SUM(net_gal) over real movements
  taxable_gal   int    physical minus dyed off-road diesel (prod_cd 6)
  lift_count    int    qualifying tickets behind the totals
                       (added by the Session-4 change request)

Functions that produce it:
  monthly_volumes(month=None) -> list[row]   # one month, or all months
  months()                    -> list[str]   # every "YYYY-MM" present

Invariants a consumer can rely on:
  1. physical_gal >= taxable_gal >= 0     (taxable is a SUBSET of physical)
  2. exactly one row per (terminal, month)
  3. terminal resolves to a real terminal
  4. lift_count >= 1 on every emitted row
```

### Why invariants matter

An invariant is a promise the producer keeps and the consumer (and a test) can
check. `physical_gal >= taxable_gal` is the cheapest, most powerful one here: it
encodes the dyed-diesel asymmetry (taxable drops a product physical keeps), so a
single assertion catches a whole class of bug for free. Write the invariants into
the contract; assert them in your tests.

### The one rule that keeps it honest

**The consumer never reaches around the contract.** The web app calls
`service.monthly_volumes(...)`; it does **not** open the database itself. The moment
a template or a route runs its own SQL, you have two sources of truth and the
numbers will drift. All correctness lives in the service; everything else inherits
it.

---

## Part 2 — FastAPI dashboard quickstart

A read-only dashboard is four small pieces: the service (data), `app.py` (routes),
templates (HTML), and a little CSS. No JavaScript framework required.

### Install & run

```bash
python3 -m pip install fastapi uvicorn jinja2   # --user --break-system-packages if pip complains
uvicorn app:app --reload                            # open http://localhost:8000
```

`uvicorn app:app` means "in `app.py`, serve the object named `app`." `--reload`
restarts on save.

### Folder shape

```
sessions/session-5/
  service.py            # your Session 4 service (the data layer)
  app.py                # FastAPI routes — calls the service, never the DB
  templates/
    base.html           # the page shell
    dashboard.html      # the view (extends base.html)
  static/
    style.css
```

### Minimal `app.py` (one view)

```python
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import service                                   # <-- the data layer

_HERE = os.path.dirname(os.path.abspath(__file__))
app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(_HERE, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(_HERE, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    month = service.months()[-1]                 # latest month
    rows = service.monthly_volumes(month)
    return templates.TemplateResponse(request, "dashboard.html",
                                      {"rows": rows, "month": month})
```

### Minimal templates

`base.html` (the shell):

```html
<!doctype html><html><head>
  <meta charset="utf-8"><title>Volumes</title>
  <link rel="stylesheet" href="/static/style.css">
</head><body>
  <header>U.S. Energy · Volumes</header>
  <main>{% block content %}{% endblock %}</main>
</body></html>
```

`dashboard.html` (the view):

```html
{% extends "base.html" %}
{% block content %}
<h1>Volumes by terminal · {{ month }}</h1>
<table>
  <tr><th>Terminal</th><th>Physical</th><th>Taxable</th></tr>
  {% for r in rows %}
  <tr><td>{{ r.terminal }}</td>
      <td>{{ "{:,}".format(r.physical_gal) }}</td>
      <td>{{ "{:,}".format(r.taxable_gal) }}</td></tr>
  {% endfor %}
</table>
{% endblock %}
```

In a template, `r.terminal` reads the `"terminal"` key of a dict row.

---

## Part 3 — Gotchas (the ones that bite live)

| Symptom | Cause | Fix |
|---|---|---|
| `TypeError: unhashable type: 'dict'` from `TemplateResponse` | Old argument order | New FastAPI wants the **request first**: `TemplateResponse(request, "name.html", {ctx})` |
| Page numbers don't match your service | A template or route ran its own SQL | Route everything through `service.monthly_volumes()`; the app must not query the DB |
| `jinja2.TemplateNotFound` | Wrong templates dir | Point `Jinja2Templates(directory=...)` at the absolute `templates/` path (see `_HERE`) |
| `/static/style.css` 404 | Static mount missing/misnamed | `app.mount("/static", StaticFiles(directory=...), name="static")` and link `/static/style.css` |
| `address already in use` | A previous `uvicorn` is still running | Stop it (Ctrl+C), or run on another port: `uvicorn app:app --port 8001` |
| Chart bar divides by zero on an empty month | No rows that month | Guard the max: `max((r["physical_gal"] for r in rows), default=1)` |

---

## Part 4 — Extending it (Session 5 directions)

Each of these is one route or one template change, and each honors the contract:

- **Month filter:** a `<select>` populated from `service.months()`; pass the chosen
  month to `monthly_volumes(month)`.
- **A simple chart:** a CSS bar per terminal — width = `physical_gal / max * 100`%.
  No charting library.
- **Terminal detail:** `GET /terminal/{terminal}` → call `monthly_volumes()` (all
  months), filter to that terminal, render across months.
- **JSON API:** `GET /api/volumes?month=` → `return service.monthly_volumes(month)`
  (FastAPI serializes the list of dicts — that's your contract, machine-readable).
- **Data-quality view (stretch):** flag any terminal-month whose void rate is
  abnormally high (there's a real one in this data). The app *telling you* a number
  is suspect is Session 3's "data is the source of truth," turned into a feature.

> The discipline never changes: **read through the service, honor the contract,
> reconcile the numbers.** A prettier page that quietly changed the numbers is worse
> than the plain table you started with.

---

*Companion cards: **D4 — Data Spec Template** (where the contract is born), **C10 —
Review Rubric** (reviewing the agent's diff), **CC — Claude Code Commands**.*
