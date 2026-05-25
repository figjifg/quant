# Pass-3 Supersession Readiness (Design-Only)

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 3)

## Pass-3 candidate links assessed: **166**

| supersession_ready | count |
|---|---:|
| `yes` (would supersede in hypothetical downstream) | 9 |
| `blocked` (manual review required) | 86 |
| `n/a` (no link / out of scope) | 71 |

## Assessment rules (design-only)

A correction link is `supersession_ready = yes` ONLY if all of the following hold:

1. Pass-3 confidence = `high_validated`.
2. Body cross-check confirmed candidate title or date.
3. Correction body contains a date-change marker (`정정사유`, `변경사유`,
   `당초`, `변경된`, `정정된`).
4. No `body_conflict` flag.
5. Correction is NOT a cancellation / withdrawal.
6. Candidate is same-category (NOT cross-category).

Anything else → `supersession_ready = blocked` → manual review required.

## Important boundary

- Supersession is **design-only**.
- No downstream wiring.
- Even `supersession_ready = yes` rows MUST go through manual review under
  the current conservative framework. They are merely identified as the
  rows where a future hypothetical consumer could apply supersession.
- This file does NOT authorise any strategy / execution / performance use.

## Per-row detail

See `pass3_candidate_links_recalibrated.csv` for the `supersession_ready`
field on each row.
