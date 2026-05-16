# B006 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| is_start | 2018-01-02 |
| is_end | 2022-12-30 |
| oos_start | 2023-01-02 |
| oos_end | 2026-05-04 |
| filter | filter_flow_sign_both_positive |
| trigger_baseline | trigger_immediate |
| trigger_candidate | trigger_acceleration |
| ranking | rank_by_combined_flow_5 |
| exit | exit_signal_reversal |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 시가 used as verified KRX regular-session open per AGENTS.md |
| calendar_source | derived from panel non-null KRX종가 rows |

## IS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| t1_baseline | -0.8401740487499133 | 0.3912685337726524 | 1214 | -0.47070942317018805 |
| t3_acceleration | -0.7925571846248682 | 0.400336417157275 | 1189 | -0.3617363925001102 |
| cost_0_t1_baseline | -0.6434911731902361 | 0.41515650741350907 | 1214 | -0.6434911731902361 |
| cost_0_t3_acceleration | -0.5449534267055618 | 0.4272497897392767 | 1189 | -0.5449534267055618 |

## OOS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| t1_baseline | 0.6406402142897907 | 0.4191780821917808 | 730 | 1.1190674285259168 |
| t3_acceleration | 0.7800858376728041 | 0.4198895027624309 | 724 | 1.3158231838403864 |
| cost_0_t1_baseline | 1.6595586314693742 | 0.4465753424657534 | 730 | 1.6595586314693742 |
| cost_0_t3_acceleration | 1.874521364185866 | 0.44613259668508287 | 724 | 1.874521364185866 |

## T3 Promote Year Breakdown

| year | period | t1_baseline_net_total_return | t3_acceleration_net_total_return | t3_minus_t1_net_total_return | t3_wins |
| --- | --- | --- | --- | --- | --- |
| 2018 | is | -0.37817649479769 | -0.283590531813635 | 0.09458596298405497 | True |
| 2019 | is | -0.07380952693427112 | -0.05635021481507374 | 0.01745931211919738 | True |
| 2020 | is | -0.3870658204411924 | -0.26275874947926525 | 0.12430707096192717 | True |
| 2021 | is | -0.24860870189994622 | -0.3594261733079215 | -0.11081747140797527 | False |
| 2022 | is | -0.40700182397943563 | -0.3606627532333402 | 0.046339070746095445 | True |
| 2023 | oos | -0.10636533805501192 | 0.04512727395579974 | 0.15149261201081166 | True |
| 2024 | oos | -0.2061946854971427 | -0.23428521960912174 | -0.028090534111979037 | False |
| 2025 | oos | 0.8831872982080866 | 0.9144378803285935 | 0.03125058212050691 | True |
| 2026 | oos | 0.1284863346929226 | 0.07851529081201702 | -0.049971043880905563 | False |

## Cost Sensitivity

| variant | multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- | --- |
| t3_acceleration | 0.0 | -0.5449534267055618 | 1.874521364185866 | 0.2898960454008055 | 0.0 |
| t3_acceleration | 1.0 | -0.7925571846248682 | 0.7800858376728041 | -0.6358643004107352 | 0.5404116271363258 |
| t3_acceleration | 2.0 | -0.9057796456463036 | 0.09988621979282875 | -0.8978103448598471 | 0.7252190499135762 |
| t3_acceleration | 3.0 | -0.9573642242581795 | -0.3219317234723428 | -0.9714929362512801 | 0.800894414715917 |
