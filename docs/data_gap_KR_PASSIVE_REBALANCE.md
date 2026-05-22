# Data Gap — KR-PASSIVE-REBALANCE-001 A형

Card status: BACKLOG (Referee Step 5 lock, 2026-05-22)
Block reason: A0 Item 1 (Data lineage) = FAIL — no index event calendar in repo
Unblock task: Backlog A0 Queue Task Q1 (`docs/backlog_A0_queue.md`)

## Spec Requirement vs Available

Pre-registered spec (`research/experiments/KR_PASSIVE_REBALANCE_001_A_test.md`)
의 fixed scope: "공식 발표 후 편입 확정 종목만 (Universe)"

이 universe 정의 자체가 데이터 부재로 구성 불가.

## Missing Fields (모두 필요)

| Field | 의미 | 현재 repo |
|---|---|---|
| `announcement_date` | 지수 운영기관 공식 편입/편출 발표일 | 없음 |
| `index_id` | 지수 identifier (KOSPI200 / KOSPI100 / KOSDAQ150 / KRX100 등) | 없음 |
| `inclusion_list` | 발표문 명시 편입 확정 종목 list | 없음 |
| `exclusion_list` | 발표문 명시 편출 확정 종목 list | 없음 |
| `effective_date` | 실제 리밸런싱 적용일 | 없음 |
| `methodology_version` | 발표 시점 방법론 버전 (변경 시 audit) | 없음 |
| `source_lineage` | 데이터 acquired source / format / date | 없음 |
| `pit_lock_flag` | 사후 정정 / 재공시 반영 X 보장 | 없음 |
| `near_miss_list` | 편입 후보 중 미편입 종목 (control 용) | 없음 |

## Why Existing Repo Data Cannot Substitute

| Repo data | 왜 substitute 불가 |
|---|---|
| `opendart_kospi_disclosures_*.parquet` | 기업 공시 only. 지수 운영기관 발표는 KRX market data dept / FnGuide / 지수 제공사 별도 source. DART 안에 KOSPI200 / 코스피100 정기 변경 발표 없음. |
| `kospi200_*_futures_features_*.csv` | 선물 가격 / 거래량 features. 지수 구성 종목 변경 발표 데이터 아님. |
| `krx_market_breadth_*.csv` | 시장 광도 (advancing / declining). 지수 변경 발표 아님. |
| `global_etf/` | 글로벌 ETF 데이터. 한국 지수 운영기관 발표 아님. |
| `equity_panels/dynamic_top100_*.csv` | 시총 상위 100 동적 panel. 지수 편입 정보 X. PIT membership 도 별개 (= 단순 시총 ranking). |
| `data/processed/sector_membership_*` | 섹터 분류. 지수 편입 X. |

## Acceptable Source Requirements

Task Q1 완료를 위한 source 는 다음 요건 모두 만족:

1. **Official announcement provenance**: 지수 운영기관 (KRX / FnGuide /
   지수 제공사) 의 공식 발표 archive. 추정 / 재구성 X.
2. **PIT integrity**: 발표일 = capture 일치. 사후 정정 / 재공시 chronology
   별도 column 으로 보존.
3. **Complete chronology**: 정기 변경 + 비정기 변경 (수시 편입/편출) 모두
   포함. 한 종류만 = 부분 가용.
4. **Index coverage**: 최소 KOSPI200 (필수). 가능 시 KOSPI100 / KOSDAQ150
   / KRX100 도.
5. **Methodology stability log**: 방법론 변경 (free-float 계산 룰 등) 시점
   기록. 변경 전후 동일 시계열 사용 위험 명시.
6. **Near-miss universe** (선택 but 강력 추천): 발표 시점 편입 후보 list
   (rank 직전 candidates). Control 구성에 필수.

## Forbidden Substitutes (Referee 명시)

다음 어느 것도 substitute 로 사용 불가:

- DART 만 사용 (기업 공시 only)
- ETF AUM 변화 추정 (사후 = look-ahead)
- Fund 보유 변화 추정 (사후 = look-ahead)
- Futures basis change (지수 변경 발표 직접 source 아님)
- 사후 최종 index membership 으로 역추적 (post-hoc reconstruction)
- 단일 vendor 추정 데이터 without source lineage

위 substitute 시도 = 즉시 REJECT trigger (사이클 1 의 global REJECT 와
일치).

## Data Acquisition Effort Estimate (사용자 host 작업)

| Source | Cost | 시간 | 난이도 |
|---|---|---|---|
| KRX 시장정보시스템 (krx.co.kr) | 무료 / 일부 유료 | 1-3 일 (수작업 download + parsing) | 중 |
| 지수 제공사 직접 contact | 협상 | 1-4 주 | 높음 (라이센스) |
| Bloomberg / Refinitiv | 유료 (구독) | 1 일 (구독 시) | 낮음 단 비용 |
| FnGuide / FN데이터 | 유료 | 1 주 | 중 |
| 학술 / 공개 archive | 무료 | 1 일 (있을 시) | 낮음 단 coverage 제한 |

추정만. 사용자 자체 평가 필요.

## Post-Unblock Path

Task Q1 완료 → A0 audit 재실행 → 12 항목 PASS 시:
- `KR_PASSIVE_REBALANCE_001_A_test.md` spec 그대로 사용 (lock 됨)
- Bull/Bear/Referee 재심의 (data 변경 = 재심의 trigger)
- Codex 위임 backtest 진입 가능

Q1 완료 후에도 자동 진입 X. 사용자 명시 결정 + Referee 재 lock 필요.
