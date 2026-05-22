# Round 2 Global A0 Gates

Date: 2026-05-22
Status: NON-NEGOTIABLE
Applies to: 모든 Round 2 카드 (KR-LIQ-FRAGILITY-AVOID / KR-TRADABILITY-RESUME-RISK
/ KR-LIQ-MIGRATION / KR-TURNOVER-ATTENTION / KR-FLOW-ABSORPTION)

이 10 gate 중 하나라도 깨지면 해당 카드는 성과 diagnostic 단계로 진입 불가
(KILL). lineage-only 카드도 lineage audit 단계에서 동일 gate 적용.

## Gate 1 — Permanent Identifier

| 요구 | 처리 |
|---|---|
| delisting | 종목코드 변경 / merged ticker / 상폐 시점까지 chronological trace |
| merge | survivor ticker / merged-out ticker 양쪽 lineage 보존 |
| rename | rename 전 / 후 동일 entity mapping |
| ticker change | KRX ticker rotation (재배정 등) 처리 |
| suspension | 거래정지 기간 + 재개 시점 명시 |

**Failure → KILL**: 위 변화 중 하나라도 추적 안 됨 = 모든 dependent 카드 kill.

## Gate 2 — Survivorship

**Requirement**: dynamic_top100 panel 이 사후 생존 universe (= 현재 상장 + 현재 시총 상위) 가 아니어야 함.

**Verification**:
- 과거 시점 t 의 top 100 = t 시점 정보 (시총 / 상장 / 거래정지) 만으로 구성 가능한가?
- 사후 상폐된 종목이 과거 panel 에 포함되어 있는가? (포함 = 정상, 미포함 = survivor bias)
- 사후 합병으로 사라진 ticker 가 합병 전 panel 에 보존되어 있는가?

**Failure → KILL**: dynamic_top100 survivor 확인 = 4 카드 (FRAGILITY / TRADABILITY / MIGRATION / TURNOVER) 모두 kill.

## Gate 3 — Tradability Semantics

W001 의 `tradable=false` 가 다음 4 cause 중 어느 것인지 명확히 구분 필요:

| Cause | 처리 |
|---|---|
| 실제 거래정지 / 매매정지 | strategy event 가능 |
| limit-lock (상한가 / 하한가 고정) | 별도 locked-position rule 필요 |
| panel absence (당시 universe 밖) | strategy event 아님 |
| data missing (vendor 누락) | strategy event 아님 |
| delisting transition | 별도 terminal event 처리 |

**Failure → KILL**: 4 cause 구분 불가 시 KR-TRADABILITY-RESUME-RISK 즉시 kill,
KR-LIQ-FRAGILITY-AVOID 도 fragile signal 의 root cause artifact 위험 = kill.

## Gate 4 — Locked Limit / Executable Status

**금지 가정**:
- limit-up 종가에 매수 가능
- limit-down 종가에 매도 가능
- 거래정지 직전 종가에 매도 가능

**Requirement**: 보수적 locked-position rule (limit-lock 시 진입 / 청산 불가능
가정 + 가능 시점까지 carry).

**Failure → KILL**: locked-position rule 없으면 모든 카드 kill.

## Gate 5 — Adjusted OHLC Sanity

**Requirement**:
- 액면분할 (split) → adjusted price 일관성
- 액면병합 (reverse split) → adjusted price 일관성
- 감자 → adjusted price 일관성
- 증자 (rights / bonus) → adjusted price 일관성
- 거래재개 가격 → 정지 전 / 후 price gap 처리 명시

**Failure → KILL**: adjusted OHLC artifact 시 KR-LIQ-MIGRATION / KR-TURNOVER-ATTENTION 즉시 kill (시총 / turnover 계산 왜곡).

## Gate 6 — Market Cap PIT

**Requirement**:
- 과거 시점 t 의 market cap = t 시점 발행주식수 × t 시점 가격
- restated (사후 정정) 주식수 사용 금지
- vendor 의 사후 보정 field 사용 금지

**Failure → KILL**: market cap restated 시 KR-LIQ-MIGRATION (size jump 통제) +
KR-TURNOVER-ATTENTION (PIT turnover 계산) 즉시 kill.

## Gate 7 — Event Ledger

**Requirement**: 모든 TEST 카드는 성과 diagnostic 전에 event ledger 먼저 생성.

Schema (자세히 = `docs/round2_event_ledger_schema.md`):
- signal_date
- entry_date
- exit_date
- stock_id (permanent identifier)
- market (KOSPI / KOSDAQ)
- tradability_state (4 cause 명시)
- trading_value (PIT)
- market_cap (PIT)
- matched_control_id
- cost_bucket
- exit_feasibility (locked / executable 명시)

**Failure → TEST 중단**: ledger 없이 성과 diagnostic 진입 시도 = 즉시 중단.

## Gate 8 — Controls

**Requirement**: 모든 TEST 카드 필수 controls:
- Random (random selection / random exclusion / random date)
- Matched non-signal (size / liquidity / volatility / trailing return 등 matched)
- Simple baseline (raw trading value / raw market cap / 20d momentum 등 단순 변형)

각 카드별 추가 control = 해당 spec 참조.

**Failure → TEST 중단**: control 미구현 시 즉시 중단.

## Gate 9 — Performance Language

**금지**:
- production
- paper
- paper candidate
- P08 / P08_IEF30
- live readiness
- shadow track
- production candidate

위 어휘 사용 시 = protocol violation.

A0 diagnostic 결과를 P08 sleeve, paper tracking, live deployment, defensive
shadow (N002-B / N001-B) 어느 것에도 연결 X.

**Failure → protocol violation**: 즉시 escalation, Referee 재심의.

## Gate 10 — Performance Metric Priority

성과 metric 평가 시 다음 우선순위:

```
1. locked-position incidence (locked-limit 으로 진입 / 청산 못한 비율)
2. exit infeasibility (청산 의도 시점에 실제로 청산 못한 비율)
3. left-tail loss (5% / 10% VaR, worst-case)
4. MDD (maximum drawdown)
5. after-cost return
6. turnover-adjusted return
```

**후순위 (Round 2 평가에서 secondary only)**:
- CAGR
- Sharpe
- gross return

이 우선순위 = 단기 alpha discovery 가 아니라 long-only research stack 의 데이터,
체결 가능성, liquidity, tail-risk 취약점 진단 목적과 일치.

## Per-Card Application

| Gate | FRAGILITY | TRADABILITY | MIGRATION | TURNOVER | FLOW-ABSORPTION |
|---|:-:|:-:|:-:|:-:|:-:|
| 1 Permanent ID | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 Survivorship | ✓ | ✓ | ✓ (top100 entry 핵심) | ✓ | ✓ |
| 3 Tradability semantics | ✓ | ✓ (핵심) | △ | △ | △ |
| 4 Locked limit | ✓ | ✓ | △ | △ | △ |
| 5 Adjusted OHLC | ✓ | ✓ | ✓ | ✓ (핵심) | ✓ |
| 6 Market cap PIT | ✓ | △ | ✓ (핵심) | ✓ (핵심) | △ |
| 7 Event ledger | ✓ | ✓ | ✓ | ✓ | lineage-only (event ledger 형식 다름) |
| 8 Controls | ✓ | ✓ | ✓ | ✓ | baseline 정의만 (Round 2 X) |
| 9 Performance language | ✓ | ✓ | ✓ | ✓ | ✓ |
| 10 Metric priority | ✓ | ✓ | ✓ | ✓ | N/A (performance X) |

## Related

- `docs/round2_referee_verdict_lock.md` — Round 2 verdict
- `docs/round2_event_ledger_schema.md` — event ledger 형식
- 각 카드 spec: `research/experiments/spec_KR_*_A0.md`
