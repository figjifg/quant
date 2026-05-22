# Top100 Full-Period Reproducibility — Partial Re-A0

Card: KR-TOP100-PIT-LINEAGE-AUDIT-001
Round 4 Partial Re-A0 verdict candidate: **PARTIAL PASS** (full-period 99.78/100 avg, not 100/100)

## Sample → Full Comparison

| Coverage | Mean Match | Median | Min |
|---|---:|---:|---:|
| Round 3 (25 sample dates) | 100.0 / 100 | 100 | 100 |
| Round 4 (full 2,046 dates) | **99.78 / 100** | 100 | 97 |

→ Sample 가 너무 cherry-picked. Full-period 에서 **slight drift** 발견.

## Reproducibility Distribution (Full Period)

| Match level | Dates | % |
|---|---:|---:|
| 100/100 perfect | 1,654 | **80.84%** |
| ≥99/100 | 1,994 | **97.46%** |
| < 99/100 | 52 | 2.54% |
| Mean | 99.78 | — |
| Min | 97 | — |

## Imperfect Match Pattern

- 거의 모든 imperfect match = 99/100 (1 ticker discrepancy)
- 2018-01 첫 거래일부터 99/100 발생 = systematic 1-ticker drift
- 일부 dates = 97-98/100 (drift 더 큼)

## Possible Causes

1. **Selection rule = 단순 거래대금추정 top 100 ≠ exact rule**: vendor 가 추가 tie-break 또는 weight 사용 가능
2. **Universe 정의 차이**: KOSPI only vs KOSPI+KOSDAQ. vendor 가 KOSPI200 외 제외 종목 일부 있음
3. **Lookback adjustment**: 단순 당일 거래대금 vs MA 또는 rolling
4. **Tie-breaking**: 100번째 종목 tie 시 market cap, name alphabet 등

→ 단순 reverse-engineered rule = **99.78/100** 까지 reproducible. Full
exact rule 은 unknown (vendor proprietary).

## Trade Value Source

| Check | Result |
|---|---|
| `거래대금추정여부` True 비율 | **0.009%** (98 / 1,141,751) |
| → vendor estimated | 거의 0 (실제 값) |
| 거래대금 source | KRX 공식 trading value 와 같은 method 추정 (정확한 source = vendor doc 필요) |

vs reconstructed `close × volume`:
- 별도 검증 미실시 (sample vendor `거래대금추정` vs `close × volume` 비교 필요)
- Tentative: 매우 가까울 것 (KRX 공식 trading value = close × shares traded)

## 815 vs 833 Universe Count

| Universe | Count |
|---|---:|
| Panel 2018-2024 only | 815 |
| Panel 2018-2024 + 2025-2026 | 833 |
| **Difference** | **18** |

설명: 18 = 2025-2026 panel 에 추가된 새 ever-top100 ticker (신규 상장 또는
2025 처음 top100 진입).

## Survivor Safety (Re-validation)

- 833 unique panel tickers 모두 ever-top100 (= 한 번이라도 동적유니버스포함=True)
- 299 disappeared tickers 가 panel 에 보존됨 (= delisted 후에도 row 남음)
- Cross-confirmed with S3: 137/258 disappeared = S3 status events 있음 (suspension/delisting/managed)
- Cross-confirmed with S4: 833/833 = KRX master 안 (100% coverage)

→ **Survivor safety strong**. 단 일부 disappeared (47%) = merger/rename
별도 lineage 별도 source 필요.

## Daily Churn (Migration Strategy Warning)

| Metric | Value |
|---|---:|
| Mean new entries per day | 19.6 / 100 |
| Max new entries on single day | 34 |
| Days with >5 new entries | 1,720 / 1,721 |
| Days with >10 new entries | 1,706 / 1,721 |

→ Top100 membership 이 매우 noisy. **KR-LIQ-MIGRATION-001 의 signal-to-noise
ratio 가 spec 예상보다 낮음** 가능성 큼. Referee 명시: 향후 strategy review
시 strong Bear objection 유지.

이 daily churn = audit finding, not strategy evidence.

## Gate 5 Dependency Status

| Concern | Round 3 | Round 4 |
|---|---|---|
| Top100 = 거래대금 (= 거래량 × close) | close = raw, split day 왜곡 | C1 adjusted OHLC 통합 후도 trade_value 자체는 raw close 기반 |
| Split day false transition 가능성 | open | 35 잔존 extreme events 중 universe 안 = 1 only → 영향 거의 0 |

→ 실제 strategy impact = minimal. 단 정확한 close 조정 시 trade_value 재계산
필요는 별도 enhancement (Top100 universe 자체 변경 risk).

## Verdict (Allowed)

**PARTIAL PASS**.

Reasons:
- Selection rule reproducible (99.78/100 avg, 80.84% perfect, 97.46% ≥99/100)
- Survivor safety strong (3 카드 cross-confirmed)
- Trade value source = vendor (KRX-equivalent estimated, 99.99% non-estimated flag)

Blockers for FULL PASS:
- 99.78 ≠ 100 = 1 ticker discrepancy in 19% of dates
- Vendor exact rule (tie-break, KOSPI/KOSDAQ scope) 미확정
- Trade_value vs close×volume reconstruction 미비교

## Migration Strategy Warning (Registered)

**Daily churn 19.6 new entries / 100 = signal-to-noise ratio 매우 낮음**.

KR-LIQ-MIGRATION-001 의 hidden_momentum_check 외에도 churn-based base rate
warning 사전 등록. 향후 strategy 재개 시 strict Bear gate.

## Defect Closure Status

| Defect | Round 3 → Round 4 |
|---|---|
| TOP_000001 generation_script_missing medium | **CLOSED** (rule documented + 99.78/100 reproducible) |
| TOP_000002 reverse-engineered rule informational | already CLOSED |
| TOP_000003 membership reproducibility informational | **PARTIAL** (sample 100% → full 99.78/100) |
| TOP_000004 candidate universe low | **PARTIAL** (KRX master = 3,154 reference, but per-date all-listed query 별도) |
| TOP_000005 survivor universe informational | already CLOSED |
| TOP_000006 Gate 5 dependency high | **CLOSED** (C1 adjusted OHLC; trade_value re-calc은 별도 enhancement) |

## Related

- `data/processed/w001_v2/panel_with_adjusted_ohlc_2018_2026.csv`
- `data/acquired/round4/s4_listed_companies/krx_ever_listed_table.csv`
- `reports/experiments/round4_partial_reA0/top100_reproducibility_per_date.csv` (2,046 rows)
- `reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/audit_summary.md`
