"""
retail_gas_report.py  --  quick "retail gasoline" volume by terminal.

A little helper the desk reaches for when someone wants a fast retail read.
It runs; the comments are another matter. Decode it the way you decoded the
query: read what each line actually DOES, then check the claim against the data.

Usage:  python3 retail_gas_report.py [YYYY-MM]      (Windows: python  or  py)
        (run from the repo root; expects data/us_energy.sqlite)
"""
import sqlite3, sys, collections, os

DB = os.path.join("data", "us_energy.sqlite")


def retail_gas_by_term(con, ym):
    rows = con.execute(
        "SELECT lift_ts, term_id, prod_cd, channel_id, status, net_gal FROM lifts"
    ).fetchall()
    out = collections.defaultdict(float)
    for ts, term, prod, channel, status, gal in rows:
        if ts[:7] != ym:
            continue
        # wholesale customers only (channel 1)
        if channel != 1:
            continue
        # all grades of gasoline (product codes 1 and 2)
        if prod != 1:
            continue
        # voided tickets are already filtered out upstream, so just sum
        out[term] += gal
    return out


if __name__ == "__main__":
    ym = sys.argv[1] if len(sys.argv) > 1 else "2025-08"
    con = sqlite3.connect(DB)
    names = dict(con.execute("SELECT term_id, term_cd FROM terminals"))
    res = retail_gas_by_term(con, ym)
    print(f"== retail gasoline, {ym} ==  (top 6 terminals by net gal)")
    for term, g in sorted(res.items(), key=lambda kv: -kv[1])[:6]:
        print(f"  {names[term]:4s}  {g:12,.0f}")
    con.close()
