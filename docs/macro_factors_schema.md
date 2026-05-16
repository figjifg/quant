# Macro Factors Schema

## Scope

C002 uses eight local FRED CSVs under
`research_input_data/inputs/macro_features/`. These files are read-only
research inputs; the C002 loader only validates and aligns them.

## Loader

Code: `src/data/macro_factors.py`

Primary functions:
- `load_fred_series(path, spec)`: validates one two-column FRED CSV.
- `load_all_fred_series(input_dir)`: loads all eight C002 FRED series.
- `align_macro_factors_to_korean_signal_dates(signal_dates, input_dir)`:
  aligns macro levels to Korean `signal_date`.
- `build_macro_factor_changes(aligned)`: converts aligned levels into daily
  regression factors.

## Raw File Schema

Each file must contain:
- `observation_date`: FRED observation date, parsed as pandas datetime.
- one FRED value column named exactly as specified below.

FRED `"."` missing values are parsed as missing numeric values. Duplicate
`observation_date` rows are rejected.

| Loader name | FRED series | File | Transform | Timing policy |
|---|---|---|---|---|
| `vix` | `VIXCLS` | `fred_vix.csv` | percent change | US after close |
| `dxy` | `DTWEXBGS` | `fred_dxy.csv` | percent change | US after close |
| `dgs2` | `DGS2` | `fred_dgs2.csv` | first difference | US after close |
| `dgs10` | `DGS10` | `fred_dgs10.csv` | first difference | US after close |
| `dexchus_usdcny` | `DEXCHUS` | `fred_dexchus.csv` | percent change | US after close |
| `baa10y_spread` | `BAA10Y` | `fred_baa10y_spread.csv` | first difference | US after close |
| `dgs3mo` | `DGS3MO` | `fred_dgs3mo.csv` | first difference | US after close |
| `dexkous_usdkrw` | `DEXKOUS` | `fred_dexkous_usdkrw.csv` | percent change | Korea same day |

## Timing Policy

For Korean `signal_date = T`:
- US after-close series use the latest FRED observation with
  `observation_date <= T - 1 calendar day`, which resolves to the prior US
  trading day when `T-1` is a weekend or US holiday. This implements the rule
  that US macro data published after the US close cannot be used for Korea on
  the same Korean date.
- `DEXKOUS` USDKRW uses the latest FRED observation with
  `observation_date <= T`, matching C002's Korea same-day timing policy.

The aligned loader emits one `<name>_source_observation_date` column per series
so downstream code can audit the exact source date used for each Korean signal
date.

## 2010-2026 Load Sanity

Rows below count non-null raw FRED observations with
`2010-01-01 <= observation_date <= 2026-12-31` in the local files as of
2026-05-16.

| Loader name | Non-null rows |
|---|---:|
| `vix` | 4145 |
| `dxy` | 4071 |
| `dgs2` | 4094 |
| `dgs10` | 4094 |
| `dexchus_usdcny` | 4090 |
| `baa10y_spread` | 4089 |
| `dgs3mo` | 4089 |
| `dexkous_usdkrw` | 4080 |
