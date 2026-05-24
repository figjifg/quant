# Real Invalid-Row Spot Check

Date: 2026-05-24  
Source dataset: `research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv`

## Headline

- Total rows: **1,093,386**
- Invalid rows (by S1-S6 mask): **11,425**
- Valid rows: **1,081,961**
- Previous P1 OHLCV invariant audit nonpos count: **11,425**
- Match with P1 finding (n_invalid >= P1 nonpos): **True**

## Reason-code distribution

| reason | count |
|---|---:|
| `S1_vendor_non_trading_forward` | 11,425 |
| `S2_nonpos_price` | 11,425 |
| `S3_ohlc_order_violation` | 11,425 |

## Filter behaviour

- `apply_ohlcv_quarantine(mode='filter')` reduces total rows from 1,093,386 to 1,081,961
  (drops **11,425** invalid rows).

## Universe builder behaviour on real data

- Panel WITHOUT `valid_ohlcv_mask` → raises ValueError: **True**
- Panel WITH `valid_ohlcv_mask` (annotated) → accepts (no exception at gate): **True**

## Sample of invalid rows (first 5)

```
        날짜   종목코드  시가  고가  저가       종가  거래량                                            invalid_ohlcv_reason_codes
2016-10-11 000050 0.0 0.0 0.0 208500.0  0.0 S1_vendor_non_trading_forward|S2_nonpos_price|S3_ohlc_order_violation
2016-10-12 000050 0.0 0.0 0.0 208500.0  0.0 S1_vendor_non_trading_forward|S2_nonpos_price|S3_ohlc_order_violation
2016-10-13 000050 0.0 0.0 0.0 208500.0  0.0 S1_vendor_non_trading_forward|S2_nonpos_price|S3_ohlc_order_violation
2016-10-14 000050 0.0 0.0 0.0 208500.0  0.0 S1_vendor_non_trading_forward|S2_nonpos_price|S3_ohlc_order_violation
2016-10-17 000050 0.0 0.0 0.0 208500.0  0.0 S1_vendor_non_trading_forward|S2_nonpos_price|S3_ohlc_order_violation
```

## Forbidden inferences (not made by this audit)

- These rows are NOT treated as halt events.
- These rows are NOT treated as price observations.
- These rows are NOT treated as suspension evidence without an external official source.
- No return / NAV / alpha / strategy metric is produced.

## Conclusion

The patch phase guard module reproduces the P1 invariant audit finding on real
data. The annotated panel correctly identifies the OHL=0 / close>0 vendor
non-trading-row signature plus other S1-S6 signatures. The universe builder
fails closed when the mask is absent and accepts when present.

## Hard locks (preserved)

- No strategy testing.
- No performance metric.
- No production / paper / P08 / live / shadow connection.
