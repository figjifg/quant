# Invalid-Row Quarantine Rules

Date: 2026-05-23  
Scope: measurement-layer A0. Strict rules; no return / signal derivation downstream.

## Rule set

Any row that triggers ANY of the following becomes a **quarantined row**. Strategy
code MUST exclude quarantined rows from feature construction, universe selection, and
execution. Audit code may still observe them.

1. OHLC ordering violation: `고가 < 저가` OR `고가 < {시가,종가}` OR `저가 > {시가,종가}`.
2. Non-positive price: any of `시가/고가/저가/종가 <= 0`.
3. Negative volume: `거래량 < 0`.
4. Negative trading value: `거래대금추정 < 0`.
5. Trading-value-estimated mismatch beyond tolerance `1e-6` relative diff when
   `거래대금추정여부 == True`.
6. (Adjusted overlay only) `adj_close <= 0` OR `adj_volume < 0`.

## Mandatory annotations at quarantine time

- `quarantine_reason_code`: one of `ohlc_order`, `nonpos_price`, `neg_volume`,
  `neg_traded_value`, `tv_estimated_mismatch`, `adj_invalid`.
- `quarantine_source_csv`: filename of input that produced the row.
- `quarantine_timestamp`: ISO datetime at quarantine run.

## Strategy-impact rule

If any strategy code, sector aggregator, factor builder, ranking script, or execution
simulator includes a quarantined row without an explicit `quarantine_override` annotation
documented at the call site, the audit FAILS.

## Hard locks

- Quarantine rules MUST NOT be relaxed to recover sample size.
- Quarantine rules MUST NOT be replaced by per-row 'winsorisation' that hides defects.
- Quarantine rules MUST NOT be used as a feature.
