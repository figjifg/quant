# G002 Stress Filter

## Baseline Comparison

| carrier | baseline_return | stress_return | baseline_sharpe | stress_sharpe | baseline_mdd | stress_mdd | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| D013 | 2.5457702903350135 | 1.9924878279462157 | 0.5333654677635088 | 0.4740775177018326 | -0.3392346174957135 | -0.34423078137831375 | not_effective |
| E014 | 3.621084739339225 | 3.1383708138260955 | 0.6311872415922518 | 0.6178868700745308 | -0.35641869371448887 | -0.3191935055745041 | not_effective |

## Stress Scalar And MDD

| carrier | lt_1_count | lt_1_share | max_stress_score | mdd_window | active_peak | active_trough | mdd_min_scalar | mdd_mean_scalar | mdd_lt_1_share |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| D013 | 7 | 0.11475409836065574 | 2.3026463486004 | 2021-01-11 to 2022-01-27 | 1.0 | 1.0 | 0.5 | 0.875 | 0.25 |
| E014 | 7 | 0.11475409836065574 | 2.3026463486004 | 2021-05-28 to 2022-01-27 | 1.0 | 1.0 | 0.5 | 0.8333333333333334 | 0.3333333333333333 |
