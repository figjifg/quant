#!/usr/bin/env python3
"""BX01-attachment-parse final pass: rewrite coverage_matrix.csv to reflect
the post-rename high-confidence cycle mapping.

Per Referee 2026-05-31 final-pass requirement (#2):
- Current coverage_matrix.csv is a PRE-RENAME artifact; it carries old filenames
  and `needs_user_cycle_confirmation` confidence.
- The post-rename state has high-confidence mappings (user renamed all files with
  date-coded `YY.M(M).ext` form).
- Action: write coverage_matrix_final.csv with current state, preserve the
  pre-rename artifact under coverage_matrix_prerename.csv for transparency.

Coverage matrix columns (per Referee guidance):
  target_bbs_seq, expected_cycle, user_supplied_file, source_class, sha256,
  mapping_confidence, basis_for_mapping, parse_eligibility, actual_parse_status,
  caveat.
"""
from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path

import openpyxl

OUT_DIR = Path("/home/jin/code/quant/data/acquired/bx01_kospi200_index_event_source_a0")
SRC = Path("/home/jin/code/quant/research_input_data/정기변경")
OLD = OUT_DIR / "coverage_matrix.csv"
PRE_RENAME_COPY = OUT_DIR / "coverage_matrix_prerename.csv"
FINAL = OUT_DIR / "coverage_matrix_final.csv"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# (target_bbs_seq, expected_cycle, expected_reg_dt, user_file, source_class, basis, parse_eligibility, parse_status, caveat)
# Plus extra non-Tier1 rows for bridge / out-of-tier1
ROWS = [
    # Tier 1
    ("555",  "2018-06", "2018-05-24", "18.6.hwp",  "C_KRX_hwp_press_release_body_text",
     "user_renamed_filename_to_18.6_authoritative_cycle_mapping_per_Referee_2026-05-30_clarification",
     "deferred_hwp_parse_out_of_scope_this_phase",
     "skeleton_only_not_parsed",
     "hwp body parser not in scope per Referee 2026-05-30; evidence-only; separate user+Referee decision required"),
    ("613",  "2019-06", "2019-05-21", "19.6.hwp",  "C_KRX_hwp_press_release_body_text",
     "user_renamed_filename_to_19.6_authoritative_cycle_mapping",
     "deferred_hwp_parse_out_of_scope_this_phase", "skeleton_only_not_parsed",
     "hwp body parser not in scope; evidence-only"),
    ("667",  "2020-06", "2020-05-27", "20.6.pdf",  "D_secondary_broker_pdf_user_supplied",
     "user_renamed_filename_to_20.6_authoritative_cycle_mapping",
     "deferred_broker_pdf_secondary_only_per_Referee", "skeleton_only_not_parsed",
     "broker publication; secondary source authority; not record-of-record per Referee 2026-05-30"),
    ("696",  "2020-12", "2020-11-25", "20.12.pdf", "D_secondary_broker_pdf_user_supplied",
     "user_renamed_filename_to_20.12_authoritative_cycle_mapping",
     "deferred_broker_pdf_secondary_only_per_Referee", "skeleton_only_not_parsed",
     "broker publication; secondary source authority"),
    ("734",  "2021-06", "2021-05-25", "21.6.xlsx", "A_KRX_xlsx_with_change_detail",
     "user_renamed_filename_to_21.6_authoritative_cycle_mapping; also '21.06+KOSPI...공지파일.xlsx' identical sha=af327b2c2bef… kept as duplicate",
     "primary_direct_parse_class_a_eligible", "parsed_direct_change_detail_sheet_kospi200_변경내역",
     "+5 add / -7 del; independent secondary cross-check matches news summary; 5/12 ticker confirmed in PIT listing"),
    ("774",  "2021-12", "2021-11-24", "21.12.xlsx", "B_KRX_xlsx_snapshot_only",
     "user_renamed_filename_to_21.12_authoritative_cycle_mapping",
     "secondary_derived_class_b_eligible_with_consecutive_snapshot_diff",
     "parsed_via_consecutive_official_snapshot_diff_vs_21.6_snapshot",
     "+10 add / -10 del; CONFLATION CAVEAT: includes 크래프톤/카카오뱅크 (2021-08 special) + 카카오페이 (2021-11 special)"),
    ("799",  "2022-06", "2022-05-24", "22.6.xlsx",  "B_KRX_xlsx_snapshot_only",
     "user_renamed_filename_to_22.6_authoritative_cycle_mapping",
     "secondary_derived_class_b_eligible", "parsed_via_consecutive_official_snapshot_diff_vs_21.12_snapshot",
     "+8 add / -8 del; CONFLATION CAVEAT: includes LG에너지솔루션 (2022-01 special)"),
    ("861",  "2023-06", "2023-05-18", "23.6.xlsx",  "B_KRX_xlsx_snapshot_only",
     "user_renamed_filename_to_23.6_authoritative_cycle_mapping",
     "secondary_derived_class_b_eligible", "parsed_via_consecutive_official_snapshot_diff_vs_22.12_bridge_snapshot",
     "+5 add / -5 del; bridged via 22.12 snapshot (not in Tier 1)"),
    ("899",  "2023-12", "2023-11-23", "23.12.xlsx", "B_KRX_xlsx_snapshot_only",
     "user_renamed_filename_to_23.12_authoritative_cycle_mapping",
     "secondary_derived_class_b_eligible", "parsed_via_consecutive_official_snapshot_diff_vs_23.6_snapshot",
     "+8 add / -8 del; CONFLATION CAVEAT: includes 에코프로머티 (2023-12 special)"),
    ("939",  "2024-06", "2024-05-24", "24.6.xlsx",  "B_KRX_xlsx_snapshot_only",
     "user_renamed_filename_to_24.6_authoritative_cycle_mapping",
     "secondary_derived_class_b_eligible", "parsed_via_consecutive_official_snapshot_diff_vs_23.12_snapshot",
     "+8 add / -8 del; CONFLATION CAVEAT: includes 포스코DX (2024-01 special)"),
    ("979",  "2024-12", "2024-11-21", "24.12.xlsx", "B_KRX_xlsx_snapshot_only",
     "user_renamed_filename_to_24.12_authoritative_cycle_mapping",
     "secondary_derived_class_b_eligible", "parsed_via_consecutive_official_snapshot_diff_vs_24.6_snapshot",
     "+5 add / -5 del"),
    ("1015", "2025-06", "2025-05-27", "25.6.xlsx",  "B_KRX_xlsx_snapshot_only",
     "user_renamed_filename_to_25.6_authoritative_cycle_mapping",
     "secondary_derived_class_b_eligible", "parsed_via_consecutive_official_snapshot_diff_vs_24.12_snapshot",
     "+9 add / -9 del"),
    ("1050", "2025-12", "2025-11-18", "25.12.xlsx", "B_KRX_xlsx_snapshot_only",
     "user_renamed_filename_to_25.12_authoritative_cycle_mapping",
     "secondary_derived_class_b_eligible", "parsed_via_consecutive_official_snapshot_diff_vs_25.6_snapshot",
     "+7 add / -8 del; KOSPI 200 row count 199 (delisting unfilled until next cycle)"),
    ("1090", "2026-06", "2026-05-22", "26.6.xlsx",  "B_KRX_xlsx_snapshot_only",
     "user_renamed_filename_to_26.6_authoritative_cycle_mapping",
     "secondary_derived_class_b_eligible", "parsed_via_consecutive_official_snapshot_diff_vs_25.12_snapshot",
     "+5 add / -5 del; KOSPI 200 row count 199"),
    # Bridge / not-in-Tier1
    ("",     "2018-12", "(not in Tier 1)", "18.12.hwp", "C_KRX_hwp_press_release_body_text",
     "user_renamed_filename; not in Tier 1 target list",
     "deferred_hwp_parse_out_of_scope_and_not_in_tier1", "skeleton_only_not_parsed",
     "hwp body parser deferred + not in Tier 1; evidence-only"),
    ("",     "2019-12", "(not in Tier 1)", "19.12.hwp", "C_KRX_hwp_press_release_body_text",
     "user_renamed_filename; not in Tier 1 target list",
     "deferred_hwp_parse_out_of_scope_and_not_in_tier1", "skeleton_only_not_parsed",
     "hwp body parser deferred + not in Tier 1; evidence-only"),
    ("",     "2022-12", "(not in Tier 1)", "22.12.xlsx", "B_KRX_xlsx_snapshot_only_bridge",
     "user_renamed_filename; not in Tier 1 target list; used only as bridge for 23-6 derivation",
     "bridge_only_used_for_consecutive_diff_continuity_not_emitted_as_tier1_event",
     "parsed_as_snapshot_used_as_diff_bridge_vs_22.6_and_23.6",
     "+1 add / -1 del (bridge events; flagged tier1_status=bridge_only_not_in_tier1 in events_v2)"),
]


def main() -> int:
    # 1) Preserve old coverage_matrix as prerename version
    if OLD.exists() and not PRE_RENAME_COPY.exists():
        shutil.copy(OLD, PRE_RENAME_COPY)
        print(f"preserved old coverage matrix as: {PRE_RENAME_COPY}")

    # 2) Write final coverage matrix
    cols = ["target_bbs_seq", "expected_cycle", "expected_reg_dt",
            "user_supplied_file", "sha256", "source_class",
            "mapping_confidence", "basis_for_mapping",
            "parse_eligibility", "actual_parse_status", "caveat"]
    out = []
    for bbs_seq, cycle, regdt, fn, cls, basis, elig, status, caveat in ROWS:
        p = SRC / fn
        if not p.exists():
            print(f"MISSING: {p}")
            continue
        sha = sha256_file(p)
        # All post-rename mappings = high_confidence per Referee
        confidence = "high (user_renamed_filename_to_cycle_authoritative_per_Referee_2026-05-30_clarification)"
        out.append({
            "target_bbs_seq": bbs_seq,
            "expected_cycle": cycle,
            "expected_reg_dt": regdt,
            "user_supplied_file": fn,
            "sha256": sha,
            "source_class": cls,
            "mapping_confidence": confidence,
            "basis_for_mapping": basis,
            "parse_eligibility": elig,
            "actual_parse_status": status,
            "caveat": caveat,
        })

    with FINAL.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} rows to {FINAL}")

    # Summary
    from collections import Counter
    print("\nby source_class:")
    for k, v in Counter(r["source_class"] for r in out).items():
        print(f"  {v}  {k}")
    print("\nby actual_parse_status:")
    for k, v in Counter(r["actual_parse_status"] for r in out).items():
        print(f"  {v}  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
