# E009 Cost Stress Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- carrier: E007 Flow + RS + Breadth, Top 3 sectors, holdings 2/2/1
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2
- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later

## Cost Stress Summary

| scenario | commission_bps | tax_bps_sell | slippage_bps | cumulative_net_total_return | sharpe | max_drawdown | trade_count | base_exact_e007_reproduction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 1.5 | 20.0 | 5.0 | 2.3200922451001436 | 0.48218421304767917 | -0.3968185249283369 | 110 | True |
| 2x | 3.0 | 40.0 | 10.0 | 2.0842981130375198 | 0.4515389906736061 | -0.4028142875610403 | 110 | False |
| 3x | 4.5 | 60.0 | 15.0 | 1.8648281409169454 | 0.4207661719712188 | -0.408762298650895 | 110 | False |
| extra_slippage | 1.5 | 20.0 | 15.0 | 2.172883963031972 | 0.46328759057992086 | -0.4004858621248141 | 110 | False |

## D018 D013 Comparison

| scenario | d018_d013_cumulative_net_total_return | d018_d013_sharpe | d018_d013_max_drawdown |
| --- | --- | --- | --- |
| base | 2.545770290335013 | 0.533365467763508 | -0.339234617495713 |
| 3x | 2.069773268014911 | 0.469941650517947 | -0.350933535588211 |

## Verdict Checks

- base_exact_e007_reproduction: True
- 3x cumulative_net_total_return >= 0: True
- 3x sharpe >= 0.20: True

