# tradable_state v2.1 Naming Patch

Date: 2026-05-22
Status: ✅ APPLIED
Origin: Referee Round 4.1 Task 1
Card: KR-TRADABILITY-SEMANTICS-AUDIT-001

## Issue (Referee 명시)

Round 4 Partial Re-A0 의 `panel_absence` 명칭이 misleading:
- 의도: "동적유니버스포함=False" (top-100 universe 밖)
- 위험 해석: "exchange 거래 불가" (= non-tradable)

→ 같은 ticker 가 KRX 에서 정상 거래되지만 단순히 top-100 universe 밖일 수 있음.

## Patch

### Code change (`src/utils/tradability.py`)

| Before (W001 v2) | After (W001 v2.1) |
|---|---|
| `"panel_absence"` enum value | `"not_in_dynamic_universe"` |
| Docstring "panel_absence" | "not_in_dynamic_universe" + 명시 "NOT a non-tradability signal" |
| Mask logic `panel_absence` | `not_in_dynamic_universe` |

Deprecated alias dict 추가:
```python
_DEPRECATED_TRADABLE_STATE_ALIASES = {
    "panel_absence": "not_in_dynamic_universe",
}
```

(아직 reader logic 에 wire 안 됨; 외부 caller 가 옛 string 쓰면 별도 alert 가능)

### Test change (`tests/test_w001_korean_utils.py`)

`test_tradable_state_partial_categorical` test 의 expected value:
- `"panel_absence"` → `"not_in_dynamic_universe"`
- Docstring priority order text 도 같이 rename

## Verification

- ✅ `pytest tests/test_w001_korean_utils.py -v`: **7/7 PASS**
- ✅ `grep -rn "panel_absence" src/ tests/`: 4 hits (모두 doc / comment / deprecated alias dict, code 동작 영향 X)
- ✅ TRADABLE_STATES enum 의 7 values 모두 valid

## Distribution Verification

기존 Round 4 결과 (`data/processed/w001_v2/panel_with_tradable_state.csv`)
의 `tradable_state` column 은 still readable 단 enum string 이 옛 이름.
v2.1 후 새로 compute 하면 `not_in_dynamic_universe` 로 분류됨.

이 패치 후 동일 source data 로 함수 호출 시:

| State (v2.1) | Count | % | 변경 |
|---|---:|---:|---|
| **not_in_dynamic_universe** (was panel_absence) | 937,153 | 82.08% | ✅ rename only |
| executable | 158,633 | 13.90% | unchanged |
| true_suspension | 32,378 | 2.84% | unchanged |
| delisting_transition | 13,448 | 1.18% | unchanged |
| data_missing | 98 | 0.009% | unchanged |
| limit_lock_candidate | 41 | 0.004% | unchanged |
| corporate_action_day (reserved) | 0 | — | unchanged |

행 수 / 분류 동일. 명칭만 변경.

## Backward Compatibility

- 기존 `data/processed/w001_v2/panel_with_tradable_state.csv` 의 `panel_absence` 문자열 row 들은 그대로 보존 (regenerate 하면 새 이름)
- `_DEPRECATED_TRADABLE_STATE_ALIASES` 로 외부 caller 가 mapping 가능
- 새 caller 코드는 모두 `not_in_dynamic_universe` 사용

## Critical Lock (Referee 명시)

> `not_in_dynamic_universe` ≠ non-tradable

이 구분이 깨지면 tradability pass 인정 불가. v2.1 docstring 에 명시:

> "**This is NOT a non-tradability signal** — the ticker is listed and
> tradable on KRX but simply not in the dynamic top-100 universe for this
> date."

## Defect Closure Status

| Defect | Round 4 status | Round 4.1 status |
|---|---|---|
| TRAD_000001 panel proxy critical | PARTIAL (naming misleading) | **CLOSED** (renamed + docstring 명시) |

## Related

- `src/utils/tradability.py` (W001 v2.1)
- `tests/test_w001_korean_utils.py`
- `data/processed/w001_v2/panel_with_tradable_state.csv` (기존 형식 보존)
- `docs/tradability_semantics_audit.md` (Round 2 base)
- `reports/experiments/round4_partial_reA0/tradable_state_v2_validation.md` (Round 4 partial)
