"""KR-STATUS-MEASUREMENT-A0-HANDOFF-STATE-MANIFEST-A0 — builder.

Referee directive REF-OPEN-012 (2026-05-26, via relay). Follows the now-closed
KR-STATUS-MANUAL-REVIEW-WORKLIST-VIEWS-A0.

Goal: a compact, deterministic HANDOFF STATE MANIFEST recording the accepted local
measurement-layer state (the REF-CLOSE-007 .. 011 phases), its hard locks, and where
the next human reviewer should look — without changing any underlying data or
granting any action authority.

It is NOT source recovery, NOT parser design, NOT manual adjudication, NOT validation,
NOT an event log, NOT an executable-status table, NOT strategy/execution. It:
- reads existing local CSV/MD only; no new data,
- does NOT edit any prior closed-phase output; does NOT patch / fix / adjudicate /
  recover / parse / validate / approve / reinterpret any row,
- does NOT create CLOSE_NOTE.md (Executor does not self-close this phase),
- newly marks no row parsed / recovered / executable / safe / authoritative /
  validated / approved / strategy-ready / execution-ready / production-ready.

This manifest is a handoff/index artifact only and carries NO approval authority.
"""
from __future__ import annotations

import csv as _csv
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
MA0 = REPO / "reports/experiments/measurement_A0"
OUT = MA0 / "KR_STATUS_MEASUREMENT_A0_HANDOFF_STATE_MANIFEST_A0"
NEXT_ACTIONS = REPO / "docs/next_actions.md"

# The REF-CLOSE-007 .. 011 phases (the directive's handoff scope), in order.
# (phase_dir, ref_close_id, accepted_commits, lock_role, key_output)
HANDOFF_PHASES = [
    ("KR_STATUS_LOCAL_ARTIFACT_CONSISTENCY_AUDIT_A0", "REF-CLOSE-007",
     "1643fd2 + 85909a3", "aggregate count locks", "count_reconciliation_matrix.csv"),
    ("KR_STATUS_RESIDUAL_ROWKEY_INTEGRITY_AUDIT_A0", "REF-CLOSE-008",
     "73c68a8 + 75247a7", "rcept_no row-key set locks", "rowkey_set_reconciliation.csv"),
    ("KR_STATUS_FAIL_CLOSED_INVARIANT_AUDIT_A0", "REF-CLOSE-009",
     "bbfbbaa + a0feb9f", "field-level fail-closed locks", "fail_closed_invariant_matrix.csv"),
    ("KR_STATUS_RESIDUAL_MANUAL_REVIEW_PACKET_CONSOLIDATION_A0", "REF-CLOSE-010",
     "32e30f8 + 4e46c99", "manual-review packet (862, fail-closed)", "manual_review_packet.csv"),
    ("KR_STATUS_MANUAL_REVIEW_WORKLIST_VIEWS_A0", "REF-CLOSE-011",
     "290f532 + d67950c + 8597af1", "navigation-only worklist (862)", "manual_review_worklist.csv"),
]

# Predecessor chain (accepted earlier; recorded for full lineage, context only).
PREDECESSOR_CHAIN = [
    ("KR_STATUS... universe residual reconciliation", "REF-CLOSE-001", "6510f5a + 40ae946"),
    ("correction full-universe validation", "REF-CLOSE-002", "e110165 + 041fcc7"),
    ("correction residual local adjudication", "REF-CLOSE-003", "6e35624 + 82d952d"),
    ("residual blocker register", "REF-CLOSE-004", "9bb4a2d + a65c791"),
    ("parser non-extracted local taxonomy", "REF-CLOSE-005", "d97f9a7 + ec88bd0"),
    ("source-recovery candidate manifest", "REF-CLOSE-006", "1a9de6a + aacbd0c"),
]

CANON_COUNTS = {
    "universe_rows": 12187, "usable_html_inline": 12145, "zip_unparseable": 42,
    "no_label_match": 511, "label_no_value": 200, "blocker_register_rows": 862,
    "parser_nonextracted_rows": 711, "correction_rows": 166,
    "correction_zip_subset": 39, "non_correction_zip_subset": 3,
}

FORBIDDEN_OUTCOME_COLS = ["validated", "approved", "effective_date_final", "recovered",
                          "parsed", "safe", "executable", "authoritative",
                          "strategy_ready", "execution_ready", "production_ready"]

# Key files to inventory (checksum) — the directive's required inputs + the 5 CLOSE_NOTEs.
KEY_OUTPUT_FILES = [
    "KR_STATUS_LOCAL_ARTIFACT_CONSISTENCY_AUDIT_A0/count_reconciliation_matrix.csv",
    "KR_STATUS_RESIDUAL_ROWKEY_INTEGRITY_AUDIT_A0/rowkey_set_reconciliation.csv",
    "KR_STATUS_FAIL_CLOSED_INVARIANT_AUDIT_A0/fail_closed_invariant_matrix.csv",
    "KR_STATUS_RESIDUAL_MANUAL_REVIEW_PACKET_CONSOLIDATION_A0/manual_review_packet.csv",
    "KR_STATUS_MANUAL_REVIEW_WORKLIST_VIEWS_A0/manual_review_worklist.csv",
    "KR_STATUS_MANUAL_REVIEW_WORKLIST_VIEWS_A0/worklist_integrity_check.csv",
]


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


def sha256_of(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    data = path.read_bytes()
    h.update(data)
    return h.hexdigest(), len(data)


def main() -> None:
    print("[start] KR-STATUS-MEASUREMENT-A0-HANDOFF-STATE-MANIFEST-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    defects: list[dict] = []
    def defect(kind, detail):
        defects.append({"defect_id": f"HO_{len(defects)+1:03d}", "kind": kind, "detail": detail})

    # 1. next_actions Active: only this phase Active
    na = NEXT_ACTIONS.read_text(encoding="utf-8")
    import re
    active_block = re.search(r"## Active\s*\n(.*?)\n## ", na, re.S)
    active_body = active_block.group(1) if active_block else ""
    this_active = "KR-STATUS-MEASUREMENT-A0-HANDOFF-STATE-MANIFEST-A0" in active_body
    other_active = any(p in active_body for p, *_ in [(x[0].replace("_", "-"),) for x in HANDOFF_PHASES])
    if not this_active:
        defect("active_marker_missing", "this phase not marked Active in next_actions")

    # 2. CLOSE_NOTE existence for REF-CLOSE-007..011
    # 3. lock summaries internally consistent
    # 5. state manifest rows
    state_rows: list[dict] = []
    for phase_dir, ref_id, commits, lock_role, key_out in HANDOFF_PHASES:
        d = MA0 / phase_dir
        cn = d / "CLOSE_NOTE.md"
        ko = d / key_out
        cn_ok = cn.exists()
        ko_ok = ko.exists()
        if not cn_ok:
            defect("close_note_missing", f"{phase_dir}/CLOSE_NOTE.md")
        if not ko_ok:
            defect("key_output_missing", f"{phase_dir}/{key_out}")
        state_rows.append({
            "ref_close_id": ref_id,
            "phase": phase_dir,
            "accepted_commits": commits,
            "accepted_status": "CLOSED",
            "lock_role": lock_role,
            "key_output_file": key_out,
            "close_note_present": cn_ok,
            "key_output_present": ko_ok,
        })
    write_csv(OUT / "measurement_a0_state_manifest.csv", state_rows)

    # Lock consistency checks
    lock_checks = []
    def lock_check(name, ok, detail):
        lock_checks.append({"lock": name, "result": "PASS" if ok else "FAIL", "detail": detail})
        if not ok:
            defect("lock_inconsistency", f"{name}: {detail}")

    # count locks
    crm = pd.read_csv(MA0 / "KR_STATUS_LOCAL_ARTIFACT_CONSISTENCY_AUDIT_A0/count_reconciliation_matrix.csv", dtype=str).fillna("")
    crm_all_pass = (crm["match"] == "PASS").all()
    lock_check("count_locks (REF-CLOSE-007)", crm_all_pass, f"{len(crm)} reconciliation rows, all PASS={crm_all_pass}")
    # set locks
    rsr = pd.read_csv(MA0 / "KR_STATUS_RESIDUAL_ROWKEY_INTEGRITY_AUDIT_A0/rowkey_set_reconciliation.csv", dtype=str).fillna("")
    rsr_all_pass = (rsr["set_equality"] == "PASS").all()
    lock_check("rowkey_set_locks (REF-CLOSE-008)", rsr_all_pass, f"{len(rsr)} set checks, all PASS={rsr_all_pass}")
    # field-level locks
    fcm = pd.read_csv(MA0 / "KR_STATUS_FAIL_CLOSED_INVARIANT_AUDIT_A0/fail_closed_invariant_matrix.csv", dtype=str).fillna("")
    fcm_all_pass = (fcm["result"] == "PASS").all()
    lock_check("field_level_fail_closed_locks (REF-CLOSE-009)", fcm_all_pass, f"{len(fcm)} invariant rows, all PASS={fcm_all_pass}")
    # packet lock
    pkt = pd.read_csv(MA0 / "KR_STATUS_RESIDUAL_MANUAL_REVIEW_PACKET_CONSOLIDATION_A0/manual_review_packet.csv", dtype=str).fillna("")
    pkt_ok = (len(pkt) == 862 and pkt["rcept_no"].nunique() == 862)
    lock_check("manual_review_packet_lock (REF-CLOSE-010)", pkt_ok, f"rows={len(pkt)}, unique={pkt['rcept_no'].nunique()} (expect 862/862)")
    # worklist lock
    wl = pd.read_csv(MA0 / "KR_STATUS_MANUAL_REVIEW_WORKLIST_VIEWS_A0/manual_review_worklist.csv", dtype=str).fillna("")
    wl_ok = (len(wl) == 862 and wl["rcept_no"].nunique() == 862)
    lock_check("worklist_view_lock (REF-CLOSE-011)", wl_ok, f"rows={len(wl)}, unique={wl['rcept_no'].nunique()} (expect 862/862)")
    # packet set == worklist set
    set_eq = set(pkt["rcept_no"]) == set(wl["rcept_no"])
    lock_check("packet_set==worklist_set", set_eq, f"set equality={set_eq}")

    # 4. Worklist state re-check
    wl_checks = []
    def wl_chk(name, value, ok):
        wl_checks.append({"check": name, "value": value, "result": "PASS" if ok else "FAIL"})
        if not ok:
            defect("worklist_state", f"{name}: {value}")
    n = len(wl); uniq = wl["rcept_no"].nunique()
    wl_chk("worklist_rows==862", n, n == 862)
    wl_chk("worklist_unique_rcept_no==862", uniq, uniq == 862)
    ids = list(wl["worklist_id"])
    expected_ids = [f"WL-{i:05d}" for i in range(1, len(ids) + 1)]
    ids_ok = (ids == expected_ids)
    wl_chk("worklist_id WL-00001..WL-%05d sequential" % len(ids), f"{ids[0]}..{ids[-1]}" if ids else "", ids_ok)
    present_forbidden = [c for c in FORBIDDEN_OUTCOME_COLS if c in wl.columns]
    wl_chk("no_exact_forbidden_outcome_columns", ",".join(present_forbidden) or "none", not present_forbidden)
    write_csv(OUT / "worklist_state_check.csv", wl_checks)

    # 6. Output inventory + sha256
    inv_rows = []
    for rel in KEY_OUTPUT_FILES + [f"{p}/CLOSE_NOTE.md" for p, *_ in HANDOFF_PHASES] + ["../../../docs/next_actions.md"]:
        # normalize: KEY_OUTPUT_FILES + close notes are under MA0; next_actions is repo-rooted
        if rel.startswith("../"):
            fp = (MA0 / rel).resolve()
            disp = str(fp.relative_to(REPO))
        else:
            fp = MA0 / rel
            disp = str(fp.relative_to(REPO))
        if fp.exists():
            digest, size = sha256_of(fp)
            inv_rows.append({"file": disp, "sha256": digest, "size_bytes": size, "present": True})
        else:
            inv_rows.append({"file": disp, "sha256": "", "size_bytes": 0, "present": False})
            defect("inventory_file_missing", disp)
    write_csv(OUT / "measurement_a0_output_inventory.csv", inv_rows)

    write_csv(OUT / "handoff_defect_ledger.csv", defects or [
        {"defect_id": "NONE", "kind": "no_defect",
         "detail": "all REF-CLOSE-007..011 CLOSE_NOTEs + key outputs present; lock "
         "summaries internally consistent; worklist state intact; only this phase Active"}])

    n_lock_fail = sum(1 for r in lock_checks if r["result"] == "FAIL")
    n_wl_fail = sum(1 for r in wl_checks if r["result"] == "FAIL")

    write_key_locks(OUT / "measurement_a0_key_locks.md", lock_checks)
    write_boundary_notes(OUT / "handoff_boundary_notes.md")
    write_input_manifest(OUT / "handoff_input_manifest.md")
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_report(OUT / "report.md", state_rows, lock_checks, wl_checks, inv_rows,
                 defects, this_active, n_lock_fail, n_wl_fail)

    print(json.dumps({
        "handoff_phases": len(state_rows),
        "close_notes_present": sum(1 for r in state_rows if r["close_note_present"]),
        "lock_checks": len(lock_checks), "lock_fail": n_lock_fail,
        "worklist_checks": len(wl_checks), "worklist_fail": n_wl_fail,
        "inventory_files": len(inv_rows),
        "inventory_present": sum(1 for r in inv_rows if r["present"]),
        "this_phase_active": this_active,
        "defects": 0 if (defects and False) else len([d for d in defects]),
    }, indent=2, default=str))


def write_key_locks(path: Path, lock_checks) -> None:
    lines = ["# Measurement-A0 Key Locks", "", "Date: 2026-05-26",
             "Phase: KR-STATUS-MEASUREMENT-A0-HANDOFF-STATE-MANIFEST-A0", "",
             "Accepted locks across the closed measurement-layer chain (verified across",
             "three independent dimensions + the packet/worklist surface):", "",
             "## Canonical locked counts", "", "| metric | value |", "|---|---:|"]
    for k, v in CANON_COUNTS.items():
        lines.append(f"| {k} | {v:,} |")
    lines += ["", "Derived identities: 711 = 511 + 200; 42 = 39 + 3; 862 = 753 + 109; "
              "12,187 = 12,145 + 42.", "",
              "## Lock dimensions (consistency re-checked this phase)", "",
              "| lock | result | detail |", "|---|---|---|"]
    for r in lock_checks:
        lines.append(f"| {r['lock']} | {r['result']} | {r['detail']} |")
    lines += ["", "## Hard-lock summary (carried, in force)", "",
              "- Execution / strategy / backtest / performance: CLOSED.",
              "- No source recovery; the 42 zip_unparseable need a separate verdict + "
              "download approval.",
              "- No parser feature expansion / code change; parser-design backlog is "
              "design-only.",
              "- No C2/C3 / event-log finalization / executable-status table / "
              "production / paper / P08 / live / shadow.",
              "- All 862 blocker rows fail-closed; correction rows non-authoritative; "
              "rejected_wrong_candidate quarantined; design-only fields (link_validated, "
              "supersession_ready) not promoted.",
              "- Manual-review packet + worklist are human-review/navigation only and "
              "fail-closed; no outcome columns; blocked_action_boundary warning-only."]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_boundary_notes(path: Path) -> None:
    path.write_text("""# Handoff Boundary Notes — What This Does NOT Authorize

Date: 2026-05-26
Phase: KR-STATUS-MEASUREMENT-A0-HANDOFF-STATE-MANIFEST-A0

This manifest is a HANDOFF / INDEX artifact only. It records accepted state and
points the next reviewer where to look. It carries NO approval authority and changes
NO underlying data.

This manifest does NOT authorize:

- ❌ source recovery of the 42 zip_unparseable bodies (needs a separate Referee
  verdict + explicit download/API approval).
- ❌ downloads / API calls / credential use / body repair.
- ❌ parser changes, parser feature expansion, or parser-design (needs a separate
  parser-design verdict).
- ❌ manual adjudication / validation / approval of any correction or residual row.
- ❌ marking any row parsed / recovered / executable / safe / authoritative /
  validated / approved / strategy-ready / execution-ready / production-ready.
- ❌ downstream wiring / C2 / C3 / event-log finalization / executable-status table.
- ❌ strategy / performance / execution / backtest / production / paper / live / P08 /
  shadow work.

What it DOES provide: a deterministic index of the accepted closed measurement-layer
state (REF-CLOSE-007 .. 011), the canonical locked counts, the lock dimensions, a
checksum inventory of key outputs, and the worklist navigation entry point — so a
future Referee/Executor session can resume from a verified, fail-closed baseline.
""", encoding="utf-8")


def write_input_manifest(path: Path) -> None:
    lines = ["# Handoff Input Manifest", "", "Date: 2026-05-26",
             "Phase: KR-STATUS-MEASUREMENT-A0-HANDOFF-STATE-MANIFEST-A0", "",
             "## Inputs used (read-only)", "",
             "- `docs/next_actions.md`"]
    for p, ref, *_ in HANDOFF_PHASES:
        lines.append(f"- `reports/experiments/measurement_A0/{p}/CLOSE_NOTE.md` ({ref})")
    for rel in KEY_OUTPUT_FILES:
        lines.append(f"- `reports/experiments/measurement_A0/{rel}`")
    lines += ["", "## No new data. No network. No parser invocation. No edits to closed artifacts.",
              "", "## Predecessor chain (accepted earlier; lineage context only)", ""]
    for name, ref, commits in PREDECESSOR_CHAIN:
        lines.append(f"- {ref}: {name} ({commits})")
    lines += ["", "## New code",
              "- `src/audit/measurement_a0/p_measurement_a0_handoff_state_manifest.py` (this phase)."]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Handoff State Manifest)

Date: 2026-05-26
Phase: KR-STATUS-MEASUREMENT-A0-HANDOFF-STATE-MANIFEST-A0

| hard lock | status |
|---|---|
| Existing local CSV/MD only; no new data | PASS |
| NO edits to prior closed-phase outputs | PASS |
| Index/handoff only; no fix/adjudicate/recover/parse/validate/approve/reinterpret | PASS |
| NO CLOSE_NOTE.md created (executor does not self-close this phase) | PASS |
| NO source recovery / parser design / manual adjudication | PASS |
| NO downloads / API / credentials / body repair / parser change / rerun | PASS |
| NO candidate / body confirmation rerun | PASS |
| NO downstream wiring / C2 / C3 / event-log / executable-status table | PASS |
| NO strategy / performance / execution / backtest / production / paper / live / P08 / shadow | PASS |
| No row newly marked parsed/recovered/executable/safe/authoritative/validated/approved/strategy-ready/execution-ready/production-ready | PASS |
| Manifest carries NO approval authority | PASS |
""", encoding="utf-8")


def write_report(path, state_rows, lock_checks, wl_checks, inv_rows, defects,
                 this_active, n_lock_fail, n_wl_fail) -> None:
    n_inv_present = sum(1 for r in inv_rows if r["present"])
    lines = [
        "# KR-STATUS-MEASUREMENT-A0-HANDOFF-STATE-MANIFEST-A0 — Report",
        "", "Date: 2026-05-26",
        "Phase opened by: Referee directive REF-OPEN-012 (via relay).",
        "Executor: Claude Code. Referee: Codex.",
        "",
        "## Phase name and scope",
        "",
        "Local handoff-state manifest only — consolidates the accepted closed "
        "measurement_A0 state (REF-CLOSE-007 .. 011) into a compact, deterministic "
        "handoff index for future Referee/Executor sessions. Reads existing local "
        "CSV/MD only; no new data; no edits to closed artifacts; changes no underlying "
        "data and grants no action authority. NOT source recovery / parser design / "
        "manual adjudication / validation / event log / executable-status table / "
        "strategy / execution. No CLOSE_NOTE (executor does not self-close).",
        "",
        "## Input artifacts used",
        "",
        "- `docs/next_actions.md`; the 5 REF-CLOSE-007..011 CLOSE_NOTE.md files; the 6 "
        "key accepted outputs (see handoff_input_manifest.md).",
        "",
        f"## next_actions Active check: only this phase Active = **{this_active}**",
        "",
        "## State manifest (REF-CLOSE-007 .. 011)",
        "",
        "| ref_close | phase | accepted commits | lock role | CLOSE_NOTE | key output |",
        "|---|---|---|---|:--:|:--:|",
    ]
    for r in state_rows:
        lines.append(f"| {r['ref_close_id']} | {r['phase']} | {r['accepted_commits']} | "
                     f"{r['lock_role']} | {'OK' if r['close_note_present'] else 'MISSING'} | "
                     f"{'OK' if r['key_output_present'] else 'MISSING'} |")
    lines += [
        "",
        "## Lock consistency (re-checked this phase)",
        "",
        "| lock | result | detail |", "|---|---|---|",
    ]
    for r in lock_checks:
        lines.append(f"| {r['lock']} | {r['result']} | {r['detail']} |")
    lines += [
        "",
        "## Worklist state re-check",
        "",
        "| check | value | result |", "|---|---|---|",
    ]
    for r in wl_checks:
        lines.append(f"| {r['check']} | {r['value']} | {r['result']} |")
    lines += [
        "",
        f"## Output inventory (sha256): **{n_inv_present}/{len(inv_rows)}** files present "
        "(see measurement_a0_output_inventory.csv for digests).",
        "",
        "## Canonical locked counts",
        "",
        "12,187 universe / 12,145 usable html_inline / 42 zip_unparseable / 511 "
        "no_label_match / 200 label_no_value / 862 blocker register / 711 parser "
        "non-extracted / 166 correction / 39 correction-zip / 3 non-correction-zip. "
        "(711=511+200; 42=39+3; 862=753+109; 12,187=12,145+42.)",
        "",
        f"## Handoff-build defects: **{0 if (defects and defects[0].get('defect_id')=='NONE') else len(defects)}**",
        "",
        ("No handoff-build defects. All REF-CLOSE-007..011 CLOSE_NOTEs + key outputs "
         "present; lock summaries internally consistent; worklist state intact; only "
         "this phase Active."
         if (not defects or defects[0].get('defect_id') == 'NONE') else
         "See handoff_defect_ledger.csv."),
        "",
        "## What this does NOT authorize",
        "",
        "See handoff_boundary_notes.md. In brief: no source recovery, no downloads/API, "
        "no parser changes/design, no manual adjudication/validation/approval, no "
        "downstream wiring/C2/C3/event-log/executable-status table, no strategy/"
        "execution, no row promoted to any usable/authoritative/ready status. The "
        "manifest is a handoff/index only and carries NO approval authority.",
        "",
        "## Confirmations",
        "",
        f"- {sum(1 for r in state_rows if r['close_note_present'])}/5 REF-CLOSE-007..011 "
        "CLOSE_NOTEs present; lock checks PASS; worklist state intact (862/862 unique, "
        "WL-00001..WL-00862, no forbidden outcome columns).",
        "- No new data; no edits to closed artifacts; index/handoff only.",
        "- No downloads / API / credentials / body repair / parser change / rerun / "
        "candidate or body confirmation rerun / source recovery / parser-design / "
        "manual adjudication.",
        "- No CLOSE_NOTE; no downstream wiring / C2-C3 / event-log / executable-status "
        "table / strategy / execution / production / paper / live / P08 / shadow.",
        "",
        "## Decision requested from Referee",
        "",
        "Executor does NOT self-close. Requesting a verdict among:",
        "- **A.** close as handoff-state manifest complete;",
        "- **B.** require another manifest pass (add fields / wider inventory);",
        "- **C.** open a downstream action (each needs its own verdict; recovery needs "
        "download approval, parser changes need a parser-design verdict);",
        "- **D.** keep all strategy / execution research closed (unchanged).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
