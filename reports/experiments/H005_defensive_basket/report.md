# H005 Defensive Basket Sleeve

## Portfolio Metrics

| variant | cumulative_net_total_return | sharpe | max_drawdown | sleeve_max_drawdown |
|---|---:|---:|---:|---:|
| D013 | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 | 0.0 |
| H001 | 3.571886489071015 | 0.6461391042868482 | -0.3392346174957135 | 0.0 |
| H002 | 2.7271802643580934 | 0.5544017014515334 | -0.3392346174957135 | -0.17252455316907733 |
| H003 | 4.013998939785267 | 0.6859100455847053 | -0.3392346174957135 | -0.13468957391253422 |
| H005 | 3.511606452694571 | 0.6399017157075155 | -0.3392346174957135 | -0.05183999017273444 |

## Basket Decomposition

- OFF basket cumulative contribution: 0.2723910697182603
- Basket sleeve max drawdown: -0.05183999017273444
- OFF basket quarters: 38
- Weights: KR carry 0.5, USD 0.25, Treasury 0.25.

## Verdict

- Overall: FAIL
- Cumulative > +254% D013 threshold: True (3.511606452694571)
- Sharpe >= 0.65: False (0.6399017157075155)
- Basket sleeve drawdown >= -0.08: True (-0.05183999017273444)
- H-family champion sleeve: H001

## Metadata

- Carrier: D013 top 5 unchanged.
- OFF sleeve: fixed defensive basket replaces zero-return cash in D013 OFF quarters.
- Basket option A was pre-registered; no post-run weight fitting was applied.
- KR short-rate source: research_input_data/inputs/macro_features/fred_kr_short_rate.csv.
- USDKRW source: research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv.
- US 10Y yield source: research_input_data/inputs/macro_features/fred_dgs10.csv.
- D013 strategy and backtest engine were not modified.
