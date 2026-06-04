"""
service.py — the volumes service (the clean data layer the dashboard consumes).

This is the Session 4 deliverable, dropped in so the dashboard runs standalone. It
does not print or render — it RETURNS data, so the web app can consume it. The app
never queries the database directly; it only ever calls these functions.

THE OUTPUT CONTRACT (what one row is):
    {
      "terminal":     str,   # terminal display code, e.g. "DAL"
      "month":        str,   # "YYYY-MM"
      "physical_gal": int,   # SUM(net_gal) over real movements, whole gallons
      "taxable_gal":  int,   # physical minus dyed off-road diesel (prod_cd 6)
    }
Invariants a consumer can rely on:
    - physical_gal >= taxable_gal >= 0   (taxable is a subset of physical)
    - one row per (terminal, month)
    - terminal resolves to a real terminal

Measures:
    physical_gal = SUM(net_gal) over real movements; excludes voids (status 8) and
                   non-physical book adjustments (mode 8). net_gal is temperature-
                   corrected gallons (never gross_gal).
    taxable_gal  = physical minus dyed/off-road diesel (prod_cd 6), tax-exempt.

Reconciles to data/vol_report.py for any month (e.g. DAL 2025-08 = 1,517,103
physical / 1,371,642 taxable).
"""
import os
import sqlite3

_HERE = os.path.dirname(os.path.abspath(__file__))
# First existing path wins — works whether this file sits in sessions/session-5/
# or one level deeper in sessions/session-5/starter/.
_DB_CANDIDATES = [
    os.path.join(_HERE, "..", "..", "data", "us_energy.sqlite"),
    os.path.join(_HERE, "..", "..", "..", "data", "us_energy.sqlite"),
]

STATUS_VOID = 8        # void / reversed         -> exclude from every measure
MODE_BOOK_ADJ = 8      # non-physical book adj   -> exclude from every measure
PROD_DYED_DIESEL = 6   # dyed off-road diesel    -> tax-exempt, exclude from TAXABLE only


def _db_path() -> str:
    for cand in _DB_CANDIDATES:
        if os.path.exists(cand):
            return os.path.abspath(cand)
    return os.path.abspath(_DB_CANDIDATES[0])


def _connect(db_path=None) -> sqlite3.Connection:
    con = sqlite3.connect(db_path or _db_path())
    con.row_factory = sqlite3.Row
    return con


def months(db_path=None) -> list[str]:
    """Every 'YYYY-MM' present in the data, ascending."""
    con = _connect(db_path)
    try:
        return [r[0] for r in con.execute(
            "SELECT DISTINCT strftime('%Y-%m', lift_ts) AS m FROM lifts ORDER BY m")]
    finally:
        con.close()


def _month_bounds(ym: str) -> tuple[str, str]:
    """Half-open [lo, hi) timestamp strings for the calendar month 'YYYY-MM'.

    A range predicate (lift_ts >= lo AND < hi) is sargable — an index on lift_ts can
    engage — whereas wrapping the column in strftime/substr defeats any index. Same
    rows as strftime(...) = 'YYYY-MM' for this data. (December rolls the year.)
    """
    y, m = int(ym[:4]), int(ym[5:7])
    lo = f"{y:04d}-{m:02d}-01 00:00:00"
    hi = f"{y + 1:04d}-01-01 00:00:00" if m == 12 else f"{y:04d}-{m + 1:02d}-01 00:00:00"
    return lo, hi


def monthly_volumes(month: str | None = None, db_path=None) -> list[dict]:
    """Clean physical and taxable net gallons by terminal, physical-descending.

    Pass month='YYYY-MM' to filter to a single month; omit for all months.
    """
    sql = """
        SELECT t.term_cd                                              AS terminal,
               strftime('%Y-%m', l.lift_ts)                          AS month,
               SUM(l.net_gal)                                        AS physical_gal,
               SUM(CASE WHEN l.prod_cd <> ? THEN l.net_gal ELSE 0 END) AS taxable_gal
        FROM lifts l
        JOIN terminals t ON t.term_id = l.term_id
        WHERE l.status <> ?          -- exclude voided / reversed tickets
          AND l.mode   <> ?          -- exclude non-physical book adjustments
        {month_filter}
        GROUP BY t.term_cd, month
        ORDER BY physical_gal DESC
    """
    params: list = [PROD_DYED_DIESEL, STATUS_VOID, MODE_BOOK_ADJ]
    month_filter = ""
    if month:
        # Sargable range, not strftime(lift_ts) = ? — see _month_bounds().
        lo, hi = _month_bounds(month)
        month_filter = "AND l.lift_ts >= ? AND l.lift_ts < ?"
        params += [lo, hi]
    con = _connect(db_path)
    try:
        return [
            {
                "terminal": r["terminal"],
                "month": r["month"],
                "physical_gal": round(r["physical_gal"] or 0),
                "taxable_gal": round(r["taxable_gal"] or 0),
            }
            for r in con.execute(sql.format(month_filter=month_filter), params)
        ]
    finally:
        con.close()
