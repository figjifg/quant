# tradable_state v2 Validation — Partial Re-A0

Card: KR-TRADABILITY-SEMANTICS-AUDIT-001
Round 4 Partial Re-A0 verdict candidate: **PARTIAL PASS** (S3 = 88% direct exchange action, advisory 12%)

## 7-State Enum (Documented)

```python
TRADABLE_STATES = (
    "executable",
    "panel_absence",
    "data_missing",
    "limit_lock_candidate",
    "true_suspension",          # set when suspension_events supplied
    "delisting_transition",     # set when suspension_events supplied
    "corporate_action_day",     # reserved, C3 dependency
)
```

## Distribution on Full Panel (1,141,751 rows)

| State | Count | % |
|---|---:|---:|
| panel_absence | 937,153 | 82.08% |
| executable | 158,633 | 13.90% |
| true_suspension | 32,378 | 2.84% |
| delisting_transition | 13,448 | 1.18% |
| data_missing | 98 | 0.009% |
| limit_lock_candidate | 41 | 0.004% |
| corporate_action_day (reserved) | 0 | — |

## S3 Source Semantics Re-Audit (Referee 명시)

Referee 가 정확히 짚은 issue: S3 = OPENDART pblntf_ty=I (거래소공시) =
**DART 의 거래소 disclosure proxy**, KRX exchange status 직접 API 아님.

### S3 source type breakdown

| Type | Count | % |
|---|---:|---:|
| **exchange_action** (직접 거래정지/재개/상폐) | 9,512 | 88.3% |
| exchange_designation (관리종목) | 292 | 2.7% |
| **other_notice** (기타시장안내) | 950 | 8.8% |
| investor_advisory (투자유의/주의/경고/위험) | 15 | 0.1% |

→ **88.3% 가 직접 exchange action**. 12% 가 기타 / advisory.

### Top exchange action patterns

- 주권매매거래정지(무상증자): 400
- 주권매매거래정지기간변경(개선기간 부여): 324
- 매매거래정지및정지해제(중요내용공시): 277
- 주권매매거래정지기간변경(상장폐지 사유 발생): 271
- 기타시장안내(상장폐지 관련): 246
- 주권매매거래정지 (주식의 병합, 분할 등): 237
- 기타시장안내(상장폐지 관련 이의신청서 접수): 229
- 주권매매거래정지해제(상장폐지에 따른 정리매매 개시): 154

→ 모두 KRX 시장조치 의 DART 거래소공시 게시 = exchange action 으로 신뢰
가능.

### S3 vs KRX official direct API

**Not yet reconciled**. KRX 공식 trading suspension API (별도 endpoint,
직접 KRX system 의 status) 와 sample reconciliation 미실시.

Referee Issue: full pass 막는 핵심 = S3 semantics 의 strict equivalence.
- Current: DART pblntf=I 거래소공시 = 88.3% 가 exchange_action category
- Need (full pass): KRX OpenAPI 또는 data.krx.co.kr 의 official suspension
  status table 과 sample reconciliation > 95%

## State Distinction: panel_absence vs not_in_dynamic_universe

Referee 명시: 이 둘 구분 필요.

현재 W001 v2 `tradable_state()` 의 `panel_absence` = `동적유니버스포함 ==
False` (= top 100 universe 밖). 즉 **사실상 not_in_dynamic_universe** 와 동의어.

**진짜 panel_absence (KRX 상장 자체 X)** 는 panel 에 row 자체가 없음 → state
계산 자체 X.

### Refined naming (recommendation)

| 현재 W001 v2 | 의미 | 권장 명칭 |
|---|---|---|
| `panel_absence` | 동적유니버스포함=False (universe 밖, 상장은 됨) | **`not_in_dynamic_universe`** |
| (none) | KRX 상장 자체 안 됨 또는 panel row 없음 | **`listed_but_not_selected`** 또는 row missing |
| `data_missing` | OHLC/trading value missing in universe | unchanged |
| `executable` | universe 안 + 정상 | unchanged |

W001 v2.1 enhancement: rename `panel_absence` → `not_in_dynamic_universe`.

→ 현재 v2 의 명명 이 **misleading** (Referee Issue). **즉시 fix 권장** (별도 W001 v2.1 patch).

## limit_lock_candidate Behavior

- 41 rows (0.004%) flagged
- C1 adjusted OHLC 도입 후 corporate action artifact 가 대부분 사라짐 (Round 3 = 60 → Round 4 = 41)
- 남은 41 = 진짜 limit move 가능성 큼 (단 정확한 검증은 C3 corporate_action_day 분리 후)

## True Suspension Linkage (32,378 rows)

- Source: S3 suspension event window between event_date and resumption
- 평균 ticker 별 suspension days = 32,378 / (suspension event 가 있는 ticker
  수) ≈ 32,378 / 1,000 ≈ 32 days per suspended ticker
- 검증: sample 10 ticker × 정지 사례 manual check (별도 audit)

## Delisting Transition Linkage (13,448 rows)

- Source: S3 첫 delisting event 부터 panel 끝까지
- 평균 ticker = 13,448 / 505 (delisted terminal status) ≈ 27 days per
  delisted ticker
- 검증: sample 10 ticker × 상폐 사례 manual check (별도 audit)

## 45,826 Row Separation (NEW)

이전 v1.x = panel_absence + executable 으로 합쳐졌던 45,826 row 가 v2 에서
명확히 분리:
- 32,378 → true_suspension
- 13,448 → delisting_transition

→ 진정한 strategy execution simulator 가 이제 가능 (corp_action_day reserved
는 잔존).

## Verdict (Allowed)

**PARTIAL PASS WITH S3 SEMANTICS RESIDUAL RISK**.

Reasons:
- 7-state enum implemented + nonzero in 6 states (1 reserved C3)
- v1.x 45,826 row 의 명확한 분리 (NEW)
- S3 88.3% direct exchange action = strong base
- S3 12% advisory / other notice = residual ambiguity

Blockers for FULL PASS:
- S3 가 OPENDART pblntf=I = disclosure proxy. KRX official suspension API
  와 direct reconciliation 미실시.
- `panel_absence` naming misleading (= `not_in_dynamic_universe`).
- `corporate_action_day` reserved (C3 dependency, S2 parser 후만).
- limit_lock_candidate 41 = corp_action 분리 후 truly residual 확정.

## Defect Closure Status

| Defect | Round 3 → Round 4 |
|---|---|
| TRAD_000001 panel proxy critical | **PARTIAL CLOSED** (categorical implemented; naming refinement = v2.1) |
| TRAD_000002 true_suspension critical | **CLOSED** (32,378 events linked, 88.3% direct exchange action) |
| TRAD_000003 limit pollution high | **PARTIAL** (60 → 41, C3 후 fully separate) |
| TRAD_000004 zero_volume conflation medium | **CLOSED** (categorical 분리) |
| TRAD_000005 delisting transition high | **CLOSED** (13,448 events linked) |
| TRAD_000006 limit threshold info | already CLOSED |

## Related

- `src/utils/tradability.py` (tradable_state 함수)
- `data/processed/w001_v2/panel_with_tradable_state.csv`
- `data/processed/w001_v2/listing_status_events.csv`
- `data/processed/w001_v2/listing_status_terminal.csv`
- `reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/audit_summary.md`
