#!/usr/bin/env python3
"""BX01-attachment-parse: consolidate v2 event artifact.

Combines:
- events_class_a.csv (12 rows, 2021-06 direct from KOSPI 200 변경내역 sheet)
- events_class_b_derived.csv (133 rows, snapshot-diff derived for 2021-12..2026-06)
- Notice-level skeleton from the prior source-A0 events.csv for cycles NOT covered
  (2018-06, 2018-12, 2019-06, 2019-12, 2020-06, 2020-12 + all 55 Tier 2 specials)

Writes: events_v2.csv with explicit `source_record_type` column distinguishing:
- `constituent_level_direct_from_change_detail_sheet` (Class A, 1 cycle, 12 rows)
- `constituent_level_derived_from_consecutive_official_snapshot_diff` (Class B, 9 Tier 1 + 1 bridge, 133 rows)
- `notice_level_skeleton_only` (everything else; preserves prior phase output)

Per Referee 2026-05-30 clarification: confidence labels are STRONG, never collapsed
together; preserve-all.
"""
from __future__ import annotations

import csv
from pathlib import Path

OUT_DIR = Path("/home/jin/code/quant/data/acquired/bx01_kospi200_index_event_source_a0")
A_FILE = OUT_DIR / "events_class_a.csv"
B_FILE = OUT_DIR / "events_class_b_derived.csv"
SKELETON_FILE = OUT_DIR / "events.csv"  # the prior phase output (notice-level skeleton)
OUT = OUT_DIR / "events_v2.csv"


def main() -> int:
    out_cols = [
        "event_id", "review_cycle", "announcement_dt", "announcement_time", "effective_dt",
        "index_name", "side", "ticker", "company_name",
        "source_class", "source_record_type",
        "source_id_or_url", "source_file", "source_file_sha256",
        "prev_snapshot_file", "prev_snapshot_sha256", "prev_snapshot_cycle",
        "tier1_status",
        "parse_status", "caveat",
    ]

    rows = []

    # Class A direct rows
    a_rows = list(csv.DictReader(A_FILE.open(encoding="utf-8")))
    for r in a_rows:
        out = {c: "" for c in out_cols}
        out.update({
            "event_id": r["event_id"],
            "review_cycle": r["review_cycle"],
            "announcement_dt": r["announcement_dt"],
            "announcement_time": r["announcement_time"],
            "effective_dt": r["effective_dt"],
            "index_name": r["index_name"],
            "side": r["side"],
            "ticker": r["ticker"],
            "company_name": r["company_name"],
            "source_class": "A_KRX_xlsx_with_change_detail",
            "source_record_type": "constituent_level_direct_from_change_detail_sheet",
            "source_id_or_url": r["source_id_or_url"],
            "source_file": r["source_file"],
            "source_file_sha256": r["source_file_sha256"],
            "tier1_status": "tier1_target",
            "parse_status": r["parse_status"],
            "caveat": r["caveat"],
        })
        rows.append(out)
    print(f"loaded {len(a_rows)} Class A rows")

    # Class B derived rows
    b_rows = list(csv.DictReader(B_FILE.open(encoding="utf-8")))
    for r in b_rows:
        out = {c: "" for c in out_cols}
        out.update({
            "event_id": r["event_id"],
            "review_cycle": r["review_cycle"],
            "announcement_dt": r["announcement_dt"],
            "announcement_time": r["announcement_time"],
            "effective_dt": r["effective_dt"],
            "index_name": r["index_name"],
            "side": r["side"],
            "ticker": r["ticker"],
            "company_name": r["company_name"],
            "source_class": r["source_class"],
            "source_record_type": "constituent_level_derived_from_consecutive_official_snapshot_diff",
            "source_id_or_url": r["source_id_or_url"],
            "source_file": r["source_file"],
            "source_file_sha256": r["source_file_sha256"],
            "prev_snapshot_file": r["prev_snapshot_file"],
            "prev_snapshot_sha256": r["prev_snapshot_sha256"],
            "prev_snapshot_cycle": r["prev_snapshot_cycle"],
            "tier1_status": r["tier1_status"],
            "parse_status": r["parse_status"],
            "caveat": r["caveat"],
        })
        rows.append(out)
    print(f"loaded {len(b_rows)} Class B derived rows")

    # Notice-level skeleton for NOT-COVERED cycles + all specials
    # Convert all skeleton rows that are NOT in our parsed coverage
    parsed_bbs_seqs = {"734", "774", "799", "861", "899", "939", "979", "1015", "1050", "1090"}
    sk_rows = list(csv.DictReader(SKELETON_FILE.open(encoding="utf-8")))
    skeleton_kept = 0
    for r in sk_rows:
        # Extract bbsSeq from event_id (BX01-<bbsSeq>-CYCLE or BX01-<bbsSeq>-SPECIAL)
        eid = r["event_id"]
        parts = eid.split("-")
        bbs_seq = parts[1].lstrip("0") if len(parts) >= 2 else ""
        if bbs_seq in parsed_bbs_seqs:
            continue  # superseded by Class A/B parse
        out = {c: "" for c in out_cols}
        out.update({
            "event_id": r["event_id"],
            "review_cycle": r["review_cycle"],
            "announcement_dt": r["announcement_dt"],
            "announcement_time": r["announcement_time"],
            "effective_dt": r["effective_dt"],
            "index_name": "KOSPI 200" if "CYCLE" in eid else "",
            "side": r["side"],
            "ticker": r["ticker"],
            "company_name": r["company_name"],
            "source_class": "notice_metadata_only",
            "source_record_type": "notice_level_skeleton_only",
            "source_id_or_url": r["source_id_or_url"],
            "tier1_status": "tier1_target" if bbs_seq in {"555", "613", "667", "696"} else "out_of_tier1",
            "parse_status": r["parse_status"],
            "caveat": (r["caveat"] + "; CARRIED FORWARD from source-A0 phase — "
                       "constituents NOT in this row; attachments user-supplied as hwp/broker pdf, "
                       "deferred per Referee directive (not parsed in this phase)" if bbs_seq in {"555","613","667","696"} else
                       r["caveat"] + "; CARRIED FORWARD from source-A0 phase — special/supplemental event; "
                       "Tier 2/3 deferred per directive"),
        })
        rows.append(out)
        skeleton_kept += 1
    print(f"carried forward {skeleton_kept} skeleton rows (uncovered cycles + Tier 2/3 specials)")

    # Sort: by announcement_dt, then by event_id
    rows.sort(key=lambda r: (r["announcement_dt"] or "9999", r["event_id"]))

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {len(rows)} rows to {OUT}")

    # Summary
    from collections import Counter
    print("\nby source_record_type:")
    for k, v in Counter(r["source_record_type"] for r in rows).items():
        print(f"  {v:>4d}  {k}")
    print("\nby tier1_status:")
    for k, v in Counter(r["tier1_status"] for r in rows).items():
        print(f"  {v:>4d}  {k}")
    print("\nby parse_status:")
    for k, v in Counter(r["parse_status"] for r in rows).items():
        print(f"  {v:>4d}  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
