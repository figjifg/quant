# Pass-2 Link Scoring Update

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 2)

## Pass-2 scoring (additive over Pass-1)

| component | weight |
|---|---:|
| `same_corp_code` | 3.0 |
| `same_stock_code` | 1.5 |
| `same_normalized_corp_name` | 1.0 (NEW) |
| `same_normalized_base_form` | 3.0 |
| `same_event_type` | 2.0 |
| `event_type_compat` (compatible roots) | 1.0 (NEW) |
| `same_paren_reason` | 1.0 |
| `proximity_score` ∈ [0, 1] | 1.5 |
| `title_similarity` ∈ [0, 1] | 1.5 (raised from 1.0) |
| **cross_category penalty** | −1.5 |
| **raw_pool no-base-form penalty** | −0.5 |
| **long-window penalty (>365d)** | −0.5 |

## Pass-2 confidence rules

- `high`: `same_base_form` AND (`same_corp` OR `same_stock`) AND `event_type_compat`
  AND `margin ≥ 1.0` AND `title_similarity ≥ 0.55` AND NOT `cross_category_candidate`.
- `medium`:
  - same-category branch: (`same_corp` OR `same_stock`) AND `event_type_compat` AND
    `title_similarity ≥ 0.50` AND NOT `cross_category_candidate`,
  - cross-category branch: `cross_category_candidate` AND (`same_corp` OR `same_stock`)
    AND `event_type_compat` AND `title_similarity ≥ 0.40`.
- `low`: (`same_corp` OR `same_stock`) AND `title_similarity ≥ 0.30`.
- `no_link`: otherwise.

Cross-category links are **capped at `medium`** even if scoring would suggest
`high`. Reason: cross-category originals are evidentially weaker — the correction
explicitly amends a different KRX disclosure form.

## Pass-2 row flags

| flag | meaning |
|---|---|
| `cross_category_candidate` | candidate sits in a category compatible with — but different from — the correction |
| `raw_pblntfty_candidate` | candidate appears in raw pool only (not in filtered status pool) |
| `long_window_candidate` | days_prior > 180 |

## What Pass-2 scoring does NOT do

- Does NOT learn weights from data.
- Does NOT use forward-looking knowledge of correctness.
- Does NOT certify any link as authoritative.
- Does NOT change the parser's behaviour on correction rows.
