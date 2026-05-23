# C2 Corporate-Action Factor-Chain Prerequisites

Date: 2026-05-23
Scope: design-only — what C2 needs from parser output before wiring is allowed.

## C2 purpose recap

C2 = corporate-action factor chain integration. Adjusts price/return series for events that change share count, capital structure, or ownership. Without correct adjustment, return calculations include spurious jumps that look like signals but are artifacts.

## Prerequisite block (Referee-locked)

### 1. Required event types per factor

| Factor | Required event types | Reason |
|---|---|---|
| `shares_outstanding_factor` | rights_issue, bonus_issue, capital_reduction, merger_split, treasury_cancel, conversion_request | Direct share count change |
| `dilution_overhang_factor` | cb_issue, bw_issue, conversion_request | Potential future shares from convertibles |
| `treasury_position_factor` | treasury_acquire / dispose / cancel / trust_create / trust_terminate / acquire_result / dispose_result | Reduces effective float |
| `corp_action_day_flag` | ALL 14 event types (any corporate event in window) | C3 input |
| `correction_overlay` | All event types with correction_prefix | Original-event amendment |

### 2. Required fields per event

| Event type | Minimum field set | Why each is required |
|---|---|---|
| All | rcept_no, rcept_date, pit_available_at, corp_code_dart, event_type | PIT + identity |
| Share-count events | shares (numeric), event_date, effective_date | Compute adjustment factor + apply at correct date |
| Capital structure | factor (e.g., 감자 ratio) or shares_before/shares_after | Compute adjustment |
| CB/BW | amount_krw, conversion_possible_shares, conversion_price, event_date, effective_date | Overhang sizing |
| Conversion | shares, event_date, effective_date | Actual exercise event |
| Corrections | cancellation_linkage, original_rcept_no | Determine cancel vs supplement |

### 3. Factor availability semantics

For each (corp_code, calendar_date), C2 must answer:
- Is there a known corporate event whose `event_date` ≤ date AND `effective_date` ≥ date?
- If yes: factor value applies
- If state ∈ {`not_available`, `unsupported_form`, `manual_required`, `correction_unlinked`, `low_confidence`}: factor value is **unknown**, not zero
- Unknown vs zero distinction is critical — silent zero = look-ahead-equivalent bias

### 4. effective_date requirement

- C2 MUST apply factor adjustment from `effective_date`, not `rcept_date` (rcept_date is PIT availability; effective_date is when the event takes effect on price/share count)
- If `effective_date` is null AND state is `available_partial`: C2 may fall back to `rcept_date + N_days` ONLY if accompanied by an explicit `effective_date_fallback_flag = True` in the row's audit log
- If `effective_date` is null AND state is anything else: row is NOT usable for C2 factor — surface to manual queue

### 5. shares_before / shares_after requirement

- For share-count factor computation, both `shares_before` and `shares_after` are required (or one + the event delta)
- Current S2 state: `shares_before` partial (D3a 2.8%); `shares_after` 0% (D3a)
- Per Referee acceptance gate (separate document), neither field currently meets the production bar
- C2 design therefore must accept (`shares_before`=null, `shares_after`=null) and surface as `manual_required`

### 6. Correction / cancellation linkage requirement

- For any row with `correction_prefix` ∈ {[기재정정], [첨부정정]}, C2 must:
  - Apply correction's fields OVER original (override amount, shares, dates if correction provides new values)
  - If correction is `correction_unlinked` (no original found): NOT usable for C2 — surface to audit queue
- For `[첨부추가]` and `[연장결정]`: original event is intact; correction is supplementary only

### 7. Minimum parser confidence

- C2 prerequisite: parser_confidence ≥ **0.80** for `available_verified` factor input
- C2 may consume `available_partial` (confidence ≥ acceptance gate but < 0.80) WITH explicit partial flag
- C2 MUST NOT consume rows where `parser_confidence < acceptance gate`

### 8. Manual audit requirement

- C2 production wiring requires per-event-type manual audit of ≥ 30 samples (was scheduled as D5b in master ticket; never executed)
- Until D5b/Manual Audit phase completes, C2 wiring is NOT allowed (Referee-locked: design-only)

## What C2 cannot do under current S2-close state

- Wire to live factor chain (parser PARTIAL → factor unreliable)
- Backfill historical factor adjustments
- Be used by any strategy testing
- Be used by P08/paper/live readiness work

## Open items requiring future Referee approval

| Open item | Trigger phase |
|---|---|
| C2 wiring for treasury subset only (partial scope) | After `S2-D3A-ONE-MORE-PASS-PHASE` AND `S2-MANUAL-AUDIT-PHASE` for treasury |
| C2 wiring for CB/BW overhang | After `S2-D3B-CUSTOM-PARSER-PHASE` AND audit |
| C2 wiring for rights/bonus/감자/merger/split | After `S2-D3C-OPEN-PHASE` AND audit |
| Full C2 production wiring | After all D3 phases + audit + Full Re-A0 |

## Hard locks

- No C2 implementation in this design phase
- No factor calculations made
- No strategy-side use
