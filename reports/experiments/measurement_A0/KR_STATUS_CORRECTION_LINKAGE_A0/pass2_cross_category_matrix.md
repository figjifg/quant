# Pass-2 Cross-Category Compatibility Matrix

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 2)

## Purpose

For a small number of corrections, the original may sit in a category other than
the correction's own (e.g. a suspension-correction whose original is the delisting
decision that triggered the suspension). This matrix governs which cross-category
candidates are CONSIDERED — not which are AUTHORITATIVE.

## Compatibility rules

### `correction.event_category = suspension_related`

| candidate event_category | title-token gate (any-of) |
|---|---|
| `suspension_related` | (none — same-category always allowed) |
| `delisting` | `상장폐지`, `정리매매`, `상장폐지 사유` |
| `liquidation` | `정리매매`, `상장폐지` |
| `managed` | `관리종목`, `투자주의`, `투자경고`, `투자위험` |
| `short_term_overheated` | `단기과열` |
| `other` | `매매거래정지`, `정지및정지해제`, `중요내용공시` |

### `correction.event_category = resumption_related`

| candidate event_category | title-token gate (any-of) |
|---|---|
| `resumption_related` | (none — same-category always allowed) |
| `suspension_related` | (none — paired event) |
| `other` | `정지해제`, `매매재개`, `중요내용공시`, `매매거래정지및정지해제` |

## Penalties and bonuses

- Cross-category candidate carries a `-1.5` score penalty so same-category
  candidates win ties.
- Raw-pool candidate without `same_base_form` carries a `-0.5` penalty (raw rows
  often have less-canonical titles).
- Days-apart > 365 carries a `-0.5` penalty (longer windows are correctness-risky).

## What this matrix does NOT do

- Does NOT parse delisting / liquidation / managed / alert / other categories.
- Does NOT mark a cross-category link as `high` confidence (capped at `medium`
  even when scoring would allow `high`).
- Does NOT treat cross-category links as authoritative.
- Does NOT auto-apply supersession across categories.

## What this matrix DOES do

- Lets the scorer surface a plausible original sitting in another KRX bucket so
  Pass 2 can quantify the no_link root-cause `cross_category_original_likely`.
