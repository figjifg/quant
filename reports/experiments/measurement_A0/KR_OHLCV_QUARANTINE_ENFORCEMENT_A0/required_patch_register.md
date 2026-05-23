# Required Patch Register (Documentation Only)

Date: 2026-05-23  
Phase: KR-OHLCV-QUARANTINE-ENFORCEMENT-A0.  
Status: **documentation only**. No patches implemented in this phase. A separate
Referee verdict is required to open a `KR-OHLCV-QUARANTINE-PATCH-PHASE` (not active).

## How to read this register

Each entry below is a **recommendation**, not an applied change. The exact callsites are
listed in `invalid_row_leak_defect_ledger.csv` keyed by `QENF_NNNNN` IDs. The recommended
patches assume the invalid-row contract in `invalid_ohlcv_row_contract.md` is the
authoritative specification.

## Patch families (priority order — highest defect-count first)

### PF-01 — `daily_return` derivation (27 LEAK callsites)

Every callsite that materialises a `daily_return` (or equivalent `Change`, `pct_change`,
`adj_return_pct`) currently has no documented invalid-row guard within the ±5-line scan
window. The vendor `Change` column on rows matching invalid-row signature S1 (OHL=0 /
close>0) is meaningless: the row's close is a forwarded prior close, not a same-day
price.

**Recommended patch (documentation-only spec)**:

1. Before any pipeline derives `daily_return` from `종가` / `KRX종가` / `adj_close` /
   raw `Change`, prepend a row filter that drops or masks rows matching invalid-row
   signatures S1–S6 from `invalid_ohlcv_row_contract.md`.
2. The mask SHOULD set both the price column AND the derived return column to NaN; do
   NOT keep the row with the raw value preserved.
3. Reasons to defer the patch until a separate phase:
   - All strategies that compute `daily_return` are currently in CLOSED status (no
     active strategy run).
   - The patch changes value-bearing outputs and therefore cannot be applied without
     re-running the dependent A0 audits (Round 4.x + measurement-layer A0 P0/P1).
4. Sample callsites in defect ledger: search for `column_name == daily_return`.

**Out of scope for this phase**: implementation, regression tests, or any rerun of
performance diagnostics.

### PF-02 — `KRX종가` / `종가` raw price reads in features and strategies (10 LEAK + 15 MISSING_GUARD)

Many features read the close column directly to compute z-scores, ratios, or
signals.

**Recommended patch (documentation-only spec)**:

1. Wrap every raw close read with an upstream `valid_ohlcv_mask` boolean column built
   at panel-load time from invariant signatures S1–S6.
2. Downstream code must apply `df = df[df["valid_ohlcv_mask"]]` (or equivalent mask) at
   the start of any feature computation that uses the close.
3. Encode the mask such that it is preserved across panel normalisation, sector
   aggregation, and W001 v2 derived joins.

### PF-03 — Sector aggregation cap-weighted return computation (`src/data/sector_aggregator.py`, 14 MISSING_GUARD)

`cap_weighted_return` aggregates the vendor `Change` per sector weighted by
`시가총액추정`. Both columns are RAW-unadjusted and inherit the invalid-row pollution
from constituents.

**Recommended patch (documentation-only spec)**:

1. Replace the aggregator's source of returns with `adj_return_pct` from the S1
   adjusted overlay AND apply the invalid-row mask.
2. Replace `시가총액추정` weights with W001 v2 adjusted-equivalent where available; if
   not available, mark the sector aggregate as `ALLOW_WITH_GUARD` and exclude it from
   strategy use (which is already the case under Research Freeze v2).

### PF-04 — Open price reads (`시가`, 13 MISSING_GUARD + 5 LEAK in features/strategies)

Open price is used in several strategy entries for execution simulation logic.
Invalid-row signature S1 places `0` in `시가` for non-trading rows; a strategy reading
this would attempt to enter at zero.

**Recommended patch (documentation-only spec)**:

1. Use the W001 v2 `tradable_state` column to gate any entry decision; reject rows
   whose `tradable_state` is not `tradable_no_event`.
2. Add an assertion that `시가 > 0` before any execution simulation reads it.
3. Cross-check against the listed-universe / executable-status backlogs before treating
   `tradable_state` as authoritative.

### PF-05 — `시가총액추정` market-cap weighting (14 MISSING_GUARD)

Used in cap-weighted aggregation and ranking. On invalid rows the value is still
derived as `종가 × 상장주식수`, which under S1 yields a nonsense `0` cap.

**Recommended patch (documentation-only spec)**:

1. Apply the invalid-row mask before cap aggregation.
2. Document the per-callsite mask in the function docstring.

### PF-06 — `동적유니버스포함` universe flag (7 MISSING_GUARD)

The vendor universe selection rule is not documented. Reading this flag without a
documented guard means the audit cannot certify it.

**Recommended patch (documentation-only spec)**:

1. Add a per-call site annotation:
   `# guard: vendor 동적유니버스 selection rule undocumented; this flag does NOT certify survivorship`.
2. Remove any code path that uses this flag to claim survivorship safety.
3. Mark dependent universes as `ALLOW_WITH_GUARD` (already the case in P0-1).

### PF-07 — Flow estimation columns (`기관순매수금액추정`, `외국인순매수금액추정`, etc., ~14 callsites combined LEAK + MISSING_GUARD)

These are vendor estimations; reconciliation gap is acceptable (FLOW_000007 closure)
but a guard is required at every callsite.

**Recommended patch (documentation-only spec)**:

1. Verify each flow-estimation read has a documented annotation:
   `# guard: vendor estimation; 95% within 5% of KRX official (FLOW_000007)`.
2. Mark callsites that produce a return-like output from these columns as defects
   pending the strategy lock.

### PF-08 — Aggregate KOSPI flow unit (`kospi_foreign_net`, `kospi_institution_net`, ~6 callsites)

Unit ambiguous (`KRW_mil_or_count`). Per P0-1 defect ledger.

**Recommended patch (documentation-only spec)**:

1. Block any conversion from these columns to KRW or to a return-equivalent quantity
   until the unit is resolved.
2. Annotate every callsite with the ambiguity.

### PF-09 — Data-loader normalisation (`src/data/equity_panel.py`, `src/data/market_flow.py`, `src/data/universe.py`)

The data loaders read panel columns into a normalised in-memory schema but do not
emit a single, canonical `valid_ohlcv_mask`.

**Recommended patch (documentation-only spec)**:

1. Emit a `valid_ohlcv_mask` column from the panel loader, built from the contract in
   `invalid_ohlcv_row_contract.md`.
2. Propagate the mask through every downstream join.
3. This is the SINGLE most leveraged patch — it would remove the need for per-callsite
   masks in PF-01 through PF-08.

### PF-10 — Pipeline orchestrator (`src/run_experiment.py`)

The orchestrator references panel columns in 288 places. Most are pipeline glue; many
are GUARDED by tests / conditions; 5 are flagged (2 LEAK + 3 MISSING_GUARD).

**Recommended patch (documentation-only spec)**:

1. Adopt PF-09 (valid_ohlcv_mask). The orchestrator should never operate on a panel
   that lacks the mask.
2. Add a load-time assertion that the mask exists.

## Patch policy

- These patches will NOT be applied in this phase.
- A separate Referee verdict opening `KR-OHLCV-QUARANTINE-PATCH-PHASE` is required.
- That phase must include:
  - regression tests at the data-loader boundary,
  - re-run of P0-1 + P0-2 + P1 + this phase to confirm the mask is preserved end-to-end,
  - reaffirmation of all hard locks before any strategy reopen review.

## Hard locks

- This register is documentation. **No implementation steps are taken.**
- No strategy reopen, no production / paper / P08 / live changes are implied.
- No mention of patches as a substitute for proper Referee verdict on a patch phase.
