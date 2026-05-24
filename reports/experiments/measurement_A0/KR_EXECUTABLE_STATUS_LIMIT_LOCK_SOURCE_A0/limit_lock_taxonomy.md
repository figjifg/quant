# Limit-Lock Taxonomy

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0

## Canonical labels

| label | definition | available source |
|---|---|---|
| `official_upper_limit` | KRX-confirmed close at upper limit (no lock claim) | NOT in repo |
| `official_lower_limit` | KRX-confirmed close at lower limit | NOT in repo |
| `official_limit_lock_upper` | KRX-confirmed actual upper-limit lock (단일가 lock-up) | NOT in repo |
| `official_limit_lock_lower` | KRX-confirmed actual lower-limit lock | NOT in repo |
| `close_at_upper_limit_candidate` | rule-derived: close ≈ prev_close × (1 + lim_pct) | THIS PHASE derives |
| `close_at_lower_limit_candidate` | rule-derived: close ≈ prev_close × (1 − lim_pct) | THIS PHASE derives |
| `upper_limit_candidate_proxy_only` | OHLCV-pattern derived (W001 v2 partial subset) | repo (41 rows total, no direction) |
| `lower_limit_candidate_proxy_only` | OHLCV-pattern derived (W001 v2 partial subset) | repo (same 41 rows, no direction) |
| `not_limit` | close significantly away from limit prices | derived |
| `unknown` | cannot determine | default for un-evidenced rows |

## Critical separations

- **close_at_limit ≠ locked**: Closing at the limit price does NOT necessarily
  mean trading was locked there. A stock may close at the limit after normal
  trading. The 'lock' label requires intraday KRX confirmation (not in repo).
- **upper_limit_candidate must be distinguished from lower_limit_candidate**:
  buy executability under upper-limit lock is asymmetric with sell
  executability under lower-limit lock.
- **candidate_proxy_only is NOT official**: candidate labels MUST be flagged
  with `confidence='proxy'` at every downstream callsite.
- **unknown MUST remain unknown**: downstream code MUST NOT default unknown
  rows to executable.
- **OHLCV invariant signatures (S1-S6) must be excluded first**: an OHL=0 row
  cannot be a limit-lock candidate; quarantine takes precedence.

## Confidence levels

| confidence | meaning |
|---|---|
| `official` | KRX intraday-confirmed limit lock (NOT acquired in this phase) |
| `semi_official_rule_derived` | rule-derived candidate (this phase) |
| `proxy` | W001 v2 OHLCV-pattern derived (existing repo) |
| `unknown` | no evidence |

## Hard locks

- `candidate_proxy_only` labels MUST NEVER be used as standalone evidence of
  non-executability.
- Future strategy code MUST consult the conservative execution rule
  (`conservative_execution_rule_design.md`) before any limit-related decision.
- OHLCV invariant signature rows take precedence over limit-lock candidate
  labels.
