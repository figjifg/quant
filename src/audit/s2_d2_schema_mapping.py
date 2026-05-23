"""S2 D2 schema mapping — Referee Round 4.1 D2 verdict.

Mandatory D2 additions (Referee 2nd verdict):
- Missing / under-sampled form sample acquisition (treasury_cancel, additional_listing,
  lockup_release, major_shareholder_sale, correction/withdrawal/cancellation, KOSDAQ)
- Actual DART form name mapping including 정정 / 자회사 / 회차 variants
- XML schema mapping per form (section/table path, field labels, units, dates,
  amounts, shares, effective date, correction refs)
- Tiny-response / attachment-only / PDF-only fallback classification (6 flags)
- Correction / cancellation / withdrawal linkage design

D2 outputs (8 required files per Referee):
1. d2_form_inventory_expanded.md
2. d2_actual_form_taxonomy_mapping.md
3. d2_xml_schema_mapping_by_form.md
4. d2_missing_event_type_samples.md
5. d2_tiny_response_attachment_fallback.md
6. d2_correction_cancellation_linkage_design.md
7. d2_parser_wave_readiness.md
8. d2_failure_modes_register.md

Hard locks: no parser implementation, no strategy testing, no return outcome.
"""
from __future__ import annotations

import io
import json
import os
import random
import re
import sys
import time
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path("/home/jin/code/quant")
ENV_PATH = REPO_ROOT / "research_input_data" / ".env"
PARQUET_PATH = (
    REPO_ROOT
    / "research_input_data"
    / "inputs"
    / "events"
    / "opendart_kospi_disclosures_20180101_20260505.parquet"
)
D1_RAW_DIR = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d1" / "raw_xml"
D1_SAMPLES_CSV = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d1" / "samples_50.csv"
D2_DIR = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d2"
D2_RAW_DIR = D2_DIR / "raw_xml"
REPORT_DIR = REPO_ROOT / "reports" / "experiments" / "S2_phase_d2_schema_mapping"

ENDPOINT_DOCUMENT = "https://opendart.fss.or.kr/api/document.xml"
ENDPOINT_LIST = "https://opendart.fss.or.kr/api/list.json"

# Referee-required taxonomy + D2 expanded form keyword mapping (R000 actual forms)
EXPANDED_FORM_MAP = {
    "treasury_acquire": ["자기주식취득결정"],
    "treasury_dispose": ["자기주식처분결정"],
    "treasury_cancel": ["주식소각결정"],
    "treasury_acquire_result": ["자기주식취득결과보고서"],
    "treasury_dispose_result": ["자기주식처분결과보고서"],
    "treasury_trust_create": ["자기주식취득신탁계약체결결정"],
    "treasury_trust_terminate": ["자기주식취득신탁계약해지결정"],
    "cb_issue": ["전환사채권발행결정"],
    "bw_issue": ["신주인수권부사채권발행결정"],
    "conversion_request": ["전환청구권행사"],
    "rights_issue": ["유상증자결정"],
    "bonus_issue": ["무상증자결정"],
    "capital_reduction": ["감자결정"],
    "merger_split": ["회사합병결정", "회사분할결정", "회사분할합병결정"],
    "additional_listing": ["추가상장"],
    "lockup_release": ["보호예수", "의무보유"],
    "major_shareholder_sale": ["임원ㆍ주요주주특정증권등소유상황보고서", "임원ㆍ주요주주특정증권등거래계획"],
    "correction_withdrawal_cancel": ["철회신고서", "취소공시"],
}

CORE_TAXONOMY = [
    "treasury_acquire",
    "treasury_dispose",
    "treasury_cancel",
    "cb_issue",
    "bw_issue",
    "conversion_request",
    "rights_issue",
    "bonus_issue",
    "capital_reduction",
    "merger_split",
    "additional_listing",
    "lockup_release",
    "major_shareholder_sale",
    "correction_withdrawal_cancel",
]

CORRECTION_PREFIXES = ["[기재정정]", "[첨부정정]", "[첨부추가]", "[연장결정]"]
SUBSIDIARY_SUFFIXES = ["(자회사의 주요경영사항)", "(종속회사의주요경영사항)"]
SERIES_PATTERN = re.compile(r"\(제\d+회차\)")

SAMPLES_PER_NEW_TYPE = 5
KOSDAQ_LIST_SAMPLES = 20
RANDOM_SEED = 20260523
REQUEST_TIMEOUT = 30
SLEEP_BETWEEN_REQUESTS = 0.3
MAX_RETRY = 3
TINY_RESPONSE_THRESHOLD = 500


def load_env(path: Path) -> None:
    raw = path.read_bytes()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    text = raw.decode("utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def strip_correction_prefix(report_nm: str) -> tuple[str, str | None]:
    if not report_nm:
        return "", None
    for p in CORRECTION_PREFIXES:
        if report_nm.startswith(p):
            return report_nm[len(p):], p
    return report_nm, None


def strip_subsidiary_suffix(report_nm: str) -> tuple[str, str | None]:
    for s in SUBSIDIARY_SUFFIXES:
        if s in report_nm:
            return report_nm.replace(s, "").strip(), s
    return report_nm, None


def normalize_form(report_nm: str) -> dict:
    base, corr = strip_correction_prefix(report_nm)
    base2, subs = strip_subsidiary_suffix(base)
    series_match = SERIES_PATTERN.search(base2)
    series = series_match.group(0) if series_match else None
    base_final = SERIES_PATTERN.sub("", base2).strip()
    return {
        "raw": report_nm,
        "correction_prefix": corr,
        "subsidiary_suffix": subs,
        "series_marker": series,
        "base_form": base_final,
    }


def select_d2_kospi_samples(parquet_path: Path) -> pd.DataFrame:
    df = pd.read_parquet(parquet_path)
    rng = random.Random(RANDOM_SEED)
    rows = []
    new_types = [
        "treasury_cancel",
        "treasury_acquire_result",
        "treasury_dispose_result",
        "treasury_trust_create",
        "treasury_trust_terminate",
        "additional_listing",
        "lockup_release",
        "major_shareholder_sale",
        "correction_withdrawal_cancel",
    ]
    for tag in new_types:
        kws = EXPANDED_FORM_MAP[tag]
        mask = df["report_nm"].apply(lambda x: any(kw in (x or "") for kw in kws))
        sub = df[mask].copy()
        sub["expected_event_type"] = tag
        if len(sub) == 0:
            print(f"  WARN: {tag} = 0 candidates in R000 KOSPI")
            continue
        n = min(SAMPLES_PER_NEW_TYPE, len(sub))
        idx = rng.sample(range(len(sub)), n)
        rows.append(sub.iloc[idx])
    out = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    if len(out) > 0:
        out = out[
            [
                "rcept_no",
                "rcept_date",
                "corp_code",
                "stock_code",
                "corp_name",
                "report_nm",
                "expected_event_type",
            ]
        ]
    return out


def acquire_kosdaq_samples(api_key: str) -> pd.DataFrame:
    rows = []
    for bgn, end in [("20230101", "20230131"), ("20240601", "20240630"), ("20250901", "20250930")]:
        params = {
            "crtfc_key": api_key,
            "corp_cls": "K",
            "bgn_de": bgn,
            "end_de": end,
            "page_no": 1,
            "page_count": 100,
        }
        try:
            r = requests.get(ENDPOINT_LIST, params=params, timeout=REQUEST_TIMEOUT)
            data = r.json() if r.status_code == 200 else {}
            if data.get("status") == "000":
                rows.extend(data.get("list", []))
            else:
                print(f"  KOSDAQ list {bgn}-{end} status={data.get('status')} msg={data.get('message','')[:80]}")
        except Exception as exc:
            print(f"  KOSDAQ list {bgn}-{end} exception: {type(exc).__name__}")
        time.sleep(SLEEP_BETWEEN_REQUESTS)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df.rename(columns={"rcept_no": "rcept_no", "rcept_dt": "rcept_date", "corp_code": "corp_code"}, inplace=True)
    if len(df) > KOSDAQ_LIST_SAMPLES:
        df = df.sample(n=KOSDAQ_LIST_SAMPLES, random_state=RANDOM_SEED).reset_index(drop=True)
    df["expected_event_type"] = "kosdaq_general"
    keep = ["rcept_no", "rcept_date", "corp_code", "stock_code", "corp_name", "report_nm", "expected_event_type"]
    for col in keep:
        if col not in df.columns:
            df[col] = None
    return df[keep]


def download_one(rcept_no: str, api_key: str, target_dir: Path) -> dict:
    result = {
        "rcept_no": rcept_no,
        "attempt": 0,
        "http_status": None,
        "ok": False,
        "bytes": 0,
        "content_type": None,
        "elapsed_ms": None,
        "error": None,
        "tiny_response_flag": False,
        "attachment_only_flag": False,
        "pdf_only_flag": False,
        "not_parseable_body": False,
    }
    for attempt in range(1, MAX_RETRY + 1):
        result["attempt"] = attempt
        start = time.time()
        try:
            r = requests.get(
                ENDPOINT_DOCUMENT,
                params={"crtfc_key": api_key, "rcept_no": rcept_no},
                timeout=REQUEST_TIMEOUT,
            )
            result["http_status"] = r.status_code
            result["bytes"] = len(r.content)
            result["content_type"] = r.headers.get("Content-Type", "")
            result["elapsed_ms"] = int((time.time() - start) * 1000)
            if r.status_code == 200 and len(r.content) > TINY_RESPONSE_THRESHOLD:
                target_zip = target_dir / f"{rcept_no}.zip"
                target_zip.write_bytes(r.content)
                try:
                    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
                        for name in zf.namelist():
                            data = zf.read(name)
                            (target_dir / f"{rcept_no}.xml").write_bytes(data)
                            break
                    result["ok"] = True
                    return result
                except zipfile.BadZipFile:
                    result["error"] = "BadZipFile"
                    result["not_parseable_body"] = True
            elif r.status_code == 200 and len(r.content) <= TINY_RESPONSE_THRESHOLD:
                result["error"] = "tiny_response"
                result["tiny_response_flag"] = True
                result["attachment_only_flag"] = True
            else:
                result["error"] = f"http_{r.status_code}"
        except requests.RequestException as exc:
            result["error"] = f"req_exception_{type(exc).__name__}"
        time.sleep(min(2 ** attempt, 8))
    return result


def analyze_xml_schema(xml_bytes: bytes) -> dict:
    text = xml_bytes.decode("utf-8", errors="replace")
    out: dict[str, object] = {
        "size_bytes": len(xml_bytes),
        "has_document": "<DOCUMENT" in text or "<document" in text.lower(),
        "section_count": text.count("<SECTION"),
        "table_count": text.count("<TABLE"),
        "th_count": text.count("<TH"),
        "td_count": text.count("<TD"),
    }
    title_match = re.search(r"<TITLE[^>]*>(.*?)</TITLE>", text, re.DOTALL)
    out["title"] = title_match.group(1).strip()[:200] if title_match else None
    th_labels = re.findall(r"<TH[^>]*>([^<]{1,80})</TH>", text)
    out["distinct_th_labels"] = sorted(set(s.strip() for s in th_labels if s.strip()))[:40]
    date_fields = [s for s in out["distinct_th_labels"] if any(k in s for k in ["일", "날짜"])]
    amount_fields = [s for s in out["distinct_th_labels"] if any(k in s for k in ["금액", "원", "단가", "총액"])]
    share_fields = [s for s in out["distinct_th_labels"] if any(k in s for k in ["주식수", "주식 수", "수량", "보통주", "우선주", "발행"])]
    effective_fields = [s for s in out["distinct_th_labels"] if any(k in s for k in ["효력", "발효", "기준", "결정일", "주총"])]
    out["candidate_date_fields"] = date_fields
    out["candidate_amount_fields"] = amount_fields
    out["candidate_share_fields"] = share_fields
    out["candidate_effective_date_fields"] = effective_fields
    correction_refs = re.findall(r"(원본\s*보고서|정정\s*보고서|원\s*공시|이전\s*공시).{0,100}", text)
    out["correction_reference_hints"] = correction_refs[:5]
    return out


def write_reports(
    d1_samples: pd.DataFrame,
    d1_xml_files: dict[str, Path],
    d2_samples: pd.DataFrame,
    d2_dl_results: list[dict],
    schema_per_form: dict[str, dict],
    failure_register: list[dict],
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    all_samples = pd.concat([d1_samples.assign(phase="D1"), d2_samples.assign(phase="D2")], ignore_index=True)
    all_samples.to_csv(D2_DIR / "all_samples_d1_d2.csv", index=False)

    # 1. d2_form_inventory_expanded.md
    inv = all_samples.groupby(["expected_event_type", "report_nm"]).size().reset_index(name="count")
    inv = inv.sort_values(["expected_event_type", "count"], ascending=[True, False])
    (REPORT_DIR / "d2_form_inventory_expanded.md").write_text(
        f"""# D2 Form Inventory Expanded

Date: 2026-05-23
Scope: D1 (45 samples) + D2 (additional samples) combined inventory.

## Coverage by taxonomy

| Event type | D1 count | D2 count | Total |
|---|---|---|---|
""" + "\n".join(
            f"| {t} | {int((d1_samples['expected_event_type']==t).sum() if 'expected_event_type' in d1_samples.columns else 0)} "
            f"| {int((d2_samples['expected_event_type']==t).sum() if len(d2_samples) else 0)} "
            f"| {int((all_samples['expected_event_type']==t).sum())} |"
            for t in CORE_TAXONOMY + (["kosdaq_general"] if (d2_samples.get('expected_event_type','').eq('kosdaq_general').any() if len(d2_samples) else False) else [])
        ) + f"""

## Full inventory (form-level)

```
{inv.to_string(index=False)}
```

## Notes

- D1 expected keyword for treasury_cancel was `자기주식취득결정` series, but R000 KOSPI shows the actual form is `주식소각결정` (697 disclosures). D2 corrects the mapping.
- KOSPI R000 has 0 disclosures with `corp_cls=K`; KOSDAQ coverage is acquired separately via OPENDART list API in D2.
- `[기재정정]`, `[첨부정정]`, `[첨부추가]`, `[연장결정]` prefixes appear naturally across multiple base forms — handled via prefix-strip normalizer in D3.
""",
        encoding="utf-8",
    )

    # 2. d2_actual_form_taxonomy_mapping.md
    mapping_rows = []
    for tag in CORE_TAXONOMY:
        kws = EXPANDED_FORM_MAP[tag]
        actual = all_samples.loc[all_samples["expected_event_type"] == tag, "report_nm"].drop_duplicates().tolist()
        n = int((all_samples["expected_event_type"] == tag).sum())
        d1_count = int((d1_samples["expected_event_type"] == tag).sum() if "expected_event_type" in d1_samples.columns else 0) if len(d1_samples) else 0
        d2_count = int((d2_samples["expected_event_type"] == tag).sum() if "expected_event_type" in d2_samples.columns else 0) if len(d2_samples) else 0
        coverage = "covered" if n > 0 else "source-unavailable"
        mapping_rows.append(
            {"event_type": tag, "expected_keywords": kws, "actual_forms_sampled": actual, "n_total": n, "n_d1": d1_count, "n_d2": d2_count, "coverage_status": coverage}
        )

    lines = ["# D2 Actual Form Taxonomy Mapping\n", "Maps Referee 14-event-type taxonomy → actual DART report_nm forms observed in samples.\n"]
    lines.append("| Event type | Expected keywords | Actual forms (sample-observed) | N(total) | N(D1) | N(D2) | Coverage |")
    lines.append("|---|---|---|---|---|---|---|")
    for m in mapping_rows:
        actual_str = "; ".join(m["actual_forms_sampled"][:6]) or "_none_"
        if len(m["actual_forms_sampled"]) > 6:
            actual_str += f" ... (+{len(m['actual_forms_sampled'])-6} more)"
        lines.append(
            f"| {m['event_type']} | {', '.join(m['expected_keywords'])} | {actual_str} | "
            f"{m['n_total']} | {m['n_d1']} | {m['n_d2']} | {m['coverage_status']} |"
        )
    lines.append("\n## Variant normalization (apply in D3 parser pipeline)\n")
    lines.append("```")
    lines.append(f"CORRECTION_PREFIXES = {CORRECTION_PREFIXES}")
    lines.append(f"SUBSIDIARY_SUFFIXES = {SUBSIDIARY_SUFFIXES}")
    lines.append("SERIES_PATTERN = r'\\(제\\d+회차\\)'")
    lines.append("```")
    lines.append(
        "Normalize each report_nm by stripping correction prefix, subsidiary suffix, series marker → base_form."
    )
    (REPORT_DIR / "d2_actual_form_taxonomy_mapping.md").write_text("\n".join(lines), encoding="utf-8")

    # 3. d2_xml_schema_mapping_by_form.md
    schema_lines = ["# D2 XML Schema Mapping by Form\n"]
    schema_lines.append(
        "For each base form encountered in D1+D2 sample, the table below lists the observed XML structure summary and candidate fields for parser implementation.\n"
    )
    schema_lines.append("Reference XML samples are stored under `data/acquired/round4/s2_dart_body_d1/raw_xml/` and `data/acquired/round4/s2_dart_body_d2/raw_xml/`.\n")
    for form, info in sorted(schema_per_form.items(), key=lambda x: x[0]):
        schema_lines.append(f"## {form}\n")
        schema_lines.append(f"- Sample rcept_no: `{info.get('rcept_no')}`")
        schema_lines.append(f"- XML size: {info.get('size_bytes', 0):,} bytes")
        schema_lines.append(f"- Has DOCUMENT root: {info.get('has_document')}")
        schema_lines.append(f"- SECTION count: {info.get('section_count')} / TABLE count: {info.get('table_count')} / TH count: {info.get('th_count')} / TD count: {info.get('td_count')}")
        if info.get("title"):
            schema_lines.append(f"- Title: `{info['title']}`")
        if info.get("distinct_th_labels"):
            schema_lines.append("- Distinct TH labels (truncated to 40):")
            for label in info["distinct_th_labels"]:
                schema_lines.append(f"  - {label}")
        for cand_key in ("candidate_date_fields", "candidate_amount_fields", "candidate_share_fields", "candidate_effective_date_fields"):
            cand = info.get(cand_key, [])
            if cand:
                schema_lines.append(f"- {cand_key}: {cand}")
        if info.get("correction_reference_hints"):
            schema_lines.append(f"- Correction reference hints in XML: {info['correction_reference_hints']}")
        schema_lines.append("")
    (REPORT_DIR / "d2_xml_schema_mapping_by_form.md").write_text("\n".join(schema_lines), encoding="utf-8")

    # 4. d2_missing_event_type_samples.md
    miss_lines = ["# D2 Missing / Under-Sampled Event Type Acquisition\n"]
    miss_lines.append("Per Referee D2 mandatory addition (c), D2 explicitly acquired samples for under-sampled event types.\n")
    miss_lines.append("| Event type | D1 sampled | D2 added | Total | Status |")
    miss_lines.append("|---|---|---|---|---|")
    for m in mapping_rows:
        if m["event_type"] in ["treasury_acquire", "treasury_dispose", "cb_issue", "bw_issue", "conversion_request",
                                "rights_issue", "bonus_issue", "capital_reduction", "merger_split"]:
            continue
        status = m["coverage_status"]
        if m["n_total"] == 0:
            status = "**SOURCE-UNAVAILABLE — explicitly marked, not silently ignored**"
        elif m["n_d2"] > 0:
            status = f"D2 expansion successful (+{m['n_d2']} samples)"
        miss_lines.append(f"| {m['event_type']} | {m['n_d1']} | {m['n_d2']} | {m['n_total']} | {status} |")
    miss_lines.append("\n## KOSDAQ coverage")
    kosdaq_n = int((d2_samples.get("expected_event_type", pd.Series([])).eq("kosdaq_general")).sum()) if len(d2_samples) else 0
    miss_lines.append(f"- KOSDAQ general samples acquired via OPENDART list API: {kosdaq_n}")
    miss_lines.append(f"- R000 KOSPI parquet has 0 KOSDAQ disclosures (corp_cls all 'Y'); D2 acquires via `list.json?corp_cls=K`.")
    (REPORT_DIR / "d2_missing_event_type_samples.md").write_text("\n".join(miss_lines), encoding="utf-8")

    # 5. d2_tiny_response_attachment_fallback.md
    d2_dl_df = pd.DataFrame(d2_dl_results) if d2_dl_results else pd.DataFrame()
    n_tiny = int(d2_dl_df.get("tiny_response_flag", pd.Series(dtype=bool)).sum()) if len(d2_dl_df) else 0
    n_attach = int(d2_dl_df.get("attachment_only_flag", pd.Series(dtype=bool)).sum()) if len(d2_dl_df) else 0
    n_not_parse = int(d2_dl_df.get("not_parseable_body", pd.Series(dtype=bool)).sum()) if len(d2_dl_df) else 0
    fb_lines = [
        "# D2 Tiny-Response / Attachment-Only Fallback Design\n",
        "Per Referee D2 mandatory addition (d), 6 classification flags defined for non-body disclosures.\n",
        "## Flags (D3 parser pipeline)\n",
        "| Flag | Trigger | Meaning |",
        "|---|---|---|",
        "| `tiny_response_flag` | HTTP 200 + body ≤ 500 bytes | OPENDART API returned no body XML (likely attachment-only filing) |",
        "| `attachment_only_flag` | tiny_response_flag OR `<DOCUMENT>` absent | Body content is in PDF/HWP attachment, not in the body XML |",
        "| `html_scrape_fallback_possible` | dart_url page contains structured table | DART web page (`dsaf001/main.do`) can be scraped instead of body XML |",
        "| `pdf_only_flag` | Attachment listing returns only PDF/HWP MIME | No machine-readable body or HTML; manual or OCR required |",
        "| `not_parseable_body` | ZIP corrupted OR XML malformed | Download succeeded but parser cannot read |",
        "| `manual_review_required` | (attachment_only AND not_pdf_parseable) OR not_parseable_body | Surface to user audit log |",
        "",
        "## D1+D2 observed counts",
        f"- tiny_response_flag (D2 download only): {n_tiny}",
        f"- attachment_only_flag (D2 download only): {n_attach}",
        f"- not_parseable_body (D2 download only): {n_not_parse}",
        "- D1 had 4 tiny-response failures retroactively classified as `tiny_response_flag = True, attachment_only_flag = True`",
        "",
        "## Parser denominator policy",
        "",
        "- Disclosures with `attachment_only_flag = True` are EXCLUDED from parser success-rate denominator (Referee directive: classified, not treated as parser failures).",
        "- Such disclosures are counted in a separate `attachment_only_count` field in the D6 A0 report.",
        "- PDF parsing / OCR is OUT OF SCOPE for current S2 phase (Referee S2 scope: parser modules only).",
        "",
        "## HTML scrape fallback (D3 prerequisite)",
        "",
        "- For `attachment_only_flag = True` AND `html_scrape_fallback_possible = True`, D3 may extract structured table from `dart_url`.",
        "- BUT: D3 parser implementation is NOT YET approved by Referee. HTML scraper is design-only in D2; implementation deferred to post-D2 Referee decision.",
    ]
    (REPORT_DIR / "d2_tiny_response_attachment_fallback.md").write_text("\n".join(fb_lines), encoding="utf-8")

    # 6. d2_correction_cancellation_linkage_design.md
    link_lines = [
        "# D2 Correction / Cancellation / Withdrawal Linkage Design\n",
        "Per Referee D2 mandatory: correction / cancellation / amendment form normalization.\n",
        "## Variant taxonomy\n",
        "| Prefix / form | Meaning | Linkage required |",
        "|---|---|---|",
        "| `[기재정정]` | 본문 기재 정정 | YES → link to most recent non-corrected version of same (corp_code + base_form) |",
        "| `[첨부정정]` | 첨부 정정 | YES (same as above) |",
        "| `[첨부추가]` | 첨부 추가 | NO — supplement, original event intact |",
        "| `[연장결정]` | 연장 결정 | NO — event continuation, no original-event reference |",
        "| `철회신고서` | 철회 | YES → original event must be marked withdrawn |",
        "| `취소공시` (e.g., 가족친화인증 취소) | 취소 | YES → original event marked cancelled |",
        "",
        "## Linkage algorithm (D3 design)\n",
        "```python",
        "def link_correction(df_events):",
        "    # 1. normalize report_nm → (correction_prefix, base_form, subsidiary_suffix, series_marker)",
        "    # 2. for each correction_prefix row, find most recent prior row with:",
        "    #    - same corp_code",
        "    #    - same base_form (after strip)",
        "    #    - same series_marker (if any)",
        "    #    - rcept_date <= correction.rcept_date",
        "    # 3. link via 'original_rcept_no' field",
        "    # 4. event_date_effective = correction's event_date if specified, else original's",
        "    # 5. amount_after_correction = correction's amounts (override original)",
        "    pass",
        "```",
        "",
        "## Output schema linkage fields (Referee 17-field schema)\n",
        "| Field | Use in linkage |",
        "|---|---|",
        "| `rcept_no` | this disclosure |",
        "| `cancellation_linkage` | original_rcept_no if this is a correction/cancellation |",
        "| `event_date` | base or corrected business date |",
        "| `effective_date` | overrides set by correction if any |",
        "| `parser_confidence` | reduced if linkage is ambiguous (multiple candidate originals) |",
        "",
        "## Edge cases observed in samples\n",
        "- `[기재정정]주요사항보고서(자기주식취득결정)` linking to original `주요사항보고서(자기주식취득결정)` → typical case\n",
        "- `[기재정정]주요사항보고서(자기주식취득결정)(자회사의 주요경영사항)` — subsidiary variant — must match same `(자회사의 주요경영사항)` suffix\n",
        "- `[기재정정]전환청구권행사(제2회차)` — series_marker `(제2회차)` must match\n",
        "- `철회신고서` (120 in R000) — body XML may not name original explicitly; use `corp_code + rcept_date window (≤30 days prior)` as fallback\n",
        "- `취소공시` patterns are heterogeneous (e.g., `가족친화인증 취소`) — most are NOT shareholder events; filter by base_form whitelist before linkage",
    ]
    (REPORT_DIR / "d2_correction_cancellation_linkage_design.md").write_text("\n".join(link_lines), encoding="utf-8")

    # 7. d2_parser_wave_readiness.md
    pw_lines = [
        "# D2 Parser Wave Readiness\n",
        "Each D3 parser wave needs a clear field map + failure modes. This document fixes those for waves D3a, D3b, D3c. Implementation NOT YET APPROVED by Referee.\n",
        "## D3a — Treasury (자사주)\n",
        "Forms covered:\n",
        "- 주요사항보고서(자기주식취득결정), 자기주식취득결과보고서, 주요사항보고서(자기주식취득신탁계약체결결정), 주요사항보고서(자기주식취득신탁계약해지결정)\n",
        "- 주요사항보고서(자기주식처분결정), 자기주식처분결과보고서\n",
        "- 주식소각결정\n",
        "\nField map:\n",
        "| Output schema field | Source TH label candidates | Notes |\n",
        "|---|---|---|\n",
        "| amount_krw | 취득예정금액, 처분예정금액, 소각예정금액 | 단위 원 vs 백만원 normalize |\n",
        "| shares | 취득예정주식수, 처분예정주식수, 소각예정주식수 | 보통주/우선주 분리 |\n",
        "| shares_before | 발행주식총수 / 자기주식 보유현황 | optional |\n",
        "| shares_after | 처분/취득 후 자기주식 수 | computed if not explicit |\n",
        "| event_date | 이사회 결의일 | rcept_date 가 아닌 결의일 |\n",
        "| effective_date | 예정 취득/처분 기간 시작일 | optional |\n",
        "\nFailure modes:\n",
        "- 신탁계약 체결/해지: 금액/주식수 둘 다 unspecified → `parser_confidence` 낮춤\n",
        "- 결과보고서 vs 결정 분리 → event_type 세분화\n",
        "- 자회사 주요경영사항 suffix → 모회사 corp_code 별도 처리\n",
        "",
        "## D3b — CB/BW + Conversion Request\n",
        "Forms covered:\n",
        "- 주요사항보고서(전환사채권발행결정), 주요사항보고서(신주인수권부사채권발행결정)\n",
        "- 전환청구권행사 (제N회차)\n",
        "\nField map:\n",
        "| Output schema field | Source TH label candidates | Notes |\n",
        "|---|---|---|\n",
        "| amount_krw | 사채총액, 발행금액 | |\n",
        "| shares | 전환가능주식수, 신주인수가능주식수 | dilution proxy |\n",
        "| factor | 전환가액 ÷ 전환가능주식수 | computed |\n",
        "| event_date | 발행 결의일, 전환청구일 | |\n",
        "| effective_date | 납입일, 전환일 | |\n",
        "\nFailure modes:\n",
        "- 회차 marker 누락 → series_marker null → linkage 어려움\n",
        "- 전환가액 reset 조항 → 본문 텍스트에 description, structured field 아님 → manual_review_required\n",
        "- 첨부정정 = factor/amount 변경 → linkage 필수\n",
        "",
        "## D3c — 기타 (유증/무증/감자/합병·분할/추가상장/보호예수/대주주매도/철회·취소)\n",
        "Forms covered:\n",
        "- 주요사항보고서(유상증자결정), 주요사항보고서(무상증자결정)\n",
        "- 주요사항보고서(감자결정)\n",
        "- 주요사항보고서(회사합병결정), 주요사항보고서(회사분할결정), 회사분할합병결정\n",
        "- 추가상장 (R000 KOSPI 3 disclosures only; KOSDAQ list API expansion required)\n",
        "- 보호예수 (기타안내사항 형태)\n",
        "- 임원ㆍ주요주주특정증권등소유상황보고서 + 거래계획\n",
        "- 철회신고서 + 취소공시 (heterogeneous, base_form whitelist 필요)\n",
        "\nFailure modes:\n",
        "- 추가상장/보호예수 = `기타안내사항` 안에 자유 텍스트 → structured field 부재 → `manual_review_required` 빈도 높음\n",
        "- 임원 보고서 = 거래 후 보고 (lag), 거래계획은 ex-ante → event_date 구분 필수\n",
        "- 취소공시 = 다수가 shareholder event 아님 (예: 인증 취소) → whitelist 적용\n",
        "",
        "## Parallelization gate\n",
        "D3a / D3b / D3c parallelizable after D2 schema mapping (this document) Referee-approved. D3 implementation NOT YET APPROVED — awaiting Referee D2 review verdict.",
    ]
    (REPORT_DIR / "d2_parser_wave_readiness.md").write_text("\n".join(pw_lines), encoding="utf-8")

    # 8. d2_failure_modes_register.md
    fr_lines = [
        "# D2 Failure Modes Register\n",
        "Consolidated list of failure modes observed in D1+D2, and the classification policy for each.\n",
        "| Failure mode | D1 count | D2 count | Classification | Parser policy |",
        "|---|---|---|---|---|",
    ]
    d1_tiny = 4  # known from D1 failure ledger
    fr_lines.append(f"| tiny_response (body absent) | {d1_tiny} | {n_tiny} | attachment_only_flag = True | excluded from parser denominator |")
    fr_lines.append(f"| not_parseable_body (BadZipFile / malformed XML) | 0 | {n_not_parse} | not_parseable_body = True | manual_review_required |")
    fr_lines.append(f"| http_non_200 | 0 | {int((d2_dl_df['http_status'].fillna(0).astype(int) != 200).sum() if len(d2_dl_df) else 0)} | retry → fail | logged separately |")
    fr_lines.append(f"| req_exception (network) | 0 | {int(d2_dl_df['error'].fillna('').str.startswith('req_exception').sum() if len(d2_dl_df) else 0)} | retry → fail | logged separately |")
    fr_lines.append("\n## Other identified failure modes (design-only, not yet hit)")
    fr_lines.append("")
    fr_lines.append("- `correction_link_ambiguous`: multiple candidate originals in time window → parser_confidence reduced")
    fr_lines.append("- `withdrawal_no_explicit_original`: 철회신고서 body does not name original rcept_no → use corp_code + 30-day window fallback")
    fr_lines.append("- `subsidiary_corp_code_mismatch`: 자회사 주요경영사항 suffix uses parent corp_code → must remap")
    fr_lines.append("- `series_marker_missing`: 전환청구권행사 회차 marker null → linkage hard")
    fr_lines.append("- `kosdaq_only_form`: D2 KOSDAQ list API surfaced disclosure types not in R000 KOSPI inventory → D3 D3c form map must extend")
    fr_lines.append("")
    fr_lines.append("## Register file")
    fr_lines.append("")
    fr_lines.append(f"Raw download log + failure detail: `data/acquired/round4/s2_dart_body_d2/d2_download_log.csv` (gitignored)")
    fr_lines.append(f"Persisted failure rows: `data/acquired/round4/s2_dart_body_d2/d2_failure_ledger.csv` (gitignored)")
    (REPORT_DIR / "d2_failure_modes_register.md").write_text("\n".join(fr_lines), encoding="utf-8")

    # Save data files (gitignored)
    if len(d2_dl_df):
        d2_dl_df.to_csv(D2_DIR / "d2_download_log.csv", index=False)
        d2_dl_df[~d2_dl_df["ok"]].to_csv(D2_DIR / "d2_failure_ledger.csv", index=False)


def main() -> int:
    load_env(ENV_PATH)
    api_key = os.environ.get("OPENDART_API_KEY")
    if not api_key:
        print("ERROR: OPENDART_API_KEY not loaded.", file=sys.stderr)
        return 1
    print(f"API key loaded (length={len(api_key)})")

    D2_DIR.mkdir(parents=True, exist_ok=True)
    D2_RAW_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Load D1 samples (already downloaded XMLs we can reuse)
    print("Loading D1 sample CSV + XML inventory...")
    d1_samples = pd.read_csv(D1_SAMPLES_CSV)
    d1_xml_files = {}
    for rcept_no in d1_samples["rcept_no"].astype(str):
        p = D1_RAW_DIR / f"{rcept_no}.xml"
        if p.exists():
            d1_xml_files[rcept_no] = p
    print(f"  D1 samples = {len(d1_samples)}, D1 XMLs available = {len(d1_xml_files)}")

    # Step 2: Select D2 KOSPI new samples (missing event types)
    print("Selecting D2 KOSPI samples for missing event types...")
    d2_kospi = select_d2_kospi_samples(PARQUET_PATH)
    print(f"  D2 KOSPI new samples = {len(d2_kospi)}")

    # Step 3: Acquire KOSDAQ samples via OPENDART list API
    print("Acquiring KOSDAQ samples via OPENDART list API...")
    d2_kosdaq = acquire_kosdaq_samples(api_key)
    print(f"  KOSDAQ samples = {len(d2_kosdaq)}")

    d2_samples = pd.concat([d2_kospi, d2_kosdaq], ignore_index=True) if len(d2_kosdaq) else d2_kospi
    if "rcept_no" in d2_samples.columns:
        d2_samples = d2_samples.drop_duplicates("rcept_no")
    print(f"  D2 total new samples = {len(d2_samples)}")

    # Step 4: Download body XML for D2 samples
    print("Downloading D2 body XMLs...")
    d2_dl_results = []
    for i, rcept_no in enumerate(d2_samples["rcept_no"].astype(str).tolist(), 1):
        res = download_one(rcept_no, api_key, D2_RAW_DIR)
        d2_dl_results.append(res)
        status = "OK" if res["ok"] else f"FAIL({res['error']})"
        flag_str = ""
        for fk in ("tiny_response_flag", "attachment_only_flag", "not_parseable_body"):
            if res[fk]:
                flag_str += f" {fk}=T"
        print(f"  [{i:>3}/{len(d2_samples)}] {rcept_no} status={res['http_status']} {status} {res['bytes']}B{flag_str}")
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # Step 5: XML schema analysis per base form (D1 + D2)
    print("Analyzing XML schemas per base form...")
    schema_per_form = {}
    all_samples = pd.concat([d1_samples.assign(phase="D1"), d2_samples.assign(phase="D2")], ignore_index=True)
    for _, row in all_samples.iterrows():
        rcept_no = str(row["rcept_no"])
        report_nm = row.get("report_nm", "") or ""
        norm = normalize_form(report_nm)
        base_form = norm["base_form"]
        if not base_form or base_form in schema_per_form:
            continue
        xml_path = None
        for d in (D1_RAW_DIR, D2_RAW_DIR):
            p = d / f"{rcept_no}.xml"
            if p.exists():
                xml_path = p
                break
        if xml_path is None:
            continue
        try:
            info = analyze_xml_schema(xml_path.read_bytes())
            info["rcept_no"] = rcept_no
            info["normalized"] = norm
            schema_per_form[base_form] = info
        except Exception as exc:
            print(f"  schema-analyze fail {rcept_no}: {type(exc).__name__}")

    print(f"  Distinct base forms analyzed: {len(schema_per_form)}")

    # Step 6: Write 8 D2 reports
    print("Writing D2 reports...")
    failure_register: list[dict] = []
    write_reports(d1_samples, d1_xml_files, d2_samples, d2_dl_results, schema_per_form, failure_register)

    n_ok = sum(1 for r in d2_dl_results if r["ok"])
    print(f"D2 schema mapping complete: {n_ok}/{len(d2_dl_results)} OK, {len(schema_per_form)} forms schema-analyzed.")
    print(f"Reports: {REPORT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
