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
| 36.0 | 1.0718741666171416 | 1.2422867576364762 | 0.31836179076818916 | -0.3336818664706048 | 5.0 | 0.04982963163975973 | 0.4098360655737705 | 120.0 | -0.038746384844015824 | 1.154522854629282 | 20.0 | -0.11530293526238955 | 0.04049802265046464 | 0.47059396684605587 | 0.5434782608695652 |
| 48.0 | 1.391481205037107 | 1.5276487593934163 | 0.4295609629982839 | -0.33368186647060516 | 5.0 | 0.059931749131977075 | 0.29508196721311475 | 85.0 | -0.03022297575220423 | 1.4650219874126038 | 0.0 | 0.0 | -0.007285420252061863 | 0.43514459802287203 | 0.42857142857142855 |
| 60.0 | 1.2562437299125393 | 1.3693725156582923 | 0.4144010855755797 | -0.3336818664706047 | 5.0 | 0.05582094116655911 | 0.26229508196721313 | 75.0 | 0.09401472235486108 | 1.061524791980136 | 0.0 | 0.0 | -0.033479997767023525 | 0.41738983159305604 | 0.42105263157894735 |
| 72.0 | 1.2126283827568458 | 1.3008358872632821 | 0.417558089653482 | -0.3423218420922356 | 3.0 | 0.05444602530833742 | 0.19672131147540983 | 60.0 | 0.0 | 1.2117406252526504 | 0.0 | 0.0 | -0.07519914139633048 | 0.42151326641190784 | 0.35294117647058826 |
| 84.0 | 1.2940096492430464 | 1.3777042738173986 | 0.4462228263739947 | -0.34232184209223526 | 3.0 | 0.056991569288500576 | 0.18032786885245902 | 55.0 | 0.0 | 1.2940096492430464 | 0.0 | 0.0 | -0.06239489082172472 | 0.4430646279323535 | 0.36666666666666664 |

## Verdict Summary

| scope | hypothesis | description | value | threshold | passes | verdict | window |
| --- | --- | --- | --- | --- | --- | --- | --- |
| grid | H7 | Pre-registered count of windows with Sharpe >= 0.40 | 4.0 | 3 of 5 for plateau; 4 of 5 for strong plateau | True | STRONG PLATEAU | nan |
| window | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.31836179076818916 | 0.4144 | None |  | 36.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.31836179076818916 | 0.4 | False |  | 36.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 20.0 | >0 for 36mo/48mo | True |  | 36.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.4098360655737705 |  | None |  | 36.0 |
| window | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.4295609629982839 | 0.4144 | None |  | 48.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4295609629982839 | 0.4 | True |  | 48.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | False |  | 48.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.29508196721311475 |  | None |  | 48.0 |
| window | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.4144010855755797 | 0.4144 | True |  | 60.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4144010855755797 | 0.4 | True |  | 60.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 60.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.26229508196721313 |  | None |  | 60.0 |
| window | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.417558089653482 | 0.4144 | None |  | 72.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.417558089653482 | 0.4 | True |  | 72.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 72.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.19672131147540983 |  | None |  | 72.0 |
| window | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.4462228263739947 | 0.4144 | None |  | 84.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4462228263739947 | 0.4 | True |  | 84.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 84.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.18032786885245902 |  | None |  | 84.0 |

## Reproduction Check

- 60mo Sharpe: 0.4144010855755797
