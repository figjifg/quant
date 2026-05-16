# B010 Codex Questions

## Blocking ambiguity: H3 denominator and 2015 coverage

The ticket has an internal contradiction on the year set used for H3:

- It says verification covers `2010-2015 + 2017`.
- It lists candidate years as `2010, 2011, 2012, 2013, 2014, 2015, 2017`, which is 7 years.
- It also says H3 requires positive yearly contribution in `>= 3 of 6 years`.
- The required final assistant format says `V1 positive years: __ of 6`.
- The required `old_data_year_breakdown.csv` says to report 7 cells per variant:
  `2010, 2011, 2012, 2013, 2014, 2015 (partial), 2017`.

The actual file
`research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv`
has rows from `2010-01-04` through `2016-12-29`, including full 2015 and
full 2016. The config excerpt excludes calendar year 2016 only, so a literal
implementation would include full calendar year 2015 and produce 7 year rows
when combined with 2017.

Please specify which H3/year-breakdown rule B010 should use:

1. Use 7 years: `2010, 2011, 2012, 2013, 2014, 2015, 2017`, and report
   `V1 positive years: __ of 7`.
2. Use 6 years by excluding 2015 from H3, while still outputting the 2015
   diagnostic row.
3. Use 6 years by truncating 2015 to a specific partial window. If so, provide
   the exact end date, because the source file contains full 2015 rows.

## Blocking ambiguity: H4 numerator

The ticket defines H4 as:

> The largest single-year (V1 - V2) delta is <= 80% of total (V1 - V2) delta.

But reportable metric 7 says:

> Largest single-year contribution as fraction of total (the H4 diagnostic,
> computed for V1)

The final response format also says:

> V1 largest-year fraction of total: __ percent

Please specify whether H4 should be computed from:

1. Per-year `V1 - V2` deltas divided by total `V1 - V2` delta, matching the
   pre-registered H4 text.
2. Per-year V1 net returns divided by total V1 net return, matching the
   reportable/final wording.
