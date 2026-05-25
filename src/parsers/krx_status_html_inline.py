"""KRX exchange-status HTML-inline parser (suspension / resumption only).

Narrow parser per S2-HTML-INLINE-PARSER-REOPEN-PHASE Referee verdict 2026-05-25.

Scope:
- HTML-inline OPENDART/KRX exchange-status disclosures only.
- Categories: suspension_related + resumption_related ONLY.
- Target fields: effective_date, suspension_start, suspension_end,
  resumption_date, resumption_time.
- Out-of-scope categories return parse_status="out_of_scope".

Hard prohibitions:
- No strategy use. No execution simulation. No performance metric.
- No rcept_dt fallback to effective_date.
- No delisting / liquidation / managed / alert extraction.
- No correction linkage; correction rows forced to manual review.
"""
from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Iterable

try:
    from bs4 import BeautifulSoup  # type: ignore
except ImportError as e:
    raise ImportError("BeautifulSoup (bs4) is required") from e

PARSER_VERSION = "krx_status_html_inline-1.1.0"

# Categories the parser will extract from. Anything else = out_of_scope.
IN_SCOPE_CATEGORIES = {"suspension_related", "resumption_related"}

# Correction markers in report_nm.
CORRECTION_MARKER_RE = re.compile(r"\[기재정정\]|\[첨부정정\]|\[첨부추가\]|\[변경\]|\[정정\]")

# Period-change disclosure marker in report_nm (added in 1.1.0).
PERIOD_CHANGE_RE = re.compile(r"기간변경")

# Body markers that indicate the AFTER-change section in a period-change disclosure.
AFTER_CHANGE_MARKERS = ("변경후", "변경 후", "정정후", "정정 후", "변경된", "정정된")
BEFORE_CHANGE_MARKERS = ("변경전", "변경 전", "정정전", "정정 전", "당초")

# ---------------------------------------------------------------------------
# Category labeling — copied from manual-audit categorize_report for consistency
# ---------------------------------------------------------------------------

def categorize_report(report_nm: str) -> str:
    if not report_nm:
        return "other"
    r = str(report_nm)
    if "정지" in r and "거래" in r and "해제" not in r and "재개" not in r:
        return "suspension_related"
    if "해제" in r or "재개" in r:
        return "resumption_related"
    if "상장폐지" in r:
        return "delisting"
    if "관리종목" in r:
        return "managed"
    if "투자" in r and ("주의" in r or "경고" in r or "위험" in r):
        return "investment_alert"
    if "정리매매" in r:
        return "liquidation"
    if "단기과열" in r:
        return "short_term_overheated"
    return "other"


# ---------------------------------------------------------------------------
# Label inventory (from manual audit) — field_type tagging
# ---------------------------------------------------------------------------

SUSPENSION_START_LABELS = (
    "매매거래정지일",
    "거래정지일",
    "정지일",
    "매매거래정지 개시일",
    "매매거래정지개시일",
)
SUSPENSION_PERIOD_LABELS = (
    "매매거래정지기간",
    "거래정지기간",
    "정지기간",
)
RESUMPTION_LABELS = (
    "매매재개일",
    "거래재개일",
    "정지해제일",
    "해제일",
    "재개일",
    "해제예정일",
    "재개예정일",
)
EFFECTIVE_GENERIC_LABELS = (
    "효력발생일",
    "적용일",
    "지정일",
    "변경일",
)

ALL_LABEL_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("suspension_start", SUSPENSION_START_LABELS),
    ("suspension_period", SUSPENSION_PERIOD_LABELS),
    ("resumption_date", RESUMPTION_LABELS),
    ("effective_generic", EFFECTIVE_GENERIC_LABELS),
)

# Build a flat lookup label_text -> field_kind, preserving longest-match order.
FLAT_LABELS: list[tuple[str, str]] = []
for kind, labels in ALL_LABEL_GROUPS:
    for lbl in sorted(labels, key=len, reverse=True):
        FLAT_LABELS.append((lbl, kind))

# ---------------------------------------------------------------------------
# Date patterns
# ---------------------------------------------------------------------------

# 2024-05-22, 2024.05.22, 2024/05/22, 2024-5-2
_DATE_DELIMITED = r"(\d{4})\s*[-./]\s*(\d{1,2})\s*[-./]\s*(\d{1,2})"
# 2024년 5월 22일 / 2024년 05월 22일
_DATE_KOREAN = r"(\d{4})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일"
# 20240522 (8 digits)
_DATE_COMPACT = r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)"

DATE_PATTERNS = [
    (re.compile(_DATE_DELIMITED), "delimited"),
    (re.compile(_DATE_KOREAN), "korean"),
]

# Range: 2024-05-20 ~ 2024-05-22 / 2024-05-20 - 2024-05-22 / 2024.05.20∼2024.05.22
_RANGE_SEP = r"\s*[~∼\-－—]\s*"
DATE_RANGE_DELIMITED = re.compile(_DATE_DELIMITED + _RANGE_SEP + _DATE_DELIMITED)
DATE_RANGE_KOREAN = re.compile(_DATE_KOREAN + _RANGE_SEP + _DATE_KOREAN)
# Korean range "2024년 5월 20일부터 5월 22일까지"
DATE_RANGE_KOREAN_BUTEO = re.compile(
    _DATE_KOREAN + r"\s*부터\s*(?:(\d{4})\s*년)?\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일\s*까지"
)

# Time after date for resumption_time
TIME_RE = re.compile(r"(\d{1,2})\s*[:시]\s*(\d{1,2})?")

# ---------------------------------------------------------------------------
# Date utilities
# ---------------------------------------------------------------------------

def _normalize_ymd(y: int, m: int, d: int) -> str | None:
    try:
        return date(y, m, d).isoformat()
    except (ValueError, TypeError):
        return None


def find_first_date(text: str) -> tuple[str | None, str | None, int, int]:
    """Return (iso_date, format_used, start_pos, end_pos) for the FIRST date found."""
    best: tuple[str, str, int, int] | None = None
    for pat, fmt in DATE_PATTERNS:
        m = pat.search(text)
        if m:
            iso = _normalize_ymd(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            if iso and (best is None or m.start() < best[2]):
                best = (iso, fmt, m.start(), m.end())
    if best is None:
        return None, None, -1, -1
    return best


def find_date_range(text: str) -> tuple[str | None, str | None, str | None, int, int]:
    """Return (start_iso, end_iso, format, start_pos, end_pos) for first range."""
    m = DATE_RANGE_DELIMITED.search(text)
    if m:
        s = _normalize_ymd(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        e = _normalize_ymd(int(m.group(4)), int(m.group(5)), int(m.group(6)))
        if s and e:
            return s, e, "range_delimited", m.start(), m.end()
    m = DATE_RANGE_KOREAN.search(text)
    if m:
        s = _normalize_ymd(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        e = _normalize_ymd(int(m.group(4)), int(m.group(5)), int(m.group(6)))
        if s and e:
            return s, e, "range_korean", m.start(), m.end()
    m = DATE_RANGE_KOREAN_BUTEO.search(text)
    if m:
        sy, sm, sd = int(m.group(1)), int(m.group(2)), int(m.group(3))
        ey = int(m.group(4)) if m.group(4) else sy
        em, ed = int(m.group(5)), int(m.group(6))
        s = _normalize_ymd(sy, sm, sd)
        e = _normalize_ymd(ey, em, ed)
        if s and e:
            return s, e, "range_korean_buteo", m.start(), m.end()
    return None, None, None, -1, -1


# ---------------------------------------------------------------------------
# Body extraction
# ---------------------------------------------------------------------------

@dataclass
class BodyExtract:
    body_format: str  # html_inline / structured_xml / other / unparseable
    text: str
    n_documents: int


def detect_body_format(text: str) -> str:
    head = text[:500].upper()
    if "<HTML" in head or "<BODY" in head:
        return "html_inline"
    if "<DOCUMENT" in head or "<DART" in head:
        return "structured_xml"
    if "<?XML" in head:
        return "structured_xml"
    return "other"


def extract_body_from_zip(zip_bytes: bytes) -> BodyExtract:
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        return BodyExtract(body_format="unparseable", text="", n_documents=0)
    docs: list[tuple[str, str]] = []
    for name in zf.namelist():
        with zf.open(name) as f:
            content = f.read()
        text = ""
        for enc in ("utf-8", "euc-kr", "cp949", "utf-16"):
            try:
                text = content.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if text:
            docs.append((name, text))
    if not docs:
        return BodyExtract(body_format="unparseable", text="", n_documents=0)
    docs.sort(key=lambda d: -len(d[1]))
    primary = docs[0][1]
    fmt = detect_body_format(primary)
    if fmt == "html_inline":
        try:
            soup = BeautifulSoup(primary, "html.parser")
            plain = soup.get_text(separator=" ", strip=True)
        except Exception:
            plain = primary
    else:
        plain = primary
    return BodyExtract(body_format=fmt, text=plain, n_documents=len(docs))


# ---------------------------------------------------------------------------
# Label scanning over body text
# ---------------------------------------------------------------------------

@dataclass
class LabelHit:
    label: str
    kind: str  # suspension_start / suspension_period / resumption_date / effective_generic
    pos: int
    window: str
    iso_date: str | None = None
    iso_end_date: str | None = None
    value_kind: str = "none"  # single_date / date_range / no_value
    raw_text_window: str = ""


def _normalize_for_scan(text: str) -> str:
    # Replace 「：」, all whitespace runs, NBSP.
    text = text.replace(" ", " ").replace(" ", " ").replace("　", " ")
    text = text.replace("：", ":")
    text = re.sub(r"\s+", " ", text)
    return text


def find_label_hits(body_text: str, max_hits: int = 40) -> list[LabelHit]:
    """Find all label occurrences and the date evidence near each."""
    text = _normalize_for_scan(body_text)
    hits: list[LabelHit] = []
    # We scan label-by-label so that longer labels are tried first to avoid
    # substring shadowing (정지일 vs 매매거래정지일).
    consumed_positions: set[int] = set()
    for lbl, kind in FLAT_LABELS:
        start = 0
        while True:
            idx = text.find(lbl, start)
            if idx == -1:
                break
            # Skip if a longer label already covered this position.
            if any(abs(idx - p) < 2 for p in consumed_positions):
                start = idx + 1
                continue
            consumed_positions.add(idx)
            after = text[idx + len(lbl): idx + len(lbl) + 80]
            window_start = max(0, idx - 30)
            window_end = min(len(text), idx + len(lbl) + 100)
            window = text[window_start:window_end]
            hit = LabelHit(label=lbl, kind=kind, pos=idx, window=window,
                           raw_text_window=window[:160])
            # Range first
            s, e, fmt, _, _ = find_date_range(after)
            if s and e:
                hit.iso_date = s
                hit.iso_end_date = e
                hit.value_kind = "date_range"
            else:
                iso, fmt, _, _ = find_first_date(after)
                if iso:
                    hit.iso_date = iso
                    hit.value_kind = "single_date"
                else:
                    hit.value_kind = "no_value"
            hits.append(hit)
            start = idx + len(lbl)
            if len(hits) >= max_hits:
                return hits
    return hits


def select_after_change_period_hit(
    body_text: str, hits: list[LabelHit], by_kind: dict[str, list[LabelHit]]
) -> LabelHit | None:
    """For period_change_disclosure (기간변경) suspension events: choose the
    AFTER-change `정지기간` hit, not the (default) FIRST occurrence.

    Strategy:
    1. Locate `AFTER_CHANGE_MARKERS` positions in normalized body.
    2. Pick the suspension_period hit whose `pos` is AFTER the LAST after-change
       marker. If none qualifies, fall through to the LAST suspension_period
       hit (heuristic: after-change section typically appears later in body).
    3. If still nothing, fall back to first suspension_period / suspension_start.
    """
    if "suspension_period" not in by_kind and "suspension_start" not in by_kind:
        return None
    text = _normalize_for_scan(body_text)

    after_marker_positions: list[int] = []
    for marker in AFTER_CHANGE_MARKERS:
        start = 0
        while True:
            idx = text.find(marker, start)
            if idx == -1:
                break
            after_marker_positions.append(idx)
            start = idx + len(marker)

    period_hits = by_kind.get("suspension_period", []) + by_kind.get("suspension_start", [])

    if after_marker_positions:
        last_after = max(after_marker_positions)
        eligible = [h for h in period_hits if h.iso_date and h.pos > last_after]
        if eligible:
            eligible.sort(key=lambda h: h.pos)
            return eligible[0]

    valued = [h for h in period_hits if h.iso_date]
    if not valued:
        return None
    valued.sort(key=lambda h: h.pos)
    return valued[-1]  # last valued occurrence as fallback


def find_resumption_time(body_text: str, resumption_iso: str | None) -> str | None:
    """Look for HH:MM near the resumption_date label."""
    if not resumption_iso:
        return None
    text = _normalize_for_scan(body_text)
    # First locate the resumption date string then scan ±60 chars for HH:MM
    yyyy, mm, dd = resumption_iso.split("-")
    candidates = [
        f"{int(yyyy)}-{int(mm)}-{int(dd)}",
        f"{yyyy}-{mm}-{dd}",
        f"{yyyy}.{mm}.{dd}",
        f"{yyyy}년 {int(mm)}월 {int(dd)}일",
    ]
    for needle in candidates:
        idx = text.find(needle)
        if idx == -1:
            continue
        window = text[idx: idx + len(needle) + 60]
        m = TIME_RE.search(window)
        if m:
            hh = int(m.group(1))
            mi = int(m.group(2)) if m.group(2) else 0
            if 0 <= hh < 24 and 0 <= mi < 60:
                return f"{hh:02d}:{mi:02d}"
    return None


# ---------------------------------------------------------------------------
# Parse pipeline
# ---------------------------------------------------------------------------

@dataclass
class ParseResult:
    rcept_no: str = ""
    rcept_dt: str = ""
    stock_code: str = ""
    corp_name: str = ""
    report_nm: str = ""
    event_category: str = ""
    body_format: str = ""
    parsed_effective_date: str | None = None
    parsed_suspension_start: str | None = None
    parsed_suspension_end: str | None = None
    parsed_resumption_date: str | None = None
    parsed_resumption_time: str | None = None
    date_label_used: str = ""
    raw_text_window: str = ""
    parser_confidence: str = "low"
    manual_review_required: bool = True
    parse_status: str = "no_extraction"
    correction_flag: bool = False
    notes: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def parse_disclosure(
    *,
    rcept_no: str,
    rcept_dt: str,
    stock_code: str,
    corp_name: str,
    report_nm: str,
    zip_bytes: bytes | None,
) -> ParseResult:
    category = categorize_report(report_nm)
    correction = bool(CORRECTION_MARKER_RE.search(report_nm or ""))
    out = ParseResult(
        rcept_no=rcept_no,
        rcept_dt=rcept_dt,
        stock_code=stock_code,
        corp_name=corp_name,
        report_nm=report_nm,
        event_category=category,
        correction_flag=correction,
    )

    if zip_bytes is None:
        out.body_format = "missing"
        out.parse_status = "body_unavailable"
        out.notes = "no zip bytes provided"
        return out

    body = extract_body_from_zip(zip_bytes)
    out.body_format = body.body_format

    if body.body_format != "html_inline":
        # Out-of-scope body format for this parser
        out.parse_status = "out_of_scope_body_format"
        out.notes = f"body_format={body.body_format}"
        return out

    if category not in IN_SCOPE_CATEGORIES:
        # Negative-control / out-of-scope category — do NOT extract suspension/resumption
        out.parse_status = "out_of_scope_category"
        out.notes = f"event_category={category}"
        return out

    hits = find_label_hits(body.text)
    if not hits:
        out.parse_status = "no_label_match"
        out.parser_confidence = "low"
        out.notes = "no Korean date label matched"
        return out

    # Aggregate by kind (priority via in-scope category)
    by_kind: dict[str, list[LabelHit]] = {}
    for h in hits:
        by_kind.setdefault(h.kind, []).append(h)

    # Decide fields
    if category == "suspension_related":
        is_period_change = bool(PERIOD_CHANGE_RE.search(report_nm or ""))

        chosen = None
        if is_period_change:
            # 1.1.0 fix: for 기간변경 disclosures, select AFTER-change period hit.
            chosen = select_after_change_period_hit(body.text, hits, by_kind)
            if chosen:
                out.notes = "period_change_disclosure: after-change period selected"
        if not chosen:
            # Default: prefer suspension_period (range) → suspension_start → effective_generic
            for kind_pref in ("suspension_period", "suspension_start", "effective_generic"):
                for h in by_kind.get(kind_pref, []):
                    if h.iso_date:
                        chosen = h
                        break
                if chosen:
                    break
        if chosen:
            out.parsed_suspension_start = chosen.iso_date
            if chosen.iso_end_date:
                out.parsed_suspension_end = chosen.iso_end_date
            out.parsed_effective_date = chosen.iso_date
            out.date_label_used = chosen.label
            out.raw_text_window = chosen.raw_text_window
            if chosen.value_kind == "date_range":
                out.parser_confidence = "high"
            else:
                out.parser_confidence = "high"
            out.parse_status = "extracted"
            out.manual_review_required = correction
        else:
            # Labels found but no date — ambiguous
            out.parse_status = "label_no_value"
            out.parser_confidence = "medium"
            out.notes = "label(s) present without parseable date"
            sample_hit = hits[0]
            out.date_label_used = sample_hit.label
            out.raw_text_window = sample_hit.raw_text_window

    elif category == "resumption_related":
        # Prefer resumption_date → effective_generic
        chosen = None
        for kind_pref in ("resumption_date", "effective_generic"):
            for h in by_kind.get(kind_pref, []):
                if h.iso_date:
                    chosen = h
                    break
            if chosen:
                break
        if chosen:
            out.parsed_resumption_date = chosen.iso_date
            out.parsed_effective_date = chosen.iso_date
            out.date_label_used = chosen.label
            out.raw_text_window = chosen.raw_text_window
            out.parsed_resumption_time = find_resumption_time(body.text, chosen.iso_date)
            out.parser_confidence = "high"
            out.parse_status = "extracted"
            out.manual_review_required = correction
        else:
            out.parse_status = "label_no_value"
            out.parser_confidence = "medium"
            out.notes = "label(s) present without parseable date"
            sample_hit = hits[0]
            out.date_label_used = sample_hit.label
            out.raw_text_window = sample_hit.raw_text_window

    if correction:
        out.manual_review_required = True
        out.notes = ((out.notes + "; ") if out.notes else "") + "correction_flag forces manual review"

    return out
