# Round 3 Defect Ledger Schema

Date: 2026-05-22
Status: REQUIRED for all Round 3 A0 AUDIT cards
Applies to: KR-G5-ADJOHLC-CORPACT-AUDIT / KR-ID-LIFECYCLE-MASTER-AUDIT /
KR-TRADABILITY-SEMANTICS-AUDIT / KR-TOP100-PIT-LINEAGE-AUDIT /
KR-FLOW-UNIT-TIMESTAMP-AUDIT

## Purpose

Defect ledger = 각 A0 audit 의 발견 (defect) 을 row-level 로 기록.
return / performance metric 대체 output. 모든 발견을 reproducible,
auditable 형식으로.

이 ledger 가 Round 3 의 핵심 산출물. Strategy performance metric 자리에
**defect count + severity + reconciliation rate + repair feasibility** 가
들어간다.

## Required Schema

| Field | Type | Description |
|---|---|---|
| `defect_id` | string | 사이클 내 unique. 카드 prefix + 일련번호 (예: `G5_000001`) |
| `card_id` | string | KR-G5-ADJOHLC-CORPACT-AUDIT-001 등 |
| `audit_item` | string | spec 의 "허용 작업" 중 어느 audit (예: `adjusted_alias_check`) |
| `defect_type` | enum | 아래 enum 참조 |
| `severity` | enum | `critical` / `high` / `medium` / `low` / `informational` |
| `location_file` | string | 발견 위치 (예: `src/utils/corporate_action.py:94`) |
| `location_data` | string | 데이터 위치 (예: `panel/종목코드=005930/날짜=2020-07-02`) |
| `affected_rows` | int | 영향 받는 row 수 (panel / event 기준) |
| `affected_tickers` | int | 영향 받는 unique ticker 수 |
| `affected_dates_range` | string | 영향 받는 date 범위 (예: `2018-01-02 ~ 2024-12-30`) |
| `reconciliation_status` | enum | `verified_against_external` / `verified_against_internal` / `unverified` / `not_applicable` |
| `reconciliation_rate` | float / null | external source 와 일치 비율 (0.0-1.0) |
| `evidence_summary` | string | 1-2 line 핵심 증거 |
| `repair_path` | enum | `requires_external_source` / `requires_code_fix` / `requires_both` / `not_repairable` |
| `repair_feasibility` | enum | `high` / `medium` / `low` / `unknown` |
| `repair_effort_estimate` | string | 시간 / 비용 추정 (예: `1-4 weeks vendor acquisition`) |
| `downstream_block_cards` | string | 이 defect 가 block 하는 카드 list (CSV, 예: `KR-LIQ-MIGRATION-001,KR-LIQ-FRAGILITY-AVOID-001`) |
| `notes` | string | free text |
| `discovered_at` | timestamp (UTC) | 발견 시각 (ISO 8601) |

## `defect_type` Enum

각 audit 카드 별 자주 발견되는 defect type:

### KR-G5-ADJOHLC-CORPACT-AUDIT-001
- `adjusted_column_missing`
- `adjusted_column_is_raw_alias`
- `extreme_return_unexplained` (예: 147 events)
- `corporate_action_factor_unreproducible`
- `cancellation_linkage_missing`
- `delisted_name_excluded_from_panel`
- `event_source_missing`

### KR-ID-LIFECYCLE-MASTER-AUDIT-001
- `ticker_rotation_unmapped`
- `name_change_unmapped`
- `delisting_terminal_event_missing`
- `merger_continuation_unmapped`
- `code_reuse_unrecognized`
- `permanent_id_source_missing`
- `disappeared_ticker_no_explanation`

### KR-TRADABILITY-SEMANTICS-AUDIT-001
- `tradability_flag_is_panel_presence_proxy`
- `true_suspension_indistinguishable`
- `limit_lock_polluted_by_corporate_action`
- `status_column_missing`
- `delisting_transition_indistinguishable`
- `data_missing_vs_panel_absence_conflation`

### KR-TOP100-PIT-LINEAGE-AUDIT-001
- `generation_script_missing`
- `selection_rule_undocumented`
- `survivor_universe_suspected`
- `delisted_member_absent`
- `market_cap_timestamp_unclear`
- `trading_value_timestamp_unclear`
- `membership_not_reproducible`

### KR-FLOW-UNIT-TIMESTAMP-AUDIT-001
- `sign_convention_unverified`
- `unit_inconsistency`
- `publication_lag_unknown`
- `t1_signal_safety_unconfirmed`
- `missingness_concentrated_in_failed_names`
- `nonzero_flow_on_nontradable_day`
- `vendor_documentation_missing`

### Cross-card (common)
- `documentation_gap`
- `function_misleading_name`
- `policy_default_too_loose`
- `metadata_only_no_actual_adjustment`

## `severity` Definition

| Severity | 의미 | 예 |
|---|---|---|
| `critical` | strategy diagnostic 자체 불가 (Round 3 gate kill) | adjusted OHLC 없음 + repair source 없음 |
| `high` | 측정 결과 신뢰성 심각하게 훼손 | tradability flag 가 panel presence proxy |
| `medium` | 결과 해석에 caveat 필요 | name change 일부 unmapped |
| `low` | 보조 audit 또는 향후 fix | 함수 이름 misleading |
| `informational` | 기록 가치만 (action X) | 일부 sample variability |

## `repair_path` Definition

| Path | 의미 |
|---|---|
| `requires_external_source` | 사용자 host 작업으로 vendor / KRX 등 외부 source 확보 필요 |
| `requires_code_fix` | repo 코드 수정만으로 가능 (소스 충분, 적용만 안 됨) |
| `requires_both` | external source + code fix 둘 다 필요 |
| `not_repairable` | 현재 데이터 / 코드 / source 로 fix 불가 (e.g. historical data lost) |

## Output File Convention

각 카드의 defect ledger:

| 카드 | 경로 |
|---|---|
| KR-G5-ADJOHLC-CORPACT-AUDIT-001 | `reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/defect_ledger.csv` |
| KR-ID-LIFECYCLE-MASTER-AUDIT-001 | `reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/defect_ledger.csv` |
| KR-TRADABILITY-SEMANTICS-AUDIT-001 | `reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/defect_ledger.csv` |
| KR-TOP100-PIT-LINEAGE-AUDIT-001 | `reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/defect_ledger.csv` |
| KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 | `reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/defect_ledger.csv` |

각 카드에 추가 audit summary:
- `reports/experiments/<CARD_ID>/audit_summary.md` = pass/fail 집계 + 재현
  방법 + repair feasibility 종합

## Round 3 Aggregate Output

5 카드 ledger 통합:
- `reports/experiments/round3_aggregate/round3_defect_summary.md` =
  card × defect_type × severity 매트릭스 + 통합 repair feasibility

## Pre-Audit Checklist

각 audit 시작 전:

- [ ] Spec 파일 (`spec_KR_*_AUDIT_A0.md`) 의 "허용 작업" / "금지 작업"
      확인
- [ ] `docs/round3_no_performance_rule.md` 의 forbidden metric / pattern
      확인
- [ ] Output 디렉토리 생성 (`reports/experiments/<CARD_ID>/`)
- [ ] Defect ledger CSV header 준비 (위 schema)

## Post-Audit Checklist

각 audit 종료 후:

- [ ] Defect ledger CSV 저장
- [ ] `audit_summary.md` 작성 (defect count by severity, repair path
      breakdown, downstream block cards)
- [ ] Pass / fail status 결정 (각 spec 의 kill gate 와 매칭)
- [ ] `docs/round3_missing_source_register.md` 에 새 missing source 추가
      (해당 시)
- [ ] Referee 보고용 short summary (사용자 cut-and-paste 가능 형식)

## Related

- `docs/round3_referee_verdict_lock.md` — Round 3 verdict
- `docs/round3_no_performance_rule.md` — forbidden metrics/patterns
- `docs/round3_missing_source_register.md` — missing source 누적
- 5 spec: `research/experiments/spec_KR_*_AUDIT_A0.md`
