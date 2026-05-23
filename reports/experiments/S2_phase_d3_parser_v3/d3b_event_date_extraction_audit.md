# D3b event_date Extraction Audit

Date: 2026-05-23 15:07:06

## Trajectory
- v1 D3b event_date: 0.0%
- v2 D3b event_date: 0.0%
- v3 D3b event_date: **0.0%**

## Fix
- Broadened D3b event_date keywords: 이사회결의일, 이사회 결의일, 결의일, 발행결의일, 결정일
- Conversion-request event_date keywords: 전환청구일, 청구일, 이사회결의일, 결의일
- effective_date kept separate: 납입일, 행사기간, 전환청구기간, 사채 만기일, 만기일, 주식상장일, 신주발행일, 신주교부일, 전환일
- NO rcept_date fallback used for event_date (Referee directive)

## Remaining limitation
- For 전환청구권행사 rows without explicit ACODE in body, parse falls back to GENERIC_CONVERSION_LABEL_MAP
- Some 전환청구권행사 disclosures store dates only in label text or free-form blocks not reached by table grid → manual_review_required

## Verification: 0.0% D3b event_date rate (still at 0 vs v2 0.0%)

## Compliance
- No rcept_date fallback used as event_date
- event_date and effective_date remain separate fields