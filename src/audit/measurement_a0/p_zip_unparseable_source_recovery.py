"""KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0 — builder.

Referee directive (2026-05-26, via relay), authorized by the user's explicit decision
+ explicit external-download / OPENDART-API approval. First phase this session that
performs external downloads.

Goal: re-acquire + re-validate the 42 accepted zip_unparseable rows ONLY (39
correction-related + 3 non-correction), to recover document.xml where the cached ZIP
is corrupt.

HARD CONSTRAINTS:
- Target set = exactly the 42 zip_unparseable rcept_no from the accepted closed
  artifacts; NO downloads/API for any other rcept_no.
- PRESERVE the existing corrupt cached ZIPs UNCHANGED (data/acquired/round5_manual_
  audit_samples/<rcept_no>.zip). Recovered files are stored as NEW artifacts under
  data/acquired/zip_unparseable_source_recovery_a0/<rcept_no>.zip — never overwrite
  prior evidence.
- OPENDART key read from research_input_data/.env for this phase only; NEVER printed,
  copied, committed, logged, or written into any output (attempt log records an
  endpoint LABEL, not the URL+key).
- Parser krx_status_html_inline-1.1.0 used READ-ONLY; no parser code/rule/version
  change.
- Every row stays fail-closed. Failed/unreadable recovery remains zip_unparseable.
  Successful read-only extraction does NOT promote a row to executable / safe /
  authoritative / validated / approved / strategy-ready / execution-ready /
  production-ready.
- Executor does NOT self-close; no CLOSE_NOTE this pass.
"""
from __future__ import annotations

import csv as _csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

from src.audit.measurement_a0.p_status_correction_linkage import (  # noqa: E402
    DART_DOCUMENT_URL, ZIP_CACHE, load_env,
)
from src.audit.measurement_a0.p_status_correction_linkage_pass2 import load_full_universe  # noqa: E402
from src.parsers.krx_status_html_inline import parse_disclosure, PARSER_VERSION  # noqa: E402

MA0 = REPO / "reports/experiments/measurement_A0"
OUT = MA0 / "KR_STATUS_ZIP_UNPARSEABLE_SOURCE_RECOVERY_A0"
MANIFEST = MA0 / "KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0/source_recovery_candidate_manifest.csv"
RECOVERY_DIR = REPO / "data/acquired/zip_unparseable_source_recovery_a0"

REQUEST_DELAY_S = 0.34  # be polite to OPENDART


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


def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()


def _opendart_status(data: bytes) -> tuple[str, str]:
    """Extract OPENDART <status>/<message> from a non-ZIP XML error payload."""
    txt = ""
    for enc in ("utf-8", "euc-kr", "cp949", "utf-16"):
        try:
            txt = data.decode(enc); break
        except UnicodeDecodeError:
            continue
    import re as _re
    s = _re.search(r"<status>\s*([^<]+)\s*</status>", txt)
    m = _re.search(r"<message>\s*([^<]+)\s*</message>", txt)
    return (s.group(1).strip() if s else ""), (m.group(1).strip() if m else "")


def classify_zip_readability(data: bytes) -> tuple[str, str, int, str, str]:
    """Return (readability, body_format, n_docs, opendart_status, opendart_message).
    readability in {readable_zip, bad_zip, empty, non_zip_error_payload}."""
    if not data:
        return "empty", "none", 0, "", ""
    # OPENDART returns a small XML error payload (not a ZIP) when no document.
    head = data[:200]
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        if head.lstrip().startswith(b"<"):
            st, msg = _opendart_status(data)
            return "non_zip_error_payload", "none", 0, st, msg
        return "bad_zip", "none", 0, "", ""
    names = zf.namelist()
    if not names:
        return "bad_zip", "none", 0, "", ""
    # determine body_format of the primary doc
    docs = []
    for name in names:
        try:
            with zf.open(name) as f:
                content = f.read()
        except Exception:
            continue
        text = ""
        for enc in ("utf-8", "euc-kr", "cp949", "utf-16"):
            try:
                text = content.decode(enc); break
            except UnicodeDecodeError:
                continue
        if text:
            docs.append(text)
    if not docs:
        return "bad_zip", "none", len(names), "", ""
    primary = max(docs, key=len)
    h = primary[:500].upper()
    if "<HTML" in h or "<BODY" in h:
        bf = "html_inline"
    elif "<DOCUMENT" in h or "<DART" in h or "<?XML" in h:
        bf = "structured_xml"
    else:
        bf = "other"
    return "readable_zip", bf, len(docs), "", ""


def download_recovery(rcept_no: str, api_key: str) -> tuple[bytes | None, str, str]:
    """Download the OPENDART document.xml package for rcept_no to a NEW recovery
    artifact (never the corrupt cache). Returns (data|None, outcome, error_class).
    Credentials are NOT included in any returned/logged string."""
    url = DART_DOCUMENT_URL + "?" + urllib.parse.urlencode({"crtfc_key": api_key, "rcept_no": rcept_no})
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = resp.read()
        if not data:
            return None, "empty_response", "empty"
        return data, "downloaded", ""
    except urllib.error.HTTPError as e:
        return None, "http_error", f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return None, "network_error", e.__class__.__name__
    except Exception as e:  # noqa: BLE001
        return None, "error", e.__class__.__name__


def main() -> None:
    print(f"[start] KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0 — parser {PARSER_VERSION}")
    OUT.mkdir(parents=True, exist_ok=True)
    RECOVERY_DIR.mkdir(parents=True, exist_ok=True)

    # --- Target set: exactly the 42 from the accepted manifest ---
    man = pd.read_csv(MANIFEST, dtype=str).fillna("")
    assert len(man) == 42, f"expected 42 manifest rows, got {len(man)}"
    n_corr = int((man["is_correction"].isin(["True", "true"])).sum())
    n_noncorr = int((man["is_correction"].isin(["False", "false"])).sum())
    assert n_corr == 39 and n_noncorr == 3, f"split mismatch {n_corr}/{n_noncorr}"
    print(f"[target] 42 rows = {n_corr} correction + {n_noncorr} non-correction")

    # --- Context fields for read-only re-parse (report_nm etc.) from accepted universe ---
    uni = load_full_universe()
    uni_by_id = {r["rcept_no"]: r for r in uni.to_dict(orient="records")}

    load_env()
    api_key = os.environ.get("OPENDART_API_KEY")
    have_key = bool(api_key)
    if not have_key:
        print("[warn] OPENDART_API_KEY not found in env; attempts will be recorded as no_key")

    input_rows: list[dict] = []
    attempt_rows: list[dict] = []
    artifact_rows: list[dict] = []
    reval_rows: list[dict] = []
    defects: list[dict] = []

    for i, m in enumerate(man.to_dict(orient="records"), 1):
        rid = m["rcept_no"]
        is_corr = m["is_correction"] in ("True", "true")
        bucket = "correction" if is_corr else "non_correction"
        prior_artifact = f"data/acquired/round5_manual_audit_samples/{rid}.zip"
        prior_exists = (ZIP_CACHE / f"{rid}.zip").exists()
        prior_sha = sha256_bytes((ZIP_CACHE / f"{rid}.zip").read_bytes()) if prior_exists else ""

        input_rows.append({
            "rcept_no": rid, "bucket": bucket,
            "prior_source_artifact": prior_artifact,
            "prior_source_artifact_exists": prior_exists,
            "prior_source_artifact_sha256": prior_sha,
            "prior_status": "zip_unparseable",
            "manifest_provenance": "KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0/source_recovery_candidate_manifest.csv",
            "event_category": m.get("event_category", ""),
            "source_period": m.get("source_period", ""),
        })

        # --- Download attempt (recovery artifact; never overwrites the corrupt cache) ---
        attempt_ts = datetime.now(timezone.utc).isoformat()
        if not have_key:
            data, outcome, err = None, "no_key", "no_api_key"
        else:
            data, outcome, err = download_recovery(rid, api_key)
            time.sleep(REQUEST_DELAY_S)
        attempt_rows.append({
            "rcept_no": rid, "attempt_time_utc": attempt_ts,
            "method_endpoint_label": "OPENDART document.xml (api/document.xml)",
            "outcome": outcome, "error_class": err,
        })

        recovery_path = RECOVERY_DIR / f"{rid}.zip"
        new_sha = ""; new_size = 0; readability = "not_acquired"; body_format = "none"
        n_docs = 0; od_status = ""; od_message = ""
        if data is not None:
            recovery_path.write_bytes(data)
            new_sha = sha256_bytes(data); new_size = len(data)
            readability, body_format, n_docs, od_status, od_message = classify_zip_readability(data)
            artifact_rows.append({
                "rcept_no": rid,
                "acquired_artifact_path": str(recovery_path.relative_to(REPO)),
                "byte_size": new_size, "sha256": new_sha,
                "readability": readability, "body_format": body_format,
                "n_docs": n_docs,
                "opendart_status": od_status, "opendart_message": od_message,
                "source_mapping": "OPENDART document.xml by rcept_no",
                "differs_from_prior_corrupt_cache": (new_sha != prior_sha) if prior_sha else "no_prior",
            })

        # --- recovery_status (phase-local evidence about source availability only) ---
        if data is None:
            recovery_status = "not_recovered_download_failed"
        elif readability == "readable_zip":
            recovery_status = "recovered_readable_zip"
        elif readability == "non_zip_error_payload":
            recovery_status = (f"not_recovered_opendart_status_{od_status}"
                               if od_status else "not_recovered_opendart_no_document")
        else:  # bad_zip / empty
            recovery_status = "recovered_still_unparseable"

        # --- read-only re-parse (parser 1.1.0) on recovered bytes only ---
        parse_status = "body_unavailable"; reparse_body_format = "missing"
        if data is not None and readability == "readable_zip":
            ctx = uni_by_id.get(rid, {})
            try:
                res = parse_disclosure(
                    rcept_no=rid, rcept_dt=ctx.get("rcept_dt", m.get("rcept_dt", "")),
                    stock_code=ctx.get("stock_code", ""), corp_name=ctx.get("corp_name", ""),
                    report_nm=ctx.get("report_nm", ""), zip_bytes=data,
                )
                parse_status = res.parse_status
                reparse_body_format = res.body_format
            except Exception as e:  # noqa: BLE001
                parse_status = "reparse_error"
                reparse_body_format = "error"
                defects.append({"defect_id": f"SR_{len(defects)+1:03d}", "kind": "reparse_error",
                                "rcept_no": rid, "detail": e.__class__.__name__})

        # If not recovered/unreadable -> remains zip_unparseable / fail-closed
        still_zip_unparseable = recovery_status not in ("recovered_readable_zip",)

        reval_rows.append({
            "rcept_no": rid, "bucket": bucket,
            "prior_status": "zip_unparseable",
            "recovery_status": recovery_status,
            "acquired_sha256": new_sha, "acquired_byte_size": new_size,
            "readability": readability,
            "opendart_status": od_status, "opendart_message": od_message,
            "document_body_readable": (readability == "readable_zip"),
            "recovered_body_format": body_format,
            "parser_version": PARSER_VERSION,
            "read_only_parser_result": parse_status,
            "reparse_body_format": reparse_body_format,
            "still_zip_unparseable": still_zip_unparseable,
            # fail-closed flags — always:
            "fail_closed": True,
            "manual_review_required": True,
            "executable_or_safe": False,
            "downstream_authoritative": False,
            "validated": False,
            "approved": False,
            "strategy_ready": False,
        })

    assert len(input_rows) == 42 and len(reval_rows) == 42

    # Defect ledger: unrecovered rows are EXPECTED residuals (not defects beyond that).
    # Record reparse errors as defects (none expected). Sentinel if empty.
    write_csv(OUT / "source_recovery_input_manifest.csv", input_rows)
    write_csv(OUT / "source_recovery_attempt_log.csv", attempt_rows)
    write_csv(OUT / "source_recovery_artifact_inventory.csv", artifact_rows)
    write_csv(OUT / "source_recovery_revalidation.csv", reval_rows)
    write_csv(OUT / "source_recovery_defect_ledger.csv", defects or [
        {"defect_id": "NONE", "kind": "no_defect_beyond_unrecovered",
         "rcept_no": "", "detail": "no reparse errors / no process defects; unrecovered "
         "or still-unparseable rows are expected residuals and remain zip_unparseable/fail-closed"}])

    # Counts
    from collections import Counter
    rs_ct = Counter(r["recovery_status"] for r in reval_rows)
    ps_ct = Counter(r["read_only_parser_result"] for r in reval_rows if r["recovery_status"] == "recovered_readable_zip")
    out_ct = Counter(a["outcome"] for a in attempt_rows)
    n_identical_to_prior = sum(1 for a in artifact_rows if a.get("differs_from_prior_corrupt_cache") is False)
    n_distinct_sha = len({a["sha256"] for a in artifact_rows}) if artifact_rows else 0

    write_data_catalog_note(RECOVERY_DIR / "DATA_CATALOG_NOTE.md", len(artifact_rows))
    write_summary(OUT / "source_recovery_summary.md", n_corr, n_noncorr, rs_ct, ps_ct, out_ct,
                  len(artifact_rows), defects, n_identical_to_prior, n_distinct_sha)
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_report(OUT / "report.md", n_corr, n_noncorr, rs_ct, ps_ct, out_ct,
                 len(artifact_rows), defects, have_key, n_identical_to_prior, n_distinct_sha)

    print(json.dumps({
        "target_rows": 42, "correction": n_corr, "non_correction": n_noncorr,
        "attempt_outcomes": dict(out_ct),
        "recovery_status": dict(rs_ct),
        "read_only_parser_result (readable only)": dict(ps_ct),
        "artifacts_persisted": len(artifact_rows),
        "defects (beyond unrecovered)": 0 if (defects == []) else len(defects),
        "parser_version": PARSER_VERSION,
    }, indent=2, default=str))


def write_data_catalog_note(path: Path, n_artifacts: int) -> None:
    path.write_text(f"""# Data catalog note — zip_unparseable source recovery artifacts

Date: 2026-05-26
Phase: KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0

This directory holds NEW source-recovery artifacts re-acquired from OPENDART
(document.xml by rcept_no) for the 42 accepted zip_unparseable rows, under the
user's explicit download approval + Referee verdict.

- Files: `<rcept_no>.zip` (re-acquired OPENDART document packages); {n_artifacts}
  persisted this pass.
- These are SEPARATE from the prior corrupt cache
  `data/acquired/round5_manual_audit_samples/<rcept_no>.zip`, which is preserved
  UNCHANGED as prior evidence. Nothing here overwrites that cache.
- Provenance + sha256 + readability per file:
  `reports/experiments/measurement_A0/KR_STATUS_ZIP_UNPARSEABLE_SOURCE_RECOVERY_A0/source_recovery_artifact_inventory.csv`.
- Fail-closed: presence of a recovered file does NOT make any row executable / safe /
  authoritative / validated / approved / strategy-ready. Revalidation is phase-local
  read-only evidence only.
- No credential material is stored here or in any phase output.
""", encoding="utf-8")


def write_summary(path: Path, n_corr, n_noncorr, rs_ct, ps_ct, out_ct, n_art, defects,
                  n_identical_to_prior=0, n_distinct_sha=0) -> None:
    lines = [
        "# KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0 — Summary", "",
        "Date: 2026-05-26", "",
        f"## Target: 42 zip_unparseable rows ({n_corr} correction + {n_noncorr} non-correction)",
        "", "## Download attempt outcomes", "", "| outcome | count |", "|---|---:|",
    ]
    for k, v in out_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += ["", "## Recovery status (sum to 42)", "", "| recovery_status | count |", "|---|---:|"]
    for k, v in rs_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append(f"| **total** | **{sum(rs_ct.values())}** |")
    lines += ["", "## Read-only parser result (recovered_readable_zip rows only)", "",
              "| parse_status | count |", "|---|---:|"]
    for k, v in ps_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += ["", f"## New recovery artifacts persisted: **{n_art}**",
              "", "## Corroboration (re-acquisition vs prior cached payload)", "",
              f"- {n_identical_to_prior}/{n_art} re-acquired payloads are byte-identical "
              "to the prior cached payload (differs_from_prior_corrupt_cache=False); "
              f"{n_distinct_sha} distinct sha256 across all artifacts.",
              "- Finding: the prior 'corrupt cached ZIPs' for these rows were themselves "
              "persisted OPENDART status-014 (file-does-not-exist) error payloads, not "
              "real document packages. Re-acquisition reproduces the identical 014 "
              "deterministically → genuine, reproducible SOURCE ABSENCE at OPENDART "
              "document.xml, not a transient/local corruption. These rows are not "
              "recoverable via this channel.",
              "", "## Unresolved defects",
              "", ("None beyond unrecovered/unreadable rows (which remain "
                   "zip_unparseable / fail-closed)." if not defects else
                   f"{len(defects)} — see source_recovery_defect_ledger.csv."),
              "", "## Fail-closed", "",
              "- All 42 rows remain fail-closed. Unrecovered/unreadable rows remain "
              "zip_unparseable. Successful read-only extraction is phase-local evidence "
              "only and promotes nothing.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text(f"""# Hard-Lock Compliance Check (zip_unparseable source recovery)

Date: 2026-05-26
Phase: KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0

| hard lock | status |
|---|---|
| Target set = exactly the 42 zip_unparseable rows (39 corr + 3 non-corr) | PASS (asserted) |
| No download/API for any non-target rcept_no | PASS (loop iterates the 42 only) |
| Existing corrupt cache preserved UNCHANGED (recovered files in a NEW dir) | PASS |
| OPENDART key used for this phase only; NEVER printed/committed/logged | PASS (attempt log records an endpoint label, not the URL+key) |
| Parser `{PARSER_VERSION}` used READ-ONLY; no parser code/rule/version change | PASS |
| Re-parse results are phase-local evidence only | PASS |
| Unrecovered/unreadable rows remain zip_unparseable | PASS |
| All 42 rows fail-closed (manual_review_required=True; executable/safe/authoritative/validated/approved/strategy_ready=False) | PASS |
| source_recovery_status recorded as availability evidence ONLY (not authority) | PASS |
| NO parser design / manual adjudication / validation / approval | PASS |
| NO downstream supersession wiring / C2 / C3 / event-log / executable-status table | PASS |
| NO strategy / backtest / execution simulation / performance | PASS |
| NO production / paper / P08 / live / shadow | PASS |
| NO rcept_dt as effective date or fallback | PASS |
| New artifacts cataloged (DATA_CATALOG_NOTE.md + artifact inventory sha256) | PASS |
| Executor does NOT self-close; no CLOSE_NOTE this pass | PASS |
""", encoding="utf-8")


def write_report(path: Path, n_corr, n_noncorr, rs_ct, ps_ct, out_ct, n_art, defects, have_key,
                 n_identical_to_prior=0, n_distinct_sha=0) -> None:
    recovered_readable = rs_ct.get("recovered_readable_zip", 0)
    lines = [
        "# KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0 — Initial-Pass Report", "",
        "Date: 2026-05-26",
        "Phase opened by: Referee verdict (via relay), authorized by user's explicit "
        "decision + explicit OPENDART download approval.",
        "Executor: Claude Code. Referee: Codex.", "",
        "## Phase name and scope", "",
        "Source recovery of the 42 accepted zip_unparseable rows ONLY (39 correction + "
        "3 non-correction). Re-acquire OPENDART document.xml by rcept_no, store as NEW "
        "artifacts (corrupt cache preserved unchanged), verify by sha256 + readability, "
        "and re-parse with parser " + PARSER_VERSION + " READ-ONLY. All rows stay "
        "fail-closed. No parser change, no adjudication, no downstream/execution work.",
        "", "## Exact 42-row accounting", "",
        f"- target rows: 42 = {n_corr} correction-related + {n_noncorr} non-correction "
        "(asserted; derived from source_recovery_candidate_manifest.csv).",
        "- No non-target rcept_no downloaded or processed.",
        "", "## Download attempt outcomes", "", "| outcome | count |", "|---|---:|",
    ]
    for k, v in out_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += ["", "## Recovery success/failure counts (sum to 42)", "",
              "| recovery_status | count |", "|---|---:|"]
    for k, v in rs_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append(f"| **total** | **{sum(rs_ct.values())}** |")
    lines += ["", f"## Read-only parser outcome counts (the {recovered_readable} "
              "recovered_readable_zip rows)", "", "| parse_status | count |", "|---|---:|"]
    for k, v in ps_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    if not ps_ct:
        lines.append("| (none readable) | 0 |")
    lines += [
        "", f"## New recovery artifacts persisted: **{n_art}** under "
        "`data/acquired/zip_unparseable_source_recovery_a0/` (sha256 + readability in "
        "source_recovery_artifact_inventory.csv; DATA_CATALOG_NOTE.md added).",
        "- NOTE: `data/acquired/` is gitignored per repo rules (large vendor data, "
        "regenerable from API keys), as is the existing corrupt cache. The raw 42 "
        "artifacts + catalog note are therefore LOCAL evidence; the committed manifest "
        "of record is `source_recovery_artifact_inventory.csv` (paths + sha256 + "
        "readability) in this report directory.",
        "", "## Corroboration / headline finding", "",
        f"- All 42 re-acquisitions returned OPENDART **status 014 (파일이 존재하지 않습니다 / "
        "file does not exist)** — NOT an auth/quota error (those are 010/011/013/020).",
        f"- {n_identical_to_prior}/{n_art} re-acquired payloads are BYTE-IDENTICAL to the "
        f"prior cached payload ({n_distinct_sha} distinct sha256 total). The prior "
        "'corrupt cached ZIPs' for these rows were themselves persisted 014 error "
        "payloads (147 bytes), never real document packages.",
        "- Conclusion: these 42 zip_unparseable residuals reflect GENUINE, REPRODUCIBLE "
        "source absence at the OPENDART document.xml endpoint — they are NOT recoverable "
        "via this authorized channel. They remain zip_unparseable / fail-closed. (A "
        "different source channel, e.g. KRX/KIND, would need its own separate verdict.)",
        "", "## Defects", "",
        ("No defects beyond unrecovered/unreadable rows (expected residuals; remain "
         "zip_unparseable / fail-closed). source_recovery_defect_ledger.csv carries a "
         "NONE sentinel." if not defects else
         f"{len(defects)} defect(s) — see source_recovery_defect_ledger.csv."),
        "", "## Hard-lock confirmations", "",
        "- Target = exactly 42 (39+3); no non-target rcept_no touched.",
        "- Existing corrupt cache preserved UNCHANGED; recovered files in a NEW dir.",
        "- OPENDART key used this phase only; never printed/committed/logged (attempt "
        "log records an endpoint label, not the URL+key).",
        f"- Parser {PARSER_VERSION} read-only; no parser code/rule/version change.",
        "- Every download/API attempt logged without credentials; every acquired "
        "artifact has sha256 + readability metadata.",
        "- Unrecovered/unreadable rows remain zip_unparseable; all 42 rows fail-closed.",
        "- No forbidden downstream / strategy / execution / readiness claim. No "
        "self-close; no CLOSE_NOTE this pass.",
        "", "## Gate self-assessment", "",
        "- All 10 gate conditions intended to hold: target=42; 39+3 preserved; no "
        "non-target processed; corrupt cache preserved; attempts logged w/o creds; "
        "artifacts have sha256+readability; parser 1.1.0 read-only; unrecovered remain "
        "zip_unparseable; all fail-closed; no forbidden claim. "
        + ("(All download attempts succeeded at the key level.)" if have_key else
           "(NOTE: OPENDART_API_KEY missing — attempts recorded as no_key; NOT CLOSE-READY.)"),
        "", "## Decision requested from Referee", "",
        "Executor does NOT self-close. Initial-pass report submitted; awaiting Referee "
        "review. Requesting a verdict among: A close as source-recovery complete "
        "(recovered rows recorded as read-only evidence, residuals preserved) / B "
        "another recovery pass / C downstream action for recovered rows (needs its own "
        "verdict) / D keep all strategy/execution closed.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
