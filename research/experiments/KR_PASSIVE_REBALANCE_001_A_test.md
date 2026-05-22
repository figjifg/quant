# KR-PASSIVE-REBALANCE-001 (A형) — Pre-Registered Diagnostic Spec

## Status
PRE-REGISTERED · TEST · diagnostic only

이 ticket 은 production approval 아니다. Referee lock 기준 "새 아이디어는
diagnostic only 이며 production / paper candidate 로 부르면 안 된다" 경계 적용.

## Cycle Lineage

- Bull/Bear/Referee 첫 사이클 결과 (2026-05-22)
- Strategy ID: `KR-PASSIVE-REBALANCE-001`
- Locked verdict: TEST (A형 only)
- B형 (사전 편입 예측모델) = 동일 ID 안에서 테스트 X, 별도 BACKLOG

## Hypothesis

지수 편입이 공식 발표된 종목 basket 에서, 발표 이후 ~ 리밸런싱 전 구간에
passive demand / ADV 압력으로 인한 단기 가격압력이 발생하는지 진단.

## Failure mode being tested

이 이벤트는 알려진 게임이다. 발표 후 edge 는 이미 front-run 되었을 수 있고,
리밸런싱 전후 slippage / 반전이 이론적 edge 를 먹을 수 있다.

## Strategy type

Event-driven · pre-registered diagnostic (B형 예측 X)

## Fixed Scope (Referee 고정, 변경 금지)

| 항목 | 고정 조건 |
|---|---|
| **Universe** | 공식 발표 후 편입 확정 종목만 |
| **Excluded** | 사전 예측 편입 후보, near-miss 예측모델, 사후 구성종목 재구성 |
| **Controls** | near-miss non-inclusion, fake rebalance date, random announced basket |
| **Execution** | announcement 이후 t+1, VWAP/close, rebalance 전 exit, rebalance 후 reversal check |
| **Cost stress** | 거래세 · 수수료 · spread · ADV participation · 종가충격 별도 측정 |
| **Kill gate** | after-cost excess 없음, demand/ADV 단조성 없음, rebalance 후 반전으로 P&L 소멸, 특정 이벤트/연도 집중 |

## Signal definition

- 신호 발생일: 지수 운영기관의 공식 편입 발표일 (DART/index provider 공시)
- 종목: 발표문에 명시된 편입 확정 종목 only (예측 X)
- Intensity proxy (sub-diagnostic 만): demand_estimate / ADV
  - demand_estimate = (ETF AUM × index weight) proxy
  - ADV = 직전 60거래일 평균 거래대금
- intensity decile 단조성 검증 = Kill gate

## Entry rule

- 발표일 T 종가 후 신호 확정
- 진입 시점: T+1 open (VWAP 또는 close 동시 측정)
- 보유 종목: 발표 확정 basket 만 (사전 예측 X)
- Position sizing: equal-weight + ADV cap (per name ≤ X% of name ADV)

## Exit rule

- Exit 시점: 리밸런싱 적용일 전일 close
- Reversal check: 리밸런싱 후 5-10거래일 추가 측정 (별도 sub-diagnostic, 진입 X)

## Holding period

발표일 T+1 ~ 리밸런싱 적용일 T_R - 1 (변동, 보통 1-3주)

## Data assumptions

- 지수 운영기관 공식 발표일 PIT (사후 정정 X)
- 발표문 본문 종목 list = source of truth
- ETF AUM proxy = 발표일 시점 기준 (사후 수정 X)
- ADV / 시총 / free float = 발표일 시점 PIT
- 상폐 / 거래정지 / 관리종목 = corporate action 처리 (W001 engine)

## Cost assumptions

별도 layer 로 분리 측정 (단일 bps 금지):
- 거래세 (매도세 0.20% KOSPI / 0.20% KOSDAQ)
- 수수료 (10-15 bps round-trip proxy)
- Spread (실측 또는 conservative 50-100 bps)
- ADV participation impact (5% / 10% / 20% bucket)
- 종가 동시호가 충격 (rebalance day stress)

## Baseline comparison

- KOSPI / KOSDAQ index excess
- Sector × size × liquidity matched non-event basket
- random announced basket (placebo)
- near-miss non-inclusion (가장 중요한 control)
- fake rebalance date (date shuffle placebo)

## Parameters to test

| Parameter | Range | Locked? |
|---|---|---|
| Entry timing | T+1 open / T+1 VWAP / T+1 close | 3 fixed |
| Exit timing | T_R-1 close / T_R close | 2 fixed |
| Position sizing | equal-weight + ADV cap 5%/10%/20% | 3 fixed |
| Cost stress | 5 layer 별도 | 모두 측정 |

총 = 3 × 2 × 3 = 18 cell. **Sub-cell tuning 후 best 선택 = REJECT trigger**.

## Parameters that must NOT be optimized

- Universe 재정의 (편입 확정 종목만)
- B형 사전 예측 모델 추가
- 사후 편입 결과 알고 사전 예측 학습
- Inclusion probability 튜닝
- Holding period 사후 최적화

## Success criteria (diagnostic only, production X)

이 카드는 production approval 받을 수 없다. 다음 모두 통과 시 = "false alpha
검증 통과, 다음 단계 = deep validation" 단계로만 승격:

1. 발표 후 ~ 리밸런싱 전 구간 after-cost excess > 0 (single name 아닌 basket 기준)
2. intensity decile (demand / ADV) 단조성 통계적으로 유의
3. near-miss non-inclusion control 과 명확한 차이 (p-value 또는 effect size)
4. fake rebalance date placebo 와 차이 명확
5. random announced basket placebo 와 차이 명확
6. Top 1, 3, 5 contributor 제거 후 효과 유지
7. 특정 연도 / 특정 index / 특정 대형 이벤트 의존 X
8. 5 cost layer 모두 반영 후에도 excess > 0

## Kill criteria

다음 중 하나라도 발생 = **kill**:

- A형 발표 후 ~ 리밸런싱 전 after-cost excess 없음
- demand / ADV intensity 단조성 X (score kill)
- 리밸런싱 후 5-10거래일 반전으로 P&L 전체 소멸
- near-miss non-inclusion control 과 차이 없음
- random/fake placebo 와 차이 없음
- Top contributor 제거 후 효과 사라짐
- 단일 연도 / 단일 index / 단일 그룹 의존
- ADV participation 5% → 20% 변화에 effect size monotonic 감소

## Global REJECT Triggers (즉시 무효화)

다음 중 하나라도 발생 → BACKLOG 아니라 **REJECT**:

- 실제 편입 결과를 알고 사전 예측모델 학습 (= B형 변형)
- 사후 확정 ETF 매수 결과를 발표일 신호로 사용
- Top contributor 1-5개 제거 후 성과 붕괴
- Matched control / placebo / cost stress 없이 gross return 만 보고 주장
- Diagnostic 결과를 P08 / paper tracking / live readiness 에 연결

## Expected weaknesses

- 이벤트 수 적음 (지수 변경 빈도 낮음) → statistical power 약함 가능
- 특정 index 의 특정 시기 (코로나, 2021 bull) 이벤트 집중 가능
- ETF AUM proxy 부정확 → demand estimate noisy
- 종가 동시호가 슬리피지 측정 어려움
- 발표 후 즉시 front-run → after-cost edge 0 가능성 높음

## A0 Audit Checks (pre-execution required)

Bear 원문 #15:
- A형 / B형 완전 분리 확인
- 이벤트 calendar 구축 (지수 × 발표일 × 적용일)
- near-miss control 정의 (어떤 종목이 near-miss 인지 PIT 기준)
- 지수별 발표 / 적용일 confirm
- 종가 / VWAP / next-day exit 3 가지 체결 가정 비교

A0 audit fail 시 = backtest 진입 X. Spec 재검토.

## Codex implementation task

```
Implement KR-PASSIVE-REBALANCE-001 A형 pre-registered diagnostic spec.

DO NOT:
- Modify research_input_data/ files
- Use future data
- Implement B형 prediction model
- Tune entry/exit per-cell after seeing results
- Aggregate metrics before A0 audit passes
- Connect output to P08 / paper tracking

Tasks:
1. A0 audit script first (event calendar + near-miss universe + cost decomposition).
2. If A0 fails: stop. Report only A0 results.
3. If A0 passes: implement 18-cell bounded backtest (3 entry × 2 exit × 3 sizing).
4. Apply 5 cost layers (tax / commission / spread / ADV impact / closing auction).
5. Compute placebo controls (near-miss, fake date, random basket).
6. Save outputs under reports/experiments/KR_PASSIVE_REBALANCE_001_A/.

Required outputs:
- config.yaml (locked scope)
- a0_audit.csv
- event_calendar.csv
- backtest_metrics.csv (18 cells)
- placebo_metrics.csv (3 controls)
- top_contributor.csv
- cost_decomposition.csv
- report.md (diagnostic only, kill gate evaluation, NO production language)
```

## Result summary

작성 금지. Bear 결과 해석 / kill 시도 단계 (Step 6) 까지 비워둠.

## Bull/Bear/Referee review

작성 금지. 사이클 Step 7-9 후 채워짐.
