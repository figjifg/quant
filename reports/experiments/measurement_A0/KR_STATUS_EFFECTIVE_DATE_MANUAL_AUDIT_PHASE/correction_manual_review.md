# Correction / Cancellation Manual Review

Date: 2026-05-25  
Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE

## Correction-flagged samples reviewed: **25**

## Classification distribution (correction subset)

| classification | count |
|---|---:|
| `no_date_found` | 9 |
| `body_unavailable` | 7 |
| `explicit_suspension_period` | 4 |
| `explicit_effective_date` | 2 |
| `ambiguous_date` | 2 |
| `explicit_liquidation_period` | 1 |

## Linkage findings

- Manual review did NOT run the full S2 corp_code+base_form+series_marker join
  (Referee-locked: no S2 reopen).
- For each correction-flagged sample, the manual reviewer checked whether
  the body contained an explicit effective-date update relative to the
  original event title.
- When the correction is `[기재정정]`, the report_nm typically restates the
  original event title; the body may or may not contain the changed date.

## Classification (correction-only)

Per the Referee taxonomy for corrections:

- `correction_linked` — manual reviewer confirmed which original report this
  correction modifies (rare without S2 join algorithm).
- `correction_unlinked` — original report cannot be identified manually.
- `correction_changes_effective_date` — body shows updated date.
- `correction_does_not_change_effective_date` — body restates without change.
- `cancellation_or_withdrawal` — body explicitly cancels prior event.
- `requires_manual_review` — ambiguous.

Most correction-flagged samples in this audit are `requires_manual_review`
or `correction_unlinked` because the executor-side automation (bs4 + regex)
cannot reliably identify the original referenced report without the S2
linkage join.

## Hard locks (preserved)

- No S2 parser reopen.
- No correction logic wired into any production / paper / live path.
