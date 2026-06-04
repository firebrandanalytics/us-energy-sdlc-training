#!/usr/bin/env python3
"""
noisy_job.py — a feed-ingest batch job that writes a big, noisy log.

Processes 8,000 records and writes job.log (8,000+ lines). A few records fail
permanently, buried among thousands of INFO lines and ~50 errors that RECOVERED on
retry. The catch: a recovered error and a permanent failure log the *same* text —
  ERROR ingest lift=NNNNNN vol parse failed value='...'
— except a recovered one has " — recovered after retry" appended. So there is NO
unique keyword that isolates the real failures; the only signal is the ABSENCE of
"recovered". (That's what makes a plain keyword grep fall short and a negative
lookahead — or a `grep ... | grep -v recovered` pipe — the right tool.)

Your job (with the agent): find the real failures FROM THE LOG (don't read this file
first), work out why, then fix the cause and re-run until nothing fails.
"""
import datetime
import pathlib
import random

LOG = pathlib.Path("job.log")
N = 8000
random.seed(42)  # deterministic

# "Dirty" feed values float() can't parse — the planted defect, at fixed records.
DIRTY = {
    611:  "4,210.5",      # thousands comma
    1473: "3180.0 gal",   # trailing unit
    2999: "",             # empty field
    4102: "1,002,544",    # big number with commas
    6840: "5120.5gal",    # unit jammed on the number
    7321: "   ",          # whitespace only
}


def parse_vol(s):
    # BUG: assumes the feed is always a clean number. It isn't (see DIRTY).
    return float(s)


def main():
    lines = []
    ts = datetime.datetime(2026, 6, 4, 9, 0, 0)
    failed = []
    for i in range(N):
        ts += datetime.timedelta(milliseconds=random.randint(40, 900))
        stamp = ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z"
        lift = f"{100000 + i:06d}"
        raw = DIRTY.get(i, f"{random.uniform(500, 9000):.1f}")

        if random.random() < 0.012:
            lines.append(f"{stamp} WARN  ingest lift={lift} slow source "
                         f"{random.randint(600, 950)}ms, retry 1/3")
        # Benign: SAME wording as a real failure, but it recovered. A clean value.
        if random.random() < 0.007:
            good = f"{random.uniform(500, 9000):.1f}"
            lines.append(f"{stamp} ERROR ingest lift={lift} vol parse failed "
                         f"value='{good}' — recovered after retry")

        try:
            vol = parse_vol(raw)
            lines.append(f"{stamp} INFO  ingest lift={lift} vol={vol:.1f} gal ok")
        except ValueError:
            failed.append(lift)
            # Real, permanent failure: identical wording, but NO "recovered" tag.
            lines.append(f"{stamp} ERROR ingest lift={lift} vol parse failed "
                         f"value='{raw}'")

    LOG.write_text("\n".join(lines) + "\n")
    print(f"ingested {N - len(failed)}/{N} records; {len(failed)} permanently failed.")
    print(f"wrote {LOG} ({len(lines)} lines). Some records did not ingest — check the log.")


if __name__ == "__main__":
    main()
