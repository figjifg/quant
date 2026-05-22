# I004 Paper Tracking Setup

Status: paper tracking only.

## Portfolios

| group | portfolio | target weights |
| --- | --- | --- |
| Primary | P08_IEF30 | SPY 29 / QQQ 21 / H001 20 / IEF 30 |
| Challenger | P08 | SPY 40 / QQQ 30 / H001 20 / IEF 10 |
| Challenger | P07 | QQQ 50 / H001 30 / IEF 20 |
| Challenger | P07_IEF30 | QQQ 40 / H001 30 / IEF 30 |
| Benchmark | QQQ_100 | QQQ 100 |
| Benchmark | SPY_100 | SPY 100 |
| Benchmark | QQQ_SPY_50_50 | QQQ 50 / SPY 50 |
| Benchmark | H001 | H001 100 |
| Benchmark | IEF | IEF 100 |

## Quarterly Procedure

- Generate `paper_trading/signals/global_YYYY-Q.json`.
- Record target weights for all 9 portfolios.
- Record component marks for SPY, QQQ, IEF, H001 and the latest local USDKRW observation.
- Track KRW NAV only; no actual trade instruction is authorized by this file.
- Compare paper NAV for at least 4 quarters before any cash deployment decision.

## 2026-Q2 Initial Mark

Generated file: `paper_trading/signals/global_2026-Q2.json`.

- As-of date: 2026-05-18.
- ETF marks: SPY, QQQ, IEF from local Yahoo Finance CSV files on 2026-05-18.
- H001 mark: latest local H001 NAV on 2026-05-04.
- USDKRW: latest local FRED DEXKOUS value on 2026-04-24.
