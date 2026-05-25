# KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0 — Final Close Note

Date: 2026-05-26
Verdict source: Referee final close verdict, 2026-05-26 (via relay).
Initial pass commit accepted as evidence: `cf4ad41` on origin/main.

## Verdict / final status

**CLOSED AS OPENDART-CHANNEL SOURCE RECOVERY ATTEMPT COMPLETED FOR 42 ZIP-UNPARSEABLE
ROWS / STATUS-014 SOURCE ABSENCE REPRODUCED / ZIP-UNPARSEABLE FAIL-CLOSED RESIDUALS
PRESERVED / EXECUTION STILL CLOSED.**

- Decision: Select **A** (accept initial pass; close after housekeeping) **+ preserve
  D** (all strategy / execution research remains closed).
- No next phase opened. KRX/KIND recovery, parser-design, manual-review,
  correction-validation, C2/C3, execution, strategy, production, paper/live/P08, and
  shadow work all remain closed (each needs a separate user + Referee verdict).

## Accepted scope

- Exactly the 42 accepted zip_unparseable rows only; split preserved: **39
  correction-related + 3 non-correction**. No non-target rcept_no processed.
- Existing corrupt cache (`data/acquired/round5_manual_audit_samples`) PRESERVED
  UNCHANGED. New OPENDART-channel artifacts written separately under
  `data/acquired/zip_unparseable_source_recovery_a0/`.
- Parser `krx_status_html_inline-1.1.0` used READ-ONLY only; no parser
  code/rule/version change. No manual adjudication / validation / approval /
  downstream wiring / strategy / execution / readiness work opened.

## Accepted commit

- `cf4ad41` (initial pass; pushed origin/main).

## Accepted code artifact

- `src/audit/measurement_a0/p_zip_unparseable_source_recovery.py`

## Accepted key results

- Target: **42** = **39 correction + 3 non-correction**.
- Download/API attempts: **42 / 42** logged (without credentials).
- OPENDART response: **42 / 42 status 014 (파일이 존재하지 않습니다 / file does not
  exist)** — a 147-byte XML error payload, NOT an auth/quota error (those are
  010/011/013/020).
- Recovered readable ZIP: **0 / 42**.
- Still zip_unparseable: **42 / 42**.
- Fail-closed: **42 / 42**.
- Prior cached payload vs re-acquired payload: **42 / 42 byte-identical, 147 bytes,
  one sha256** (differs_from_prior_corrupt_cache=False). The prior "corrupt cached
  ZIPs" were themselves persisted 014 error payloads, never real document packages.
- Read-only parser result: N/A (0 readable ZIP). Parser version recorded
  `krx_status_html_inline-1.1.0`.
- Defect ledger: **NONE** sentinel for process defects; the 42 unrecovered rows are
  EXPECTED residuals (source absent), not fixed rows.

## Accepted caveats (recorded per verdict)

- This proves source absence **only for the authorized OPENDART document.xml
  channel**. It does NOT prove absence from every possible external source.
- Any KRX/KIND or other-source recovery would require a separate user + Referee
  verdict.
- `source_recovery_status` is availability evidence only — NOT authority, NOT safety,
  NOT validation, NOT readiness.

## Local artifact vs committed manifest nuance (required)

- The raw 42 re-acquired artifacts AND `DATA_CATALOG_NOTE.md` live under
  `data/acquired/zip_unparseable_source_recovery_a0/`, which is **gitignored per repo
  rules** (large vendor data, regenerable from API keys), exactly like the existing
  corrupt cache.
- **The raw artifacts were NOT committed to git.** The COMMITTED manifest of record is
  `source_recovery_artifact_inventory.csv` (in this report directory), which carries
  each artifact's path + byte size + **sha256** + readability. This CLOSE_NOTE does
  NOT imply the raw artifacts were committed.

## No-promotion confirmation (required)

- No row became parsed, recovered, executable, safe, authoritative, validated,
  approved, strategy-ready, execution-ready, or production-ready. All 42 remain
  `zip_unparseable` / fail-closed.

## Accepted gate state

**PASS** (all 10 gate conditions held). Closed after housekeeping.

## Accepted deliverables (preserved, unchanged)

8 required under
`reports/experiments/measurement_A0/KR_STATUS_ZIP_UNPARSEABLE_SOURCE_RECOVERY_A0/`:
source_recovery_input_manifest.csv / source_recovery_attempt_log.csv /
source_recovery_artifact_inventory.csv / source_recovery_revalidation.csv /
source_recovery_summary.md / hard_lock_compliance_check.md /
source_recovery_defect_ledger.csv / report.md.
Local (gitignored) evidence preserved unchanged: the 42 raw artifacts +
DATA_CATALOG_NOTE.md under `data/acquired/zip_unparseable_source_recovery_a0/`.

## Continuing hard locks (preserved)

- No KRX/KIND or other-source recovery without a separate verdict + access approval.
- No parser design / rule / version change. No manual adjudication / validation /
  approval. No correction row becomes authoritative.
- No C2/C3 / event-log finalization / executable-status final table.
- No strategy / backtest / execution simulation / performance metrics.
- No production / paper / P08 / live / shadow. No rcept_dt effective-date fallback.
- No row marked executable / safe / authoritative / validated / approved /
  strategy-ready / execution-ready / production-ready.
- OPENDART key remains private (never printed/committed/logged).

## End condition

`KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0` is closed. Active work empty. No next
phase opened. The 42 zip_unparseable residuals are confirmed unrecoverable via the
OPENDART document.xml channel (status 014, reproduced byte-identically) and remain
fail-closed. Await explicit user + Referee decision for any other-source recovery or
non-data-cleaning phase.
