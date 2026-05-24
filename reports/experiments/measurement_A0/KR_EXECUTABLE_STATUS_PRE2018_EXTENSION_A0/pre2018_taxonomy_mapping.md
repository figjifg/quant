# Pre-2018 Taxonomy Mapping

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0

Uses the canonical taxonomy from KR-EXECUTABLE-STATUS-COVERAGE-A0:

| DART report_nm pattern | mapped category | canonical taxonomy label |
|---|---|---|
| contains `정지` AND `거래` AND NOT `해제` AND NOT `재개` | suspension_related | full_day_suspension |
| contains `해제` OR `재개` | resumption_related | resumption_day |
| contains `상장폐지` | delisting | delisting_transition |
| contains `관리종목` | managed | managed_stock |
| contains `투자` AND (`주의` OR `경고` OR `위험`) | investment_alert | investment_attention/warning/danger |
| contains `정리매매` | liquidation | liquidation_trading |
| contains `단기과열` | short_term_overheated | short_term_overheated |
| else | other | unknown (requires_manual_review) |

## Critical rules

- Same regex as Round 4 S3 — keeps the 2010-2017 dataset directly compatible
  with the 2018-2026 S3 dataset.
- `other` rows REQUIRE manual review before status assignment.
- Effective status date may differ from filing rcept_dt (DART body parse
  needed for exact dates; S2 phase CLOSED AS PARTIAL).

## Hard locks

- No new label invented without DART body evidence.
- `unknown` status MUST NOT be treated as executable.
