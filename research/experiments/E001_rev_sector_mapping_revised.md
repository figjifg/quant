# E001-rev — 섹터 매핑 인프라 (지피티 권장 기준으로 수정)

## 상태
계획됨

## 이게 무슨 ticket 인가

E001 의 사전 등록 검증 기준 (b)(c) 가 한국 시장 현실에 mathematical
으로 불가능한 가정이었음을 발견. 또한 KOGI(지배구조지수) 매핑 오류
발견. 정직하게 정정.

**중요**: 이건 사후 결과 fitting 이 아니라:
- (b) 100 universe / 12 그룹 = 8.33 평균 → 평균 ≥10 은 mathematically 불가능
- (c) 한국 시장의 반도체 집중 (삼성+SK하이닉스) 이 KOSPI 30-50% → 40% dominance ≤40% 도 시장 구조상 불가능
- KOGI 는 산업 분류가 아니라 KRX 지배구조 지수 (ESG 성격) → 산업 매핑 source 로 쓰면 안 됨

수정 사유 모두 **데이터 구조 / 수학적 불가능성 / 매핑 오류** 이지
성과 (수익률) 보고 판단 아님. Layer 2 백테스트는 아직 안 했음.

## 원래 E001 결과 (정직하게 기록)

검증 4 기준:
- (a) 시총가중 coverage ≥99%: 평균 99.1% OK, 최저 95.6% FAIL
- (b) 각 12 그룹 평균 ≥10 종목: FAIL
- (c) 단일 그룹 시총가중 ≤40%: 최대 60% FAIL
- (d) "기타" ≤5%: 최대 4.4% PASS

원인:
- (a) FAIL: KOGI → 99 기타 매핑 실수. 카카오 (시총 큰 종목) 가 통째로 기타로 빠짐. 매핑 오류.
- (b) FAIL: 12 그룹 × 10 = 120 종목 필요, universe 100 종목. mathematical 불가능.
- (c) FAIL: 한국 시장 반도체/IT 집중 구조 (삼성+SK하이닉스 ~30-50%). 시장 구조 문제.

## 새 검증 기준 (지피티 권장, 사전 등록)

### Hard pass 기준 (모두 통과해야 PROCEED)

| 코드 | 기준 |
|---|---|
| (a1) | 시총가중 sector assignment coverage ≥99% (모든 리밸런싱 시점 minimum) |
| (a2) | 기타/unknown/legacy 시총가중 비중 ≤5% (모든 리밸런싱 시점 maximum) |
| (a3) | 비산업 KIS 코드 (KOGI 등) 는 산업분류로 직접 매핑 금지. KSIC fallback 또는 manual override 필수 |
| (a4) | Top-K 선택된 섹터는 allocation rule 충족 종목 수 보유 (예: Top 3 시 1위/2위 섹터 ≥2, 3위 ≥1) — Layer 2 실험 단계에서 검증 |

### Warning / diagnostic 기준 (보고는 하되 통과/실패 안 함)

| 코드 | 기준 |
|---|---|
| (b1) | 그룹별 종목 수 mean / median / min 보고 |
| (b2) | thin sector (종목 수 ≤2) warning + breadth score neutral 처리 |
| (b3) | 종목 수 ≥3 인 섹터에서만 breadth 신뢰 |
| (c1) | 단일 그룹 시총가중 >50% → warning |
| (c2) | 단일 그룹 시총가중 >70% → hard review / fail |
| (c3) | 섹터 내 single-name dominance (top1, top2 비중) 보고 |

### Report-only 기준

- 12 그룹별 시총 비중 추이
- 12 그룹별 종목 수 추이
- 기타/unknown 종목 리스트
- KSIC fallback 사용 종목 리스트
- manual override 종목 리스트
- 비산업 KIS 코드 처리 로그

## 매핑 우선순위 (지피티 권장, 사전 등록)

```
1. manual_override
   - 카카오, NAVER 등 high-impact 예외 종목 (필요 시 yaml 명시)
2. KIS 산업 중분류
   - 산업 중분류로 확인된 코드만 사용
3. KSIC fallback
   - KIS 중분류가 비산업 (테마/지수/ESG) 또는 없을 때
4. unknown / legacy
   - 모두 실패시 (보고 + universe 표시)
```

## 비산업 KIS 코드 list (사전 등록, 산업 매핑 금지)

`configs/sector_mapping.yaml` 에 명시:

```yaml
non_industry_kis_codes:
  - 'KOGI(지배구조지수)'   # KRX 지배구조 지수 (ESG)
  # 향후 발견되는 비산업 코드 추가
```

이들은 산업 매핑 직접 사용 금지 → KSIC fallback 또는 manual override
필수.

## 12 그룹 (E001 와 동일, 변경 없음)

```yaml
sector_groups:
  - code: '01', name: 반도체/IT하드웨어
  - code: '02', name: 자동차/운송장비
  - code: '03', name: 2차전지/화학/소재
  - code: '04', name: 철강금속
  - code: '05', name: 조선/기계/산업재
  - code: '06', name: 금융
  - code: '07', name: 헬스케어
  - code: '08', name: 인터넷/게임/SW
  - code: '09', name: 소비재/유통
  - code: '10', name: 음식료
  - code: '11', name: 에너지/유틸리티
  - code: '12', name: 건설/부동산
  - code: '99', name: 기타
```

## 구현 작업

### 1단계: yaml 수정
- `configs/sector_mapping.yaml` 업데이트:
  - `kis_mcls_to_group` 에서 'KOGI(지배구조지수)' 제거 (산업 매핑 금지)
  - `non_industry_kis_codes` list 추가
  - 매핑 우선순위 명시
- `manual_override.csv` 또는 yaml 안 inline — 현재는 비어 있음, KOGI 케이스가 KSIC fallback 으로 자동 해결되면 manual override 불필요

### 2단계: sector_mapping_loader.py 업데이트
- 비산업 코드 처리 로직 추가
- 매핑 우선순위 적용 (manual → KIS 중분류 (비산업 제외) → KSIC → 기타)
- mapping_source 컬럼에 'manual_override' / 'kis_mcls' / 'ksic_fallback' / 'other' 명시

### 3단계: 재실행
- `data/processed/stock_sector_mapping_20260518.csv` 재생성
- 종목별 final_sector 변경 사항 보고 (KOGI 종목들이 어떻게 변경됐는지)

### 4단계: 새 기준으로 검증
- (a1) coverage 측정 + report
- (a2) 기타 비중 측정 + report
- (a3) 비산업 코드 처리 검증
- (a4) 종목 수 분포 (선택 가능성 진단)
- (b1-3) 그룹 count diagnostic
- (c1-3) dominance diagnostic
- 모두 통과/실패 명시

### 5단계: 산출물
- `reports/experiments/E001_rev_sector_mapping_revised/report.md`
- `reports/experiments/E001_rev_sector_mapping_revised/coverage_after_mapping.csv`
- `reports/experiments/E001_rev_sector_mapping_revised/group_distribution.csv`
- `reports/experiments/E001_rev_sector_mapping_revised/dominance_diagnostic.csv`
- `reports/experiments/E001_rev_sector_mapping_revised/single_name_dominance.csv`
- `reports/experiments/E001_rev_sector_mapping_revised/manual_review_log.md`
- `reports/experiments/E001_rev_sector_mapping_revised/non_industry_code_handling.md`

## 엄격 제약
- DO NOT modify src/backtest/engine.py
- DO NOT modify 기존 strategy 모듈 / D013 / research_input_data/
- KIS snapshot 자체 재호출 X (E000 결과 그대로 사용)
- 결과 보기 전 yaml freeze
- 매핑 변경은 추가/수정만, 12 그룹 정의 자체는 변경 금지 (E001 그대로)

## 완료 기준
- yaml 수정
- 종목별 final mapping 재생성
- 새 검증 기준 4 가지 (a1-a4) hard pass
- diagnostic 기준 (b1-b3, c1-c3) 보고
- 최종 한국어 보고

## 범위 외
- ❌ Layer 2 백테스트 (E003 부터)
- ❌ 변수 score 계산 (E004 부터)
- ❌ 12 그룹 정의 변경
- ❌ KIS snapshot 재호출

## 결과 요약
codex 결과 받은 후 작성.

## Claude 검토
결과 확인 후 작성.
