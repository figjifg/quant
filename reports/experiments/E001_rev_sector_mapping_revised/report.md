# E001-rev sector mapping revised report

## 변경 사항
- `KOGI(지배구조지수)`를 `kis_mcls_mapping`에서 제거하고 `non_industry_kis_codes`에 등록했다.
- 매핑 우선순위는 manual override, KIS 산업 중분류(비산업 코드 제외), KSIC fallback, `99` 기타 순서다.
- `mapping_source` 값은 `manual_override`, `kis_mcls`, `ksic_fallback`, `other`만 사용한다.

## 카카오 매핑 변화
- 035720 카카오: 이전 `99` 기타 -> 새 `08` 인터넷/게임/SW.
- 새 mapping_source: `ksic_fallback`; KIS `KOGI(지배구조지수)`는 직접 산업 매핑에 쓰지 않고 KSIC `자료처리, 호스팅, 포털 및 기타 인터넷 정보매개서비스업`를 사용했다.

## Hard pass
| 기준 | 결과 | 값 |
|---|---|---|
| (a1) 시총가중 sector assignment coverage >= 99% | PASS | 평균 0.999895, 최저 0.993295 (2025Q4) |
| (a2) 기타/unknown/legacy 시총가중 비중 <= 5% | PASS | 최대 0.006705 (2025Q4) |
| (a3) 비산업 KIS 코드 직접 산업 매핑 금지 | PASS | 직접 kis_mcls 매핑 0건 |
| (a4) Top-K allocation rule | SKIP | Layer 2 실험 단계(E003+)에서 검증 |

## Diagnostic b1: 12 그룹별 종목 수
| final_sector_code | final_sector_name | mean_n_stocks | median_n_stocks | min_n_stocks |
| --- | --- | --- | --- | --- |
| 01 | 반도체/IT하드웨어 | 11.23 | 11.00 | 6 |
| 02 | 자동차/운송장비 | 8.29 | 8.00 | 5 |
| 03 | 2차전지/화학/소재 | 16.68 | 16.00 | 10 |
| 04 | 철강금속 | 4.06 | 4.00 | 1 |
| 05 | 조선/기계/산업재 | 9.82 | 9.00 | 5 |
| 06 | 금융 | 14.61 | 15.00 | 6 |
| 07 | 헬스케어 | 6.11 | 5.00 | 1 |
| 08 | 인터넷/게임/SW | 12.73 | 12.00 | 6 |
| 09 | 소비재/유통 | 8.02 | 8.50 | 2 |
| 10 | 음식료 | 3.53 | 3.50 | 1 |
| 11 | 에너지/유틸리티 | 1.52 | 1.00 | 1 |
| 12 | 건설/부동산 | 3.36 | 3.00 | 0 |

## Diagnostic b2-b3: thin sector / breadth
- thin sector(분기말 종목 수 <=2) 발생 행 수: 121.
- thin sector 발생 분기 수: 66.
- breadth 신뢰 가능 그룹 수(>=3 종목) 평균: 10.17, 최저: 8.
- 전체 thin sector 목록은 `thin_sector_list.csv`에 저장했다.

## Diagnostic c1-c3: dominance
- 단일 그룹 dominance 최대값: 0.600349 (2026Q2, 01 반도체/IT하드웨어).
- >50% warning 분기 수: 2.
- >70% hard fail 분기 수: 0.
- >50% warning 분기 list: 2026Q1, 2026Q2.
- >70% hard fail 분기 list: 없음.

### 섹터 내 single-name top1/top2 평균 비중
| final_sector_code | final_sector_name | avg_top1_weight | avg_top2_weight |
| --- | --- | --- | --- |
| 01 | 반도체/IT하드웨어 | 0.7120 | 0.8511 |
| 02 | 자동차/운송장비 | 0.3382 | 0.5829 |
| 03 | 2차전지/화학/소재 | 0.3068 | 0.4670 |
| 04 | 철강금속 | 0.6747 | 0.8857 |
| 05 | 조선/기계/산업재 | 0.2769 | 0.4832 |
| 06 | 금융 | 0.1760 | 0.3188 |
| 07 | 헬스케어 | 0.6813 | 0.8485 |
| 08 | 인터넷/게임/SW | 0.2274 | 0.4018 |
| 09 | 소비재/유통 | 0.5223 | 0.7077 |
| 10 | 음식료 | 0.6305 | 0.8427 |
| 11 | 에너지/유틸리티 | 0.9194 | 0.9982 |
| 12 | 건설/부동산 | 0.5670 | 0.8066 |

## Report-only files
- `group_distribution.csv`
- `coverage_after_mapping.csv`
- `dominance_diagnostic.csv`
- `single_name_dominance.csv`
- `ksic_fallback_log.csv`
- `non_industry_code_handling.md`
- `sector_count_diagnostic.csv`
- `thin_sector_list.csv`
- `breadth_diagnostic.csv`
- `single_name_dominance_summary.csv`

## 종합 판정
- PROCEED.
