# D2 Failure Modes Register

Consolidated list of failure modes observed in D1+D2, and the classification policy for each.

| Failure mode | D1 count | D2 count | Classification | Parser policy |
|---|---|---|---|---|
| tiny_response (body absent) | 4 | 0 | attachment_only_flag = True | excluded from parser denominator |
| not_parseable_body (BadZipFile / malformed XML) | 0 | 0 | not_parseable_body = True | manual_review_required |
| http_non_200 | 0 | 0 | retry → fail | logged separately |
| req_exception (network) | 0 | 0 | retry → fail | logged separately |

## Other identified failure modes (design-only, not yet hit)

- `correction_link_ambiguous`: multiple candidate originals in time window → parser_confidence reduced
- `withdrawal_no_explicit_original`: 철회신고서 body does not name original rcept_no → use corp_code + 30-day window fallback
- `subsidiary_corp_code_mismatch`: 자회사 주요경영사항 suffix uses parent corp_code → must remap
- `series_marker_missing`: 전환청구권행사 회차 marker null → linkage hard
- `kosdaq_only_form`: D2 KOSDAQ list API surfaced disclosure types not in R000 KOSPI inventory → D3 D3c form map must extend

## Register file

Raw download log + failure detail: `data/acquired/round4/s2_dart_body_d2/d2_download_log.csv` (gitignored)
Persisted failure rows: `data/acquired/round4/s2_dart_body_d2/d2_failure_ledger.csv` (gitignored)