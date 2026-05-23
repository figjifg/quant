# Downstream Strategy Blockers

Date: 2026-05-23
Scope: design-only — explain why each affected card remains CLOSED post S2-close, and what would unblock it.

## Locked context

- All Korean standalone-alpha cards are currently CLOSED (Research Freeze v2).
- Reopening any card is a separate Referee verdict, not a consequence of this design phase.
- This document documents the parser-side and C2/C3-side prerequisites for each card's potential reopen, so that future Referee verdicts have a clear dependency view.

## Affected card register

### 1. `KR-DART-BODY-RETURN-001` (Round 1 BACKLOG)

**What it tries to do**: Use OPENDART body-disclosed treasury / dividend / shareholder-return events as direct signal source.

**Why blocked now**:
- Parser output for treasury group is `manual_required` (5 of 7 base forms) or `available_partial` (2 forms — treasury_acquire_result + treasury_cancel partial fields).
- Even the partial subset is below the C2 factor-chain `available_verified` bar.
- Strategy testing remains globally CLOSED (Research Freeze v2).

**What would unblock it (partial)**:
- `S2-D3A-ONE-MORE-PASS-PHASE` approved AND executed AND lifts treasury_acquire / treasury_dispose / treasury_cancel field extraction to ≥ 60%.
- `S2-MANUAL-AUDIT-PHASE` runs ≥ 30 samples per treasury event type and validates.
- C2 wiring approved for treasury subset.
- Research Freeze v2 reopen verdict for this specific card.

**What would unblock it (full)**:
- Above + all D3c forms (especially 합병 / 분할 / 감자 — which the original card scope covered).

### 2. `KR-OVERHANG-AVOID-001` (Round 1 BACKLOG)

**What it tries to do**: Avoid stocks with high pending dilution (CB/BW outstanding, conversion requests in window, lockup releases).

**Why blocked now**:
- D3b: CB/BW event_date = 0% extraction (Referee acceptance gate FAIL).
- conversion_request: 5/6 ambiguous (html_inline).
- D3c: lockup_release = unsupported_form.
- No usable overhang event log.

**What would unblock it**:
- `S2-D3B-CUSTOM-PARSER-PHASE` approved AND executed (4-7 weeks).
- SECTION/COVER text scanner for event_date.
- conversion_request dedicated parser family.
- `S2-D3C-OPEN-PHASE` for lockup_release.
- Manual audit + C2 wiring for overhang factor.

### 3. `KR-QUALITY-VALUE-RETURN-001` (Round 1 BACKLOG)

**What it tries to do**: Korean quality/value/shareholder-yield composite using fundamental + return events.

**Why blocked now**:
- Shareholder-yield component depends on dividend + buyback events.
- Buyback (treasury_acquire / cancel) = partial.
- Dividend events are NOT in the S2 phase parser scope (they would be a separate disclosure type — 현금ㆍ현물배당결정 / 중간배당 / 분기배당, which appear in R000 KOSPI inventory but are NOT in the Referee 10/14 event-type taxonomy).
- Fundamental (재무제표 / EDGAR-style) is a different data source entirely, NOT covered by S2 phase at all.

**What would unblock it (partial)**:
- Treasury cancel/buyback partial coverage via D3a one-more-pass.
- Dividend event parser as a NEW scope (not in S2 phase) — would be `S2-DIVIDEND-EXTENSION-PHASE` (new phase candidate, NOT currently on Referee menu).
- Fundamental data source separate from S2 (e.g., 한국 EDGAR-equivalent disclosure parser).

### 4. `KR-CONDITIONAL-SHOCK-REVERSION-001`

**What it tries to do**: Trade reversion after corporate-action-induced price shocks (e.g., post-감자, post-merger, post-소각).

**Why blocked now**:
- Requires `corp_action_day` enum to be populated (C3 reclassification).
- C3 is design-only; `corporate_action_day` enum remains reserved.
- Required event types (감자, 합병, 분할, 소각) are mostly D3c (unsupported_form).

**What would unblock it**:
- C3 wiring approved (requires Full Re-A0 + manual audit).
- D3a one-more-pass for treasury_cancel.
- D3c-open phase for 감자 / 합병 / 분할 (rights_issue / capital_reduction / merger_split).
- Research Freeze v2 reopen verdict.

### 5. Round 2 liquidity / tradability cards (where applicable)

**What they try to do**: Filter or weight by liquidity / tradability state including suspension, surveillance, limit days.

**Why blocked now**:
- TRAD_000003 (limit pollution, 41 rows) requires C3 `corp_action_day` separation to be unblocked.
- Without C3 wiring, limit pollution rows remain in tradability ambiguity.
- Round 2 strategy testing globally CLOSED.

**What would unblock**:
- C3 wiring approved.
- D3 one-more-pass + D3c open for events that move stocks to/from limit states.
- Round 2 reopen verdict (separate).

## Summary blocker matrix

| Card | Primary blocker | Phase to unblock | Estimated minimum gap |
|---|---|---|---|
| KR-DART-BODY-RETURN-001 | D3a partial → not C3-ready | D3A-ONE-MORE-PASS + MANUAL-AUDIT + C2 wiring | 4-8 weeks engineering + Referee approvals |
| KR-OVERHANG-AVOID-001 | D3b event_date 0% | D3B-CUSTOM-PARSER + D3C-OPEN (lockup) + MANUAL-AUDIT + C2 wiring | 6-12 weeks |
| KR-QUALITY-VALUE-RETURN-001 | Dividend parser missing entirely | NEW phase (not on menu) + fundamental data source | not on current roadmap |
| KR-CONDITIONAL-SHOCK-REVERSION-001 | C3 reclassification not populated | D3 phases + Full Re-A0 + C3 wiring + Referee reopen | 10+ weeks |
| Round 2 tradability cards | C3 + Round 2 reopen | Above + separate Round 2 verdict | depends |

## Cards NOT affected by this design phase

These cards' closures are independent of S2/C2/C3 state and not subject to reopen via the parser path:
- E-family (sector / breadth — closed for separate reasons, not parser dependent)
- F-family (stock selection — closed)
- G-family (risk overlay — closed)
- H-family (carry — H001 deployed in P08; not blocked by parser)
- I-family (US ETF — closed)
- K / J / Q / R / S / X-Lab — closed independently

## Hard locks

- No strategy reopened by this document
- No strategy testing implied or allowed
- Reopen of any card requires Referee verdict
- Reopen is a card-level decision, not a parser-phase auto-trigger
