# Manual-Audit Reliability

Date: 2026-05-25  
Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE

## Reviewer-confidence distribution

| reviewer_confidence | count |
|---|---:|
| `high` | 110 |
| `medium` | 18 |
| `low` | 67 |

## Reasons for low confidence

| reason | count |
|---|---:|
| `body_no_evidence` | 60 |
| `title_only_or_label_no_value` | 18 |
| `zip_unparseable` | 7 |

## Reliability heuristics

- `high`: explicit_* classification with a parsed date value.
- `medium`: title_only_date_hint or label-present-no-value.
- `low`: body_no_evidence / body_unavailable / download_failed / unparseable
  / other.

## Executor caveat

The executor is an LLM and cannot apply the kind of judgment a domain-aware
human reviewer would (cross-referencing prior events, reading 한국어 tables
in 자회사의 주요경영사항, recognising filing patterns). The reliability
scores above reflect what a bs4 + regex pipeline can determine from each
document body. A future phase with actual human reviewers would likely
lift the `medium` and `low` confidences.

## Hard locks (preserved)

- Confidence values do NOT constitute approval to use the data downstream.
- `medium` and `low` rows MUST be treated as `unknown` at any execution-
  simulation gate.
