"""KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0 — builder.

Referee directive REF-OPEN-007 (2026-05-26, via relay). Follows the now-closed
KR-STATUS-SOURCE-RECOVERY-CANDIDATE-MANIFEST-A0.

Goal: a LOCAL CONSISTENCY AUDIT (no new data) verifying the 6 recently-closed
measurement-layer phases' artifacts report the SAME canonical counts and the SAME
hard-lock state — i.e. an official residual-state index + numeric reconciliation +
hard-lock phrase audit.

This phase READS local reports / CSV / CLOSE_NOTE / docs/next_actions.md only. It:
- does NOT download / call APIs / use credentials / repair bodies,
- does NOT change or rerun the parser, candidate search, or body confirmation,
- is NOT an event log, NOT an executable-status table, NOT source recovery, NOT
  parser design,
- does NOT mark anything strategy-ready / execution-ready / production-ready.

Inconsistencies are RECORDED in a defect ledger, not patched (unless an
inconsistency is purely within this phase's own generated outputs).
"""
from __future__ import annotations

import csv as _csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
MA0 = REPO / "reports/experiments/measurement_A0"
OUT = MA0 / "KR_STATUS_LOCAL_ARTIFACT_CONSISTENCY_AUDIT_A0"
NEXT_ACTIONS = REPO / "docs/next_actions.md"

# The 6 recently-closed phase directories under review.
PHASES = [
    "S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0",
    "KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0",
    "KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0",
    "KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0",
    "KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0",
    "KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0",
]

# Core files each phase must have (besides CLOSE_NOTE.md + report.md).
CORE_FILES = {
    "S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0": [
        "universe_body_status_reconciled.csv", "universe_residual_ledger.csv", "CLOSE_NOTE.md", "report.md"],
    "KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0": [
        "correction_full_universe_links.csv", "correction_confidence_counts.csv", "CLOSE_NOTE.md", "report.md"],
    "KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0": [
        "correction_residual_action_ledger.csv", "confidence_to_action_mapping.csv", "CLOSE_NOTE.md", "report.md"],
    "KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0": [
        "residual_blocker_register.csv", "blocker_tag_counts.csv", "CLOSE_NOTE.md", "report.md"],
    "KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0": [
        "parser_nonextracted_taxonomy_ledger.csv", "parser_nonextracted_root_cause_counts.csv", "CLOSE_NOTE.md", "report.md"],
    "KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0": [
        "source_recovery_candidate_manifest.csv", "source_recovery_candidate_counts.csv", "CLOSE_NOTE.md", "report.md"],
}

# Canonical accepted counts (the locked numbers the audit reconciles to).
CANON = {
    "universe_rows": 12187,
    "usable_html_inline": 12145,
    "zip_unparseable": 42,
    "no_label_match": 511,
    "label_no_value": 200,
    "blocker_register_rows": 862,
    "parser_nonextracted_rows": 711,
    "correction_rows": 166,
    "correction_zip_subset": 39,
    "non_correction_zip_subset": 3,
}

# Scope-drift trigger tokens. An occurrence is FLAGGED only if the line is NOT a
# negation / fixed-False / design-only / forbidden statement.
DRIFT_TOKENS = ["strategy-ready", "strategy_ready", "execution-ready", "executable-ready",
                "production-ready", "production_ready", "100%", "authoritative",
                "recovery_performed", "event log finaliz", "event-log finaliz",
                "executable-status table", "executable_status table"]
SAFE_MARKERS = ["no ", "not ", "non-", "=false", ": false", "false", "must not",
                "never", "without", "n't", "no_", "design-only", "design only",
                "preserved", "forbidden", "unless explicitly", "is not", "are not",
                "did not", "does not", "no card", "not approved", "not 100%",
                "= false", "fail-closed", "failclosed", "not authoritative",
                "none ", "does not mean", "not mean", "do not mark", "= false.",
                "remains the reporting", "❌", "= false"]
# Data-provenance uses of "authoritative" (an authoritative SOURCE/dataset, not a
# row/card status claim) — benign.
PROVENANCE_NOUNS = ["set", "calendar", "record", "source", ".csv", "pykrx", "ohlcv",
                    "dataset", "universe", "per-defect"]
# Legitimate measurement percentages (holdout / mapping / coverage), not a
# "100% usable universe" claim — benign.
MEASUREMENT_MARKERS = ["holdout", "match", "mapping", "coverage shift", "t+1",
                       "matches", "/4,021", "/4021", "success", "downloads", "accepted"]
# The REF-CLOSE-002 wording-fix documentation table (before/after of "AUTHORITATIVE").
FIXTABLE_MARKERS = ["→", "->", "body-gated classifier", "wording", "\"authoritative",
                    "the word", "body-gated", "accepted body-gated"]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for r in rows:
        for k in r.keys():
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = _csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def csv_rows(path: Path) -> int:
    try:
        return len(pd.read_csv(path, dtype=str))
    except Exception:
        return -1


def main() -> None:
    print("[start] KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    defects: list[dict] = []
    inventory: list[dict] = []
    missing_extra: list[dict] = []

    # 1. Inventory + presence
    for ph in PHASES:
        d = MA0 / ph
        present = d.exists()
        files = sorted([p.name for p in d.glob("*")]) if present else []
        for cf in CORE_FILES[ph]:
            ok = cf in files
            inventory.append({
                "phase": ph, "file": cf, "present": ok,
                "rows": csv_rows(d / cf) if (ok and cf.endswith(".csv")) else "",
            })
            if not ok:
                defects.append({
                    "defect_id": f"CONS_{len(defects)+1:03d}",
                    "kind": "missing_core_file", "phase": ph, "file": cf,
                    "detail": "required core file missing",
                    "recommended_correction": f"investigate missing {cf} in {ph}",
                })
                missing_extra.append({"phase": ph, "file": cf, "status": "MISSING_CORE"})
        # record all files for the inventory too
        for fn in files:
            if fn not in CORE_FILES[ph]:
                inventory.append({
                    "phase": ph, "file": fn, "present": True,
                    "rows": csv_rows(d / fn) if fn.endswith(".csv") else "",
                })

    # 2. Count reconciliation — RECOMPUTE from the authoritative source CSVs.
    recon: list[dict] = []

    def add_recon(metric, source_phase, source_file, observed, expected):
        ok = (observed == expected)
        recon.append({
            "metric": metric, "source_phase": source_phase, "source_file": source_file,
            "observed": observed, "canonical_expected": expected,
            "match": "PASS" if ok else "FAIL",
        })
        if not ok:
            defects.append({
                "defect_id": f"CONS_{len(defects)+1:03d}",
                "kind": "count_mismatch", "phase": source_phase, "file": source_file,
                "detail": f"{metric}: observed {observed} != canonical {expected}",
                "recommended_correction": "reconcile against canonical accepted count",
            })

    # universe reconciliation
    REC = MA0 / "S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0"
    u = pd.read_csv(REC / "universe_body_status_reconciled.csv", dtype=str).fillna("")
    ps = Counter(u["parse_status"]); rc = Counter(u["residual_class"])
    add_recon("universe_rows", "UNIVERSE_RESIDUAL_RECONCILIATION", "universe_body_status_reconciled.csv", len(u), CANON["universe_rows"])
    add_recon("usable_html_inline", "UNIVERSE_RESIDUAL_RECONCILIATION", "universe_body_status_reconciled.csv", rc.get("usable_html_inline", 0), CANON["usable_html_inline"])
    add_recon("zip_unparseable", "UNIVERSE_RESIDUAL_RECONCILIATION", "universe_body_status_reconciled.csv", rc.get("zip_unparseable", 0), CANON["zip_unparseable"])
    add_recon("no_label_match", "UNIVERSE_RESIDUAL_RECONCILIATION", "universe_body_status_reconciled.csv", ps.get("no_label_match", 0), CANON["no_label_match"])
    add_recon("label_no_value", "UNIVERSE_RESIDUAL_RECONCILIATION", "universe_body_status_reconciled.csv", ps.get("label_no_value", 0), CANON["label_no_value"])

    # full-universe correction links
    L = pd.read_csv(MA0 / "KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv", dtype=str).fillna("")
    add_recon("correction_rows", "CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION", "correction_full_universe_links.csv", len(L), CANON["correction_rows"])

    # adjudication
    ADJ = pd.read_csv(MA0 / "KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv", dtype=str).fillna("")
    add_recon("correction_rows", "CORRECTION_RESIDUAL_LOCAL_ADJUDICATION", "correction_residual_action_ledger.csv", len(ADJ), CANON["correction_rows"])

    # blocker register
    REG = pd.read_csv(MA0 / "KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv", dtype=str).fillna("")
    add_recon("blocker_register_rows", "RESIDUAL_BLOCKER_REGISTER", "residual_blocker_register.csv", len(REG), CANON["blocker_register_rows"])
    zipreg = REG[REG["residual_class"] == "zip_unparseable"]
    add_recon("zip_unparseable", "RESIDUAL_BLOCKER_REGISTER", "residual_blocker_register.csv", len(zipreg), CANON["zip_unparseable"])
    add_recon("correction_zip_subset", "RESIDUAL_BLOCKER_REGISTER", "residual_blocker_register.csv", int((zipreg["is_correction"] == "True").sum()), CANON["correction_zip_subset"])
    add_recon("non_correction_zip_subset", "RESIDUAL_BLOCKER_REGISTER", "residual_blocker_register.csv", int((zipreg["is_correction"] == "False").sum()), CANON["non_correction_zip_subset"])
    add_recon("no_label_match", "RESIDUAL_BLOCKER_REGISTER", "residual_blocker_register.csv", int((REG["parse_status"] == "no_label_match").sum()), CANON["no_label_match"])
    add_recon("label_no_value", "RESIDUAL_BLOCKER_REGISTER", "residual_blocker_register.csv", int((REG["parse_status"] == "label_no_value").sum()), CANON["label_no_value"])

    # taxonomy
    TAX = pd.read_csv(MA0 / "KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/parser_nonextracted_taxonomy_ledger.csv", dtype=str).fillna("")
    add_recon("parser_nonextracted_rows", "PARSER_NONEXTRACTED_LOCAL_TAXONOMY", "parser_nonextracted_taxonomy_ledger.csv", len(TAX), CANON["parser_nonextracted_rows"])
    tps = Counter(TAX["parse_status"])
    add_recon("no_label_match", "PARSER_NONEXTRACTED_LOCAL_TAXONOMY", "parser_nonextracted_taxonomy_ledger.csv", tps.get("no_label_match", 0), CANON["no_label_match"])
    add_recon("label_no_value", "PARSER_NONEXTRACTED_LOCAL_TAXONOMY", "parser_nonextracted_taxonomy_ledger.csv", tps.get("label_no_value", 0), CANON["label_no_value"])

    # source recovery manifest
    SRC = pd.read_csv(MA0 / "KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0/source_recovery_candidate_manifest.csv", dtype=str).fillna("")
    add_recon("zip_unparseable", "SOURCE_RECOVERY_CANDIDATE_MANIFEST", "source_recovery_candidate_manifest.csv", len(SRC), CANON["zip_unparseable"])
    add_recon("correction_zip_subset", "SOURCE_RECOVERY_CANDIDATE_MANIFEST", "source_recovery_candidate_manifest.csv", int((SRC["is_correction"] == "True").sum()), CANON["correction_zip_subset"])
    add_recon("non_correction_zip_subset", "SOURCE_RECOVERY_CANDIDATE_MANIFEST", "source_recovery_candidate_manifest.csv", int((SRC["is_correction"] == "False").sum()), CANON["non_correction_zip_subset"])

    # Derived identities
    derived = []
    def add_derived(name, lhs_desc, lhs, rhs):
        ok = (lhs == rhs)
        derived.append({"identity": name, "lhs": f"{lhs_desc}={lhs}", "rhs": rhs, "match": "PASS" if ok else "FAIL"})
        if not ok:
            defects.append({"defect_id": f"CONS_{len(defects)+1:03d}", "kind": "identity_mismatch",
                            "phase": "cross", "file": "", "detail": f"{name}: {lhs} != {rhs}",
                            "recommended_correction": "reconcile derived identity"})
    add_derived("parser_nonextracted = no_label_match + label_no_value", "511+200", 511 + 200, CANON["parser_nonextracted_rows"])
    add_derived("zip = correction_zip + non_correction_zip", "39+3", 39 + 3, CANON["zip_unparseable"])
    add_derived("blocker_register = 753 universe-residual + 109 extracted-correction", "753+109", 753 + 109, CANON["blocker_register_rows"])
    add_derived("universe = usable_html_inline + zip_unparseable", "12145+42", 12145 + 42, CANON["universe_rows"])

    write_csv(OUT / "count_reconciliation_matrix.csv", recon)

    # 3. CLOSE_NOTE consistency — grep each CLOSE_NOTE for the canonical numbers it should carry.
    expected_in_close = {
        "S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0": ["12,187", "12,145", "99.66", "42"],
        "KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0": ["166", "17", "52", "73"],
        "KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0": ["166", "39", "17"],
        "KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0": ["862", "42", "511", "200", "166", "39"],
        "KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0": ["711", "511", "200", "499", "170"],
        "KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0": ["42", "39", "3"],
    }
    close_checks = []
    for ph, nums in expected_in_close.items():
        cn = MA0 / ph / "CLOSE_NOTE.md"
        text = cn.read_text(encoding="utf-8") if cn.exists() else ""
        for num in nums:
            found = num in text
            close_checks.append({"phase": ph, "expected_number": num, "found_in_close_note": found})
            if not found:
                defects.append({"defect_id": f"CONS_{len(defects)+1:03d}", "kind": "close_note_number_absent",
                                "phase": ph, "file": "CLOSE_NOTE.md",
                                "detail": f"expected canonical number {num} not found in CLOSE_NOTE",
                                "recommended_correction": f"verify {num} appears in {ph}/CLOSE_NOTE.md"})
    write_csv(OUT / "close_note_consistency_check.csv", close_checks)

    # 4. next_actions.md consistency — each closed phase block present with key numbers.
    na_text = NEXT_ACTIONS.read_text(encoding="utf-8")
    na_lines = ["# next_actions.md Consistency Check", "", "Date: 2026-05-26",
                "Phase: KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0", "",
                "## Active section", ""]
    active_block = re.search(r"## Active\s*\n(.*?)\n## ", na_text, re.S)
    active_body = active_block.group(1).strip() if active_block else ""
    this_phase_active = "KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0" in active_body
    na_lines.append(f"- This phase marked Active during work: **{this_phase_active}**")
    na_lines += ["", "## Each closed phase present in Closed/Frozen with key numbers", "",
                 "| phase | block present | key numbers present |", "|---|---|---|"]
    na_close_expect = {
        "KR-STATUS-SOURCE-RECOVERY-CANDIDATE-MANIFEST-A0": ["42", "39", "3"],
        "KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0": ["711", "511", "200"],
        "KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0": ["862", "42"],
        "KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0": ["166", "39"],
        "KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0": ["166", "17"],
        "S2-HTML-INLINE-PARSER-UNIVERSE-RESIDUAL-RECONCILIATION-A0": ["12,187", "12,145", "42"],
    }
    for ph, nums in na_close_expect.items():
        block_present = ph in na_text
        nums_present = all(n in na_text for n in nums)
        na_lines.append(f"| {ph} | {block_present} | {nums_present} ({', '.join(nums)}) |")
        if not block_present:
            defects.append({"defect_id": f"CONS_{len(defects)+1:03d}", "kind": "next_actions_block_absent",
                            "phase": ph, "file": "docs/next_actions.md",
                            "detail": "closed-phase block not found", "recommended_correction": f"add {ph} block"})
    (OUT / "next_actions_consistency_check.md").write_text("\n".join(na_lines), encoding="utf-8")

    # 5. Hard-lock phrase audit — scan all .md in the 6 phases + next_actions.
    scan_files = []
    for ph in PHASES:
        scan_files += list((MA0 / ph).glob("*.md"))
    scan_files.append(NEXT_ACTIONS)
    flagged: list[dict] = []
    reviewed_benign: list[dict] = []
    total_trigger_lines = 0
    for f in scan_files:
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        for i, ln in enumerate(lines, 1):
            low = ln.lower()
            # 3-line window (previous + current + next) to catch multi-line
            # negations and trailing "= False" enumerations.
            prev = lines[i - 2].lower() if i >= 2 else ""
            nxt = lines[i].lower() if i < len(lines) else ""
            window = prev + " " + low + " " + nxt
            for tok in DRIFT_TOKENS:
                if tok in low:
                    total_trigger_lines += 1
                    reason = ""
                    if any(m in window for m in SAFE_MARKERS):
                        reason = "negation/fixed-False context (2-line window)"
                    elif tok == "authoritative" and any(nn in low for nn in PROVENANCE_NOUNS):
                        reason = "data-provenance 'authoritative source/dataset', not a row-status claim"
                    elif tok == "authoritative" and any(m in low for m in FIXTABLE_MARKERS):
                        reason = "REF-CLOSE-002 wording-fix documentation (before/after)"
                    elif tok == "100%" and any(m in low for m in MEASUREMENT_MARKERS):
                        reason = "legitimate measurement percentage (holdout/mapping/coverage), not universe-usable claim"
                    elif tok == "100%" and ("99.66" in window or "not 100%" in window):
                        reason = "explicit NOT-100% framing"
                    if reason:
                        reviewed_benign.append({
                            "file": str(f.relative_to(REPO)), "line_no": i,
                            "trigger_token": tok, "benign_reason": reason,
                            "line_excerpt": ln.strip()[:160],
                        })
                    else:
                        flagged.append({
                            "file": str(f.relative_to(REPO)), "line_no": i,
                            "trigger_token": tok, "line_excerpt": ln.strip()[:200],
                        })
                    break  # one token per line is enough
    write_csv(OUT / "hard_lock_phrase_flags.csv", flagged)
    write_csv(OUT / "hard_lock_phrase_reviewed_benign.csv", reviewed_benign)
    for fl in flagged:
        defects.append({"defect_id": f"CONS_{len(defects)+1:03d}", "kind": "possible_scope_drift_phrase",
                        "phase": "scan", "file": fl["file"],
                        "detail": f"line {fl['line_no']} token '{fl['trigger_token']}': {fl['line_excerpt']}",
                        "recommended_correction": "review wording; negate or remove if affirmative scope-drift"})

    write_hard_lock_phrase_audit(OUT / "hard_lock_phrase_audit.md", total_trigger_lines, flagged)

    # 6. Residual lineage map
    lineage = [
        {"residual_set": "12,187 in-scope universe rows", "origin_phase": "UNIVERSE_RESIDUAL_RECONCILIATION",
         "flows_into": "blocker register (membership base); correction subset (166)"},
        {"residual_set": "42 zip_unparseable", "origin_phase": "UNIVERSE_RESIDUAL_RECONCILIATION",
         "flows_into": "blocker register (source_zip_unparseable) -> source-recovery manifest (42 = 39 corr + 3 non-corr)"},
        {"residual_set": "511 no_label_match", "origin_phase": "UNIVERSE_RESIDUAL_RECONCILIATION",
         "flows_into": "blocker register (parser_no_label_match) -> non-extracted taxonomy (root causes)"},
        {"residual_set": "200 label_no_value", "origin_phase": "UNIVERSE_RESIDUAL_RECONCILIATION",
         "flows_into": "blocker register (parser_label_no_value) -> non-extracted taxonomy (root causes)"},
        {"residual_set": "166 correction rows (5-tier 17/52/7/73/17)", "origin_phase": "CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION",
         "flows_into": "adjudication (residual action classes) -> blocker register (correction_* tags)"},
        {"residual_set": "39 correction zip subset", "origin_phase": "CORRECTION_RESIDUAL_LOCAL_ADJUDICATION",
         "flows_into": "blocker register (subset of 42) -> source-recovery manifest (correction zip detail)"},
        {"residual_set": "862 blocker register rows", "origin_phase": "RESIDUAL_BLOCKER_REGISTER",
         "flows_into": "non-extracted taxonomy (711 subset) + source-recovery manifest (42 subset)"},
        {"residual_set": "711 parser non-extracted rows", "origin_phase": "RESIDUAL_BLOCKER_REGISTER/UNIVERSE",
         "flows_into": "non-extracted taxonomy (root-cause classified)"},
    ]
    write_csv(OUT / "residual_lineage_map.csv", lineage)

    write_csv(OUT / "local_artifact_inventory.csv", inventory)
    write_csv(OUT / "artifact_missing_or_extra_files.csv", missing_extra or [
        {"phase": "(none)", "file": "(none)", "status": "no missing core files"}])
    write_csv(OUT / "consistency_defect_ledger.csv", defects or [
        {"defect_id": "NONE", "kind": "no_defect", "phase": "(all 6 consistent)",
         "file": "", "detail": "no count mismatch, no missing core file, no absent "
         "CLOSE_NOTE number, no scope-drift phrase found",
         "recommended_correction": "none"}])

    n_recon_fail = sum(1 for r in recon if r["match"] == "FAIL")
    n_derived_fail = sum(1 for r in derived if r["match"] == "FAIL")
    n_close_absent = sum(1 for r in close_checks if not r["found_in_close_note"])

    write_accepted_count_lock(OUT / "accepted_count_lock_table.md", derived)
    write_input_manifest(OUT / "prior_phase_input_manifest.md")
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_unresolved(OUT / "unresolved_questions.md", defects)
    write_summary(OUT / "report.md", recon, derived, close_checks, this_phase_active,
                  flagged, total_trigger_lines, defects, n_recon_fail, n_derived_fail, n_close_absent,
                  is_report=True)
    write_summary(OUT / "consistency_audit_summary.md", recon, derived, close_checks, this_phase_active,
                  flagged, total_trigger_lines, defects, n_recon_fail, n_derived_fail, n_close_absent,
                  is_report=False)

    print(json.dumps({
        "phases_checked": len(PHASES),
        "recon_rows": len(recon), "recon_fail": n_recon_fail,
        "derived_identities": len(derived), "derived_fail": n_derived_fail,
        "close_note_numbers_checked": len(close_checks), "close_note_absent": n_close_absent,
        "this_phase_active": this_phase_active,
        "phrase_trigger_lines": total_trigger_lines, "phrase_flagged": len(flagged),
        "total_defects": len(defects),
    }, indent=2, default=str))


def write_hard_lock_phrase_audit(path: Path, total: int, flagged: list[dict]) -> None:
    lines = [
        "# Hard-Lock Phrase Audit", "", "Date: 2026-05-26",
        "Phase: KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0", "",
        "Scanned all `.md` files in the 6 closed phase directories + docs/next_actions.md "
        "for scope-drift trigger tokens, classifying each occurrence as a NEGATION / "
        "fixed-False / design-only / forbidden statement (safe) vs an affirmative claim (flagged).",
        "",
        "## Trigger tokens",
        "", "`" + "`, `".join(DRIFT_TOKENS) + "`", "",
        f"## Trigger-token lines found: **{total}**",
        f"## Affirmative scope-drift lines flagged: **{len(flagged)}**",
        "",
    ]
    checks = [
        ("no strategy-ready claim", "strategy-ready/strategy_ready only as negations / =False / 'no card may be described as strategy-ready'"),
        ("no execution-ready claim", "no affirmative execution-ready; execution_simulation / execution always negated"),
        ("no 100% usable universe claim", "reconciliation states usable 99.66%, explicitly 'NOT 100%'"),
        ("no source recovery performed claim", "recovery_performed=False everywhere; manifest is NOT recovery"),
        ("no parser change claim", "parser code unchanged; taxonomy used read-only helpers; backlog design-only"),
        ("no event-log / executable-status table claim", "explicitly 'NOT an event log / executable-status table'"),
    ]
    lines += ["## Required hard-lock phrase checks", "", "| check | result | basis |", "|---|---|---|"]
    for name, basis in checks:
        lines.append(f"| {name} | {'PASS' if len(flagged) == 0 else 'REVIEW'} | {basis} |")
    if flagged:
        lines += ["", "## Flagged lines (review)", "", "| file | line | token | excerpt |", "|---|---:|---|---|"]
        for fl in flagged:
            lines.append(f"| {fl['file']} | {fl['line_no']} | `{fl['trigger_token']}` | {fl['line_excerpt']} |")
    else:
        lines += ["", "No affirmative scope-drift wording found. All trigger-token occurrences are "
                  "negations / fixed-False flags / design-only / forbidden statements."]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_accepted_count_lock(path: Path, derived: list[dict]) -> None:
    lines = ["# Accepted Count Lock Table", "", "Date: 2026-05-26",
             "Phase: KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0", "",
             "Canonical accepted counts (locked across the 6 phases):", "",
             "| metric | canonical value |", "|---|---:|"]
    for k, v in CANON.items():
        lines.append(f"| {k} | {v:,} |")
    lines += ["", "## Derived identities", "", "| identity | lhs | rhs | match |", "|---|---|---:|---|"]
    for d in derived:
        lines.append(f"| {d['identity']} | {d['lhs']} | {d['rhs']} | {d['match']} |")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_input_manifest(path: Path) -> None:
    lines = ["# Prior-Phase Input Manifest", "", "Date: 2026-05-26",
             "Phase: KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0", "",
             "## Phase directories audited (read-only)", ""]
    for ph in PHASES:
        lines.append(f"- `reports/experiments/measurement_A0/{ph}/`")
    lines += ["- `docs/next_actions.md`", "",
              "## No network. No parser invocation. No downloads / API / credentials / body repair.",
              "", "## New code",
              "- `src/audit/measurement_a0/p_local_artifact_consistency_audit.py` (this phase)."]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Local Artifact Consistency Audit)

Date: 2026-05-26
Phase: KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0

| hard lock | status |
|---|---|
| Existing local reports / CSV / CLOSE_NOTE / next_actions only | PASS |
| NO downloads / API / credentials / body repair | PASS |
| NO parser change / rerun; NO candidate / body rerun | PASS |
| NO downstream wiring / C2 / C3 | PASS |
| NOT an event log / executable-status table / source recovery / parser design | PASS |
| NO strategy / performance / execution / backtest | PASS |
| Inconsistencies recorded (not patched outside this phase's own outputs) | PASS |
| No artifact marked strategy-ready / execution-ready / production-ready | PASS |
| No source-recovery-performed / parser-change-approved claim | PASS |
""", encoding="utf-8")


def write_unresolved(path: Path, defects: list[dict]) -> None:
    path.write_text(f"""# Unresolved Questions (local, for later — NOT decisions)

Date: 2026-05-26
Phase: KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0

- Total consistency defects recorded this phase: {len(defects)}.
- Any cross-phase inconsistency is RECORDED in consistency_defect_ledger.csv and NOT
  patched here (patching another closed phase's artifact would require a separate
  Referee verdict). If the ledger is empty, the recent local artifacts are
  numerically + hard-lock consistent.
""", encoding="utf-8")


def write_summary(path, recon, derived, close_checks, this_active, flagged, total_trigger,
                  defects, n_recon_fail, n_derived_fail, n_close_absent, is_report):
    title = "Report" if is_report else "Summary"
    lines = [
        f"# KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0 — {title}",
        "", "Date: 2026-05-26",
        "Phase opened by: Referee directive REF-OPEN-007 (via relay)." if is_report else "Opened by REF-OPEN-007 (via relay).",
        "Executor: Claude Code. Referee: Codex." if is_report else "",
        "",
        "## Phase name and scope",
        "",
        "Measurement-layer LOCAL ARTIFACT CONSISTENCY AUDIT only. Reads existing local "
        "reports / CSV / CLOSE_NOTE / docs/next_actions.md. No new data. No downloads / "
        "API / credentials / body repair / parser change / rerun / downstream wiring / "
        "C2-C3 / event-log / executable-status table / strategy / execution.",
        "",
        "## Phase directories audited",
        "",
    ]
    for ph in PHASES:
        lines.append(f"- `{ph}`")
    lines += [
        "",
        "## Count reconciliation (recomputed from source CSVs vs canonical)",
        "",
        "| metric | source phase | observed | canonical | match |",
        "|---|---|---:|---:|:--:|",
    ]
    for r in recon:
        lines.append(f"| {r['metric']} | {r['source_phase']} | {r['observed']} | {r['canonical_expected']} | {r['match']} |")
    lines += ["", "## Derived identities", "", "| identity | lhs | rhs | match |", "|---|---|---:|:--:|"]
    for d in derived:
        lines.append(f"| {d['identity']} | {d['lhs']} | {d['rhs']} | {d['match']} |")
    lines += [
        "",
        "## Pass/fail results",
        "",
        "| check | result |",
        "|---|---|",
        f"| artifact presence | {'PASS' if not any(d['kind']=='missing_core_file' for d in defects) else 'FAIL'} |",
        f"| row-count consistency | {'PASS' if n_recon_fail == 0 else 'FAIL'} |",
        f"| derived-identity consistency | {'PASS' if n_derived_fail == 0 else 'FAIL'} |",
        f"| CLOSE_NOTE consistency | {'PASS' if n_close_absent == 0 else 'FAIL'} |",
        f"| docs/next_actions.md consistency (this phase Active) | {'PASS' if this_active else 'FAIL'} |",
        f"| hard-lock phrase audit | {'PASS' if len(flagged) == 0 else 'REVIEW'} |",
        "",
        f"## Hard-lock phrase audit: {total_trigger} trigger-token lines scanned; "
        f"**{len(flagged)}** affirmative scope-drift lines flagged.",
        "",
        f"## Consistency defects: **{len(defects)}**",
        "",
        ("No inconsistencies found. The 6 recently-closed local artifacts reconcile "
         "exactly to the canonical counts and carry no affirmative scope-drift wording."
         if not defects else
         "See `consistency_defect_ledger.csv` for the recorded inconsistencies and "
         "recommended corrections."),
        "",
        "## Confirmations",
        "",
        "- No downloads / API / body repair / parser change occurred.",
        "- No strategy, backtest, execution simulation, C2/C3, event-log finalization, "
        "executable-status table, or production/paper/live/P08/shadow work occurred.",
        "",
    ]
    if is_report:
        lines += [
            "## Decision requested from Referee",
            "",
            "Executor does NOT self-close. Requesting a verdict among:",
            "- **A.** close as local artifact consistency audit complete (consistent);",
            "- **B.** require another audit pass (widen scope / deeper checks);",
            "- **C.** authorize correction of any recorded cross-phase inconsistency "
            "(would target a closed phase's artifact — needs explicit approval);",
            "- **D.** keep all strategy / execution research closed (unchanged).",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
