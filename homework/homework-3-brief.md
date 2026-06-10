# Homework #3 — Stand Up the Dashboard Starter

**Assigned after:** Session 4 (From Vague Ask to a Working Service)
**Due before:** Session 5
**Time budget:** 30–45 minutes (deliberately small)

---

## The Assignment

In Session 4 you built a **service** — a `service.py` that *returns* clean monthly
volumes by terminal. Now put the smallest possible **web page** on top of it: a
read-only dashboard with **one view**, a table of volumes by terminal.

That's it. Skeleton plus one table. No month picker, no chart, no detail pages, no
JSON API — those are what we build *together* in Session 5. This homework is
intentionally light: the goal is that you arrive at Session 5 with something
running, so we can spend the session **extending** it instead of bootstrapping it.

> **Why so small?** Session 5 is the capstone — splitting work across parallel
> agents to grow this dashboard. You get far more out of that if the skeleton
> already exists. Starting small here is the setup for going wide there.

---

## What you're building

A FastAPI app with a single route — `GET /` — that calls your service and renders
a table:

```
U.S. Energy · Volumes Dashboard
Fuel volumes by terminal · 2025-12

Terminal    Physical (net gal)    Taxable (net gal)
ICT              1,359,752            1,192,172
MSN              1,310,078            1,192,310
...
```

(Those are the real top-2 for 2025-12 — if your service is right, your page should
show exactly these.)

The shape that matters: **`app.py` never touches the database.** It imports
`service.py` and renders whatever the service returns. That seam — the output
contract you wrote in Session 4 — is the whole reason the app stays simple.

---

## Setup

Work in **`sessions/session-5/`** of the **course repo** (the dashboard lives
where you'll extend it next session). Bring your Session 4 service over from
*your* repo:

```bash
cd sessions/session-5                       # in the course repo
cp ../../../<initials>-volume-service/service.py ./service.py        # adjust the path to YOUR repo
cp ../../../<initials>-volume-service/test_service.py ./test_service.py 2>/dev/null || true
python3 -m pip install fastapi uvicorn jinja2     # pytest you already have from Session 4
# (if pip says "externally-managed-environment", add: --user --break-system-packages)
```

Your service reads its database path from the **`DB_PATH`** environment variable
(that's why we made it configurable). From `sessions/session-5/` the course data
is two levels up, so set it once per shell:

```bash
export DB_PATH=../../data/us_energy.sqlite
```

Confirm the service works from here:

```bash
python3 -c "import service; print(service.monthly_volumes(service.months()[-1])[0])"
# -> the top row for the latest month:
#    {'terminal': 'ICT', 'month': '2025-12', 'physical_gal': 1359752, 'taxable_gal': 1192172, 'lift_count': 164}
```

Keep **D5 — Output Contract & Dashboard** open. It has the FastAPI quickstart and
the contract pattern you'll lean on.

---

## What to Produce

### 1. `app.py` — one route

A FastAPI app whose `GET /` route:

- calls `service.months()` to find the latest month;
- calls `service.monthly_volumes(month)` for that month;
- renders the rows as an HTML table via a Jinja2 template.

Direct Claude Code to build it. A prompt that works:

```
In this folder there's a service.py exposing monthly_volumes(month) and months(),
which return clean volume rows by terminal (fields: terminal, month, physical_gal,
taxable_gal, lift_count). Build a minimal read-only FastAPI app, app.py, with ONE route GET /
that shows a table of the latest month's volumes by terminal, rendered with a
Jinja2 template. The app must call the service — it must NOT query the database
itself. Keep it minimal: no month filter, no chart, no other routes. Use
templates/ for the HTML and a small static/style.css. Note: this FastAPI version
wants the request first: templates.TemplateResponse(request, "name.html", {...}).
Then tell me how to run it.
```

Review the diff before you accept it (**C10** habit). The two things to check:

- **It calls the service**, not the database. If you see `sqlite3.connect` in
  `app.py`, send it back — the data layer is `service.py`'s job.
- **The numbers match your Session 4 service.** Same volumes, now in a browser.

### 2. Run it and see it

```bash
uvicorn app:app --reload
# open http://localhost:8000
```

You should see your table in a browser. That's the deliverable: a running page,
served by FastAPI, showing real reconciled numbers from your service.

### 3. One sentence on the seam

In a comment at the top of `app.py` (or your reflection notes), write one line:
*why does the app import the service instead of running SQL itself?* You'll build on
that answer in Session 5 when two agents extend this in parallel.

---

## The Safety Net — You Will Not Be Blocked

A working starter is committed at **`sessions/session-5/starter/`**. If you run out
of time, get stuck, or your build won't run, you can still do the Session 5 lab:

```bash
cd sessions/session-5
cp -r starter/* .          # app.py, service.py, templates/, static/, requirements.txt
uvicorn app:app --reload   # confirm it serves at http://localhost:8000
```

**Try to build your own first** — the learning is in wiring the app to the service
yourself, and in catching the "don't query the DB from the app" mistake in your own
diff. The starter is your reference and your fallback, not your first move. (If you
do use it, skim `app.py` so you understand what you're extending.)

---

## Stretch (optional, if you finish early)

Pick one — small wins that make Session 5 smoother:

- **Show the row count and month** in the page header (e.g. "25 terminals ·
  2025-12").
- **Light styling** — right-align the numbers, a header bar, tabular figures. (The
  committed starter's `style.css` is a fine reference if you want one.)
- **A `requirements.txt`** pinning `fastapi`, `uvicorn`, `jinja2`, so a teammate
  can `pip install -r requirements.txt` and run it.

Don't add a month filter or chart yet — resist it. Those are Session 5, on purpose.

---

## Reflection — Bring These to Session 5

After you finish, jot short answers:

1. **Did it run, and do the numbers match your service?** One sentence.
2. **The seam:** in your own words, what does keeping SQL out of `app.py` buy you?
3. **One thing you'd want to add** to the dashboard — a feature you'll be glad we
   build next session.
4. **One snag** — a moment the agent did something you had to correct, or a setup
   issue you hit (so we can clear it for the room).

Keep each to two or three sentences. Capturing it while it's fresh, not writing a
report.

---

## Pre-work for Session 5 — only if DevOps fought you in class

You used Azure DevOps from the agent in Session 4 (work items, the ticket
comment, the repo push). Session 5 finishes the loop there — the clean-context
review of your PR, the merge, the tickets closing — so if **any** of that
errored for you in class, fix it before Tuesday:

```bash
az extension add --name azure-devops     # the DevOps plugin for the az CLI (once)
az login                                 # browser sign-in with your work account
az devops configure --defaults organization=https://dev.azure.com/<your-org> project=<your-project>
az boards work-item list --top 1 -o table   # any output (even "no items") = working
```

If it still errors on permissions, note the exact message and bring it — we
triage access patterns (own repo vs. shared repo + your branch) at the top of
Session 5. Nothing else in this homework depends on DevOps.

---

## What to Bring to Session 5

- Your running `sessions/session-5/` dashboard (or the copied starter).
- Your four reflection bullets.
- `az devops project list` working (or the error message it gave you — see
  pre-work above).

Session 5 opens with a quick share-back, then we **extend this dashboard** — month
filter, a chart, a terminal-detail page, a JSON API — by splitting the work across
parallel agents, all building against your service's contract. The cleaner your
skeleton, the more the parallel build just clicks together.

---

*Reference: **D5 — Output Contract & Dashboard** (the FastAPI quickstart and the
contract pattern); **C10 — Review Rubric** (reviewing the agent's diff). The service
you're building on is from the Session 4 lab. Questions? Session 5 opens with the
share-back.*
