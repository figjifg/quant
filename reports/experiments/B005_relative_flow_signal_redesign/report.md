# B005 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| is_start | 2018-01-02 |
| is_end | 2022-12-30 |
| oos_start | 2023-01-02 |
| oos_end | 2026-05-04 |
| strategy | B005 absolute baseline vs relative z-score vs relative median-diff alpha definitions |
| trigger | trigger_immediate for all variants |
| exit | signal reversal using each variant's own alpha columns; relative columns are renamed before engine handoff |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 시가 used as verified KRX regular-session open per AGENTS.md |
| calendar_source | derived from panel non-null KRX종가 rows |

## IS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| absolute_baseline | -0.8401740487499133 | 0.3912685337726524 | 1214 | -0.47070942317018805 |
| relative_zscore | -0.8047633662282923 | 0.40657894736842104 | 1520 | -0.3566065325567688 |
| relative_median_diff | -0.8292643041976658 | 0.40561724363161333 | 1531 | -0.37031319373402305 |

## OOS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| absolute_baseline | 0.6406402142897907 | 0.4191780821917808 | 730 | 1.1190674285259168 |
| relative_zscore | -0.07706521100944286 | 0.3910891089108911 | 1010 | 0.39483589048566836 |
| relative_median_diff | -0.055476529069321434 | 0.39221556886227543 | 1002 | 0.405074543002088 |

## Signal Redesign Year Breakdown

| year | is_h1_check_2020 | oos_h3_check_2025 | absolute_baseline_net_total_return | relative_zscore_net_total_return | relative_median_diff_net_total_return | relative_zscore_minus_absolute_baseline | relative_median_diff_minus_absolute_baseline |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2018 | False | False | -0.37817649479769 | -0.5059384879316016 | -0.4726295717169997 | -0.12776199313391157 | -0.09445307691930971 |
| 2019 | False | False | -0.07380952693427112 | -0.0939903698953436 | -0.12463671051768255 | -0.020180842961072476 | -0.05082718358341143 |
| 2020 | True | False | -0.3870658204411924 | -0.05382494456737663 | -0.04369261899603216 | 0.3332408758738158 | 0.34337320144516026 |
| 2021 | False | False | -0.24860870189994622 | -0.27983658326611427 | -0.3055528004833693 | -0.031227881366168053 | -0.056944098583423086 |
| 2022 | False | False | -0.40700182397943563 | -0.37530433215628756 | -0.4519459246164049 | 0.03169749182314807 | -0.0449441006369693 |
| 2023 | False | False | -0.10636533805501192 | -0.2945961310334868 | -0.2760045751184521 | -0.1882307929784749 | -0.1696392370634402 |
| 2024 | False | False | -0.2061946854971427 | -0.22224548589011928 | -0.3198889055321089 | -0.016050800392976572 | -0.11369422003496621 |
| 2025 | False | True | 0.8831872982080866 | 0.2716063362684775 | 0.43024055341161005 | -0.6115809619396091 | -0.45294674479647656 |
| 2026 | False | False | 0.1284863346929226 | 0.2850591503676305 | 0.2786830406006713 | 0.15657281567470793 | 0.1501967059077487 |

## Trade-Set Overlap

| variant | absolute_baseline | relative_zscore | relative_median_diff |
| --- | --- | --- | --- |
| absolute_baseline | 1.0 | 0.29568491167101074 | 0.3558449424591157 |
| relative_zscore | 0.29568491167101074 | 1.0 | 0.5502143294549908 |
| relative_median_diff | 0.3558449424591157 | 0.5502143294549908 | 1.0 |

## Cost Sensitivity

| variant | multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- | --- |
| absolute_baseline | 0.0 | -0.6434911731902361 | 1.6595586314693742 | -0.06499663181235271 | 0.0 |
| absolute_baseline | 1.0 | -0.8401740487499133 | 0.6406402142897907 | -0.7414261730523879 | 0.4448673583808787 |
| absolute_baseline | 2.0 | -0.9286174570779422 | 0.009809365117319446 | -0.9289202576444962 | 0.612552200886233 |
| absolute_baseline | 3.0 | -0.9682397984770311 | -0.37988100684138504 | -0.9805793764515442 | 0.6902655781574483 |
