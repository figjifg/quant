# Recovery-Request Schema Draft (DESIGN-ONLY — NOT APPROVED)

Date: 2026-05-26
Phase: KR-STATUS-SOURCE-RECOVERY-CANDIDATE-MANIFEST-A0

A DESIGN-ONLY sketch of what a future approved recovery request might record. NOT
approved; no field here authorizes any action.

| field | meaning |
|---|---|
| rcept_no | OPENDART receipt id of the corrupt-ZIP row |
| approved_by_referee_verdict_id | the FUTURE verdict id that would authorize recovery |
| download_approved_by_user | explicit user approval flag (FUTURE) |
| source_endpoint | OPENDART document.json (FUTURE; not called here) |
| reacquired_ok | whether re-fetch succeeded (FUTURE) |
| reparsed_parse_status | parse_status after re-acquire (FUTURE; read-only parser) |
| still_fail_closed_until_validated | always True until a separate validation verdict |

This schema is illustrative only. No recovery, download, or parser run is performed
or authorized by this phase.
