# D010 — D009 z-score window neighborhood grid (D006 equivalent on D009)

## Status
planned

## What this ticket is

D006 가 D001 의 window plateau (48-84mo Sharpe 0.47-0.48) 검증.
D009 가 COMPARABLE ADOPT (Sharpe 0.41) — robustness 도 확인 필요.

D010 = D009 carrier 에 D006 와 동일한 window grid [36, 48, 60, 72, 84]
적용.

## Single change

Window grid on D009 carrier. 다른 모든 D009 parameter (10 vars, 5
blocks, sign convention, threshold ≥ 0, selection, costs, rebalance)
identical.

## Pre-registered verdict (D006 와 동일 기준)

| 결과 | Verdict |
|---|---|
| ≥ 4 of 5 Sharpe ≥ 0.40 | **STRONG PLATEAU** — D009 robust |
| 3 of 5 ≥ 0.40 | PLATEAU acceptable |
| 2 of 5 ≥ 0.40 | MARGINAL |
| 1 of 5 (only 60mo) ≥ 0.40 | **CLIFF — D009 FRAGILE** |

Combined with D006 STRONG PLATEAU: D009 STRONG → both carriers
window-robust → choose by other criteria.

## Hypothesis

### H1: 60mo (D009) 재현
- D010-60mo Sharpe = 0.4144 (D009 정확 재현)

### H7: D009 window plateau (cliff vs plateau)

### H8: 36mo, 48mo 의 2010-2014 trade 수 (warmup-artifact)

## Implementation

D006 와 동일 pattern. New strategy `d010_window_grid_on_d009.py`,
config `d010.yaml`, 5 backtest variants. D001-D009 byte-identical
reproducibility.

### Configuration

`configs/backtests/d010.yaml`: D009 와 동일하되 `z_score_window_grid:
[36, 48, 60, 72, 84]` 사용.

### Completion criteria
- pytest fully green
- engine.py untouched
- D001-D009 byte-identical
- D010-60mo Sharpe = 0.4144 (D009 reproduce)
- Grid table + verdict
