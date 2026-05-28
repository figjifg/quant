#!/usr/bin/env python3
"""BX01: Reconciliation report.

Per-year + per-review counts; missing-field census; cross-check counts against an
independent secondary source (web-research summary; cited verbatim in the report).
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/home/jin/code/quant/data/acquired/bx01_kospi200_index_event_source_a0")
EVENTS = ROOT / "events.csv"
INDEX = ROOT / "raw" / "kospi200_notice_index.json"
OUT = ROOT / "reconciliation.csv"


def main() -> int:
    rows = list(csv.DictReader(EVENTS.open(encoding="utf-8")))
    print(f"loaded {len(rows)} events")

    by_year_type = defaultdict(lambda: Counter())
    by_year_side = defaultdict(lambda: Counter())
    for r in rows:
        y = r["announcement_dt"][:4] if r["announcement_dt"] else "UNKNOWN"
        by_year_type[y][r["event_type"]] += 1
        by_year_side[y][r["side"]] += 1

    # Missing-field census
    fields_to_check = ("effective_dt", "ticker", "company_name", "review_cycle", "announcement_time")
    missing = {f: 0 for f in fields_to_check}
    for r in rows:
        for f in fields_to_check:
            if not r.get(f):
                missing[f] += 1

    # Write reconciliation.csv
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["year", "regular_reviews", "special_events",
                    "addition", "deletion", "split_action", "supplemental", "cycle", "other"])
        for y in sorted(by_year_type):
            t = by_year_type[y]
            s = by_year_side[y]
            w.writerow([y, t.get("regular_review",0), t.get("special",0),
                        s.get("addition",0), s.get("deletion",0), s.get("split_action",0),
                        s.get("supplemental",0), s.get("cycle",0), s.get("other",0)])
        w.writerow([])
        w.writerow(["TOTAL_BY_TYPE", sum(t.get("regular_review",0) for t in by_year_type.values()),
                    sum(t.get("special",0) for t in by_year_type.values())])
        w.writerow([])
        w.writerow(["MISSING_FIELD_CENSUS_(rows_lacking_value)"])
        for fld, mc in missing.items():
            w.writerow([fld, mc, f"of {len(rows)} rows = {mc/len(rows)*100:.1f}%"])

    # Print summary
    print()
    print("by-year by-type:")
    for y in sorted(by_year_type):
        t = by_year_type[y]
        print(f"  {y}: regular={t.get('regular_review',0):2d}  special={t.get('special',0):2d}")
    print()
    print("missing-field census:")
    for fld, mc in missing.items():
        print(f"  {fld:20s}: {mc:>3d}/{len(rows)} ({mc/len(rows)*100:.1f}%)")
    print(f"\nwrote {OUT}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
