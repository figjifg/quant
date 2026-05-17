# D010 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| z_score_window_grid | [36, 48, 60, 72, 84] |
| macro_gate | D009 variables, factor blocks, signs, threshold, selection, costs, and rebalance are unchanged; only z-score window varies |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Grid Summary

| window | net_cum | cost0_cum | Sharpe | MaxDD | pos_years | annualized | ON_share | trades | 2010-2017_net | 2018-2026_net | 2010-2014_trades | 2010-2014_net | composite_mean | composite_std | composite_positive_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36.0 | 1.0718741666171416 | 1.2422867576364762 | 0.31836179076818916 | -0.3336818664706048 | 5.0 | 0.04982963163975973 | 0.4098360655737705 | 120.0 | -0.038746384844015824 | 1.154522854629282 | 20.0 | -0.11530293526238955 | 0.037691919136321916 | 0.45777655053852717 | 0.5434782608695652 |
| 48.0 | 1.3080507154536813 | 1.4234154559881729 | 0.4224498634487824 | -0.34232184209223526 | 4.0 | 0.05742221753640253 | 0.26229508196721313 | 75.0 | 0.09401472235486108 | 1.1088607174720866 | 0.0 | 0.0 | -0.010760422246329863 | 0.4203574761432307 | 0.38095238095238093 |
| 60.0 | 1.0244143636045604 | 1.1188556327370036 | 0.36524689410364136 | -0.3336818664706047 | 4.0 | 0.04820688257946193 | 0.2459016393442623 | 70.0 | 0.09401472235486108 | 0.8497028244254743 | 0.0 | 0.0 | -0.03428530665464613 | 0.40416182915908916 | 0.39473684210526316 |
| 72.0 | 1.2126283827568458 | 1.3008358872632821 | 0.417558089653482 | -0.3423218420922356 | 3.0 | 0.05444602530833742 | 0.19672131147540983 | 60.0 | 0.0 | 1.2117406252526504 | 0.0 | 0.0 | -0.07640668398066434 | 0.4082681800907421 | 0.35294117647058826 |
| 84.0 | 1.2940096492430464 | 1.3777042738173986 | 0.4462228263739947 | -0.34232184209223526 | 3.0 | 0.056991569288500576 | 0.18032786885245902 | 55.0 | 0.0 | 1.2940096492430464 | 0.0 | 0.0 | -0.06798745973362916 | 0.43018260252097235 | 0.36666666666666664 |

## Verdict Summary

| scope | hypothesis | description | value | threshold | passes | verdict | window |
| --- | --- | --- | --- | --- | --- | --- | --- |
| grid | H7 | Pre-registered count of windows with Sharpe >= 0.40 | 3.0 | 3 of 5 for plateau; 4 of 5 for strong plateau | True | PLATEAU | nan |
| window | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.31836179076818916 | 0.4144 | None |  | 36.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.31836179076818916 | 0.4 | False |  | 36.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 20.0 | >0 for 36mo/48mo | True |  | 36.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.4098360655737705 |  | None |  | 36.0 |
| window | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.4224498634487824 | 0.4144 | None |  | 48.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4224498634487824 | 0.4 | True |  | 48.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | False |  | 48.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.26229508196721313 |  | None |  | 48.0 |
| window | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.36524689410364136 | 0.4144 | False |  | 60.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.36524689410364136 | 0.4 | False |  | 60.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 60.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.2459016393442623 |  | None |  | 60.0 |
| window | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.417558089653482 | 0.4144 | None |  | 72.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.417558089653482 | 0.4 | True |  | 72.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 72.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.19672131147540983 |  | None |  | 72.0 |
| window | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.4462228263739947 | 0.4144 | None |  | 84.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4462228263739947 | 0.4 | True |  | 84.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 84.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.18032786885245902 |  | None |  | 84.0 |

## Reproduction Check

- 60mo Sharpe: 0.36524689410364136
