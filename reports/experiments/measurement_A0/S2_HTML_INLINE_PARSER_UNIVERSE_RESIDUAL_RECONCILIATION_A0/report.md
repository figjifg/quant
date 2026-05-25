# S2-HTML-INLINE-PARSER-UNIVERSE-RESIDUAL-RECONCILIATION-A0 — Report

Date: 2026-05-26  
Phase: S2-HTML-INLINE-PARSER-UNIVERSE-RESIDUAL-RECONCILIATION-A0  
Parser: `krx_status_html_inline-1.1.0` (used as-is; no feature expansion).

## Phase name and scope

Measurement-layer universe-level residual reconciliation only. suspension_related
+ resumption_related. Reconcile the exact remaining non-body / unavailable /
out-of-scope / malformed source states across the in-scope 12,187-row universe
using existing local artifacts only. No downloads, no acquisition, no strategy,
no execution simulation.

## Inputs used (paths)

- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_FULL_UNIVERSE_VALIDATION_A0/pass2_full_universe_parser_outputs.csv` (authoritative 12,187-row set)
- `data/acquired/round5_manual_audit_samples/` (cached ZIPs, read-only)
- expansion/completion parser outputs + defect ledgers (cross-check; see manifest)

## Exact row counts

- In-scope universe rows: **12187**
- Cached unique rcept_no total: **12274** (in-scope 12187 + out-of-scope 87)
- In-scope rows with a cache FILE present: **12187** (file present ≠ usable; see below)
- In-scope rows with a USABLE html_inline body: **12145** (99.66%)
- In-scope rows extracted (html_inline + date): **11434**

## Exact residual class counts

| residual_class | count |
|---|---:|
| `zip_unparseable` | 42 |
| **(usable_html_inline, non-residual)** | **12145** |

Residual total = **42**. Residual + usable = 42 + 12145 = 12187 = universe 12187. ✓

## Reconciliation from prior accepted numbers

- Prior accepted in-scope universe: 12187 → reconciled **12187** ✓ (identical).
- Prior body-available estimate: ~11977 → reconciled exact **12145** USABLE html_inline bodies (Δ +168 vs estimate; prior was an additive estimate, this is the exact reconciled count). Separately, 12187 rows have a cache FILE, but 42 of those files are unparseable (corrupt) and are NOT usable.
- Prior universe-level residual estimate: ~210 → reconciled exact **42** (Δ -168 vs estimate; reconciliation shows the real residual is smaller and is entirely zip_unparseable, with NO truly-missing / structured_xml / attachment_only rows).

## Target-set accounting confirmation

- Target-set accounting unchanged: **162 already cached + 5,579 newly acquired + 3 zip_unparseable = 5,744**.
- Target-set body_unavailable = 0 (completion phase) is CONFIRMED at universe
  level: every in-scope row now has a cache file.
- **NO 100% COMPLETION CLAIM.** Target-set body_unavailable = 0, and every
  in-scope row has a cache file, but this does NOT mean usable body coverage is
  100%: 42 cached ZIPs are unparseable (corrupt) source defects.
- **Usable html_inline body coverage = 12145/12187 = 99.66% (NOT 100%)**; 42 residual rows remain manual_review_required / unavailable.

## Residual handling

- Every residual row is in `universe_residual_ledger.csv` with explicit
  `residual_class`, `reason`, `manual_review_required = True`, and
  `executable_or_safe = False`.
- All residuals remain manual_review_required / unavailable. None promoted to
  parsed / executable / safe.
- The reconciled 42 `zip_unparseable` count exceeds the 3+4
  reported in the expansion/completion download batches because those phases
  only counted corrupt ZIPs among rows they downloaded in-run. This universe-wide
  pass re-checks ALL cached in-scope ZIPs — including ones cached in earlier
  phases (manual-audit / effective-date / correction-linkage / the 162
  already-cached) — so it surfaces every currently-corrupt cached ZIP.

## Hard locks preserved

- Execution simulation remains CLOSED. Strategy testing remains CLOSED.
- No return / NAV / performance metric produced.
- No parser feature expansion (read-only audit classifier only).
- No new downloads. No C2/C3. No production / paper / P08 / live / shadow.
- See `hard_lock_compliance_check.md`.

## Decision requested from Referee

Review reconciled counts and residual ledger. Decide whether to: (A) close as
universe residual reconciled; (B) require another reconciliation pass; (C) open a
residual-source-recovery phase (e.g. structured_xml / attachment handling) — note
that would need a separate verdict and is NOT in this phase's scope; (D) keep all
strategy research closed.

Executor does NOT self-close this phase.
