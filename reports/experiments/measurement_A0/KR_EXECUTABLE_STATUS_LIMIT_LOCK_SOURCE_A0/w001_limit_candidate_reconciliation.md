# W001 v2 Limit Candidate Reconciliation

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0  
Method: for each W001 v2 panel row, derive close_at_upper_candidate and
close_at_lower_candidate via KRX historical price-limit rule; compare to
existing W001 v2 `tradable_state='limit_lock_candidate'`.

## Headline: **1141751 panel rows scanned**

Reconciliation classes for rows that are EITHER a W001 candidate OR a rule
candidate (others = `not_limit`, omitted from per-row ledger):

| reconciliation_class | count |
|---|---:|
| `rule_candidate_but_no_repo_flag` | 334 |
| `repo_candidate_but_no_official_support` | 39 |
| `matched_limit_candidate` | 2 |

## Interpretation

- `matched_limit_candidate`: W001 v2 flagged the row AND the rule-derived
  close matches the upper/lower limit. Both signals agree.
- `repo_candidate_but_no_official_support`: W001 v2 has the candidate flag,
  but `close ≠ rule-derived limit price`. Investigate why — could be
  corporate-action prev_close adjustment, different lim_pct (IPO day-1),
  or a W001 v2 false positive.
- `rule_candidate_but_no_repo_flag`: KRX historical rule says `close ≈
  limit_price` but W001 v2 did NOT flag the row. This expands the candidate
  set significantly — the W001 v2 41-row set was UNDER-COUNTED.

## Note on W001 v2 derivation

The 41-row W001 v2 `limit_lock_candidate` count is implausibly low for an
8-year, ~900-ticker panel. The much larger rule-derived candidate count
(see ledger) suggests W001 v2 derivation did not consistently apply the
historical rule. This audit phase confirms the rule-derived set is the
correct best-available proxy.

## Hard locks (preserved)

- Rule-derived candidate is NOT official limit-lock evidence.
- W001 v2 41-row count is incomplete and SHOULD NOT be used as the canonical
  candidate set going forward.
- No execution simulation.
