# KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0 — Final Close Note

Date: 2026-05-26  
Verdict source: Referee final close verdict REF-CLOSE-005, 2026-05-26 (via relay).  
Initial pass commit accepted as evidence: `d97f9a7` on origin/main.

## Verdict

**CLOSED AS PARSER NON-EXTRACTED LOCAL TAXONOMY COMPLETED / FAIL-CLOSED PARSE STATUS
PRESERVED / EXECUTION STILL CLOSED.**

- Decision: option **A** (initial pass accepted; close after housekeeping).
- Do NOT open parser-design / parser-expansion automatically. Do NOT change parser
  code. Do NOT extract or assign effective_date. Do NOT perform downloads / API
  calls / body repair.
- Do NOT open strategy testing / backtesting / execution simulation / C2-C3 /
  all-event event-log finalization / executable-status final table / production /
  paper / P08 / live / shadow work.

## Accepted scope

- Measurement-layer parser non-extracted local taxonomy only; suspension_related +
  resumption_related status rows; the 711 parser non-extracted rows only.
- Existing local artifacts + cached local bodies read-only — no downloads, no API,
  no data acquisition, no body repair, no parser feature expansion, no parser code
  change, no extraction upgrade, no effective_date extraction/assignment, no
  candidate search / body confirmation rerun, no downstream wiring, no C2/C3, no
  all-event event-log finalization, no executable-status final table, no strategy /
  performance / execution / backtest work.

## Accepted commit (initial pass)

- `d97f9a7` (pushed origin/main).

## Accepted code artifact + method

- `src/audit/measurement_a0/p_parser_nonextracted_local_taxonomy.py`
- Accepted method: read-only use of existing parser helpers
  (`extract_body_from_zip`, `find_label_hits`, `_normalize_for_scan`); parser source
  behaviour was NOT changed.

## Accepted key results

- Exact source counts: no_label_match 511 / label_no_value 200 / total 711.
- Exact correction overlap: no_label_match 11 / label_no_value 7 / total 18.
- Root-cause counts (sum to 711):

| root_cause_class | count |
|---|---:|
| only_generic_or_contextual_label | 499 |
| label_present_but_attachment_or_table_context_required | 170 |
| label_present_but_value_in_unhandled_format | 23 |
| correction_disclosure_manual_only | 18 |
| title_body_mismatch | 1 |
| **total** | **711** |

- Reconciliation by parse_status:
  - no_label_match 511 = 499 only_generic_or_contextual + 11 correction + 1 title_body_mismatch.
  - label_no_value 200 = 170 attachment/table context + 23 unhandled format + 7 correction.
- Every row has: stable `rcept_no` key, original parse_status preserved,
  `root_cause_class`, and fail-closed flags.
- All 711 rows fail-closed: manual_review_required=True, executable_or_safe=False,
  downstream_authoritative=False, parsed_clean_and_usable=False, strategy_ready=False,
  production_ready=False, effective_date_extracted=False.

## Accepted defects / limits

- Root-cause taxonomy is diagnostic / manual-review support only.
- 511 no_label_match rows remain no_label_match; 200 label_no_value rows remain
  label_no_value.
- The 170 table/structure-context rows + 23 unhandled-format rows are NOT extracted;
  manual-review-only.
- The 18 correction-overlap rows remain correction manual-review-only and
  non-authoritative.
- No root-cause class implies parser success.
- `parser_design_backlog_candidates.md` is accepted ONLY as design-only / NOT
  approved. No parser change, extraction upgrade, or row reclassification is accepted.

## Accepted gate state

**PASS** for this parser non-extracted local taxonomy phase. Closed after housekeeping.

## Accepted deliverables (preserved, unchanged)

10 required + 4 optional under
`reports/experiments/measurement_A0/KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/`:
parser_nonextracted_taxonomy_summary.md / parser_nonextracted_taxonomy_ledger.csv /
parser_nonextracted_root_cause_counts.csv / parser_nonextracted_correction_overlap.csv /
parser_nonextracted_examples.csv / parser_design_backlog_candidates.md /
fail_closed_policy_check.md / prior_phase_input_manifest.md /
hard_lock_compliance_check.md / report.md / body_text_length_distribution.csv /
unresolved_questions.md.

## Continuing hard locks (preserved)

- No return backtest / NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD.
- No post-event drift / migration / turnover / resume / reversal / flow-return.
- No raw jump alpha / price-only mean reversion.
- No generic value / quality / momentum / RS ranking.
- No DART body alpha / overhang filter alpha / flow strategy testing.
- No execution simulation. No C2/C3 integration. No all-event event log finalization.
- No executable-status final table.
- No delisting / liquidation / managed / alert parser unless explicitly opened.
- No parser feature expansion unless explicitly opened.
- No executable assumption from panel presence.
- No survivorship-safe claim unless explicitly supported.
- No unknown status treated as executable.
- No panel absence treated as non-tradable.
- No OHLCV signature treated as suspension proof.
- No rule-derived limit candidate treated as official lock evidence.
- No rcept_dt treated as effective status date.
- No effective_date inferred from rcept_dt fallback.
- No parser result described as strategy-ready.
- No correction row treated as authoritative unless high_validated and validated.
- No medium / low / no_link correction row treated as authoritative.
- No supersession rule wired downstream.
- No body_unavailable row treated as parsed or safe.
- No no_label_match row treated as parsed or safe.
- No label_no_value row treated as parsed or safe.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## Possible future phases (none active, separate Referee verdict each)

- A parser-design / feasibility phase for one or more root-cause classes (e.g. the
  170 table/structure-context rows or the 23 unhandled-format rows) — parser changes
  remain forbidden until such a phase is explicitly opened.
- Source-recovery for the 42 zip_unparseable bodies (separate verdict + download
  approval).

## End condition

`KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0` is closed. Active work empty. Await
Referee review of this close report. Under the user-authorized local measurement-layer
data-cleaning autonomy, the Referee may open the next local-only data-cleaning phase
by verdict; non-local / non-data-cleaning phases still require explicit user +
Referee decision.
