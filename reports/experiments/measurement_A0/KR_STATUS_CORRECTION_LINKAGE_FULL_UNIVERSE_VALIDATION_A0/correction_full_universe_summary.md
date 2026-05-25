# KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0 — Summary

Date: 2026-05-26
Phase opened by Referee directive REF-OPEN-002 (via relay).
Predecessor: KR-STATUS-CORRECTION-LINKAGE-A0 Pass 3 (commit 2f890d7).

## What this phase adds over Pass 3

- Pass 3 computed the 166-row universe counts with the SCORE-ONLY classifier
  and ran the body-confirmation gate only on the ~72-row manual sample.
- Body coverage has since expanded (~11.5% → ~98.3%). All 166 in-scope
  correction rows now have a cached body, so the body-confirmation gate is
  applied to EVERY row here (cache-only; no downloads).

## In-scope correction rows: **166**

## Cached body-format breakdown (read-only classifier)

| body_format | count |
|---|---:|
| `html_inline` | 127 |
| `zip_unparseable` | 39 |

## Full-universe 5-tier confidence (post-body, AUTHORITATIVE — sums to 166)

| confidence | this phase (post-body) | Pass-3 (score-only) | delta |
|---|---:|---:|---:|
| `high_validated` | 17 | 35 | -18 |
| `medium_needs_manual` | 52 | 42 | +10 |
| `low_needs_manual` | 7 | 18 | -11 |
| `no_link` | 73 | 71 | +2 |
| `rejected_wrong_candidate` | 17 | 0 | +17 |
| **total** | **166** | **166** | — |

## Score-only re-derivation (control — must match Pass 3 exactly)

| confidence | this phase (score-only) | Pass-3 | match |
|---|---:|---:|:--:|
| `high_validated` | 35 | 35 | ✓ |
| `medium_needs_manual` | 42 | 42 | ✓ |
| `low_needs_manual` | 18 | 18 | ✓ |
| `no_link` | 71 | 71 | ✓ |
| `rejected_wrong_candidate` | 0 | 0 | ✓ |

## Evidence-state distribution

| evidence_state | count |
|---|---:|
| `html_inline_body_confirms_candidate` | 63 |
| `no_candidate` | 47 |
| `source_blocked_zip_unparseable` | 39 |
| `html_inline_body_no_candidate_ref` | 17 |

## Blocked-overlay distribution (extra classes mapped onto the 5-tier)

| blocked_overlay | count |
|---|---:|
| `(none — high_validated or clean no_link)` | 70 |
| `other_manual_review_required` | 40 |
| `source_blocked_zip_unparseable` | 39 |
| `source_blocked_non_extracted` | 17 |

## Validation status

- link_validated (= high_validated, body-confirmed): **17**
- supersession_ready = yes (design-only): **17**
- manual_review_required: **166 / 166** (ALL correction rows; hard lock).

## Hard locks preserved

- Cache-only; no downloads / API / acquisition. No parser feature expansion.
- Correction rows remain manual_review_required; parser output
  non-authoritative. medium / low / no_link / blocked rows NOT authoritative.
- Supersession design-only; no downstream wiring. No C2/C3. No execution sim.
- No rcept_dt used as effective_date. No strategy / performance / production.
