# G001 MDD Cooldown

## Baseline Comparison

| carrier | baseline_return | mdd_return | baseline_sharpe | mdd_sharpe | baseline_mdd | mdd_mdd | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| D013 | 2.5457702903350135 | 1.7277771621578437 | 0.5333654677635088 | 0.4561585164400151 | -0.3392346174957135 | -0.3392346174957134 | not_effective |
| E014 | 3.621084739339225 | 2.725353384103918 | 0.6311872415922518 | 0.5932677623565429 | -0.35641869371448887 | -0.2999204241636154 | not_effective |

## Exposure Scalar And MDD

| carrier | lt_1_count | lt_1_share | mdd_window | active_peak | active_trough | mdd_min_scalar | mdd_mean_scalar | mdd_lt_1_share |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| D013 | 19 | 0.3114754098360656 | 2020-02-17 to 2020-03-19 | 1.0 | 1.0 | nan | nan | nan |
| E014 | 17 | 0.2786885245901639 | 2018-01-29 to 2020-03-19 | 1.0 | 1.0 | 0.839619096122815 | 0.9510141878780423 | 0.625 |
