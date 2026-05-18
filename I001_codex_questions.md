# I001 Codex Questions

## USDKRW endpoint gap

- ETF files run through 2026-05-18, but `research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv` ends at 2026-04-24.
- I001 outputs were generated with USDKRW carried forward from the last available FRED observation for ETF rows after that date.
- For final research interpretation, should I001 be frozen with this convention, truncated to the common ETF/FX endpoint, or regenerated after a newer approved USDKRW input is added?
