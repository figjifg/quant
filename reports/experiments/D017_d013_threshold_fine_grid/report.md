# D011 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| on_threshold_grid | [-0.4, -0.3, -0.25, -0.2, -0.15, -0.1, 0.0] |
| macro_gate | D009 variables, 60-month z-score window, factor blocks, signs, selection, costs, and rebalance are unchanged; only composite threshold varies |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Grid Summary

| threshold | net_cum | cost0_cum | Sharpe | MaxDD | pos_years | annualized | ON_share | trades | 2010-2017_net | 2018-2026_net | composite_mean | composite_std | composite_positive_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| -0.4 | 0.6156561801244 | 0.7890975571356187 | 0.16184795262514606 | -0.5974704381808513 | 6.0 | 0.03254342845671032 | 0.5409836065573771 | 155.0 | 0.09401472235486108 | 0.4762213968663245 | -0.03428530665464613 | 0.40416182915908916 | 0.39473684210526316 |
| -0.3 | 1.7888548181431099 | 2.0273913643712933 | 0.3740767236395032 | -0.48094774438612786 | 7.0 | 0.07086417952805024 | 0.4426229508196721 | 125.0 | 0.09401472235486108 | 1.54817033843154 | -0.03428530665464613 | 0.40416182915908916 | 0.39473684210526316 |
| -0.25 | 2.4499504047323755 | 2.720135784269507 | 0.5108089762888298 | -0.3392346174957135 | 7.0 | 0.08617969317031471 | 0.39344262295081966 | 115.0 | 0.09401472235486108 | 2.152211880377565 | -0.03428530665464613 | 0.40416182915908916 | 0.39473684210526316 |
| -0.2 | 2.5457702903350135 | 2.8099324519098956 | 0.5333654677635088 | -0.3392346174957135 | 7.0 | 0.08816790559736765 | 0.3770491803278688 | 110.0 | 0.09401472235486108 | 2.239762293090378 | -0.03428530665464613 | 0.40416182915908916 | 0.39473684210526316 |
| -0.15 | 2.401527319295397 | 2.631508419179685 | 0.5365747279341907 | -0.3392346174957135 | 6.0 | 0.08515525485170183 | 0.3442622950819672 | 100.0 | 0.09401472235486108 | 2.1079678167557803 | -0.03428530665464613 | 0.40416182915908916 | 0.39473684210526316 |
| -0.1 | 1.535184731805431 | 1.6973069627318877 | 0.4163435506054858 | -0.3392346174957135 | 6.0 | 0.06406865037187481 | 0.32786885245901637 | 95.0 | 0.09401472235486108 | 1.3163925543934925 | -0.03428530665464613 | 0.40416182915908916 | 0.39473684210526316 |
| 0.0 | 1.0244143636045604 | 1.1188556327370036 | 0.36524689410364136 | -0.3336818664706047 | 4.0 | 0.04820688257946193 | 0.2459016393442623 | 70.0 | 0.09401472235486108 | 0.8497028244254743 | -0.03428530665464613 | 0.40416182915908916 | 0.39473684210526316 |

## Verdict Summary

| scope | hypothesis | description | value | threshold | passes | verdict | threshold_value |
| --- | --- | --- | --- | --- | --- | --- | --- |
| grid | H7 | Pre-registered count of thresholds with Sharpe >= 0.40 | 4.0 | 3 of 5 for plateau; 4 of 5 for strong plateau | True | STRONG PLATEAU | nan |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.16184795262514606 | -0.4 | None |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.16184795262514606 | -0.4 | False |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.5409836065573771 | -0.4 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.3740767236395032 | -0.3 | None |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.3740767236395032 | -0.3 | False |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.4426229508196721 | -0.3 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.5108089762888298 | -0.25 | None |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.5108089762888298 | -0.25 | True |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.39344262295081966 | -0.25 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.5333654677635088 | -0.2 | None |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.5333654677635088 | -0.2 | True |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.3770491803278688 | -0.2 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.5365747279341907 | -0.15 | None |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.5365747279341907 | -0.15 | True |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.3442622950819672 | -0.15 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.4163435506054858 | -0.1 | None |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.4163435506054858 | -0.1 | True |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.32786885245901637 | -0.1 | None |  |  |
| threshold | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.36524689410364136 | 0.0 | False |  | 0.4144 |
| threshold | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.36524689410364136 | 0.0 | False |  | 0.4 |
| threshold | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.2459016393442623 | 0.0 | None |  |  |

## Reproduction Check

- Threshold 0.0 Sharpe: 0.36524689410364136
