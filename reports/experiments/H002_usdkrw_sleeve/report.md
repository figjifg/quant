# H002 USDKRW Sleeve

## Portfolio Metrics

| variant | cumulative_net_total_return | sharpe | max_drawdown |
|---|---:|---:|---:|
| D013 baseline | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 |
| D013 + USDKRW | 2.7271802643580934 | 0.5544017014515334 | -0.3392346174957135 |

## OFF FX Contribution

- OFF FX cumulative contribution: 0.0511623594223245
- OFF FX quarters: 38
- KRW weakening compounded contribution: 1.0902355033576585
- FX sleeve max drawdown: -0.17252455316907733
- H001 KR carry cumulative uplift vs D013: 1.0261161987360017

## Verdict

- Overall: FAIL
- Cumulative improves vs D013: True (0.1814099740230799)
- Sharpe >= 0.53: True (0.5544017014515334)
- MDD worsening <= 0.05: True (0.0)
- FX sleeve drawdown >= -0.05: False (-0.17252455316907733)
- H003/H005 진행 권고: H002는 FX drawdown 기준에서 실패했으므로 H003/H005 defensive sleeve를 우선 검토한다.

## Metadata

- Carrier: D013 top 5 unchanged.
- OFF sleeve: USD cash marked in KRW replaces zero-return cash in D013 OFF quarters.
- USDKRW source: research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv.
- USD carry assumption: 0.0.
- FX formula: `end_usdkrw / start_usdkrw - 1`, aligned from signal_date T to next quarter signal_date T+1Q.
- D013 strategy and backtest engine were not modified.
