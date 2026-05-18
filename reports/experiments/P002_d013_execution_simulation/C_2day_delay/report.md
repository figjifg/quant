# P002 C_2day_delay

## Metadata

| key | value |
| --- | --- |
| scenario | C: 2-day delay |
| carrier | D013 unchanged: 10 variables, 5 blocks, 60-month z-score, threshold -0.2, market-cap top 5 |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| price_data | panel OHLCV only |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Metrics

| cumulative | Sharpe | MDD | trades | fallback count | fallback frequency |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3.0868867301556984 | 0.5973210992849247 | -0.3394736332024365 | 110 | 0 | 0.0 |
