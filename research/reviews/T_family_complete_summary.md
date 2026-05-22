# T-family complete summary

Status: T-family complete as research. New alpha family X. O-family operations tooling starts next.

Mission redefinition: build a tax-aware global allocation quant system using the validated Korean macro sleeve plus global ETF exposures.

Paper tracking versions:

| version | role |
| --- | --- |
| Gross P08_IEF30 | research reference |
| V1 taxable P08_IEF30 | overseas ETF direct, HIFO, KRW 2.5M exemption, 22% capital gains tax |
| MIX1 practical shadow | V1 50% + ISA 30% + pension 20%, simplicity first |
| V4 pension-only shadow | pension savings 100%, withdrawal tax reflected, lock-up assumed |

## T000 through T004 results

| ticket | result |
| --- | --- |
| T000 | I005 tax model was reproducible but incomplete for Korean taxable-account realism. HIFO plus KRW 2.5M exemption became the default taxable-lot assumption. |
| T001 | Rebalance-frequency test showed drift-heavy variants can raise net CAGR, but quarterly remains the practical control point for portfolio identity and operations. |
| T002 | No-trade bands raised net CAGR in some cases, but positive-band candidates failed drift/stress filters. Quarterly 0pp remains the selected practical setting. |
| T003 | TLH impact was small in a trending bull sample. Best TLH scenario improved net CAGR only about 0.005pp versus no TLH and missed the pre-registered threshold. |
| T004 | Account/vehicle selection was the largest implementation lever. Pension/IRP/ISA mixes dominated small rebalance and TLH tweaks, subject to lock-up and tax-rule confirmation. |

## P08_IEF30 net CAGR anchors

| scenario | CAGR |
| --- | ---: |
| Gross P08_IEF30 | 12.74% |
| MIX2 account mix | 12.58% |
| V4 pension-only after withdrawal tax | 12.83% |

Notes:

- Gross reference from I003.5 / T004: 12.738381%.
- MIX2 after pension withdrawal tax from T004: 12.578490%.
- V4 after pension withdrawal tax from T004: 12.826661%.

## Operational conclusions

- HIFO plus KRW 2.5M annual capital-gains exemption is the default taxable-lot assumption for V1 taxable tracking.
- Quarterly rebalance is the practical optimum because T001 and T002 confirm that less-controlled drift variants do not clear the operational stress filter.
- No-trade band is X for the current default: positive bands did not survive the combined drift/stress criteria.
- TLH is low priority because the measured effect was small in the trending bull sample.
- Account/vehicle is the largest implementation lever and should be tracked explicitly.
- Next family: O-family operations tooling.
- Tax-professional confirmation is mandatory before live implementation. The T-family remains research/diagnostic until that review is complete.
