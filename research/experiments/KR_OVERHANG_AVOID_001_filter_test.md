# KR-OVERHANG-AVOID-001 (filter형) — Pre-Registered Diagnostic Spec

## Status
PRE-REGISTERED · TEST · diagnostic only · exclusion filter (NOT standalone alpha)

이 ticket 은 production approval 아니다. Standalone alpha 가 아니라 **long-only
basket exclusion filter** 로만 테스트한다.

## Cycle Lineage

- Bull/Bear/Referee 첫 사이클 결과 (2026-05-22)
- Strategy ID: `KR-OVERHANG-AVOID-001`
- Locked verdict: TEST (filter형 only)
- Standalone alpha / long-short alpha / production basket 연결 = 즉시 REJECT

## Hypothesis

CB/BW, 전환청구, 추가상장, 유상증자, 보호예수 해제, 대주주 매도 등 잠재
공급압력 (overhang) 이 큰 종목을 long-only 후보 basket 에서 제외할 때,
tail risk / left-tail / drawdown contribution 이 의미 있게 개선되는지 진단.

**"overhang 종목을 사서/팔아서 돈 버는 전략" 가설 X.** 단지 negative
selection 제거 filter 의 효과를 측정.

## Failure mode being tested

overhang 이 이미 가격에 반영되었거나, 조달 자금이 성장 투자로 연결되는 기업
까지 제외해 좋은 turnaround 를 놓칠 수 있다. 또는 overhang exclusion 효과가
사실은 high-volatility exclusion 효과인 경우.

## Strategy type

Exclusion filter · pre-registered diagnostic · MDD/tail focus (alpha 아님)

## Fixed Scope (Referee 고정, 변경 금지)

| 항목 | 고정 조건 |
|---|---|
| **Role** | long-only 후보 basket exclusion filter |
| **Excluded** | standalone alpha, long-short, production 후보 연결 |
| **Event taxonomy** | CB/BW, 전환청구, 추가상장, 유상증자, 보호예수 해제, 대주주 매도 |
| **Measurement** | potential shares / free float, event age, event severity |
| **Controls** | random exclusion, high-vol non-overhang exclusion, event-date shuffle |
| **Evaluation** | return 보다 MDD, left-tail, drawdown contribution, bad-name avoidance 우선 |
| **Kill gate** | random exclusion 과 차이 없음, high-vol exclusion 과 차이 없음, 특정 업종 제거 효과뿐, filtered basket 이 원본보다 tail 개선 없음 |

## Signal definition

각 종목 × 날짜 에 대해 overhang event flag + intensity:

- Event types (taxonomy): CB / BW / 전환청구 / 추가상장 / 유상증자 / 보호예수 해제 / 대주주 매도
- Per-event: potential_shares / free_float, event_age (공시 후 거래일 수), event_severity
- 종목 overhang flag = 최근 N 거래일 내 위 event 중 하나라도 발생 (binary)
- 종목 overhang intensity = Σ (potential_shares × age_decay) / free_float

## Filter rule

- 연구용 long-only basket (W001 또는 다른 long-only universe) 에서 시작
- 매 rebalance 일에 overhang flag = true 종목 **제외**
- 또는 overhang intensity 상위 decile 제외 (2 variant)
- 보유 중 overhang 공시 발생 = exit (단 exit delay rule 적용)

## Application universe

- 원본 long-only 후보 basket (예: KOSPI dynamic top 100 또는 W001 universe)
- **production candidate basket 연결 금지**
- 진단용 universe 만 사용

## Data assumptions

- DART/KIND 공시 PIT (접수번호 기준)
- CB/BW 발행조건 (전환가, 리픽싱, 기간) PIT
- 사후 확정 전환 물량 / 실제 상장 물량 / 철회 = 사용 X (look-ahead)
- 당시 공시된 potential / scheduled amount 만 사용
- 보호예수 해제일 = 공시 시점 스케줄 사용

## Cost assumptions

- Filter 자체 비용: 진입 단계 turnover 영향 (제외 = 진입 안 함, 비용 X)
- Exit 단계 비용: 보유 중 overhang 공시 발생 시 즉시 exit 가정의 slippage
  - 거래세 + 수수료 + spread (실측 또는 conservative)
  - 소형주 exit 시 ADV impact

## Baseline comparison

- **원본 basket (filter 적용 X)** = 가장 중요한 baseline
- Random exclusion (overhang flag 와 같은 비율로 무작위 제외)
- High-volatility exclusion (overhang 과 같은 비율로 vol 상위 제외)
- Event-date shuffle (overhang 이벤트 날짜 무작위 shuffle 후 동일 filter)
- Sector exclusion (해당 이벤트가 많은 sector 통째 제외)

## Parameters to test

| Parameter | Range | Locked? |
|---|---|---|
| Filter binary | overhang flag = true 제외 | 1 |
| Filter decile | intensity 상위 10% / 20% 제외 | 2 |
| Lookback N | 20일 / 60일 / 120일 | 3 |
| Exit delay | 즉시 / T+1 / T+5 | 3 |

총 = (1 + 2) × 3 × 3 = 27 cell.

## Parameters that must NOT be optimized

- Standalone alpha 측정 (long basket / signal score / weight)
- Long-short 변환
- Production basket 연결
- 사후 확정 전환물량 / 추가상장 결과 사용
- 결과 보고 weight tuning

## Success criteria (diagnostic only)

이 카드는 production approval 받을 수 없다. 다음 모두 통과 시 = "false alpha
검증 통과, exclusion filter 효과 확인" 단계로만 승격:

1. Filtered basket MDD 개선 (원본 대비, p-value 또는 effect size)
2. Filtered basket left-tail (5% / 10% VaR) 개선
3. Drawdown contribution: 제외된 종목들의 원본 basket 내 contribution 이 음수 평균
4. Bad-name avoidance: 제외된 종목들의 forward N 일 수익률 음수 평균
5. Random exclusion 과 명확한 차이
6. High-vol exclusion 과 명확한 차이 (overhang 효과 ≠ vol 효과 검증)
7. Event-date shuffle placebo 와 차이 명확
8. 특정 sector (예: KOSDAQ 바이오) 제외 효과만이 아님 (sector-neutral 검증)
9. Lookback N / exit delay 변화에 monotonic 또는 stable

## Kill criteria

- 원본 basket 대비 MDD / left-tail 개선 X
- Random exclusion 과 차이 없음
- High-vol exclusion 과 차이 없음 (= 사실은 vol 효과)
- 특정 sector 제거 효과만 (sector-neutral 후 소멸)
- Event-date shuffle 과 차이 없음
- Top contributor (가장 많이 회피된 종목) 1-5개 제거 시 효과 붕괴
- Exit delay 0/T+1/T+5 사이 효과 정반대 movement

## Global REJECT Triggers (즉시 무효화)

- Standalone alpha 측정 시도 (long signal score 등)
- Long-short 전환
- Production basket / paper tracking / P08 연결
- 사후 확정 전환물량 · 추가상장 결과를 발표일 신호 사용
- Top contributor 1-5개 제거 후 성과 붕괴
- Matched control / placebo / cost stress 없이 gross return 만 보고 주장

## Expected weaknesses

- overhang 이 이미 가격 반영 → filter 효과 0 가능
- 좋은 turnaround 기업 (CB 로 R&D 자금 조달) 제외 → return 손실
- 작은 이벤트 수 → statistical power 약함
- 특정 위기 구간 (2020 COVID) 의 KOSDAQ 바이오 cluster 효과 dominate 가능
- Vendor 본문 파싱 부정확 → false flag

## A0 Audit Checks (pre-execution required)

Bear 원문 #15:
- Overhang event taxonomy 정의 (7 category 명확)
- 공시 유형별 sample audit (CB / 추가상장 / 보호예수 각 20-50건)
- Potential shares / free float 계산 PIT 검증
- Cancellation / withdrawal 처리 (사후 결과 사용 X)
- 원본 basket 대비 filtered basket 비교 frame 고정
- W001 corrected calendar / tradability / corporate action engine 사용

A0 audit fail 시 = backtest 진입 X.

## Codex implementation task

```
Implement KR-OVERHANG-AVOID-001 filter형 pre-registered diagnostic spec.

DO NOT:
- Implement as standalone alpha
- Implement long-short variant
- Connect filtered basket to P08 / paper tracking / production
- Use future settlement / actual conversion results
- Modify research_input_data/ files
- Aggregate metrics before A0 audit passes

Tasks:
1. A0 audit script: event taxonomy + potential_shares/free_float PIT computation
   + sample audit (CB/추가상장/보호예수 각 20+).
2. If A0 fails: stop. Report only A0 results.
3. If A0 passes: implement 27-cell bounded filter diagnostic.
4. Apply on existing long-only research basket (W001 universe or KOSPI top 100).
5. Compute placebo controls (random, high-vol, event-date shuffle, sector).
6. Save outputs under reports/experiments/KR_OVERHANG_AVOID_001_filter/.

Required outputs:
- config.yaml (locked scope, filter-only)
- a0_audit.csv (taxonomy + sample audit)
- event_log.csv (PIT events with intensity)
- filtered_vs_original.csv (27 cells: MDD / left-tail / DD contribution)
- placebo_metrics.csv (4 controls)
- top_avoided_contributor.csv
- sector_neutral_check.csv
- report.md (diagnostic only, kill gate evaluation, NO production language)
```

## Result summary

작성 금지. Bear 결과 해석 / kill 시도 단계 (Step 6) 까지 비워둠.

## Bull/Bear/Referee review

작성 금지. 사이클 Step 7-9 후 채워짐.
