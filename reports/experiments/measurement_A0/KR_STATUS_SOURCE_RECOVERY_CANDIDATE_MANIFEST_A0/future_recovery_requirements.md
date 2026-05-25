# Future Recovery Requirements (LOCAL STATEMENT — no recovery performed)

Date: 2026-05-26
Phase: KR-STATUS-SOURCE-RECOVERY-CANDIDATE-MANIFEST-A0

This states what a FUTURE recovery WOULD require. It performs NO recovery and grants
NO authorization. Recovery remains gated behind a separate Referee verdict + explicit
download approval.

## What future recovery of the 42 zip_unparseable rows would require

1. A separate Referee verdict explicitly opening a source-recovery phase.
2. Explicit user download/API approval (OPENDART document.json re-fetch by rcept_no).
3. Re-acquire each corrupt `document.xml` ZIP from the source, replacing ONLY the
   corrupt local cache entry (no other cache mutation).
4. Re-validate each re-acquired body with the parser (read-only) and re-classify
   parse_status. Until then every row stays `zip_unparseable`, fail-closed.
5. No effective_date assignment, no downstream wiring, no executable-status use —
   those remain separately gated even after a successful recovery.

## Why these rows cannot be locally adjudicated now

- The cached ZIP is corrupt (BadZipFile), so there is no body text to inspect. No
  local-only step can recover the content; it MUST be re-fetched from source.

## Distribution context (for prioritization only — NOT a recovery plan)

- 39 of 42 are correction rows; all 39 carry correction action class
  `zip_unparseable_requires_source_recovery`.
- Underlying linkage confidence of the 39 correction rows (had their bodies been
  readable): {'no_link': 20, 'medium_needs_manual': 12, 'low_needs_manual': 7}.
- 3 of 42 are non-correction status rows.
