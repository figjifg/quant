# S2 Source Coverage — Final

Date: 2026-05-23 15:42:46

## Acquisition phases

| Phase | Disclosures attempted | Successful download | Notes |
|---|---|---|---|
| D1 dry run | 45 (originally 50, treasury_cancel mapping 0) | 41 (91.1%) | 4 tiny-response API errors |
| D2 schema mapping | 63 | 63 (100%) | mapping corrected (treasury_cancel = 주식소각결정) + KOSDAQ via list.json |
| Total (D1+D2 union) | 108 unique rcept_no | ≈ 104 XML files | KOSPI source corp_cls='Y' from R000 + KOSDAQ corp_cls='K' from OPENDART list API |

## Period and universe

- Period: **2018-01-01 ~ 2026-05-22** (R000 inputs range)
- Universe: **KOSPI + KOSDAQ**
  - KOSPI: R000 input parquet `opendart_kospi_disclosures_20180101_20260505.parquet` (450,190 disclosures)
  - KOSDAQ: OPENDART list API `list.json?corp_cls=K` (20 samples acquired)

## OPENDART endpoint coverage

- `https://opendart.fss.or.kr/api/document.xml` — body XML download for individual rcept_no
- `https://opendart.fss.or.kr/api/list.json` — disclosure list filter (used for KOSDAQ acquisition)

## Response type distribution (104 XML files)

| Response type | Count | Note |
|---|---|---|
| dart_xml_structured | 66 | DART3 or DART4 XSD, `<DOCUMENT>` root, structured tables |
| html_inline | 38 | `<html>` root, EUC-KR encoded, free CSS tables |

## Hard locks reaffirmed

- No strategy testing was performed during acquisition
- No raw download data was used for strategy signal construction
- API key handled via BOM/CRLF-safe parser, length-only log