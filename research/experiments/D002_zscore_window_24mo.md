# D002 — Z-score window shortened (60mo → 24mo)

## Status
planned

## What this ticket is

D001 결과 (Sharpe 0.48, Max DD -23%) 가 진짜 architectural win.
그러나 60-month z-score warmup 으로 **2010-2017 전체 zero trades**.
실효 backtest 가 2015-2026 (10년) 만.

D002 = **z-score window 만 변경** (60mo → 24mo). 다른 모든 D001 와
동일. Warmup 5년 → 2년 줄여서 full 16년 backtest 가능.

## Single change

| 변수 | D001 | **D002** |
|---|---|---|
| Z-score window | **60 months** | **24 months** |
| Variables (8) | same | same |
| 6 factor blocks | same | same |
| Sign convention | same | same |
| Composite threshold | ≥ 0 | same |
| Selection / rebalance / costs | same | same |

**Single architectural parameter change**: window length.

## Why 24 months

- **2 years = 1 business cycle minimum** — short-term regime characterization
- **Eliminates 5-year warmup** — D001 의 2010-2014 zero-trade 해결
- **Quarterly anchor 와 호환** — 8 quarters = 24 months 가 자연스러운 분할
- 12 months 는 너무 짧음 (annual cycle 만 cover); 60 monthss 는 너무 길음

## Hypothesis (사전 등록)

### H7 (D002 architecture-specific): Window effect
- D002 net cumulative vs D001 (+129.07%): variation acceptable
- **D002 2010-2014 trades > 0** (warmup 해결 확인 필수)
- 만약 D002 Sharpe < 0.40 (vs D001 0.48) → window 가 너무 짧아 noise 증가
- D002 Sharpe ≥ 0.40 + warmup 해결 → factor aggregation **완전 validated**

### H8 (subperiod robustness — 진짜 검증)
- 2010-2017 net ≥ 0 (with actual trades, not zero-flat)
- 2018-2026 net ≥ 0 유지

D001 이 2010-2017 0% 였으니 (zero-trade), D002 2010-2017 가 어떤 값이든 정직한 evaluation 가능. 양수면 full robust strategy 확인. 음수면 D001 의 high Sharpe 가 사실 2018-2026 만의 효과.

### H9 (descriptive): Window 단축 효과
- D002 composite 분포 (D001 보다 noisier 예상)
- D002 regime ON share (D001 22.95% 와 비교)
- D002 trade count (D001 보다 많을 가능성)

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 |
|---|---|---|
| 2010-2017 ≥ 0 + Sharpe ≥ 0.40 | **STRONG PROMOTE D002 — true robust strategy** | D003 = position sizing 또는 Layer 2 |
| 2010-2017 ≥ 0 + Sharpe < 0.40 | window 너무 짧 (noise) | D003 = 36 months 시도 |
| 2010-2017 < 0 + Sharpe ≥ 0.40 | D001 의 success 가 modern era 효과 | strategic 재고 |
| 2010-2017 < 0 + Sharpe < 0.40 | 양쪽 다 안 좋음 | D003 = position sizing 또는 다른 방향 |

## Reportable metrics

기존 + window-specific:
1. Full + subperiod cumulative (full 16 years now possible)
2. (D002 - D001) per-year delta
3. **2010-2014 trades count** (warmup 해결 확인)
4. D002 vs D001 composite distribution 비교
5. Regime ON share, max DD, Sharpe
6. H1-H7 + H8 + H9

## Implementation task

매우 작은 변경:
- `src/features/macro_regime.py` — z-score window 를 parameter 화
  (60 default, override 가능). 또는 D002-specific function.
- `src/strategies/d002_zscore_24mo.py` (NEW) — clone of d001 with 24mo
- `src/run_experiment.py` — D002 dispatch
- `configs/backtests/d002.yaml` (NEW) — z_score_window_months: 24
- `tests/test_d002_strategy.py` (NEW)

**Do NOT touch**:
- engine.py
- D001 strategy (preserve)
- 기존 modules

### Configuration

`configs/backtests/d002.yaml` = d001.yaml clone with:
```yaml
regime:
  z_score_window_months: 24  # was 60
  # 나머지 동일
```

### Completion criteria

기존 + window-specific:
- pytest fully green (currently 243)
- engine.py untouched
- D001 reproducibility (existing test 그대로 pass)
- Final message:
  - V1 D002 cumulative net + cost-0 (vs D001 +129.07 / +139.71)
  - V1 D002 vs C014 v11 (+111.36 / +148.39)
  - Subperiod 2010-2017 V1 D002 net + cost-0 (CRITICAL — D001 was 0)
  - Subperiod 2018-2026
  - **2010-2014 trade count** (warmup verification)
  - V1 max DD, positive years, Sharpe, annualized
  - Regime ON share (D001 was 22.95 percent)
  - Composite distribution comparison
  - H1-H7 + H8 + H9 summary

If ambiguity, write D002_codex_questions.md.

### Out of scope

- ❌ Position sizing
- ❌ Risk breaker
- ❌ Block weights
- ❌ 변수 추가
- ❌ Selection / rebalance / engine 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
