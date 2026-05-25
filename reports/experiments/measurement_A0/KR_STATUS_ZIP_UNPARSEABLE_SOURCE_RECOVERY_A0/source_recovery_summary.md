# KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0 — Summary

Date: 2026-05-26

## Target: 42 zip_unparseable rows (39 correction + 3 non-correction)

## Download attempt outcomes

| outcome | count |
|---|---:|
| `downloaded` | 42 |

## Recovery status (sum to 42)

| recovery_status | count |
|---|---:|
| `not_recovered_opendart_status_014` | 42 |
| **total** | **42** |

## Read-only parser result (recovered_readable_zip rows only)

| parse_status | count |
|---|---:|

## New recovery artifacts persisted: **42**

## Corroboration (re-acquisition vs prior cached payload)

- 42/42 re-acquired payloads are byte-identical to the prior cached payload (differs_from_prior_corrupt_cache=False); 1 distinct sha256 across all artifacts.
- Finding: the prior 'corrupt cached ZIPs' for these rows were themselves persisted OPENDART status-014 (file-does-not-exist) error payloads, not real document packages. Re-acquisition reproduces the identical 014 deterministically → genuine, reproducible SOURCE ABSENCE at OPENDART document.xml, not a transient/local corruption. These rows are not recoverable via this channel.

## Unresolved defects

None beyond unrecovered/unreadable rows (which remain zip_unparseable / fail-closed).

## Fail-closed

- All 42 rows remain fail-closed. Unrecovered/unreadable rows remain zip_unparseable. Successful read-only extraction is phase-local evidence only and promotes nothing.
