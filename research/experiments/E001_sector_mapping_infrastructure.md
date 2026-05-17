# E001 — 섹터 매핑 인프라 (중분류 + KSIC hybrid → 12 그룹 freeze)

## 상태
계획됨

## 이게 무슨 ticket 인가

E000 결과:
- KIS 중분류 만 사용 시 coverage 76-87% (시총가중) — 부족
- KIS 중분류 + KSIC fallback 시 99-100% — 통과
- 두 source 를 우리 custom 12 그룹에 매핑 필요

E001 = 매핑 freeze + 종목별 final sector 결정 + coverage 검증.

## 12 그룹 (사전 등록, 결과 보기 전 freeze)

지피티 추천 + 한국 시장 실정 반영:

| 코드 | 그룹 | 포함 분야 |
|---|---|---|
| 01 | 반도체/IT하드웨어 | 반도체, 디스플레이, 전기전자 부품 |
| 02 | 자동차/운송장비 | 완성차, 부품 |
| 03 | 2차전지/화학/소재 | 배터리, 일반 화학, 종이/목재 (소재) |
| 04 | 철강금속 | 철강, 비철금속 |
| 05 | 조선/기계/산업재 | 조선, 기계, 방산, 일반 산업재 |
| 06 | 금융 | 은행, 증권, 보험 |
| 07 | 헬스케어 | 제약, 바이오, 의료기기 |
| 08 | 인터넷/게임/SW | 플랫폼, 게임, SW, IT 서비스 |
| 09 | 소비재/유통 | 화장품, 의류, 유통, 백화점 |
| 10 | 음식료 | 식품, 음료 |
| 11 | 에너지/유틸리티 | 정유, 전력, 가스 |
| 12 | 건설/부동산 | 건설, 건자재 |

기타/매핑 불가:
- KOGI (지배구조 지수) 같은 ETF 류 → "기타" 처리 (Layer 2 에서 제외)
- 매핑 불명확 종목 → manual 검토 후 12 그룹 중 하나에 배정 또는 "기타"

## 매핑 규칙 (사전 등록)

### 우선순위
1. KIS 중분류 (`idx_bztp_mcls_cd_name`) 우선 → 12 그룹 매핑
2. KIS 중분류 없으면 KSIC (`std_idst_clsf_cd_name`) → 12 그룹 매핑
3. 둘 다 없으면 "기타" (Layer 2 매수 후보 제외)

### KIS 중분류 → 12 그룹 (초안, codex 가 freeze)

| KIS 중분류 | 12 그룹 |
|---|---|
| 전기,전자 | 01 반도체/IT하드웨어 |
| 운수장비 | 02 자동차/운송장비 |
| 화학 | 03 2차전지/화학/소재 |
| 종이,목재 | 03 2차전지/화학/소재 |
| 비금속광물 | 03 2차전지/화학/소재 |
| 철강및금속 | 04 철강금속 |
| 기계 | 05 조선/기계/산업재 |
| 운수창고 | 05 조선/기계/산업재 |
| 금융업 | 06 금융 |
| 증권 | 06 금융 |
| 의약품 | 07 헬스케어 |
| 의료정밀 | 07 헬스케어 |
| 서비스업 | 08 인터넷/게임/SW |
| 유통업 | 09 소비재/유통 |
| 섬유,의복 | 09 소비재/유통 |
| 음식료품 | 10 음식료 |
| 전기가스업 | 11 에너지/유틸리티 |
| 건설업 | 12 건설/부동산 |
| 통신업 | 08 인터넷/게임/SW (또는 별도?) |
| KOGI(지배구조지수) | 기타 |

**검토 필요**:
- 의료정밀 가 헬스케어 (의료기기) 인지 반도체 검사장비 (IT) 인지 — codex 가 종목 명단 보고 판단
- 통신업 종목 수가 적으면 08 SW 와 합치고, 충분히 많으면 별도 그룹

### KSIC → 12 그룹 (codex 가 종목 분포 보고 매핑 후 freeze)

KSIC 코드는 한국표준산업분류 — 세분화됨. codex 가 다음 작업:
1. 우리 universe 에 나타난 KSIC 코드 전체 list 작성
2. 각 KSIC 코드 → 12 그룹 매핑안 제안
3. 매핑 검토 후 freeze

## 사전 등록 검증 기준

매핑 freeze 후 다음 확인:
1. **Coverage**: 종목 수 ≥ 99%, 시총가중 ≥ 99% (12 그룹 매핑된 비율)
2. **그룹별 종목 수 분포**: 각 그룹에 최소 10 종목 이상 (분기말 기준 평균)
3. **단일 그룹 dominance**: 한 그룹이 시총가중 > 40% 면 위험 — D013 의 시총 top 5 가 거의 그 그룹에 몰릴 수 있음
4. **그룹 간 종목 이동**: 한 종목이 multiple 매핑 source 에서 충돌 없는지 (중분류 vs KSIC 다른 그룹 나오면 우선순위 적용)
5. **"기타" 비중**: 시총가중 < 5% (그 이상이면 매핑 보강 필요)

## 산출물 (사전 등록)

- `configs/sector_mapping.yaml` (NEW, freeze) — 12 그룹 정의 + 중분류/KSIC 매핑 dict
- `data/processed/stock_sector_mapping_20260518.csv` (NEW) — 종목코드, 종목명, 중분류, KSIC, final_sector, mapping_source
- `reports/experiments/E001_sector_mapping_infrastructure/coverage_after_mapping.csv` — 분기말 별 coverage
- `reports/experiments/E001_sector_mapping_infrastructure/group_distribution.csv` — 그룹별 종목 수 + 시총 비중 시계열
- `reports/experiments/E001_sector_mapping_infrastructure/manual_review_log.md` — 매뉴얼 결정 사항 + 이유
- `reports/experiments/E001_sector_mapping_infrastructure/report.md` — 종합 보고

## 구현 작업

### 1단계: 분포 분석
- universe (KIS snapshot 923 종목) 의 KIS 중분류 분포
- universe 의 KSIC 분포 (코드별 종목 수)
- 각 분류의 대표 종목 명단 (codex 가 매핑 결정 보조)

### 2단계: 매핑 freeze
- KIS 중분류 → 12 그룹: 위 ticket 의 초안 검토 후 yaml 작성
- KSIC → 12 그룹: codex 가 KSIC 코드별 매핑안 제안, yaml 작성
- 매뉴얼 결정 사항 (예: 통신업 별도 그룹, 의료정밀 헬스케어) manual_review_log.md 에 기록

### 3단계: 종목별 최종 매핑
- 우선순위: 중분류 → KSIC → "기타"
- mapping_source 컬럼으로 어느 source 에서 왔는지 기록

### 4단계: 검증
- 위 5개 검증 기준 모두 측정
- 통과 / 부분통과 / 실패 판정
- 부분통과 시 manual 보강 작업

## 엄격 제약
- DO NOT modify src/backtest/engine.py
- DO NOT modify 기존 strategy 모듈 / D013 / research_input_data/
- 새 코드: src/data/sector_mapping_loader.py 정도만
- 새 데이터: data/processed/ 와 configs/sector_mapping.yaml
- 매핑 freeze 는 결과 보기 전 commit (사후 변경 금지)
- 매뉴얼 결정 사항은 모두 manual_review_log.md 에 명시

## 완료 기준
- 매핑 yaml + final mapping CSV 생성
- coverage 검증 통과 (시총가중 ≥ 99%)
- 그룹별 분포 sanity 통과
- 최종 한국어 보고

## 범위 외
- ❌ 섹터 aggregate 계산 (E002)
- ❌ 백테스트 실험 (E003 이후)
- ❌ Layer 2 의 변수 점수 (E004 이후)
- ❌ KIS snapshot 자체 재호출

## 결과 요약
codex 결과 받은 후 작성.

## Claude 검토
결과 확인 후 작성.
