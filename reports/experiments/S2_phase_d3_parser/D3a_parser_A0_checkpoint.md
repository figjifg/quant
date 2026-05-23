# D3a Treasury Parser A0 Checkpoint

Date: 2026-05-23 14:25:06
Origin: Referee narrowed staged D3 entry (Option e, 2026-05-23).

## Source coverage

- D3a samples (D1+D2 union): 36
- attachment_only excluded from denominator: 0
- parser denominator (non-attachment): 36

## Form coverage (D3a)

| Form | Count |
|---|---|
| 자기주식처분결과보고서 | 6 |
| 주식소각결정 | 5 |
| 자기주식취득결과보고서 | 5 |
| 주요사항보고서(자기주식처분결정) | 5 |
| 주요사항보고서(자기주식취득신탁계약체결결정) | 5 |
| 주요사항보고서(자기주식취득신탁계약해지결정) | 5 |
| 주요사항보고서(자기주식취득결정) | 4 |
| 자기주식취득결정 | 1 |

## Parse success

- parser_status = 'ok' (excluding attachment_only): 36 / 36 = 100.0%

## Field extraction rate (D3a denominator)

| Field | Rate |
|---|---|
| amount_krw | 5.6% |
| shares | 2.8% |
| event_date | 2.8% |
| effective_date | 2.8% |
| shares_before | 0.0% |
| shares_after | 0.0% |

## Parser confidence distribution (bucket 0.0-1.0)

```
{"0.0": 34, "0.6": 2}
```

## manual_review_required rate
- D3a: 100.0%

## PIT timestamp lock

- rcept_no = OPENDART receipt number (PIT)
- rcept_date = receipt date (= pit_available_at floor; intraday rcept_dt available in R000 source as `YYYYMMDD`)
- All D3a parsed rows carry rcept_no + rcept_date as PIT anchor (verified non-null in parser status CSV)

## Failure modes observed (D3a)

- attachment_only count: 0
- response_type=html_inline (within D3a samples): 9
- parser_exception count: 0

## C2/C3 readiness

- C2 (factor chain): D3a outputs are NOT yet wired into C2; this checkpoint is parser-only
- C3 (corp action day reclassification): D3a event_date + effective_date are populated where extractable; integration deferred

## Hard locks reaffirmed

- No strategy testing performed or recommended
- No return outcome calculated
- No parser output described as strategy-ready
- Attachment_only count tracked separately, NOT mixed into failure rate