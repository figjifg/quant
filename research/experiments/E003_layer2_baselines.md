# E003 — Layer 2 baseline 3개 (D013 재현 + count-matched + pure basket)

## 상태
계획됨

## 이게 무슨 ticket 인가

지피티 권장 두 트랙 분리의 첫 단계. Layer 2 의 실제 변수 점수
(E004~E007) 를 도입하기 전 3 가지 baseline 을 정의 + 실행 + 비교.

이 셋의 비교로 알 수 있는 것:
- "섹터 분산 자체" 의 효과 (단순 분산 vs 알파)
- "5 종목 한계" vs "섹터 바스켓 한계"
- D013 의 자연 sector 분포가 이미 분산되어 있다는 finding 정량화

## 3 baseline 정의 (사전 등록)

### E003-A: D013 control 재현

D013 그대로. E002 의 새 데이터 인프라 위에서 byte-identical 결과
나오는지 sanity check.

- 변수, 임계값, 윈도우, 종목 선택 (시총 top 5), 비용, 리밸런싱 모두 D013 동일
- 기대: 누적 +254.58%, 샤프 0.5334 (D013 와 정확 일치)
- 다르면 데이터 변경이 D013 에 영향 끼침 → 버그 (E002 검증 단계로 회귀 필요)

### E003-B: Count-matched sector-diversified

D013 의 macro gate 그대로, 단 종목 선택 규칙 변경:
- D013 ON 분기에 universe 의 시총 순위 부여
- **각 sector 에서 최대 1 종목만 선택** (sector 분산 cap)
- 시총 큰 순서로 sector 1 개씩 채워 5 종목 도달
- 예: 1위 삼성전자 (01 반도체), 2위 SK하이닉스 (01 반도체 — skip), 다음 3위 LG에너지솔루션 (03 화학/소재), 4위 현대차 (02 자동차), 5위 카카오 (08 인터넷) 등
- 5 sector 분산 5 종목 portfolio (D013 와 같은 종목 수)

목적: "같은 종목 수 한계에서 단순 sector 분산이 D013 보다 나은가?"

기대 비교: D013 가 이미 자연 분산 (E002 d013_sector_distribution.csv 확인) 이라 큰 차이 없을 수 있음. 그러면 finding 자체.

### E003-C: Pure sector basket

D013 의 macro gate 그대로, 종목 선택 완전히 다름:
- D013 ON 분기에 universe 의 모든 매핑된 종목 (sector 99 제외)
- 각 sector 12 그룹 (실제로 종목 있는 그룹만, thin sector 제외 ≥3 종목)
- **각 sector equal-weight** (= 1/n_present_sectors)
- 각 sector 내 종목 = sector cap-weight

목적: "섹터 바스켓 방식 자체" 의 알파/리스크 profile

기대 비교: 종목 수 많음 (분기 80+ 종목) → 분산 효과 큼. D013 보다 낮은 변동성 예상.

## 사전 등록 hypothesis

### H1: E003-A 가 D013 정확 재현
- Sharpe 0.5334
- 누적 +254.58%
- 다르면 buf

### H7: 3 baseline 비교
- E003-A vs E003-B: 누적 수익률, 샤프, 최대 손실폭, 양의 수익 연도
- E003-A vs E003-C: 같은 항목
- E003-B vs E003-C: 종목 수 한계 (5 vs 80+) 효과 분리

### H8: D013 의 자연 분산 확인
- E003-A 와 E003-B 의 매수 분기 별 sector 분포 비교
- D013 의 시총 top 5 가 이미 5+ sector 에 자연 분산 → E003-B 와 큰 차이 없을 가능성

## 산출물

각 baseline:
- reports/experiments/E003_layer2_baselines/A_d013_replication/
- reports/experiments/E003_layer2_baselines/B_count_matched/
- reports/experiments/E003_layer2_baselines/C_pure_basket/
- 각각 metrics.json, trades.csv, signals.csv, equity_curve.csv, quarterly_year_breakdown.csv, subperiod_breakdown.csv, sector_holdings.csv (어떤 sector 의 종목 보유했는지)

종합:
- reports/experiments/E003_layer2_baselines/comparison_summary.csv (A/B/C 의 metrics 한 표)
- reports/experiments/E003_layer2_baselines/sector_holding_overlap.csv (A vs B vs C 의 종목/섹터 overlap)
- reports/experiments/E003_layer2_baselines/report.md (정리)

## 구현 작업

### 새 strategy
- src/strategies/e003_a_d013_replication.py (E003-A) — D013 strategy 그대로
- src/strategies/e003_b_count_matched.py (E003-B) — D013 macro gate + sector 분산 종목 선택
- src/strategies/e003_c_pure_basket.py (E003-C) — D013 macro gate + sector basket

### Config
- configs/backtests/e003.yaml (3 variants)

### Dispatcher
- src/run_experiment.py 의 E003 처리

### 테스트
- tests/test_e003_strategy.py: 각 baseline 의 sector 분배 로직 검증

## 엄격 제약
- DO NOT modify src/backtest/engine.py
- DO NOT modify 기존 strategy 모듈 / D013 / research_input_data/
- DO NOT modify D001-D015 결과 (byte-identical 유지)
- E003-A 가 D013 정확 재현 (sanity)
- 새 sector aggregate 데이터 (E002) 사용
- pytest 통과

## 완료 기준
- 3 baseline 모두 실행 완료
- comparison_summary.csv 생성
- E003-A 가 D013 결과 정확 일치
- 한국어 보고

## 결과 요약
codex 결과 받은 후 작성.

## Claude 검토
결과 확인 후 작성.
