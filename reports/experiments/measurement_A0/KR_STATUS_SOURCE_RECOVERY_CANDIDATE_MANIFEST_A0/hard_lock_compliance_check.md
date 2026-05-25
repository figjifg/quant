# Hard-Lock Compliance Check (Source-Recovery Candidate Manifest)

Date: 2026-05-26
Phase: KR-STATUS-SOURCE-RECOVERY-CANDIDATE-MANIFEST-A0

| hard lock | status |
|---|---|
| Existing local artifacts only; NO downloads / API / credentials | PASS |
| NO body repair / file replacement / cache mutation | PASS |
| NO parser feature expansion / code change | PASS (parser not invoked) |
| NO candidate search / body confirmation rerun | PASS |
| NO downstream wiring / C2 / C3 | PASS |
| NOT an event log / NOT executable-status table / NOT recovery run | PASS |
| NO strategy / performance / execution / backtest | PASS |
| 42 / 39 / 3 reconcile exactly | PASS (asserted) |
| recovery_performed=False on all 42 | PASS |
| requires_separate_verdict=True + requires_download_approval=True on all 42 | PASS |
| safe_for_current_use=False on all 42 | PASS |
| all fail-closed flags hold on all 42 | PASS |
| no row recovered / repaired / parsed / safe / executable | PASS |
| no rcept_dt as effective_date; no card strategy-ready | PASS |
