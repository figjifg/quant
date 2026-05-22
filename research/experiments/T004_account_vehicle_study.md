# T004 account / vehicle study

## Status

- Type: diagnostic tax/account-vehicle study.
- Production decision: not allowed from this ticket alone. Korean tax assumptions must be checked with a tax professional before implementation.
- Code path: `src/audit/t004_account_vehicle_study.py`.
- Output path: `reports/experiments/T004_account_vehicle_study/`.

## Hypothesis

Changing the implementation vehicle for the same `P08_IEF30` exposure can improve net CAGR materially. The likely source is replacing overseas-listed ETF capital gains tax drag with domestic-listed ETF taxation, ISA separate taxation, and pension/IRP tax-credit mechanics.

Target exposure is fixed:

| Sleeve | Weight |
| --- | ---: |
| SPY proxy | 29% |
| QQQ proxy | 21% |
| H001 Korean sleeve | 20% |
| IEF proxy | 30% |

No D013/H001 strategy changes are allowed. No engine changes are allowed. ETF tracking error is simplified to zero: Korean-listed US ETF proxies use the same index return path as SPY/QQQ/IEF.

## Pre-registered vehicles

### V1 - Overseas-listed ETF direct, taxable account

- Instruments: SPY, QQQ, IEF, plus H001.
- Baseline: T000-C / T003-A.
- Lot accounting: HIFO.
- Capital gains tax: 22% on overseas-listed ETF realized gains.
- Annual capital gains exemption: KRW 2,500,000.
- Dividend withholding: 15% on overseas-listed ETF dividend proxy.
- Contribution limit: none.

### V2 - Korean-listed US ETF proxies, taxable account

- Instruments: KODEX 미국S&P500 proxy, TIGER 미국나스닥100 proxy, KODEX 미국채10년 or ARIRANG 미국장기우량회사채 proxy, plus H001.
- Lot accounting: HIFO.
- Trading gains on Korean-listed overseas ETFs: dividend-income tax treatment, 15.4%.
- Dividends/distributions: 15.4%.
- Annual KRW 2,500,000 overseas capital gains exemption: not applicable.
- Comprehensive income taxation threshold is not modeled. Assumption: no global comprehensive taxation on annual financial income above KRW 20,000,000.
- Contribution limit: none.

### V3 - Brokerage ISA

- Instruments: Korean-listed ETF proxies only for US sleeves, plus H001.
- Overseas-listed ETF direct holding: not allowed.
- Contribution limit simplification: KRW 20,000,000 per year and KRW 100,000,000 total; this diagnostic starts with KRW 100,000,000 and treats the whole account as within the simplified lifetime cap.
- ISA tax: KRW 2,000,000 tax-free allowance per tax year, excess taxed separately at 9.9%.
- Comprehensive taxation: not modeled.

### V4 - Pension savings account

- Instruments: Korean-listed ETF proxies only for US sleeves, plus H001.
- Annual tax-credit base: KRW 6,000,000.
- Tax-credit rate simplification: 13.2%.
- Pension withdrawal tax after age 55 simplification: 5.5%.
- Lock-up: assumed for the full 16-year backtest. Early-withdrawal other-income tax penalty of 16.5% is not applied to headline results; it is shown as a lock-up diagnostic.

### V5 - IRP

- Instruments: Korean-listed ETF proxies and H001 within IRP rules.
- Annual tax-credit base: KRW 3,000,000, assuming pension savings plus IRP combined ceiling of KRW 9,000,000.
- Tax-credit rate simplification: 13.2%.
- Pension withdrawal tax after age 55 simplification: 5.5%.
- Risky-asset limit: 70%. `P08_IEF30` has SPY+QQQ+H001 = 70% and IEF = 30%, so it is treated as IRP-compatible.
- Lock-up: assumed for the full 16-year backtest. Early-withdrawal 16.5% diagnostic is reported separately.

## Pre-registered scenarios

| Scenario | Definition |
| --- | --- |
| T004-V1 | 100% V1 |
| T004-V2 | 100% V2 |
| T004-V3 | 100% V3 |
| T004-V4 | 100% V4 |
| T004-V5 | 100% V5 |
| T004-MIX1 | 50% V1 + 30% V3 + 20% V4 |
| T004-MIX2 | 30% V1 + 30% V3 + 20% V4 + 20% V5 |
| T004-MIX3 | 60% V2 + 20% V4 + 20% V5 |

## Common settings

- Backtest period: 2010-01-04 through 2026-05-18.
- Initial capital: KRW 100,000,000.
- Rebalance: quarterly.
- Commission: 0.25% on traded notional, same for V1 and V2-style domestic proxies.
- Lot accounting: HIFO where taxable lot accounting is relevant.
- Ongoing NAV: taxes and credits are reflected when modeled as paid/received.
- Gross reference: I003.5 `B04_SPY29_QQQ21_H00120_IEF30` CAGR 12.738381%.
- Baseline reference: T003-A / T000-C net CAGR 12.462572%.

## Required outputs

- `vehicle_scenarios.csv`
- `tax_by_vehicle.csv`
- `vehicle_attribution.csv`
- `lock_up_analysis.csv`
- `daily_nav_by_vehicle.csv`
- `report.md`

## Report requirements

The report must be in Korean and include:

- Net comparison of the 5 vehicles.
- Net comparison of the 3 mixes.
- Most efficient vehicle and mix.
- Net effect of 22% overseas capital gains tax versus 15.4% Korean ETF dividend-income taxation.
- Actual effect of the ISA KRW 2,000,000 tax-free allowance.
- Pension savings / IRP tax-credit value versus lock-up and withdrawal tax.
- Korean tax assumptions as of 2026, with comprehensive taxation excluded as a simplification.
- Tax-professional confirmation required before production use.
- Verdict: recommended production vehicle combination for `P08_IEF30`.
- T-family summary conclusion from T000 through T004.
