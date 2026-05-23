# C2/C3 Input-State Taxonomy

Date: 2026-05-23
Scope: design-only definition of 10 input states for C2/C3 consumption of parser output.

## Purpose

C2 (factor chain integration) and C3 (corporate-action day reclassification) must consume parser output without silently dropping uncertain cases. This taxonomy defines exactly how a per-event-type, per-row classification is surfaced to downstream consumers.

## 10 States (Referee-locked)

| State | Trigger condition | C2 treatment | C3 treatment | Audit log behavior |
|---|---|---|---|---|
| `available_verified` | parser_confidence ≥ acceptance gate AND manual_audit_status = passed AND PIT lock valid AND correction linkage resolved | usable as factor input | usable for `corp_action_day` reclassification | logged as `event_source=parser_v_final` |
| `available_partial` | parser_confidence ≥ acceptance gate AND manual_audit_status = not_audited AND PIT lock valid | usable as factor input WITH partial flag; downstream consumers must aggregate `n_partial` | usable for `corp_action_day` reclassification WITH partial flag | logged as `event_source=parser_partial` |
| `manual_required` | parser_confidence < acceptance gate OR extraction_errors non-empty OR ambiguous label | NOT usable as factor input; surface to audit queue | NOT usable for `corp_action_day`; remains under reserved enum | logged as `event_source=manual_required` |
| `not_available` | event_type not yet supported by any parser wave (D3c forms) | branch must accept `factor_value=None`; C2 must NOT block | `corp_action_day` remains reserved for this row | logged as `event_source=not_available` |
| `deferred_s2` | originally G5/TRAD blocker tagged DEFERRED-S2 in Round 3 | NOT usable; tracked separately under deferred ledger | NOT usable; tracked under deferred ledger | logged as `event_source=deferred_s2` |
| `unsupported_form` | base_form not in current D3a/D3b taxonomy (e.g., 추가상장 / 보호예수) | NOT usable; C2 must NOT silently include | NOT usable | logged as `event_source=unsupported_form` |
| `attachment_only` | tiny_response_flag = True OR pdf_only_flag = True | NOT usable as factor input; tracked under attachment_only_count (Referee-required separate accounting) | NOT usable for `corp_action_day` | logged as `event_source=attachment_only` |
| `parser_failed` | parser_status in {parser_exception, read_error, malformed_body} | NOT usable; surfaced as engineering issue | NOT usable; surfaced as engineering issue | logged as `event_source=parser_failed` |
| `correction_unlinked` | correction_prefix non-null AND linkage candidate not found in 180-day window | partial usability: parser output exists but original-event reference missing | NOT usable for `corp_action_day` (cannot determine cancel vs supplement) | logged as `event_source=correction_unlinked` |
| `low_confidence` | parser_confidence < acceptance gate AND no extraction_errors | NOT usable as primary factor; may be tracked as secondary signal candidate (audit-only) | NOT usable for `corp_action_day` | logged as `event_source=low_confidence` |

## State priority / classification order

When a row could match multiple states, the priority order is (highest first):

1. `parser_failed` (engineering issue — stop)
2. `attachment_only` (body not present — separate accounting)
3. `unsupported_form` (D3c / unknown base_form)
4. `not_available` (event_type not in any parser wave)
5. `deferred_s2` (G5/TRAD deferred ledger)
6. `correction_unlinked` (linkage gap)
7. `manual_required` (extraction errors or ambiguous)
8. `low_confidence` (below gate, no errors)
9. `available_partial` (above gate, not manually audited)
10. `available_verified` (above gate, manually audited)

## Audit log fields per row

Every row exported from parser to C2/C3 must carry:
- `event_source` (one of the 10 above)
- `event_status_reason` (string explaining trigger)
- `parser_confidence`
- `manual_audit_status` ∈ {passed, failed, not_audited}
- `pit_available_at`
- `cancellation_linkage` (rcept_no of original if correction, else null)
- `extraction_errors` (list, may be empty)
- `phase` (D3a / D3b / D3c-skeleton / D3c-not-yet)

## C2/C3 behavior contract

- C2 MUST accept any input state without silently dropping rows
- C2 MUST NOT treat `not_available` / `unsupported_form` / `parser_failed` rows as zero-factor (they are missing, not zero)
- C3 MUST keep `corporate_action_day` enum reserved for any row not in `available_verified` or `available_partial`
- Both C2 and C3 MUST surface `manual_required` / `correction_unlinked` rows to the audit queue, never bypass

## Hard locks

- No state collapses available_* + manual_required + not_available into a single "usable" set
- No silent type coercion (e.g., `None` → 0)
- No strategy decision branches based on these states (strategy is closed)
