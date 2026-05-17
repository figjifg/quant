# D007 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| on_threshold_grid | [-0.2, -0.1, 0.0, 0.1, 0.2] |
| macro_gate | D001 variables, 60-month z-score window, factor blocks, signs, selection, costs, and rebalance are unchanged; only composite threshold varies |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Grid Summary

| threshold | net_cum | cost0_cum | Sharpe | MaxDD | pos_years | annualized | ON_share | trades | 2010-2017_net | 2018-2026_net | composite_mean | composite_std | composite_positive_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| -0.2 | 1.02128620381291 | 1.1435497860841397 | 0.34651678156753457 | -0.3392346174957135 | 4.0 | 0.04809868103722037 | 0.29508196721311475 | 90.0 | 0.0 | 1.02128620381291 | -0.22008966303812005 | 0.5317946006029692 | 0.4375 |
| -0.1 | 1.0278448541003073 | 1.1288669005414995 | 0.3699827913567774 | -0.3392346174957134 | 4.0 | 0.048325362358622836 | 0.2459016393442623 | 75.0 | 0.0 | 1.0278448541003073 | -0.22008966303812005 | 0.5317946006029692 | 0.4375 |
| 0.0 | 1.2906841868750734 | 1.397144393892741 | 0.48422119520674023 | -0.23673459774712757 | 4.0 | 0.05688921504561084 | 0.22950819672131148 | 70.0 | 0.0 | 1.2906841868750734 | -0.22008966303812005 | 0.5317946006029692 | 0.4375 |
| 0.1 | 1.1277032286836755 | 1.211784075726539 | 0.4704346395631132 | -0.23673459774712757 | 4.0 | 0.05169471490382094 | 0.19672131147540983 | 60.0 | 0.0 | 1.1277032286836755 | -0.22008966303812005 | 0.5317946006029692 | 0.4375 |
| 0.2 | 0.503614974972816 | 0.5478772935349889 | 0.28286169332397637 | -0.266477947631111 | 3.0 | 0.027601550056027824 | 0.14754098360655737 | 45.0 | 0.0 | 0.503614974972816 | -0.22008966303812005 | 0.5317946006029692 | 0.4375 |

## Verdict Summary

| scope | hypothesis | description | value | threshold | passes | verdict | threshold_value |
| --- | --- | --- | --- | --- | --- | --- | --- |
| grid | H7 | Pre-registered count of thresholds with Sharpe >= 0.40 | 2.0 | 3 of 5 for plateau; 4 of 5 for strong plateau | False | MARGINAL | nan |
| threshold | H1 | Threshold 0.0 reproduces D001 Sharpe 0.4842 | 0.34651678156753457 | -0.2 | None |  | 0.4842 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.34651678156753457 | -0.2 | False |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.29508196721311475 | -0.2 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D001 Sharpe 0.4842 | 0.3699827913567774 | -0.1 | None |  | 0.4842 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.3699827913567774 | -0.1 | False |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.2459016393442623 | -0.1 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D001 Sharpe 0.4842 | 0.48422119520674023 | 0.0 | True |  | 0.4842 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.48422119520674023 | 0.0 | True |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.22950819672131148 | 0.0 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D001 Sharpe 0.4842 | 0.4704346395631132 | 0.1 | None |  | 0.4842 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.4704346395631132 | 0.1 | True |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.19672131147540983 | 0.1 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D001 Sharpe 0.4842 | 0.28286169332397637 | 0.2 | None |  | 0.4842 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.28286169332397637 | 0.2 | False |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.14754098360655737 | 0.2 | None |  |  |

## Reproduction Check

- Threshold 0.0 Sharpe: 0.48422119520674023
