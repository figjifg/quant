# D3a Treasury Parser A0 Checkpoint (v3 — 2nd precision tuning)

Date: 2026-05-23 15:07:06
Origin: Referee Option (b) 2nd, 2026-05-23.

## Source coverage
- D3a samples: 36 | attachment_only: 0 | denominator: 36

## Form coverage
| Form | Count | ACODEs |
|---|---|---|
| 자기주식처분결과보고서 | 6 | 00683 |
| 주식소각결정 | 5 | _n/a_ |
| 자기주식취득결과보고서 | 5 | 00681 |
| 주요사항보고서(자기주식처분결정) | 5 | 11333 |
| 주요사항보고서(자기주식취득신탁계약체결결정) | 5 | 11334 |
| 주요사항보고서(자기주식취득신탁계약해지결정) | 5 | 11335 |
| 주요사항보고서(자기주식취득결정) | 4 | 11332 |
| 자기주식취득결정 | 1 | _n/a_ |

## Parse success
- parser_status='ok': 36/36 = 100.0%

## Field extraction rate (v3)
| Field | Rate |
|---|---|
| amount_krw | 36.1% |
| shares | 13.9% |
| event_date | 13.9% |
| effective_date | 2.8% |
| shares_before | 2.8% |
| shares_after | 0.0% |

## Parser confidence
- mean: 0.185, max: 1.000

## manual_review_required: 100.0%

## PIT lock: 100% (rcept_no + rcept_date populated)

## Hard locks reaffirmed: no strategy / no return outcome / no parser-strategy-ready