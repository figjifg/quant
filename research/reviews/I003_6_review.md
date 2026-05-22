# Review — I003.6

## Verdict
promote with warning — P08_IEF30 long-history validation PASSED with GFC warning.

## One-line conclusion
The long-history US-core proxy strengthens P08_IEF30 as a candidate because Sharpe robustness survived, P07-style QQQ concentration risk was exposed, and the main caveat is now explicit: GFC-like regimes can still produce about -35% MDD.

## Did the hypothesis survive OOS?
Yes, with a material drawdown warning. Treating 1993-2009 as OOS for the P08_IEF30 proxy, the available proxy window begins in 2002-07 because IEF did not exist earlier. Over the full available proxy history through 2026, SPY 40 / QQQ 30 / IEF 30 produced CAGR 10.93%, Sharpe 0.84, and MDD -37%, ranking first by Sharpe among the tested long-history comparators.

## Baseline comparison
P08_IEF30 proxy Sharpe 0.84 exceeded SPY 0.65, QQQ 0.52, SPY/QQQ 50/50 0.54, and IEF 0.55 in the long-history comparison. During dot-com stress, QQQ buy-hold suffered about -41% CAGR and -83% MDD, while the P08_IEF30 proxy's available 2002-07 onward slice showed about +5.5% CAGR and -13% MDD.

## What improved?
Long-history evidence now supports the P08_IEF30 design choice: lower QQQ concentration than P07-style portfolios reduced catastrophic dot-com exposure while retaining the best tested full-history Sharpe.

## What got worse?
The GFC window is worse than the 2010-2026 backtest suggested. P08_IEF30 proxy showed about -2.5% CAGR and -35% MDD in 2008-2009, roughly 19pp deeper than the 2010-2026 P08_IEF30 backtest MDD.

## Cost sensitivity
Not tested in I003.6. This was a long-history proxy stress audit, not a production cost, FX, tax, or execution audit.

## Parameter sensitivity
Not tested. Do not infer new optimized weights from this audit.

## Regime sensitivity
Dot-com: pass for the available proxy slice and confirms P07-style QQQ concentration risk. GFC: warning due to -35% proxy MDD. 2022: warning reconfirmed because equities and Treasuries both lost money, with P08_IEF30 proxy down about -22% and about -25% MDD.

## Liquidity and capacity concerns
Not the focus of I003.6. ETF-level liquidity and operational cost assumptions remain under I005 and paper-tracking gates.

## Possible biases
- look-ahead bias: low for buy-hold ETF proxy series, but this does not validate H001 timing.
- survivorship bias: possible because ETF proxy uses surviving instruments and cannot reconstruct unavailable pre-inception sleeves.
- data snooping: moderate at the family level because P08_IEF30 was selected before this validation, but I003.6 was a gate/stress audit rather than a new search.
- multiple testing: moderate across I-family allocation variants; no new weights should be chosen from I003.6.
- market beta exposure: high by design through SPY and QQQ sleeves.
- price momentum contamination: not applicable as a buy-hold allocation proxy.

## Most likely failure mode
A GFC-like equity crash combined with insufficient Treasury offset can produce roughly -35% MDD. A 2022-style inflation/rate shock can also cause equity and Treasury sleeves to lose together.

## Next experiment
Continue paper tracking operations, complete I005 production-style validation, and obtain tax-professional confirmation before any implementation decision.

## Do not do next
- Do not run new weight optimization from I003.6.
- Do not add a new sleeve as a reaction to this audit.
- Do not relabel P08_IEF30 beyond strengthened candidate status.
