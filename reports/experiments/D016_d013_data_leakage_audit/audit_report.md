# D016 D013 Data Leakage Audit

Overall verdict: PASS - no timing leakage detected

## Timing Table

| variable | rule | min_lag_days | violations | passed |
|---|---|---:|---:|---|
| VIX 60d/240d | US after close: source <= signal_date - 1d | 1 | 0 | True |
| BAA10Y spread | US after close: source <= signal_date - 1d | 1 | 0 | True |
| USDKRW yoy | Korea same day: source <= signal_date | 0 | 0 | True |
| DXY yoy | US after close: source <= signal_date - 1d | 1 | 0 | True |
| US 10y real yield | US after close: source <= signal_date - 1d | 1 | 0 | True |
| US 2-10y curve | US after close: both sources <= signal_date - 1d | 1 | 0 | True |
| Brent yoy | US after close: source <= signal_date - 1d | 1 | 0 | True |
| 10y breakeven | US after close: source <= signal_date - 1d | 1 | 0 | True |
| OECD CLI Korea | OECD CLI conservative lag: observation month-end +75 calendar days | 118 | 0 | True |
| KR exports yoy | KR exports lag: observation month-end +14 calendar days | 56 | 0 | True |

## z-score and execution checks

- Factor z-scores are computed from monthly regime history through each signal date only.
- D013 signals keep `signal_date` and `execution_date` separate; all trades execute after the signal date.
- OECD CLI now uses month-end +75 calendar days; KR exports and other monthly variables retain month-end +14 days.
