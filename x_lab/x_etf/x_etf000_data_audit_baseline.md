# X-ETF000 Data Audit + Baseline Board

X-Lab quarantine applies. This task is data audit and baseline only. Strategy
optimization is not authorized.

## Universe

SPY, QQQ, IWM, IEF, TLT, SHY, GLD, UUP, DBC, VWO, EWY, EWJ, EWZ, MCHI.

## Benchmarks

- buy-and-hold each ETF
- 60/40: SPY 60% + IEF 40%
- P08 proxy: SPY 29% + QQQ 21% + IEF 50%, US-only proxy without H001
- `P08_IEF30` where local daily NAV is available

## Audit Scope

- local data availability from `research_input_data/inputs/global_etf/`
- row count, start date, end date, duplicate date count, missing price count
- adjusted close assumption from local Yahoo Finance CSVs
- USD-only and KRW-converted baseline metrics
- stress windows: GFC proxy 2008-2009, COVID 2020-02 to 2020-03, 2022 full year
- 2010-2026 comparison period and long-history period where local coverage
  allows

## Cost / Tax Assumptions

`X-ETF000` reports gross-only baseline metrics. T-family default assumptions
for future taxable strategy work are HIFO, KRW 2.5M annual exemption, 22%
capital-gains tax, 0.25% round-trip trading cost, 10 bps FX cost, and 15%
dividend withholding. They are not applied to this buy-and-hold diagnostic.

## Outputs

Generated outputs are written under:

`x_lab/x_etf/x_etf000_results/`

- `data_availability.csv`
- `buyhold_metrics.csv`
- `benchmark_portfolios.csv`
- `stress_windows.csv`
- `baseline_board.md`
- `verdict.json`
