# Official Limit-Lock Source Report

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0

## Headline

**Official daily upper-limit / lower-limit lock source: NOT IN REPO.**

- pykrx exposes no daily limit-lock list endpoint (tested: only price-change
  and OHLCV endpoints).
- KRX 정보데이터시스템 단일가매매 endpoint is not in repo (would require
  separate manual scraping with licensing).
- KOSCOM intraday halt/limit feed is commercial; not pursued.

## Best-available source acquired in this phase

Approach: apply the KRX historical price-limit rule to W001 v2 panel data to
compute per-row close_at_upper_candidate / close_at_lower_candidate.

**Rule:**
- 2010-01-04 → 2015-06-14: KOSPI/KOSDAQ ±15%.
- 2015-06-15 → present: KOSPI/KOSDAQ ±30%.

**Derivation:**
- `upper_limit_price = prev_close × (1 + lim_pct)`.
- `lower_limit_price = prev_close × (1 - lim_pct)`.
- Candidate if `|close − limit_price| / limit_price ≤ 0.001` (0.1% tick tolerance).

## Coverage

| candidate type | count |
|---|---:|
| `close_at_upper_limit_candidate` | 325 |
| `close_at_lower_limit_candidate` | 11 |

## W001 v2 limit_lock_candidate (proxy from prior derivation)

- 41 rows total in W001 v2 panel — UNDER-COUNTED.
- Compare to rule-derived candidate set (above).

## What this source CANNOT do

- Cannot distinguish 'close at limit after normal trading' from 'lock-held'.
- Cannot capture intraday VI / circuit-breaker events.
- Cannot adjust for corporate-action reference price on the rule day.
- Cannot handle IPO first-listing day (different rule).
- Cannot replace official KRX limit-lock log.

## Hard locks (preserved)

- Rule-derived candidate is `semi_official_rule_derived` confidence — NOT
  KRX-confirmed lock evidence.
- No execution simulation.
- No strategy reopen authorised by this phase.
