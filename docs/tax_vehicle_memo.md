# Tax & Vehicle Memo

## Scope

This is T005-lite: a simplified tax and account-vehicle memo for deployment preparation.

It does not modify any backtest, strategy, or tax engine result. Korean tax treatment is summarized at a high level using 2026 assumptions and requires tax-professional confirmation before live use.

## T-Family Conclusion

Default production assumption:

- HIFO lot accounting.
- KRW 2.5M annual overseas ETF capital-gains exemption.
- MIX1 practical vehicle split: V1 50% + ISA 30% + pension 20%.

The T-family result is that vehicle choice and lot accounting are major implementation levers. They are not new alpha signals.

## Income Sensitivity

| Investor case | Practical implication |
|---|---|
| General resident, earned income below KRW 50M | V1, ISA, and pension are all usable candidates. |
| Middle income, KRW 50M to KRW 100M | Prioritize ISA limit usage and pension tax-credit capacity. |
| High income, above KRW 100M | Watch financial-income comprehensive taxation threshold if annual financial income exceeds KRW 20M. |
| Financial income below KRW 20M | V2 domestic ETF distribution tax treatment stays closer to 15.4% withholding in the simplified model. |
| Financial income above KRW 20M | V2 may face comprehensive taxation risk; V1 overseas ETF direct capital-gains classification can be preferable. |

## Vehicle Framework

| Vehicle | Simplified treatment | Key constraint |
|---|---|---|
| V1 overseas ETF direct | 22% capital-gains tax after KRW 2.5M annual exemption | No contribution cap, but taxable realization management matters. |
| V2 Korea-listed ETF | 15.4% dividend-income-style taxation in simplified model | Comprehensive taxation risk if financial income exceeds threshold. |
| ISA brokerage | KRW 2M tax-free allowance plus 9.9% separate taxation after allowance | Account limit assumed at KRW 100M. |
| Pension savings | Annual KRW 6M tax-credit base at 13.2% | Lock-up until age 55. |
| IRP | Annual KRW 3M additional tax-credit base, KRW 9M combined with pension | Lock-up and product constraints. |

## Default Assumptions

- Use HIFO for taxable overseas ETF lot selection.
- Use the KRW 2.5M annual exemption before modeling 22% overseas ETF capital-gains tax.
- Treat ISA and pension as account-level implementation overlays, not strategy signals.
- Confirm actual broker reporting, FX basis, lot selection, and account constraints before live trading.
