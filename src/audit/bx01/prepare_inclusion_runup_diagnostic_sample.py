#!/usr/bin/env python3
"""BX01-KOSPI200-INCLUSION-RUNUP-DIAGNOSTIC-BACKTEST-DESIGN-A0 — sample prep.

Per Referee ask_0015 / ask_claude_52: LOCAL-ONLY DESIGN phase. Produces sample
metadata + control-design registries ONLY. NO price reads, NO return
calculation, NO statistics, NO backtest execution.

Inputs (LOCAL ONLY, read-only):
- events_v3.csv (BX01 authoritative event artifact)
- per_cycle_effective_dt.csv (rulebook-A0 cycle effective dates)
- special_candidate_links.csv (title-enrichment secondary links)
- krx_official_calendar_2010_2026.csv (trading calendar)
- krx_pit_sector_classifications.csv (PIT sector for matched control design)
- krx_listed_monthly_snapshots_2010_2026.csv (PIT listing for ticker resolution)

Outputs:
- inclusion_runup_sample_preview.csv  (main sample)
- negative_control_candidate_registry.csv  (deletion-side, registry only)
- control_matching_design_registry.csv  (matched control design per event)
- sample_exclusion_log.csv  (every excluded row with reason)
- manifest.csv  (10-col provenance schema)
"""
from __future__ import annotations

import csv
import hashlib
import re
from datetime import date, timedelta
from pathlib import Path

# ---- Paths ------------------------------------------------------------------

PROJ = Path("/home/jin/code/quant")
OUT_DIR = PROJ / "data/acquired/bx01_kospi200_inclusion_runup_diagnostic_design_a0"
EVENTS_V3 = PROJ / "data/acquired/bx01_kospi200_index_event_source_a0/events_v3.csv"
SPECIALS_LINKS = PROJ / "data/acquired/bx01_kospi200_specials_title_enrichment_a0/special_candidate_links.csv"
PER_CYCLE = PROJ / "data/acquired/bx01_kospi200_rulebook_effective_dt_a0/per_cycle_effective_dt.csv"
CAL_FILE = PROJ / "data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv"
SECTOR_FILE = PROJ / "data/processed/krx_pit_sector_classifications.csv"
LISTING_FILE = PROJ / "data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv"

# ---- In-scope cycles --------------------------------------------------------
# Per directive: Class A 2021-06 + Class B 2021-12..2025-12, EXCLUDE 2026-06 +
# bridge 2022-12 + 4 missing Tier 1 + deletion-side.
IN_SCOPE_CYCLES = {
    "2021-06", "2021-12", "2022-06", "2023-06", "2023-12",
    "2024-06", "2024-12", "2025-06", "2025-12",
}
EXCLUDED_CYCLES_REASON = {
    "2026-06": "effective_dt_rulebook_derived_blank_calendar_cutoff",
    "2022-12": "bridge_only_not_in_tier1",
    "2018-06": "skeleton_only_hwp_deferred_tier1",
    "2019-06": "skeleton_only_hwp_deferred_tier1",
    "2020-06": "skeleton_only_broker_pdf_deferred_tier1",
    "2020-12": "skeleton_only_broker_pdf_deferred_tier1",
    "2018-12": "skeleton_only_hwp_deferred_not_in_tier1",
    "2019-12": "skeleton_only_hwp_deferred_not_in_tier1",
}


# ---- Helpers ----------------------------------------------------------------

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_calendar(p: Path) -> list[date]:
    out: list[date] = []
    with p.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                d = date.fromisoformat(row["date"])
                out.append(d)
            except Exception:
                pass
    return sorted(set(out))


def next_trading_day(d: date, cal_set: set[date]) -> date | None:
    """Return first trading day strictly after d. None if not in calendar."""
    if not cal_set:
        return None
    cand = d + timedelta(days=1)
    last_cal = max(cal_set)
    while cand <= last_cal:
        if cand in cal_set:
            return cand
        cand += timedelta(days=1)
    return None


def shift_trading_days(d: date, n: int, cal_sorted: list[date]) -> date | None:
    """Shift d by n trading days using the sorted calendar list. Return None
    if shift falls outside calendar coverage."""
    if d not in set(cal_sorted):
        # Round to nearest available trading day
        if not cal_sorted or d < cal_sorted[0] or d > cal_sorted[-1]:
            return None
        i = next((j for j, c in enumerate(cal_sorted) if c >= d), None)
        if i is None:
            return None
    else:
        i = cal_sorted.index(d)
    j = i + n
    if j < 0 or j >= len(cal_sorted):
        return None
    return cal_sorted[j]


def latest_sector_snapshot_on_or_before(snapshot_dates_sorted: list[str], target_date: str) -> str | None:
    """Return the latest sector snapshot YYYYMMDD on or before target_date."""
    target = target_date.replace("-", "")
    last = None
    for d in snapshot_dates_sorted:
        if d <= target:
            last = d
        else:
            break
    return last


# ---- Main -------------------------------------------------------------------

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load calendar
    cal_sorted = load_calendar(CAL_FILE)
    cal_set = set(cal_sorted)
    print(f"calendar: {len(cal_sorted)} trading days "
          f"{cal_sorted[0]}..{cal_sorted[-1]}")

    # Load special_candidate_links (title-enrichment)
    title_link = {}  # event_id -> dict
    if SPECIALS_LINKS.exists():
        with SPECIALS_LINKS.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                eid = r["matching_class_b_event_id"]
                title_link[eid] = r
    print(f"title-linked events: {len(title_link)}")

    # Load sector mapping (PIT) for matched-control design
    sector_snapshot_dates: list[str] = []
    sector_by_date_ticker: dict[tuple[str, str], str] = {}
    if SECTOR_FILE.exists():
        with SECTOR_FILE.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                sd = r["date"]
                sector_by_date_ticker[(sd, r["종목코드"])] = r.get("업종명", "")
        sector_snapshot_dates = sorted({d for d, _ in sector_by_date_ticker.keys()})
        print(f"sector snapshots: {len(sector_snapshot_dates)}")

    # Load events_v3
    events: list[dict] = []
    with EVENTS_V3.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            events.append(r)
    print(f"events_v3: {len(events)} rows")

    # ---- Apply scope rules ----
    main_sample: list[dict] = []
    neg_ctrl: list[dict] = []
    excluded: list[dict] = []
    excl_reasons_counter: dict[str, int] = {}

    def excl(row: dict, reason: str, role_note: str = "excluded_with_reason"):
        excluded.append({
            "event_id": row.get("event_id", ""),
            "review_cycle": row.get("review_cycle", ""),
            "ticker": row.get("ticker", ""),
            "side": row.get("side", ""),
            "source_record_type": row.get("source_record_type", ""),
            "exclusion_reason": reason,
        })
        excl_reasons_counter[reason] = excl_reasons_counter.get(reason, 0) + 1

    for r in events:
        srt = r.get("source_record_type", "")
        side = r.get("side", "")
        cycle = r.get("review_cycle", "")
        eff_design = r.get("effective_dt_rulebook_derived", "").strip()
        ticker = r.get("ticker", "").strip()
        company = r.get("company_name", "").strip()
        ann = r.get("announcement_dt", "").strip()
        idx = r.get("index_name", "").strip()
        eid = r.get("event_id", "")

        # Skip skeleton
        if "skeleton_only" in srt or "notice_level_skeleton" in srt:
            excl(r, "skeleton_only_or_notice_level_only_not_constituent_level"); continue

        # Constituent-level only
        if "constituent_level" not in srt:
            excl(r, "not_constituent_level"); continue

        if not ticker:
            excl(r, "ticker_missing"); continue

        # Exclude excluded cycles per directive
        if cycle in EXCLUDED_CYCLES_REASON:
            excl(r, f"cycle_excluded__{EXCLUDED_CYCLES_REASON[cycle]}"); continue

        # In-scope cycles only
        if cycle not in IN_SCOPE_CYCLES:
            excl(r, f"cycle_not_in_scope__{cycle or 'blank'}"); continue

        # Side: addition for main; deletion for neg_ctrl
        if side == "addition":
            if not eff_design:
                excl(r, "addition_blank_effective_dt_rulebook_derived"); continue
        elif side == "deletion":
            # Go to negative control registry; not main sample
            pass
        else:
            excl(r, f"side_unsupported__{side or 'blank'}"); continue

        # Tag caveats
        if srt == "constituent_level_direct_from_change_detail_sheet":
            src_role = "class_a_direct_primary"
            eff_conf = "primary" if eff_design else "blocked_or_blank"
        elif srt == "constituent_level_derived_from_consecutive_official_snapshot_diff":
            # Determine title-link status
            if eid in title_link:
                src_role = "class_b_title_linked_secondary"
            else:
                src_role = "class_b_snapshot_diff_derived"
            eff_conf = "provisional_secondary_rulebook_derived" if eff_design else "blocked_or_blank"
        else:
            excl(r, f"unknown_source_record_type__{srt}"); continue

        title_status = "high_secondary_triangulated" if eid in title_link else "no_title_link"
        if src_role == "class_a_direct_primary":
            title_status = "not_applicable"  # Class A is primary; title link concept not applicable

        # conflation_status per cycle
        UNRESOLVED_CYCLES = {"2021-12", "2022-06", "2024-06"}
        if cycle in UNRESOLVED_CYCLES:
            conf_status = "partially_separated" if (eid in title_link and side == "addition") else "unresolved"
        elif cycle == "2021-06":
            conf_status = "clean"  # Class A is direct/primary
        else:
            conf_status = "clean"

        if side == "deletion":
            sample_role = "negative_control_candidate_only"
        else:
            sample_role = "main_inclusion_addition_sample"

        # Compute timing labels (no prices!)
        entry_dt = next_trading_day(date.fromisoformat(ann), cal_set) if ann else None
        try:
            eff_dt_obj = date.fromisoformat(eff_design) if eff_design else None
        except Exception:
            eff_dt_obj = None

        # Exit candidates (labels only, no prices)
        try:
            ann_dt_obj = date.fromisoformat(ann)
            t_plus_5 = shift_trading_days(ann_dt_obj, 5, cal_sorted)
            t_plus_10 = shift_trading_days(ann_dt_obj, 10, cal_sorted)
        except Exception:
            t_plus_5 = t_plus_10 = None
        eff_minus_1 = None
        if eff_dt_obj:
            eff_minus_1 = shift_trading_days(eff_dt_obj, -1, cal_sorted)

        # PIT sector for matched-control design (label only)
        sector = ""
        if sector_snapshot_dates and ticker and ann:
            sd = latest_sector_snapshot_on_or_before(sector_snapshot_dates, ann)
            if sd:
                sector = sector_by_date_ticker.get((sd, ticker), "")

        out_row = {
            "event_id": eid,
            "review_cycle": cycle,
            "ticker": ticker,
            "company_name": company,
            "index_name": idx,
            "side": side,
            "announcement_dt": ann,
            "effective_dt_design": eff_design,
            "entry_dt_design": entry_dt.isoformat() if entry_dt else "",
            "exit_dt_candidate_T_plus_5": t_plus_5.isoformat() if t_plus_5 else "",
            "exit_dt_candidate_T_plus_10": t_plus_10.isoformat() if t_plus_10 else "",
            "exit_dt_candidate_effective_minus_1": eff_minus_1.isoformat() if eff_minus_1 else "",
            "pit_sector_label_for_matched_control_design": sector,
            "source_record_type": src_role,
            "effective_dt_confidence": eff_conf,
            "title_link_status": title_status,
            "conflation_status": conf_status,
            "sample_role": sample_role,
            "caveat": (
                "design-only timing labels; no price/return computed; "
                "canonical effective_dt remains blank in events_v3 and not modified here; "
                "effective_dt_design uses provisional secondary rulebook basis except Class A direct; "
                "PIT sector label is for matched-control design only, not used for return calc"
            ),
        }

        if side == "deletion":
            neg_ctrl.append(out_row)
        else:
            main_sample.append(out_row)

    print(f"\nmain inclusion-addition sample: {len(main_sample)}")
    print(f"negative-control candidate registry: {len(neg_ctrl)}")
    print(f"excluded rows: {len(excluded)}")
    print(f"  by reason: {excl_reasons_counter}")

    # ---- Write CSVs ----
    cols_main = list(main_sample[0].keys()) if main_sample else []
    with (OUT_DIR / "inclusion_runup_sample_preview.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols_main, lineterminator="\n")
        w.writeheader()
        w.writerows(main_sample)

    cols_neg = list(neg_ctrl[0].keys()) if neg_ctrl else cols_main
    with (OUT_DIR / "negative_control_candidate_registry.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols_neg, lineterminator="\n")
        w.writeheader()
        w.writerows(neg_ctrl)

    # control matching design registry — per-event spec, not selected peers
    with (OUT_DIR / "control_matching_design_registry.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow([
            "event_id", "ticker", "company_name", "announcement_dt", "review_cycle",
            "match_dim_1", "match_dim_2", "match_dim_3", "match_dim_4",
            "match_dim_5", "control_pool_definition",
            "exclusion_from_pool", "design_caveat",
        ])
        for r in main_sample:
            w.writerow([
                r["event_id"], r["ticker"], r["company_name"], r["announcement_dt"], r["review_cycle"],
                "date=announcement_dt",
                f"sector={r['pit_sector_label_for_matched_control_design']}",
                "market_cap_bucket=defer_to_execution_phase_via_PIT_listing_panel",
                "liquidity_bucket=defer_to_execution_phase_via_PIT_volume_panel",
                "index_membership=KOSPI200_constituent_status_at_announcement_dt-1",
                "pool=all_KOSPI_listed_non_KOSPI200_on_announcement_dt-1_with_same_sector_and_size_quintile_and_liquidity_quintile",
                f"exclude={r['ticker']}__self_inclusion",
                "design-only; no peer selected here; execution phase would draw via deterministic PIT panel join",
            ])

    # Exclusion log
    cols_excl = ["event_id", "review_cycle", "ticker", "side", "source_record_type", "exclusion_reason"]
    with (OUT_DIR / "sample_exclusion_log.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols_excl, lineterminator="\n")
        w.writeheader()
        w.writerows(excluded)

    # Manifest
    with (OUT_DIR / "manifest.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow([
            "filename", "local_path", "bytes", "sha256", "source_url",
            "final_url", "retrieved_at_utc", "source_class",
            "license_note", "parse_status",
        ])
        for name in [
            "inclusion_runup_sample_preview.csv",
            "negative_control_candidate_registry.csv",
            "control_matching_design_registry.csv",
            "sample_exclusion_log.csv",
        ]:
            p = OUT_DIR / name
            if p.exists():
                w.writerow([
                    name, str(p), p.stat().st_size, sha256_file(p),
                    "(derived from local BX01 artifacts)",
                    "(derived from local BX01 artifacts)",
                    "(local derivation, not a network fetch)",
                    "design_artifact_derived_locally",
                    "internal_research_audit_use_only",
                    "design_only_no_returns_no_statistics",
                ])

    # ---- Counts summary by cycle / role / source_record_type ----
    by_cycle: dict[str, dict[str, int]] = {}
    for r in main_sample:
        c = r["review_cycle"]
        by_cycle.setdefault(c, {"total": 0, "class_a_direct_primary": 0,
                                 "class_b_snapshot_diff_derived": 0,
                                 "class_b_title_linked_secondary": 0})
        by_cycle[c]["total"] += 1
        by_cycle[c][r["source_record_type"]] += 1

    print("\nmain sample by cycle:")
    for c in sorted(by_cycle):
        print(f"  {c}: total={by_cycle[c]['total']:>3d} "
              f"  A={by_cycle[c]['class_a_direct_primary']:>2d} "
              f"  B_snap={by_cycle[c]['class_b_snapshot_diff_derived']:>2d} "
              f"  B_title={by_cycle[c]['class_b_title_linked_secondary']:>2d}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
