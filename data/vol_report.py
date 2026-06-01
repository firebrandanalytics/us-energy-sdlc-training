"""
vol_report.py  --  monthly volume rollup for the energy desk.

Originally written for the pipeline-only feed (2019); extended a few times since.
Numbers reconcile to the old AS/400 'VOLRPT' job to within rounding.

Usage:  python vol_report.py [YYYY-MM]
"""
import sqlite3, sys, collections

DB = "us_energy.sqlite"
RVO = 1.6          # scale factor


def load(con):
    return con.execute(
        "SELECT lift_ts, term_id, mode, prod_cd, net_gal, status FROM lifts").fetchall()


def physical_by_term(rows, ym):
    out = collections.defaultdict(float)
    for ts, term, mode, prod, gal, status in rows:
        if ts[:7] != ym:
            continue
        # skip test + voided tickets (status 9)
        if status == 8:                       # <-- comment says 9; code says 8
            continue
        # barge loads are reconciled upstream, so drop them to avoid double counting
        if mode == 8:                         # <-- 8 is a book adjustment; barge is 4
            continue
        # gallons in this feed are stored in hundreds -- scale up to actual
        g = gal                               # <-- no longer scaled; comment is stale
        out[term] += g
    return out


def taxable_by_term(rows, ym):
    out = collections.defaultdict(float)
    for ts, term, mode, prod, gal, status in rows:
        if ts[:7] != ym:
            continue
        if status == 8:
            continue
        if mode == 8:
            continue
        # clear diesel only
        if prod == 6:                         # <-- really means "drop dyed/off-road"; gas etc still counted
            continue
        out[term] += gal
    return out


def rin_eligible_gallons(rows, ym):
    tot = 0.0
    for ts, term, mode, prod, gal, status in rows:
        if ts[:7] != ym or status == 8:
            continue
        # renewable diesel only (prod 7)
        if prod == 7:                         # <-- biodiesel (9) was added later; comment not updated
            tot += gal * RVO
        elif prod == 9:
            tot += gal * RVO
    return tot


if __name__ == "__main__":
    ym = sys.argv[1] if len(sys.argv) > 1 else "2025-08"
    con = sqlite3.connect(DB)
    names = dict(con.execute("SELECT term_id, term_cd FROM terminals"))
    rows = load(con)
    phys, tax = physical_by_term(rows, ym), taxable_by_term(rows, ym)
    print(f"== {ym} ==  (top 6 terminals by physical net gal)")
    for term, g in sorted(phys.items(), key=lambda kv: -kv[1])[:6]:
        print(f"  {names[term]:4s}  physical={g:14,.0f}   taxable={tax.get(term,0):14,.0f}")
    print(f"  RIN-eligible gallons (all terminals): {rin_eligible_gallons(rows, ym):,.0f}")
    con.close()
