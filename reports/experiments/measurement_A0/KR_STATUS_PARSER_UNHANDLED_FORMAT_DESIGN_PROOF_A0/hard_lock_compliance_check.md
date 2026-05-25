# Hard-lock compliance check — KR-STATUS-PARSER-UNHANDLED-FORMAT-DESIGN-PROOF-A0

| lock | status |
|---|---|
| target = exactly 23 rows | PASS |
| all 23 from `label_present_but_value_in_unhandled_format` | PASS |
| all 23 within `date_format_or_relative_date_handling` theme | PASS |
| no non-target row included | PASS |
| no download / API / credential / source-recovery / body-repair | PASS (read-only cache + accepted CSVs) |
| no parser code/rule/version change | PASS (parser imported read-only; not modified/invoked to change outputs) |
| no edits under src/parsers/ | PASS |
| no parser/candidate-linkage/body-confirmation rerun changing accepted outputs | PASS |
| every row fail-closed | PASS (manual_review_required=True; all safety/readiness flags False) |
| no row newly parsed/recovered/executable/safe/authoritative/validated/approved/ready | PASS |
| candidate date/value evidence hypothetical/proof-only, not final | PASS (named *_PROOF_ONLY; no effective_date/parsed_date column) |
| false-positive guardrails recorded for future parser-change candidates | PASS |
| relative/TBD/unresolvable values not promoted, stay fail-closed | PASS |
| outputs separate design proof from approved parser behavior | PASS |
| no downstream/strategy/execution/readiness claim | PASS |
| CSVs LF + git show --check HEAD passes | PASS (verified post-commit) |
| no rcept_dt as effective date | PASS |
| no self-close / no CLOSE_NOTE this pass | PASS |
