# Parser Validation Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE

## Method

- Run `parse_disclosure` against the 195 cached manual-audit ZIPs.
- Compare `parsed_effective_date` to manual-audit ground truth
  (`effective_date_value` from `manual_effective_date_audit.csv`).
- Date normalisation: range start used when ground-truth value is a range.
- In-scope rows = `suspension_related` + `resumption_related` (filtered by
  `parser_input_sample_plan.csv`).
- Out-of-scope rows reported separately in `negative_control_results.md`.

## In-scope sample size

- Total in-scope samples: **108**
- suspension_related: 67
- resumption_related: 41

## Overall comparison outcome (in-scope only)

| outcome | count |
|---|---:|
| `exact_match` | 98 |
| `missed_date` | 4 |
| `agreed_no_date` | 4 |
| `non_html_body` | 2 |

## Exact-match rate (parser vs manual audit): **98/108 = 90.7%**

### Category split

- suspension_related exact match: **62/67 = 92.5%**
- resumption_related exact match: **36/41 = 87.8%**

## Period split

| period | total | exact_match | mismatch | parser_only | missed | agreed_no_date | body_unavail |
|---|---:|---:|---:|---:|---:|---:|---:|
| `pre_2018` | 55 | 49 | 0 | 0 | 3 | 3 | 0 |
| `post_2018` | 53 | 49 | 0 | 0 | 1 | 1 | 0 |

## Parser confidence distribution (in-scope)

| confidence | count |
|---|---:|
| `high` | 98 |
| `medium` | 1 |
| `low` | 9 |

## Manual-review-required count (in-scope): **14**

(includes all correction-flagged rows and all medium/low confidence rows.)

## Baseline comparison

| baseline | sample | extraction rate |
|---|---:|---:|
| Prior simple-regex A0 | 113 | 1.8% |
| Manual audit (bs4) | 195 | 56.4% |
| Parser (this phase) overall in-scope | 108 | 90.7% exact match |
| Parser (this phase) suspension only | 67 | 92.5% exact match |
| Parser (this phase) resumption only | 41 | 87.8% exact match |

## Material improvement assessment

- Suspension exact-match 92.5% vs manual audit 92.5% extraction.
- Resumption exact-match 87.8% vs manual audit 90.2% extraction.

Parser produces strictly more structured output (suspension_start /
suspension_end / resumption_date / resumption_time) than the manual-audit
classification, with deterministic confidence labels and a strict
negative-control gate.

## What this validation does NOT do

- Does NOT certify strategy / backtest readiness.
- Does NOT open execution simulation.
- Does NOT certify correctness for delisting / liquidation / managed / alert.
- Does NOT certify across the entire S3 + pre-2018 universe (17,924 events) —
  only the 195 sampled disclosures.
