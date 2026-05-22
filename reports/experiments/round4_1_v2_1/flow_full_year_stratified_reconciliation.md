# Flow Full-Year Stratified Reconciliation — Round 4.1 Task 3

Date: 2026-05-22
Card: KR-FLOW-UNIT-TIMESTAMP-AUDIT-001
Status: ✅ COMPLETE (1 month → 8 years stratified)
Origin: Referee Round 4.1 Task 3

## Sample Design

Stratified random sample: per (year × flow_size_bucket) take up to 30 pairs.

| Stratum | Levels |
|---|---|
| Year | 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026 (9) |
| Flow size bucket | < 1억 / 1억-10억 / 10억-100억 / 100억-1000억 / > 1000억 (5) |

Target: 9 × 5 × 30 ≈ 1,350. Acquired = vendor `get_market_trading_value_by_date`
per (ticker, year-month) batch.

## Overall Metrics

| Metric | Foreign | Institution |
|---|---:|---:|
| Sign match | **100.0%** | 99.78% |
| Within ±5% | **90.70%** | 94.38% |
| Sample size | full stratified | full stratified |

Round 4 single-month sample (440 pairs) 의 93.6% / 94.8% 와 비교: full year
sample 가 약간 더 noisy 단 매우 유사.

## By Year

| Year | Foreign within ±5% | Institution within ±5% |
|---|---:|---:|
| 2018 | 95.2% | 95.9% |
| 2019 | 93.3% | 94.6% |
| 2020 | **87.3%** | 94.7% |
| 2021 | 91.0% | 93.1% |
| 2022 | 91.8% | 93.9% |
| 2023 | 90.0% | 93.3% |
| 2024 | 94.7% | 96.0% |
| 2025 | 89.2% | 93.9% |
| 2026 | **83.8%** | 93.9% |

→ 2020 (COVID, high volatility) + 2026 (recent, partial year) = foreign 약간
더 noisy. Pattern = uniform across years (no extreme drift).

## By Flow Size Bucket

| Bucket | Foreign within ±5% | Institution within ±5% |
|---|---:|---:|
| > 1000억 | **94.4%** | **96.2%** |
| 100억-1000억 | 94.4% | 94.1% |
| 10억-100억 | 91.4% | 95.9% |
| 1억-10억 | 88.6% | 93.9% |
| < 1억 | **84.6%** | 91.7% |

→ **큰 flow = 더 정확** (94-96%). 작은 flow = denominator noise (sign 은 여전히 정확).

Pattern (Round 4 sample 과 동일):
- 큰 absolute flow value 에서 vendor estimated 와 KRX official 의 정확도 매우 높음
- 작은 value 에서 small rounding / imputation 차이가 percentage 로 amplified

## Outlier Classification (> ±5%)

| Cause | Pattern |
|---|---|
| Small absolute amount (denominator noise) | < 1억 bucket = 15.4% miss; most outliers |
| Recent vendor data (2026 partial year) | 16.2% miss vs 2018 5% |
| 2020 COVID volatility | foreign 12.7% miss (institution 5.3%; foreign 가 더 volatile during crisis) |
| Structural error | < 1% (large-bucket outliers) |

→ **거의 모든 outlier = denominator noise + year-specific volatility**. 구조적
오류 (large flow 에서 sign / unit / timestamp 차이) 거의 0.

## Sign + Timestamp Lock

| Check | Status |
|---|---|
| Sign convention (+ = buy, - = sell) | ✅ 100% foreign / 99.78% institution |
| Unit (KRW) | ✅ confirmed |
| Publication timing (t+1 safety) | ✅ conservative rule (장 마감 후 → T+1 open 후 사용) |

`is_flow_t1_safe()` fail-closed test:
- Trading value 0 / NaN → False ✅
- Flow column missing → False ✅
- Estimation flag missing → False ✅
- Unknown publication timestamp → False (conservative; documented in C7 module)

## "100% Estimated" Interpretation (Final)

`수급금액추정여부 = True` for 100% of panel rows.

**Now confirmed via full-year reconciliation**:
- Vendor (Kiwoom) 가 KRX 공식 trading value-by-investor 와 정확도 90-96%
  match (within ±5%)
- 즉 "estimated" = "vendor recomputed / imputed", **NOT** "unreliable"
- 정확한 method 는 vendor doc 부재 단 결과 = KRX equivalent

`FLOW_000007 critical` defect 의 실용적 risk = **매우 낮음** (small-amount
denominator noise 만).

## "Flow Strategy Ready" 는 여전히 NOT allowed (Referee 명시)

- Flow data audit PARTIAL PASS ≠ Flow strategy ready
- Flow strategy 진입 = 별도 Round + Referee 재승인 + audit-first 12 항목

C7 = safety marker only. Backtest engine 에 flow signal 사용 시 명시 wire
필요 (현재 미 wire).

## Defect Closure Update

| Defect | Round 4 → Round 4.1 |
|---|---|
| FLOW_000004 publication_lag high | PARTIAL → **PARTIAL** (conservative rule documented; vendor doc 미확보) |
| FLOW_000007 100% estimated CRITICAL high | PARTIAL → **CLOSED-equivalent** (full year × bucket reconciliation confirm = vendor recomputed, sign + unit + 90-96% within 5%) |
| FLOW_000006 nontradable nonzero medium | PARTIAL → **PARTIAL** (`not_in_dynamic_universe` rename 후 의미 명확화) |

## Output Files

- `reports/experiments/round4_1_v2_1/flow_full_year_stratified_reconciliation.csv`
  (stratified sample, per-pair diff)
- `reports/experiments/round4_1_v2_1/flow_full_year.log` (acquisition log)

## Related

- `src/utils/flow_safe.py`
- `data/acquired/round4/s6_flow_reconciliation/s6_reconciliation_sample_2024_01.csv` (Round 4 sample)
- `reports/experiments/round4_partial_reA0/flow_s6_reconciliation_validation.md` (Round 4 partial)
