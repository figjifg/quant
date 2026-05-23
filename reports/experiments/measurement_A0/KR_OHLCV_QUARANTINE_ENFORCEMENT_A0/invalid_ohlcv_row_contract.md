# Invalid OHLCV Row Contract

Date: 2026-05-23  
Predecessor: P1 `KR_OHLCV_UNIT_INVARIANT_A0/ohlcv_invariant_summary.md`
+ `invalid_row_quarantine_rules.md` (initial pass CLOSED AS PARTIAL / DEFECT-FOUND).

## Purpose

Define the canonical row-level signatures that disqualify a (date, ticker) row from
downstream OHLCV use. Separate vendor non-trading-row convention from true missing data.
Do NOT infer suspension / halt / executable status from these rows alone.

## Coverage

Applies to:

- 4 equity panels (`날짜, 종목코드, 시가, 고가, 저가, 종가, 거래량, 거래대금추정,
  Change`).
- W001 v2 derived (`panel_with_adjusted_ohlc_2018_2026.csv` and
  `panel_with_tradable_state.csv`) — both `종가` and `adj_close` family.
- S1 adjusted OHLC (`adj_open, adj_high, adj_low, adj_close, adj_volume,
  adj_return_pct`).

Does NOT cover (out of scope here):

- KRX official halt log (not in repo; tracked by `KR-EXECUTABLE-STATUS-BACKLOG-001`).
- DART status events (tracked by W001 v2 `listing_status_events.csv`).
- Other dataset families (macro, US, futures).

## Invariant signatures (any single match → quarantined row)

### S1. OHL = 0 / close > 0  (vendor non-trading-row convention)

**Definition**:
```
시가 == 0 AND 고가 == 0 AND 저가 == 0 AND 종가 > 0
```
(equivalent on adjusted: `adj_open == 0 AND adj_high == 0 AND adj_low == 0 AND
adj_close > 0`)

**Origin**: vendor (Kiwoom / pykrx) places `0` in OHL positions for rows where intraday
trading did not occur but a forwarded previous close is reported. P1 confirms this is
the dominant signature across all panels + S1.

**Quarantine reason code**: `vendor_non_trading_forward`.

**Hard locks specific to this signature**:
- Do NOT interpret the row as a price observation.
- Do NOT interpret the row as a halt or suspension event — that requires an external
  official source.
- Do NOT use `종가` on this row as a same-day price level (it is a forwarded prior
  close).

### S2. Non-positive price

**Definition**: any of `{시가, 고가, 저가, 종가} <= 0` (and on adjusted: any of
`{adj_open, adj_high, adj_low, adj_close} <= 0`).

**Quarantine reason code**: `nonpos_price`.

S1 is the dominant subset of S2 (vendor non-trading rows). Rows that match S2 without
matching S1 (e.g., only `저가 == 0`) are still quarantined but flagged with
`nonpos_irregular` for separate inspection.

### S3. OHLC ordering violation

**Definition**: any of:
- `고가 < 저가`,
- `고가 < 시가`,
- `고가 < 종가`,
- `저가 > 시가`,
- `저가 > 종가`.

**Quarantine reason code**: `ohlc_order_violation`.

Rows matching S1 also automatically match S3 (because `고가 = 0 < 종가`). The audit
records both reason codes for those rows.

### S4. Negative volume / trading value

**Definition**:
- `거래량 < 0`, OR
- `거래대금추정 < 0`, OR
- `adj_volume < 0`.

**Quarantine reason code**: `neg_volume_or_value`.

P1 observed **0** such rows. Signature is documented for future-proofing.

### S5. Vendor trading-value estimation mismatch

**Definition**: when `거래대금추정여부 == True`, the vendor rule should yield
`거래대금추정 == 종가 × 거래량`. A row whose `abs(거래대금추정 − 종가 × 거래량) /
abs(종가 × 거래량) > 1e-6` matches.

**Quarantine reason code**: `tv_estimated_mismatch`.

P1 observed 98 such rows in the 2025-2026 KRX panel (post-NXT), suggesting a different
estimation rule. Until vendor confirms the formula, these rows MUST be excluded from any
estimation-based usage.

### S6. Missing adjusted overlay where required

**Definition**: any code path that requires `adj_close` (or any `adj_*`) for the row but
finds it null / absent, while raw `종가` exists.

**Quarantine reason code**: `adj_missing`.

This signature flags rows that the corporate-action overlay did not cover. Such rows
MUST NOT be returned-from / used-as a clean price observation, because the raw `종가`
on a corporate-action day is artifactual on its own.

## Combined invariant

A row is **invalid** if it matches ANY of `{S1, S2, S3, S4, S5, S6}`. The audit must
record every matched signature, not the first match only.

## Forbidden inferences from invalid rows (Referee-lock)

The following inferences are explicitly disallowed on invalid rows:

| Forbidden inference | Why |
|---|---|
| The stock was halted that day. | Requires external official halt log; vendor zero ≠ halt. |
| The stock was suspended that day. | Same reason as above. |
| The stock had zero volume that day. | The row's volume value is not trusted on invalid rows. |
| The stock's close on that day was the recorded `종가`. | S1 rows carry a forwarded prior close; that is not a same-day observation. |
| The stock's return on that day was the recorded `Change`. | Same reason; the vendor's `Change` on a forwarded row is meaningless. |
| The row is comparable to a non-invalid row of another ticker. | Mixing valid and invalid rows breaks any cross-sectional comparison. |

## Required exclusion order

When any downstream code reads OHLCV fields, the **invalid-row filter MUST run before**:

1. signal construction,
2. event ledger construction,
3. execution simulation,
4. t+1 mapping,
5. tradability logic,
6. universe construction,
7. any future strategy diagnostic.

Equivalent forms allowed:
- physical row exclusion (drop),
- masking (set to NaN with a propagation rule),
- explicit per-call guard (a documented per-callsite filter).

Forms NOT allowed:
- silent fillna(0) that preserves zero values,
- silent fillna(method='ffill') across an invalid row,
- silent re-use of `종가` as the same-day price on an invalid row.

## Cross-references

- `KR_OHLCV_UNIT_INVARIANT_A0/invalid_row_quarantine_rules.md` (predecessor)
- `KR_OHLCV_UNIT_INVARIANT_A0/ohlcv_invariant_summary.md`
- `KR_FIELD_METADATA_CONTRACT_A0/column_contract_table.csv`
- `KR_FIELD_METADATA_CONTRACT_A0/field_allowlist_denylist.csv`

## Hard locks

- This contract is the authoritative definition for this phase.
- It MUST NOT be relaxed to recover sample size.
- It MUST NOT be replaced by per-row winsorisation that hides defects.
- It MUST NOT be used as a feature.
- It MUST NOT be reinterpreted to permit strategy testing.
