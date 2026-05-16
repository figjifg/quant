# B010 2010-2017 Equity Panel Schema Verification

## Files Inspected

| file | rows | date coverage | columns |
| --- | ---: | --- | ---: |
| `research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv` | 1093386 | 2010-01-04 to 2016-12-29 | 25 |
| `research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv` | 1087741 | 2017-01-02 to 2024-12-30 | 20 |
| `research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv` | 969208 | 2018-01-02 to 2024-12-30 | 20 |
| `research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv` | 172543 | 2025-01-02 to 2026-05-06 | 26 |

## Schema Differences

The 2010-2016 panel has these columns that are absent from the
2017-2024 and 2018-2024 panels:

| column | observed values in 2010-2016 | loader role |
| --- | --- | --- |
| `통합거래량반영여부` | all `False` | NXT/integrated-market metadata; keep in normalized schema with safe false default when absent. |
| `통합종가반영여부` | all `False` | NXT/integrated-market metadata; keep in normalized schema with safe false default when absent. |
| `통합종가제외여부` | all `False` | NXT/integrated-market metadata; keep in normalized schema with safe false default when absent. |
| `가격범위후보정여부` | all `False` | NXT/integrated-market metadata; keep in normalized schema with safe false default when absent. |
| `KRX종가` | present; byte-equivalent numeric close to `종가` in every row | Load-bearing close column. Validate equality against `종가`; use as native KRX close. |

The 2025-2026 panel also has the four integration flags and `KRX종가`,
plus `키움거래대금순위`. That rank column is not required by the current
loader, universe builder, feature builder, or B-family strategies.

The 2017-2024 and 2018-2024 panels do not have `KRX종가` or the four
integration flags. Per `AGENTS.md`, these pre-NXT panels should synthesize
`KRX종가` from `종가`, because `종가` is the KRX close by definition in that
period. The loader records this as `krx_close_source=from_종가_fallback`.

## Close-Column Checks

| file | `종가 != KRX종가` rows |
| --- | ---: |
| `kiwoom_dynamic_top100_2010_2016_panel.csv` | 0 |
| `dynamic_top100_2025_2026_krx_panel.csv` | 0 |

For files with native `KRX종가`, the loader must continue to raise if any
row differs from `종가`; it must not silently overwrite either column.

## Normalized In-Memory Schema

`src/data/equity_panel.py` should normalize every supported panel to include:

- Existing required columns used by features, universe construction, and
  backtest execution.
- `KRX종가`, with `krx_close_source` equal to `native` when the source file
  has `KRX종가`, otherwise `from_종가_fallback`.
- The four integration flags, coerced to boolean and defaulted to `False`
  when absent from older pre-NXT files.

The integration flags are not alpha inputs and are not used for filtering in
B010. They are carried for metadata and safety checks. `거래대금추정여부`
remains the quality gate for headline rows; `수급금액추정여부` remains a
non-filtering label.

## B010 Window Normalization

B010 uses:

- 2010-2015 rows from `kiwoom_dynamic_top100_2010_2016_panel.csv`.
- 2017 rows from `dynamic_top100_2017_2024_panel.csv`.
- No 2016 rows, per ticket gap-year exclusion.
- No 2018-2024 rows from the 2017-2024 panel, because those dates are
  already-seen B001-B009 territory.

The KRX trading calendar for B010 is derived from the normalized panel rows
with non-null `KRX종가`; no external calendar is introduced.
