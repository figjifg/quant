# Permanent ID Fallback Validation — Partial Re-A0

Card: KR-ID-LIFECYCLE-MASTER-AUDIT-001
Round 4 Partial Re-A0 verdict candidate: **PARTIAL PASS** (fallback = ticker-based, not full corp-code)

## Coverage Reproduction

| Source | Count | Coverage |
|---|---:|---:|
| DART corp_code | 783 | 94.0% |
| KRX ticker fallback | 50 | 6.0% |
| **Total** | **833 / 833** | **100%** ✅ |

## Fallback 50 Stability Analysis

Fallback rule: `permanent_id = "KRX_TICKER_<ticker>"` (no DART corp_code match).

### Fallback ticker types

| Type | Examples | Risk |
|---|---|---|
| Banking / financial mergers (사라진 종목) | 우리은행, 신한, 우리종금 | Low — merged into parent (corp_code 이동) |
| Spin-off / restructure | HD현대미포, HD현대인프라코어, 코오롱모빌리티그룹 | Medium — new corp_code 발급 가능 |
| Special share class (우선주) | CJ4우(전환), 아모레퍼시픽홀딩스3우C | Low — base 종목 corp_code 따로 |
| Fund / specialty vehicle | 하나니켈1호, 하나니켈2호, 한국ANKOR유전, 베트남개발1, 코리아오토글라스 | Medium — special vehicle, DART corp 등록 안 됨 |
| Mergers (사라진 종목 후 새 상장) | 쌍용C&E (= 한일시멘트 흡수), 한국제지 (= 한솔제지 통합), 오렌지라이프 (신한지주 흡수), 하이트홀딩스 등 | Low-Medium — old ticker terminated |
| Renamed entities | KH 필룩스, 비케이탑스, 청호ICT, 폴루스바이오팜, 락앤락 | Medium — rename 후 corp_code 그대로일 수 있으나 매핑 안 됨 |

### Fallback stability test

**Test 1**: Fallback ticker 가 ticker reuse 에 견디는가?
- 50 fallback 중 0 = KRX master 에서 multi-ticker 또는 reuse 발견
- 단 ID = `KRX_TICKER_<ticker>` 는 ticker rotation 후 같은 ID 가 다른 entity 를 가리킬 위험 있음

**Test 2**: Fallback ticker 가 relisting 에 견디는가?
- 일부 fallback (예: 우리은행, 오렌지라이프, 쌍용C&E) = 흡수 / 통합으로 terminated
- relisting 가능성 낮음 (= 새 ticker / 새 corp_code 발급)

**Test 3**: Fallback 의 first/last snapshot 정합성
- 모두 `krx_first_snapshot ≤ krx_last_snapshot` ✅
- 일부 (한국유리, 대덕GDS, 성지건설) = first = last (single snapshot 출현)

## Limitations

| Limitation | Impact |
|---|---|
| Fallback ID 가 corp_code 가 아닌 단순 ticker 기반 | Ticker rotation / 재배정 시 ID stability 위험 |
| 합병으로 사라진 entity 의 corp_code 별도 추가 매핑 X | Lineage trace 불완전 |
| 우선주 / 특수증권 = base entity 와 ID 별도 | base 와의 grouping logic 필요 |

## 815 vs 833 Universe Count Difference (Referee 명시)

| Universe | Count |
|---|---:|
| Panel 2018-2024 only | 815 unique tickers |
| Panel 2018-2024 + 2025-2026 (union) | **833** unique tickers |
| Difference | 18 |

설명:
- 2025-2026 panel 에 새 등장 ticker = 18
  - 2025년 신규 상장 또는 2025년에 처음 top100 진입한 종목
- 815 → 833 = 2025-2026 panel 추가로 18 ticker 추가
- 833 모두 permanent_id_master 에 mapping

## Verdict (Allowed)

**PARTIAL PASS**.

Reason:
- 100% coverage achieved (833/833)
- DART 94% strong base
- Fallback 50 = ticker-based temporary ID (Referee 명시: full pass 불허)
- Ticker rotation / merge / rename 의 source-aware mapping 필요 (W001 v2.1 또는 별도 enhancement)

## Defect Closure Status

| Defect | Round 3 → Round 4 |
|---|---|
| ID_000001 uniqueness | already CLOSED |
| ID_000002 disappeared terminal | **PARTIAL** (S3 53% cross-ref + S4 100% cover; 121/258 = merger/rename 별도 source 필요) |
| ID_000003 code reuse | **CLOSED** (DART 내 0 reuse + KRX master cross-ref) |
| ID_000004 name change | **CLOSED** (152 ticker name change 모두 추적 가능) |
| ID_000005 permanent ID source missing | **PARTIAL** (94% DART + 6% fallback, fallback stability = ticker-based caveat) |
| ID_000006 within-DART linkage | already CLOSED |
| ID_000007 top100 lifecycle | already CLOSED |

## Related

- `data/processed/w001_v2/permanent_id_master.csv`
- `data/acquired/round4/s4_listed_companies/krx_ever_listed_table.csv`
- `reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/audit_summary.md`
