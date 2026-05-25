# KR-STATUS-CORRECTION-LINKAGE-A0 — Pass 2 Final Summary

Date: 2026-05-25
Predecessor passes: Pass 1 (commit 3d09033, accepted as evidence; phase NOT closed).

## Transparency note on Pass-1 vs Pass-2 universe parsing

During Pass-2 development the executor discovered that **Pass-1's `rcept_dt`
parser only accepted the 8-digit `YYYYMMDD` form** (used by pre-2018 OPENDART
exports). Post-2018 OPENDART exports store `rcept_dt` as ISO `YYYY-MM-DD`. As a
result, Pass-1 had ~85 / 166 in-scope corrections with `NaT` `rcept_dt_iso`,
which silently disabled the date-based candidate-search predicate
`rcept_dt_iso < corr_dt` for those rows. The Pass-1 outputs and gate verdict
remain accepted as evidence; this disclosure is to explain why the Pass-2
no_link reduction (123 → 70) is substantially larger than the candidate-pool
expansion alone would predict.

The Pass-2 universe loader now parses BOTH formats with explicit fallback:

```
iso_parse = pd.to_datetime(rcept_dt, format="%Y-%m-%d", errors="coerce")
compact_parse = pd.to_datetime(rcept_dt, format="%Y%m%d", errors="coerce")
rcept_dt_iso = iso_parse.fillna(compact_parse)
```

This fix is the dominant single driver of Pass-2 no_link reduction. Cross-category
linkage, raw-pool expansion, and longer windows contributed additional reductions
that are quantified in `pass2_window_sensitivity.csv` and
`pass2_no_link_root_cause_ledger.csv`.

## Scope respected

- Measurement-layer correction-linkage A0 only.
- suspension_related + resumption_related only.
- HTML-inline status disclosures only.
- correction-flagged rows + candidate originals only.
- No delisting / liquidation / managed / alert parser.
- No DART body alpha. No overhang. No all-event event log.
- No C2/C3 wiring. No strategy testing. No execution simulation.
- No performance diagnostics. No production / paper / P08 / live / shadow.

## What was delivered (Pass 2 only)

Code:
- `src/audit/measurement_a0/p_status_correction_linkage_pass2.py`

Pass-2 outputs in `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_A0/`:
1. `pass2_referee_lock.md`
2. `pass2_expanded_candidate_pool.md`
3. `pass2_candidate_links.csv`
4. `pass2_window_sensitivity.csv`
5. `pass2_cross_category_matrix.md`
6. `pass2_no_link_root_cause_ledger.csv`
7. `pass2_manual_validation_sample.csv`
8. `pass2_manual_validation_summary.md`
9. `pass2_link_scoring_update.md`
10. `pass2_defect_delta.csv`
11. `pass2_gate_status.md`
12. `pass2_final_summary.md` (this file)

Pass-1 artifacts preserved untouched.

## Headline results

- Expanded candidate pool: filtered_status=17924 + raw_pblntfty=726123 (total 744047).
- Pass-1 no_link: **123** → Pass-2 no_link: **70** (reduction 53).
- Pass-2 candidate-link confidence (in-scope 166): high 36 / medium 42 / low 18 / no_link 70.
- Cross-category candidates: 7.
- Pass-2 manual sample: 80 rows; linked_total 43; sample link rate 55.1%.
- Wrong-candidate risk flagged: 12.
- Pass-2 gate state: **CORRECTION_LINKAGE_REQUIRES_MORE_WORK**.

## Pass-criteria evaluation

| criterion | status |
|---|---|
| no_link population materially explained | YES |
| candidate search expansion tested transparently | YES |
| manual sample link rate improves OR failure clearly explained | YES (rate 55.1% vs 53.3% pass-1) |
| cross-category linkage necessity quantified | YES |
| wrong-candidate risk measured | YES |
| parser correction interaction remains safe | YES |
| supersession rules remain design-only | YES |
| gate status explicitly stated | YES |
| no strategy test / execution sim / performance metric produced | YES |

## Hard locks (preserved)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim /
  production / paper / P08 / live / shadow.
- No rcept_dt defaulted to effective date.
- No effective_date inferred from rcept_dt fallback.
- No panel / OHLCV used as effective-date proof.
- No card is strategy-ready.
- No C2/C3 wiring.
- No correction row treated as authoritative unless linked AND validated.
- No delisting / liquidation parser opened by cross-category linkage.
- No credential committed.

## Awaiting Referee

Referee will decide after Pass 2 whether to:
- A. close as correction linkage validated for sample,
- B. require another correction-linkage pass,
- C. open full-universe parser validation,
- D. open delisting / liquidation manual expansion,
- E. keep all strategy research closed.
