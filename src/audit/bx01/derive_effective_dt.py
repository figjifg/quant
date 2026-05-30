#!/usr/bin/env python3
"""BX01-rulebook-effective-dt-A0: derive per-cycle effective_dt under hybrid (c).

Inputs:
- Mirae 2021-11 KOSPI200 methodology PDF (broker-hosted KRX-attributed secondary):
  Rule §7.1: "정기변경일 = KOSPI200 선물시장 6월/12월 결제월 최종거래일의 다음 매매거래일."
- Hana 2020-05-25 장내파생상품 거래설명서 PDF (broker-hosted KRX-attributed secondary):
  Page 8 + Page 15: "KOSPI200 선물 최종거래일 = 각 결제월의 두 번째 목요일."
- Local KRX trading calendar (krx_official_calendar_2010_2026.csv) — used for
  "next trading day" lookup only.

Outputs:
- per_cycle_effective_dt.csv (full basis table with 12 fields per Referee spec)
- events_v3.csv (events_v2_xref.csv + 4 new effective_dt_* columns; preserve-all)
- reconciliation_v3.csv (per-cycle counts, confidence breakdown, 2026-06 gap note)

Per Referee 2026-05-31 hybrid (c) clarification:
- Mirae methodology = secondary KRX-publisher-attributed rulebook copy
- Hana 거래설명서 = secondary broker-hosted KRX-attributed derivatives product spec
- BOTH are NOT primary KRX
- 9 cycles 2021-06..2025-12 = provisional secondary-triangulated fill with strict labels
- 2026-06 = blank (calendar cutoff)
- effective_dt MUST come from rule + local calendar; NEVER convention/news fill
- Press release 2026-06-12 match used only as reconciliation, NOT as fill basis
"""
from __future__ import annotations

import csv
import hashlib
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path("/home/jin/code/quant/data/acquired/bx01_kospi200_rulebook_effective_dt_a0")
RAW = ROOT / "raw"
CAL_FILE = Path("/home/jin/code/quant/data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv")
EVENTS_IN = Path("/home/jin/code/quant/data/acquired/bx01_kospi200_index_event_source_a0/events_v2_xref.csv")
OUT_CYCLE = ROOT / "per_cycle_effective_dt.csv"
OUT_EVENTS = Path("/home/jin/code/quant/data/acquired/bx01_kospi200_index_event_source_a0/events_v3.csv")
OUT_RECON = Path("/home/jin/code/quant/data/acquired/bx01_kospi200_index_event_source_a0/reconciliation_v3.csv")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# Cycle plan: only 9/10 in-calendar Tier 1 cycles
TIER1_TO_DERIVE = [
    ("2021-06", "734",  "2021-05-25"),
    ("2021-12", "774",  "2021-11-24"),
    ("2022-06", "799",  "2022-05-24"),
    ("2023-06", "861",  "2023-05-18"),
    ("2023-12", "899",  "2023-11-23"),
    ("2024-06", "939",  "2024-05-24"),
    ("2024-12", "979",  "2024-11-21"),
    ("2025-06", "1015", "2025-05-27"),
    ("2025-12", "1050", "2025-11-18"),
]
TIER1_BLANK = ("2026-06", "1090", "2026-05-22")  # calendar cutoff before needed date


# Source label constants per Referee's required wording
METHODOLOGY_BASIS = "secondary_KRX_publisher_attributed_rulebook_copy__primary_KRX_access_blocked"
METHODOLOGY_RULE_TEXT = "정기변경일 = KOSPI200 선물시장 6월/12월 결제월 최종거래일의 다음 매매거래일 (Mirae 2021-11 §7.1 KRX-publisher-attributed)"
FUTURES_LTD_BASIS = "secondary_broker_hosted_KRX_attributed_derivatives_product_description__primary_KRX_access_blocked"
FUTURES_LTD_RULE_TEXT = "settlement_month_second_thursday (Hana 2020-05-25 거래설명서 p8+p15 KRX-attributed)"
CONFIDENCE = "provisional_secondary_rulebook_calendar_confirmed"
DERIVATION_METHOD = "rulebook_text_plus_local_krx_trading_calendar"
CAL_SOURCE = "data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv"

PER_ROW_CAVEAT = (
    "secondary-triangulated derivation: methodology rule from broker-hosted "
    "KRX-publisher-attributed copy (Mirae 2021-11 §7.1), futures final-trading-day "
    "rule from broker-hosted KRX-attributed derivatives product description (Hana "
    "2020-05-25 거래설명서 p8+p15); primary KRX access (index.krx.co.kr OTP path) "
    "blocked from sandbox; this is NOT a primary KRX-confirmed derivation; "
    "amendment history indicates semi-annual rule from 2019-12-11; the in-calendar "
    "lookup uses local KRX trading calendar artifact; separate primary KRX "
    "rulebook confirmation would be required before any test-design PASS"
)


def second_thursday(year: int, month: int) -> date:
    """Return the 2nd Thursday of the given month."""
    d = date(year, month, 1)
    # Find first Thursday: weekday 3 (Mon=0..Sun=6)
    while d.weekday() != 3:
        d += timedelta(days=1)
    # Second Thursday
    return d + timedelta(days=7)


def load_calendar() -> set[date]:
    df = pd.read_csv(CAL_FILE)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return set(df["date"].tolist())


def next_trading_day(d: date, cal: set[date]) -> date | None:
    candidate = d + timedelta(days=1)
    for _ in range(20):  # max 20 days forward
        if candidate in cal:
            return candidate
        candidate += timedelta(days=1)
    return None


def main() -> int:
    # File sha256s for manifest reference
    mirae_v2_sha = sha256_file(RAW / "miraeasset_kospi200_methodology_v2.pdf")
    hana_sha = sha256_file(RAW / "hana_listed_derivatives_trade_description.pdf")
    print(f"Mirae v2 sha = {mirae_v2_sha[:16]}...")
    print(f"Hana sha     = {hana_sha[:16]}...")

    cal = load_calendar()
    print(f"calendar coverage: {min(cal)} .. {max(cal)} (n={len(cal)})\n")

    # Build per-cycle table
    rows = []
    for cycle, bbsseq, regdt in TIER1_TO_DERIVE:
        yr = int(cycle[:4])
        mo = int(cycle[5:7])
        last_trade_day = second_thursday(yr, mo)
        in_cal = last_trade_day in cal
        effective_dt = next_trading_day(last_trade_day, cal)

        # Sanity: should always be ≤ 7 days after the Thursday
        if effective_dt is None:
            confidence = "blocked_calendar_lookup_failed"
            caveat = PER_ROW_CAVEAT + "; ERROR: next_trading_day lookup returned None (calendar gap)"
        else:
            gap = (effective_dt - last_trade_day).days
            if gap > 4:
                confidence = "ambiguous_long_gap_after_futures_last_trade_day"
                caveat = PER_ROW_CAVEAT + f"; WARN: {gap}d gap between futures last-trade day and effective_dt — possible holiday cluster"
            else:
                confidence = CONFIDENCE
                caveat = PER_ROW_CAVEAT

        rows.append({
            "review_cycle": cycle,
            "bbs_seq": bbsseq,
            "announcement_dt": regdt,
            "methodology_source_id": "miraeasset_kospi200_methodology_v2.pdf",
            "methodology_version_dt": "2021-11 (filename timestamp; KRX-publisher attribution)",
            "methodology_rule_section": "§7.1 (page 9)",
            "methodology_rule_text_summary": METHODOLOGY_RULE_TEXT,
            "methodology_basis_class": METHODOLOGY_BASIS,
            "futures_ltd_source_id": "hana_listed_derivatives_trade_description.pdf",
            "futures_ltd_version_dt": "2020-05-25 (KRX-attributed derivatives product description)",
            "futures_ltd_rule_section": "p8 + p15",
            "futures_ltd_rule_text_summary": FUTURES_LTD_RULE_TEXT,
            "futures_ltd_basis_class": FUTURES_LTD_BASIS,
            "futures_last_trade_day_computed": last_trade_day.isoformat(),
            "futures_last_trade_day_in_calendar": "yes" if in_cal else "no",
            "calendar_source": CAL_SOURCE,
            "derivation_method": DERIVATION_METHOD,
            "effective_dt": effective_dt.isoformat() if effective_dt else "",
            "effective_dt_confidence": confidence,
            "effective_dt_caveat": caveat,
        })
        print(f"  {cycle}: 2nd Thu={last_trade_day} (in_cal={in_cal}) → effective_dt={effective_dt}")

    # 2026-06 blank row per Referee Q2
    rows.append({
        "review_cycle": "2026-06",
        "bbs_seq": "1090",
        "announcement_dt": "2026-05-22",
        "methodology_source_id": "(rule would apply: methodology + futures_ltd rules same as 9 derived)",
        "methodology_version_dt": "(would be same)",
        "methodology_rule_section": "(would be same)",
        "methodology_rule_text_summary": METHODOLOGY_RULE_TEXT,
        "methodology_basis_class": METHODOLOGY_BASIS,
        "futures_ltd_source_id": "hana_listed_derivatives_trade_description.pdf",
        "futures_ltd_version_dt": "(would be same)",
        "futures_ltd_rule_section": "(would be same)",
        "futures_ltd_rule_text_summary": FUTURES_LTD_RULE_TEXT,
        "futures_ltd_basis_class": FUTURES_LTD_BASIS,
        "futures_last_trade_day_computed": "2026-06-11 (computable from rule)",
        "futures_last_trade_day_in_calendar": "no (calendar cutoff 2026-05-22)",
        "calendar_source": CAL_SOURCE,
        "derivation_method": DERIVATION_METHOD,
        "effective_dt": "",
        "effective_dt_confidence": "blocked_calendar_coverage_cutoff",
        "effective_dt_caveat": (
            "calendar_coverage_cutoff_2026-05-22__effective_dt_not_computed__"
            "secondary_press_reconciliation_suggests_2026-06-12_but_primary_calendar_support_missing; "
            "calendar fetch not authorized in this phase per Referee Q2 directive"
        ),
    })

    # Write per_cycle_effective_dt.csv
    cols = list(rows[0].keys())
    with OUT_CYCLE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {len(rows)} rows to {OUT_CYCLE}")

    # Build cycle → effective_dt lookup
    cycle_to_eff = {r["review_cycle"]: (r["effective_dt"], r["methodology_basis_class"],
                                          r["futures_ltd_basis_class"],
                                          r["effective_dt_confidence"],
                                          r["effective_dt_caveat"]) for r in rows}

    # Enrich events_v2_xref.csv → events_v3.csv
    if not EVENTS_IN.exists():
        print(f"ERROR: events_v2_xref.csv not found at {EVENTS_IN}")
        return 2
    in_rows = list(csv.DictReader(EVENTS_IN.open(encoding="utf-8")))
    print(f"loaded {len(in_rows)} events_v2_xref rows")

    new_cols = ["effective_dt_filled",
                "effective_dt_methodology_basis_class",
                "effective_dt_futures_ltd_basis_class",
                "effective_dt_confidence_v3",
                "effective_dt_caveat_v3"]
    out_cols = list(in_rows[0].keys()) + new_cols

    filled_count = 0
    blank_count = 0
    not_applicable_count = 0
    for r in in_rows:
        cycle = r.get("review_cycle", "")
        if cycle in cycle_to_eff:
            eff, mbasis, fbasis, conf, cav = cycle_to_eff[cycle]
            r["effective_dt_filled"] = eff
            r["effective_dt_methodology_basis_class"] = mbasis
            r["effective_dt_futures_ltd_basis_class"] = fbasis
            r["effective_dt_confidence_v3"] = conf
            r["effective_dt_caveat_v3"] = cav
            if eff:
                filled_count += 1
            else:
                blank_count += 1
        else:
            r["effective_dt_filled"] = ""
            r["effective_dt_methodology_basis_class"] = ""
            r["effective_dt_futures_ltd_basis_class"] = ""
            r["effective_dt_confidence_v3"] = "not_applicable_cycle_out_of_rulebook_phase_scope"
            r["effective_dt_caveat_v3"] = (
                "skeleton or non-rulebook-phase row; effective_dt fill not in scope"
            )
            not_applicable_count += 1

    with OUT_EVENTS.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_cols, lineterminator="\n")
        w.writeheader()
        w.writerows(in_rows)
    print(f"wrote {len(in_rows)} rows to {OUT_EVENTS}")
    print(f"  filled (high-confidence + provisional secondary): {filled_count}")
    print(f"  blank (2026-06 cutoff or other):                  {blank_count}")
    print(f"  not_applicable (out of rulebook phase scope):      {not_applicable_count}")

    # Reconciliation v3
    from collections import Counter
    with OUT_RECON.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["section", "key", "value", "note"])
        w.writerow(["", "", "", ""])
        w.writerow(["GLOBAL", "total_events_v3_rows", len(in_rows), ""])
        w.writerow(["GLOBAL", "effective_dt_filled_rows", filled_count,
                    "provisional secondary basis; rule-cited; calendar-confirmed"])
        w.writerow(["GLOBAL", "effective_dt_blank_rows", blank_count,
                    "includes 2026-06 cycle calendar cutoff"])
        w.writerow(["GLOBAL", "effective_dt_not_applicable_rows", not_applicable_count,
                    "skeleton or out-of-rulebook-scope rows"])
        w.writerow(["", "", "", ""])
        w.writerow(["PER_CYCLE", "review_cycle", "effective_dt_filled", "confidence"])
        for r in rows:
            w.writerow(["PER_CYCLE", r["review_cycle"], r["effective_dt"] or "(blank)",
                        r["effective_dt_confidence"]])
        w.writerow(["", "", "", ""])
        w.writerow(["BASIS", "methodology_source_id", "miraeasset_kospi200_methodology_v2.pdf",
                    f"sha256={mirae_v2_sha}"])
        w.writerow(["BASIS", "methodology_basis_class", METHODOLOGY_BASIS, ""])
        w.writerow(["BASIS", "futures_ltd_source_id", "hana_listed_derivatives_trade_description.pdf",
                    f"sha256={hana_sha}"])
        w.writerow(["BASIS", "futures_ltd_basis_class", FUTURES_LTD_BASIS, ""])
        w.writerow(["BASIS", "calendar_source", CAL_SOURCE,
                    f"coverage 2010-01-04 .. 2026-05-22"])
        w.writerow(["", "", "", ""])
        w.writerow(["RECONCILIATION_NOTE", "key", "value", "note"])
        w.writerow(["RECONCILIATION_NOTE", "2026-06_press_release_match",
                    "press_says_2026-06-12; rule_computes_2026-06-11_Thu_plus_1_trading_day=2026-06-12",
                    "RECONCILIATION ONLY — not used as fill basis (per Referee Q2)"])
        w.writerow(["RECONCILIATION_NOTE", "primary_KRX_access",
                    "BLOCKED (index.krx.co.kr OTP path) — same blocker as BX01-source-A0",
                    "secondary-triangulated derivation is provisional"])
        w.writerow(["", "", "", ""])
        w.writerow(["RESIDUAL_BLOCKERS", "key", "value", "note"])
        w.writerow(["RESIDUAL_BLOCKERS", "primary_KRX_rulebook_access", "blocked", "blocker"])
        w.writerow(["RESIDUAL_BLOCKERS", "primary_KRX_derivatives_spec_access", "blocked", "blocker"])
        w.writerow(["RESIDUAL_BLOCKERS", "2026-06_calendar_cutoff", "blocked", "blocker"])
        w.writerow(["RESIDUAL_BLOCKERS", "tier1_skeleton_only_cycles_2018-06_2019-06_2020-06_2020-12",
                    "4 cycles still skeleton (carry-forward from attachment-parse phase)",
                    "blocker for cycle-complete TEST design"])
        w.writerow(["RESIDUAL_BLOCKERS", "regular_special_conflation_class_b_rows",
                    "preserved as caveat from attachment-parse phase", "blocker"])

    print(f"wrote {OUT_RECON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
