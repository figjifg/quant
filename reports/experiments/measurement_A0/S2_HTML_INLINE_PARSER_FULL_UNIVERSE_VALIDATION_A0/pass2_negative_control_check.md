# Pass-2 Negative-Control Check

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 (Pass 2)

## Out-of-scope universe checked: **5737**
## False positives (any in-scope field extracted): **0**

## Verdict

- Pass-1 FP: 0 / 5,737.
- Pass-2 FP: 0 / 5737.
- Regression: NONE.

Parser 1.1.0 change is gated behind `suspension_related` category branch,
so out-of-scope rows continue to short-circuit at `out_of_scope_category`
or `body_unavailable`. No in-scope field can leak.
