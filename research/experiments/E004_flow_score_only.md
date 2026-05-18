# E004 — Flow score 단독 (외국인 수급만으로 섹터 선택)

## 상태
계획됨

## 이게 무슨 ticket 인가

E003 baseline 확립 후 Layer 2 의 첫 변수 score 도입.

지피티 권장:
> 진단 먼저, 포트폴리오 나중

Flow score 가 정말 섹터 forward return 을 예측하는지 먼저 봐야 함
(rank IC, top-bottom spread). 그 다음 portfolio.

## 변수 정의 (사전 등록)

### Sector Flow Score

지피티 권장 두 정규화:

```
flow_by_value_20d = sum(섹터 외국인 순매수 금액, 최근 20 거래일) /
                     sum(섹터 거래대금, 최근 20 거래일)

flow_by_mcap_60d = sum(섹터 외국인 순매수 금액, 최근 60 거래일) /
                    섹터 유동시총 (없으면 일반 시총)
```

cross-sectional z-score 적용:

```
Flow Score = zscore_cross_section(
    평균(flow_by_value_20d, flow_by_mcap_60d)
)
```

cross-sectional z-score = 각 리밸런싱 시점에 12 sector 끼리 비교.

### 매수 후보

- D013 ON 분기: Flow Score 상위 K sector 선택
- K = 3 (지피티 1차 권장)
- 각 sector 의 종목 분배: E003-B 같은 규칙 (sector 내 시총 top, count-matched)
- 5 종목 분배: Top 2 sectors = 3/2, Top 3 = 2/2/1, Top 4 = 2/1/1/1, Top 5 = 1씩
- E004 는 Top 3 으로 시작 → 2/2/1 분배

## 진단 단계 (포트폴리오 전)

Hard pass 전제: Flow Score 가 섹터 forward return 을 예측해야 함

### 진단 1: Sector Score vs forward return correlation
- 각 분기말 (리밸런싱 시점) 의 Flow Score
- 그 후 다음 분기 (3 개월) sector return
- 12 sector pooled correlation
- 분기별 Rank IC (Spearman)
- 평균 Rank IC, 표준편차, t-stat

### 진단 2: Top vs Bottom spread
- 분기별 Top 3 sector 의 평균 forward return
- 분기별 Bottom 3 sector 의 평균 forward return
- Spread (Top - Bottom)
- 평균 spread, 표준편차, t-stat

### 진단 3: 시기별 안정성
- 2010-2017 / 2018-2026 subperiod 별 Rank IC, spread
- spike year (2020, 2025, 2026) 의 영향

## 포트폴리오 단계

### 사전 등록 verdict
| 결과 | 판정 |
|---|---|
| Rank IC 평균 ≥ 0.05 AND Top-Bottom spread t-stat ≥ 2 | 진단 통과 → 포트폴리오 backtest 진행 |
| Rank IC 평균 0~0.05 OR spread t-stat 1~2 | weak, 그래도 backtest |
| Rank IC 평균 < 0 또는 spread t-stat < 0 | Flow Score 가 noise → portfolio backtest skip, finding 만 |

### 포트폴리오 backtest
- D013 ON 분기에 Flow Score Top 3 sector
- 각 sector 의 시총 top 1-2 종목 (allocation 2/2/1)
- 총 5 종목
- 비용 동일 (1.5/20/5 bps)

### Portfolio verdict
- 누적 수익 / 샤프 / 최대 손실폭 vs E003-A (D013 +254% / 0.53)
- Sharpe ≥ 0.40 AND 누적 ≥ +150% → 가능성 있음
- Sharpe < 0.30 → Flow 단독 부족, 다음 변수 (RS, Breadth) 추가 필요

## 산출물

- reports/experiments/E004_flow_score_only/
  - diagnostics_rank_ic.csv (분기별 + 통합)
  - diagnostics_top_bottom_spread.csv
  - subperiod_diagnostics.csv
  - portfolio/ (D013 ON + Flow Top 3 결과)
    - metrics.json, trades.csv, signals.csv, equity_curve.csv, etc
  - sector_selection_log.csv (어떤 sector 선택했는지 분기별)
  - comparison_with_e003.csv
  - report.md

## 구현

### 새 코드
- src/features/sector_flow_score.py (NEW) — Flow Score 계산
- src/strategies/e004_flow_only.py (NEW) — D013 macro gate + Flow Top 3 sector + count-matched 종목

### Config
- configs/backtests/e004.yaml

### 테스트
- tests/test_sector_flow_score.py — z-score 정확성, no-look-ahead

## 엄격 제약
- DO NOT modify src/backtest/engine.py
- DO NOT modify 기존 strategy 모듈 (D001-D015, E003)
- D001-D015, E003-A 결과 byte-identical 유지
- DO NOT modify research_input_data/
- DO NOT use future data (Flow score 의 lookback 은 분기말 시점에서 과거만)
- thin sector (n_stocks ≤2) 는 Flow score 계산에서 제외 (z-score 안정성)

## 완료 기준
- pytest 통과
- 진단 단계 결과 (Rank IC, spread)
- 포트폴리오 결과 (verdict 에 따라 실행 또는 skip)
- 한국어 보고

## 결과 요약
codex 결과 받은 후 작성.

## Claude 검토
결과 확인 후 작성.
