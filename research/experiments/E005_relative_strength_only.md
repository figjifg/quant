# E005 — Relative Strength score 단독

## 상태
계획됨

## 이게 무슨 ticket 인가

E004 (Flow 단독) FAIL — 외국인 수급 lagging. E005 = 가격 기반 RS
score 단독. 모멘텀이 sector forward return 예측력 있는지 확인.

지피티 권장: "외국인 수급 없이 가격 상대강도만으로 섹터 선택력이
있는가?"

## 변수 정의 (사전 등록)

### Sector RS Score

```
sector_rel_ret_20d = sector_cap_weighted_return_20d (sum of daily) -
                     kospi_cap_weighted_return_20d

sector_rel_ret_60d = sector_cap_weighted_return_60d -
                     kospi_cap_weighted_return_60d

RS Score = zscore_cross_section(
    평균(sector_rel_ret_20d, sector_rel_ret_60d)
)
```

KOSPI cap-weighted return: research_input_data/inputs/macro_features/
krx_market_breadth_kospi_2010_2026.csv 의 cap_weighted_return 사용.

thin sector 제외 (cross-sectional z-score 안정성).

## 진단 (E004 와 동일 구조)

### Rank IC, Top-Bottom spread, subperiod, spike year

진단 기준 (사전 등록):
- Rank IC 평균 ≥ 0.05 AND spread t-stat ≥ 2 → 통과

## 포트폴리오 (진단 통과 시)

- D013 macro gate ON 분기에 RS Top 3 sector 선택
- 분배: 2/2/1 (E004 와 동일)
- 비용 1.5/20/5 bps

## 산출물

- reports/experiments/E005_relative_strength_only/
- diagnostics_rank_ic.csv
- diagnostics_top_bottom_spread.csv
- subperiod_diagnostics.csv
- portfolio/ (진단 통과 시)
- sector_selection_log.csv
- comparison_with_e003_e004.csv
- report.md

## 엄격 제약
- DO NOT modify engine, 기존 strategy
- D001-D015, E003, E004 byte-identical
- 새 코드: src/features/sector_rs_score.py, src/strategies/e005_rs_only.py
- look-ahead 방지

## 결과 요약
codex 결과 받은 후 작성.

## Claude 검토
결과 확인 후 작성.
