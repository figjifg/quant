"""S2 D3 Triage — Referee S2-D3-Triage phase (infrastructure only).

Allowed (per 2026-05-23 Referee verdict):
1. D3a manual-audit-driven label enumeration (per base form)
2. D3b feasibility triage (5-category classification)
3. D3b custom-parser decision
4. C2/C3 design constraints

NOT allowed: D3c full implementation, C2/C3 integration, unified event log,
strategy testing, return outcome, parser-strategy-ready claim.
"""
from __future__ import annotations

import json
import re
import sys
import warnings
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

REPO_ROOT = Path("/home/jin/code/quant")
D1_RAW = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d1" / "raw_xml"
D2_RAW = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d2" / "raw_xml"
D1_SAMPLES = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d1" / "samples_50.csv"
D2_SAMPLES = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d2" / "all_samples_d1_d2.csv"
REPORT_DIR = REPO_ROOT / "reports" / "experiments" / "S2_phase_d3_triage"
TRIAGE_DATA_DIR = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d3_triage"

CORRECTION_PREFIXES = ["[기재정정]", "[첨부정정]", "[첨부추가]", "[연장결정]"]
SUBSIDIARY_SUFFIXES = ["(자회사의 주요경영사항)", "(종속회사의주요경영사항)"]
SERIES_PATTERN = re.compile(r"\(제\s*\d+\s*회\s*차?\)")

D3A_BASE_FORMS = [
    "주요사항보고서(자기주식취득결정)", "주요사항보고서(자기주식처분결정)", "주식소각결정",
    "주요사항보고서(자기주식취득신탁계약체결결정)", "주요사항보고서(자기주식취득신탁계약해지결정)",
    "자기주식취득결과보고서", "자기주식처분결과보고서",
]
D3B_CATEGORIES = {
    "cb_issue": ["전환사채권발행결정"],
    "bw_issue": ["신주인수권부사채권발행결정"],
    "conversion_request": ["전환청구권행사"],
}

# Target labels by D3a base form (Referee target fields)
D3A_TARGET_FIELDS = ["amount_krw", "shares", "event_date", "effective_date"]
D3A_TARGET_HINTS = {
    "주요사항보고서(자기주식취득결정)": {
        "amount_krw": ["취득예정금액"], "shares": ["취득예정주식"],
        "event_date": ["이사회결의일", "이사회 결의일", "결의일"],
        "effective_date": ["취득예상기간", "취득기간"],
    },
    "주요사항보고서(자기주식처분결정)": {
        "amount_krw": ["처분예정금액"], "shares": ["처분예정주식"],
        "event_date": ["이사회결의일", "이사회 결의일", "처분결정일", "결의일"],
        "effective_date": ["처분예정기간", "처분기간"],
    },
    "주식소각결정": {
        "amount_krw": ["소각예정금액", "소각금액"], "shares": ["소각예정주식", "소각주식수"],
        "event_date": ["이사회결의일", "결의일"],
        "effective_date": ["소각예정일"],
    },
    "주요사항보고서(자기주식취득신탁계약체결결정)": {
        "amount_krw": ["계약금액", "신탁계약금액"], "shares": ["취득예정주식수", "취득가능주식"],
        "event_date": ["이사회결의일", "결의일"],
        "effective_date": ["계약기간"],
    },
    "주요사항보고서(자기주식취득신탁계약해지결정)": {
        "amount_krw": ["반환금액", "계약금액"], "shares": ["보유주식수", "취득주식수"],
        "event_date": ["이사회결의일", "결의일"],
        "effective_date": ["해지일", "계약기간"],
    },
    "자기주식취득결과보고서": {
        "amount_krw": ["취득가액총", "1주당취득가액"], "shares": ["취득수량", "취득주식 총수"],
        "event_date": ["일 자", "보고일"],
        "effective_date": ["부터", "까지"],
    },
    "자기주식처분결과보고서": {
        "amount_krw": ["처분가액총", "1주당처분가액"], "shares": ["처분수량", "처분주식 총수"],
        "event_date": ["일 자", "보고일"],
        "effective_date": ["부터", "까지"],
    },
}


def safe_decode(b: bytes) -> str:
    head = b[:200].decode("ascii", errors="replace").lower()
    m = re.search(r'encoding=["\']([^"\']+)["\']', head)
    enc = m.group(1) if m else "utf-8"
    try:
        return b.decode(enc, errors="replace")
    except LookupError:
        return b.decode("utf-8", errors="replace")


def clean_text(t: str) -> str:
    t = t.replace("&cr;", " ").replace("&nbsp;", " ").replace("\xa0", " ")
    return re.sub(r"\s+", " ", t).strip()


def strip_normalize(report_nm: str) -> str:
    if not report_nm:
        return ""
    for p in CORRECTION_PREFIXES:
        if report_nm.startswith(p):
            report_nm = report_nm[len(p):]
            break
    for s in SUBSIDIARY_SUFFIXES:
        if s in report_nm:
            report_nm = report_nm.replace(s, "").strip()
            break
    return SERIES_PATTERN.sub("", report_nm).strip()


def get_xml_path(rcept_no: str) -> Path | None:
    for d in (D1_RAW, D2_RAW):
        p = d / f"{rcept_no}.xml"
        if p.exists():
            return p
    return None


def classify_response(b: bytes) -> str:
    if len(b) <= 500:
        return "tiny"
    head = b[:600].decode("utf-8", errors="replace").lower()
    if "<html" in head:
        return "html_inline"
    if "<document" in head:
        return "dart_xml"
    return "unknown"


def extract_all_pairs(xml_bytes: bytes) -> list[tuple[str, str]]:
    text = safe_decode(xml_bytes)
    text = re.sub(r"<USERMARK[^>]*/?>", "", text)
    try:
        soup = BeautifulSoup(text, "lxml")
    except Exception:
        soup = BeautifulSoup(text, "html.parser")
    pairs: list[tuple[str, str]] = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells_raw = tr.find_all(["td", "th"])
            cells = [clean_text(c.get_text(" ", strip=True)) for c in cells_raw]
            cells = [c for c in cells if c]
            if len(cells) >= 2:
                pairs.append((cells[0][:80], " | ".join(cells[1:])[:160]))
            # flat adjacency
            for i in range(len(cells) - 1):
                if cells[i] and len(cells[i]) <= 80:
                    pairs.append((cells[i][:80], cells[i + 1][:160]))
    return pairs


def has_label_for(pairs: list[tuple[str, str]], keywords: list[str]) -> tuple[bool, str | None]:
    """Return (found_in_table, sample_value)."""
    for label, value in pairs:
        if any(kw in label for kw in keywords):
            v = (value or "").strip()
            if v and v != label.strip():
                return True, value[:80]
    return False, None


def find_in_freetext(xml_bytes: bytes, keywords: list[str]) -> bool:
    """Check whether keyword appears in free-text outside tables (e.g., SECTION/COVER)."""
    text = safe_decode(xml_bytes)
    # remove table content first
    text_no_tables = re.sub(r"<TABLE.*?</TABLE>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text_no_tags = re.sub(r"<[^>]+>", " ", text_no_tables)
    text_no_tags = clean_text(text_no_tags)
    return any(kw in text_no_tags for kw in keywords)


def classify_d3b_extractability(xml_bytes: bytes, resp_type: str, sub_category: str) -> dict:
    """Classify D3b row into 5 Referee categories per target field."""
    if resp_type == "tiny":
        return {"shares": "attachment_only", "event_date": "attachment_only"}
    if resp_type == "unknown":
        return {"shares": "not_extractable", "event_date": "not_extractable"}

    if sub_category in ("cb_issue", "bw_issue"):
        shares_kw = ["전환(행사)가능주식수", "전환가능주식수", "행사가능주식수", "전환가능주식", "행사가능주식"]
        event_kw = ["이사회결의일", "이사회 결의일", "결의일", "발행결의일"]
    else:  # conversion_request
        shares_kw = ["발행주식", "전환주식수", "신주의 종류와 수", "전환에 따라 발행한", "전환가능주식수"]
        event_kw = ["전환청구일", "청구일", "이사회결의일", "결의일"]

    pairs = extract_all_pairs(xml_bytes)
    result = {}
    for field, kws in [("shares", shares_kw), ("event_date", event_kw)]:
        in_table, sample = has_label_for(pairs, kws)
        if in_table:
            result[field] = "structured_extractable"
            result[f"{field}_sample"] = sample
        else:
            in_text = find_in_freetext(xml_bytes, kws)
            if in_text:
                result[field] = "text_extractable"
            else:
                if resp_type == "html_inline":
                    result[field] = "ambiguous"
                else:
                    result[field] = "not_extractable"
    return result


def d3a_label_audit(samples_d3a: pd.DataFrame) -> dict:
    """Per D3a base form, audit which target fields have deterministic table labels."""
    out = {}  # base_form -> {field -> {n_samples, n_table_hit, sample_labels: [...], determinism}}
    for base_form, group in samples_d3a.groupby("base_form_normalized"):
        if base_form not in D3A_TARGET_HINTS:
            continue
        hints = D3A_TARGET_HINTS[base_form]
        field_audit = {}
        n_total = 0
        for _, row in group.iterrows():
            xml_path = get_xml_path(str(row["rcept_no"]))
            if not xml_path:
                continue
            n_total += 1
            xml_bytes = xml_path.read_bytes()
            resp = classify_response(xml_bytes)
            if resp == "tiny":
                continue
            pairs = extract_all_pairs(xml_bytes)
            for field in D3A_TARGET_FIELDS:
                kws = hints.get(field, [])
                in_table, sample = has_label_for(pairs, kws)
                field_audit.setdefault(field, {"n_table_hit": 0, "samples": [], "distinct_labels": Counter()})
                if in_table:
                    field_audit[field]["n_table_hit"] += 1
                    if sample:
                        field_audit[field]["samples"].append({"rcept_no": str(row["rcept_no"]), "value": sample})
                    # find the actual label that matched
                    for label, value in pairs:
                        if any(kw in label for kw in kws):
                            field_audit[field]["distinct_labels"][label[:60]] += 1
                            break
        # compute determinism
        for field in D3A_TARGET_FIELDS:
            fa = field_audit.get(field, {"n_table_hit": 0, "samples": [], "distinct_labels": Counter()})
            hit_rate = fa["n_table_hit"] / max(1, n_total)
            n_distinct = len(fa["distinct_labels"])
            if hit_rate >= 0.7 and n_distinct <= 5:
                determinism = "deterministic"
            elif hit_rate >= 0.4:
                determinism = "partially_deterministic"
            else:
                determinism = "non_deterministic"
            fa["hit_rate"] = round(hit_rate, 3)
            fa["determinism"] = determinism
            fa["distinct_labels_top"] = dict(fa["distinct_labels"].most_common(8))
            del fa["distinct_labels"]
            fa["samples"] = fa["samples"][:5]
            field_audit[field] = fa
        out[base_form] = {"n_total": n_total, "fields": field_audit}
    return out


def d3b_triage(samples_d3b: pd.DataFrame) -> dict:
    """Per CB/BW/conversion sub-category, classify each row in 5 categories per field."""
    out = {}
    for sub_cat, kws in D3B_CATEGORIES.items():
        rows = samples_d3b[samples_d3b["base_form_normalized"].apply(lambda x: any(k in (x or "") for k in kws))]
        classifications = []
        for _, row in rows.iterrows():
            xml_path = get_xml_path(str(row["rcept_no"]))
            if not xml_path:
                classifications.append({"rcept_no": str(row["rcept_no"]), "shares": "missing_xml", "event_date": "missing_xml"})
                continue
            xml_bytes = xml_path.read_bytes()
            resp = classify_response(xml_bytes)
            cls = classify_d3b_extractability(xml_bytes, resp, sub_cat)
            cls["rcept_no"] = str(row["rcept_no"])
            cls["response_type"] = resp
            classifications.append(cls)
        out[sub_cat] = classifications
    return out


def write_reports(d3a_audit: dict, d3b_classifications: dict, samples_d3a: pd.DataFrame, samples_d3b: pd.DataFrame):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TRIAGE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. d3a_manual_label_audit.md
    lines = [
        "# D3a Manual-Audit-Driven Label Enumeration\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Origin: Referee S2-D3-Triage verdict (2026-05-23).\n",
        "## Scope",
        f"- D3a base forms audited: {len(d3a_audit)}",
        f"- Available samples in D1+D2 union (Referee target was 10/base-form; we have fewer):",
    ]
    for bf in D3A_BASE_FORMS:
        n_avail = int((samples_d3a["base_form_normalized"] == bf).sum())
        lines.append(f"  - `{bf}`: **{n_avail}** samples available (target 10)")
    lines += [
        "",
        "**Limitation**: This is a desk-audit using the existing 36-row D3a sample. A true manual audit with 10 samples per base form would require acquiring more disclosures of each form. The determinism scores below should be read as 'how deterministic is the label-keyword mapping ON THE CURRENT SAMPLE'.",
        "",
        "## Determinism scoring",
        "- `deterministic`: ≥70% sample hit rate AND ≤5 distinct label phrasings",
        "- `partially_deterministic`: 40-70% hit rate",
        "- `non_deterministic`: <40% hit rate",
        "",
    ]
    for base_form, audit in d3a_audit.items():
        lines.append(f"## Base form: `{base_form}` (n={audit['n_total']})\n")
        for field in D3A_TARGET_FIELDS:
            fa = audit["fields"].get(field, {})
            lines.append(f"### Field: `{field}`")
            lines.append(f"- hit_rate: {fa.get('hit_rate', 0):.1%} ({fa.get('n_table_hit', 0)} / {audit['n_total']})")
            lines.append(f"- determinism: **{fa.get('determinism', 'n/a')}**")
            lbls = fa.get("distinct_labels_top", {})
            if lbls:
                lines.append(f"- distinct label phrasings (top {len(lbls)}):")
                for lbl, c in lbls.items():
                    lines.append(f"  - [{c}] `{lbl}`")
            else:
                lines.append("- distinct label phrasings: _none captured in current sample_")
            samples = fa.get("samples", [])
            if samples:
                lines.append("- sample value extractions:")
                for s in samples[:3]:
                    lines.append(f"  - `{s['rcept_no']}` → `{s.get('value','?')[:60]}`")
            lines.append("")
    # overall verdict
    overall_det = []
    for base_form, audit in d3a_audit.items():
        det_counts = Counter(audit["fields"].get(f, {}).get("determinism", "n/a") for f in D3A_TARGET_FIELDS)
        n_det = det_counts.get("deterministic", 0)
        overall_det.append((base_form, n_det, det_counts))
    lines += [
        "## Overall D3a label determinism summary\n",
        "| Base form | # fields deterministic | # partial | # non-deterministic |",
        "|---|---|---|---|",
    ]
    for bf, n_det, dc in overall_det:
        lines.append(f"| {bf} | {dc.get('deterministic',0)} | {dc.get('partially_deterministic',0)} | {dc.get('non_deterministic',0)} |")
    lines += [
        "",
        "## Verdict",
        "",
    ]
    deterministic_forms = [bf for bf, _, dc in overall_det if dc.get("deterministic", 0) >= 2]
    if len(deterministic_forms) >= 3:
        lines.append(f"- Labels are deterministic for ≥2 fields in {len(deterministic_forms)} base forms — D3a can plausibly receive one more targeted parser pass focused on these forms.")
        lines.append(f"- Forms with deterministic mapping: {', '.join(deterministic_forms)}")
        lines.append("- Per Referee decision rule: 'If D3a manual audit shows labels are deterministic, D3a may receive one more targeted parser pass.'")
    else:
        lines.append(f"- Labels are NOT consistently deterministic across base forms. Only {len(deterministic_forms)} of {len(overall_det)} base forms have ≥2 deterministic target fields.")
        lines.append("- Per Referee decision rule: 'If D3a labels remain ambiguous, lock D3a as PARTIAL.'")
        lines.append("- Executor recommendation: lock D3a as PARTIAL.")
    lines.append("\n## Hard locks reaffirmed: no strategy / no return outcome / no parser-strategy-ready")
    (REPORT_DIR / "d3a_manual_label_audit.md").write_text("\n".join(lines), encoding="utf-8")

    # 2. d3b_feasibility_triage.md
    lines = [
        "# D3b Feasibility Triage\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## 5-category classification (Referee taxonomy)",
        "",
        "- `structured_extractable`: target field found in body table via label-keyword match",
        "- `text_extractable`: target field present in free-text (outside tables) — keyword found in SECTION/COVER text",
        "- `attachment_only`: tiny response, body XML absent",
        "- `ambiguous`: HTML inline response without clear table label structure",
        "- `not_extractable`: target field not found in any form within the body",
        "- `missing_xml`: download failed in D1 (already known)",
        "",
    ]
    for sub_cat, rows in d3b_classifications.items():
        lines.append(f"## Sub-category: `{sub_cat}` (n={len(rows)})\n")
        if not rows:
            lines.append("_No samples in D1+D2 union for this sub-category._\n")
            continue
        # shares + event_date classification counts
        shares_counts = Counter(r.get("shares", "missing_xml") for r in rows)
        event_counts = Counter(r.get("event_date", "missing_xml") for r in rows)
        lines.append("### Shares classification distribution")
        lines.append("| Category | Count |")
        lines.append("|---|---|")
        for cat, cnt in shares_counts.most_common():
            lines.append(f"| {cat} | {cnt} |")
        lines.append("\n### event_date classification distribution")
        lines.append("| Category | Count |")
        lines.append("|---|---|")
        for cat, cnt in event_counts.most_common():
            lines.append(f"| {cat} | {cnt} |")
        lines.append("\n### Per-row triage (sample-level)")
        lines.append("| rcept_no | response_type | shares classification | event_date classification |")
        lines.append("|---|---|---|---|")
        for r in rows[:15]:
            lines.append(f"| {r.get('rcept_no')} | {r.get('response_type','?')} | {r.get('shares','?')} | {r.get('event_date','?')} |")
        lines.append("")
    # overall verdict
    cb_rows = d3b_classifications.get("cb_issue", [])
    bw_rows = d3b_classifications.get("bw_issue", [])
    conv_rows = d3b_classifications.get("conversion_request", [])
    cb_shares_text = sum(1 for r in cb_rows if r.get("shares") in ("text_extractable", "ambiguous"))
    bw_shares_text = sum(1 for r in bw_rows if r.get("shares") in ("text_extractable", "ambiguous"))
    conv_event_text = sum(1 for r in conv_rows if r.get("event_date") in ("text_extractable", "ambiguous"))
    lines += [
        "## Verdict",
        f"- CB issue: shares mostly text_extractable/ambiguous = {cb_shares_text} / {len(cb_rows)}",
        f"- BW issue: shares mostly text_extractable/ambiguous = {bw_shares_text} / {len(bw_rows)}",
        f"- conversion request: event_date mostly text_extractable/ambiguous = {conv_event_text} / {len(conv_rows)}",
        "",
        "Per Referee decision rule: 'If D3b shares/event_date are mostly text_extractable or ambiguous, do not continue generic parser tuning. Mark D3b as requiring per-form custom parser or manual audit.'",
        "",
    ]
    text_or_ambig_ratio = (cb_shares_text + bw_shares_text + conv_event_text) / max(1, (len(cb_rows) + len(bw_rows) + len(conv_rows)))
    if text_or_ambig_ratio >= 0.4:
        lines.append(f"- **Verdict: D3b requires per-form custom parser or manual audit** (text_extractable/ambiguous share = {text_or_ambig_ratio:.1%}).")
        lines.append("- Generic parser tuning should STOP.")
    else:
        lines.append(f"- text_extractable/ambiguous share is moderate ({text_or_ambig_ratio:.1%}). Some D3b extraction may still be reachable via continued tuning.")
    lines.append("\n## Hard locks reaffirmed: no strategy / no return outcome / no parser-strategy-ready")
    (REPORT_DIR / "d3b_feasibility_triage.md").write_text("\n".join(lines), encoding="utf-8")

    # 3. d3b_custom_parser_decision.md
    lines = [
        "# D3b Custom Parser Decision\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Scope: feasibility decision only. NO custom parser implementation per Referee.\n",
        "## Question 1: ACODE 11324 / 11325 need custom parsers?",
        "",
        f"- v3 parser amount_krw extraction (D3b): 23.5% (with current generic + ACODE-specific keyword stack)",
        f"- v3 parser conversion_price extraction: 29.4%",
        f"- v3 parser shares extraction: 5.9% (below v1 baseline 29.4%)",
        f"- v3 parser event_date extraction: 0.0%",
        "",
        "These ACODEs use multi-tier `<TABLE>` structures where:",
        "- `(A)` and `(B)` annotation columns split values between '대상자별' and aggregate rows",
        "- `1차/2차/3차` columns expand into multi-period series",
        "- Some target labels (event_date in particular) sit in `<COVER>` text, NOT in any `<TABLE>` row",
        "",
        "**Decision: YES** — ACODE 11324 and 11325 need form-specific custom parsers that:",
        "1. parse `<COVER>` / `<SECTION>` text for event_date (이사회 결의(결정)일 free-text date)",
        "2. handle `(A)` / `(B)` annotation columns explicitly",
        "3. dispatch on 'mass발행' vs '특정인 대상자' structure",
        "",
        "## Question 2: conversion_request without ACODE needs separate parser family?",
        "",
        f"- conversion_request samples in D1+D2: {len(conv_rows)} rows",
        f"- ACODE field on these rows in v3 audit trail: typically None (form '전환청구권행사' is published under different form code)",
        "",
        "**Decision: YES** — conversion_request needs its own parser family because:",
        "- No ACODE → cannot dispatch via ACODE_HINTS map",
        "- 회차 marker `(제N회차)` is critical and resides in report_nm, not body",
        "- 전환청구일 / 청구일 typically appear as label-value but in a smaller, simpler table than CB/BW",
        "",
        "## Question 3: SECTION/COVER text scanner required?",
        "",
        f"- v3 audit shows event_date 0% on D3b — root cause: in CB/BW 발행결정 body, event_date (이사회결의일) often lives in `<COVER>` block as free-text date, not in a table.",
        "",
        "**Decision: YES** — A SECTION/COVER text scanner is required for D3b event_date. Pattern target:",
        "  `이사회\\s*결의(결정)?일\\s*[:\\s]*(\\d{4})[년\\.\\-]\\s*(\\d{1,2})[월\\.\\-]\\s*(\\d{1,2})`",
        "",
        "## Estimated effort for D3b custom parser stack",
        "",
        "| Component | Estimated effort |",
        "|---|---|",
        "| ACODE 11324 (CB) custom parser | 1-2 weeks |",
        "| ACODE 11325 (BW) custom parser | 1-2 weeks (similar to CB) |",
        "| conversion_request parser family | 1 week |",
        "| SECTION/COVER text scanner | 3-5 days |",
        "| Manual audit on 20-50 samples per type | 1-2 weeks user time |",
        "| **Total** | **4-7 weeks** |",
        "",
        "## Compliance",
        "",
        "- This document is a FEASIBILITY decision only. No custom parser implementation per Referee restriction.",
        "- No strategy / no return outcome / no parser-strategy-ready language.",
        "- Referee approval required before implementing.",
    ]
    (REPORT_DIR / "d3b_custom_parser_decision.md").write_text("\n".join(lines), encoding="utf-8")

    # 4. d3_parser_scope_lock.md
    lines = [
        "# D3 Parser Scope Lock\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Final state of each D3 wave (post-triage)",
        "",
        "| Wave | Lock state | Reason |",
        "|---|---|---|",
    ]
    # D3a verdict (use the same logic as the audit)
    deterministic_forms_count = sum(1 for bf, _, dc in overall_det if dc.get("deterministic", 0) >= 2)
    if deterministic_forms_count >= 3:
        d3a_lock = "ONE-MORE-PASS-ALLOWED"
        d3a_reason = f"{deterministic_forms_count}/{len(overall_det)} base forms have deterministic labels for ≥2 target fields"
    else:
        d3a_lock = "PARTIAL"
        d3a_reason = f"only {deterministic_forms_count}/{len(overall_det)} base forms have deterministic labels"
    lines.append(f"| D3a | **{d3a_lock}** | {d3a_reason} |")
    lines.append(f"| D3b | **PARTIAL / NOT C3-ready** | shares (5.9% vs v1 29.4%) and event_date (0.0%) both miss Referee pass targets; custom parsers required (see d3b_custom_parser_decision.md) |")
    lines.append(f"| D3c | **CLOSED** | not opened per Referee; remains skeleton-only |")
    lines += [
        "",
        "## Downstream constraints",
        "",
        "- D3a current state may produce a partial corporate-action event log for treasury actions, but ONLY if explicitly marked as PARTIAL/INFRA. Cannot be described as strategy-ready.",
        "- D3b state means CB/BW dilution events and conversion requests are NOT in a usable event log shape. Overhang signal construction is blocked.",
        "- D3c forms (additional listing / lockup / major shareholder sale / correction-cancellation) remain unparsed; their event types are NOT available in any event log.",
        "- C2 (factor chain integration) and C3 (corporate action day reclassification) are NOT C3-ready.",
        "- KR-DART-BODY-RETURN-001 (backlog) remains unblock-able only on the D3a treasury subset, and only as PARTIAL.",
        "",
        "## Hard locks",
        "",
        "- No D3c full implementation",
        "- No C2/C3 integration",
        "- No unified all-event event log finalization",
        "- No strategy testing / return outcome",
        "- No parser-strategy-ready claim",
        "",
        "## Reopen conditions (Referee-only)",
        "",
        "- D3a one-more-pass: Referee approval after this triage",
        "- D3b: Referee approval to implement custom parsers OR mark D3b PARTIAL permanent",
        "- D3c: Referee approval after D3a/D3b state is resolved",
    ]
    (REPORT_DIR / "d3_parser_scope_lock.md").write_text("\n".join(lines), encoding="utf-8")

    # 5. c2_c3_design_constraints.md
    lines = [
        "# C2 / C3 Design Constraints (post-D3 triage)\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## C2 (factor chain integration) constraints",
        "",
        "- C2 design CANNOT assume a complete corporate-action event log.",
        "- D3a treasury events are partially available (subject to D3a PARTIAL/one-more-pass state).",
        "- D3b dilution events (CB/BW/conversion) are NOT C3-ready.",
        "- C2 factor chain must explicitly track which event types are sourced from parser vs not-yet-sourced.",
        "- C2 design should NOT block on a unified event log; instead, accept per-event-type partial coverage with explicit not_available flags.",
        "",
        "## C3 (corporate action day reclassification) constraints",
        "",
        "- C3 cannot reclassify days for corporate actions whose events are not in the partial event log.",
        "- Treasury cancellation (주식소각결정) and merger/split require the D3a one-more-pass to be feasible inputs to C3.",
        "- CB/BW dilution and conversion request events are NOT available for C3 reclassification until D3b custom parsers exist (Referee approval required).",
        "- C3 design must include a not_yet_available branch that surfaces uncovered events as audit log entries.",
        "",
        "## Affected G5 / TRAD residuals",
        "",
        "- G5_000005 DEFERRED-S2: still deferred; S2 phase parser cannot yet provide the corporate action day reclassification input.",
        "- G5_000004 35 strategy-relevant events: only the treasury subset is partially reachable via D3a. Other event types (CB/BW/conversion) remain unparsed.",
        "- TRAD_000003 limit pollution (41 rows): same constraint; C3 reclassification of corp_action_day still blocked.",
        "",
        "## Allowed C2/C3 design activities",
        "",
        "- Documentation updates reflecting D3a partial / D3b not-ready / D3c closed",
        "- Schema design for event log with explicit `event_source` and `event_status` fields (parser-source / not_available / partial)",
        "- Spec for not_yet_available event type handling in C3 day reclassification",
        "",
        "## NOT allowed",
        "",
        "- Wire parser outputs into a production C2/C3 path",
        "- Create unified all-event event log",
        "- Use C2/C3 outputs in strategy testing of any kind",
        "- Treat parser output as strategy-ready",
    ]
    (REPORT_DIR / "c2_c3_design_constraints.md").write_text("\n".join(lines), encoding="utf-8")

    # 6. d3_next_referee_decision_brief.md
    lines = [
        "# D3 Next Referee Decision Brief\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Triage summary",
        f"- D3a: {d3a_lock} ({deterministic_forms_count}/{len(overall_det)} base forms with deterministic labels)",
        "- D3b: PARTIAL / NOT C3-ready (Referee pass targets MISSED on shares and event_date)",
        "- D3c: CLOSED",
        "- C2/C3 integration: design-only constraints documented",
        "",
        "## Decision points for Referee",
        "",
        "### Decision 1: D3a one-more-pass",
        f"- This triage shows D3a labels are deterministic on {deterministic_forms_count}/{len(overall_det)} base forms.",
        "- Per Referee rule: deterministic → one more targeted parser pass allowed.",
        "- Question: approve one final D3a parser pass with manual-audit-driven labels? OR lock D3a as PARTIAL?",
        "",
        "### Decision 2: D3b custom parsers",
        "- Feasibility study shows D3b needs:",
        "  - ACODE 11324 / 11325 custom parsers",
        "  - conversion_request separate parser family",
        "  - SECTION/COVER text scanner for event_date",
        "- Estimated effort: 4-7 weeks",
        "- Question: approve D3b custom parser implementation? OR lock D3b as permanently PARTIAL?",
        "",
        "### Decision 3: S2 phase end",
        "- Per original Referee S2 phase scope, the end condition is the S2 parser A0 report.",
        "- The D3 triage may be the natural stopping point — D3a partial + D3b partial = honest A0 outcome.",
        "- Question: declare S2 phase complete with current PARTIAL state and produce the S2 parser A0 final report? OR continue D3a/D3b work?",
        "",
        "### Decision 4: C2/C3 design",
        "- Design constraints documented; no wiring permitted.",
        "- Question: allow C2/C3 design-only work to proceed in parallel? OR hold until D3 state is finalized?",
        "",
        "## Hard prohibitions (continuing)",
        "",
        "- No D3c full implementation",
        "- No unified all-event event log finalization",
        "- No strategy testing / return outcome / strategy-ready claim",
        "- No production / paper / P08 / live readiness / shadow connection",
        "",
        "## Executor stance",
        "",
        "Executor offers no preference among Decisions 1-4. Each is a Referee policy choice about scope vs effort. Reporting facts only.",
    ]
    (REPORT_DIR / "d3_next_referee_decision_brief.md").write_text("\n".join(lines), encoding="utf-8")

    # Save triage data for audit trail
    with open(TRIAGE_DATA_DIR / "d3a_audit.json", "w", encoding="utf-8") as f:
        json.dump(d3a_audit, f, ensure_ascii=False, indent=2)
    with open(TRIAGE_DATA_DIR / "d3b_classifications.json", "w", encoding="utf-8") as f:
        json.dump(d3b_classifications, f, ensure_ascii=False, indent=2)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TRIAGE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading samples...")
    d1_df = pd.read_csv(D1_SAMPLES); d1_df["phase"] = "D1"
    d2_df = pd.read_csv(D2_SAMPLES) if D2_SAMPLES.exists() else pd.DataFrame()
    if "phase" not in d2_df.columns and len(d2_df) > 0:
        d2_df["phase"] = "D2"
    samples = pd.concat([d1_df, d2_df], ignore_index=True)
    samples["rcept_no"] = samples["rcept_no"].astype(str)
    samples = samples.drop_duplicates("rcept_no").reset_index(drop=True)
    samples["base_form_normalized"] = samples["report_nm"].astype(str).apply(strip_normalize)

    samples_d3a = samples[samples["base_form_normalized"].isin(D3A_BASE_FORMS)].copy()
    d3b_keys = [kw for kws in D3B_CATEGORIES.values() for kw in kws]
    samples_d3b = samples[samples["base_form_normalized"].apply(lambda x: any(k in (x or "") for k in d3b_keys))].copy()
    print(f"  D3a samples: {len(samples_d3a)}, D3b samples: {len(samples_d3b)}")

    print("Running D3a label audit...")
    d3a_audit = d3a_label_audit(samples_d3a)
    print(f"  D3a base forms audited: {len(d3a_audit)}")

    print("Running D3b feasibility triage...")
    d3b_classifications = d3b_triage(samples_d3b)
    for sc, rows in d3b_classifications.items():
        print(f"  {sc}: {len(rows)} rows classified")

    print("Writing reports...")
    write_reports(d3a_audit, d3b_classifications, samples_d3a, samples_d3b)
    print(f"Reports: {REPORT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
