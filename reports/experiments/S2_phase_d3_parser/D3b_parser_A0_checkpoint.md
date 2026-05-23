# D3b CB/BW + Conversion Parser A0 Checkpoint

Date: 2026-05-23 14:25:06

## Source coverage

- D3b samples (D1+D2 union): 17
- attachment_only excluded from denominator: 0
- parser denominator (non-attachment): 17

## Form coverage (D3b)

| Form | Count |
|---|---|
| 주요사항보고서(전환사채권발행결정) | 6 |
| 전환청구권행사 | 6 |
| 주요사항보고서(신주인수권부사채권발행결정) | 5 |

## Parse success

- parser_status = 'ok' (excluding attachment_only): 14 / 17 = 82.4%

## Field extraction rate (D3b denominator)

| Field | Rate |
|---|---|
| amount_krw | 0.0% |
| shares | 29.4% |
| conversion_price | 0.0% |
| event_date | 0.0% |
| effective_date | 0.0% |

## Series marker tracking
- rows with series_marker not null: 2 / 17
- series_marker missing on `전환청구권행사` without `(제N회차)` annotation → manual_review_required

## manual_review_required rate: 100.0%

## Reset clause / conversion price adjustment

- 전환가액 reset 조항은 본문 free-text 안에 위치, structured field 아님 → parser does not auto-detect; all CB/BW rows with conversion_price present are flagged for manual_review_required confirmation of reset clause presence

## PIT timestamp lock
- Same as D3a (rcept_no/rcept_date)

## Failure modes observed (D3b)
- attachment_only count: 0
- response_type=html_inline within D3b: 6
- parser_exception count: 0

## C2/C3 readiness
- Series marker linkage: design implemented in linkage smoke test; integration deferred

## Hard locks reaffirmed
- No strategy testing / return outcome / strategy-ready language