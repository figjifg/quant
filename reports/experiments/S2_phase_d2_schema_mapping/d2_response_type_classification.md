# D2 Response Type Classification — Natural Finding

Date: 2026-05-23
Origin: D2 schema analysis of 104 XML samples (D1 41 + D2 63)

## Natural finding

OPENDART `document.xml` endpoint returns 2 distinct response formats. This was not anticipated in the master ticket and surfaced during D2 schema mapping. It impacts the D3 parser implementation strategy (form-based dispatch required).

## Response type counts (104 samples)

| Type | Count | Schema | Where |
|---|---|---|---|
| `dart_xml_structured` | 66 | DART3 (`dart3.xsd`) or DART4 (`dart4.xsd`) — `<DOCUMENT>` root, `<BODY>`, `<COVER>` or `<LIBRARY>` or `<SECTION>` containers, structured `<TABLE>`/`<TR>`/`<TD>` | All 주요사항보고서 series; 자기주식취득결과보고서; 전환사채발행결정; 회사합병/분할결정; 감자결정; 유무상증자결정 |
| `html_inline` | 38 | HTML page (no DART XSD) — `<html>` root, EUC-KR encoded, free CSS, inline `<table>` | 기타안내사항(안내공시) series (보호예수 만료); 기타시장안내 series (추가상장 안내, KOSDAQ 업종변경 등); 임원ㆍ주요주주특정증권등소유상황보고서; 자기주식취득/처분 결과보고서 (some); 철회신고서 (some) |

## D3 parser dispatch rule

```python
def parse_body(rcept_no: str, xml_bytes: bytes, report_nm: str) -> dict:
    head = xml_bytes[:500].decode('utf-8', errors='replace').lower()
    if '<html' in head:
        return parse_html_inline(xml_bytes, report_nm)
    elif '<document' in head and ('dart3.xsd' in head or 'dart4.xsd' in head):
        return parse_dart_xml(xml_bytes, report_nm)
    else:
        return {'parser_status': 'unrecognized_format', 'manual_review_required': True}
```

## Additional D3 parser requirements (revealed by D2)

1. **Charset detection**: DART3 XSD files vary in encoding (UTF-8 vs EUC-KR observed). Parser must detect `<?xml encoding="..."?>` header and decode accordingly.
2. **Schema version detection**: `dart3.xsd` and `dart4.xsd` have slightly different element names (e.g., `<DOCUMENT-HEADER>` vs none, `<COVER>` vs `<LIBRARY>`). Parser should handle both.
3. **HTML inline parser**: For `html_inline` type, BeautifulSoup (or lxml.html) is needed. The table structure is freer than DART XSD; field extraction relies on label text matching, not XPath.
4. **Form-name-based dispatch**: Even within `dart_xml_structured`, different `<DOCUMENT-NAME ACODE>` codes have different field layouts. Parser should dispatch on `(response_type, base_form, ACODE)` tuple.

## Implications for D3a / D3b / D3c readiness

| Wave | Affected response types | Implication |
|---|---|---|
| D3a (자사주) | dart_xml_structured (취득/처분/소각 결정), dart_xml_structured (결과보고서); some html_inline (결과보고서 일부) | D3a needs both XML and HTML parser branches |
| D3b (CB/BW + 전환청구) | dart_xml_structured for all observed cases | D3b is XML-only path |
| D3c (기타) | Heavily mixed: 유증/무증/감자/합병·분할 are XML; 추가상장/보호예수/임원보고서/철회 are mostly HTML or other | D3c needs strongest dispatch logic |

## Counts by event type (response type breakdown)

This breakdown is approximate (sampled from D1+D2 mapping):

| Event type | dart_xml_structured | html_inline | Notes |
|---|---|---|---|
| treasury_acquire | ~5 | 0 | main XML |
| treasury_dispose | ~5 | 0 | main XML |
| treasury_cancel | ~5 | 0 | 주식소각결정 = XML |
| treasury_*_result | ~5 | 5 | mix (결정 = XML, 결과보고서 may differ) |
| cb_issue, bw_issue | ~9 | 0 | main XML |
| conversion_request | ~5 | 0 | XML |
| rights_issue, bonus_issue | ~10 | 0 | XML |
| capital_reduction | ~5 | 0 | XML |
| merger_split | ~5 | 0 | XML |
| additional_listing | 0 | 3 | 기타시장안내 = HTML |
| lockup_release | 0 | 5 | 기타안내사항 = HTML |
| major_shareholder_sale | 0 | 5 | 임원·주요주주 = HTML |
| correction_withdrawal_cancel | mixed | mixed | 철회신고서 일부 HTML |
| kosdaq_general | mixed | mixed | various |

## Compliance with Referee D2 scope

- ✅ Schema mapping only — no parser implementation
- ✅ All response types classified, not silently ignored
- ✅ HTML parser is **design-only** in D2; implementation deferred to post-D2 Referee verdict
- ✅ No strategy testing, no return outcome
