"""Unit tests for src/parsers/krx_status_html_inline.py."""
from __future__ import annotations

import io
import zipfile

import pytest

from src.parsers.krx_status_html_inline import (
    categorize_report,
    detect_body_format,
    extract_body_from_zip,
    find_date_range,
    find_first_date,
    find_label_hits,
    find_resumption_time,
    parse_disclosure,
)


def _make_zip(html: str, filename: str = "body.xml") -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, html.encode("utf-8"))
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Category labeling
# ---------------------------------------------------------------------------

def test_categorize_suspension():
    assert categorize_report("주권매매거래정지(불성실공시법인 지정)") == "suspension_related"


def test_categorize_resumption():
    assert categorize_report("주권매매거래정지 해제(불성실공시 지정 효력 발생)") == "resumption_related"


def test_categorize_delisting():
    assert categorize_report("상장폐지결정") == "delisting"


def test_categorize_liquidation():
    assert categorize_report("정리매매 개시") == "liquidation"


def test_categorize_other():
    assert categorize_report("기타 안내") == "other"


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

def test_find_first_date_delimited():
    iso, fmt, _, _ = find_first_date("매매거래정지일: 2024-05-22 사유")
    assert iso == "2024-05-22"
    assert fmt == "delimited"


def test_find_first_date_korean():
    iso, fmt, _, _ = find_first_date("매매거래정지일은 2024년 5월 22일이며")
    assert iso == "2024-05-22"
    assert fmt == "korean"


def test_find_first_date_invalid_returns_none():
    iso, _, _, _ = find_first_date("매매거래정지일 미정")
    assert iso is None


def test_find_date_range_delimited():
    s, e, fmt, _, _ = find_date_range("정지기간 2024-05-20 ~ 2024-05-22")
    assert s == "2024-05-20"
    assert e == "2024-05-22"
    assert fmt == "range_delimited"


def test_find_date_range_korean_buteo():
    s, e, fmt, _, _ = find_date_range("정지기간 2024년 5월 20일부터 5월 22일까지")
    assert s == "2024-05-20"
    assert e == "2024-05-22"
    assert fmt == "range_korean_buteo"


# ---------------------------------------------------------------------------
# Body extraction
# ---------------------------------------------------------------------------

def test_detect_body_format_html():
    assert detect_body_format("<html><body>foo</body></html>") == "html_inline"


def test_detect_body_format_xml_dart():
    assert detect_body_format("<?xml version='1.0'?><DOCUMENT>") == "structured_xml"


def test_extract_body_strips_html():
    z = _make_zip("<html><body><p>매매거래정지일: 2024-05-22</p></body></html>")
    b = extract_body_from_zip(z)
    assert b.body_format == "html_inline"
    assert "매매거래정지일: 2024-05-22" in b.text


def test_extract_body_unparseable():
    b = extract_body_from_zip(b"not-a-zip")
    assert b.body_format == "unparseable"


# ---------------------------------------------------------------------------
# Label scanning
# ---------------------------------------------------------------------------

def test_find_label_hits_suspension_period():
    hits = find_label_hits("매매거래정지기간: 2024-05-20 ~ 2024-05-22")
    assert any(h.kind == "suspension_period" and h.iso_date == "2024-05-20" for h in hits)


def test_find_label_hits_resumption():
    hits = find_label_hits("매매재개일: 2024년 5월 23일")
    assert any(h.kind == "resumption_date" and h.iso_date == "2024-05-23" for h in hits)


def test_find_label_hits_no_match():
    hits = find_label_hits("그냥 기타 내용")
    assert hits == []


def test_resumption_time_extraction():
    body = "매매재개일: 2024-05-23 09:00"
    t = find_resumption_time(body, "2024-05-23")
    assert t == "09:00"


# ---------------------------------------------------------------------------
# parse_disclosure end-to-end
# ---------------------------------------------------------------------------

def test_parse_suspension_with_period_range():
    html = """<html><body>
    <table><tr><td>매매거래정지기간</td><td>2024-05-20 ~ 2024-05-22</td></tr></table>
    </body></html>"""
    z = _make_zip(html)
    r = parse_disclosure(
        rcept_no="20240520123456",
        rcept_dt="20240520",
        stock_code="005930",
        corp_name="삼성전자",
        report_nm="주권매매거래정지(불성실공시법인 지정)",
        zip_bytes=z,
    )
    assert r.event_category == "suspension_related"
    assert r.parse_status == "extracted"
    assert r.parsed_suspension_start == "2024-05-20"
    assert r.parsed_suspension_end == "2024-05-22"
    assert r.parsed_effective_date == "2024-05-20"
    assert r.parser_confidence == "high"
    assert r.manual_review_required is False
    assert r.date_label_used == "매매거래정지기간"


def test_parse_resumption_korean_date():
    html = "<html><body><p>매매재개일은 2024년 5월 23일 09시 입니다.</p></body></html>"
    z = _make_zip(html)
    r = parse_disclosure(
        rcept_no="20240523111111",
        rcept_dt="20240522",
        stock_code="005930",
        corp_name="삼성전자",
        report_nm="주권매매거래정지 해제(불성실공시법인 지정 효력)",
        zip_bytes=z,
    )
    assert r.event_category == "resumption_related"
    assert r.parse_status == "extracted"
    assert r.parsed_resumption_date == "2024-05-23"
    assert r.parsed_resumption_time == "09:00"
    assert r.parser_confidence == "high"


def test_parse_delisting_is_out_of_scope():
    """Negative control: parser must NOT extract dates from delisting bodies."""
    html = "<html><body><p>매매거래정지일: 2024-05-22 상장폐지결정</p></body></html>"
    z = _make_zip(html)
    r = parse_disclosure(
        rcept_no="20240522999999",
        rcept_dt="20240522",
        stock_code="005930",
        corp_name="X",
        report_nm="상장폐지결정",
        zip_bytes=z,
    )
    assert r.event_category == "delisting"
    assert r.parse_status == "out_of_scope_category"
    assert r.parsed_effective_date is None
    assert r.parsed_suspension_start is None


def test_parse_correction_forces_manual_review():
    html = "<html><body><p>매매거래정지일 2024-05-22</p></body></html>"
    z = _make_zip(html)
    r = parse_disclosure(
        rcept_no="20240522888888",
        rcept_dt="20240522",
        stock_code="005930",
        corp_name="X",
        report_nm="[기재정정]주권매매거래정지(불성실공시법인 지정)",
        zip_bytes=z,
    )
    assert r.correction_flag is True
    assert r.parse_status == "extracted"
    assert r.manual_review_required is True


def test_parse_no_zip_bytes():
    r = parse_disclosure(
        rcept_no="x", rcept_dt="x", stock_code="x", corp_name="x",
        report_nm="주권매매거래정지", zip_bytes=None,
    )
    assert r.parse_status == "body_unavailable"
    assert r.manual_review_required is True


def test_parse_label_present_no_date():
    html = "<html><body><p>매매거래정지일 미정 추후 통보</p></body></html>"
    z = _make_zip(html)
    r = parse_disclosure(
        rcept_no="x", rcept_dt="x", stock_code="x", corp_name="x",
        report_nm="주권매매거래정지", zip_bytes=z,
    )
    assert r.parse_status == "label_no_value"
    assert r.parser_confidence == "medium"


def test_parse_structured_xml_out_of_scope():
    z = _make_zip("<?xml version='1.0'?><DOCUMENT><FOO/></DOCUMENT>")
    r = parse_disclosure(
        rcept_no="x", rcept_dt="x", stock_code="x", corp_name="x",
        report_nm="주권매매거래정지", zip_bytes=z,
    )
    assert r.parse_status == "out_of_scope_body_format"


def test_parse_managed_negative_control():
    html = "<html><body><p>매매거래정지일 2024-05-22</p></body></html>"
    z = _make_zip(html)
    r = parse_disclosure(
        rcept_no="x", rcept_dt="x", stock_code="x", corp_name="x",
        report_nm="관리종목지정", zip_bytes=z,
    )
    assert r.event_category == "managed"
    assert r.parse_status == "out_of_scope_category"
    assert r.parsed_effective_date is None
