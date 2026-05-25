# Supersession Rule Design (Design-Only)

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0

## Purpose

Documents the conservative rules a future downstream consumer **would** apply if
this correction linkage were ever wired into an event-log pipeline. This phase
does NOT wire anything; this is design only.

## Conservative rules

1. **High-confidence correction link (`link_confidence = high`)**
   - If correction body contains an explicit effective-date change (date change
     marker present), corrected fields supersede original fields.
   - Original event remains in audit trail but is marked
     `superseded_by_correction = True`.
2. **Medium-confidence correction link (`link_confidence = medium`)**
   - `manual_review_required = True` on BOTH correction and candidate original.
   - No automatic supersession.
3. **Low-confidence or no_link (`link_confidence ∈ {low, no_link}`)**
   - BOTH correction and candidate original remain `manual_review_required = True`.
   - No supersession.
   - Correction is recorded as an unlinked correction; the candidate original
     remains valid only if independently extractable.
4. **Cancellation / withdrawal markers in body**
   - Correction text contains `취소` / `철회` / `무효` near the event reference →
     prior event MUST NOT be treated as active until linkage is resolved manually.
   - High-confidence link is REQUIRED to allow cancellation propagation.
5. **Correction changes effective date**
   - When body has date-change markers (`정정사유`, `변경사유`, `당초`, etc.) +
     a high-confidence link → original parser output for `effective_date` MUST NOT
     be used as final authoritative value.
   - The corrected `effective_date` must be re-extracted via the parser, with
     manual review required.

## Rules that are explicitly EXCLUDED from this design

- No automatic event-log finalization (C2/C3 wiring).
- No automatic execution-simulation gate updates.
- No automatic strategy-side use of corrected effective dates.
- No back-population to ops / paper / live / shadow systems.
- No correction-linkage call from production code paths.

## Conservative defaults under uncertainty

- When in doubt, prefer `manual_review_required = True` over any automatic
  supersession.
- When the correction body cannot be retrieved (`body_format = unavailable`),
  treat the correction as `no_link` regardless of title-only signals.
- When multiple candidate originals tie on score (`margin < 0.5`), DO NOT pick
  one automatically; emit `low_confidence` and require manual review.

## Design-only boundary

- This file documents rules. It does NOT implement rules in production code.
- No call site of these rules is wired into strategy / execution / performance /
  production code paths.
- Wiring requires a separate Referee verdict.
