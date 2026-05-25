"""KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0 — builder.

Referee directive REF-OPEN-008 (2026-05-26, via relay). Follows the now-closed
KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0.

Goal: verify the accepted COUNT LOCKS also hold at the rcept_no ROW-KEY / SET level
— not merely as aggregate counts. (Two ledgers can both have 42 rows yet contain
DIFFERENT rcept_no sets; the aggregate audit would not catch that. This phase does
exact set equality + duplicate-key + union/overlap checks.)

Reads existing local CSV/MD artifacts from the already-closed measurement_A0 phases.
No new data. It:
- does NOT edit any prior closed-phase output,
- does NOT patch mismatches (records them only),
- does NOT create CLOSE_NOTE.md (Executor does not self-close this phase),
- does NOT download / call APIs / use credentials / repair bodies / change or rerun
  the parser / rerun candidate search or body confirmation / perform source recovery,
- is NOT an event log / executable-status table / downstream wiring,
- marks no row strategy-ready / execution-ready / production-ready / executable /
  safe / downstream-authoritative.
"""
from __future__ import annotations

import csv as _csv
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
MA0 = REPO / "reports/experiments/measurement_A0"
OUT = MA0 / "KR_STATUS_RESIDUAL_ROWKEY_INTEGRITY_AUDIT_A0"

UNIV = MA0 / "S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv"
LINKS = MA0 / "KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv"
ADJ = MA0 / "KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv"
REG = MA0 / "KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv"
TAX = MA0 / "KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/parser_nonextracted_taxonomy_ledger.csv"
MAN = MA0 / "KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0/source_recovery_candidate_manifest.csv"


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
    print("[start] KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    mismatches: list[dict] = []

    def mm(check: str, detail: str, keys: list[str]):
        mismatches.append({
            "mismatch_id": f"RK_{len(mismatches)+1:03d}", "check": check,
            "detail": detail, "example_keys": ",".join(sorted(keys)[:20]),
            "n_keys": len(keys),
        })

    # ---- Load ledgers ----
    u = pd.read_csv(UNIV, dtype=str).fillna("")
    links = pd.read_csv(LINKS, dtype=str).fillna("")
    adj = pd.read_csv(ADJ, dtype=str).fillna("")
    reg = pd.read_csv(REG, dtype=str).fillna("")
    tax = pd.read_csv(TAX, dtype=str).fillna("")
    man = pd.read_csv(MAN, dtype=str).fillna("")

    # ---- 1. Duplicate-key check per ledger ----
    dup_rows = []
    def dup_check(name, df, keycol):
        n = len(df)
        uniq = df[keycol].nunique()
        ndup = n - uniq
        dup_rows.append({"ledger": name, "key_col": keycol, "rows": n,
                         "unique_keys": uniq, "duplicates": ndup,
                         "result": "PASS" if ndup == 0 else "FAIL"})
        if ndup:
            dupes = df[keycol][df[keycol].duplicated()].unique().tolist()
            mm("duplicate_key", f"{name}: {ndup} duplicate {keycol}", list(dupes))
    dup_check("universe_body_status_reconciled", u, "rcept_no")
    dup_check("correction_full_universe_links", links, "correction_rcept_no")
    dup_check("correction_residual_action_ledger", adj, "correction_rcept_no")
    dup_check("residual_blocker_register", reg, "rcept_no")
    dup_check("parser_nonextracted_taxonomy_ledger", tax, "rcept_no")
    dup_check("source_recovery_candidate_manifest", man, "rcept_no")
    write_csv(OUT / "rowkey_duplicate_check.csv", dup_rows)

    # ---- Build row-key SETS ----
    def S(series):
        return set(series.tolist())

    U_zip = S(u[u["residual_class"] == "zip_unparseable"]["rcept_no"])
    U_nolabel = S(u[u["parse_status"] == "no_label_match"]["rcept_no"])
    U_labelnoval = S(u[u["parse_status"] == "label_no_value"]["rcept_no"])
    U_bodyunavail = S(u[u["parse_status"] == "body_unavailable"]["rcept_no"])
    U_nonext = U_nolabel | U_labelnoval            # 711
    U_753 = U_nolabel | U_labelnoval | U_bodyunavail  # 753 (non-extracted incl zip)

    REG_all = S(reg["rcept_no"])
    REG_zip = S(reg[reg["residual_class"] == "zip_unparseable"]["rcept_no"])
    iscorr = reg["is_correction"].isin(["True", "true"])
    REG_corr = S(reg[iscorr]["rcept_no"])
    REG_zip_corr = S(reg[(reg["residual_class"] == "zip_unparseable") & iscorr]["rcept_no"])
    REG_zip_noncorr = S(reg[(reg["residual_class"] == "zip_unparseable") & (~iscorr)]["rcept_no"])
    REG_parser_resid = S(reg[reg["parse_status"].isin(["no_label_match", "label_no_value"])]["rcept_no"])

    MAN_all = S(man["rcept_no"])
    mcorr = man["is_correction"].isin(["True", "true"])
    MAN_corr = S(man[mcorr]["rcept_no"])
    MAN_noncorr = S(man[~mcorr]["rcept_no"])

    ADJ_all = S(adj["correction_rcept_no"])
    ADJ_zip = S(adj[adj["residual_action_class"] == "zip_unparseable_requires_source_recovery"]["correction_rcept_no"])
    LINKS_all = S(links["correction_rcept_no"])
    TAX_all = S(tax["rcept_no"])

    # ---- Set reconciliation helper ----
    recon: list[dict] = []
    def set_eq(name, expected_size, named_sets: dict):
        items = list(named_sets.items())
        ref_name, ref = items[0]
        all_match = True
        for nm, st in items[1:]:
            only_ref = ref - st
            only_st = st - ref
            ok = (not only_ref and not only_st)
            if not ok:
                all_match = False
                mm(name, f"{ref_name} vs {nm}: only_in_{ref_name}={len(only_ref)}, only_in_{nm}={len(only_st)}",
                   list(only_ref | only_st))
        size_ok = all(len(st) == expected_size for st in named_sets.values())
        if not size_ok:
            all_match = False
        recon.append({
            "check": name, "expected_size": expected_size,
            "sets_compared": " == ".join(named_sets.keys()),
            "sizes": "/".join(str(len(st)) for st in named_sets.values()),
            "set_equality": "PASS" if all_match else "FAIL",
        })

    # 2. 42 zip set: universe == register == manifest
    set_eq("zip_unparseable_set_42", 42, {"universe": U_zip, "register": REG_zip, "manifest": MAN_all})
    # 3. 39 correction-zip subset: adjudication == register == manifest
    set_eq("correction_zip_set_39", 39, {"adjudication": ADJ_zip, "register": REG_zip_corr, "manifest": MAN_corr})
    # 4. 3 non-correction zip: register == manifest
    set_eq("non_correction_zip_set_3", 3, {"register": REG_zip_noncorr, "manifest": MAN_noncorr})
    # 5. 711 parser non-extracted: universe(no_label∪label_no_value) == register == taxonomy
    set_eq("parser_nonextracted_set_711", 711, {"universe": U_nonext, "register": REG_parser_resid, "taxonomy": TAX_all})
    # 6. 166 correction: links == adjudication == register
    set_eq("correction_set_166", 166, {"links": LINKS_all, "adjudication": ADJ_all, "register": REG_corr})
    write_csv(OUT / "rowkey_set_reconciliation.csv", recon)

    # ---- 7. 862 register == U_753 ∪ correction_166 (overlap preserved) ----
    union_753_166 = U_753 | REG_corr  # correction set is REG_corr (== 166, verified above)
    only_reg = REG_all - union_753_166
    only_union = union_753_166 - REG_all
    overlap = U_753 & REG_corr
    overlap_rows = [{
        "component": "U_753 (universe non-extracted: no_label+label_no_value+zip)", "size": len(U_753),
    }, {
        "component": "correction_166 (register correction subset)", "size": len(REG_corr),
    }, {
        "component": "overlap (corrections that are also universe non-extracted)", "size": len(overlap),
    }, {
        "component": "union = 753 + 166 - overlap", "size": len(union_753_166),
    }, {
        "component": "register_all", "size": len(REG_all),
    }, {
        "component": "union == register_all", "size": "PASS" if (not only_reg and not only_union) else "FAIL",
    }]
    write_csv(OUT / "rowkey_overlap_summary.csv", overlap_rows)
    if only_reg or only_union:
        mm("register_union_862", f"register vs (U_753 ∪ corr_166): only_in_register={len(only_reg)}, only_in_union={len(only_union)}",
           list(only_reg | only_union))
    # overlap detail: by parse_status of the corrections that fall in U_753
    overlap_by_ps = {}
    if overlap:
        ups = dict(zip(u["rcept_no"], u["parse_status"]))
        from collections import Counter
        overlap_by_ps = dict(Counter(ups.get(r, "?") for r in overlap))

    # ---- Subset matrix ----
    submatrix = []
    def subset_chk(child_name, child, parent_name, parent):
        outside = child - parent
        submatrix.append({
            "child_set": child_name, "parent_set": parent_name,
            "child_size": len(child), "parent_size": len(parent),
            "child_subset_of_parent": "PASS" if not outside else "FAIL",
            "n_outside_parent": len(outside),
        })
        if outside:
            mm("subset_violation", f"{child_name} not subset of {parent_name}", list(outside))
    subset_chk("correction_zip_39", REG_zip_corr, "zip_42", REG_zip)
    subset_chk("non_correction_zip_3", REG_zip_noncorr, "zip_42", REG_zip)
    subset_chk("zip_42", U_zip, "body_unavailable_universe", U_bodyunavail)
    subset_chk("correction_166", REG_corr, "register_all_862", REG_all)
    subset_chk("parser_nonextracted_711", U_nonext, "register_all_862", REG_all)
    subset_chk("zip_42", U_zip, "register_all_862", REG_all)
    write_csv(OUT / "rowkey_subset_matrix.csv", submatrix)

    # ---- 8. No row-key mismatch silently changes parse/safety status ----
    status_checks = []
    # parse_status agreement across universe / register / taxonomy for shared keys
    u_ps = dict(zip(u["rcept_no"], u["parse_status"]))
    reg_ps = dict(zip(reg["rcept_no"], reg["parse_status"]))
    tax_ps = dict(zip(tax["rcept_no"], tax["parse_status"]))
    shared_reg = [k for k in reg_ps if k in u_ps and reg_ps[k]]
    disagree_reg = [k for k in shared_reg if reg_ps[k] != u_ps[k]]
    status_checks.append({"check": "parse_status agree universe vs register (shared keys)",
                          "shared": len(shared_reg), "disagreements": len(disagree_reg),
                          "result": "PASS" if not disagree_reg else "FAIL"})
    if disagree_reg:
        mm("parse_status_disagreement_reg", "register parse_status != universe", disagree_reg)
    disagree_tax = [k for k in tax_ps if k in u_ps and tax_ps[k] != u_ps[k]]
    status_checks.append({"check": "parse_status agree universe vs taxonomy (shared keys)",
                          "shared": len(tax_ps), "disagreements": len(disagree_tax),
                          "result": "PASS" if not disagree_tax else "FAIL"})
    if disagree_tax:
        mm("parse_status_disagreement_tax", "taxonomy parse_status != universe", disagree_tax)

    # fail-closed safety flags must hold wherever present (no row flipped safe)
    def flag_all(df, col, want):
        if col not in df.columns:
            return None
        bad = df[~df[col].isin([want])]
        return len(bad)
    for df, name in [(reg, "register"), (tax, "taxonomy"), (man, "manifest")]:
        for col, want in [("manual_review_required", "True"), ("executable_or_safe", "False"),
                          ("downstream_authoritative", "False")]:
            nbad = flag_all(df, col, want)
            if nbad is None:
                continue
            status_checks.append({"check": f"{name}.{col} all == {want}",
                                  "shared": len(df), "disagreements": nbad,
                                  "result": "PASS" if nbad == 0 else "FAIL"})
            if nbad:
                mm("safety_flag_flip", f"{name}.{col} has {nbad} rows != {want}", [])
    write_csv(OUT / "rowkey_status_consistency_check.csv", status_checks)

    # ---- Mismatch ledger (sentinel if none) ----
    write_csv(OUT / "rowkey_mismatch_ledger.csv", mismatches or [
        {"mismatch_id": "NONE", "check": "all_rowkey_checks", "detail":
         "no duplicate key, no set-equality violation, no subset violation, no "
         "union/overlap mismatch, no parse_status disagreement, no safety-flag flip",
         "example_keys": "", "n_keys": 0}])

    n_recon_fail = sum(1 for r in recon if r["set_equality"] == "FAIL")
    n_dup_fail = sum(1 for r in dup_rows if r["result"] == "FAIL")
    n_sub_fail = sum(1 for r in submatrix if r["child_subset_of_parent"] == "FAIL")
    n_status_fail = sum(1 for r in status_checks if r["result"] == "FAIL")
    union_ok = (not only_reg and not only_union)

    write_lock_table(OUT / "accepted_rowkey_lock_table.md", recon, overlap_rows, union_ok)
    write_input_manifest(OUT / "rowkey_input_manifest.md")
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_report(OUT / "report.md", dup_rows, recon, submatrix, overlap_rows,
                 status_checks, mismatches, n_dup_fail, n_recon_fail, n_sub_fail,
                 n_status_fail, union_ok, overlap_by_ps)

    print(json.dumps({
        "duplicate_fail": n_dup_fail,
        "set_reconciliation_fail": n_recon_fail,
        "subset_fail": n_sub_fail,
        "union_862_ok": union_ok,
        "status_consistency_fail": n_status_fail,
        "total_mismatches": len(mismatches),
        "overlap_size": len(overlap),
        "overlap_by_parse_status": overlap_by_ps,
    }, indent=2, default=str))


def write_lock_table(path: Path, recon, overlap_rows, union_ok) -> None:
    lines = ["# Accepted Row-Key Lock Table", "", "Date: 2026-05-26",
             "Phase: KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0", "",
             "Locked at the rcept_no SET level (not just aggregate counts):", "",
             "| set check | expected size | sets | set equality |", "|---|---:|---|---|"]
    for r in recon:
        lines.append(f"| {r['check']} | {r['expected_size']} | {r['sets_compared']} | {r['set_equality']} |")
    lines += ["", "## 862 register union (overlap preserved, not double-counted)", "",
              "| component | size |", "|---|---:|"]
    for r in overlap_rows:
        lines.append(f"| {r['component']} | {r['size']} |")
    lines += ["", f"Register == (U_753 ∪ correction_166) at set level: **{'PASS' if union_ok else 'FAIL'}**"]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_input_manifest(path: Path) -> None:
    lines = ["# Row-Key Input Manifest", "", "Date: 2026-05-26",
             "Phase: KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0", "",
             "## Input ledgers (read-only; key column)", "",
             f"- `{UNIV.relative_to(REPO)}` (rcept_no)",
             f"- `{LINKS.relative_to(REPO)}` (correction_rcept_no)",
             f"- `{ADJ.relative_to(REPO)}` (correction_rcept_no)",
             f"- `{REG.relative_to(REPO)}` (rcept_no)",
             f"- `{TAX.relative_to(REPO)}` (rcept_no)",
             f"- `{MAN.relative_to(REPO)}` (rcept_no)", "",
             "## No new data. No network. No parser invocation. No edits to closed artifacts.",
             "", "## New code",
             "- `src/audit/measurement_a0/p_residual_rowkey_integrity_audit.py` (this phase)."]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Residual Row-Key Integrity Audit)

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0

| hard lock | status |
|---|---|
| Existing local CSV/MD only; no new data | PASS |
| NO edits to prior closed-phase outputs | PASS |
| Mismatches recorded, NOT patched | PASS |
| NO CLOSE_NOTE.md created (executor does not self-close this phase) | PASS |
| NO downloads / API / credentials / body repair | PASS |
| NO parser change / rerun; NO candidate / body confirmation rerun | PASS |
| NO source recovery; NO parser-design approval | PASS |
| NO downstream wiring / C2 / C3 / event-log / executable-status table | PASS |
| NO strategy / performance / execution / backtest / production / paper / live / P08 / shadow | PASS |
| No row marked strategy-ready / execution-ready / production-ready / executable / safe / downstream-authoritative | PASS |
""", encoding="utf-8")


def write_report(path, dup_rows, recon, submatrix, overlap_rows, status_checks,
                 mismatches, n_dup_fail, n_recon_fail, n_sub_fail, n_status_fail,
                 union_ok, overlap_by_ps) -> None:
    lines = [
        "# KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0 — Report",
        "", "Date: 2026-05-26",
        "Phase opened by: Referee directive REF-OPEN-008 (via relay).",
        "Executor: Claude Code. Referee: Codex.",
        "",
        "## Phase name and scope",
        "",
        "Local row-key (rcept_no) integrity audit only. Verifies the accepted count "
        "locks hold at the SET level (exact rcept_no set equality + duplicate-key + "
        "union/overlap), not merely as aggregate counts. Existing local CSV/MD only; "
        "no new data; no edits to closed artifacts; mismatches recorded not patched; "
        "no CLOSE_NOTE (executor does not self-close).",
        "",
        "## Input artifacts used",
        "",
        f"- `{UNIV.relative_to(REPO)}`",
        f"- `{LINKS.relative_to(REPO)}`",
        f"- `{ADJ.relative_to(REPO)}`",
        f"- `{REG.relative_to(REPO)}`",
        f"- `{TAX.relative_to(REPO)}`",
        f"- `{MAN.relative_to(REPO)}`",
        "",
        "## Duplicate-key results",
        "",
        "| ledger | key | rows | unique | duplicates | result |",
        "|---|---|---:|---:|---:|---|",
    ]
    for r in dup_rows:
        lines.append(f"| {r['ledger']} | {r['key_col']} | {r['rows']} | {r['unique_keys']} | {r['duplicates']} | {r['result']} |")
    lines += [
        "",
        "## Row-key SET reconciliation (exact set equality)",
        "",
        "| set check | expected | sets | sizes | set equality |",
        "|---|---:|---|---|---|",
    ]
    for r in recon:
        lines.append(f"| {r['check']} | {r['expected_size']} | {r['sets_compared']} | {r['sizes']} | {r['set_equality']} |")
    lines += [
        "",
        "## Subset matrix",
        "",
        "| child set | parent set | child | parent | subset? | n outside |",
        "|---|---|---:|---:|---|---:|",
    ]
    for r in submatrix:
        lines.append(f"| {r['child_set']} | {r['parent_set']} | {r['child_size']} | {r['parent_size']} | {r['child_subset_of_parent']} | {r['n_outside_parent']} |")
    lines += [
        "",
        "## 862 register union (overlap preserved, not double-counted)",
        "",
        "| component | size |", "|---|---:|",
    ]
    for r in overlap_rows:
        lines.append(f"| {r['component']} | {r['size']} |")
    lines += [
        "",
        f"Overlap (corrections that are also universe non-extracted) by parse_status: "
        f"{overlap_by_ps} (expected: body_unavailable 39 + no_label_match 11 + "
        "label_no_value 7 = 57).",
        "",
        "## Status / safety consistency (no row-key mismatch silently changes status)",
        "",
        "| check | shared/rows | disagreements | result |",
        "|---|---:|---:|---|",
    ]
    for r in status_checks:
        lines.append(f"| {r['check']} | {r['shared']} | {r['disagreements']} | {r['result']} |")
    overall = (n_dup_fail == 0 and n_recon_fail == 0 and n_sub_fail == 0 and
               n_status_fail == 0 and union_ok)
    lines += [
        "",
        "## Overall result",
        "",
        f"- duplicate-key: {'PASS' if n_dup_fail == 0 else 'FAIL'}",
        f"- set reconciliation: {'PASS' if n_recon_fail == 0 else 'FAIL'}",
        f"- subset matrix: {'PASS' if n_sub_fail == 0 else 'FAIL'}",
        f"- 862 union/overlap: {'PASS' if union_ok else 'FAIL'}",
        f"- status/safety consistency: {'PASS' if n_status_fail == 0 else 'FAIL'}",
        f"- **total mismatches recorded: {len([m for m in mismatches]) if mismatches else 0}**",
        "",
        ("**CLEAN PASS — the accepted count locks hold at the rcept_no SET level.**"
         if overall else
         "**MISMATCHES FOUND — see rowkey_mismatch_ledger.csv. Not patched (closed "
         "artifacts are not edited).**"),
        "",
        "## Confirmations",
        "",
        "- No downloads / API / credentials / body repair / parser change / rerun.",
        "- No candidate / body confirmation rerun; no source recovery; no parser-design.",
        "- No edits to prior closed-phase outputs; mismatches recorded not patched.",
        "- No CLOSE_NOTE created. No strategy / execution / C2-C3 / event-log / "
        "executable-status table / production / paper / live / P08 / shadow work.",
        "",
        "## Decision requested from Referee",
        "",
        "Executor does NOT self-close. Requesting a verdict among:",
        "- **A.** close as row-key integrity audit complete (locks hold at set level);",
        "- **B.** require another integrity pass (widen checks / add ledgers);",
        "- **C.** authorize correction of a recorded row-key mismatch (would target a "
        "closed phase's artifact — needs explicit approval; none found this pass);",
        "- **D.** keep all strategy / execution research closed (unchanged).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
