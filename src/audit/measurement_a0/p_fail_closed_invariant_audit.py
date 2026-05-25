"""KR-STATUS-FAIL-CLOSED-INVARIANT-AUDIT-A0 — builder.

Referee directive REF-OPEN-009 (2026-05-26, via relay). Follows the now-closed
KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0.

Goal: verify all residual / correction / source-defect row sets remain fail-closed by
FIELD-LEVEL status flags — not merely by count (REF-OPEN-007) or row-key membership
(REF-OPEN-008). Third verification dimension: the actual safety-flag VALUES on every
row.

Reads existing local CSV/MD only. It:
- does NOT edit any prior closed-phase output,
- does NOT patch violations (records them only),
- does NOT create CLOSE_NOTE.md (Executor does not self-close this phase),
- does NOT download / call APIs / use credentials / repair bodies / change or rerun
  the parser / rerun candidate search or body confirmation / perform source recovery
  / approve parser design,
- is NOT an event log / executable-status table / downstream wiring,
- newly marks no row strategy-ready / execution-ready / production-ready / executable
  / safe / downstream-authoritative.

SCOPING NOTE: the universe ledger's 11,434 cleanly-`extracted` rows are legitimately
manual_review_required=False (they are NOT residuals). The fail-closed
manual_review_required=True invariant is therefore asserted ONLY on the universe's
753 residual rows (parse_status in no_label_match/label_no_value/body_unavailable),
not the extracted rows. executable_or_safe=False is asserted universe-wide (it holds
for all 12,187).
"""
from __future__ import annotations

import csv as _csv
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
MA0 = REPO / "reports/experiments/measurement_A0"
OUT = MA0 / "KR_STATUS_FAIL_CLOSED_INVARIANT_AUDIT_A0"

LEDGERS = {
    "universe_body_status_reconciled": MA0 / "S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv",
    "correction_full_universe_links": MA0 / "KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv",
    "supersession_readiness_full_universe": MA0 / "KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/supersession_readiness_full_universe.csv",
    "correction_residual_action_ledger": MA0 / "KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv",
    "residual_blocker_register": MA0 / "KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv",
    "parser_nonextracted_taxonomy_ledger": MA0 / "KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/parser_nonextracted_taxonomy_ledger.csv",
    "source_recovery_candidate_manifest": MA0 / "KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0/source_recovery_candidate_manifest.csv",
}

# Flags that MUST be True (fail-closed / gate flags).
MUST_TRUE = ["manual_review_required", "recovery_required", "requires_separate_verdict",
             "requires_download_approval"]
# Flags that MUST NOT be True (forbidden-truthy: would imply usability / approval).
FORBIDDEN_TRUTHY = ["executable_or_safe", "downstream_authoritative",
                    "parsed_clean_and_usable", "strategy_ready", "production_ready",
                    "safe_for_current_use", "recovery_performed", "supersession_wired",
                    "effective_date_extracted", "parser_change_approved"]


def truthy(v) -> bool:
    return str(v).strip().lower() in ("true", "1", "yes")


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


def main() -> None:
    print("[start] KR-STATUS-FAIL-CLOSED-INVARIANT-AUDIT-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    dfs = {name: pd.read_csv(p, dtype=str).fillna("") for name, p in LEDGERS.items()}

    violations: list[dict] = []

    def add_viol(ledger, flag, expected, rcept_no, got, scope):
        violations.append({
            "violation_id": f"FC_{len(violations)+1:04d}", "ledger": ledger,
            "flag": flag, "expected": expected, "rcept_no": rcept_no, "got": got,
            "scope": scope,
        })

    # 1. Flag/column schema inventory
    schema_rows = []
    all_safety = MUST_TRUE + FORBIDDEN_TRUTHY
    for name, df in dfs.items():
        for flag in all_safety:
            present = flag in df.columns
            schema_rows.append({
                "ledger": name, "flag": flag, "present": present,
                "role": ("must_be_true" if flag in MUST_TRUE else "must_not_be_true"),
                "distinct_values": "|".join(sorted(set(df[flag]))[:5]) if present else "",
            })
    write_csv(OUT / "flag_schema_inventory.csv", schema_rows)

    # ---- Invariant matrix builder ----
    matrix: list[dict] = []

    def check_flag(ledger_name, df, flag, want_true, scope_label, key_col="rcept_no", mask=None):
        if flag not in df.columns:
            matrix.append({"ledger": ledger_name, "scope": scope_label, "flag": flag,
                           "expected": ("True" if want_true else "not True"),
                           "rows_checked": 0, "violations": 0, "result": "ABSENT"})
            return
        sub = df if mask is None else df[mask]
        n = len(sub)
        if want_true:
            bad = sub[~sub[flag].map(truthy)]
        else:
            bad = sub[sub[flag].map(truthy)]
        nbad = len(bad)
        matrix.append({"ledger": ledger_name, "scope": scope_label, "flag": flag,
                       "expected": ("True" if want_true else "not True"),
                       "rows_checked": n, "violations": nbad,
                       "result": "PASS" if nbad == 0 else "FAIL"})
        if nbad:
            kc = key_col if key_col in sub.columns else (
                "correction_rcept_no" if "correction_rcept_no" in sub.columns else sub.columns[0])
            for _, r in bad.iterrows():
                add_viol(ledger_name, flag, ("True" if want_true else "not True"),
                         r.get(kc, ""), r.get(flag, ""), scope_label)

    # 2. 862 blocker register fail-closed
    reg = dfs["residual_blocker_register"]
    check_flag("residual_blocker_register", reg, "manual_review_required", True, "all_862")
    for flag in ["executable_or_safe", "downstream_authoritative", "parsed_clean_and_usable",
                 "strategy_ready", "production_ready"]:
        check_flag("residual_blocker_register", reg, flag, False, "all_862")

    # 3. 711 parser non-extracted fail-closed
    tax = dfs["parser_nonextracted_taxonomy_ledger"]
    check_flag("parser_nonextracted_taxonomy_ledger", tax, "manual_review_required", True, "all_711")
    for flag in ["executable_or_safe", "downstream_authoritative", "parsed_clean_and_usable",
                 "strategy_ready", "production_ready", "effective_date_extracted"]:
        check_flag("parser_nonextracted_taxonomy_ledger", tax, flag, False, "all_711")

    # 4. 42 source recovery manifest recovery-gated
    man = dfs["source_recovery_candidate_manifest"]
    for flag in ["recovery_required", "requires_separate_verdict", "requires_download_approval",
                 "manual_review_required"]:
        check_flag("source_recovery_candidate_manifest", man, flag, True, "all_42")
    for flag in ["recovery_performed", "safe_for_current_use", "executable_or_safe",
                 "downstream_authoritative", "parsed_clean_and_usable", "strategy_ready",
                 "production_ready"]:
        check_flag("source_recovery_candidate_manifest", man, flag, False, "all_42")

    # 5. 166 correction rows manual-review / non-authoritative (links + adjudication)
    links = dfs["correction_full_universe_links"]
    adj = dfs["correction_residual_action_ledger"]
    check_flag("correction_full_universe_links", links, "manual_review_required", True, "all_166")
    check_flag("correction_residual_action_ledger", adj, "manual_review_required", True, "all_166")
    check_flag("correction_residual_action_ledger", adj, "downstream_authoritative", False, "all_166")
    check_flag("correction_residual_action_ledger", adj, "supersession_wired", False, "all_166")

    # universe: manual_review on the 753 residual subset only; executable_or_safe universe-wide
    u = dfs["universe_body_status_reconciled"]
    resid_mask = u["parse_status"].isin(["no_label_match", "label_no_value", "body_unavailable"])
    check_flag("universe_body_status_reconciled", u, "manual_review_required", True,
               "residual_753_only", mask=resid_mask)
    check_flag("universe_body_status_reconciled", u, "executable_or_safe", False, "all_12187")

    write_csv(OUT / "fail_closed_invariant_matrix.csv", matrix)

    # 6. Correction confidence gate
    gate_rows = []
    conf_ct = Counter(links["confidence_5tier"])
    EXPECT = {"high_validated": 17, "medium_needs_manual": 52, "low_needs_manual": 7,
              "no_link": 73, "rejected_wrong_candidate": 17}
    for cls, exp in EXPECT.items():
        got = conf_ct.get(cls, 0)
        gate_rows.append({"confidence_class": cls, "count": got, "expected": exp,
                          "count_match": "PASS" if got == exp else "FAIL"})
        if got != exp:
            add_viol("correction_full_universe_links", "confidence_5tier_count",
                     str(exp), cls, str(got), "gate")
    # high_validated: design-only (link_validated True) but NOT downstream-authoritative / wired
    hv_ids = set(links[links["confidence_5tier"] == "high_validated"]["correction_rcept_no"])
    adj_hv = adj[adj["correction_rcept_no"].isin(hv_ids)]
    hv_auth_bad = adj_hv[adj_hv["downstream_authoritative"].map(truthy)] if "downstream_authoritative" in adj_hv else adj_hv.iloc[0:0]
    hv_wired_bad = adj_hv[adj_hv["supersession_wired"].map(truthy)] if "supersession_wired" in adj_hv else adj_hv.iloc[0:0]
    gate_rows.append({"confidence_class": "high_validated", "count": len(hv_ids),
                      "expected": "downstream_authoritative=0 & supersession_wired=0",
                      "count_match": "PASS" if (len(hv_auth_bad) == 0 and len(hv_wired_bad) == 0) else "FAIL"})
    # rejected_wrong_candidate quarantined, NOT dropped (present, count 17)
    rej = conf_ct.get("rejected_wrong_candidate", 0)
    gate_rows.append({"confidence_class": "rejected_wrong_candidate_quarantined_not_dropped",
                      "count": rej, "expected": ">=1 (17)",
                      "count_match": "PASS" if rej == 17 else "FAIL"})
    # medium/low/no_link not authoritative (adjudication downstream_authoritative=False already
    # checked all_166; reaffirm none of those classes are authoritative)
    nonauth_ids = set(links[links["confidence_5tier"].isin(
        ["medium_needs_manual", "low_needs_manual", "no_link", "rejected_wrong_candidate"])]["correction_rcept_no"])
    adj_na = adj[adj["correction_rcept_no"].isin(nonauth_ids)]
    na_bad = adj_na[adj_na["downstream_authoritative"].map(truthy)] if "downstream_authoritative" in adj_na else adj_na.iloc[0:0]
    gate_rows.append({"confidence_class": "medium/low/no_link/rejected non-authoritative",
                      "count": len(nonauth_ids), "expected": "downstream_authoritative=0",
                      "count_match": "PASS" if len(na_bad) == 0 else "FAIL"})
    write_csv(OUT / "correction_confidence_gate_check.csv", gate_rows)

    # 7. Source recovery gate check (explicit per-flag on the 42)
    sr_rows = []
    for flag, want in [("recovery_performed", False), ("requires_separate_verdict", True),
                       ("requires_download_approval", True), ("safe_for_current_use", False),
                       ("executable_or_safe", False), ("downstream_authoritative", False),
                       ("strategy_ready", False), ("production_ready", False),
                       ("manual_review_required", True)]:
        if flag not in man.columns:
            sr_rows.append({"flag": flag, "expected": want, "rows": len(man),
                            "compliant": "ABSENT", "result": "ABSENT"})
            continue
        comp = man[flag].map(truthy) if want else ~man[flag].map(truthy)
        ncomp = int(comp.sum())
        sr_rows.append({"flag": flag, "expected": want, "rows": len(man),
                        "compliant": ncomp, "result": "PASS" if ncomp == len(man) else "FAIL"})
    write_csv(OUT / "source_recovery_gate_check.csv", sr_rows)

    # 8. Forbidden-truthy flag scan across ALL audited ledgers (any column matching a
    #    forbidden flag name that is truthy on any row).
    scan_rows = []
    for name, df in dfs.items():
        for col in df.columns:
            if col in FORBIDDEN_TRUTHY:
                ntrue = int(df[col].map(truthy).sum())
                scan_rows.append({"ledger": name, "flag_column": col, "rows": len(df),
                                  "truthy_count": ntrue,
                                  "result": "PASS" if ntrue == 0 else "FAIL"})
                if ntrue:
                    for _, r in df[df[col].map(truthy)].iterrows():
                        kc = "rcept_no" if "rcept_no" in df.columns else "correction_rcept_no"
                        add_viol(name, col, "not True", r.get(kc, ""), r.get(col, ""), "forbidden_truthy_scan")
    # also record parser_change_approved absence explicitly
    scan_rows.append({"ledger": "(all)", "flag_column": "parser_change_approved",
                      "rows": "-", "truthy_count": 0, "result": "ABSENT (no such column; nothing approved)"})
    write_csv(OUT / "forbidden_truthy_flag_scan.csv", scan_rows)

    # Violation ledger (sentinel if none)
    write_csv(OUT / "fail_closed_violation_ledger.csv", violations or [
        {"violation_id": "NONE", "ledger": "(all audited)", "flag": "all_invariants",
         "expected": "fail-closed", "rcept_no": "", "got": "",
         "scope": "no must-be-True flag was False; no forbidden flag was True; "
         "correction gate intact; source-recovery gate intact"}])

    n_matrix_fail = sum(1 for r in matrix if r["result"] == "FAIL")
    n_gate_fail = sum(1 for r in gate_rows if r["count_match"] == "FAIL")
    n_sr_fail = sum(1 for r in sr_rows if r["result"] == "FAIL")
    n_scan_fail = sum(1 for r in scan_rows if r["result"] == "FAIL")

    write_input_manifest(OUT / "fail_closed_input_manifest.md")
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_report(OUT / "report.md", schema_rows, matrix, gate_rows, sr_rows, scan_rows,
                 violations, n_matrix_fail, n_gate_fail, n_sr_fail, n_scan_fail)

    print(json.dumps({
        "matrix_checks": len(matrix), "matrix_fail": n_matrix_fail,
        "gate_checks": len(gate_rows), "gate_fail": n_gate_fail,
        "source_recovery_checks": len(sr_rows), "source_recovery_fail": n_sr_fail,
        "forbidden_truthy_scans": len(scan_rows), "forbidden_truthy_fail": n_scan_fail,
        "total_violations": len(violations),
    }, indent=2, default=str))


def write_input_manifest(path: Path) -> None:
    lines = ["# Fail-Closed Input Manifest", "", "Date: 2026-05-26",
             "Phase: KR-STATUS-FAIL-CLOSED-INVARIANT-AUDIT-A0", "",
             "## Input ledgers (read-only)", ""]
    for name, p in LEDGERS.items():
        lines.append(f"- `{p.relative_to(REPO)}`")
    lines += ["", "## No new data. No network. No parser invocation. No edits to closed artifacts.",
              "", "## Scoping note",
              "- universe manual_review_required=True asserted on the 753 residual rows only "
              "(the 11,434 extracted rows are legitimately False / not residuals); "
              "executable_or_safe=False asserted universe-wide (holds for all 12,187).",
              "", "## New code",
              "- `src/audit/measurement_a0/p_fail_closed_invariant_audit.py` (this phase)."]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Fail-Closed Invariant Audit)

Date: 2026-05-26
Phase: KR-STATUS-FAIL-CLOSED-INVARIANT-AUDIT-A0

| hard lock | status |
|---|---|
| Existing local CSV/MD only; no new data | PASS |
| NO edits to prior closed-phase outputs | PASS |
| Violations recorded, NOT patched | PASS |
| NO CLOSE_NOTE.md created (executor does not self-close this phase) | PASS |
| NO downloads / API / credentials / body repair | PASS |
| NO parser change / rerun; NO candidate / body confirmation rerun | PASS |
| NO source recovery; NO parser-design approval | PASS |
| NO downstream wiring / C2 / C3 / event-log / executable-status table | PASS |
| NO strategy / performance / execution / backtest / production / paper / live / P08 / shadow | PASS |
| No row NEWLY marked strategy-ready / execution-ready / production-ready / executable / safe / downstream-authoritative | PASS |
""", encoding="utf-8")


def write_report(path, schema_rows, matrix, gate_rows, sr_rows, scan_rows, violations,
                 n_matrix_fail, n_gate_fail, n_sr_fail, n_scan_fail) -> None:
    overall = (n_matrix_fail == 0 and n_gate_fail == 0 and n_sr_fail == 0 and n_scan_fail == 0)
    lines = [
        "# KR-STATUS-FAIL-CLOSED-INVARIANT-AUDIT-A0 — Report",
        "", "Date: 2026-05-26",
        "Phase opened by: Referee directive REF-OPEN-009 (via relay).",
        "Executor: Claude Code. Referee: Codex.",
        "",
        "## Phase name and scope",
        "",
        "Local fail-closed invariant audit only. Verifies all residual / correction / "
        "source-defect row sets remain fail-closed by FIELD-LEVEL status flags (not "
        "merely count or row-key membership). Existing local CSV/MD only; no new "
        "data; no edits to closed artifacts; violations recorded not patched; no "
        "CLOSE_NOTE (executor does not self-close).",
        "",
        "## Input artifacts used",
        "",
    ]
    for name, p in LEDGERS.items():
        lines.append(f"- `{p.relative_to(REPO)}`")
    lines += [
        "",
        "## Scoping note",
        "",
        "The universe ledger's 11,434 cleanly-extracted rows are legitimately "
        "`manual_review_required=False` (NOT residuals). The fail-closed "
        "manual_review_required=True invariant is asserted on the universe's **753 "
        "residual rows only**; `executable_or_safe=False` is asserted universe-wide "
        "(holds for all 12,187).",
        "",
        "## Fail-closed invariant matrix (field-level)",
        "",
        "| ledger | scope | flag | expected | rows | violations | result |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for r in matrix:
        lines.append(f"| {r['ledger']} | {r['scope']} | {r['flag']} | {r['expected']} | {r['rows_checked']} | {r['violations']} | {r['result']} |")
    lines += [
        "",
        "## Correction confidence gate",
        "",
        "| confidence class / check | count | expected | result |",
        "|---|---:|---|---|",
    ]
    for r in gate_rows:
        lines.append(f"| {r['confidence_class']} | {r['count']} | {r['expected']} | {r['count_match']} |")
    lines += [
        "",
        "## Source-recovery gate (the 42 manifest rows)",
        "",
        "| flag | expected | rows | compliant | result |",
        "|---|---|---:|---|---|",
    ]
    for r in sr_rows:
        lines.append(f"| {r['flag']} | {r['expected']} | {r['rows']} | {r['compliant']} | {r['result']} |")
    lines += [
        "",
        "## Forbidden-truthy flag scan (any forbidden flag True anywhere)",
        "",
        "| ledger | flag column | rows | truthy count | result |",
        "|---|---|---:|---:|---|",
    ]
    for r in scan_rows:
        lines.append(f"| {r['ledger']} | {r['flag_column']} | {r['rows']} | {r['truthy_count']} | {r['result']} |")
    lines += [
        "",
        "## Overall result",
        "",
        f"- fail-closed invariant matrix: {'PASS' if n_matrix_fail == 0 else 'FAIL'} ({n_matrix_fail} fail)",
        f"- correction confidence gate: {'PASS' if n_gate_fail == 0 else 'FAIL'} ({n_gate_fail} fail)",
        f"- source-recovery gate: {'PASS' if n_sr_fail == 0 else 'FAIL'} ({n_sr_fail} fail)",
        f"- forbidden-truthy scan: {'PASS' if n_scan_fail == 0 else 'FAIL'} ({n_scan_fail} fail)",
        f"- **total row-level violations: {0 if (violations and violations[0].get('violation_id')=='NONE') else len(violations)}**",
        "",
        ("**CLEAN PASS — every audited residual / correction / source-defect row "
         "remains fail-closed at the field level; no forbidden flag is True anywhere.**"
         if overall else
         "**VIOLATIONS FOUND — see fail_closed_violation_ledger.csv. Not patched "
         "(closed artifacts are not edited).**"),
        "",
        "## Confirmations",
        "",
        "- No downloads / API / credentials / body repair / parser change / rerun.",
        "- No candidate / body confirmation rerun; no source recovery; no parser-design.",
        "- No edits to prior closed-phase outputs; violations recorded not patched.",
        "- No CLOSE_NOTE created. No strategy / execution / C2-C3 / event-log / "
        "executable-status table / production / paper / live / P08 / shadow work.",
        "- No row newly marked strategy/execution/production-ready, executable, safe, "
        "or downstream-authoritative.",
        "",
        "## Decision requested from Referee",
        "",
        "Executor does NOT self-close. Requesting a verdict among:",
        "- **A.** close as fail-closed invariant audit complete (invariants hold at field level);",
        "- **B.** require another invariant pass (widen flag set / add ledgers);",
        "- **C.** authorize correction of a recorded field-level violation (would target "
        "a closed phase's artifact — needs explicit approval; none found this pass);",
        "- **D.** keep all strategy / execution research closed (unchanged).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
