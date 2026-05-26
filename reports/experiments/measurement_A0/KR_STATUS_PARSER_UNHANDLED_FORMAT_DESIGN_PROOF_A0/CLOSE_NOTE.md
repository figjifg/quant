# CLOSE_NOTE — KR-STATUS-PARSER-UNHANDLED-FORMAT-DESIGN-PROOF-A0

## Final status

CLOSED AS UNHANDLED-FORMAT DESIGN PROOF COMPLETED / ONE GUARDED FUTURE PARSER-CHANGE
CANDIDATE RECORDED / RELATIVE-TBD AND NON-TARGET VALUES PRESERVED FAIL-CLOSED /
EXECUTION STILL CLOSED.

Referee final verdict (2026-05-26, via relay): Select A (accept initial pass) + preserve
D (all strategy / execution / downstream work remains closed). Authorized by the user's
explicit decision to open a LOCAL-ONLY unhandled-format parser-design proof phase. NOT
download/API, source-recovery, parser-change, or manual-adjudication approval.

## Accepted commit

- Initial pass: `da6b403` (pushed to origin/main; parent `212b505`).
- Code: `src/audit/measurement_a0/p_parser_unhandled_format_design_proof.py`.
- 9 required deliverables ACCEPTED (this CLOSE_NOTE.md added by the close housekeeping commit).

## Exact 23-row scope

- Target scope was exactly 23 rows, all sharing the locked prior classification:
  - prior taxonomy class `label_present_but_value_in_unhandled_format` = 23
  - prior parse status `label_no_value` = 23
  - feasibility bucket `parser_design_candidate` = 23
  - design theme `date_format_or_relative_date_handling` = 23
- All 23 are html_inline, locally available, resumption-related, 0 corrections.
- No non-target row.

## Value pattern counts (sum 23)

- relative_or_tbd_marker = 19
- other_ambiguous = 2
- date_range_or_period_text = 1
- absolute_date_unhandled_format = 1

## Design-proof bucket counts (sum 23)

- relative_tbd_keep_fail_closed = 19
- ambiguous_requires_manual_or_later_design = 2
- out_of_scope_keep_fail_closed = 1
- future_parser_change_candidate_guarded = 1

## False-positive risk counts (sum 23)

- blocked_not_evaluable = 20
- high_ambiguous = 2
- medium_requires_additional_guard = 1

## Required future approval counts (sum 23)

- none_keep_fail_closed = 20
- manual_adjudication_approval_required = 2
- parser_change_verdict_after_design_proof_review = 1

## The one genuine guarded parser-change candidate

- `20210430900254`
- proof-only value: `'21.5.3`
- proof-only normalized value: `2021-05-03`
- This is NOT accepted as an effective date and NOT parser output. Guardrail = a future
  parser MIGHT add a strict `'YY.M.D` rule, but ONLY with century disambiguation (20YY
  vs 19YY) and confirmation that the matched label-kind is the effective date for this
  event; reject if >1 distinct date or relative context. Requires a separate
  parser-change verdict.

## The other 22 rows remain fail-closed

- 19 are relative / TBD / deadline expressions ("…제출일 익일" = the day AFTER a future
  document submission; "1년 이내 … 限" = within 1 year, deadline). No absolute date
  exists; a parser change cannot recover a date that is not present.
- 1 is a suspension period resolving to delisting ("2011년 04월 21일~상장폐지") — not a
  resumption date; out of scope.
- 2 contain parseable suspension timestamps (정지일시), NOT resumption dates; the
  resumption value is genuinely absent. This is a field-selection / value-absence issue,
  NOT a date the parser fails to read — correcting the prior taxonomy's "date-like
  fragment adjacent but not parser-recognized format" framing for these rows. They
  require separate manual-adjudication approval if pursued.

## Self-audit note (disclosed during the initial pass)

A crude 2-digit-year regex first false-matched the trailing "10-12-30" inside full
4-digit dates "2010-12-30". Switched to an apostrophe-anchored detector (`'YY.M.D`) so
only genuine 2-digit-year dates count — correctly separating the 1 real unhandled-format
candidate from the 2 full-date suspension-timestamp rows.

## Accepted limits / hard locks

- Proof-only / planning evidence only.
- No parser code/rule/version change is approved or occurred.
- No `src/parsers/` edit is approved or occurred.
- No download/API/source recovery/body repair occurred.
- No manual adjudication occurred.
- No row is marked parsed/recovered/safe/validated/approved/executable/authoritative/
  strategy-ready/execution-ready/production-ready.
- No accepted/final effective date; no `effective_date`/`parsed_date`/
  `effective_date_final` final field (candidate evidence named
  `hypothetical_candidate_value_iso_PROOF_ONLY`; `is_proof_only_not_parser_output=True`).
- `rcept_dt` remains forbidden as an effective-date fallback.
- All 23 rows remain fail-closed (manual_review_required=True; all safety/readiness flags
  False).
- No downstream / C2-C3 / event-log / executable-status-table / strategy / backtest /
  execution / performance / production / paper / live / P08 / shadow work is opened.
- `git show --check HEAD` passes; CSVs use LF line endings.

## Close housekeeping

- docs/next_actions.md: phase moved Active → Closed/Frozen; Active is empty.
- All accepted initial-pass artifacts preserved unchanged.
- No next phase opened.

## Forward note

After this close, LOCAL-only measurement-layer data cleaning is effectively exhausted.
Any next direction (parser-change, manual adjudication, external source-channel recovery,
or standby) requires a separate user + Referee decision. No auto-resume.
