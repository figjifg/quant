"""KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0 — builder.

Referee directive REF-OPEN-003 (2026-05-26, via relay). Follows the now-closed
KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0.

Goal: package the 166 in-scope correction rows from the closed full-universe phase
into a precise residual-action ledger + manual-review packet, BEFORE any future
recovery / manual review / supersession discussion.

This phase READS existing local artifacts only. It does NOT:
- download or repair any body (zip_unparseable rows get a recovery-REQUIREMENTS
  ledger, NOT recovery),
- call any API or use credentials,
- re-run the parser / candidate search / body confirmation,
- expand parser features,
- wire supersession downstream,
- touch C2/C3 / strategy / performance / execution / production / paper / live /
  P08 / shadow.

It assigns each correction row exactly one local residual ACTION class, mapped back
to the accepted 5-tier confidence class (17/52/7/73/17). All rows remain
manual_review_required (correction parser output non-authoritative). No row is
promoted to executable / safe / strategy-ready / downstream-authoritative.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

MA0 = REPO / "reports/experiments/measurement_A0"
PRIOR = MA0 / "KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0"
OUT = MA0 / "KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0"

LINKS = PRIOR / "correction_full_universe_links.csv"
NOLINK_ROOT = PRIOR / "no_link_medium_low_root_cause_ledger.csv"

# Prior accepted 5-tier counts (reconciliation target).
PASS_PRIOR = {
    "high_validated": 17,
    "medium_needs_manual": 52,
    "low_needs_manual": 7,
    "no_link": 73,
    "rejected_wrong_candidate": 17,
    "total": 166,
}
FIVE_TIER = ("high_validated", "medium_needs_manual", "low_needs_manual",
             "no_link", "rejected_wrong_candidate")

# no_link root-cause → action class mapping
NO_LINK_ROOT_TO_ACTION = {
    "original_not_in_raw_pool": "no_link_original_not_found",
    "original_likely_outside_730d": "no_link_original_not_found",
    "original_requires_attachment_or_body_reference": "no_link_original_not_found",
    "original_likely_cross_category_not_allowed": "no_link_cross_category_blocked",
    "insufficient_evidence": "no_link_insufficient_evidence",
    "original_possible_but_title_too_generic": "no_link_insufficient_evidence",
    "corp_code_or_stock_code_missing": "no_link_insufficient_evidence",
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
    import csv as _csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = _csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def assign_action(row: dict, root_cause: str) -> tuple[str, str]:
    """Deterministic single residual-action class per correction row, priority-ordered.
    Returns (action_class, action_note)."""
    conf = row["confidence_5tier"]
    body_fmt = row["body_format_cache"]
    ev = row["evidence_state"]

    # Priority 1: corrupt cached body — dominant need is source recovery (cannot be
    # locally adjudicated without the body), regardless of tentative 5-tier.
    if body_fmt == "zip_unparseable":
        return ("zip_unparseable_requires_source_recovery",
                f"cached body corrupt; capped at {conf}; needs source recovery (separate verdict + download approval)")

    # Priority 2: body-confirmed validated link (design-only).
    if conf == "high_validated":
        return ("accepted_high_validated_design_only",
                "body confirms candidate title/date; design-only; still manual_review_required")

    # Priority 3: scored high but body cross-check failed — quarantined.
    if conf == "rejected_wrong_candidate":
        return ("rejected_wrong_candidate_quarantined",
                "html_inline body present but candidate not referenced; quarantined")

    # Priority 4: no_link — subdivide by accepted root cause.
    if conf == "no_link":
        return (NO_LINK_ROOT_TO_ACTION.get(root_cause, "no_link_insufficient_evidence"),
                f"root_cause={root_cause or 'unclassified'}")

    # Priority 5: medium / low (html_inline, not zip).
    if ev == "html_inline_body_confirms_candidate":
        return ("body_confirms_candidate_but_below_high",
                f"body references candidate but below high bar ({conf})")
    if conf == "low_needs_manual":
        return ("low_confidence_manual_only", "weak match; manual review only")
    return ("other_manual_review_required", f"{conf}; manual review required")


def main() -> None:
    print("[start] KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    links = pd.read_csv(LINKS, dtype=str).fillna("")
    root = pd.read_csv(NOLINK_ROOT, dtype=str).fillna("")
    n = len(links)
    print(f"[load] {n} correction rows from prior accepted artifact")
    assert n == 166, f"expected 166 correction rows, got {n}"

    root_by_rcept = dict(zip(root["correction_rcept_no"], root["root_cause"]))

    # Verify the 5-tier counts match the prior accepted state (control).
    conf_counts = Counter(links["confidence_5tier"])
    for k in FIVE_TIER:
        assert conf_counts.get(k, 0) == PASS_PRIOR[k], \
            f"5-tier mismatch {k}: {conf_counts.get(k, 0)} != {PASS_PRIOR[k]}"
    print(f"[control] 5-tier reproduces accepted {dict(conf_counts)}")

    action_ledger: list[dict] = []
    rejected_rows: list[dict] = []
    zip_rows: list[dict] = []
    no_link_med_low_rows: list[dict] = []
    packet_rows: list[dict] = []
    contrast_rows: list[dict] = []
    cross_tab: Counter = Counter()       # (5tier, action)
    action_counts: Counter = Counter()

    for r in links.to_dict(orient="records"):
        rcept = r["correction_rcept_no"]
        conf = r["confidence_5tier"]
        root_cause = root_by_rcept.get(rcept, "")
        action, note = assign_action(r, root_cause)
        action_counts[action] += 1
        cross_tab[(conf, action)] += 1

        base = {
            "correction_rcept_no": rcept,
            "correction_rcept_dt": r["correction_rcept_dt"],
            "corp_name": r["corp_name"],
            "stock_code": r["stock_code"],
            "event_category": r["event_category"],
            "correction_report_nm": r["correction_report_nm"],
            "confidence_5tier": conf,
            "evidence_state": r["evidence_state"],
            "body_format_cache": r["body_format_cache"],
            "blocked_overlay": r["blocked_overlay"],
            "residual_action_class": action,
            "residual_action_note": note,
            "root_cause": root_cause,
            "candidate_rcept_no": r["candidate_rcept_no"],
            "candidate_rcept_dt_iso": r["candidate_rcept_dt_iso"],
            "title_similarity": r["title_similarity"],
            "pass3_score": r["pass3_score"],
            "manual_review_required": True,      # hard lock — always True
            "downstream_authoritative": False,   # never
            "supersession_ready": r["supersession_ready"],
            "supersession_wired": False,         # design-only; never wired
        }
        action_ledger.append(base)

        # manual-review packet: every row a future human reviewer would need.
        packet_rows.append({
            "correction_rcept_no": rcept,
            "corp_name": r["corp_name"],
            "stock_code": r["stock_code"],
            "correction_report_nm": r["correction_report_nm"],
            "confidence_5tier": conf,
            "residual_action_class": action,
            "candidate_rcept_no": r["candidate_rcept_no"],
            "candidate_report_nm": r["candidate_report_nm"],
            "candidate_rcept_dt_iso": r["candidate_rcept_dt_iso"],
            "body_format_cache": r["body_format_cache"],
            "body_refs_candidate_title": r["body_refs_candidate_title"],
            "body_refs_candidate_date": r["body_refs_candidate_date"],
            "title_similarity": r["title_similarity"],
            "manual_review_required": True,
            "human_validation_claimed": False,   # this packet does NOT claim review done
            "authoritative": False,
            "review_question": _review_question(action),
        })

        if conf == "rejected_wrong_candidate":
            rejected_rows.append({
                "correction_rcept_no": rcept,
                "corp_name": r["corp_name"],
                "correction_report_nm": r["correction_report_nm"],
                "candidate_rcept_no": r["candidate_rcept_no"],
                "candidate_report_nm": r["candidate_report_nm"],
                "candidate_rcept_dt_iso": r["candidate_rcept_dt_iso"],
                "body_format_cache": r["body_format_cache"],
                "body_refs_candidate_title": r["body_refs_candidate_title"],
                "body_refs_candidate_date": r["body_refs_candidate_date"],
                "title_similarity": r["title_similarity"],
                "pass3_score": r["pass3_score"],
                "why_evidence_failed": (
                    "scoring matched a candidate (score "
                    f"{r['pass3_score']}, title_similarity {r['title_similarity']}) "
                    "but the html_inline correction body references NEITHER the "
                    "candidate's title token NOR its date — body cross-check failed; "
                    "kept quarantined, NOT a confirmed link"),
                "status": "quarantined_manual_review_required",
            })

        if r["body_format_cache"] == "zip_unparseable":
            zip_rows.append({
                "correction_rcept_no": rcept,
                "corp_name": r["corp_name"],
                "correction_report_nm": r["correction_report_nm"],
                "tentative_confidence_5tier": conf,
                "blocker": "cached document.xml ZIP is unparseable (BadZipFile/corrupt)",
                "local_adjudication_possible": False,
                "recovery_requirement": (
                    "re-acquire the OPENDART document.xml for this rcept_no "
                    "(document.json endpoint) and re-validate the body"),
                "recovery_performed": False,            # NOT performed this phase
                "needs_separate_verdict_and_download_approval": True,
                "overlaps_universe_zip_unparseable_residual": True,
            })

        if conf in ("no_link", "medium_needs_manual", "low_needs_manual"):
            no_link_med_low_rows.append({
                "correction_rcept_no": rcept,
                "corp_name": r["corp_name"],
                "event_category": r["event_category"],
                "confidence_5tier": conf,
                "body_format_cache": r["body_format_cache"],
                "root_cause": root_cause,
                "residual_action_class": action,
                "next_action": _next_action(action),
                "authoritative": False,
                "manual_review_required": True,
            })

        if conf == "high_validated":
            contrast_rows.append({
                "correction_rcept_no": rcept,
                "corp_name": r["corp_name"],
                "candidate_rcept_no": r["candidate_rcept_no"],
                "candidate_rcept_dt_iso": r["candidate_rcept_dt_iso"],
                "title_similarity": r["title_similarity"],
                "body_refs_candidate_title": r["body_refs_candidate_title"],
                "body_refs_candidate_date": r["body_refs_candidate_date"],
                "note": "design-only validated link; still manual_review_required; NOT wired",
            })

    assert sum(action_counts.values()) == 166, f"action sum {sum(action_counts.values())} != 166"

    # confidence_to_action_mapping cross-tab
    mapping_rows = []
    for (conf, action), cnt in sorted(cross_tab.items()):
        mapping_rows.append({
            "confidence_5tier": conf,
            "residual_action_class": action,
            "count": cnt,
        })

    # Write deliverables
    write_csv(OUT / "correction_residual_action_ledger.csv", action_ledger)
    write_csv(OUT / "rejected_wrong_candidate_adjudication.csv", rejected_rows)
    write_csv(OUT / "zip_unparseable_recovery_requirements.csv", zip_rows)
    write_csv(OUT / "no_link_medium_low_action_ledger.csv", no_link_med_low_rows)
    write_csv(OUT / "manual_review_packet.csv", packet_rows)
    write_csv(OUT / "confidence_to_action_mapping.csv", mapping_rows)
    # optional
    write_csv(OUT / "high_validated_contrast_examples.csv", contrast_rows)
    write_csv(OUT / "residual_action_counts.csv",
              [{"residual_action_class": k, "count": v} for k, v in action_counts.most_common()])

    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_input_manifest(OUT / "prior_phase_input_manifest.md")
    write_unresolved(OUT / "unresolved_questions.md", action_counts)
    write_summary(OUT / "residual_local_adjudication_summary.md",
                  conf_counts, action_counts, cross_tab)
    write_report(OUT / "report.md", conf_counts, action_counts, cross_tab)

    print(json.dumps({
        "in_scope": n,
        "five_tier": dict(conf_counts),
        "action_counts": dict(action_counts),
        "action_sum": sum(action_counts.values()),
        "rejected_detail_rows": len(rejected_rows),
        "zip_recovery_rows": len(zip_rows),
        "no_link_med_low_rows": len(no_link_med_low_rows),
    }, indent=2, default=str))


def _review_question(action: str) -> str:
    return {
        "accepted_high_validated_design_only":
            "Confirm the body-confirmed link is correct before any future use (design-only).",
        "zip_unparseable_requires_source_recovery":
            "Recover the corrupt body (separate verdict) before any linkage decision.",
        "rejected_wrong_candidate_quarantined":
            "Confirm the scored candidate is genuinely wrong (body does not reference it).",
        "no_link_original_not_found":
            "Is the original disclosure outside the local raw pool? May need source expansion.",
        "no_link_insufficient_evidence":
            "Candidate(s) too weak — does a correct original exist locally at all?",
        "no_link_cross_category_blocked":
            "Cross-category original suspected but blocked by policy — adjudicate manually.",
        "body_confirms_candidate_but_below_high":
            "Body references candidate but below high bar — confirm/upgrade manually.",
        "low_confidence_manual_only":
            "Weak match — confirm or discard manually.",
        "other_manual_review_required":
            "Manual review required — classify.",
    }.get(action, "Manual review required.")


def _next_action(action: str) -> str:
    return {
        "no_link_original_not_found": "candidate source expansion (separate verdict) OR accept as no local original",
        "no_link_insufficient_evidence": "manual search for a stronger original",
        "no_link_cross_category_blocked": "manual cross-category adjudication",
        "body_confirms_candidate_but_below_high": "manual confirm/upgrade",
        "low_confidence_manual_only": "manual confirm/discard",
        "other_manual_review_required": "manual classify",
        "zip_unparseable_requires_source_recovery": "source recovery (separate verdict + download approval)",
    }.get(action, "manual review")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Residual Local Adjudication)

Date: 2026-05-26
Phase: KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0

| hard lock | status |
|---|---|
| Existing local artifacts only; NO downloads / API / acquisition | PASS (reads prior CSVs only) |
| NO body repair / recovery (zip_unparseable gets requirements only) | PASS |
| NO parser feature expansion (parser not invoked) | PASS |
| NO candidate search / body confirmation re-run | PASS |
| NO downstream supersession wiring (design-only) | PASS |
| NO C2/C3 / execution / strategy / performance / backtest | PASS |
| Correction rows remain manual_review_required (166/166) | PASS |
| Correction parser output non-authoritative | PASS |
| medium / low / no_link / blocked NOT authoritative | PASS |
| rejected_wrong_candidate kept quarantined (not dropped) | PASS |
| high_validated remains design-only + manual_review_required | PASS |
| No rcept_dt as effective status date / no rcept_dt fallback | PASS |
| No executable / survivorship-safe / strategy-ready claim | PASS |
| No production / paper / P08 / live / shadow connection | PASS |
| All 166 rows reconcile exactly | PASS |
| Action-class counts sum to 166 | PASS |
| Every row has confidence class + action class + evidence state + manual-review | PASS |
""", encoding="utf-8")


def write_input_manifest(path: Path) -> None:
    path.write_text(f"""# Prior-Phase Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0

## Inputs used (read-only)

- `{LINKS.relative_to(REPO)}` — 166-row accepted full-universe links
  (confidence_5tier, evidence_state, body_format_cache, blocked_overlay, body
  cross-check flags, candidate fields, supersession_ready).
- `{NOLINK_ROOT.relative_to(REPO)}` — accepted no_link / medium / low root causes.
- Reconciliation baseline: KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0
  accepted counts 17 / 52 / 7 / 73 / 17 (total 166), 39 zip_unparseable.

## No inputs from outside the local repo. No network. No parser invocation.

## New code

- `src/audit/measurement_a0/p_correction_residual_local_adjudication.py`
  (this phase; pure local transformation of accepted CSV/MD artifacts).
""", encoding="utf-8")


def write_unresolved(path: Path, action_counts: Counter) -> None:
    path.write_text(f"""# Unresolved Questions (local, for later — NOT decisions)

Date: 2026-05-26
Phase: KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0

These are packaged questions for a FUTURE human/Referee decision. This phase does
NOT answer them and does NOT take any action on them.

1. The {action_counts.get('zip_unparseable_requires_source_recovery', 0)}
   zip_unparseable correction bodies: whether to open a separate
   residual-source-recovery phase (would need its own Referee verdict + download
   approval). NOT performed here.
2. The {action_counts.get('no_link_original_not_found', 0)} no_link_original_not_found
   rows: whether the original disclosure exists outside the local raw pool (would
   need candidate-source expansion, separate verdict).
3. The {action_counts.get('rejected_wrong_candidate_quarantined', 0)}
   rejected_wrong_candidate rows: kept quarantined; no further automated action.
4. Whether any high_validated design-only link should ever be wired downstream —
   currently forbidden; supersession remains design-only.
""", encoding="utf-8")


def _ct_table(cross_tab: Counter) -> list[str]:
    lines = ["| confidence_5tier | residual_action_class | count |", "|---|---|---:|"]
    for (conf, action), cnt in sorted(cross_tab.items()):
        lines.append(f"| `{conf}` | `{action}` | {cnt} |")
    return lines


def write_summary(path: Path, conf_counts: Counter, action_counts: Counter,
                  cross_tab: Counter) -> None:
    lines = [
        "# KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0 — Summary",
        "", "Date: 2026-05-26",
        "Opened by Referee directive REF-OPEN-003 (via relay).",
        "Predecessor: KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0 "
        "(commits e110165 + 041fcc7).",
        "",
        "## Purpose",
        "",
        "Package the 166 in-scope correction rows into a row-level residual-ACTION "
        "ledger + manual-review packet, mapped back to the accepted 5-tier "
        "confidence. Local only — NO downloads, NO body repair, NO recovery.",
        "",
        "## Accepted 5-tier confidence (control — matches prior exactly)",
        "",
        "| confidence | count |", "|---|---:|",
    ]
    for k in FIVE_TIER:
        lines.append(f"| `{k}` | {conf_counts.get(k, 0)} |")
    lines.append(f"| **total** | **{sum(conf_counts.values())}** |")
    lines += [
        "", "## Residual action classes (sum to 166)", "",
        "| residual_action_class | count |", "|---|---:|",
    ]
    for k, v in action_counts.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append(f"| **total** | **{sum(action_counts.values())}** |")
    lines += ["", "## Confidence → action mapping (cross-tab)", ""]
    lines += _ct_table(cross_tab)
    lines += [
        "", "## Hard locks", "",
        "- Local artifacts only; no downloads / API / body repair / parser expansion.",
        "- All 166 remain manual_review_required; none authoritative / executable /",
        "  strategy-ready. rejected quarantined; high_validated design-only.",
        "- Supersession NOT wired. No C2/C3 / execution / strategy / production.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, conf_counts: Counter, action_counts: Counter,
                 cross_tab: Counter) -> None:
    n_zip = action_counts.get("zip_unparseable_requires_source_recovery", 0)
    n_rej = action_counts.get("rejected_wrong_candidate_quarantined", 0)
    lines = [
        "# KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0 — Report",
        "", "Date: 2026-05-26",
        "Phase opened by: Referee directive REF-OPEN-003 (via relay).",
        "Executor: Claude Code. Referee: Codex.",
        "",
        "## Phase name and scope",
        "",
        "Measurement-layer residual ADJUDICATION PACKET only. suspension_related + "
        "resumption_related correction rows. Existing local artifacts only. No new "
        "downloads, no API, no body repair, no parser feature expansion, no "
        "downstream supersession wiring, no C2/C3, no strategy / performance / "
        "execution work. This is NOT residual-source recovery.",
        "",
        "## Inputs used (paths)",
        "",
        f"- `{LINKS.relative_to(REPO)}` (166-row accepted links).",
        f"- `{NOLINK_ROOT.relative_to(REPO)}` (accepted no_link/medium/low root causes).",
        "- See `prior_phase_input_manifest.md`.",
        "",
        f"## Exact total rows reconciled: **{sum(conf_counts.values())}**",
        "",
        "## Counts by accepted 5-tier confidence class",
        "",
        "| confidence | count |", "|---|---:|",
    ]
    for k in FIVE_TIER:
        lines.append(f"| `{k}` | {conf_counts.get(k, 0)} |")
    lines.append(f"| **total** | **{sum(conf_counts.values())}** |")
    lines += [
        "",
        "## Counts by residual action class (sum to 166)",
        "",
        "| residual_action_class | count |", "|---|---:|",
    ]
    for k, v in action_counts.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append(f"| **total** | **{sum(action_counts.values())}** |")
    lines += [
        "",
        "## Explicit reconciliation to 166 correction rows",
        "",
        f"- 5-tier sum = {sum(conf_counts.values())}; action-class sum = "
        f"{sum(action_counts.values())}. Both = 166.",
        "- Every row carries exactly one accepted 5-tier class AND exactly one "
        "residual action class (see cross-tab below + "
        "`correction_residual_action_ledger.csv`).",
        "",
        "## Explicit reconciliation to prior accepted counts (17 / 52 / 7 / 73 / 17)",
        "",
        "| confidence | this phase | prior accepted | match |",
        "|---|---:|---:|:--:|",
    ]
    for k in FIVE_TIER:
        cur = conf_counts.get(k, 0)
        lines.append(f"| `{k}` | {cur} | {PASS_PRIOR[k]} | {'✓' if cur == PASS_PRIOR[k] else '✗'} |")
    lines += [
        "",
        "## Confidence → residual-action mapping (cross-tab)",
        "",
        "Note the priority rule: a `zip_unparseable` cached body routes the row to "
        "`zip_unparseable_requires_source_recovery` regardless of its tentative "
        "5-tier (it cannot be locally adjudicated without the body). This is why the "
        f"{n_zip} zip rows are pulled out of their medium/low/no_link buckets.",
        "",
    ]
    lines += _ct_table(cross_tab)
    lines += [
        "",
        "## Confirmations (required by directive)",
        "",
        f"- The {n_zip} zip_unparseable rows were NOT downloaded or repaired — they "
        "receive a recovery-REQUIREMENTS ledger only "
        "(`zip_unparseable_recovery_requirements.csv`, recovery_performed=False).",
        f"- The {n_rej} rejected_wrong_candidate rows remain QUARANTINED "
        "(`rejected_wrong_candidate_adjudication.csv`); none silently dropped.",
        "- no_link / medium / low rows remain MANUAL-REVIEW-ONLY and NOT authoritative.",
        "- high_validated remains DESIGN-LEVEL ONLY and manual_review_required.",
        "- Supersession is NOT wired downstream (supersession_wired=False on all rows).",
        "- NO strategy, backtest, execution simulation, C2/C3, or "
        "production/paper/live/P08/shadow work occurred.",
        "",
        "## Defects / residuals",
        "",
        f"- {n_zip} zip_unparseable correction bodies (source defects; recovery "
        "requires a separate verdict + download approval; overlap the universe-level "
        "42 zip_unparseable residuals).",
        f"- {n_rej} rejected_wrong_candidate rows (scored but body-unconfirmed).",
        f"- {action_counts.get('no_link_original_not_found', 0)} no_link_original_not_found "
        f"+ {action_counts.get('no_link_insufficient_evidence', 0)} "
        f"no_link_insufficient_evidence "
        f"+ {action_counts.get('no_link_cross_category_blocked', 0)} "
        "no_link_cross_category_blocked.",
        "",
        "## Decision requested from Referee",
        "",
        "Executor does NOT self-close. Requesting a verdict among:",
        "- **A.** close as residual adjudication packet complete;",
        "- **B.** require another adjudication pass (refine action classes / packet);",
        f"- **C.** open a separate residual-source-recovery for the {n_zip} "
        "zip_unparseable correction bodies (needs its own verdict + download approval);",
        "- **D.** keep all strategy / execution research closed (unchanged).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
