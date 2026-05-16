# B007 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| is_start | 2018-01-02 |
| is_end | 2022-12-30 |
| oos_start | 2023-01-02 |
| oos_end | 2026-05-04 |
| filter_candidates | F1 flow_sign_both_positive; F2 relative_AND_absolute_positive; F3 persistence_4_of_5 |
| trigger | trigger_acceleration |
| ranking | rank_by_combined_flow_5 |
| exit | exit_signal_reversal on absolute fnv_5/inv_5 |
| relative_feature_policy | median-difference relative flow, cross-sectional moments by signal_date over eligible execution universe |
| persistence_policy | per-ticker right-labeled rolling 5-row count of combined_flow_1 > 0 using signal dates through T only |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 시가 used as verified KRX regular-session open per AGENTS.md |
| calendar_source | derived from panel non-null KRX종가 rows |

## IS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| f1_baseline | -0.7925571846248682 | 0.400336417157275 | 1189 | -0.3617363925001102 |
| f2_relative_and_absolute | -0.7930085984175538 | 0.4005102040816326 | 1176 | -0.36324113226517624 |
| f3_persistence_4_of_5 | -0.7865788545049432 | 0.39173553719008264 | 1210 | -0.352835829787375 |
| cost_0_f1_baseline | -0.5449534267055618 | 0.4272497897392767 | 1189 | -0.5449534267055618 |
| cost_0_f2_relative_and_absolute | -0.5497607368660513 | 0.42517006802721086 | 1176 | -0.5497607368660513 |
| cost_0_f3_persistence_4_of_5 | -0.5254609811715771 | 0.41652892561983473 | 1210 | -0.5254609811715771 |

## OOS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| f1_baseline | 0.7800858376728041 | 0.4198895027624309 | 724 | 1.3158231838403864 |
| f2_relative_and_absolute | 1.004223533146971 | 0.42441054091539526 | 721 | 1.5537555234706506 |
| f3_persistence_4_of_5 | 1.1041868609831256 | 0.426812585499316 | 731 | 1.646342178147111 |
| cost_0_f1_baseline | 1.874521364185866 | 0.44613259668508287 | 724 | 1.874521364185866 |
| cost_0_f2_relative_and_absolute | 2.2303450668721867 | 0.4535367545076283 | 721 | 2.2303450668721867 |
| cost_0_f3_persistence_4_of_5 | 2.4175517306182512 | 0.45964432284541723 | 731 | 2.4175517306182512 |

## Filter Exploration Year Breakdown

| year | period | is_v_recovery_diagnostic_2020 | oos_spike_capture_diagnostic_2025 | f1_baseline_net_total_return | f2_relative_and_absolute_net_total_return | f3_persistence_4_of_5_net_total_return | f2_minus_f1_net_total_return | f3_minus_f1_net_total_return | f2_wins_f1 | f3_wins_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018 | is | False | False | -0.283590531813635 | -0.3076613684285946 | -0.2805151249665919 | -0.024070836614959568 | 0.003075406847043105 | False | True |
| 2019 | is | False | False | -0.05635021481507374 | 0.03557949019354312 | -0.1720000831649383 | 0.09192970500861686 | -0.11564986834986457 | True | False |
| 2020 | is | True | False | -0.26275874947926525 | -0.2996108677339523 | -0.14463391320701213 | -0.03685211825468704 | 0.11812483627225312 | False | True |
| 2021 | is | False | False | -0.3594261733079215 | -0.33981211879224693 | -0.3492557292846583 | 0.01961405451567455 | 0.01017044402326317 | True | True |
| 2022 | is | False | False | -0.3606627532333402 | -0.39121343296216227 | -0.3643762027970756 | -0.030550679728822083 | -0.003713449563735427 | False | False |
| 2023 | oos | False | False | 0.04512727395579974 | 0.06981563292235493 | -0.014463699727584212 | 0.02468835896655519 | -0.05959097368338395 | True | False |
| 2024 | oos | False | False | -0.23428521960912174 | -0.25920432685370665 | -0.24724373267899635 | -0.024919107244584904 | -0.012958513069874611 | False | False |
| 2025 | oos | False | True | 0.9144378803285935 | 1.0702554455706892 | 1.0690696404980016 | 0.15581756524209567 | 0.15463176016940805 | True | True |
| 2026 | oos | False | False | 0.07851529081201702 | 0.13390762863434125 | 0.2995185354979877 | 0.05539233782232422 | 0.22100324468597066 | True | True |

## Trade-Set Overlap

| variant | F1 | F2 | F3 |
| --- | --- | --- | --- |
| F1 | 1.0 | 0.884272997032641 | 0.42056763730187985 |
| F2 | 0.884272997032641 | 1.0 | 0.40175310445580714 |
| F3 | 0.42056763730187985 | 0.40175310445580714 | 1.0 |

## Cost Sensitivity

| variant | multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- | --- |
| f3_persistence_4_of_5 | 0.0 | -0.5254609811715771 | 2.4175517306182512 | 0.5992646851165637 | 0.0 |
| f3_persistence_4_of_5 | 1.0 | -0.7865788545049432 | 1.1041868609831256 | -0.5571611982152966 | 0.5478428774853641 |
| f3_persistence_4_of_5 | 2.0 | -0.9043702862185705 | 0.29261557619123524 | -0.8781075853829219 | 0.7295557000456595 |
| f3_persistence_4_of_5 | 3.0 | -0.9573108627656061 | -0.20775842318202786 | -0.9666512239414013 | 0.8046501496400714 |
