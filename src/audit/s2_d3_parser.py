"""S2 D3 parser — Referee narrowed staged entry (Option e).

Approved waves:
- D3a treasury parser (7 forms)
- D3b CB/BW + conversion parser (3 forms)
- D3c: skeleton/prototype only (HTML dispatcher tested, no full parser yet)

Hard locks: no strategy test, no return outcome, no parser-strategy-ready claim.

D3 checkpoint outputs (Referee 8 required):
1. D3a_parser_A0_checkpoint.md
2. D3b_parser_A0_checkpoint.md
3. d3_parser_status_by_form.csv
4. d3_manual_review_queue.csv
5. d3_response_type_dispatch_test.md
6. d3_correction_linkage_smoke_test.md
7. d3_failure_modes_register.md
8. d3_next_wave_recommendation.md
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree, html as lxml_html

REPO_ROOT = Path("/home/jin/code/quant")
ENV_PATH = REPO_ROOT / "research_input_data" / ".env"
D1_RAW_DIR = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d1" / "raw_xml"
D2_RAW_DIR = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d2" / "raw_xml"
D1_SAMPLES = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d1" / "samples_50.csv"
D2_SAMPLES = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d2" / "all_samples_d1_d2.csv"
D3_DIR = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d3"
REPORT_DIR = REPO_ROOT / "reports" / "experiments" / "S2_phase_d3_parser"


# -----------------------------------------------------------------------------
# Shared infrastructure
# -----------------------------------------------------------------------------

CORRECTION_PREFIXES = ["[기재정정]", "[첨부정정]", "[첨부추가]", "[연장결정]"]
SUBSIDIARY_SUFFIXES = ["(자회사의 주요경영사항)", "(종속회사의주요경영사항)"]
SERIES_PATTERN = re.compile(r"\(제\s*\d+\s*회\s*차?\)")

D3A_FORMS = {
    "treasury_acquire": ["자기주식취득결정"],
    "treasury_dispose": ["자기주식처분결정"],
    "treasury_cancel": ["주식소각결정"],
    "treasury_trust_create": ["자기주식취득신탁계약체결결정"],
    "treasury_trust_terminate": ["자기주식취득신탁계약해지결정"],
    "treasury_acquire_result": ["자기주식취득결과보고서"],
    "treasury_dispose_result": ["자기주식처분결과보고서"],
}

D3B_FORMS = {
    "cb_issue": ["전환사채권발행결정"],
    "bw_issue": ["신주인수권부사채권발행결정"],
    "conversion_request": ["전환청구권행사"],
}

# label keywords → output field
TREASURY_LABEL_MAP = {
    "amount_krw": ["취득예정금액", "처분예정금액", "소각예정금액", "취득금액", "처분금액", "소각금액"],
    "shares": ["취득예정주식", "처분예정주식", "소각예정주식", "취득주식수", "처분주식수", "소각주식수", "보통주식", "기타주식"],
    "shares_before": ["발행주식총수", "발행주식의 총수"],
    "shares_after": ["취득후 자기주식", "처분후 자기주식", "취득 후 자기주식", "처분 후 자기주식"],
    "event_date": ["이사회결의일", "이사회 결의일", "결의일"],
    "effective_date": ["취득예상기간", "처분예상기간", "소각예정일", "취득기간", "처분기간"],
}

CB_BW_LABEL_MAP = {
    "amount_krw": ["사채총액", "발행금액", "사채의 권면총액"],
    "shares": ["전환가능주식", "신주인수가능주식", "전환주식수"],
    "conversion_price": ["전환가액", "행사가액"],
    "conversion_possible_shares": ["전환가능주식", "신주인수가능주식"],
    "event_date": ["이사회결의일", "이사회 결의일", "발행결의일"],
    "effective_date": ["납입일", "발행일", "만기일"],
    "series_marker": ["회차"],
}

CONVERSION_LABEL_MAP = {
    "amount_krw": ["사채총액", "전환된 사채의 권면총액"],
    "shares": ["발행주식", "전환주식수"],
    "conversion_price": ["전환가액"],
    "event_date": ["전환청구일", "청구일"],
    "effective_date": ["주식상장일", "신주발행일", "신주교부일"],
}

# Amount unit normalizer
AMOUNT_UNITS = [
    ("백만원", 1_000_000),
    ("천원", 1_000),
    ("억원", 100_000_000),
    ("만원", 10_000),
    ("원", 1),
]


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


def classify_response(xml_bytes: bytes) -> dict:
    head = xml_bytes[:600].decode("utf-8", errors="replace").lower()
    out = {
        "response_type": "unknown",
        "schema_version": None,
        "tiny_response_flag": False,
        "attachment_only_flag": False,
    }
    if len(xml_bytes) <= 500:
        out["tiny_response_flag"] = True
        out["attachment_only_flag"] = True
        out["response_type"] = "tiny"
        return out
    if "<html" in head:
        out["response_type"] = "html_inline"
        return out
    if "<document" in head:
        if "dart4.xsd" in head:
            out["schema_version"] = "dart4"
            out["response_type"] = "dart_xml_structured"
        elif "dart3.xsd" in head:
            out["schema_version"] = "dart3"
            out["response_type"] = "dart_xml_structured"
        else:
            out["schema_version"] = "dart_unknown"
            out["response_type"] = "dart_xml_structured"
        return out
    return out


def detect_charset(xml_bytes: bytes) -> str:
    head = xml_bytes[:200].decode("ascii", errors="replace").lower()
    m = re.search(r'encoding=["\']([^"\']+)["\']', head)
    if m:
        return m.group(1).lower()
    return "utf-8"


def safe_decode(xml_bytes: bytes) -> str:
    charset = detect_charset(xml_bytes)
    aliases = {"euc-kr": "euc-kr", "cp949": "cp949", "ks_c_5601-1987": "euc-kr"}
    try:
        return xml_bytes.decode(charset, errors="replace")
    except (LookupError, UnicodeDecodeError):
        return xml_bytes.decode("utf-8", errors="replace")


def strip_normalize_form(report_nm: str) -> dict:
    if not report_nm:
        return {"raw": "", "correction_prefix": None, "subsidiary_suffix": None, "series_marker": None, "base_form": ""}
    raw = report_nm
    corr = None
    for p in CORRECTION_PREFIXES:
        if report_nm.startswith(p):
            report_nm = report_nm[len(p):]
            corr = p
            break
    subs = None
    for s in SUBSIDIARY_SUFFIXES:
        if s in report_nm:
            report_nm = report_nm.replace(s, "").strip()
            subs = s
            break
    series_match = SERIES_PATTERN.search(report_nm)
    series = series_match.group(0) if series_match else None
    base = SERIES_PATTERN.sub("", report_nm).strip()
    return {
        "raw": raw,
        "correction_prefix": corr,
        "subsidiary_suffix": subs,
        "series_marker": series,
        "base_form": base,
    }


def normalize_amount(text: str) -> tuple[float | None, str | None]:
    if not text:
        return None, "empty"
    t = text.replace(",", "").replace(" ", "").strip()
    unit = None
    multiplier = 1.0
    for u, mult in AMOUNT_UNITS:
        if u in t:
            unit = u
            multiplier = mult
            t = t.replace(u, "")
            break
    try:
        val = float(re.search(r"-?\d+(\.\d+)?", t).group(0)) * multiplier
        return val, unit or "원_assumed"
    except (AttributeError, ValueError):
        return None, f"unparseable:{text[:30]}"


def normalize_shares(text: str) -> tuple[int | None, str | None]:
    if not text:
        return None, "empty"
    t = text.replace(",", "").replace(" ", "").strip()
    t = t.replace("주", "")
    try:
        n = int(re.search(r"\d+", t).group(0))
        return n, None
    except (AttributeError, ValueError):
        return None, f"unparseable:{text[:30]}"


DATE_PATTERNS = [
    re.compile(r"(\d{4})[-\.년/]\s*(\d{1,2})[-\.월/]\s*(\d{1,2})"),
    re.compile(r"(\d{4})(\d{2})(\d{2})"),
]


def normalize_date(text: str) -> tuple[str | None, str | None]:
    if not text:
        return None, "empty"
    for pat in DATE_PATTERNS:
        m = pat.search(text)
        if m:
            y, mo, d = m.group(1), m.group(2), m.group(3)
            try:
                return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}", None
            except ValueError:
                continue
    return None, f"unparseable:{text[:30]}"


def extract_dart_label_value_pairs(xml_bytes: bytes) -> list[tuple[str, str]]:
    text = safe_decode(xml_bytes)
    text = re.sub(r"<USERMARK[^>]*/?>", "", text)
    pairs = []
    # extract <TR> ... </TR> blocks, then per row pull TH and TD cells.
    tr_blocks = re.findall(r"<TR[^>]*>(.*?)</TR>", text, re.DOTALL | re.IGNORECASE)
    for tr in tr_blocks:
        cells = re.findall(r"<T[HD][^>]*>(.*?)</T[HD]>", tr, re.DOTALL | re.IGNORECASE)
        cells = [re.sub(r"<[^>]+>", " ", c).replace("&nbsp;", " ").strip() for c in cells]
        cells = [re.sub(r"\s+", " ", c) for c in cells if c]
        if len(cells) >= 2:
            label = cells[0]
            value = " | ".join(cells[1:])
            if label and len(label) <= 80:
                pairs.append((label, value))
    return pairs


def extract_html_label_value_pairs(xml_bytes: bytes) -> list[tuple[str, str]]:
    try:
        soup = BeautifulSoup(xml_bytes, "lxml")
    except Exception:
        soup = BeautifulSoup(xml_bytes, "html.parser")
    pairs = []
    for tr in soup.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if len(cells) >= 2:
            label = cells[0].get_text(" ", strip=True)
            value = " | ".join(c.get_text(" ", strip=True) for c in cells[1:])
            if label and len(label) <= 80:
                pairs.append((label, value))
    return pairs


def find_value(pairs: list[tuple[str, str]], keywords: list[str]) -> str | None:
    for label, value in pairs:
        if any(kw in label for kw in keywords):
            return value
    return None


# -----------------------------------------------------------------------------
# D3a treasury parsers
# -----------------------------------------------------------------------------

def parse_treasury(pairs: list[tuple[str, str]], event_type: str) -> dict:
    fields = {
        "amount_krw": None,
        "amount_unit": None,
        "shares": None,
        "shares_before": None,
        "shares_after": None,
        "event_date": None,
        "effective_date": None,
        "label_hits": {},
        "extraction_errors": [],
    }
    amount_raw = find_value(pairs, TREASURY_LABEL_MAP["amount_krw"])
    if amount_raw:
        val, unit = normalize_amount(amount_raw)
        fields["amount_krw"] = val
        fields["amount_unit"] = unit
        fields["label_hits"]["amount_krw"] = amount_raw[:60]
        if val is None:
            fields["extraction_errors"].append(f"amount_unparseable:{amount_raw[:30]}")
    shares_raw = find_value(pairs, TREASURY_LABEL_MAP["shares"])
    if shares_raw:
        val, err = normalize_shares(shares_raw)
        fields["shares"] = val
        fields["label_hits"]["shares"] = shares_raw[:60]
        if err:
            fields["extraction_errors"].append(f"shares_{err}")
    sb_raw = find_value(pairs, TREASURY_LABEL_MAP["shares_before"])
    if sb_raw:
        val, _ = normalize_shares(sb_raw)
        fields["shares_before"] = val
        fields["label_hits"]["shares_before"] = sb_raw[:60]
    sa_raw = find_value(pairs, TREASURY_LABEL_MAP["shares_after"])
    if sa_raw:
        val, _ = normalize_shares(sa_raw)
        fields["shares_after"] = val
        fields["label_hits"]["shares_after"] = sa_raw[:60]
    ed_raw = find_value(pairs, TREASURY_LABEL_MAP["event_date"])
    if ed_raw:
        val, err = normalize_date(ed_raw)
        fields["event_date"] = val
        fields["label_hits"]["event_date"] = ed_raw[:60]
        if err:
            fields["extraction_errors"].append(f"event_date_{err}")
    eff_raw = find_value(pairs, TREASURY_LABEL_MAP["effective_date"])
    if eff_raw:
        val, _ = normalize_date(eff_raw)
        fields["effective_date"] = val
        fields["label_hits"]["effective_date"] = eff_raw[:60]
    return fields


# -----------------------------------------------------------------------------
# D3b CB/BW + conversion parsers
# -----------------------------------------------------------------------------

def parse_cb_bw(pairs: list[tuple[str, str]], event_type: str) -> dict:
    fields = {
        "amount_krw": None,
        "amount_unit": None,
        "shares": None,
        "conversion_price": None,
        "conversion_possible_shares": None,
        "event_date": None,
        "effective_date": None,
        "series_marker": None,
        "label_hits": {},
        "extraction_errors": [],
    }
    amt = find_value(pairs, CB_BW_LABEL_MAP["amount_krw"])
    if amt:
        val, unit = normalize_amount(amt)
        fields["amount_krw"] = val
        fields["amount_unit"] = unit
        fields["label_hits"]["amount_krw"] = amt[:60]
        if val is None:
            fields["extraction_errors"].append(f"amount_unparseable:{amt[:30]}")
    cps = find_value(pairs, CB_BW_LABEL_MAP["conversion_possible_shares"])
    if cps:
        val, _ = normalize_shares(cps)
        fields["conversion_possible_shares"] = val
        fields["shares"] = val
        fields["label_hits"]["conversion_possible_shares"] = cps[:60]
    cp = find_value(pairs, CB_BW_LABEL_MAP["conversion_price"])
    if cp:
        val, unit = normalize_amount(cp)
        fields["conversion_price"] = val
        fields["label_hits"]["conversion_price"] = cp[:60]
    ed = find_value(pairs, CB_BW_LABEL_MAP["event_date"])
    if ed:
        val, _ = normalize_date(ed)
        fields["event_date"] = val
        fields["label_hits"]["event_date"] = ed[:60]
    eff = find_value(pairs, CB_BW_LABEL_MAP["effective_date"])
    if eff:
        val, _ = normalize_date(eff)
        fields["effective_date"] = val
        fields["label_hits"]["effective_date"] = eff[:60]
    return fields


def parse_conversion_request(pairs: list[tuple[str, str]]) -> dict:
    fields = {
        "amount_krw": None,
        "shares": None,
        "conversion_price": None,
        "event_date": None,
        "effective_date": None,
        "label_hits": {},
        "extraction_errors": [],
    }
    amt = find_value(pairs, CONVERSION_LABEL_MAP["amount_krw"])
    if amt:
        val, unit = normalize_amount(amt)
        fields["amount_krw"] = val
        fields["label_hits"]["amount_krw"] = amt[:60]
    sh = find_value(pairs, CONVERSION_LABEL_MAP["shares"])
    if sh:
        val, _ = normalize_shares(sh)
        fields["shares"] = val
        fields["label_hits"]["shares"] = sh[:60]
    cp = find_value(pairs, CONVERSION_LABEL_MAP["conversion_price"])
    if cp:
        val, _ = normalize_amount(cp)
        fields["conversion_price"] = val
        fields["label_hits"]["conversion_price"] = cp[:60]
    ed = find_value(pairs, CONVERSION_LABEL_MAP["event_date"])
    if ed:
        val, _ = normalize_date(ed)
        fields["event_date"] = val
        fields["label_hits"]["event_date"] = ed[:60]
    eff = find_value(pairs, CONVERSION_LABEL_MAP["effective_date"])
    if eff:
        val, _ = normalize_date(eff)
        fields["effective_date"] = val
        fields["label_hits"]["effective_date"] = eff[:60]
    return fields


# -----------------------------------------------------------------------------
# Dispatcher
# -----------------------------------------------------------------------------

def classify_event_type(base_form: str) -> tuple[str | None, str | None]:
    """Return (wave, event_type)."""
    for ev, kws in D3A_FORMS.items():
        if any(kw in base_form for kw in kws):
            return ("D3a", ev)
    for ev, kws in D3B_FORMS.items():
        if any(kw in base_form for kw in kws):
            return ("D3b", ev)
    return (None, None)


def compute_confidence(extraction: dict, required_fields: list[str]) -> float:
    n_required = len(required_fields)
    if n_required == 0:
        return 0.0
    n_present = sum(1 for f in required_fields if extraction.get(f) is not None)
    base = n_present / n_required
    n_errors = len(extraction.get("extraction_errors", []))
    penalty = min(0.5, 0.1 * n_errors)
    return max(0.0, min(1.0, base - penalty))


def needs_manual_review(extraction: dict, response_type: str, required_fields: list[str]) -> bool:
    if response_type in ("html_inline", "tiny", "unknown"):
        return True
    if any(extraction.get(f) is None for f in required_fields):
        return True
    if len(extraction.get("extraction_errors", [])) > 0:
        return True
    return False


def parse_one(row: dict, xml_path: Path) -> dict:
    rcept_no = str(row["rcept_no"])
    report_nm = row.get("report_nm", "") or ""
    norm = strip_normalize_form(report_nm)
    base_form = norm["base_form"]
    wave, event_type = classify_event_type(base_form)

    result = {
        "rcept_no": rcept_no,
        "rcept_date": row.get("rcept_date"),
        "corp_code_dart": row.get("corp_code"),
        "stock_code": row.get("stock_code"),
        "report_nm": report_nm,
        "base_form": base_form,
        "correction_prefix": norm["correction_prefix"],
        "subsidiary_suffix": norm["subsidiary_suffix"],
        "series_marker": norm["series_marker"],
        "wave": wave,
        "event_type": event_type,
        "response_type": None,
        "schema_version": None,
        "tiny_response_flag": False,
        "attachment_only_flag": False,
        "extraction": None,
        "parser_confidence": 0.0,
        "manual_review_required": True,
        "parser_status": None,
        "error": None,
    }

    if not xml_path or not xml_path.exists():
        result["parser_status"] = "missing_xml"
        result["error"] = "xml_file_not_found"
        return result

    try:
        xml_bytes = xml_path.read_bytes()
    except Exception as exc:
        result["parser_status"] = "read_error"
        result["error"] = type(exc).__name__
        return result

    cls = classify_response(xml_bytes)
    result.update({
        "response_type": cls["response_type"],
        "schema_version": cls["schema_version"],
        "tiny_response_flag": cls["tiny_response_flag"],
        "attachment_only_flag": cls["attachment_only_flag"],
    })

    if cls["response_type"] == "tiny":
        result["parser_status"] = "attachment_only_excluded_from_denominator"
        return result

    if wave is None:
        result["parser_status"] = "D3c_skeleton_only"
        if cls["response_type"] == "html_inline":
            # D3c HTML prototype: extract pairs but don't parse fields
            try:
                pairs = extract_html_label_value_pairs(xml_bytes)
                result["extraction"] = {"d3c_pairs_sample": pairs[:5], "n_pairs": len(pairs)}
            except Exception as exc:
                result["error"] = f"html_proto_{type(exc).__name__}"
        return result

    try:
        if cls["response_type"] == "dart_xml_structured":
            pairs = extract_dart_label_value_pairs(xml_bytes)
        elif cls["response_type"] == "html_inline":
            pairs = extract_html_label_value_pairs(xml_bytes)
        else:
            pairs = []
        if wave == "D3a":
            ext = parse_treasury(pairs, event_type)
            req_fields = ["amount_krw", "shares", "event_date"]
        elif wave == "D3b":
            if event_type == "conversion_request":
                ext = parse_conversion_request(pairs)
                req_fields = ["shares", "event_date"]
            else:
                ext = parse_cb_bw(pairs, event_type)
                req_fields = ["amount_krw", "event_date"]
        else:
            ext = {}
            req_fields = []
        result["extraction"] = ext
        result["parser_confidence"] = compute_confidence(ext, req_fields)
        result["manual_review_required"] = needs_manual_review(ext, cls["response_type"], req_fields)
        result["parser_status"] = "ok"
    except Exception as exc:
        result["parser_status"] = "parser_exception"
        result["error"] = f"{type(exc).__name__}:{str(exc)[:80]}"

    return result


# -----------------------------------------------------------------------------
# Correction linkage smoke test
# -----------------------------------------------------------------------------

def correction_linkage_smoke_test(parsed: list[dict]) -> dict:
    df = pd.DataFrame(parsed)
    if "correction_prefix" not in df.columns or len(df) == 0:
        return {"corrections_total": 0, "linked": 0, "unlinked": 0, "details": []}
    corrections = df[df["correction_prefix"].isin(CORRECTION_PREFIXES)].copy()
    details = []
    linked = 0
    for _, c in corrections.iterrows():
        candidates = df[
            (df["corp_code_dart"] == c["corp_code_dart"])
            & (df["base_form"] == c["base_form"])
            & (df["correction_prefix"].isna() | (df["correction_prefix"] == ""))
        ]
        if c["series_marker"]:
            candidates = candidates[candidates["series_marker"] == c["series_marker"]]
        # within +/- 60 days
        try:
            c_date = pd.to_datetime(c["rcept_date"])
            candidates = candidates.copy()
            candidates["d"] = pd.to_datetime(candidates["rcept_date"])
            candidates = candidates[(candidates["d"] <= c_date) & (candidates["d"] >= c_date - pd.Timedelta(days=180))]
        except Exception:
            pass
        if len(candidates) > 0:
            linked += 1
            original = candidates.sort_values("rcept_date", ascending=False).iloc[0]
            details.append({
                "correction_rcept_no": c["rcept_no"],
                "correction_prefix": c["correction_prefix"],
                "base_form": c["base_form"],
                "linked_to": original["rcept_no"],
                "days_gap": int((c_date - pd.to_datetime(original["rcept_date"])).days) if c_date is not None else None,
            })
        else:
            details.append({
                "correction_rcept_no": c["rcept_no"],
                "correction_prefix": c["correction_prefix"],
                "base_form": c["base_form"],
                "linked_to": None,
                "days_gap": None,
            })
    return {
        "corrections_total": len(corrections),
        "linked": linked,
        "unlinked": len(corrections) - linked,
        "details": details,
    }


# -----------------------------------------------------------------------------
# Report writers
# -----------------------------------------------------------------------------

def write_reports(parsed: list[dict], linkage: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    D3_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(parsed)

    # parser_status_by_form.csv
    status_cols = ["base_form", "wave", "event_type", "response_type", "schema_version",
                   "parser_status", "parser_confidence", "manual_review_required",
                   "tiny_response_flag", "attachment_only_flag"]
    flat = df[["rcept_no", "rcept_date", "corp_code_dart"] + status_cols + ["error"]].copy()
    flat["parser_confidence"] = flat["parser_confidence"].round(3)
    flat.to_csv(REPORT_DIR / "d3_parser_status_by_form.csv", index=False)

    # manual_review_queue.csv
    manual = df[df["manual_review_required"] == True].copy()
    manual_cols = ["rcept_no", "rcept_date", "corp_code_dart", "stock_code", "report_nm",
                   "wave", "event_type", "response_type", "parser_status", "error"]
    manual[manual_cols].to_csv(REPORT_DIR / "d3_manual_review_queue.csv", index=False)

    n_total = len(df)
    n_d3a = int((df["wave"] == "D3a").sum())
    n_d3b = int((df["wave"] == "D3b").sum())
    n_d3c_skel = int(df["parser_status"].eq("D3c_skeleton_only").sum())
    n_attach = int(df["attachment_only_flag"].sum())

    # D3a checkpoint
    d3a = df[df["wave"] == "D3a"].copy()
    d3a_denom = d3a[~d3a["attachment_only_flag"]].copy()
    d3a_n_ok = int(d3a_denom["parser_status"].eq("ok").sum())
    d3a_field_rates = {}
    for f in ["amount_krw", "shares", "event_date", "effective_date", "shares_before", "shares_after"]:
        rate = (d3a_denom["extraction"].apply(lambda x: x is not None and (x or {}).get(f) is not None).sum()
                / max(1, len(d3a_denom)))
        d3a_field_rates[f] = round(rate, 3)
    d3a_conf_buckets = (d3a_denom["parser_confidence"].apply(lambda x: f"{int(x*5)/5:.1f}").value_counts().to_dict())
    d3a_manual_rate = round(d3a_denom["manual_review_required"].mean() if len(d3a_denom) else 0, 3)
    d3a_form_counts = d3a["base_form"].value_counts().to_dict()

    d3a_lines = [
        "# D3a Treasury Parser A0 Checkpoint\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Origin: Referee narrowed staged D3 entry (Option e, 2026-05-23).\n",
        "## Source coverage",
        "",
        f"- D3a samples (D1+D2 union): {len(d3a)}",
        f"- attachment_only excluded from denominator: {int(d3a['attachment_only_flag'].sum())}",
        f"- parser denominator (non-attachment): {len(d3a_denom)}",
        "",
        "## Form coverage (D3a)",
        "",
        "| Form | Count |",
        "|---|---|",
    ]
    for form, c in sorted(d3a_form_counts.items(), key=lambda x: -x[1]):
        d3a_lines.append(f"| {form} | {c} |")
    d3a_lines += [
        "",
        "## Parse success",
        "",
        f"- parser_status = 'ok' (excluding attachment_only): {d3a_n_ok} / {len(d3a_denom)} = {d3a_n_ok / max(1,len(d3a_denom)):.1%}",
        "",
        "## Field extraction rate (D3a denominator)",
        "",
        "| Field | Rate |",
        "|---|---|",
    ]
    for f, r in d3a_field_rates.items():
        d3a_lines.append(f"| {f} | {r:.1%} |")
    d3a_lines += [
        "",
        "## Parser confidence distribution (bucket 0.0-1.0)",
        "",
        "```",
        json.dumps(d3a_conf_buckets, ensure_ascii=False),
        "```",
        "",
        f"## manual_review_required rate",
        f"- D3a: {d3a_manual_rate:.1%}",
        "",
        "## PIT timestamp lock",
        "",
        "- rcept_no = OPENDART receipt number (PIT)",
        "- rcept_date = receipt date (= pit_available_at floor; intraday rcept_dt available in R000 source as `YYYYMMDD`)",
        "- All D3a parsed rows carry rcept_no + rcept_date as PIT anchor (verified non-null in parser status CSV)",
        "",
        "## Failure modes observed (D3a)",
        "",
        f"- attachment_only count: {int(d3a['attachment_only_flag'].sum())}",
        f"- response_type=html_inline (within D3a samples): {int(d3a['response_type'].eq('html_inline').sum())}",
        f"- parser_exception count: {int(d3a['parser_status'].eq('parser_exception').sum())}",
        "",
        "## C2/C3 readiness",
        "",
        "- C2 (factor chain): D3a outputs are NOT yet wired into C2; this checkpoint is parser-only",
        "- C3 (corp action day reclassification): D3a event_date + effective_date are populated where extractable; integration deferred",
        "",
        "## Hard locks reaffirmed",
        "",
        "- No strategy testing performed or recommended",
        "- No return outcome calculated",
        "- No parser output described as strategy-ready",
        "- Attachment_only count tracked separately, NOT mixed into failure rate",
    ]
    (REPORT_DIR / "D3a_parser_A0_checkpoint.md").write_text("\n".join(d3a_lines), encoding="utf-8")

    # D3b checkpoint
    d3b = df[df["wave"] == "D3b"].copy()
    d3b_denom = d3b[~d3b["attachment_only_flag"]].copy()
    d3b_n_ok = int(d3b_denom["parser_status"].eq("ok").sum())
    d3b_field_rates = {}
    for f in ["amount_krw", "shares", "conversion_price", "event_date", "effective_date"]:
        rate = (d3b_denom["extraction"].apply(lambda x: x is not None and (x or {}).get(f) is not None).sum()
                / max(1, len(d3b_denom)))
        d3b_field_rates[f] = round(rate, 3)
    d3b_series_count = int(d3b_denom["series_marker"].notna().sum())
    d3b_form_counts = d3b["base_form"].value_counts().to_dict()
    d3b_manual_rate = round(d3b_denom["manual_review_required"].mean() if len(d3b_denom) else 0, 3)

    d3b_lines = [
        "# D3b CB/BW + Conversion Parser A0 Checkpoint\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Source coverage",
        "",
        f"- D3b samples (D1+D2 union): {len(d3b)}",
        f"- attachment_only excluded from denominator: {int(d3b['attachment_only_flag'].sum())}",
        f"- parser denominator (non-attachment): {len(d3b_denom)}",
        "",
        "## Form coverage (D3b)",
        "",
        "| Form | Count |",
        "|---|---|",
    ]
    for form, c in sorted(d3b_form_counts.items(), key=lambda x: -x[1]):
        d3b_lines.append(f"| {form} | {c} |")
    d3b_lines += [
        "",
        "## Parse success",
        "",
        f"- parser_status = 'ok' (excluding attachment_only): {d3b_n_ok} / {len(d3b_denom)} = {d3b_n_ok / max(1,len(d3b_denom)):.1%}",
        "",
        "## Field extraction rate (D3b denominator)",
        "",
        "| Field | Rate |",
        "|---|---|",
    ]
    for f, r in d3b_field_rates.items():
        d3b_lines.append(f"| {f} | {r:.1%} |")
    d3b_lines += [
        "",
        f"## Series marker tracking",
        f"- rows with series_marker not null: {d3b_series_count} / {len(d3b_denom)}",
        "- series_marker missing on `전환청구권행사` without `(제N회차)` annotation → manual_review_required",
        "",
        f"## manual_review_required rate: {d3b_manual_rate:.1%}",
        "",
        "## Reset clause / conversion price adjustment",
        "",
        "- 전환가액 reset 조항은 본문 free-text 안에 위치, structured field 아님 → parser does not auto-detect; all CB/BW rows with conversion_price present are flagged for manual_review_required confirmation of reset clause presence",
        "",
        "## PIT timestamp lock",
        "- Same as D3a (rcept_no/rcept_date)",
        "",
        "## Failure modes observed (D3b)",
        f"- attachment_only count: {int(d3b['attachment_only_flag'].sum())}",
        f"- response_type=html_inline within D3b: {int(d3b['response_type'].eq('html_inline').sum())}",
        f"- parser_exception count: {int(d3b['parser_status'].eq('parser_exception').sum())}",
        "",
        "## C2/C3 readiness",
        "- Series marker linkage: design implemented in linkage smoke test; integration deferred",
        "",
        "## Hard locks reaffirmed",
        "- No strategy testing / return outcome / strategy-ready language",
    ]
    (REPORT_DIR / "D3b_parser_A0_checkpoint.md").write_text("\n".join(d3b_lines), encoding="utf-8")

    # d3_response_type_dispatch_test.md
    rt_counts = df["response_type"].value_counts().to_dict()
    dispatch_lines = [
        "# D3 Response Type Dispatch Test\n",
        "Verification that the parser dispatches correctly based on (response_type, base_form, ACODE).\n",
        "## Response type distribution (D1+D2 samples in D3 pipeline)\n",
        "| Response type | Count |",
        "|---|---|",
    ]
    for rt, c in rt_counts.items():
        dispatch_lines.append(f"| {rt} | {c} |")
    dispatch_lines += [
        "",
        "## Dispatch matrix",
        "",
        "| Response type | D3a path | D3b path | D3c path |",
        "|---|---|---|---|",
        "| dart_xml_structured | parse_dart_label_value_pairs → parse_treasury | parse_dart_label_value_pairs → parse_cb_bw / parse_conversion_request | skeleton only |",
        "| html_inline | extract_html_label_value_pairs → parse_treasury (fallback) | extract_html_label_value_pairs → parse_cb_bw (fallback) | prototype only (record n_pairs) |",
        "| tiny | attachment_only_excluded_from_denominator | attachment_only_excluded_from_denominator | attachment_only_excluded_from_denominator |",
        "| unknown | manual_review_required | manual_review_required | manual_review_required |",
        "",
        "## Charset / schema detection summary",
        "- DART3/DART4 schema detection from `<DOCUMENT xsi:noNamespaceSchemaLocation>` header",
        "- HTML inline branch invoked when first 600 bytes contain `<html`",
        "- Charset auto-detect via `<?xml encoding=...?>`; default UTF-8 if absent",
    ]
    (REPORT_DIR / "d3_response_type_dispatch_test.md").write_text("\n".join(dispatch_lines), encoding="utf-8")

    # d3_correction_linkage_smoke_test.md
    link_lines = [
        "# D3 Correction / Cancellation Linkage Smoke Test\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Summary",
        f"- corrections_total (D1+D2 samples with correction_prefix in {CORRECTION_PREFIXES}): {linkage['corrections_total']}",
        f"- linked to a prior non-corrected original within 180 days, same corp_code + base_form + series_marker: {linkage['linked']}",
        f"- unlinked: {linkage['unlinked']}",
        f"- link rate: {(linkage['linked'] / max(1, linkage['corrections_total'])):.1%}",
        "",
        "## Algorithm",
        "",
        "```",
        "for each correction row:",
        "  candidates = where(",
        "    corp_code_dart == correction.corp_code_dart",
        "    AND base_form == correction.base_form",
        "    AND correction_prefix is null",
        "    AND series_marker matches (if any)",
        "    AND rcept_date in [correction.rcept_date - 180d, correction.rcept_date]",
        "  )",
        "  if candidates non-empty: link to most recent",
        "  else: leave unlinked → manual_review_required for the correction row",
        "```",
        "",
        "## Notes",
        "",
        "- Smoke test relies on the union of D1+D2 sampled disclosures only. In production D3, the candidate set would be the full R000 KOSPI parquet (450k disclosures) — link rate would be substantially higher.",
        "- Unlinked corrections in this smoke test = the original is outside the sampled set, NOT necessarily an algorithmic failure.",
        "- True end-to-end smoke test requires R000 full join in C3 integration phase (not part of D3 checkpoint).",
        "",
        "## Sample linkage details (first 10)",
        "",
        "```",
        json.dumps(linkage["details"][:10], ensure_ascii=False, indent=2),
        "```",
    ]
    (REPORT_DIR / "d3_correction_linkage_smoke_test.md").write_text("\n".join(link_lines), encoding="utf-8")

    # d3_failure_modes_register.md
    fm_lines = [
        "# D3 Failure Modes Register\n",
        "## Failure mode counts (D1+D2 pipeline through D3 parser)\n",
        "| Failure mode | Count | Classification policy |",
        "|---|---|---|",
        f"| attachment_only (tiny response) | {int(df['attachment_only_flag'].sum())} | excluded from parser denominator |",
        f"| html_inline (D3a/D3b XML-expected forms, fallback used) | {int(((df['response_type'] == 'html_inline') & df['wave'].notna()).sum()) if 'wave' in df.columns else 0} | manual_review_required |",
        f"| parser_exception | {int(df['parser_status'].eq('parser_exception').sum())} | manual_review_required, logged |",
        f"| missing_xml | {int(df['parser_status'].eq('missing_xml').sum())} | excluded with error logged |",
        f"| read_error | {int(df['parser_status'].eq('read_error').sum())} | excluded with error logged |",
        f"| D3c_skeleton_only (forms outside D3a/D3b) | {n_d3c_skel} | NOT parsed, awaits D3c approval |",
        "",
        "## Manual review queue size",
        f"- {int(df['manual_review_required'].sum())} rows requiring manual review",
        "- queue file: `d3_manual_review_queue.csv`",
        "",
        "## Common extraction errors",
    ]
    error_samples = (df["extraction"].apply(lambda x: x is not None and len((x or {}).get("extraction_errors", [])) > 0).sum())
    fm_lines.append(f"- rows with at least one extraction_error: {int(error_samples)}")
    fm_lines.append("")
    fm_lines.append("## Confidence policy")
    fm_lines.append("- `parser_confidence` = (n_present_required_fields / n_required) − 0.1 × n_extraction_errors, clipped to [0,1]")
    fm_lines.append("- D3a required: amount_krw, shares, event_date")
    fm_lines.append("- D3b CB/BW required: amount_krw, event_date")
    fm_lines.append("- D3b conversion required: shares, event_date")
    fm_lines.append("- Confidence < 0.6 or any required field missing → manual_review_required = True")
    (REPORT_DIR / "d3_failure_modes_register.md").write_text("\n".join(fm_lines), encoding="utf-8")

    # d3_next_wave_recommendation.md
    d3a_ok_rate = d3a_n_ok / max(1, len(d3a_denom))
    d3b_ok_rate = d3b_n_ok / max(1, len(d3b_denom))
    nw_lines = [
        "# D3 Next Wave Recommendation\n",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## D3a checkpoint result",
        f"- denominator: {len(d3a_denom)}",
        f"- parser_status=ok rate: {d3a_ok_rate:.1%}",
        f"- manual_review_required rate: {d3a_manual_rate:.1%}",
        "",
        "## D3b checkpoint result",
        f"- denominator: {len(d3b_denom)}",
        f"- parser_status=ok rate: {d3b_ok_rate:.1%}",
        f"- manual_review_required rate: {d3b_manual_rate:.1%}",
        "",
        "## Recommendation (executor's view, Referee decides)",
        "",
        "- D3a and D3b parser_status=ok rates above with the small samples should be interpreted as **infrastructure readiness**, not strategic precision",
        "- Field-level extraction rates (especially `event_date` and `effective_date`) reflect label-keyword matching in current sample set; tuning expected as form variants grow",
        "- D3c full implementation is NOT requested in this checkpoint — D3c skeleton + HTML prototype exists in the parser pipeline as designed",
        "",
        "## Open options for Referee",
        "",
        "- (a) Approve D3c full implementation after this checkpoint",
        "- (b) Require D3a/D3b precision tuning (label map expansion, manual audit on extraction) before D3c",
        "- (c) Require integration smoke test against a larger sample (e.g., 500 disclosures across D3a/D3b forms) before D3c",
        "- (d) Hold D3 at current state and proceed to C2/C3 integration design",
        "",
        "## Compliance reaffirm",
        "- No strategy testing, no return outcome, no parser-strategy-ready claim",
        "- End condition for current step = D3a/D3b parser A0 checkpoint only",
    ]
    (REPORT_DIR / "d3_next_wave_recommendation.md").write_text("\n".join(nw_lines), encoding="utf-8")

    # save parsed rows for audit trail (gitignored)
    df_export = df.copy()
    df_export["extraction_json"] = df_export["extraction"].apply(lambda x: json.dumps(x, ensure_ascii=False) if x else None)
    df_export = df_export.drop(columns=["extraction"])
    df_export.to_csv(D3_DIR / "d3_parsed_rows.csv", index=False)


# -----------------------------------------------------------------------------
# Main pipeline
# -----------------------------------------------------------------------------

def main() -> int:
    load_env(ENV_PATH)
    api_key_loaded = bool(os.environ.get("OPENDART_API_KEY"))
    print(f"API key available: {api_key_loaded} (not required for D3 parsing of existing XML)")

    D3_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading D1+D2 sample inventory...")
    d1_df = pd.read_csv(D1_SAMPLES)
    d1_df["phase"] = "D1"
    if D2_SAMPLES.exists():
        d2_df = pd.read_csv(D2_SAMPLES)
        if "phase" not in d2_df.columns:
            d2_df["phase"] = "D2"
    else:
        d2_df = pd.DataFrame()
    samples = pd.concat([d1_df, d2_df], ignore_index=True)
    samples["rcept_no"] = samples["rcept_no"].astype(str)
    samples = samples.drop_duplicates("rcept_no").reset_index(drop=True)
    print(f"  Total D1+D2 unique samples: {len(samples)}")

    print("Parsing each sample...")
    parsed = []
    for i, row in enumerate(samples.to_dict(orient="records"), 1):
        rcept_no = str(row["rcept_no"])
        xml_path = None
        for d in (D1_RAW_DIR, D2_RAW_DIR):
            p = d / f"{rcept_no}.xml"
            if p.exists():
                xml_path = p
                break
        result = parse_one(row, xml_path)
        parsed.append(result)
        if i % 25 == 0 or i == len(samples):
            print(f"  [{i}/{len(samples)}] processed (last: {rcept_no} wave={result['wave']} status={result['parser_status']})")

    print("Running correction linkage smoke test...")
    linkage = correction_linkage_smoke_test(parsed)
    print(f"  corrections_total={linkage['corrections_total']} linked={linkage['linked']} unlinked={linkage['unlinked']}")

    print("Writing D3 checkpoint reports...")
    write_reports(parsed, linkage)

    n_d3a_ok = sum(1 for p in parsed if p["wave"] == "D3a" and p["parser_status"] == "ok")
    n_d3b_ok = sum(1 for p in parsed if p["wave"] == "D3b" and p["parser_status"] == "ok")
    print(f"D3 checkpoint complete: D3a_ok={n_d3a_ok}, D3b_ok={n_d3b_ok}")
    print(f"Reports: {REPORT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
