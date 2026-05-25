"""KR-STATUS-MANUAL-REVIEW-WORKLIST-VIEWS-A0 — builder.

Referee directive REF-OPEN-011 (2026-05-26, via relay). Follows the now-closed
KR-STATUS-RESIDUAL-MANUAL-REVIEW-PACKET-CONSOLIDATION-A0.

Goal: stable, deterministic WORKLIST VIEWS over the accepted 862-row manual-review
packet, for FUTURE human inspection only — preserving all fail-closed and review-only
limits.

This is a navigation/index view. It is NOT manual adjudication, NOT validation, NOT
source recovery, NOT parser design, NOT an event log, NOT an executable-status table.
It:
- reads existing local artifacts only; no new data,
- does NOT edit any prior closed-phase output,
- does NOT fix / adjudicate / recover / parse / validate / approve any row,
- does NOT create CLOSE_NOTE.md (Executor does not self-close this phase),
- adds NO outcome columns (validated / approved / effective_date_final / recovered /
  parsed / safe / executable / authoritative / readiness),
- newly marks no row parsed / recovered / executable / safe / authoritative /
  validated / approved / strategy-ready / execution-ready / production-ready.

`blocked_action_boundary` is a WARNING boundary field, NOT approval. Worklist views
remain human-navigation-only and fail-closed.
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
PKT_DIR = MA0 / "KR_STATUS_RESIDUAL_MANUAL_REVIEW_PACKET_CONSOLIDATION_A0"
OUT = MA0 / "KR_STATUS_MANUAL_REVIEW_WORKLIST_VIEWS_A0"

PACKET = PKT_DIR / "manual_review_packet.csv"
BUCKET_COUNTS = PKT_DIR / "manual_review_bucket_counts.csv"
SENTINEL = PKT_DIR / "prior_audit_sentinel_check.csv"
PKT_DEFECTS = PKT_DIR / "packet_build_defect_ledger.csv"

FAILCLOSED_FLAGS = ["manual_review_required", "executable_or_safe",
                    "downstream_authoritative", "parsed_clean_and_usable",
                    "recovered", "human_validation_claimed"]
FAILCLOSED_EXPECT = {"manual_review_required": True, "executable_or_safe": False,
                     "downstream_authoritative": False, "parsed_clean_and_usable": False,
                     "recovered": False, "human_validation_claimed": False}

# bucket -> blocked_action_boundary (WARNING field, NOT approval)
BUCKET_BOUNDARY = {
    "source_recovery_required": "requires_separate_source_recovery_verdict_and_download_approval",
    "parser_table_or_attachment_context": "requires_future_parser_design_verdict",
    "parser_generic_or_contextual_label": "requires_future_parser_design_verdict",
    "parser_unhandled_format": "requires_future_parser_design_verdict",
    "correction_manual_review": "manual_correction_review_only_non_authoritative",
    "rejected_wrong_candidate_quarantine": "quarantine_review_only",
    "mixed_or_multi_blocker": "manual_triage_only",
}

# Outcome column names that MUST NOT appear in the worklist (positive-outcome implying).
FORBIDDEN_OUTCOME_COLS = ["validated", "approved", "effective_date_final",
                          "parsed", "safe", "executable", "authoritative",
                          "strategy_ready", "execution_ready", "production_ready",
                          "recovered_ok", "recovery_done"]


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
    print("[start] KR-STATUS-MANUAL-REVIEW-WORKLIST-VIEWS-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    pkt = pd.read_csv(PACKET, dtype=str).fillna("")

    integrity: list[dict] = []
    defects: list[dict] = []
    def defect(kind, detail):
        defects.append({"defect_id": f"WLB_{len(defects)+1:03d}", "kind": kind, "detail": detail})

    # 1. packet 862 rows / 862 unique rcept_no
    n = len(pkt)
    uniq = pkt["rcept_no"].nunique()
    integrity.append({"check": "packet_rows==862", "value": n, "result": "PASS" if n == 862 else "FAIL"})
    integrity.append({"check": "packet_unique_rcept_no==862", "value": uniq, "result": "PASS" if uniq == 862 else "FAIL"})
    if n != 862 or uniq != 862:
        defect("packet_count_mismatch", f"rows={n}, unique={uniq}")

    # 2. bucket counts still sum to 862 and match the accepted distribution
    bc = pd.read_csv(BUCKET_COUNTS, dtype=str).fillna("")
    bc_nontotal = bc[bc["review_bucket"] != "TOTAL"]
    bc_sum = bc_nontotal["count"].astype(int).sum()
    live_bc = Counter(pkt["review_bucket"])
    bc_match = (bc_sum == 862 and all(
        int(r["count"]) == live_bc.get(r["review_bucket"], -1) for _, r in bc_nontotal.iterrows()))
    integrity.append({"check": "bucket_counts_sum==862_and_match_packet", "value": bc_sum,
                      "result": "PASS" if bc_match else "FAIL"})
    if not bc_match:
        defect("bucket_count_mismatch", f"accepted sum {bc_sum} vs live {dict(live_bc)}")

    # 3. all packet rows fail-closed
    for flag, want in FAILCLOSED_EXPECT.items():
        if flag not in pkt.columns:
            integrity.append({"check": f"failclosed:{flag}", "value": "ABSENT", "result": "FAIL"})
            defect("failclosed_flag_absent", flag)
            continue
        if want:
            nbad = int((~pkt[flag].map(truthy)).sum())
        else:
            nbad = int(pkt[flag].map(truthy).sum())
        integrity.append({"check": f"failclosed:{flag}=={want}", "value": nbad,
                          "result": "PASS" if nbad == 0 else "FAIL"})
        if nbad:
            defect("failclosed_violation", f"{flag}: {nbad} rows != {want}")

    # 4. prior packet sentinels clean
    sent = pd.read_csv(SENTINEL, dtype=str).fillna("")
    sent_clean = all(truthy(v) for v in sent["clean"]) if "clean" in sent.columns else False
    integrity.append({"check": "prior_audit_sentinel_check_all_clean", "value": str(sent_clean),
                      "result": "PASS" if sent_clean else "FAIL"})
    if not sent_clean:
        defect("prior_sentinel_not_clean", "prior_audit_sentinel_check.csv has clean != True")
    pdl = pd.read_csv(PKT_DEFECTS, dtype=str).fillna("")
    pdl_none = (len(pdl) == 1 and set(pdl.get("defect_id", pd.Series())) == {"NONE"})
    integrity.append({"check": "packet_build_defect_ledger_only_NONE", "value": len(pdl),
                      "result": "PASS" if pdl_none else "FAIL"})
    if not pdl_none:
        defect("packet_defect_ledger_not_none", f"{len(pdl)} rows")

    write_csv(OUT / "worklist_integrity_check.csv", integrity)

    # 5./6. Build deterministic worklist rows (stable sort by review_bucket, rcept_no).
    recs = pkt.to_dict(orient="records")
    recs.sort(key=lambda r: (r["review_bucket"], r["rcept_no"]))
    # per-bucket shard sequence
    shard_seq: Counter = Counter()
    worklist: list[dict] = []
    examples_by_bucket: dict[str, list[dict]] = {}
    for i, r in enumerate(recs, 1):
        bucket = r["review_bucket"]
        shard_seq[bucket] += 1
        wl = {
            "worklist_id": f"WL-{i:05d}",
            "shard_id": f"SHARD-{bucket}",
            "shard_seq": shard_seq[bucket],
            "review_bucket": bucket,
            "rcept_no": r["rcept_no"],
            # read-only source context
            "rcept_dt": r.get("rcept_dt", ""),
            "stock_code": r.get("stock_code", ""),
            "event_category": r.get("event_category", ""),
            "is_correction": r.get("is_correction", ""),
            "parse_status": r.get("parse_status", ""),
            "residual_class": r.get("residual_class", ""),
            "taxonomy_root_cause": r.get("taxonomy_root_cause", ""),
            "source_recovery_class": r.get("source_recovery_class", ""),
            "correction_confidence_5tier": r.get("correction_confidence_5tier", ""),
            "correction_action_class": r.get("correction_action_class", ""),
            # read-only review note + WARNING boundary (not approval)
            "review_note": r.get("review_priority_note", ""),
            "blocked_action_boundary": BUCKET_BOUNDARY.get(bucket, "manual_triage_only"),
            # carried fail-closed flags (NOT outcome columns; same as packet)
            "manual_review_required": True,
            "executable_or_safe": False,
            "downstream_authoritative": False,
            "parsed_clean_and_usable": False,
            "recovered": False,
            "human_validation_claimed": False,
        }
        worklist.append(wl)
        ex = examples_by_bucket.setdefault(bucket, [])
        if len(ex) < 5:
            ex.append({k: wl[k] for k in ("worklist_id", "shard_id", "review_bucket",
                       "rcept_no", "parse_status", "taxonomy_root_cause",
                       "correction_confidence_5tier", "blocked_action_boundary")})

    # Guard: no forbidden outcome column leaked into the worklist.
    wl_cols = set(worklist[0].keys()) if worklist else set()
    leaked = [c for c in FORBIDDEN_OUTCOME_COLS if c in wl_cols]
    integrity.append({"check": "no_forbidden_outcome_columns", "value": ",".join(leaked) or "none",
                      "result": "PASS" if not leaked else "FAIL"})
    if leaked:
        defect("forbidden_outcome_column", ",".join(leaked))
    # rewrite integrity with the guard row included
    write_csv(OUT / "worklist_integrity_check.csv", integrity)

    assert len(worklist) == 862, f"worklist rows {len(worklist)} != 862"

    write_csv(OUT / "manual_review_worklist.csv", worklist)

    # worklist bucket counts
    wbc = Counter(w["review_bucket"] for w in worklist)
    write_csv(OUT / "worklist_bucket_counts.csv",
              [{"review_bucket": k, "count": v, "blocked_action_boundary": BUCKET_BOUNDARY.get(k, "manual_triage_only")}
               for k, v in wbc.most_common()] +
              [{"review_bucket": "TOTAL", "count": sum(wbc.values()), "blocked_action_boundary": ""}])

    # shard manifest (one shard per bucket; worklist_id range)
    shard_rows = []
    for bucket in sorted(wbc):
        ids = [w["worklist_id"] for w in worklist if w["review_bucket"] == bucket]
        shard_rows.append({
            "shard_id": f"SHARD-{bucket}", "review_bucket": bucket, "rows": len(ids),
            "worklist_id_first": ids[0], "worklist_id_last": ids[-1],
            "blocked_action_boundary": BUCKET_BOUNDARY.get(bucket, "manual_triage_only"),
        })
    write_csv(OUT / "worklist_shard_manifest.csv", shard_rows)

    examples = [e for lst in examples_by_bucket.values() for e in lst]
    write_csv(OUT / "worklist_examples.csv", examples)

    write_csv(OUT / "worklist_build_defect_ledger.csv", defects or [
        {"defect_id": "NONE", "kind": "no_defect",
         "detail": "862 rows / 862 unique; bucket counts match; all fail-closed; prior "
         "sentinels clean; no forbidden outcome column; worklist deterministic"}])

    write_boundary_policy(OUT / "worklist_boundary_policy.md")
    write_input_manifest(OUT / "worklist_input_manifest.md")
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_report(OUT / "report.md", integrity, wbc, shard_rows, defects)

    n_int_fail = sum(1 for r in integrity if r["result"] == "FAIL")
    print(json.dumps({
        "worklist_rows": len(worklist),
        "bucket_counts": dict(wbc),
        "shards": len(shard_rows),
        "integrity_checks": len(integrity), "integrity_fail": n_int_fail,
        "build_defects": len(defects),
        "deterministic_sort": "review_bucket,rcept_no",
    }, indent=2, default=str))


def write_boundary_policy(path: Path) -> None:
    lines = ["# Worklist Boundary Policy", "", "Date: 2026-05-26",
             "Phase: KR-STATUS-MANUAL-REVIEW-WORKLIST-VIEWS-A0", "",
             "`blocked_action_boundary` is a WARNING boundary field, NOT approval. It",
             "tells a future human reviewer what would still be required BEFORE any",
             "action — it grants nothing.", "",
             "| review_bucket | blocked_action_boundary | meaning |",
             "|---|---|---|"]
    meanings = {
        "requires_separate_source_recovery_verdict_and_download_approval":
            "body unreadable; needs a separate Referee verdict + explicit download/API approval",
        "requires_future_parser_design_verdict":
            "needs a separate parser-design/feasibility verdict; parser changes forbidden until then",
        "manual_correction_review_only_non_authoritative":
            "correction disclosure; human review only; never downstream-authoritative",
        "quarantine_review_only": "scored candidate not body-confirmed; quarantined; human confirms wrong-candidate",
        "manual_triage_only": "does not fit a single clean bucket; human triage only",
    }
    for bucket, boundary in BUCKET_BOUNDARY.items():
        lines.append(f"| `{bucket}` | `{boundary}` | {meanings.get(boundary, '')} |")
    lines += ["", "## Boundary is not approval",
              "- No boundary value authorizes recovery, downloads, parser changes,",
              "  adjudication, validation, or any downstream action.",
              "- Worklist views are human-navigation-only and fail-closed. Every row",
              "  remains manual_review_required=True with all usability/authority flags False."]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_input_manifest(path: Path) -> None:
    lines = ["# Worklist Input Manifest", "", "Date: 2026-05-26",
             "Phase: KR-STATUS-MANUAL-REVIEW-WORKLIST-VIEWS-A0", "",
             "## Input artifacts (read-only)", ""]
    for p in [PACKET, BUCKET_COUNTS, SENTINEL, PKT_DEFECTS]:
        lines.append(f"- `{p.relative_to(REPO)}`")
    lines += ["", "## No new data. No network. No parser invocation. No edits to closed artifacts.",
              "", "## Determinism",
              "- Worklist rows sorted by (review_bucket, rcept_no); worklist_id = WL-{i:05d}",
              "  in that order. Re-running on the same packet yields identical IDs.",
              "", "## New code",
              "- `src/audit/measurement_a0/p_manual_review_worklist_views.py` (this phase)."]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Manual-Review Worklist Views)

Date: 2026-05-26
Phase: KR-STATUS-MANUAL-REVIEW-WORKLIST-VIEWS-A0

| hard lock | status |
|---|---|
| Existing local artifacts only; no new data | PASS |
| NO edits to prior closed-phase outputs | PASS |
| Navigation/index view only; no fix/adjudicate/recover/parse/validate/approve | PASS |
| NO CLOSE_NOTE.md created (executor does not self-close this phase) | PASS |
| NO source recovery / parser design / manual adjudication | PASS |
| NO downloads / API / credentials / body repair / parser change / rerun | PASS |
| NO candidate / body confirmation rerun | PASS |
| NO downstream wiring / C2 / C3 / event-log / executable-status table | PASS |
| NO strategy / performance / execution / backtest / production / paper / live / P08 / shadow | PASS |
| NO outcome columns (validated/approved/effective_date_final/parsed/safe/executable/authoritative/readiness) | PASS |
| Every worklist row carries fail-closed flags (manual_review_required=True; others False) | PASS |
| blocked_action_boundary is a WARNING field, not approval | PASS |
| 862 row count preserved; deterministic worklist_id | PASS |
""", encoding="utf-8")


def write_report(path, integrity, wbc, shard_rows, defects) -> None:
    n_int_fail = sum(1 for r in integrity if r["result"] == "FAIL")
    lines = [
        "# KR-STATUS-MANUAL-REVIEW-WORKLIST-VIEWS-A0 — Report",
        "", "Date: 2026-05-26",
        "Phase opened by: Referee directive REF-OPEN-011 (via relay).",
        "Executor: Claude Code. Referee: Codex.",
        "",
        "## Phase name and scope",
        "",
        "Local worklist-view generation only, derived from the closed 862-row "
        "manual-review packet. Navigation/index view for FUTURE human inspection — NOT "
        "manual adjudication, NOT validation, NOT source recovery, NOT parser design, "
        "NOT an event log, NOT an executable-status table. Existing local artifacts "
        "only; no new data; no edits to closed artifacts; no CLOSE_NOTE.",
        "",
        "## Input artifacts used",
        "",
    ]
    for p in [PACKET, BUCKET_COUNTS, SENTINEL, PKT_DEFECTS]:
        lines.append(f"- `{p.relative_to(REPO)}`")
    lines += [
        "",
        f"## Worklist row count: **{sum(wbc.values())}** (= accepted 862 packet rows; deterministic, sorted by review_bucket,rcept_no; worklist_id=WL-NNNNN)",
        "",
        "## Bucket / shard counts (sum to 862)",
        "",
        "| review_bucket | shard_id | rows | worklist_id range | blocked_action_boundary |",
        "|---|---|---:|---|---|",
    ]
    for r in shard_rows:
        lines.append(f"| {r['review_bucket']} | {r['shard_id']} | {r['rows']} | {r['worklist_id_first']}..{r['worklist_id_last']} | {r['blocked_action_boundary']} |")
    lines.append(f"| **TOTAL** | — | **{sum(wbc.values())}** | — | — |")
    lines += [
        "",
        "## Integrity check results",
        "",
        "| check | value | result |",
        "|---|---|---|",
    ]
    for r in integrity:
        lines.append(f"| {r['check']} | {r['value']} | {r['result']} |")
    lines += [
        "",
        f"## Worklist-build defects: **{0 if (defects and defects[0].get('defect_id')=='NONE') else len(defects)}**",
        "",
        ("No worklist-build defects. 862 rows / 862 unique; bucket counts match the "
         "accepted distribution; all fail-closed; prior sentinels clean; no forbidden "
         "outcome column; worklist deterministic."
         if (not defects or defects[0].get('defect_id') == 'NONE') else
         "See worklist_build_defect_ledger.csv."),
        "",
        "## Confirmations",
        "",
        "- 862-row count preserved; worklist deterministic (sorted by review_bucket, "
        "rcept_no; stable WL-NNNNN ids).",
        "- Every worklist row fail-closed: manual_review_required=True; "
        "executable_or_safe / downstream_authoritative / parsed_clean_and_usable / "
        "recovered / human_validation_claimed = False.",
        "- NO outcome columns added (no validated / approved / effective_date_final / "
        "parsed / safe / executable / authoritative / readiness).",
        "- `blocked_action_boundary` is a WARNING boundary field, NOT approval.",
        "- No new data; no edits to closed artifacts; index/navigation only — no row "
        "fixed / adjudicated / recovered / parsed / validated / approved.",
        "- No downloads / API / credentials / body repair / parser change / rerun / "
        "candidate or body confirmation rerun / source recovery / parser-design.",
        "- No CLOSE_NOTE; no strategy / execution / C2-C3 / event-log / "
        "executable-status table / production / paper / live / P08 / shadow.",
        "",
        "## Decision requested from Referee",
        "",
        "Executor does NOT self-close. Requesting a verdict among:",
        "- **A.** close as manual-review worklist views complete;",
        "- **B.** require another worklist pass (refine shards / fields / ordering);",
        "- **C.** open a downstream action for a shard/bucket (each needs its own "
        "verdict; recovery needs download approval, parser changes need a parser-design "
        "verdict);",
        "- **D.** keep all strategy / execution research closed (unchanged).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
