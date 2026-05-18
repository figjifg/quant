# H003 US Treasury Sleeve

## Portfolio Metrics

| variant | cumulative_net_total_return | sharpe | max_drawdown |
|---|---:|---:|---:|
| D013 baseline | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 |
| D013 + US Treasury | 4.013998939785267 | 0.6859100455847053 | -0.3392346174957135 |

## Sleeve Comparison

- H001 KR carry cumulative net return: 3.571886489071015
- H002 USDKRW cumulative net return: 2.7271802643580934
- H003 minus H001 cumulative net return: 0.4421124507142524
- Treasury sleeve cumulative contribution: 0.41407889660874675
- Treasury sleeve max drawdown: -0.13468957391253422
- 2022 Treasury sleeve compounded impact: 0.030362280349587545

## Verdict

- Overall: FAIL
- Cumulative improves vs D013: True (1.4682286494502539)
- Sharpe >= 0.53: True (0.6859100455847053)
- Treasury sleeve drawdown >= -0.10: False (-0.13468957391253422)
- H004 Gold 가치: Treasury가 금리 상승기에 손실을 낸다면 H004 Gold는 rate-rise hedge 후보로 가치가 있다.
- H005 basket 진행 권고: H003는 단독 기준을 통과하지 못했으므로 H001 KR carry 중심 basket에 Treasury를 제한 비중 후보로만 검토한다.

## Metadata

- Carrier: D013 top 5 unchanged.
- OFF sleeve: simple US 10Y Treasury return translated to KRW replaces zero-return cash in D013 OFF quarters.
- US 10Y yield source: research_input_data/inputs/macro_features/fred_dgs10.csv.
- USDKRW source: research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv.
- Effective duration: 7.0.
- Formula: `-delta_yield_decimal * 7 + start_yield_decimal / 4 + usdkrw_quarter_return`.
- D013 strategy and backtest engine were not modified.
