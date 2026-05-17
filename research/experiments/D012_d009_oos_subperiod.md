# D012 — D009 out-of-time subperiod split (D008 equivalent on D009)

## Status
planned

## What this ticket is

D008 가 D001 의 STRONG generalization per pre-registered, 그러나
spike-dependent (2025 = 59.4%) finding. D009 가 spike dependency
29.8% 로 절반인데 — temporal stability 도 검증 필요.

D012 = D009 carrier 에 D008 과 동일한 subperiod schemes 적용.

## Subperiods (D008 와 동일)

- full: 2010-2026
- scheme_a_is/oos: 2015-2020 / 2021-2026
- scheme_b_is/oos: 2015-2019 / 2020-2026
- scheme_c_is/oos: 2015-2021 / 2022-2026
- per-year breakdown
- rolling 3yr Sharpe

## Pre-registered verdict (D008 와 동일)

OOS Sharpe per scheme:
- ≥ 0.40 → STRONG GENERALIZATION
- 0.30-0.40 → ACCEPTABLE
- 0.20-0.30 → MARGINAL
- 0.10-0.20 → WEAK
- < 0.10 또는 음수 → OOS COLLAPSE

Combined with D008 STRONG (3/3): D012 STRONG → D009 도 generalize;
D012 weaker → D009 less temporally robust 라도 spike-dependency 낮은
점은 가치 있음.

## Hypothesis

### H1: D009 재현
- D012 full-period Sharpe = 0.4144

### H7: D009 OOS robustness per 3 schemes

### H8: Per-year breakdown — D009 가 D001 보다 더 균일한지

### H9: 2020, 2025 spike year contribution (D009 는 29.8% 이미 보임)

## Implementation

D008 와 동일 pattern. New strategy `d012_subperiod_on_d009.py`.

### Configuration

`configs/backtests/d012.yaml`: D008 와 동일 subperiods 설정, D009
blocks.

### Completion criteria
- pytest fully green
- engine.py untouched
- D001-D011 byte-identical
- D012 full-period reproduces D009
- Subperiod table, IS/OOS comparison, per-year breakdown, verdict
