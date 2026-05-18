# E004 Flow Score Only Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- sector_aggregate_csv: data/processed/sector_aggregate_daily.csv
- score: z-score across sectors of average(flow_by_value_20d, flow_by_mcap_60d)
- timing: signal quarter-end T uses sector data through T; execution is T+1 or later
- thin_sector_policy: n_stocks <= 2 excluded from score and Top-K selection
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## Diagnostic Verdict

- verdict: FAIL
- rank_ic_mean: 0.00392449080973671
- rank_ic_std: 0.32265290137571656
- rank_ic_t_stat: 0.09499760561319921
- top_bottom_spread_mean: -0.014680903435069004
- top_bottom_spread_std: 0.14918910406006367
- top_bottom_spread_t_stat: -0.7685649834695819
- positive_spread_ratio: 0.5081967213114754

## Subperiod Diagnostics

| period | n_quarters | rank_ic_mean | rank_ic_std | rank_ic_t_stat | spread_mean | spread_std | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010_2017 | 28 | 0.0025974025974025822 | 0.3142747822664726 | 0.0437329478227982 | -0.020738214099048625 | 0.1532165992328457 | -0.7162168774978757 | 0.4642857142857143 |
| 2018_2026 | 33 | 0.005050505050505055 | 0.3344514765666245 | 0.08674783845214529 | -0.0095413671141166 | 0.14787140515322958 | -0.37066653328859284 | 0.5454545454545454 |
| spike_years_2020_2025_2026 | 9 | -0.06863876863876861 | 0.3436454539283445 | -0.5992114941792381 | -0.04386711728345161 | 0.22887140503786452 | -0.5750012843613325 | 0.4444444444444444 |
| excluding_spike_years | 52 | 0.016483516483516477 | 0.32072116494365366 | 0.3706157895236876 | -0.009629443345925862 | 0.13338672606473595 | -0.5205833108320087 | 0.5192307692307693 |
| year_2020 | 4 | 0.021212121212121238 | 0.46988266124126127 | 0.09028688633067 | 0.0187442708412772 | 0.3195931938071717 | 0.11730081368745705 | 0.75 |
| year_2025 | 4 | -0.11958874458874455 | 0.2680047329041119 | -0.8924375572988975 | -0.08076327582284362 | 0.16424688073643062 | -0.9834375601013164 | 0.25 |
| year_2026 | 1 | -0.22424242424242422 | nan | nan | -0.1467280356247988 | nan | nan | 0.0 |

## Comparison With E003

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count |
| --- | --- | --- | --- | --- |
| E003_A_d013_replication | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 | 110 |

## Portfolio

Portfolio skipped because the pre-registered diagnostic pass rule was not met.

