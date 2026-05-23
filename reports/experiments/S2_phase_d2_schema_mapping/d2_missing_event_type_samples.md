# D2 Missing / Under-Sampled Event Type Acquisition

Per Referee D2 mandatory addition (c), D2 explicitly acquired samples for under-sampled event types.

| Event type | D1 sampled | D2 added | Total | Status |
|---|---|---|---|---|
| treasury_cancel | 0 | 5 | 5 | D2 expansion successful (+5 samples) |
| additional_listing | 0 | 3 | 3 | D2 expansion successful (+3 samples) |
| lockup_release | 0 | 5 | 5 | D2 expansion successful (+5 samples) |
| major_shareholder_sale | 0 | 5 | 5 | D2 expansion successful (+5 samples) |
| correction_withdrawal_cancel | 0 | 5 | 5 | D2 expansion successful (+5 samples) |

## KOSDAQ coverage
- KOSDAQ general samples acquired via OPENDART list API: 20
- R000 KOSPI parquet has 0 KOSDAQ disclosures (corp_cls all 'Y'); D2 acquires via `list.json?corp_cls=K`.