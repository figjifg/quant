# D1 Source Coverage

Date: 2026-05-23
Scope: S2 D1 dry run, 50 disclosures small-scale

| Item | Value |
|---|---|
| Period (sample) | 2018-02-06 ~ 2026-03-17 |
| Universe source | KOSPI (R000 input parquet) |
| corp_cls in sample | ['Y(KOSPI source)'] |
| Total samples | 45 |
| Distinct report_nm | 29 |
| Event types covered | 9 / 10 |
| Source parquet | `research_input_data/inputs/events/opendart_kospi_disclosures_20180101_20260505.parquet` |
| Parquet total rows | 450,190 |

## Event types not covered in D1 dry run

Referee taxonomy 10 event types 중 D1 dry run sample 에 포함되지 않은 type:
- 추가상장 (R000 KOSPI 일반 disclosure 에 별도 form 없음 — KOSDAQ 또는 KRX 상장공시 별도 source 필요)
- 보호예수 해제 (R000 KOSPI 일반 disclosure 에 별도 form 없음 — 의무보유등 별도 source 필요)
- 대주주 매도 (R000 KOSPI 에 임원·주요주주특정증권등소유상황보고서 50,948건 존재 — D1 미포함, D2 부터)
- 정정/철회/취소 (D1 미포함, D2 부터)

D2 에서 위 4 type 도 form mapping 확장 필요.
