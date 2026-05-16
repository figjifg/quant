# B010 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv"] |
| is_start | 2010-01-04 |
| is_end | 2015-12-30 |
| oos_start | 2017-01-02 |
| oos_end | 2017-12-28 |
| excluded_years | [2016] |
| candidate_years | [2010, 2011, 2012, 2013, 2014, 2015, 2017] |
| filter_candidate | filter_persistence_4_of_5 |
| filter_baseline | filter_flow_sign_both_positive |
| trigger | trigger_acceleration |
| ranking | rank_by_combined_flow_5 |
| exit | exit_signal_reversal on absolute fnv_5/inv_5 |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## IS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| carrier_t3_f3 | -0.6620596144657085 | 0.4121212121212121 | 1485 | -0.023109114712597578 |
| t3_f1_baseline | -0.7203198701081772 | 0.41011984021304926 | 1502 | -0.08633312255016046 |
| cash | 0.0 | 0.0 | 0 | 0.0 |
| cost_0_carrier_t3_f3 | -0.09781484455026868 | 0.4356902356902357 | 1485 | -0.09781484455026868 |
| cost_0_t3_f1_baseline | -0.24468029865789243 | 0.43342210386151797 | 1502 | -0.24468029865789243 |
| cost_0_cash | 0.0 | 0.0 | 0 | 0.0 |

## OOS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| carrier_t3_f3 | -0.14349032823673946 | 0.4396551724137931 | 232 | 0.008640190553208305 |
| t3_f1_baseline | -0.05459684992628744 | 0.463519313304721 | 233 | 0.1038177020980463 |
| cash | 0.0 | 0.0 | 0 | 0.0 |
| cost_0_carrier_t3_f3 | -0.0012636035678923463 | 0.46551724137931033 | 232 | -0.0012636035678923463 |
| cost_0_t3_f1_baseline | 0.10297036008982063 | 0.49356223175965663 | 233 | 0.10297036008982063 |
| cost_0_cash | 0.0 | 0.0 | 0 | 0.0 |

## Full Verification Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| carrier_t3_f3 | -0.7105507913104743 | 0.4158415841584158 | 1717 | -0.020189245385956678 |
| t3_f1_baseline | -0.7355895241872457 | 0.41729106628242074 | 1735 | -0.05729737414230851 |
| cash | 0.0 | 0.0 | 0 | 0.0 |
| cost_0_carrier_t3_f3 | -0.09895484893159445 | 0.43972044263249854 | 1717 | -0.09895484893159445 |
| cost_0_t3_f1_baseline | -0.16690475702775975 | 0.44149855907780977 | 1735 | -0.16690475702775975 |
| cost_0_cash | 0.0 | 0.0 | 0 | 0.0 |

## Old Data Year Breakdown

| year | carrier_t3_f3_net_total_return | carrier_t3_f3_hit_rate | carrier_t3_f3_trade_count | t3_f1_baseline_net_total_return | t3_f1_baseline_hit_rate | t3_f1_baseline_trade_count | cash_net_total_return | cash_hit_rate | cash_trade_count | v1_minus_v2_net_total_return |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.24659704379697867 | 0.5209302325581395 | 215.0 | 0.1619096946795675 | 0.4908256880733945 | 218.0 | 0.0 | 0.0 | 0.0 | 0.08468734911741116 |
| 2011.0 | -0.47924860699566096 | 0.36470588235294116 | 255.0 | -0.365647981190527 | 0.3861003861003861 | 259.0 | 0.0 | 0.0 | 0.0 | -0.11360062580513397 |
| 2012.0 | -0.09294912512723663 | 0.4364406779661017 | 236.0 | -0.25780350486719983 | 0.4163265306122449 | 245.0 | 0.0 | 0.0 | 0.0 | 0.1648543797399632 |
| 2013.0 | -0.37373606459544173 | 0.35793357933579334 | 271.0 | -0.33618803690485566 | 0.3722627737226277 | 274.0 | 0.0 | 0.0 | 0.0 | -0.03754802769058607 |
| 2014.0 | -0.04756354501693172 | 0.40160642570281124 | 249.0 | -0.1163533103285107 | 0.40963855421686746 | 249.0 | 0.0 | 0.0 | 0.0 | 0.06878976531157899 |
| 2015.0 | -0.035513077913599145 | 0.41312741312741313 | 259.0 | -0.13798526505482067 | 0.40077821011673154 | 257.0 | 0.0 | 0.0 | 0.0 | 0.10247218714122153 |
| 2017.0 | -0.14349032823673946 | 0.4396551724137931 | 232.0 | -0.05459684992628744 | 0.463519313304721 | 233.0 | 0.0 | 0.0 | 0.0 | -0.08889347831045202 |

## Verification Diagnostic

| diagnostic | value | threshold | passes |
| --- | --- | --- | --- |
| h1_v1_cost_0_net_gt_0 | -0.09895484893159445 | 0.0 | False |
| h2_v1_net_total_return_ge_-0.20 | -0.7105507913104743 | -0.2 | False |
| h3_v1_positive_years_ge_4_of_7 | 1.0 | 4 | False |
| h4_largest_positive_year_fraction_le_80pct | 1.0 | 0.8 | False |
| h4_total_positive_year_return | 0.24659704379697867 |  |  |
| h5_v1_minus_v2_net_total_return | 0.025038732876771386 |  |  |
| survival_2010_2017_v1_cost_0_full | -0.09895484893159445 |  |  |
| survival_2018_2026_v1_cost_0_oos_from_b009 | 2.4175517306182512 |  |  |

## Cost Sensitivity

| variant | multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- | --- |
| carrier_t3_f3 | 0.0 | -0.09781484455026868 | -0.0012636035678923463 | -0.09895484893159445 | 0.0 |
| carrier_t3_f3 | 1.0 | -0.6620596144657085 | -0.14349032823673946 | -0.7105507913104743 | 0.6903615459245176 |
| carrier_t3_f3 | 2.0 | -0.8739845547333254 | -0.2659878909787279 | -0.9075031372505535 | 0.9540583354586583 |
| carrier_t3_f3 | 3.0 | -0.9532242472061556 | -0.3714210709927629 | -0.970597747405338 | 1.070927822533104 |
