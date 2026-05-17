# D011 — D009 composite threshold neighborhood grid (D007 equivalent on D009)

## Status
planned

## What this ticket is

D007 가 D001 의 threshold plateau MARGINAL (2/5) 검증. D009 carrier
도 같은 차원 확인.

D011 = D009 carrier 에 threshold grid [-0.2, -0.1, 0.0, +0.1, +0.2]
적용.

## Pre-registered verdict (D007 와 동일)

| 결과 | Verdict |
|---|---|
| ≥ 4 of 5 Sharpe ≥ 0.40 | STRONG PLATEAU |
| 3 of 5 | PLATEAU |
| 2 of 5 | MARGINAL |
| 1 of 5 (only 0.0) | CLIFF |

Combined with D007 MARGINAL: D011 STRONG → D009 더 robust;
D011 MARGINAL → D009/D001 비슷.

## Hypothesis

### H1: threshold 0.0 (D009) 재현
- D011-0.0 Sharpe = 0.4144 (D009 정확 재현)

### H7: D009 threshold cliff vs plateau

## Implementation

D007 와 동일 pattern. New strategy `d011_threshold_grid_on_d009.py`.
D001-D010 byte-identical.

### Configuration

`configs/backtests/d011.yaml`: D009 동일하되 `on_threshold_grid:
[-0.2, -0.1, 0.0, 0.1, 0.2]`.

### Completion criteria
- pytest fully green
- engine.py untouched
- D001-D010 byte-identical
- D011-0.0 Sharpe = 0.4144 (D009 reproduce)
- Grid table + verdict
