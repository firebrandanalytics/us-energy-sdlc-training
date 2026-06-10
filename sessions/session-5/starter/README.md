# Dashboard starter — Homework 3 → Session 5

A minimal read-only web dashboard over the volumes **service** you built in
Session 4. It has exactly one view: a table of clean monthly volumes by terminal
for the latest month. This is the skeleton you **extend in Session 5**.

The shape of the whole thing: `app.py` knows nothing about SQL. It calls
`service.py` and renders what comes back. That seam — the service's output
contract — is what lets the app and the data layer evolve independently (and what
lets parallel agents extend them at the same time in Session 5).

## Run it

```bash
python3 -m pip install -r requirements.txt   # add --user --break-system-packages if pip complains
export DB_PATH=../../data/us_energy.sqlite      # run from sessions/session-5/
uvicorn app:app --reload
# open http://localhost:8000
```

You should see a table of terminals with physical and taxable net gallons for the
latest month — the same numbers your Session 4 service reconciled to the legacy
script.

## What's here

| File | What it is |
|---|---|
| `service.py` | The data layer (your Session 4 service): `monthly_volumes(month)` and `months()`. The app only ever calls these — it never touches the database. |
| `app.py` | The FastAPI app. One route: `GET /` renders the volumes table. |
| `templates/base.html`, `templates/dashboard.html` | The Jinja2 views. |
| `static/style.css` | Minimal styling. |
| `requirements.txt` | `fastapi`, `uvicorn`, `jinja2`. |

## Catching up for Session 5

If you didn't build your own dashboard in Homework 3 — or it isn't running — you
can still do today's lab. Copy this starter up into your Session 5 working
directory and start from here:

```bash
cd sessions/session-5
cp -r starter/* .
```

Then rejoin the class at **"extend the dashboard."** Nobody is blocked.

Reads `../../data/us_energy.sqlite`.
