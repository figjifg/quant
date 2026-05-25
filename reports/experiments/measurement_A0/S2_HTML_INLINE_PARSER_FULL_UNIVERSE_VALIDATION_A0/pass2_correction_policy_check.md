# Pass-2 Correction Policy Check

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 (Pass 2)

## Method

Re-apply closed `KR-STATUS-CORRECTION-LINKAGE-A0` Pass-3 rule
(`high_validated`-only authoritative use) to in-scope correction rows in
Pass-2 parser output. No change to correction policy.

## In-scope correction rows: **166**
## Authoritative-use allowed (high_validated only): **35**
## Blocked to manual review: **131**

## Regression

Identical to Pass 1:
- 35 high_validated allowed.
- 131 blocked to manual review.

Pass-2 parser change does NOT touch correction policy. The 1.1.0 fix
is for period_change_disclosure (a suspension-related sub-pattern), not
for correction-flagged rows. Correction-flagged period-change rows still
have `manual_review_required = True` regardless of after-change selection.
