# E002 — 섹터 aggregate 생성

## 상태
계획됨

## 이게 무슨 ticket 인가

E001-rev 에서 종목별 sector mapping 확정. E002 = 그 mapping 을
panel 들과 join 해서 **섹터 단위 시계열 raw aggregate** 생성.

Layer 2 의 모든 변수 (Flow score, RS score, Breadth score) 가 이
raw aggregate 위에서 계산된다.

## 생성할 데이터

### 일별 섹터 aggregate (long format)

`data/processed/sector_aggregate_daily.csv`:

| 컬럼 | 설명 |
|---|---|
| date | 거래일 |
| sector_code | 12 그룹 코드 (01~12, 99) |
| sector_name | 12 그룹 이름 |
| n_stocks | 그 날 그 섹터의 universe 종목 수 (동적유니버스포함=True 기준) |
| sum_market_cap | 섹터 시총 합 |
| sum_traded_value | 섹터 거래대금 합 |
| sum_foreign_net_buy_amount | 섹터 외국인 순매수 금액 합 |
| sum_foreign_net_buy_shares | 섹터 외국인 순매매 수량 합 |
| sum_institution_net_buy_amount | 섹터 기관 순매수 금액 합 |
| sum_institution_net_buy_shares | 섹터 기관 순매매 수량 합 |
| cap_weighted_return | 그 날 섹터 시총가중 수익률 |
| top1_market_cap | 섹터 내 시총 top1 비중 (single-name dominance 진단) |
| top2_market_cap | 섹터 내 시총 top2 비중 |

### 종목별 일별 데이터 (E004+ 의 breadth 계산용)

`data/processed/stock_daily_with_sector.csv` (또는 panel 에 sector 컬럼만 추가):

| 컬럼 | 설명 |
|---|---|
| date | 거래일 |
| ticker | 종목코드 |
| sector_code | 12 그룹 코드 |
| foreign_net_buy_amount | 종목별 외국인 순매수 금액 |
| return | 종목 일별 수익률 |
| in_universe | 동적유니버스포함 여부 |

이건 panel 자체에 sector 컬럼 추가하는 게 깔끔할 수도.

## 데이터 소스

Panel 4 개:
- kiwoom_dynamic_top100_2010_2016_panel.csv
- dynamic_top100_2017_2024_panel.csv (2017-12-31 까지만 사용 — D013 config 와 동일)
- dynamic_top100_2018_2024_panel.csv
- dynamic_top100_2025_2026_krx_panel.csv

기존 macro/KOSPI:
- krx_market_breadth_kospi_2010_2026.csv (KOSPI cap_weighted_return — Layer 2 의 RS 계산 baseline)

Sector mapping:
- data/processed/stock_sector_mapping_20260518.csv

## 처리 단계

### 1. Panel 통합 + universe 필터
- 4 개 panel 합치기 (D013 config 의 panel_date_filters 동일 적용)
- 동적유니버스포함=True 만 사용 (그 시점 universe 만 sector aggregate 에 포함)
- 중복 날짜/종목 처리 (dedupe last)

### 2. Sector mapping join
- 종목코드 6자리 ↔ sector_mapping 의 ticker
- 매칭 안 되는 종목 명단 보고 (E001-rev 에서 cover 됐어야 함)

### 3. 일별 종목 sector 부착
- 결과: 일별 종목 row + sector_code

### 4. 일별 sector aggregate
- groupby(date, sector_code) → sum/mean/count
- top1, top2 종목 비중 = top market_cap 순위로

### 5. KOSPI baseline 결합
- krx_market_breadth_kospi_2010_2026.csv 의 cap_weighted_return = KOSPI 시총가중 수익률
- 섹터 RS 계산 시 baseline (E004 에서 사용, E002 에서는 raw 만)

### 6. 검증 (사전 등록)

Hard pass:
- 모든 분기말에 12 그룹 (또는 thin sector 제외 후 ≥8) 의 aggregate 값 존재
- D013 의 quarterly_year_breakdown.csv 와 비교: 같은 분기말의 portfolio 종목 5개의 sector 매핑이 reasonable
- cap_weighted_return 의 시계열이 KOSPI 와 high correlation (≥0.7)

Diagnostic:
- thin sector (≤2 종목) 분기 list
- sector breadth (≥3 종목 분기) 가능 비율
- single-name dominance (top1, top2 비중) 시계열

Report-only:
- 12 그룹별 시총 비중 시계열
- 12 그룹별 외국인 순매수 시계열
- 12 그룹별 거래대금 시계열

## 산출물

- `data/processed/sector_aggregate_daily.csv` — 일별 섹터 raw aggregate
- `data/processed/stock_with_sector_daily.csv` (또는 mapping lookup 만) — 종목별 sector 추가
- `reports/experiments/E002_sector_aggregate/aggregate_summary.csv` — 분기말 요약
- `reports/experiments/E002_sector_aggregate/validation_report.md` — 검증 결과
- `reports/experiments/E002_sector_aggregate/sanity_diagnostics.csv` — single-name dominance, breadth feasibility

## 엄격 제약
- DO NOT modify src/backtest/engine.py
- DO NOT modify 기존 strategy 모듈 / D013 / research_input_data/
- D001-D015 의 결과 파일 byte-identical 유지
- 새 코드: src/data/sector_aggregator.py 정도
- 결과 보기 전 검증 기준 freeze

## 완료 기준
- aggregate CSV 생성
- pytest 통과 (현재 312)
- 검증 hard pass 통과
- diagnostic 결과 report
- 최종 한국어 보고

## 범위 외
- ❌ Layer 2 변수 score 계산 (E004+)
- ❌ baseline 백테스트 (E003)
- ❌ Top-K 섹터 선택 로직
- ❌ KIS snapshot 재호출 또는 sector mapping 변경

## 결과 요약
codex 결과 받은 후 작성.

## Claude 검토
결과 확인 후 작성.
