# I004 Static Allocation Champion Registration

Status: registered (formal candidate, NOT production deployment)

Candidate: P08_IEF30 = SPY 29 / QQQ 21 / H001 20 / IEF 30

## Rationale

- Multi-metric score #1 (7점).
- Sharpe 1.172.
- CAGR 12.7% (>= 12% 최소 기준).
- MDD -16.4%.
- 2022 stress best (-14.6%, P07 -19.1% 대비 +4.5pp).
- COVID drawdown controlled (-16.4%).
- 2025 spike dependence low (-0.040, P07 -0.078 보다 작음).
- Rebalance frequency robust (monthly~annual Sharpe 차이 ±0.001).
- Clear economic structure: US broad/growth core + Korea macro satellite + Treasury diversifier.

## Interpretation

P08_IEF30 is not merely a grid-best Sharpe selection. I003.5 was a pre-registered frontier validation, and the promotion is based on the multi-metric framework.

## Updated Rule

- Old rule "grid best cannot be final" remains valid for pure Sharpe picking.
- Multi-metric winner from pre-registered frontier testing may be promoted to formal candidate.
- Candidate advancement still requires I005, paper NAV validation, and tax-professional review.

## I003.6 Long-history Validation Results

- Full-history proxy result: P08_IEF30 proxy (SPY 40 / QQQ 30 / IEF 30, H001 omitted) produced CAGR 10.93%, Sharpe 0.84, and MDD -37% over the available long-history window. Its Sharpe was the top result among SPY, QQQ, SPY/QQQ 50/50, and IEF long-history comparators.
- P07-style catastrophic risk was confirmed in dot-com stress: QQQ buy-hold suffered -41% CAGR and -83% MDD in 2000-2002, while the P08_IEF30 proxy was only available from 2002-07 and showed +5.5% CAGR with -13% MDD in its available dot-com slice. This supports reducing QQQ exposure from the P07-style 50% concentration to the P08_IEF30 effective 21% QQQ allocation in the full candidate.
- GFC 2008-2009 remains an operating-awareness warning: P08_IEF30 proxy showed -2.5% CAGR and -35% MDD, materially deeper than the 2010-2026 backtest MDD of -16.4%, while still better than SPY and QQQ buy-hold drawdowns.
- 2022 stress was reconfirmed: P08_IEF30 proxy lost about -22% with -25% MDD, and Treasury exposure did not hedge the shock (IEF -14.5%, TLT -30%).

## Known Limitations

- Long-history dot-com validation is partial because IEF begins in 2002-07; 2000-2002 can identify P07-style QQQ catastrophic risk, but cannot fully reproduce P08_IEF30 before IEF availability.
- H001 cannot be reproduced before 2010; I003.6 is a US-core proxy only, not full P08_IEF30 replication.
- GFC-like regimes can plausibly produce approximately -35% MDD in the P08_IEF30 proxy.
- IEF 30% duration risk.
- 2010-2026 US bull regime 의존성 미확인.
- 실제 세금/환전/배당 처리 미검증.
- ETF 거래 비용 / 분기 슬리피지 미검증.

## Pending Gates

- I003.6 long-history US core stress: PASS, with GFC -35% MDD warning.
- I005 production-style validation (cost/FX/tax/execution).
- Paper tracking 4 분기 이상 NAV 일치.
- Tax-professional confirmation before implementation.

## Verdict

I003.6 strengthens P08_IEF30 as the formal static allocation champion candidate. The remaining gates are paper tracking for at least 4 quarters, I005 production-style validation, and tax-professional confirmation.
