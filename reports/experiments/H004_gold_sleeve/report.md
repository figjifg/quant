# H004 Gold Sleeve

## Portfolio Metrics

| variant | cumulative_net_total_return | sharpe | max_drawdown | sleeve_max_drawdown |
|---|---:|---:|---:|---:|
| D013 | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 | 0.0 |
| H001 | 3.571886489071015 | 0.6461391042868482 | -0.3392346174957135 | <NA> |
| H002 | 2.7271802643580934 | 0.5544017014515334 | -0.3392346174957135 | -0.1725245531690773 |
| H003 | 4.013998939785267 | 0.6859100455847053 | -0.3392346174957135 | -0.1346895739125342 |
| H005 | 3.511606452694571 | 0.6399017157075155 | -0.3392346174957135 | -0.0518399901727344 |
| H004 | 3.0913047840293464 | 0.593506299110405 | -0.44267311057475944 | -0.4023092753584948 |

## Required Findings

- D013 + Gold cumulative/Sharpe/MDD: 3.0913047840293464 / 0.593506299110405 / -0.44267311057475944
- H001 KR carry cumulative/Sharpe: 3.571886489071015 / 0.6461391042868482
- H004 minus H001 cumulative net return: -0.4805817050416685
- 2010-Q1~Q3 cash fallback rows: 3; compounded impact: 0.0
- 2022 gold sleeve compounded impact: -0.004230769230769371
- Gold sleeve max DD: -0.4023092753584948

## Verdict

- Overall: FAIL
- Cumulative > +254% D013 threshold: True (3.0913047840293464)
- Sharpe >= 0.53: True (0.593506299110405)
- Gold sleeve drawdown >= -0.15: False (-0.4023092753584948)
- H-family champion final decision: H001

## Metadata

- Carrier: D013 top 5 unchanged.
- OFF sleeve: KODEX 골드선물(H) 132030 close-to-close KRW return replaces zero-return cash in D013 OFF quarters.
- Gold ETF source: research_input_data/inputs/macro_features/krx_kodex_gold_132030.csv.
- Price column: close. USDKRW translation: none.
- Inception policy: signal dates before 2010-10-01 use pre-registered cash fallback return 0.
- D013 strategy and backtest engine were not modified.
