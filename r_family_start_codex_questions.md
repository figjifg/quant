# R-family Start Codex Questions

## Blocker

`R000` OPENDART audit could not load:

`research_input_data/inputs/events/opendart_kospi_disclosures_20180101_20260505.parquet`

The current `.venv` has pandas, but no parquet engine:

- `pyarrow`: missing
- `fastparquet`: missing

No external network or dependency install was attempted.

## Question

Should `pyarrow` or `fastparquet` be added to the approved local environment
and `requirements.txt`, or should the OPENDART disclosure file be provided in
CSV format for the R000 audit?

## Current R000 Output

`reports/experiments/R000_opendart_event_data_audit/report.md` records:

`Verdict: NEEDS DATA`

