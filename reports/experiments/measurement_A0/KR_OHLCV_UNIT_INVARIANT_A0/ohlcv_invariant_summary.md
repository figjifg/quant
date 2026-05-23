# OHLCV Unit Invariant Audit — Summary

Date: 2026-05-23  
Scope: measurement-layer A0 only. NO return / jump / momentum / reversal / performance.

## Headline numbers

- Total rows scanned across panels + S1: 4901098
- OHLC ordering violations: 58649
- Non-positive price rows: 53556
- Negative volume/value rows: 0

## Per-source breakdown

| source | rows_total | ohlc_violations | nonpos_rows | neg_rows |
|---|---:|---:|---:|---:|
| `kiwoom_2010_2016` | 1093386 | 11425 | 11425 | 0 |
| `dynamic_top100_2017_2024` | 1087741 | 8993 | 8993 | 0 |
| `dynamic_top100_2018_2024` | 969208 | 7450 | 7450 | 0 |
| `krx_2025_2026` | 172543 | 2163 | 2163 | 0 |
| `s1_adjusted_ohlc` | 1578220 | 28618 | 23525 | 0 |

## Pattern finding — `OHL == 0` while `close > 0`

Across **all** panels and S1 adjusted, the non-positive rows share one signature:
`시가 = 고가 = 저가 = 0` (or `adj_open = adj_high = adj_low = 0`) with `종가 > 0`
(or `adj_close > 0`). This is the vendor convention for **non-trading rows**
(halts / suspensions / period-bookend rows) where intraday data is absent but the
previous close is forwarded. These rows trigger BOTH the OHLC-ordering rule
(`고가 < 종가` because `고가 == 0`) AND the non-positive-price rule.

Implication:
- The two violation counts coincide for the equity panels because they describe the
  same row set.
- These rows MUST be quarantined per the rules in `invalid_row_quarantine_rules.md`.
- They MUST NOT be used as evidence of a price level on that day.
- Cross-check with `KR-EXECUTABLE-STATUS-BACKLOG-001` and W001 v2 listing_status_events
  is required before treating any of them as a suspension event.

## Trading value estimation (vendor `거래대금추정`)

| panel | rows_estimated | mismatch_count |
|---|---:|---:|
| `kiwoom_2010_2016` | 0 | 0 |
| `dynamic_top100_2017_2024` | 0 | 0 |
| `dynamic_top100_2018_2024` | 0 | 0 |
| `krx_2025_2026` | 98 | 98 |

## Kill gates (Referee)

- **OHLC ordering broad?** Look at counts above; broad = quarantine affected rows/fields.
- **Price/value unit clear?** See `trading_value_unit_plausibility.md` — close×volume agreement on estimated rows is the plausibility evidence. Aggregate market_flow flow unit (KRW_mil vs count) is ambiguous → defect logged.
- **Quarantined rows ever used downstream?** Strategy code uses `tradable_state` and adjusted overlay; the v2 wiring is responsible for excluding quarantined rows. This audit produces the canonical quarantine row list. Downstream verification = separate audit.

## Allowed output enumeration (per Referee)

- defect ledger ✔ (CSV form)
- invariant defect tables ✔
- quarantine rule doc ✔
- unit plausibility doc ✔

## Disallowed output (Referee-lock)

- No turnover, liquidity, or volume-based ranking.
- No close-on-close return.
- No reversion / momentum / RS / quality metric.
- No execution simulation.

## Cross references

- `ohlc_ordering_violations.csv`
- `nonpositive_price_rows.csv`
- `negative_volume_value_rows.csv`
- `trading_value_unit_plausibility.md`
- `invalid_row_quarantine_rules.md`
- `../KR_FIELD_METADATA_CONTRACT_A0/`
- `../KR_CALENDAR_PANEL_ALIGN_A0/`
