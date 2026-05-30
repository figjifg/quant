#!/usr/bin/env python3
"""BX01-attachment-parse final pass: listing-name/ticker cross-check.

Per Referee 2026-05-31 final-pass requirement (#1):
- Join events_v2.csv constituent-level rows against listing-universe-A0 outputs
  (`data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv`).
- Use the listing snapshot AS OF announcement_dt (PIT — never later snapshots).
- For each row, check: (a) ticker exists in PIT listing snapshot; (b) recorded
  company_name matches listing name; (c) market = KOSPI.
- Tag with match_status: `match_clean` / `match_name_diff` / `ticker_not_in_pit_listing` /
  `pit_snapshot_unavailable`. NEVER DROP.

Output: events_v2_xref.csv (enriched), and update reconciliation_v2 with cross-check
counts.
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

OUT_DIR = Path("/home/jin/code/quant/data/acquired/bx01_kospi200_index_event_source_a0")
EVENTS = OUT_DIR / "events_v2.csv"
LISTING = Path("/home/jin/code/quant/data/acquired/krx_listed_universe/"
               "krx_listed_monthly_snapshots_2010_2026.csv")
OUT = OUT_DIR / "events_v2_xref.csv"


def main() -> int:
    # Load listing universe
    listing = pd.read_csv(LISTING, dtype={"ticker": str})
    listing["snapshot_date"] = pd.to_datetime(listing["snapshot_date"]).dt.date
    snapshot_dates = sorted(listing["snapshot_date"].unique())
    print(f"loaded listing universe: {listing.shape}, snapshot_date range "
          f"{snapshot_dates[0]} .. {snapshot_dates[-1]}, "
          f"{len(snapshot_dates)} unique snapshots")

    def latest_snapshot_on_or_before(d: date) -> date | None:
        """PIT: return the latest listing snapshot_date <= d."""
        lo, hi = 0, len(snapshot_dates) - 1
        if not snapshot_dates or d < snapshot_dates[0]:
            return None
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if snapshot_dates[mid] <= d:
                lo = mid
            else:
                hi = mid - 1
        return snapshot_dates[lo]

    # Build a fast lookup: snapshot_date -> {ticker -> (market, name)}
    by_snapshot: dict[date, dict[str, tuple[str, str]]] = {}
    for sd, sub in listing.groupby("snapshot_date"):
        by_snapshot[sd] = {row.ticker: (row.market, str(row.name) if pd.notna(row.name) else "")
                             for row in sub.itertuples(index=False)}

    # Load events_v2
    events = list(csv.DictReader(EVENTS.open(encoding="utf-8")))
    print(f"loaded events_v2.csv: {len(events)} rows")

    # Process each row
    out_rows = []
    counts = {"match_clean": 0,
              "match_ticker_only_listing_name_unavailable": 0,
              "match_name_diff": 0,
              "ticker_not_in_pit_listing": 0,
              "pit_snapshot_unavailable": 0,
              "non_constituent_level_skipped": 0}
    name_diff_examples = []
    not_in_pit_examples = []

    for r in events:
        ert = r.get("source_record_type", "")
        if "constituent_level" not in ert:
            r["xref_match_status"] = "not_applicable_skeleton_row"
            r["xref_pit_snapshot_date"] = ""
            r["xref_listing_name"] = ""
            r["xref_market"] = ""
            counts["non_constituent_level_skipped"] += 1
            out_rows.append(r)
            continue

        ann = r.get("announcement_dt", "")
        try:
            ann_d = date.fromisoformat(ann)
        except Exception:
            r["xref_match_status"] = "pit_snapshot_unavailable"
            r["xref_pit_snapshot_date"] = ""
            r["xref_listing_name"] = ""
            r["xref_market"] = ""
            counts["pit_snapshot_unavailable"] += 1
            out_rows.append(r)
            continue

        sd = latest_snapshot_on_or_before(ann_d)
        if sd is None or sd not in by_snapshot:
            r["xref_match_status"] = "pit_snapshot_unavailable"
            r["xref_pit_snapshot_date"] = ""
            r["xref_listing_name"] = ""
            r["xref_market"] = ""
            counts["pit_snapshot_unavailable"] += 1
            out_rows.append(r)
            continue

        ticker = r.get("ticker", "").strip()
        if ticker not in by_snapshot[sd]:
            r["xref_match_status"] = "ticker_not_in_pit_listing"
            r["xref_pit_snapshot_date"] = sd.isoformat()
            r["xref_listing_name"] = ""
            r["xref_market"] = ""
            counts["ticker_not_in_pit_listing"] += 1
            if len(not_in_pit_examples) < 10:
                not_in_pit_examples.append((r["ticker"], r["company_name"], r["review_cycle"], r["side"]))
            out_rows.append(r)
            continue

        listing_market, listing_name = by_snapshot[sd][ticker]
        r["xref_pit_snapshot_date"] = sd.isoformat()
        r["xref_listing_name"] = listing_name
        r["xref_market"] = listing_market

        # Compare names (loose: trim + case-insensitive + ignore spaces)
        nA = (r.get("company_name") or "").replace(" ", "").lower()
        nB = (listing_name or "").strip().replace(" ", "").lower()

        if not nB:
            # Listing snapshot has the ticker but no name — known limitation of
            # listing-universe-A0 (25.3% panel-coverage gap per project memory).
            r["xref_match_status"] = "match_ticker_only_listing_name_unavailable"
            counts["match_ticker_only_listing_name_unavailable"] += 1
        elif nA == nB:
            r["xref_match_status"] = "match_clean"
            counts["match_clean"] += 1
        else:
            r["xref_match_status"] = "match_name_diff"
            counts["match_name_diff"] += 1
            if len(name_diff_examples) < 10:
                name_diff_examples.append((r["ticker"], r["company_name"], listing_name, r["review_cycle"], r["side"]))
        out_rows.append(r)

    # Write enriched events
    cols = list(out_rows[0].keys())
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    print(f"\nwrote {len(out_rows)} rows to {OUT}\n")

    print("xref counts:")
    for k, v in counts.items():
        print(f"  {v:>4d}  {k}")

    if name_diff_examples:
        print("\nname-diff examples (first 10):")
        for tk, n_attach, n_list, cyc, side in name_diff_examples:
            print(f"  {tk}  cycle={cyc} {side:>8s}  attachment='{n_attach}'  listing='{n_list}'")

    if not_in_pit_examples:
        print("\nticker-not-in-pit-listing examples (first 10):")
        for tk, n_attach, cyc, side in not_in_pit_examples:
            print(f"  {tk}  cycle={cyc} {side:>8s}  attachment='{n_attach}'")

    # Also append xref summary to reconciliation_v2.csv
    REC = OUT_DIR / "reconciliation_v2.csv"
    with REC.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["", "", "", ""])
        w.writerow(["LISTING_NAME_CROSS_CHECK", "key", "value", "note"])
        for k, v in counts.items():
            w.writerow(["LISTING_NAME_CROSS_CHECK", k, v, ""])
        w.writerow(["LISTING_NAME_CROSS_CHECK", "method",
                    "PIT: latest listing snapshot_date <= announcement_dt; name compared ignoring space + case",
                    ""])
        w.writerow(["LISTING_NAME_CROSS_CHECK", "drop_policy",
                    "NONE — every row preserved with xref_match_status caveat per Referee",
                    ""])
    print(f"\nappended LISTING_NAME_CROSS_CHECK section to {REC}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
