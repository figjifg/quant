# D3b CB/BW + Conversion Parser A0 Checkpoint (v2 — precision tuning)

Date: 2026-05-23 14:39:15

## Source coverage
- D3b samples: 17 | attachment_only: 0 | denominator: 17

## Form coverage (with ACODE)
| Base form | Count | ACODEs |
|---|---|---|
| 주요사항보고서(전환사채권발행결정) | 6 | 11324 |
| 전환청구권행사 | 6 | _n/a_ |
| 주요사항보고서(신주인수권부사채권발행결정) | 5 | 11325 |

## Parse success
- parser_status='ok': 14/17 = 82.4%

## Field extraction rate (v2)
| Field | Rate |
|---|---|
| amount_krw | 23.5% |
| shares | 5.9% |
| conversion_price | 29.4% |
| event_date | 0.0% |
| effective_date | 5.9% |

## Series marker tracking: 2/17 rows with non-null series_marker

## manual_review_required rate: 100.0%

## Reset clause / conversion price adjustment
- Reset clauses are free-text in body; parser cannot auto-detect → flagged via manual_review

## PIT lock: rcept_no + rcept_date populated

## Failure modes
- attachment_only: 0
- html_inline within D3b: 6
- parser_exception: 0
- missing_xml: 3

## Hard locks reaffirmed: no strategy testing / strategy-ready language