"""
app.py — minimal read-only dashboard over the volumes service (Homework 3 starter).

This is the skeleton you EXTEND in Session 5. It has exactly one view: a table of
clean monthly volumes by terminal for the latest month, read from service.py.
No month filter, no chart, no terminal-detail page, no JSON API — those are what
you and the agent add in class, against the service's output contract.

The point of the split: app.py knows nothing about SQL. It calls the service and
renders what comes back. That seam — the service's contract — is what lets you (and
parallel agents) build the app and the data layer independently.

Run:
    python3 -m pip install -r requirements.txt
    export DB_PATH=../../data/us_energy.sqlite   # when running from sessions/session-5/
    uvicorn app:app --reload      # then open http://localhost:8000
"""
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import service

_HERE = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="U.S. Energy — Volumes Dashboard (starter)")
templates = Jinja2Templates(directory=os.path.join(_HERE, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(_HERE, "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    months = service.months()
    month = months[-1] if months else None          # latest month only, for now
    rows = service.monthly_volumes(month=month)
    # NOTE: newer FastAPI wants the request FIRST: TemplateResponse(request, name, ctx)
    return templates.TemplateResponse(request, "dashboard.html", {
        "rows": rows,
        "month": month,
    })
