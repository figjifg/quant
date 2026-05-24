# Parser Feasibility Assessment

Date: 2026-05-25  
Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE

## Method

For each event category, compute the per-sample extraction rate (explicit
effective-date class) and the dominant body format. Assess parser feasibility.
**This phase does NOT implement any parser.**

## Per-category assessment

| category | n_samples | extraction_rate | dominant_body_format | feasibility |
|---|---:|---:|---|---|
| `delisting` | 52 | 3.8% | html_inline | `parser_not_feasible_without_attachment` |
| `investment_alert` | 1 | 0.0% | html_inline | `parser_not_feasible_without_attachment` |
| `liquidation` | 3 | 0.0% | html_inline | `parser_not_feasible_without_attachment` |
| `managed` | 28 | 28.6% | html_inline | `parser_feasible_with_custom_rules` |
| `other` | 2 | 50.0% | html_inline | `parser_feasible_html_inline` |
| `resumption_related` | 41 | 90.2% | html_inline | `parser_feasible_html_inline` |
| `short_term_overheated` | 1 | 0.0% | html_inline | `parser_not_feasible_without_attachment` |
| `suspension_related` | 67 | 92.5% | html_inline | `parser_feasible_html_inline` |

## Overall: **110/195 = 56.4%**
## Overall feasibility: **parser_feasible_html_inline**

## Recommendation (decision input only — not a plan)

- If overall feasibility ≥ parser_feasible_html_inline: a future Referee
  verdict could plausibly approve `S2-HTML-INLINE-PARSER-REOPEN-PHASE`.
- If overall feasibility = parser_feasible_with_custom_rules: per-form
  custom parsers would be needed (matches S2 D3 triage finding).
- If overall feasibility = manual_review_required: manual queue is the
  primary path; parser reopen alone would not solve the gap.
- If parser_not_feasible_without_attachment: attachment/PDF parsing or
  external-source acquisition would be required.

## What this assessment does NOT do

- Does NOT approve any parser phase.
- Does NOT write parser code.
- Does NOT estimate engineering effort.
- Does NOT compare against the prior S2 D3 manual-audit results in detail
  (S2 D3a / D3b PARTIAL).

## Hard locks (preserved)

- No parser implementation.
- No S2 parser reopen.
- No strategy testing / execution simulation.
