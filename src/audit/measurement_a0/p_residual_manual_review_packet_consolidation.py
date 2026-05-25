"""KR-STATUS-RESIDUAL-MANUAL-REVIEW-PACKET-CONSOLIDATION-A0 — builder.

Referee directive REF-OPEN-010 (2026-05-26, via relay). Follows the now-closed
KR-STATUS-FAIL-CLOSED-INVARIANT-AUDIT-A0.

Goal: a single LOCAL human-review packet index for all known residual / correction /
source-defect blockers, keyed by rcept_no over the accepted 862 blocker-register
rows, using the already-accepted count / row-key / fail-closed locks. This is a
TRIAGE / INDEX artifact only.

It is NOT a fix, NOT source recovery, NOT parser design, NOT an event log, NOT an
executable-status table. It:
- reads existing local CSV/MD only; no new data,
- does NOT edit any prior closed-phase output; does NOT patch residuals,
- does NOT create CLOSE_NOTE.md (Executor does not self-close this phase),
- does NOT download / call APIs / use credentials / repair bodies / change or rerun
  the parser / rerun candidate search or body confirmation,
- newly marks no row parsed / recovered / executable / safe / authoritative /
  strategy-ready / execution-ready / production-ready.

Every packet row is human-review-only and fail-closed.
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
OUT = MA0 / "KR_STATUS_RESIDUAL_MANUAL_REVIEW_PACKET_CONSOLIDATION_A0"

REG = MA0 / "KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv"
TAX = MA0 / "KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/parser_nonextracted_taxonomy_ledger.csv"
MAN = MA0 / "KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0/source_recovery_candidate_manifest.csv"
LINKS = MA0 / "KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv"
ADJ = MA0 / "KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv"
ROWKEY_MM = MA0 / "KR_STATUS_RESIDUAL_ROWKEY_INTEGRITY_AUDIT_A0/rowkey_mismatch_ledger.csv"
FAILCLOSED_VL = MA0 / "KR_STATUS_FAIL_CLOSED_INVARIANT_AUDIT_A0/fail_closed_violation_ledger.csv"

TAX_ROOT_TO_BUCKET = {
    "label_present_but_attachment_or_table_context_required": "parser_table_or_attachment_context",
    "only_generic_or_contextual_label": "parser_generic_or_contextual_label",
    "label_present_but_value_in_unhandled_format": "parser_unhandled_format",
    "title_body_mismatch": "mixed_or_multi_blocker",
    "correction_disclosure_manual_only": "correction_manual_review",  # corrections handled by correction branch
}


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


def assign_bucket(is_corr, residual_class, action_class, tax_root) -> str:
    """Conservative single review bucket, priority-ordered (uses local evidence only)."""
    # 1. corrupt-ZIP source defect dominates (body unreadable locally)
    if residual_class == "zip_unparseable":
        return "source_recovery_required"
    # 2. correction rows are manual-review by policy (correction dimension dominant)
    if is_corr:
        if action_class == "rejected_wrong_candidate_quarantined":
            return "rejected_wrong_candidate_quarantine"
        return "correction_manual_review"
    # 3. non-correction parser non-extracted -> taxonomy root cause
    if tax_root:
        return TAX_ROOT_TO_BUCKET.get(tax_root, "mixed_or_multi_blocker")
    return "mixed_or_multi_blocker"


def sentinel_clean(path: Path, id_col: str) -> tuple[bool, int, str]:
    """A prior audit ledger is 'clean' iff its only row is the NONE sentinel."""
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
    except Exception:
        return False, -1, "unreadable"
    n = len(df)
    ids = set(df[id_col]) if id_col in df.columns else set()
    clean = (n == 1 and ids == {"NONE"})
    return clean, n, ("only NONE sentinel" if clean else f"{n} rows, ids={sorted(ids)[:5]}")


def main() -> None:
    print("[start] KR-STATUS-RESIDUAL-MANUAL-REVIEW-PACKET-CONSOLIDATION-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    reg = pd.read_csv(REG, dtype=str).fillna("")
    tax = pd.read_csv(TAX, dtype=str).fillna("")
    man = pd.read_csv(MAN, dtype=str).fillna("")
    links = pd.read_csv(LINKS, dtype=str).fillna("")
    adj = pd.read_csv(ADJ, dtype=str).fillna("")

    assert len(reg) == 862, f"expected 862 register rows, got {len(reg)}"

    tax_root = dict(zip(tax["rcept_no"], tax["root_cause_class"]))
    man_set = set(man["rcept_no"])
    links_conf = dict(zip(links["correction_rcept_no"], links["confidence_5tier"]))
    links_super = dict(zip(links["correction_rcept_no"], links["supersession_ready"]))
    adj_action = dict(zip(adj["correction_rcept_no"], adj["residual_action_class"]))

    defects: list[dict] = []
    def defect(kind, rcept, detail):
        defects.append({"defect_id": f"PKT_{len(defects)+1:03d}", "kind": kind,
                        "rcept_no": rcept, "detail": detail})

    packet: list[dict] = []
    bucket_ct: Counter = Counter()
    examples_by_bucket: dict[str, list[dict]] = {}
    # source-blocker crosswalk: (bucket) x (residual_class/parse_status)
    crosswalk: Counter = Counter()

    for r in reg.to_dict(orient="records"):
        rid = r["rcept_no"]
        is_corr = truthy(r.get("is_correction"))
        residual_class = r.get("residual_class", "")
        parse_status = r.get("parse_status", "")
        action_class = r.get("correction_action_class", "")
        troot = tax_root.get(rid, "")
        conf = links_conf.get(rid, "") if is_corr else ""
        # annotation completeness sanity
        if is_corr and not conf:
            defect("correction_without_confidence", rid, "correction row missing confidence_5tier in links")

        bucket = assign_bucket(is_corr, residual_class, action_class, troot)
        bucket_ct[bucket] += 1
        crosswalk[(bucket, parse_status or residual_class or "?")] += 1

        row = {
            "rcept_no": rid,
            "rcept_dt": r.get("rcept_dt", ""),
            "stock_code": r.get("stock_code", ""),
            "event_category": r.get("event_category", ""),
            "is_correction": is_corr,
            # parser / source annotations
            "parse_status": parse_status,
            "residual_class": residual_class,
            "blocker_tags": r.get("blocker_tags", ""),
            "taxonomy_root_cause": troot,
            "source_recovery_class": ("zip_unparseable_requires_source_recovery"
                                      if rid in man_set else ""),
            # correction annotations
            "correction_confidence_5tier": conf,
            "correction_action_class": action_class,
            "correction_supersession_ready": links_super.get(rid, "") if is_corr else "",
            # triage
            "review_bucket": bucket,
            "review_priority_note": _priority_note(bucket),
            # fail-closed (carried from register; never relaxed)
            "manual_review_required": True,
            "executable_or_safe": False,
            "downstream_authoritative": False,
            "parsed_clean_and_usable": False,
            "recovered": False,
            "human_validation_claimed": False,
        }
        packet.append(row)

        ex = examples_by_bucket.setdefault(bucket, [])
        if len(ex) < 6:
            ex.append({
                "review_bucket": bucket, "rcept_no": rid, "is_correction": is_corr,
                "parse_status": parse_status, "residual_class": residual_class,
                "taxonomy_root_cause": troot, "correction_confidence_5tier": conf,
                "correction_action_class": action_class,
            })

    assert sum(bucket_ct.values()) == 862, f"bucket sum {sum(bucket_ct.values())} != 862"

    examples = [e for lst in examples_by_bucket.values() for e in lst]

    # bucket counts
    write_csv(OUT / "manual_review_bucket_counts.csv",
              [{"review_bucket": k, "count": v} for k, v in bucket_ct.most_common()] +
              [{"review_bucket": "TOTAL", "count": sum(bucket_ct.values())}])

    # source crosswalk (bucket x parse_status/residual_class)
    cw_rows = [{"review_bucket": b, "source_blocker": s, "count": c}
               for (b, s), c in sorted(crosswalk.items())]
    write_csv(OUT / "manual_review_source_crosswalk.csv", cw_rows)

    write_csv(OUT / "manual_review_packet.csv", packet)
    write_csv(OUT / "manual_review_examples.csv", examples)

    # Sentinel checks
    rk_clean, rk_n, rk_note = sentinel_clean(ROWKEY_MM, "mismatch_id")
    fc_clean, fc_n, fc_note = sentinel_clean(FAILCLOSED_VL, "violation_id")
    sentinel_rows = [
        {"prior_audit": "rowkey_mismatch_ledger", "expected": "only NONE sentinel",
         "rows": rk_n, "clean": rk_clean, "note": rk_note},
        {"prior_audit": "fail_closed_violation_ledger", "expected": "only NONE sentinel",
         "rows": fc_n, "clean": fc_clean, "note": fc_note},
    ]
    write_csv(OUT / "prior_audit_sentinel_check.csv", sentinel_rows)
    if not rk_clean:
        defect("rowkey_sentinel_not_clean", "", rk_note)
    if not fc_clean:
        defect("fail_closed_sentinel_not_clean", "", fc_note)

    write_csv(OUT / "packet_build_defect_ledger.csv", defects or [
        {"defect_id": "NONE", "kind": "no_defect", "rcept_no": "",
         "detail": "packet built over all 862 register rows; every row bucketed and "
         "annotated; both prior audit sentinels clean"}])

    write_schema(OUT / "manual_review_packet_schema.md")
    write_input_manifest(OUT / "manual_review_input_manifest.md")
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_report(OUT / "report.md", bucket_ct, cw_rows, sentinel_rows, defects,
                 rk_clean, fc_clean)

    print(json.dumps({
        "packet_rows": len(packet),
        "bucket_counts": dict(bucket_ct),
        "bucket_sum": sum(bucket_ct.values()),
        "rowkey_sentinel_clean": rk_clean,
        "fail_closed_sentinel_clean": fc_clean,
        "packet_build_defects": len(defects),
    }, indent=2, default=str))


def _priority_note(bucket: str) -> str:
    return {
        "source_recovery_required": "corrupt cached body; needs source recovery (separate verdict + download approval) before any review",
        "parser_table_or_attachment_context": "html_inline body; value in table/attachment context; human can read body to extract",
        "parser_generic_or_contextual_label": "html_inline body mentions domain terms but no exact date label; human can locate value",
        "parser_unhandled_format": "label present; value in relative/non-ISO/unhandled format; human can interpret",
        "correction_manual_review": "correction disclosure; non-authoritative; human adjudicates linkage",
        "rejected_wrong_candidate_quarantine": "scored candidate not body-confirmed; quarantined; human confirms wrong-candidate",
        "mixed_or_multi_blocker": "does not fit a single clean bucket; human triages",
    }.get(bucket, "human review required")


def write_schema(path: Path) -> None:
    path.write_text("""# Manual-Review Packet Schema

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-MANUAL-REVIEW-PACKET-CONSOLIDATION-A0

## Key

- Row-level, keyed by **`rcept_no`**, over the accepted 862 blocker-register rows.

## Columns (manual_review_packet.csv)

- Identity/context: rcept_no, rcept_dt, stock_code, event_category, is_correction.
- Parser/source annotations: parse_status, residual_class, blocker_tags,
  taxonomy_root_cause, source_recovery_class.
- Correction annotations: correction_confidence_5tier, correction_action_class,
  correction_supersession_ready.
- Triage: review_bucket, review_priority_note.
- Fail-closed (carried, never relaxed): manual_review_required=True,
  executable_or_safe=False, downstream_authoritative=False,
  parsed_clean_and_usable=False, recovered=False, human_validation_claimed=False.

## Review buckets (conservative, one per row; priority-ordered)

1. `source_recovery_required` — corrupt-ZIP body (residual_class=zip_unparseable);
   dominant: needs source recovery (separate verdict + download approval).
2. `rejected_wrong_candidate_quarantine` — correction action
   rejected_wrong_candidate_quarantined.
3. `correction_manual_review` — other correction rows (non-authoritative).
4. `parser_table_or_attachment_context` — non-correction; taxonomy
   label_present_but_attachment_or_table_context_required.
5. `parser_generic_or_contextual_label` — non-correction; taxonomy
   only_generic_or_contextual_label.
6. `parser_unhandled_format` — non-correction; taxonomy
   label_present_but_value_in_unhandled_format.
7. `mixed_or_multi_blocker` — does not fit a single clean bucket (e.g.
   title_body_mismatch).

## Boundaries

- Human-review-only and fail-closed. The packet INDEXES blockers; it does NOT fix,
  recover, parse, or mark any row usable. supersession_ready / link_validated values
  carried from prior phases remain DESIGN-ONLY (not authority/safety/readiness/wired).
""", encoding="utf-8")


def write_input_manifest(path: Path) -> None:
    lines = ["# Manual-Review Input Manifest", "", "Date: 2026-05-26",
             "Phase: KR-STATUS-RESIDUAL-MANUAL-REVIEW-PACKET-CONSOLIDATION-A0", "",
             "## Input ledgers (read-only)", ""]
    for p in [REG, TAX, MAN, LINKS, ADJ, ROWKEY_MM, FAILCLOSED_VL]:
        lines.append(f"- `{p.relative_to(REPO)}`")
    lines += ["", "## No new data. No network. No parser invocation. No edits to closed artifacts.",
              "", "## New code",
              "- `src/audit/measurement_a0/p_residual_manual_review_packet_consolidation.py` (this phase)."]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Manual-Review Packet Consolidation)

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-MANUAL-REVIEW-PACKET-CONSOLIDATION-A0

| hard lock | status |
|---|---|
| Existing local CSV/MD only; no new data | PASS |
| NO edits to prior closed-phase outputs | PASS |
| Index/triage only; no residual fixed/recovered/parsed | PASS |
| NO CLOSE_NOTE.md created (executor does not self-close this phase) | PASS |
| NO source recovery / parser design | PASS |
| NO downloads / API / credentials / body repair / parser change / rerun | PASS |
| NO candidate / body confirmation rerun | PASS |
| NO downstream wiring / C2 / C3 / event-log / executable-status table | PASS |
| NO strategy / performance / execution / backtest / production / paper / live / P08 / shadow | PASS |
| 862 register row count preserved exactly | PASS |
| Every packet row fail-closed + human-review-only | PASS |
| No row newly marked parsed/recovered/executable/safe/authoritative/strategy-ready/execution-ready/production-ready | PASS |
| Design-only fields (supersession_ready/link_validated) carried as design-only, not promoted | PASS |
""", encoding="utf-8")


def write_report(path, bucket_ct, cw_rows, sentinel_rows, defects, rk_clean, fc_clean) -> None:
    lines = [
        "# KR-STATUS-RESIDUAL-MANUAL-REVIEW-PACKET-CONSOLIDATION-A0 — Report",
        "", "Date: 2026-05-26",
        "Phase opened by: Referee directive REF-OPEN-010 (via relay).",
        "Executor: Claude Code. Referee: Codex.",
        "",
        "## Phase name and scope",
        "",
        "Local manual-review packet consolidation only — a single human-review TRIAGE/"
        "INDEX over the accepted 862 blocker-register rows, keyed by rcept_no, using "
        "the already-accepted count / row-key / fail-closed locks. Existing local "
        "CSV/MD only; no new data; no edits to closed artifacts; index only (not a "
        "fix, not source recovery, not parser design, not an event log, not an "
        "executable-status table); no CLOSE_NOTE (executor does not self-close).",
        "",
        "## Input artifacts used",
        "",
    ]
    for p in [REG, TAX, MAN, LINKS, ADJ, ROWKEY_MM, FAILCLOSED_VL]:
        lines.append(f"- `{p.relative_to(REPO)}`")
    lines += [
        "",
        f"## Packet row count: **{sum(bucket_ct.values())}** (= accepted 862 blocker-register rows, keyed by rcept_no)",
        "",
        "## Review bucket counts (conservative, one per row; sum to 862)",
        "",
        "| review_bucket | count |", "|---|---:|",
    ]
    for k, v in bucket_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append(f"| **total** | **{sum(bucket_ct.values())}** |")
    lines += [
        "",
        "Bucket partition (priority-ordered, local evidence only): corrupt-ZIP rows → "
        "source_recovery_required; correction rows → rejected_wrong_candidate_quarantine "
        "or correction_manual_review; non-correction parser non-extracted rows → "
        "parser_* by taxonomy root cause; the lone title_body_mismatch → "
        "mixed_or_multi_blocker.",
        "",
        "## Source crosswalk (bucket × parse_status / residual_class)",
        "",
        "| review_bucket | source_blocker | count |", "|---|---|---:|",
    ]
    for r in cw_rows:
        lines.append(f"| {r['review_bucket']} | {r['source_blocker']} | {r['count']} |")
    lines += [
        "",
        "## Prior audit sentinel check",
        "",
        "| prior audit | expected | rows | clean |",
        "|---|---|---:|---|",
    ]
    for r in sentinel_rows:
        lines.append(f"| {r['prior_audit']} | {r['expected']} | {r['rows']} | {r['clean']} |")
    lines += [
        "",
        f"- rowkey_mismatch_ledger clean (only NONE): **{rk_clean}**",
        f"- fail_closed_violation_ledger clean (only NONE): **{fc_clean}**",
        "",
        f"## Packet-build defects: **{0 if (defects and defects[0].get('defect_id')=='NONE') else len(defects)}**",
        "",
        ("No packet-build defects. Every one of the 862 register rows is bucketed and "
         "annotated; both prior audit sentinels are clean."
         if (not defects or defects[0].get('defect_id') == 'NONE') else
         "See packet_build_defect_ledger.csv."),
        "",
        "## Confirmations",
        "",
        "- 862 blocker-register row count preserved exactly; every packet row "
        "fail-closed (manual_review_required=True; executable_or_safe / "
        "downstream_authoritative / parsed_clean_and_usable / recovered = False; "
        "human_validation_claimed=False).",
        "- No new data; no edits to closed artifacts; index/triage only — no residual "
        "fixed / recovered / parsed.",
        "- supersession_ready / link_validated values carried from prior phases remain "
        "DESIGN-ONLY (not promoted to authority / safety / readiness / wired).",
        "- No downloads / API / credentials / body repair / parser change / rerun / "
        "candidate or body confirmation rerun / source recovery / parser-design.",
        "- No CLOSE_NOTE; no strategy / execution / C2-C3 / event-log / "
        "executable-status table / production / paper / live / P08 / shadow.",
        "",
        "## Decision requested from Referee",
        "",
        "Executor does NOT self-close. Requesting a verdict among:",
        "- **A.** close as manual-review packet consolidation complete;",
        "- **B.** require another consolidation pass (refine buckets / annotations);",
        "- **C.** open a downstream manual-review or source-recovery action for one or "
        "more buckets (each needs its own verdict; recovery needs download approval);",
        "- **D.** keep all strategy / execution research closed (unchanged).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
