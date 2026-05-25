# Correction Policy Application Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0

## Method

Apply closed `KR-STATUS-CORRECTION-LINKAGE-A0` Pass-3 rules:
- ONLY `high_validated` correction links may be treated as design-level
  sample-supported evidence.
- `medium_needs_manual` / `low_needs_manual` / `no_link` /
  `rejected_wrong_candidate` rows remain MANUAL-REVIEW-ONLY.
- No correction row becomes authoritative by default.
- Supersession remains design-only.
- No downstream wiring authorised.

## In-scope correction rows: **166**
## Authoritative-use allowed (high_validated only): **35**
## Blocked to manual review: **131**

## Pass-3 confidence distribution

| pass3_confidence | count |
|---|---:|
| `high_validated` | 35 |
| `medium_needs_manual` | 42 |
| `low_needs_manual` | 18 |
| `no_link` | 71 |
| `rejected_wrong_candidate` | 0 |

## Important boundary

- Pass-3 confidence was computed in `KR-STATUS-CORRECTION-LINKAGE-A0`.
- This phase does NOT recompute Pass-3 confidence — it APPLIES the closed rule.
- Parser behaviour on correction rows unchanged (still forces manual review).
- No row is promoted to authoritative beyond Pass-3 rules.
