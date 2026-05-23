# D3a Treasury Parser A0 Checkpoint (v2 — precision tuning)

Date: 2026-05-23 14:39:15
Origin: Referee Option (b) precision tuning round.

## Source coverage
- D3a samples: 36 | attachment_only: 0 | denominator: 36

## Form coverage (with ACODE)

| Base form | Count | ACODEs in sample |
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

## Field extraction rate (v2)
| Field | Rate |
|---|---|
| amount_krw | 27.8% |
| shares | 13.9% |
| event_date | 13.9% |
| effective_date | 2.8% |
| shares_before | 2.8% |
| shares_after | 0.0% |

## Parser confidence distribution (bucket)
```
{"0.0": 27, "0.4": 8, "1.0": 1}
```

## manual_review_required rate: 100.0%

## PIT timestamp lock
- rcept_no + rcept_date populated on all rows (verified)

## Failure modes
- attachment_only: 0
- response_type=html_inline: 9
- parser_exception: 0
- missing_xml: 0

## C2/C3 readiness: not yet wired

## Hard locks reaffirmed: no strategy, no return outcome, no parser-strategy-ready