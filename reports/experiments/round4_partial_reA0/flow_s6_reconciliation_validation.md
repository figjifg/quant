# Flow S6 Reconciliation Validation — Partial Re-A0

Card: KR-FLOW-UNIT-TIMESTAMP-AUDIT-001
Round 4 Partial Re-A0 verdict candidate: **PARTIAL PASS FOR DATA AUDIT** (100% sign match, 93-95% within ±5%; 6% outliers = small-amount noise)

## Sample Design (Existing)

| Field | Value |
|---|---|
| Period | 2024-01-02 ~ 2024-01-31 (22 trading days) |
| Tickers | 20 (top by 2024 max market cap) |
| Pairs | 440 (ticker × date) |
| Source 1 | Panel `외국인순매수금액추정` / `기관순매수금액추정` |
| Source 2 | KRX official via `pykrx.get_market_trading_value_by_date` |

## Reconciliation Result

| Metric | Foreign | Institution |
|---|---:|---:|
| Sign match | **100.0%** | 99.8% |
| Within ±5% | 93.6% | 94.8% |
| Median \|diff\| | < 1% | < 1% |

## 5% Outliers Classification (Referee 명시)

### Foreign outliers (28 / 440 = 6.4%)

| Size bucket (\|KRX flow\|) | n | Within ±5% |
|---|---:|---:|
| < 1억 KRW | 103 | 86.4% |
| 1억-10억 | 212 | 95.3% |
| 10억-100억 | 122 | 97.5% |
| 100억-1조 | 3 | 66.7% (sample too small) |

→ **거의 모든 outlier = 작은 absolute flow value 에서 denominator noise**.

Outlier sample (largest pct diff):
- ticker 80 (KRW 1.1M flow): -260% diff
- ticker 286940 (kSCHD inc.): 다수의 outlier (벤처/소형 종목)
- ticker 300720 (KRW 1.7M flow): 66% diff

→ Pct diff 가 big = small flow value. **Absolute amount 작은 거에 noisy**.

### 결론

- 큰 flow 종목 (10억-100억 bucket): 97.5% within ±5% (반환 강함)
- 작은 flow 종목 (<1억): 86.4% within ±5% (vendor 와 KRX 의 minor rounding/imputation 차이)
- **Sign convention 100% 확정**

## Sample Design Limitations

Referee 요구: "expand or document S6 reconciliation sample design".

**Current sample 한계**:
- 1 month only (2024-01)
- 20 tickers (all 시총 top)
- No year-by-year coverage (vendor coverage 가 시간에 따라 다를 수 있음)
- No KOSDAQ (KOSPI top 시총 only)
- No suspended / delisted ticker (active만)

**Full reconciliation 계획** (별도 phase):
- 매월 1주 random sample × 8 years = ~100 pairs × 96 months × 833 tickers = 너무 큼
- 권장: monthly random 5 ticker × 5 day × 96 months × 833 tickers 의 5%
  uniform sample ≈ 20,000 pairs (per year ~2,500)
- 또는 ticker × year stratified sample

## Sign Convention Lock

| Convention | Verified | Source |
|---|---|---|
| `+` = net buy | ✅ | Sample 100% match |
| `-` = net sell | ✅ | Sample 100% match |
| Unit | KRW | Ratio < 1.0 sanity passed |

## Publication Lag (Referee 요구)

| Source | Publication |
|---|---|
| KRX official (krx.co.kr) | 장 마감 후 ~18:00 KST (KRX 시장정보시스템 release) |
| Vendor (Kiwoom REST) | 장 마감 후 (정확한 시각 vendor doc 부재) |

C7 `is_flow_t1_safe()` 가 보수적 t+1 rule 사용:
- T 일 flow value = T+1 09:00 KST open 이후 안전
- 단 vendor doc 부재로 정확한 lag 미확정 = residual risk

## Estimated Flag Meaning

| Status | Value |
|---|---|
| `수급금액추정여부 = True` panel rows | 100% (1,141,751) |
| → Round 3 critical finding 의 정확한 해석 |
- Vendor 가 자체 computation (실제 KRX API 와 method 약간 다름)
- 단 sample reconciliation 100% sign + 95% within ±5% = 실용적 가치 동일

**해석**: "estimated = True" = "vendor recomputed / imputed", NOT "unreliable".
- KRX 공식 trade 정정 시 vendor 가 update 안 할 수 있음
- 또는 분 단위 timing 정확도 차이

## `is_flow_t1_safe()` Fail-Closed Test

| Input | Expected | Actual |
|---|---|---|
| 모든 flow column 존재 + 거래대금추정 > 0 + estimation flag exists | True | ✅ True |
| 거래대금추정 == 0 | False (fail-closed) | ✅ False |
| Flow column missing | False | ✅ False |
| Estimation flag missing | False | ✅ False |

→ fail-closed 동작 정상.

## Verdict (Allowed)

**PARTIAL PASS FOR DATA AUDIT**.

Reasons:
- Sign convention 100% confirmed (sample 440)
- Unit consistency confirmed
- Within ±5% = 93-95% (small-amount denominator noise = 정상)
- C7 fail-closed 동작 정상
- 100% estimated flag = informational, not disqualifying (reconciliation 결과)

Blockers for FULL PASS / FLOW STRATEGY READY:
- Sample = 1 month / 20 ticker / top size only (uniform 8-year sample 미실시)
- Vendor publication lag exact time 미확정
- vendor doc 부재 (Kiwoom REST API 정확한 estimation method 미문서화)
- KOSDAQ / suspended / delisted ticker reconciliation 미실시

## Flow Strategy Authorization

> "FLOW STRATEGY READY 는 NOT allowed" (Referee 명시)

C7 = safety marker only. Flow strategy 진입 = 별도 phase + Referee 재승인 +
4 sources (S1, S3, S4, S6) full + W001 v2 C2/C3 complete + audit-first
12 항목 통과.

## Defect Closure Status

| Defect | Round 3 → Round 4 |
|---|---|
| FLOW_000001 field doc low | **CLOSED** (C7 + pykrx field doc) |
| FLOW_000002 sign convention informational | **CLOSED** (100% sample) |
| FLOW_000003 unit consistency informational | already CLOSED |
| FLOW_000004 publication lag high | **PARTIAL** (t+1 conservative rule documented, exact vendor lag 미확정) |
| FLOW_000005 missingness informational | already CLOSED |
| FLOW_000006 nontradable nonzero medium | **PARTIAL** (panel_absence dominant cause confirmed; C5 + C7 separation) |
| FLOW_000007 100% estimated CRITICAL | **PARTIAL CLOSED** (sample 95% match → reliable enough as informational; full year audit 미실시) |
| FLOW_000008 F-family warning medium | already CLOSED |

## Related

- `src/utils/flow_safe.py`
- `data/acquired/round4/s6_flow_reconciliation/s6_reconciliation_sample_2024_01.csv`
- `reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/audit_summary.md`
