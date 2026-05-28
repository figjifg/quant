#!/usr/bin/env python3
"""BX01: Build the 11-field event table from acquired metadata.

What we have (sandbox-acquired):
- 85-row notice metadata index (kospi200_notice_index.json) with REG_DT (announcement),
  bbs_seq, title, attach metadata.

What we DO NOT have (blocked by sandbox network — file.krx.co.kr returns 0 bytes for
all OTP-token download attempts):
- The xlsx/hwp/xls attachments that list which constituents were added/deleted in each
  regular review.

What we CAN extract from titles alone:
- For SPECIAL/SUPPLEMENTAL events (수시변경 / 특별변경 / 특례편입): the company name is
  often in the title (e.g., "크래프톤 신규상장에 따른 KOSPI 200 등 수시변경 안내").
- For REGULAR reviews: the review cycle (e.g., "'25.6월" → 2025-06 review).
- Announcement date: REG_DT from the metadata.
- Effective date: NOT directly in title; for regular reviews, the standard rule is the
  KOSPI 200 effective date is the second-Thursday-of-the-rebalance-month +1 trading-day
  (this needs trading-calendar reconciliation — DEFERRED, marked `effective_dt_unknown_pit`).

This script writes events.csv with PRESERVE-ALL semantics: every event a row with
parse_status describing what we know vs what is gated on attachment-download.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path("/home/jin/code/quant/data/acquired/bx01_kospi200_index_event_source_a0")
INDEX = ROOT / "raw" / "kospi200_notice_index.json"
OUT = ROOT / "events.csv"


# Pattern for cycle extraction:
#   "'25.6월", "'25.12월", "26.6월", "2018년 6월", "2018년 12월", "2017년 12월"
CYCLE_RE = [
    re.compile(r"['’](\d{2})\s*[.\s]\s*(\d{1,2})\s*월"),  # '25.6월
    re.compile(r"(\d{2})\s*[.\s]\s*(\d{1,2})\s*월"),  # 25.6월 / 26.6월
    re.compile(r"(\d{4})\s*년\s*(\d{1,2})\s*월"),  # 2018년 6월
    re.compile(r"(\d{1,2})\s*월\s*정기변경"),  # bare "6월 정기변경"
]


def extract_cycle(title: str, fallback_year: int) -> tuple[str | None, str | None]:
    """Return (yyyy_mm, source_note)."""
    for rx in CYCLE_RE[:3]:
        m = rx.search(title)
        if m:
            grs = m.groups()
            if len(grs) == 2 and rx.pattern.startswith("(\\d{4})"):
                y, mo = int(grs[0]), int(grs[1])
            else:
                y, mo = int(grs[0]), int(grs[1])
                if y < 100:
                    y = 2000 + y
            return (f"{y:04d}-{mo:02d}", f"title-cycle:{m.group(0)!r}")
    # bare month
    m = CYCLE_RE[3].search(title)
    if m:
        mo = int(m.group(1))
        return (f"{fallback_year:04d}-{mo:02d}", f"title-month-only:{m.group(0)!r}")
    return (None, "no-cycle-in-title")


# Pattern: special-event company-name extraction — best-effort heuristic, KEEP RAW SUBSTRING
SPECIAL_NAME_RE = [
    # "<NAME> 신규상장에 따른 KOSPI 200 ..."
    re.compile(r"^[\s\[\]가-힣A-Z0-9]*\s*([가-힣A-Z0-9()\.\s]+?)\s+신규상장에"),
    # "<NAME> 이전상장에 따른 KOSPI 200 ..."
    re.compile(r"^([가-힣A-Z0-9()\.\s]+?)\s+이전상장에"),
    # "<NAME>의 KOSPI200 등 ... 특례편입"
    re.compile(r"^([가-힣A-Z0-9()\.\s]+?)\s*의\s+KOSPI\s*200"),
    # "<NAME>의 인적분할에 따른 KOSPI 200 ..."
    re.compile(r"^([가-힣A-Z0-9()\.\s]+?)\s+인적분할"),
    # "<NAME> 관련 KOSPI 200 ..." / "<NAME>(<NAME>의 ...)"
    re.compile(r"^([가-힣A-Z0-9()\.\s]+?)\s+관련\s+KOSPI"),
    # "<NAME>의 관리종목지정"
    re.compile(r"\(?([가-힣A-Z0-9()\.\s]+?)\s+관리종목지정"),
]


def extract_special_name(title: str) -> tuple[str | None, str]:
    for rx in SPECIAL_NAME_RE:
        m = rx.search(title)
        if m:
            name = m.group(1).strip(" ()[]")
            # Filter out common false catches
            if name and "KOSPI" not in name and "코스피" not in name and len(name) >= 2:
                return (name, f"title-pattern:{rx.pattern[:30]}")
    return (None, "no-name-extracted-from-title")


def main() -> int:
    notices = json.load(INDEX.open(encoding="utf-8"))

    out_rows = []
    eid = 0
    for n in notices:
        eid += 1
        reg_dt = n["reg_dt"]  # announcement date
        title = n["title"]
        seq = n["bbs_seq"]
        kind = n["event_kind"]
        year = int(reg_dt[:4]) if reg_dt else None
        cycle, cycle_src = extract_cycle(title, year or 0)

        if kind == "regular":
            # Regular review — title rarely names individual constituents; CONSTITUENT-LEVEL
            # adds/deletes are in the xlsx/hwp attachment which is BLOCKED.
            # Emit ONE row per review notice at REVIEW-CYCLE granularity (side='cycle').
            out_rows.append({
                "event_id": f"BX01-{seq:0>5}-CYCLE",
                "review_cycle": cycle or "",
                "announcement_dt": reg_dt,
                "announcement_time": "",  # not in metadata; KRX press 09:00 KST typical (NOT recorded here)
                "effective_dt": "",  # gated on attachment + trading-calendar reconciliation
                "side": "cycle",
                "ticker": "",
                "company_name": "",
                "event_type": "regular_review",
                "source_id_or_url": f"KRX MDCINFO005 bbsSeq={seq}",
                "parse_status": "metadata_only__constituents_gated_on_attachment_download",
                "caveat": (cycle_src + "; "
                           "constituent-level adds/deletes are in xlsx/hwp attachments which "
                           "this sandbox cannot fetch (file.krx.co.kr returns Content-Length: 0 "
                           "for all OTP-token download attempts); "
                           "effective_dt requires KRX trading-calendar reconciliation"),
            })
        else:  # special
            name, name_src = extract_special_name(title)
            event_type = "special"
            # Heuristic side from title keywords
            if "신규상장" in title or "이전상장" in title or "특례편입" in title:
                side = "addition"
            elif "관리종목" in title or "상장폐지" in title or "피흡수합병" in title:
                side = "deletion"
            elif "인적분할" in title or "기업분할" in title:
                side = "split_action"
            elif "수시변경" in title or "특별변경" in title:
                side = "supplemental"
            else:
                side = "other"
            out_rows.append({
                "event_id": f"BX01-{seq:0>5}-SPECIAL",
                "review_cycle": "",
                "announcement_dt": reg_dt,
                "announcement_time": "",
                "effective_dt": "",
                "side": side,
                "ticker": "",
                "company_name": name or "",
                "event_type": event_type,
                "source_id_or_url": f"KRX MDCINFO005 bbsSeq={seq}",
                "parse_status": ("title_extracted_name" if name
                                 else "metadata_only__no_name_in_title"),
                "caveat": (name_src + "; "
                           "exact effective date and any per-constituent details are in the attachment "
                           "(xlsx/hwp/pdf) which this sandbox cannot fetch; "
                           "company-name extraction is title-based heuristic and NOT cross-checked against an exchange listing-name table"),
            })

    # Sort by announcement date
    out_rows.sort(key=lambda r: (r["announcement_dt"], r["event_id"]))
    cols = [
        "event_id", "review_cycle", "announcement_dt", "announcement_time", "effective_dt",
        "side", "ticker", "company_name", "event_type", "source_id_or_url", "parse_status", "caveat",
    ]
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for row in out_rows:
            w.writerow(row)

    # Summary
    print(f"wrote {len(out_rows)} rows to {OUT}")
    from collections import Counter
    print("by event_type:", dict(Counter(r["event_type"] for r in out_rows)))
    print("by side:", dict(Counter(r["side"] for r in out_rows)))
    print("by parse_status:", dict(Counter(r["parse_status"] for r in out_rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
