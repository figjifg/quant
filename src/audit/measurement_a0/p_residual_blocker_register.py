"""KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0 — builder.

Referee directive REF-OPEN-004 (2026-05-26, via relay). Follows the now-closed
KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0.

Goal: consolidate the residual blockers scattered across the recently-closed phases
into ONE fail-closed, row-level register keyed by rcept_no, so that NO future phase
mistakes a residual row for parsed / executable / safe / authoritative.

Coverage (union by rcept_no):
- 42 universe-level zip_unparseable rows (body never parsed),
- 511 no_label_match rows (html_inline body, parser found no label),
- 200 label_no_value rows (label found, no value),
- all 166 correction rows (manual_review_required regardless of parse outcome).

This is a LOCAL CONSOLIDATION ONLY. It reads existing accepted CSV artifacts and:
- does NOT download / call APIs / repair bodies / acquire data,
- does NOT re-run the parser / candidate search / body confirmation,
- does NOT expand parser features,
- is NOT an event log, NOT an executable-status table, NOT downstream wiring,
- does NOT mark any row executable / safe / strategy-ready / production-ready /
  downstream-authoritative.

Every register row is fail-closed: manual_review_required=True, executable_or_safe
=False, downstream_authoritative=False.
"""
from __future__ import annotations

import csv as _csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

MA0 = REPO / "reports/experiments/measurement_A0"
UNIV = MA0 / "S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv"
ADJ = MA0 / "KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv"
LINKS = MA0 / "KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv"
OUT = MA0 / "KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0"

# Accepted prior counts (reconciliation targets).
PRIOR_UNIVERSE = {"total": 12187, "extracted": 11434, "no_label_match": 511,
                  "label_no_value": 200, "body_unavailable": 42, "zip_unparseable": 42}
PRIOR_CORRECTION_ACTIONS = {
    "accepted_high_validated_design_only": 17,
    "body_confirms_candidate_but_below_high": 40,
    "rejected_wrong_candidate_quarantined": 17,
    "no_link_original_not_found": 37,
    "no_link_insufficient_evidence": 15,
    "no_link_cross_category_blocked": 1,
    "zip_unparseable_requires_source_recovery": 39,
}

# correction action class -> correction blocker tag
ACTION_TO_TAG = {
    "accepted_high_validated_design_only": "correction_high_validated_design_only",
    "body_confirms_candidate_but_below_high": "correction_body_confirmed_below_high",
    "rejected_wrong_candidate_quarantined": "correction_wrong_candidate_quarantined",
    "no_link_original_not_found": "correction_no_link_original_not_found",
    "no_link_insufficient_evidence": "correction_no_link_insufficient_evidence",
    "no_link_cross_category_blocked": "correction_no_link_cross_category_blocked",
    # zip correction rows are blocked at source; they carry source tags instead of a
    # linkage-outcome tag (plus correction_manual_review_required).
    "zip_unparseable_requires_source_recovery": None,
}


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
    print("[start] KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    univ = pd.read_csv(UNIV, dtype=str).fillna("")
    adj = pd.read_csv(ADJ, dtype=str).fillna("")
    print(f"[load] universe={len(univ)} correction_actions={len(adj)}")

    # Control: reconcile universe counts.
    ps = Counter(univ["parse_status"])
    rc = Counter(univ["residual_class"])
    assert len(univ) == PRIOR_UNIVERSE["total"], "universe total mismatch"
    for k in ("extracted", "no_label_match", "label_no_value", "body_unavailable"):
        assert ps.get(k, 0) == PRIOR_UNIVERSE[k], f"parse_status {k} mismatch {ps.get(k)}"
    assert rc.get("zip_unparseable", 0) == PRIOR_UNIVERSE["zip_unparseable"], "zip mismatch"
    print(f"[control] universe parse_status reconciled {dict(ps)}")

    # Correction action map.
    action_by_id = dict(zip(adj["correction_rcept_no"], adj["residual_action_class"]))
    corr_ids = set(action_by_id)
    assert len(corr_ids) == 166, f"expected 166 corrections, got {len(corr_ids)}"
    act_ct = Counter(action_by_id.values())
    for k, v in PRIOR_CORRECTION_ACTIONS.items():
        assert act_ct.get(k, 0) == v, f"correction action {k} mismatch {act_ct.get(k)}"
    print(f"[control] correction actions reconciled {dict(act_ct)}")

    # Universe lookup by rcept_no.
    univ_by_id = {r["rcept_no"]: r for r in univ.to_dict(orient="records")}

    # Build the register: union of (universe residual rows) ∪ (166 correction rows).
    # Universe residual rows = parse_status in {no_label_match, label_no_value,
    # body_unavailable} (i.e. NOT cleanly extracted). Plus all corrections.
    residual_status = {"no_label_match", "label_no_value", "body_unavailable"}
    register_ids: set[str] = set()
    for rid, r in univ_by_id.items():
        if r["parse_status"] in residual_status:
            register_ids.add(rid)
    register_ids |= corr_ids  # all corrections, incl. parser-extracted ones

    print(f"[register] {len(register_ids)} unique rcept_no")

    register_rows: list[dict] = []
    tag_counts: Counter = Counter()
    overlap_cell: Counter = Counter()         # (parse_status, correction_action|not_correction)
    correction_overlap_rows: list[dict] = []  # corrections × their universe body residual
    packet_rows: list[dict] = []
    examples: list[dict] = []
    source_recovery_subset: list[dict] = []

    for rid in sorted(register_ids):
        u = univ_by_id.get(rid, {})
        parse_status = u.get("parse_status", "MISSING_FROM_UNIVERSE")
        residual_class = u.get("residual_class", "")
        is_corr = rid in corr_ids
        action = action_by_id.get(rid, "")

        tags: list[str] = []
        # source / parser dimension
        if residual_class == "zip_unparseable" or parse_status == "body_unavailable":
            tags += ["source_zip_unparseable", "source_recovery_required_separate_approval"]
        elif parse_status == "no_label_match":
            tags.append("parser_no_label_match")
        elif parse_status == "label_no_value":
            tags.append("parser_label_no_value")
        # extracted rows get no source/parser blocker tag (only here if correction)

        # correction dimension
        if is_corr:
            tags.append("correction_manual_review_required")
            ctag = ACTION_TO_TAG.get(action)
            if ctag:
                tags.append(ctag)

        # universal fail-closed tag
        tags.append("manual_review_required")

        # dedupe while preserving order
        seen = set()
        tags = [t for t in tags if not (t in seen or seen.add(t))]
        for t in tags:
            tag_counts[t] += 1

        overlap_cell[(parse_status, action if is_corr else "not_correction")] += 1

        row = {
            "rcept_no": rid,
            "rcept_dt": u.get("rcept_dt", ""),
            "stock_code": u.get("stock_code", ""),
            "event_category": u.get("event_category", ""),
            "in_universe_status_table": rid in univ_by_id,
            "body_format": u.get("body_format", ""),
            "parse_status": parse_status,
            "residual_class": residual_class,
            "is_correction": is_corr,
            "correction_action_class": action,
            "blocker_tags": "|".join(tags),
            "n_blocker_tags": len(tags),
            # fail-closed assertions — always these values:
            "manual_review_required": True,
            "executable_or_safe": False,
            "downstream_authoritative": False,
            "parsed_clean_and_usable": False,  # even 'extracted' corrections are NOT usable downstream
            "strategy_ready": False,
            "production_ready": False,
        }
        register_rows.append(row)

        packet_rows.append({
            "rcept_no": rid,
            "event_category": u.get("event_category", ""),
            "is_correction": is_corr,
            "primary_blocker": tags[0] if tags else "manual_review_required",
            "blocker_tags": "|".join(tags),
            "do_not_use_as": "executable | safe | strategy-ready | downstream-authoritative | parsed-clean",
            "manual_review_required": True,
            "human_validation_claimed": False,
        })

        if is_corr and parse_status in residual_status:
            correction_overlap_rows.append({
                "rcept_no": rid,
                "event_category": u.get("event_category", ""),
                "universe_parse_status": parse_status,
                "universe_residual_class": residual_class,
                "correction_action_class": action,
                "overlap_type": ("correction_AND_universe_zip" if residual_class == "zip_unparseable"
                                 else f"correction_AND_{parse_status}"),
            })

        if "source_recovery_required_separate_approval" in tags:
            source_recovery_subset.append({
                "rcept_no": rid,
                "event_category": u.get("event_category", ""),
                "is_correction": is_corr,
                "correction_action_class": action,
                "blocker": "zip_unparseable; body never parsed",
                "recovery_performed": False,
                "needs_separate_verdict_and_download_approval": True,
            })

        if len(examples) < 30:
            examples.append({
                "rcept_no": rid, "parse_status": parse_status,
                "is_correction": is_corr, "correction_action_class": action,
                "blocker_tags": "|".join(tags),
            })

    # Overlap matrix rows
    overlap_rows = []
    for (ps_k, act_k), cnt in sorted(overlap_cell.items()):
        overlap_rows.append({
            "universe_parse_status": ps_k,
            "correction_action_or_not": act_k,
            "count": cnt,
        })

    # Tag count CSV
    tag_rows = [{"blocker_tag": k, "count": v} for k, v in tag_counts.most_common()]

    # --- Sanity reconciliations ---
    n_zip = tag_counts["source_zip_unparseable"]
    n_no_label = tag_counts["parser_no_label_match"]
    n_label_no_value = tag_counts["parser_label_no_value"]
    n_corr_mrr = tag_counts["correction_manual_review_required"]
    assert n_zip == 42, f"zip tag {n_zip} != 42"
    assert n_no_label == 511, f"no_label tag {n_no_label} != 511"
    assert n_label_no_value == 200, f"label_no_value tag {n_label_no_value} != 200"
    assert n_corr_mrr == 166, f"correction tag {n_corr_mrr} != 166"
    assert tag_counts["manual_review_required"] == len(register_ids), "manual_review tag != register size"
    # 39 correction zip ⊂ 42 universe zip
    corr_zip = sum(1 for r in register_rows if r["is_correction"] and r["residual_class"] == "zip_unparseable")
    assert corr_zip == 39, f"correction zip {corr_zip} != 39"

    # Write deliverables
    write_csv(OUT / "residual_blocker_register.csv", register_rows)
    write_csv(OUT / "blocker_tag_counts.csv", tag_rows)
    write_csv(OUT / "blocker_overlap_matrix.csv", overlap_rows)
    write_csv(OUT / "correction_overlap_with_body_residuals.csv", correction_overlap_rows)
    write_csv(OUT / "manual_review_blocker_packet.csv", packet_rows)
    # optional
    write_csv(OUT / "blocker_examples.csv", examples)
    write_csv(OUT / "source_recovery_candidate_subset.csv", source_recovery_subset)

    write_fail_closed_policy(OUT / "fail_closed_policy_table.md")
    write_schema(OUT / "blocker_register_schema.md")
    write_input_manifest(OUT / "prior_phase_input_manifest.md")
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_summary(OUT / "residual_blocker_register_summary.md",
                  len(register_ids), tag_counts, overlap_cell, corr_zip)
    write_report(OUT / "report.md", len(register_ids), tag_counts, overlap_cell,
                 corr_zip, correction_overlap_rows)

    print(json.dumps({
        "register_unique_rcept_no": len(register_ids),
        "universe_residual_rows": len(register_ids) - 109,  # informational
        "tag_counts": dict(tag_counts),
        "correction_zip_subset": corr_zip,
        "overlap_cells": {f"{k[0]}|{k[1]}": v for k, v in sorted(overlap_cell.items())},
        "source_recovery_subset": len(source_recovery_subset),
    }, indent=2, default=str))


def write_fail_closed_policy(path: Path) -> None:
    path.write_text("""# Fail-Closed Policy Table

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0

Every blocker tag is FAIL-CLOSED: in the absence of explicit, separately-approved
resolution, the row MUST be treated as unusable. What each tag forbids downstream:

| blocker tag | what a future phase MUST NOT infer |
|---|---|
| `source_zip_unparseable` | MUST NOT treat as parsed / extracted / body-available / usable. Body never parsed (corrupt ZIP). |
| `source_recovery_required_separate_approval` | MUST NOT download/repair without a SEPARATE Referee verdict + download approval. |
| `parser_no_label_match` | html_inline body present but parser found NO target label. MUST NOT treat as extracted / safe / value-bearing. |
| `parser_label_no_value` | label found but NO value parsed. MUST NOT treat as an extracted value. |
| `correction_manual_review_required` | Correction disclosure. Parser output NON-authoritative. MUST NOT treat as authoritative by default. |
| `correction_high_validated_design_only` | DESIGN-ONLY validated link. MUST NOT wire / supersede / execute. Still manual review. |
| `correction_body_confirmed_below_high` | Body references candidate but below high bar. MUST NOT treat as confirmed link. |
| `correction_wrong_candidate_quarantined` | Scored candidate NOT supported by body. MUST NOT treat as a link. Quarantined. |
| `correction_no_link_original_not_found` | No local original found. MUST NOT fabricate a link. |
| `correction_no_link_insufficient_evidence` | Candidate(s) too weak. MUST NOT treat as linked. |
| `correction_no_link_cross_category_blocked` | Cross-category original blocked by policy. MUST NOT auto-link. |
| `manual_review_required` | Universal. MUST NOT treat ANY register row as executable / safe / strategy-ready / production-ready / downstream-authoritative. |

## Global fail-closed rules

- No register row is parsed-clean-and-usable, executable, safe, strategy-ready,
  production-ready, or downstream-authoritative — regardless of tag combination.
- A correction row that is parser-`extracted` is STILL
  `correction_manual_review_required` (correction parser output non-authoritative).
- This register is NOT an event log, NOT an executable-status table, NOT downstream
  wiring. It only preserves residual blocker + manual-review state for later local
  review.
""", encoding="utf-8")


def write_schema(path: Path) -> None:
    path.write_text("""# Blocker Register Schema

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0

## Key

- Row-level, keyed by **`rcept_no`** (the OPENDART disclosure receipt number).
- Corrections are status rows too, so `correction_rcept_no` == `rcept_no`; the
  register uses a single combined key (`rcept_no`). `is_correction` flags whether a
  row is a correction.

## Columns (residual_blocker_register.csv)

- `rcept_no`, `rcept_dt`, `stock_code`, `event_category` — identity / context.
- `in_universe_status_table` — present in the 12,187-row universe status table.
- `body_format`, `parse_status`, `residual_class` — from the universe reconciliation.
- `is_correction`, `correction_action_class` — from the correction adjudication.
- `blocker_tags` (`|`-joined), `n_blocker_tags` — multi-label blocker tags.
- Fail-closed flags (always fixed): `manual_review_required=True`,
  `executable_or_safe=False`, `downstream_authoritative=False`,
  `parsed_clean_and_usable=False`, `strategy_ready=False`, `production_ready=False`.

## Membership

Register = (universe rows with parse_status in {no_label_match, label_no_value,
body_unavailable}) ∪ (all 166 correction rows). Cleanly-`extracted`
NON-correction universe rows are NOT blockers and are NOT in the register.
""", encoding="utf-8")


def write_input_manifest(path: Path) -> None:
    path.write_text(f"""# Prior-Phase Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0

## Inputs used (read-only)

- `{UNIV.relative_to(REPO)}`
  (12,187-row universe body status: body_format / parse_status / residual_class /
  manual_review_required / executable_or_safe).
- `{ADJ.relative_to(REPO)}`
  (166-row correction residual action ledger: residual_action_class).
- Context only: `{LINKS.relative_to(REPO)}` (full-universe correction links) and
  KR_STATUS_CORRECTION_LINKAGE_A0 (Pass-3 origin).

## No network. No parser invocation. No downloads / API / acquisition / body repair.

## New code

- `src/audit/measurement_a0/p_residual_blocker_register.py` (this phase; pure local
  consolidation of accepted CSV artifacts).
""", encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Residual Blocker Register)

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0

| hard lock | status |
|---|---|
| Existing local artifacts only; NO downloads / API / acquisition | PASS (reads prior CSVs only) |
| NO body repair / recovery | PASS |
| NO parser feature expansion (parser not invoked) | PASS |
| NO candidate search / body confirmation rerun | PASS |
| NO downstream wiring / C2 / C3 | PASS |
| NOT an event log / NOT all-event finalization | PASS |
| NOT an executable-status final table | PASS |
| NO strategy / performance / execution / backtest | PASS |
| Every register row fail-closed (manual_review_required=True) | PASS |
| executable_or_safe=False on all register rows | PASS |
| downstream_authoritative=False on all register rows | PASS |
| no_label_match / label_no_value NOT treated as parsed/safe | PASS |
| correction rows NOT treated as downstream-authoritative | PASS |
| 39 correction zip reconcile as subset of 42 universe zip | PASS (verified) |
| No row executable / safe / strategy-ready / production-ready | PASS |
| No rcept_dt as effective status date / no rcept_dt fallback | PASS |
| Source counts reconcile to accepted prior numbers | PASS (asserted) |
""", encoding="utf-8")


def _overlap_table(overlap_cell: Counter) -> list[str]:
    lines = ["| universe_parse_status | correction_action_or_not | count |",
             "|---|---|---:|"]
    for (ps_k, act_k), cnt in sorted(overlap_cell.items()):
        lines.append(f"| `{ps_k}` | `{act_k}` | {cnt} |")
    return lines


def write_summary(path: Path, n_reg: int, tag_counts: Counter,
                  overlap_cell: Counter, corr_zip: int) -> None:
    lines = [
        "# KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0 — Summary",
        "", "Date: 2026-05-26",
        "Opened by Referee directive REF-OPEN-004 (via relay).",
        "Consolidates residual blockers from the recently-closed measurement-layer phases.",
        "",
        f"## Unique register rows (keyed by rcept_no): **{n_reg}**",
        "",
        "Register = (universe rows: 42 zip_unparseable + 511 no_label_match + 200 "
        "label_no_value = 753) ∪ (166 correction rows). The 109 parser-`extracted` "
        "correction rows are added because corrections are manual_review_required "
        "regardless of parse outcome; the other 57 corrections (39 zip + 11 "
        "no_label_match + 7 label_no_value) already fall inside the 753.",
        f"  → {n_reg} = 753 + 109.",
        "",
        "## Blocker tag counts (multi-label; do NOT sum to register size)",
        "",
        "| blocker_tag | count |", "|---|---:|",
    ]
    for k, v in tag_counts.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        f"## Key overlap: 39 correction zip_unparseable ⊂ 42 universe zip_unparseable "
        f"(verified corr_zip={corr_zip}; 3 universe-zip are non-correction).",
        "",
        "## Overlap matrix (universe parse_status × correction action / not_correction)",
        "",
    ]
    lines += _overlap_table(overlap_cell)
    lines += [
        "",
        "## Fail-closed",
        "",
        "- Every register row: manual_review_required=True, executable_or_safe=False,",
        "  downstream_authoritative=False, parsed_clean_and_usable=False.",
        "- NOT an event log. NOT an executable-status table. NOT downstream wiring.",
        "- No downloads / API / body repair. No strategy / execution / production.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, n_reg: int, tag_counts: Counter, overlap_cell: Counter,
                 corr_zip: int, correction_overlap_rows: list[dict]) -> None:
    co_ct = Counter(r["universe_parse_status"] for r in correction_overlap_rows)
    lines = [
        "# KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0 — Report",
        "", "Date: 2026-05-26",
        "Phase opened by: Referee directive REF-OPEN-004 (via relay).",
        "Executor: Claude Code. Referee: Codex.",
        "",
        "## Phase name and scope",
        "",
        "Measurement-layer residual BLOCKER REGISTER (local artifact consolidation) "
        "only. suspension_related + resumption_related status rows. Existing local "
        "artifacts only. No downloads, no API, no body repair, no parser feature "
        "expansion, no candidate/body rerun, no downstream wiring, no C2/C3, no "
        "all-event event-log finalization, no executable-status final table, no "
        "strategy / performance / execution work.",
        "",
        "## Inputs used (paths)",
        "",
        f"- `{UNIV.relative_to(REPO)}` (12,187-row universe body status).",
        f"- `{ADJ.relative_to(REPO)}` (166-row correction residual actions).",
        "- Context: full-universe links + KR_STATUS_CORRECTION_LINKAGE_A0. See "
        "`prior_phase_input_manifest.md`.",
        "",
        "## Exact row counts from each source artifact",
        "",
        "| source artifact | rows | relevant counts |",
        "|---|---:|---|",
        "| universe_body_status_reconciled.csv | 12,187 | extracted 11,434 / "
        "no_label_match 511 / label_no_value 200 / body_unavailable(zip) 42 |",
        "| correction_residual_action_ledger.csv | 166 | 17/40/17/37/15/1/39 by action |",
        "",
        f"## Exact unique rows in the blocker register: **{n_reg}**",
        "",
        "Register key = **`rcept_no`** (combined single key; corrections are status "
        "rows, so `correction_rcept_no` == `rcept_no`; `is_correction` flags them). "
        "Membership = (universe non-extracted residuals: 42 + 511 + 200 = 753) ∪ "
        f"(166 correction rows) = 753 + 109 parser-extracted corrections = **{n_reg}**.",
        "",
        "## Exact count by blocker tag (multi-label)",
        "",
        "| blocker_tag | count |", "|---|---:|",
    ]
    for k, v in tag_counts.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Exact overlap counts",
        "",
        "| residual set | count | notes |",
        "|---|---:|---|",
        f"| universe zip_unparseable | 42 | tag `source_zip_unparseable` |",
        f"| └ correction zip_unparseable subset | {corr_zip} | ⊂ 42; "
        "3 universe-zip are non-correction |",
        f"| no_label_match | 511 | of which {co_ct.get('no_label_match', 0)} are corrections |",
        f"| label_no_value | 200 | of which {co_ct.get('label_no_value', 0)} are corrections |",
        f"| correction manual-review rows | 166 | all `correction_manual_review_required` |",
        f"| └ correction parser-extracted (clean body, still manual-review) | "
        f"{166 - corr_zip - co_ct.get('no_label_match', 0) - co_ct.get('label_no_value', 0)} | added to register |",
        "",
        "## Overlap matrix (universe parse_status × correction action / not_correction)",
        "",
    ]
    lines += _overlap_table(overlap_cell)
    lines += [
        "",
        "## Register key explanation",
        "",
        "The register is **row-level by `rcept_no`** (a single combined key). "
        "Corrections share the same key space; `is_correction=True` distinguishes "
        "them. A row may carry multiple blocker tags (e.g. a correction whose body "
        "is zip_unparseable carries `source_zip_unparseable` + "
        "`source_recovery_required_separate_approval` + "
        "`correction_manual_review_required` + `manual_review_required`).",
        "",
        "## This is NOT ...",
        "",
        "- NOT an event log / all-event finalization.",
        "- NOT an executable-status table.",
        "- NOT downstream wiring / C2 / C3.",
        "It is a local register that preserves residual-blocker + manual-review state.",
        "",
        "## Confirmations",
        "",
        "- All blockers are FAIL-CLOSED: every register row has "
        "manual_review_required=True, executable_or_safe=False, "
        "downstream_authoritative=False, parsed_clean_and_usable=False, "
        "strategy_ready=False, production_ready=False.",
        "- No downloads / API / body repair occurred (pure read of local CSVs).",
        "- No strategy, backtest, execution simulation, C2/C3, or "
        "production/paper/live/P08/shadow work occurred.",
        "- The 39 correction zip rows reconcile exactly as a subset of the 42 "
        "universe zip rows.",
        "",
        "## Defects / residuals (preserved, fail-closed)",
        "",
        "- 42 zip_unparseable (source defects; source recovery needs separate verdict "
        "+ download approval).",
        "- 511 no_label_match + 200 label_no_value (usable html_inline but "
        "non-extracted; manual review only).",
        "- 166 correction rows (all manual_review_required; non-authoritative).",
        "",
        "## Decision requested from Referee",
        "",
        "Executor does NOT self-close. Requesting a verdict among:",
        "- **A.** close as residual blocker register complete;",
        "- **B.** require another consolidation pass (refine tags / policy / packet);",
        "- **C.** open a separate residual-source-recovery for the 42 zip_unparseable "
        "rows (needs its own verdict + download approval);",
        "- **D.** keep all strategy / execution research closed (unchanged).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
