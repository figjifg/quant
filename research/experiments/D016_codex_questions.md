# D016 Codex Questions

## Blocker

D016 timing audit found a mismatch between the pre-registered ticket timing
rule and the current D013 macro alignment code.

The ticket requires:

- `KR_CLI`: monthly, approximately 2-month publication lag
- `KR_exports`: monthly, approximately 1-month publication lag

Current implementation in `src/data/macro_factors.py` applies the same monthly
availability rule to all monthly series:

```text
availability_date = source_observation_date + MonthEnd(0) + 14 days
```

For `KR_CLI`, this allows a January observation to be used from February 14.
Example checked in the current code:

| signal_date | variable | source_observation_date used |
| --- | --- | --- |
| 2020-02-14 | KR_CLI | 2020-01-01 |
| 2020-02-28 | KR_CLI | 2020-01-01 |
| 2020-03-02 | KR_CLI | 2020-01-01 |

Under the D016 ticket's approximately 2-month lag requirement, this appears to
be a look-ahead issue for D013's frozen carrier.

## Question

Should Codex:

1. Treat D013 as invalid under D016 and stop until a new ticket authorizes a
   corrected CLI lag and D013 rerun, or
2. Treat the existing `MonthEnd + 14 days` policy as the intended D013 frozen
   carrier timing despite the D016 ticket text, and continue the audit batch
   without changing D013?

Codex has not modified `src/backtest/engine.py`, existing strategy modules, or
`research_input_data/`.
