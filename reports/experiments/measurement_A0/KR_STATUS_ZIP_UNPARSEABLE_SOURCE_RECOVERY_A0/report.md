# KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0 — Initial-Pass Report

Date: 2026-05-26
Phase opened by: Referee verdict (via relay), authorized by user's explicit decision + explicit OPENDART download approval.
Executor: Claude Code. Referee: Codex.

## Phase name and scope

Source recovery of the 42 accepted zip_unparseable rows ONLY (39 correction + 3 non-correction). Re-acquire OPENDART document.xml by rcept_no, store as NEW artifacts (corrupt cache preserved unchanged), verify by sha256 + readability, and re-parse with parser krx_status_html_inline-1.1.0 READ-ONLY. All rows stay fail-closed. No parser change, no adjudication, no downstream/execution work.

## Exact 42-row accounting

- target rows: 42 = 39 correction-related + 3 non-correction (asserted; derived from source_recovery_candidate_manifest.csv).
- No non-target rcept_no downloaded or processed.

## Download attempt outcomes

| outcome | count |
|---|---:|
| `downloaded` | 42 |

## Recovery success/failure counts (sum to 42)

| recovery_status | count |
|---|---:|
| `not_recovered_opendart_status_014` | 42 |
| **total** | **42** |

## Read-only parser outcome counts (the 0 recovered_readable_zip rows)

| parse_status | count |
|---|---:|
| (none readable) | 0 |

## New recovery artifacts persisted: **42** under `data/acquired/zip_unparseable_source_recovery_a0/` (sha256 + readability in source_recovery_artifact_inventory.csv; DATA_CATALOG_NOTE.md added).
- NOTE: `data/acquired/` is gitignored per repo rules (large vendor data, regenerable from API keys), as is the existing corrupt cache. The raw 42 artifacts + catalog note are therefore LOCAL evidence; the committed manifest of record is `source_recovery_artifact_inventory.csv` (paths + sha256 + readability) in this report directory.

## Corroboration / headline finding

- All 42 re-acquisitions returned OPENDART **status 014 (파일이 존재하지 않습니다 / file does not exist)** — NOT an auth/quota error (those are 010/011/013/020).
- 42/42 re-acquired payloads are BYTE-IDENTICAL to the prior cached payload (1 distinct sha256 total). The prior 'corrupt cached ZIPs' for these rows were themselves persisted 014 error payloads (147 bytes), never real document packages.
- Conclusion: these 42 zip_unparseable residuals reflect GENUINE, REPRODUCIBLE source absence at the OPENDART document.xml endpoint — they are NOT recoverable via this authorized channel. They remain zip_unparseable / fail-closed. (A different source channel, e.g. KRX/KIND, would need its own separate verdict.)

## Defects

No defects beyond unrecovered/unreadable rows (expected residuals; remain zip_unparseable / fail-closed). source_recovery_defect_ledger.csv carries a NONE sentinel.

## Hard-lock confirmations

- Target = exactly 42 (39+3); no non-target rcept_no touched.
- Existing corrupt cache preserved UNCHANGED; recovered files in a NEW dir.
- OPENDART key used this phase only; never printed/committed/logged (attempt log records an endpoint label, not the URL+key).
- Parser krx_status_html_inline-1.1.0 read-only; no parser code/rule/version change.
- Every download/API attempt logged without credentials; every acquired artifact has sha256 + readability metadata.
- Unrecovered/unreadable rows remain zip_unparseable; all 42 rows fail-closed.
- No forbidden downstream / strategy / execution / readiness claim. No self-close; no CLOSE_NOTE this pass.

## Gate self-assessment

- All 10 gate conditions intended to hold: target=42; 39+3 preserved; no non-target processed; corrupt cache preserved; attempts logged w/o creds; artifacts have sha256+readability; parser 1.1.0 read-only; unrecovered remain zip_unparseable; all fail-closed; no forbidden claim. (All download attempts succeeded at the key level.)

## Decision requested from Referee

Executor does NOT self-close. Initial-pass report submitted; awaiting Referee review. Requesting a verdict among: A close as source-recovery complete (recovered rows recorded as read-only evidence, residuals preserved) / B another recovery pass / C downstream action for recovered rows (needs its own verdict) / D keep all strategy/execution closed.
