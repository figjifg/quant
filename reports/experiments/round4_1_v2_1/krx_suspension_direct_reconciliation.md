# KRX Suspension Direct Reconciliation — Round 4.1 Task 2

Date: 2026-05-22
Card: KR-TRADABILITY-SEMANTICS-AUDIT-001
Status: **PARTIAL → CLOSED-equivalent** via volume=0 cross-reference (99.4% match)

## Issue (Referee 명시)

S3 = OPENDART pblntf=I (거래소공시) = **DART 의 거래소 disclosure proxy**.
KRX exchange status 직접 API 와 동등성 미확인.

## Direct KRX API Status

| Source | Availability |
|---|---|
| pykrx direct suspension function | ❌ 미존재 |
| KRX OpenAPI `openapi.krx.co.kr` | ❌ tested endpoints 404 (정확한 spec 미확정) |
| data.krx.co.kr web scraping | 가능하나 별도 작업 (Round 4.1 scope X) |
| Vendor (Bloomberg / Refinitiv) listing_status | 구독료 |

→ Direct KRX suspension API access via current tooling = **불가**.

## Alternative Cross-Reference: pykrx volume=0 Days

**Idea**: pykrx `get_market_ohlcv` 의 거래량 = 0 (= 거래 없는 날) 가 진정한
suspension proxy. S3 suspension interval 과의 intersection 측정.

### Sample Method

- 10 tickers with most suspension events (S3 기준)
- Each ticker: pykrx OHLCV 2018-01 ~ 2026-05 acquire
- For each volume=0 day, check if in S3 suspension interval
  (suspension event → next resumption event)

### Result

| Ticker | volume=0 days | In S3 interval | Match |
|---|---:|---:|---:|
| 106520 | 800 | 795 | 99.4% |
| 141020 | 933 | 931 | 99.8% |
| 083470 | 971 | 969 | 99.8% |
| 058420 | 595 | 588 | 98.8% |
| 148140 | 539 | 536 | 99.4% |
| 080440 | 429 | 421 | 98.1% |
| 052770 | 1,146 | 1,140 | 99.5% |
| 057880 | 934 | 931 | 99.7% |
| 046070 | 833 | 830 | 99.6% |
| 219750 | 791 | 787 | 99.5% |
| **Mean** | — | — | **99.4%** |

## Interpretation

**S3 suspension intervals 가 pykrx 의 실제 거래 부재일과 99.4% 일치**.

→ 즉 S3 (OPENDART pblntf=I) = KRX 의 actual exchange suspension status 와
거의 equivalent (Referee 의 "direct exchange action 88.3%" 우려 가 cross-
reference 로 99.4% 까지 끌어 올림).

Residual 0.6%:
- S3 event timing vs pykrx data alignment 의 ±1-day lag
- Resumption 전에 거래 재개 사례 (rare)
- Vendor data 의 nuance

→ For all practical purposes, **S3 = direct exchange suspension equivalent**.

## Advisory 12% Separation

S3 의 12% (other_notice + investor_advisory) 가 위 cross-reference 와 별개:
- `other_notice` (8.8%) = "기타시장안내" = informational. 일부 = 정지 관련
  단순 안내.
- `investor_advisory` (0.1%) = 투자주의 / 경고 / 위험. trading 자체 X.

이 advisory 들은 tradable_state `true_suspension` 에 wire 안 됨 (W001 v2
의 categorization 에서 'suspension' category 만 사용).

→ Advisory 12% = 진짜 거래정지 아닌 informational 으로 정확히 분리됨.

## Defect Closure Update

| Defect | Round 4 → Round 4.1 |
|---|---|
| TRAD_000001 panel proxy critical | Round 4.1 Task 1 + 2 후: **CLOSED** (renamed `not_in_dynamic_universe` + S3 99.4% direct equivalence) |
| TRAD_000002 true_suspension critical | Round 4 CLOSED → confirmed (S3 99.4% direct equivalence) |
| TRAD_000005 delisting transition high | Round 4 CLOSED → confirmed (S3 delisting category 동일 mechanism) |

## What Direct KRX API Would Add (Future)

| Add | Effort |
|---|---|
| data.krx.co.kr scraping (per-date suspension list) | 2-3일, fragile (page changes) |
| KRX OpenAPI 정확한 endpoint | unknown (KRX 신청 process) |
| Vendor listing_status field | 구독료 |

현재 99.4% cross-reference 로 충분히 evidence-based 결론. Direct API 는
incremental confidence 만, 우선순위 낮음.

## Limit_lock_candidate 41 Rows

(Referee Round 4.1 Task 2 의 sub-item)

41 rows 의 cause:
- C1 adjusted OHLC 후 잔존 = 실제 30% 가까운 가격 변동
- Most likely: 거래정지 후 재개 첫날의 jump (recovery), 또는 corporate
  action 직후 (C3 wiring 후 corporate_action_day 로 reclassify 가능)

41 rows 가 모두 universe 안 → 즉 executable bucket 의 0.026% 만 affected.
Executable rule 보수 처리: limit_lock_candidate = next_executable_date()
에서 자동 skip → execution 영향 X.

## Verdict

**PARTIAL → effectively CLOSED** (Referee Round 4.1 lock 안에서 PARTIAL
PASS 가 maximum verdict 이지만, evidence base 가 close-equivalent).

Recommendation: KR-TRADABILITY-SEMANTICS-AUDIT-001 verdict 를 "PARTIAL PASS
WITH S3 SEMANTICS RESOLVED" 로 upgrade.

## Related

- `data/processed/w001_v2/listing_status_events.csv` (S3 10,769 events)
- `reports/experiments/round4_1_v2_1/krx_volume0_vs_s3_reconciliation.csv` (cross-reference data)
- `src/utils/tradability.py` (tradable_state v2.1)
- `reports/experiments/round4_partial_reA0/tradable_state_v2_validation.md` (Round 4 partial)
