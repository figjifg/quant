# S2 Manual Audit Findings — Final

Date: 2026-05-23 15:42:46

## Manual review queue across S2 phase

| Round | Manual review queue size | Notes |
|---|---|---|
| D3 v1 | 108 rows | First-pass; all rows flagged |
| D3 v2 | 108 rows | Same denominator; precision tuning round 1 |
| D3 v3 | 108 rows | Same; precision tuning round 2 |
| D3 triage | 35 (D3a) + 17 (D3b) | per-base-form deterministic vs partial vs non-deterministic |

## D3a label-determinism findings (from triage)

Recorded in `reports/experiments/S2_phase_d3_triage/d3a_manual_label_audit.md`:

| Base form | Deterministic fields (≥70% hit, ≤5 phrasings) |
|---|---|
| 자기주식취득결과보고서 | **4/4** |
| 주식소각결정 | 2/4 (amount, event_date) |
| 자기주식처분결과보고서 | 0/4 (all partial) |
| 주요사항보고서(자기주식처분결정) | 0/4 (3 partial) |
| 주요사항보고서(자기주식취득결정) | 0/4 (3 partial) |
| 주요사항보고서(자기주식취득신탁계약체결결정) | 0/4 (all non-deterministic) |
| 주요사항보고서(자기주식취득신탁계약해지결정) | 0/4 (2 partial) |

## D3b feasibility findings (from triage)

Recorded in `reports/experiments/S2_phase_d3_triage/d3b_feasibility_triage.md`:

- CB issue: event_date 5/6 NOT extractable from body tables
- BW issue: event_date 3/5 NOT extractable, 2/5 missing_xml
- conversion_request: shares + event_date 5/6 ambiguous (html_inline)

## Manual audit limitations

- Referee target was 30 samples per event type for manual audit. Acquired sample size was 4-6 per D3a base form and 5-6 per D3b sub-category — well below target.
- A true full manual audit (e.g., 30 per event type × 17 event types ≈ 500 disclosures + manual review) was not performed in this S2 phase. It is feasible as a follow-up phase but not approved by Referee for S2 close.
- D5b (manual audit) per master ticket was never executed — only D5a (sample extraction framework) was implemented.

## Hard locks

- Manual audit findings did NOT produce strategy-ready event flags
- No strategy testing conducted on audit-marked samples