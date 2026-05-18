# E012 Top4 Robustness Ablation Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- carrier: E011 Top4 unless the table explicitly changes score or Top-K
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2
- lookback_robustness: skipped

## Score Ablation

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | c_exact_e011 |
| --- | --- | --- | --- | --- | --- |
| rs_only | 2.274400843657125 | 0.44164946695733176 | -0.4360686013626559 | 110 | False |
| rs_breadth | 3.621084739339225 | 0.6311872415922518 | -0.35641869371448887 | 110 | False |
| flow_rs_breadth | 2.9652796624027413 | 0.5660027769289406 | -0.41474162966818906 | 110 | True |

## Pre-Registered Flow Verdict

- flow_main_alpha: False

## Top-K Grid

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | top_k | top_sector_stock_counts |
| --- | --- | --- | --- | --- | --- | --- |
| top_3 | 2.3200922451001436 | 0.48218421304767917 | -0.3968185249283369 | 110 | 3 | 2/2/1 |
| top_4 | 2.9652796624027413 | 0.5660027769289406 | -0.41474162966818906 | 110 | 4 | 2/1/1/1 |
| top_5 | 2.270205965794112 | 0.5146640851015111 | -0.36582185935250466 | 110 | 5 | 1/1/1/1/1 |

## Cost Stress

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | commission_bps | tax_bps_sell | slippage_bps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| base | 2.9652796624027413 | 0.5660027769289406 | -0.41474162966818906 | 110 | 1.5 | 20.0 | 5.0 |
| 2x | 2.687449524208444 | 0.5348705780681344 | -0.42058350129612654 | 110 | 3.0 | 40.0 | 10.0 |
| 3x | 2.4285814010127074 | 0.5035685083516096 | -0.42637855765402266 | 110 | 4.5 | 60.0 | 15.0 |
| extra_slippage | 2.795457664052093 | 0.5471930444315489 | -0.4183374770698004 | 110 | 1.5 | 20.0 | 15.0 |

## Robustness Verdict

- topk_sharpe_ge_0p40_count: 3

