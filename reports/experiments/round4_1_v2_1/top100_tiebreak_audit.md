# Top100 Tie-Break Residual Audit — Round 4.1 Task 4

Date: 2026-05-22
Card: KR-TOP100-PIT-LINEAGE-AUDIT-001
Status: ✅ COMPLETE (tie-break + boundary residual 분석)
Origin: Referee Round 4.1 Task 4
Output ledger: `top100_tiebreak_residual_ledger.csv` (894 rows)

## Mismatch Summary

Round 4 result: 99.78/100 mean match across 2,046 full-period dates.

Mismatch totals:
- **391 dates with mismatch** (= 19.1% of 2,046)
- **894 mismatch records total** (447 each direction)
- Mean mismatch tv_rank: 80 (= near top-100 boundary)
- 75% percentile tv_rank: 101 (= exact boundary)
- **54% of mismatches at rank 95-110** (boundary zone)

## Tie-Break Pattern Analysis

### Frequent mismatchers (Top 10)

| Ticker | Name | Mismatch count |
|---|---|---:|
| 108320 | LX세미콘 | 139 |
| 003670 | 포스코켐텍 | 95 |
| 036420 | 제이콘텐트리 | 55 |
| 090460 | 비에이치 | 53 |
| 068270 | 셀트리온 | 28 |
| 097520 | 엠씨넥스 | 25 |
| 066970 | 엘앤에프 | 19 |
| 004020 | 현대제철 | 10 |
| 100090 | 삼강엠앤티 | 10 |
| 178920 | PI첨단소재 | 8 |

→ 일부 frequent mismatchers (LX세미콘 139 events) = systematic vendor rule
difference. 일반적으로 vendor 가 추가 rule (KOSPI200 강제 포함, market cap
weight 등) 적용 가능성.

### Cause Categories

| Cause | Count | % |
|---|---:|---:|
| Boundary tie (rank 95-110) | 483 | 54.0% |
| Off-boundary mismatch | 411 | 46.0% |

**54% boundary** = 단순 tie-break rule 차이 (vendor 의 tie-break 가 자체
ranking 과 약간 다름):
- Vendor 가 거래대금 동률 시 ticker 알파벳 / market cap / 다른 기준 사용 가능
- 단순 reverse-engineered rule = `sort by 거래대금 desc, then 종목코드 asc`

**46% off-boundary** = systematic rule difference:
- Vendor 가 단순 거래대금 top 100 이 아닌 weighted / smoothed / KOSPI200
  inclusion 등 사용 가능
- 일부 special-case ticker (LX세미콘 등) 가 vendor 의 special handling

## Tie-Break Candidate Test (informal)

가정한 tie-break:
1. `sort by 거래대금 desc, 종목코드 asc` (current)
2. `sort by 거래대금 desc, 시가총액 desc` (alternative)
3. `sort by 거래대금 desc, market (KOSPI > KOSDAQ)` (alternative)

각 가정으로 sample dates 재현해도 99.78/100 보다 큰 개선 X (정확한 rule
unknown).

→ vendor rule = 단순 거래대금 top 100 + small additional smoothing/inclusion
rule (정확한 spec 미공개).

## Trade Value Source Confirmation

| Source | Status |
|---|---|
| `거래대금추정` field | 99.991% non-estimated (= 실제 값, 0.009% 가 vendor estimated) |
| Source = close × volume reconstructed? | **No** — separate field |
| Cross-reference with pykrx `get_market_ohlcv` volume × close | 미실시 (별도 enhancement) |

Tentative: `거래대금추정` = vendor 가 KRX 공식 trading_value 와 같은 method
계산. 단 vendor doc 부재.

## Universe Membership

- Panel 의 동적유니버스포함 universe = KOSPI + KOSDAQ 통합 top 100
- Round 4 finding 재확인: ~563 candidate tickers per date (= top 100 + ~463
  out-of-top100 candidate)

## Daily Churn Warning (Re-Lock)

| Metric | Value |
|---|---:|
| Mean new entries per day | **19.6 / 100** |
| Max new entries (single day) | 34 |
| Days with > 5 new entries | 1,720 / 1,721 |

→ Top100 membership 매우 noisy. KR-LIQ-MIGRATION-001 의 strong Bear
objection 으로 보존 (Referee 명시).

## Strategy Impact Assessment

| Aspect | Impact |
|---|---|
| 99.78/100 mismatch | 0.22 ticker 차이 / 100 = strategy basket 의 0.22% |
| Boundary mismatch (54%) | 단순 swap (one ticker 차이) = negligible |
| Off-boundary (46%) | More structural 단 여전히 1 ticker 수준 |
| Daily churn 19.6/100 | strategy 의 ~20% basket 매일 교체 = matched control 필수 |

→ Strategy diagnostic 의 universe membership 정확성에는 영향 매우 작음.

## Maximum Verdict (Referee Round 4.1 lock)

**PARTIAL PASS** (exact tie-break 미확정 단 strong evidence base).

Improvement vs Round 4:
- 894 mismatch records full ledger
- Tie-break hypothesis tested (no exact rule recovered)
- Boundary vs off-boundary breakdown (54% / 46%)
- Top 10 systematic mismatcher list

## Defect Closure Update

| Defect | Round 4 → Round 4.1 |
|---|---|
| TOP_000003 reproducibility informational | PARTIAL → **PARTIAL** (894 records ledger 완성, vendor exact rule unknown) |
| TOP_000004 candidate universe low | PARTIAL → **PARTIAL** (panel ~563 candidate confirmed; full per-date all-listed query 별도) |

## Related

- `reports/experiments/round4_1_v2_1/top100_tiebreak_residual_ledger.csv`
- `reports/experiments/round4_partial_reA0/top100_full_period_reproducibility.md`
- `reports/experiments/round4_partial_reA0/top100_reproducibility_per_date.csv` (2,046 rows)
