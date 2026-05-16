# B008 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| is_start | 2018-01-02 |
| is_end | 2022-12-30 |
| oos_start | 2023-01-02 |
| oos_end | 2026-05-04 |
| filter_baseline | filter_flow_sign_both_positive |
| filter_candidate | filter_relative_AND_absolute_positive |
| trigger | trigger_acceleration |
| ranking | rank_by_combined_flow_5 |
| exit | exit_signal_reversal on absolute fnv_5/inv_5 |
| relative_feature_policy | median-difference relative flow, cross-sectional moments by signal_date over eligible execution universe |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 시가 used as verified KRX regular-session open per AGENTS.md |
| calendar_source | derived from panel non-null KRX종가 rows |
| oos_year_wins_f2_gt_f1 | 3 of 4 |
| oos_delta_excluding_2025 | 0.05516158954429451 |
| oos_delta_2025 | 0.15581756524209567 |

## IS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| f1_baseline | -0.7925571846248682 | 0.400336417157275 | 1189 | -0.3617363925001102 |
| f2_promote | -0.7930085984175538 | 0.4005102040816326 | 1176 | -0.36324113226517624 |
| cost_0_f1_baseline | -0.5449534267055618 | 0.4272497897392767 | 1189 | -0.5449534267055618 |
| cost_0_f2_promote | -0.5497607368660513 | 0.42517006802721086 | 1176 | -0.5497607368660513 |

## OOS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| f1_baseline | 0.7800858376728041 | 0.4198895027624309 | 724 | 1.3158231838403864 |
| f2_promote | 1.004223533146971 | 0.42441054091539526 | 721 | 1.5537555234706506 |
| cost_0_f1_baseline | 1.874521364185866 | 0.44613259668508287 | 724 | 1.874521364185866 |
| cost_0_f2_promote | 2.2303450668721867 | 0.4535367545076283 | 721 | 2.2303450668721867 |

## F2 Promote Year Breakdown

| year | period | f1_baseline_net_total_return | f2_promote_net_total_return | f2_minus_f1_net_total_return | f2_wins_f1 |
| --- | --- | --- | --- | --- | --- |
| 2018 | is | -0.283590531813635 | -0.3076613684285946 | -0.024070836614959568 | False |
| 2019 | is | -0.05635021481507374 | 0.03557949019354312 | 0.09192970500861686 | True |
| 2020 | is | -0.26275874947926525 | -0.2996108677339523 | -0.03685211825468704 | False |
| 2021 | is | -0.3594261733079215 | -0.33981211879224693 | 0.01961405451567455 | True |
| 2022 | is | -0.3606627532333402 | -0.39121343296216227 | -0.030550679728822083 | False |
| 2023 | oos | 0.04512727395579974 | 0.06981563292235493 | 0.02468835896655519 | True |
| 2024 | oos | -0.23428521960912174 | -0.25920432685370665 | -0.024919107244584904 | False |
| 2025 | oos | 0.9144378803285935 | 1.0702554455706892 | 0.15581756524209567 | True |
| 2026 | oos | 0.07851529081201702 | 0.13390762863434125 | 0.05539233782232422 | True |

## Cost Sensitivity

| variant | multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- | --- |
| f2_promote | 0.0 | -0.5497607368660513 | 2.2303450668721867 | 0.43425246030306175 | 0.0 |
| f2_promote | 1.0 | -0.7930085984175538 | 1.004223533146971 | -0.5909066890366057 | 0.5419355240979045 |
| f2_promote | 2.0 | -0.9051836065885815 | 0.24074123158587102 | -0.8839943649590958 | 0.7258549078287935 |
| f2_promote | 3.0 | -0.9567270561911138 | -0.2336243818155349 | -0.9672988510678256 | 0.8000161806099808 |
