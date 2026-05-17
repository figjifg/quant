# D011 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| on_threshold_grid | [-0.2, -0.1, 0.0, 0.1, 0.2] |
| macro_gate | D009 variables, 60-month z-score window, factor blocks, signs, selection, costs, and rebalance are unchanged; only composite threshold varies |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Grid Summary

| threshold | net_cum | cost0_cum | Sharpe | MaxDD | pos_years | annualized | ON_share | trades | 2010-2017_net | 2018-2026_net | composite_mean | composite_std | composite_positive_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| -0.2 | 2.5457702903350135 | 2.8099324519098956 | 0.5333654677635088 | -0.3392346174957135 | 7.0 | 0.08816790559736765 | 0.3770491803278688 | 110.0 | 0.09401472235486108 | 2.239762293090378 | -0.033479997767023525 | 0.41738983159305604 | 0.42105263157894735 |
| -0.1 | 1.535184731805431 | 1.6973069627318877 | 0.4163435506054858 | -0.3392346174957135 | 6.0 | 0.06406865037187481 | 0.32786885245901637 | 95.0 | 0.09401472235486108 | 1.3163925543934925 | -0.033479997767023525 | 0.41738983159305604 | 0.42105263157894735 |
| 0.0 | 1.2562437299125393 | 1.3693725156582923 | 0.4144010855755797 | -0.3336818664706047 | 5.0 | 0.05582094116655911 | 0.26229508196721313 | 75.0 | 0.09401472235486108 | 1.061524791980136 | -0.033479997767023525 | 0.41738983159305604 | 0.42105263157894735 |
| 0.1 | 1.2012657144272754 | 1.289087724461913 | 0.4258966812133466 | -0.33368186647060516 | 4.0 | 0.05408367996462138 | 0.21311475409836064 | 60.0 | 0.09401472235486108 | 1.012098804017063 | -0.033479997767023525 | 0.41738983159305604 | 0.42105263157894735 |
| 0.2 | 0.7558065692171194 | 0.8143008698803009 | 0.33705329365403236 | -0.33368186647060516 | 3.0 | 0.03829325318144794 | 0.18032786885245902 | 50.0 | 0.09401472235486108 | 0.6049204213977621 | -0.033479997767023525 | 0.41738983159305604 | 0.42105263157894735 |

## Verdict Summary

| scope | hypothesis | description | value | threshold | passes | verdict | threshold_value |
| --- | --- | --- | --- | --- | --- | --- | --- |
| grid | H7 | Pre-registered count of thresholds with Sharpe >= 0.40 | 4.0 | 3 of 5 for plateau; 4 of 5 for strong plateau | True | STRONG PLATEAU | nan |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.5333654677635088 | -0.2 | None |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.5333654677635088 | -0.2 | True |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.3770491803278688 | -0.2 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.4163435506054858 | -0.1 | None |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.4163435506054858 | -0.1 | True |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.32786885245901637 | -0.1 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.4144010855755797 | 0.0 | True |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.4144010855755797 | 0.0 | True |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.26229508196721313 | 0.0 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.4258966812133466 | 0.1 | None |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.4258966812133466 | 0.1 | True |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.21311475409836064 | 0.1 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.33705329365403236 | 0.2 | None |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.33705329365403236 | 0.2 | False |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.18032786885245902 | 0.2 | None |  |  |

## Reproduction Check

- Threshold 0.0 Sharpe: 0.4144010855755797
