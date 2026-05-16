# B009 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| is_start | 2018-01-02 |
| is_end | 2022-12-30 |
| oos_start | 2023-01-02 |
| oos_end | 2026-05-04 |
| filter_baseline | filter_flow_sign_both_positive |
| filter_candidate | filter_persistence_4_of_5 |
| trigger | trigger_acceleration |
| ranking | rank_by_combined_flow_5 |
| exit | exit_signal_reversal on absolute fnv_5/inv_5 |
| persistence_policy | per-ticker right-labeled rolling 5-row count of combined_flow_1 > 0 using signal dates through T only |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 시가 used as verified KRX regular-session open per AGENTS.md |
| calendar_source | derived from panel non-null KRX종가 rows |
| oos_year_wins_f3_gt_f1 | 2 of 4 |
| oos_delta_excluding_2025 | 0.1484537579327121 |
| oos_delta_2025 | 0.15463176016940805 |
| oos_delta_excluding_2025_and_2026 | -0.07254948675325856 |

## IS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| f1_baseline | -0.7925571846248682 | 0.400336417157275 | 1189 | -0.3617363925001102 |
| f3_promote | -0.7865788545049432 | 0.39173553719008264 | 1210 | -0.352835829787375 |
| cost_0_f1_baseline | -0.5449534267055618 | 0.4272497897392767 | 1189 | -0.5449534267055618 |
| cost_0_f3_promote | -0.5254609811715771 | 0.41652892561983473 | 1210 | -0.5254609811715771 |

## OOS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| f1_baseline | 0.7800858376728041 | 0.4198895027624309 | 724 | 1.3158231838403864 |
| f3_promote | 1.1041868609831256 | 0.426812585499316 | 731 | 1.646342178147111 |
| cost_0_f1_baseline | 1.874521364185866 | 0.44613259668508287 | 724 | 1.874521364185866 |
| cost_0_f3_promote | 2.4175517306182512 | 0.45964432284541723 | 731 | 2.4175517306182512 |

## F3 Promote Year Breakdown

| year | period | f1_baseline_net_total_return | f3_promote_net_total_return | f3_minus_f1_net_total_return | f3_wins_f1 |
| --- | --- | --- | --- | --- | --- |
| 2018 | is | -0.283590531813635 | -0.2805151249665919 | 0.003075406847043105 | True |
| 2019 | is | -0.05635021481507374 | -0.1720000831649383 | -0.11564986834986457 | False |
| 2020 | is | -0.26275874947926525 | -0.14463391320701213 | 0.11812483627225312 | True |
| 2021 | is | -0.3594261733079215 | -0.3492557292846583 | 0.01017044402326317 | True |
| 2022 | is | -0.3606627532333402 | -0.3643762027970756 | -0.003713449563735427 | False |
| 2023 | oos | 0.04512727395579974 | -0.014463699727584212 | -0.05959097368338395 | False |
| 2024 | oos | -0.23428521960912174 | -0.24724373267899635 | -0.012958513069874611 | False |
| 2025 | oos | 0.9144378803285935 | 1.0690696404980016 | 0.15463176016940805 | True |
| 2026 | oos | 0.07851529081201702 | 0.2995185354979877 | 0.22100324468597066 | True |

## Cost Sensitivity

| variant | multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- | --- |
| f3_promote | 0.0 | -0.5254609811715771 | 2.4175517306182512 | 0.5992646851165637 | 0.0 |
| f3_promote | 1.0 | -0.7865788545049432 | 1.1041868609831256 | -0.5571611982152966 | 0.5478428774853641 |
| f3_promote | 2.0 | -0.9043702862185705 | 0.29261557619123524 | -0.8781075853829219 | 0.7295557000456595 |
| f3_promote | 3.0 | -0.9573108627656061 | -0.20775842318202786 | -0.9666512239414013 | 0.8046501496400714 |
