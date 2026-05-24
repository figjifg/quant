# Conservative Execution Rule Design (Design-Only)

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0

**This is design only.** No execution simulation runs in this phase. No
strategy testing. The rules below define how a *future* execution simulator
(if/when authorised) would handle limit-lock candidates conservatively.

## Principle

When official limit-lock evidence is NOT available, assume the worst case
for the simulator's order direction. Asymmetric: buyer hits upper-lock,
seller hits lower-lock.

## Decision matrix

| candidate type | buy intent | sell intent | rationale |
|---|---|---|---|
| `close_at_upper_limit_candidate` | **fail-closed (assume not executable)** | conservative: assume executable; flag as stress | upper-lock typically means buy queue exhausted; sells more likely to fill |
| `close_at_lower_limit_candidate` | conservative: assume executable; flag as stress | **fail-closed (assume not executable)** | lower-lock typically means sell queue exhausted; buys more likely to fill |
| `not_limit` | normal | normal | no constraint |
| `unknown` | **fail-closed** | **fail-closed** | conservative default |
| `upper_limit_candidate_proxy_only` (W001 v2 41 rows; no direction) | **fail-closed for BOTH directions** | **fail-closed for BOTH directions** | proxy lacks direction information; must be conservative |
| official_limit_lock_upper (FUTURE — not in repo) | always non-executable for buy | always executable for sell (subject to other gates) | exact lock evidence trumps candidate label |
| official_limit_lock_lower (FUTURE — not in repo) | always executable for buy (subject to other gates) | always non-executable for sell | exact lock evidence trumps candidate label |

## Rule precedence (descending priority)

1. OHLCV quarantine (S1-S6 from `KR_OHLCV_QUARANTINE_ENFORCEMENT_A0`): if
   the row matches any quarantine signature, return `unknown` and
   fail-closed regardless of limit candidate status.
2. `executable_status` (from `KR_EXECUTABLE_STATUS_COVERAGE_A0`):
   if `full_day_suspension` / `delisting_transition` / `liquidation_trading`
   / `managed_stock`, return non-executable regardless of limit candidate.
3. **Official limit-lock label** (when ever acquired): use directly.
4. **Rule-derived `close_at_upper_limit_candidate` / `close_at_lower_limit_candidate`**:
   apply asymmetric conservative rule above.
5. **Proxy `upper_limit_candidate_proxy_only` / `lower_limit_candidate_proxy_only`**:
   fail-closed for both directions.
6. `not_limit` + executable_status `executable`: normal execution allowed.
7. `unknown` (default for un-evidenced rows): fail-closed.

## What this rule does NOT do

- Does NOT estimate the probability of execution under limit-lock.
- Does NOT model partial fills or queue position.
- Does NOT model the next-day re-open after a limit-lock-induced halt.
- Does NOT apply to ETFs / ETNs / KONEX (different limit rules).
- Does NOT replace official limit-lock data when it becomes available.

## Implementation deferred

Implementation requires:
1. A separate Referee verdict opening an execution-simulation patch phase.
2. The official KRX intraday limit-lock data (currently not in repo).
3. A re-run of the dependent A0 audits with the new rule wired in.

Until then, this rule design remains documentation-only. Any future
strategy code that references limit-lock state MUST cite this rule
explicitly at the call site.

## Hard locks (preserved)

- No execution simulation in this phase.
- No strategy reopen authorised.
- No production / paper / P08 / live / shadow change.
