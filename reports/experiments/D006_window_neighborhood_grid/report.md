# D006 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| z_score_window_grid | [36, 48, 60, 72, 84] |
| macro_gate | D001 variables, factor blocks, signs, threshold, selection, costs, and rebalance are unchanged; only z-score window varies |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Grid Summary

| window | net_cum | cost0_cum | Sharpe | MaxDD | pos_years | annualized | ON_share | trades | 2010-2017_net | 2018-2026_net | 2010-2014_trades | 2010-2014_net | composite_mean | composite_std | composite_positive_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36.0 | 0.9310997700227825 | 1.054637548874438 | 0.3163979756328085 | -0.3392346174957135 | 4.0 | 0.04490999665703166 | 0.3114754098360656 | 95.0 | -0.026594350089605312 | 0.9838592165563729 | 0.0 | 0.0 | -0.07804286132658746 | 0.5055833984556 | 0.475 |
| 48.0 | 1.3032394319755864 | 1.42619120722446 | 0.4687319570751616 | -0.22305633883403753 | 4.0 | 0.057274928501143796 | 0.26229508196721313 | 80.0 | 0.0 | 1.3032394319755864 | 0.0 | 0.0 | -0.16869428293410313 | 0.504675237849478 | 0.4444444444444444 |
| 60.0 | 1.2906841868750734 | 1.397144393892741 | 0.48422119520674023 | -0.23673459774712757 | 4.0 | 0.05688921504561084 | 0.22950819672131148 | 70.0 | 0.0 | 1.2906841868750734 | 0.0 | 0.0 | -0.22008966303812005 | 0.5317946006029692 | 0.4375 |
| 72.0 | 1.1947792772228127 | 1.2893618637045297 | 0.4756713625654831 | -0.23673459774712757 | 4.0 | 0.05387604987188732 | 0.21311475409836064 | 65.0 | 0.0 | 1.1947792772228127 | 0.0 | 0.0 | -0.172155889429335 | 0.4932325992929362 | 0.4642857142857143 |
| 84.0 | 1.132793427600841 | 1.2103387037586275 | 0.4783455711739302 | -0.2367345977471278 | 3.0 | 0.05186248426144635 | 0.18032786885245902 | 55.0 | 0.0 | 1.132793427600841 | 0.0 | 0.0 | -0.22175200429375552 | 0.5342522616770242 | 0.4583333333333333 |

## Verdict Summary

| scope | hypothesis | description | value | threshold | passes | verdict | window |
| --- | --- | --- | --- | --- | --- | --- | --- |
| grid | H7 | Pre-registered count of windows with Sharpe >= 0.40 | 4.0 | 3 of 5 for plateau; 4 of 5 for strong plateau | True | STRONG PLATEAU | nan |
| window | H1 | 60-month D006 reproduces D001 Sharpe 0.4842 | 0.3163979756328085 | 0.4842 | None |  | 36.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.3163979756328085 | 0.4 | False |  | 36.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | False |  | 36.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.3114754098360656 |  | None |  | 36.0 |
| window | H1 | 60-month D006 reproduces D001 Sharpe 0.4842 | 0.4687319570751616 | 0.4842 | None |  | 48.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4687319570751616 | 0.4 | True |  | 48.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | False |  | 48.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.26229508196721313 |  | None |  | 48.0 |
| window | H1 | 60-month D006 reproduces D001 Sharpe 0.4842 | 0.48422119520674023 | 0.4842 | True |  | 60.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.48422119520674023 | 0.4 | True |  | 60.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 60.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.22950819672131148 |  | None |  | 60.0 |
| window | H1 | 60-month D006 reproduces D001 Sharpe 0.4842 | 0.4756713625654831 | 0.4842 | None |  | 72.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4756713625654831 | 0.4 | True |  | 72.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 72.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.21311475409836064 |  | None |  | 72.0 |
| window | H1 | 60-month D006 reproduces D001 Sharpe 0.4842 | 0.4783455711739302 | 0.4842 | None |  | 84.0 |
| window | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4783455711739302 | 0.4 | True |  | 84.0 |
| window | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |  | 84.0 |
| window | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.18032786885245902 |  | None |  | 84.0 |

## Reproduction Check

- 60mo Sharpe: 0.48422119520674023
