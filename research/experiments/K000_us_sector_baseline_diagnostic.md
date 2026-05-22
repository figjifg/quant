# K000 US Sector Baseline Diagnostic

Status: READY (immediately executable)

## Purpose

Measure simple buy-and-hold behavior, cross-sector correlation, and stress
performance for 11 US sector ETFs.

This is a US sector sleeve diagnostic, not rotation research.

## Universe

XLE, XLF, XLK, XLV, XLP, XLU, XLI, XLY, XLB, XLRE, XLC.

## Period

- Main period: 1998-12 through latest local 2026 data.
- XLRE begins separately in 2015-10.
- XLC begins separately in 2018-06.

## Measurements

- Sector buy-and-hold CAGR, Sharpe, and max drawdown.
- Daily return correlation matrix across sectors.
- Diversification value versus SPY.
- Stress-period performance:
  - GFC: 2008-2009.
  - 2022: full year.
  - COVID: 2020-02 through 2020-03.
  - Dot-com: 2000-2002.

## Prohibited

- Rotation timing.
- Momentum ranking.
- Parameter grid.

## Output

`reports/experiments/K000_us_sector_baseline_diagnostic/`

Required files:

- `config.yaml`
- `daily_nav_by_sector.csv`
- `correlation_matrix.csv`
- `stress_by_sector.csv`
- `metrics.json`
- `report.md`
