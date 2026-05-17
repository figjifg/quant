# D014 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| z_score_window_grid | [36, 48, 60, 72, 84] |
| macro_gate | D013 variables, factor blocks, signs, threshold -0.2, selection, costs, and rebalance are unchanged; only z-score window varies |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Grid Summary

| window | net_cum | cost0_cum | Sharpe | MaxDD | pos_years | annualized | ON_share | trades | 2010-2017_net | 2018-2026_net | 2010-2014_trades | 2010-2014_net | composite_mean | composite_std | composite_positive_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36.0 | 1.2089924261849547 | 1.4452635520856925 | 0.30061602794316405 | -0.41800741433772404 | 7.0 | 0.054330267209729444 | 0.5245901639344263 | 155.0 | -0.1642972160321734 | 1.6422146364362797 | 20.0 | -0.11530293526238955 | 0.037691919136321916 | 0.45777655053852717 | 0.5434782608695652 |
| 48.0 | 1.9768396305934783 | 2.2414636513166486 | 0.43498107792439267 | -0.3392346174957135 | 7.0 | 0.07553742918705231 | 0.4426229508196721 | 130.0 | -0.056013565443905344 | 2.1522118803775654 | 0.0 | 0.0 | -0.010760422246329863 | 0.4203574761432307 | 0.38095238095238093 |
| 60.0 | 2.5457702903350135 | 2.8099324519098956 | 0.5333654677635088 | -0.3392346174957135 | 7.0 | 0.08816790559736765 | 0.3770491803278688 | 110.0 | 0.09401472235486108 | 2.239762293090378 | 0.0 | 0.0 | -0.03428530665464613 | 0.40416182915908916 | 0.39473684210526316 |
| 72.0 | 1.3324974257347288 | 1.4825788697656934 | 0.33332674836656756 | -0.48094774438612775 | 5.0 | 0.05816621235508945 | 0.3114754098360656 | 95.0 | 0.0 | 1.3315615740077287 | 0.0 | 0.0 | -0.07640668398066434 | 0.4082681800907421 | 0.35294117647058826 |
| 84.0 | 1.4025542645202376 | 1.5314623062128359 | 0.40514725582831074 | -0.3392346174957134 | 5.0 | 0.060258657177189257 | 0.26229508196721313 | 80.0 | 0.0 | 1.4025542645202376 | 0.0 | 0.0 | -0.06798745973362916 | 0.43018260252097235 | 0.36666666666666664 |

## Verdict Summary

| scope | hypothesis | description | value | threshold | passes | verdict | window |
| --- | --- | --- | --- | --- | --- | --- | --- |
| grid | H7 | Pre-registered count of windows with Sharpe >= 0.40 | 3.0 | 3 of 5 for plateau; 4 of 5 for strong plateau | True | PLATEAU | nan |
| window | H1 | 60-month D014 reproduces D013 Sharpe 0.5334 | 0.30061602794316405 | 0.5334 | None |  | 36.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.30061602794316405 | 0.4 | False |  | 36.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 20.0 | >0 for 36mo/48mo | True |  | 36.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.5245901639344263 |  | None |  | 36.0 |
| window | H1 | 60-month D014 reproduces D013 Sharpe 0.5334 | 0.43498107792439267 | 0.5334 | None |  | 48.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.43498107792439267 | 0.4 | True |  | 48.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | False |  | 48.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.4426229508196721 |  | None |  | 48.0 |
| window | H1 | 60-month D014 reproduces D013 Sharpe 0.5334 | 0.5333654677635088 | 0.5334 | True |  | 60.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.5333654677635088 | 0.4 | True |  | 60.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 60.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.3770491803278688 |  | None |  | 60.0 |
| window | H1 | 60-month D014 reproduces D013 Sharpe 0.5334 | 0.33332674836656756 | 0.5334 | None |  | 72.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.33332674836656756 | 0.4 | False |  | 72.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 72.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.3114754098360656 |  | None |  | 72.0 |
| window | H1 | 60-month D014 reproduces D013 Sharpe 0.5334 | 0.40514725582831074 | 0.5334 | None |  | 84.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.40514725582831074 | 0.4 | True |  | 84.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 84.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.26229508196721313 |  | None |  | 84.0 |

## Reproduction Check

- 60mo Sharpe: 0.5333654677635088
