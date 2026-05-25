# Approval-Boundary Memo

Date: 2026-05-26
Phase: KR-STATUS-SOURCE-RECOVERY-CANDIDATE-MANIFEST-A0

This manifest is a LOCAL PACKET. It explicitly does NOT authorize any of:

- ❌ downloads / API calls / credential use,
- ❌ body repair / file replacement / cache mutation,
- ❌ parser rerun beyond a FUTURE approved recovery,
- ❌ marking any row parsed / extracted / safe / executable / downstream-authoritative,
- ❌ effective_date assignment,
- ❌ event-log finalization / executable-status table / C2-C3 / strategy / execution /
  production / paper / P08 / live / shadow.

What it DOES do: enumerate the 42 corrupt-ZIP source defects with metadata + blocker
tags + recovery-boundary flags, so that IF a future recovery phase is ever opened
(by a separate Referee verdict + explicit download approval), the candidate set and
its constraints are already documented. Until then, all 42 remain fail-closed and
`safe_for_current_use=False`.
