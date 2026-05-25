# Link Scoring Design

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0

## Candidate search

For each correction-flagged row, search candidate originals using:

- same `corp_code` if available, else same `stock_code_str`;
- same `event_category`;
- correction not itself a candidate (originals must NOT be correction-flagged);
- prior to correction `rcept_dt`;
- within time window (default 180 days; sensitivity at 30 / 90 / 365 days).

## Scoring components

Score is a weighted sum of transparent components:

| component | weight |
|---|---:|
| `same_corp_code` (1 / 0) | 3.0 |
| `same_stock_code` (1 / 0) | 1.5 |
| `same_normalized_base_form` (1 / 0) | 3.0 |
| `same_event_type` (1 / 0) | 2.0 |
| `same_paren_reason` (1 / 0) | 1.0 |
| `proximity_score` ∈ [0, 1] (1 = same day) | 1.5 |
| `title_similarity` ∈ [0, 1] (SequenceMatcher ratio) | 1.0 |

## link_confidence enum

| confidence | condition |
|---|---|
| `high` | `same_base_form` AND (`same_corp` OR `same_stock`) AND `same_event_type` AND margin ≥ 1.0 AND title_similarity ≥ 0.60 |
| `medium` | (`same_corp` OR `same_stock`) AND `same_event_type` AND title_similarity ≥ 0.55 |
| `low` | (`same_corp` OR `same_stock`) AND title_similarity ≥ 0.45 |
| `no_link` | no candidates within window OR all fail the above |

`margin` = score(top) − score(2nd best). A small margin indicates ambiguity.

## What this scoring does NOT do

- Does NOT certify any link as authoritative for downstream strategy use.
- Does NOT use future-knowledge of which original the correction "really" amends.
- Does NOT learn weights from data — weights are hand-fixed for transparency.
- Does NOT incorporate body parse output beyond the parser interaction check.
- Does NOT make any execution-simulation claim.

## Window sensitivity

| window (days) | corrections with ≥1 candidate |
|---:|---:|
| 30 | 35 |
| 90 | 44 |
| 180 | 46 |
| 365 | 54 |

