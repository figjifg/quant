# E000 KIS Sector Snapshot Log

- run_timestamp_utc: 2026-05-17T16:29:41.567666+00:00
- snapshot_path: data/processed/sector_membership_kis_snapshot_20260518.csv
- coverage_path: reports/experiments/E000_layer2_data_inventory/kis_sector_coverage.csv
- missing_path: reports/experiments/E000_layer2_data_inventory/missing_sector_names.csv
- total_unique_tickers: 923
- kis_api_success_count: 923
- kis_api_fail_count: 0
- count_coverage_pct: 100.000000
- mcap_weighted_coverage_pct: nan
- verdict: PROCEED WITH BIAS FLAG

## Sector Field Sanity

- Recommended middle-class column: `idx_bztp_mcls_cd_name`
- Non-empty successful rows: 651 / 923

## Missing Top 10

| 종목코드 | 종목명 | appearing_panels | top100_appearance_count | best_mcap_rank | has_price_data | has_foreign_flow_data |
| --- | --- | --- | --- | --- | --- | --- |
| 000660 | SK하이닉스 | dynamic_top100_2017_2024_panel.csv;dynamic_top100_2018_2024_panel.csv;dynamic_top100_2025_2026_krx_panel.csv;kiwoom_dynamic_top100_2010_2016_panel.csv | 5743 | 1 | True | True |
| 005380 | 현대차 | dynamic_top100_2017_2024_panel.csv;dynamic_top100_2018_2024_panel.csv;dynamic_top100_2025_2026_krx_panel.csv;kiwoom_dynamic_top100_2010_2016_panel.csv | 5743 | 2 | True | True |
| 005490 | POSCO홀딩스 | dynamic_top100_2017_2024_panel.csv;dynamic_top100_2018_2024_panel.csv;dynamic_top100_2025_2026_krx_panel.csv;kiwoom_dynamic_top100_2010_2016_panel.csv | 5743 | 2 | True | True |
| 051910 | LG화학 | dynamic_top100_2017_2024_panel.csv;dynamic_top100_2018_2024_panel.csv;dynamic_top100_2025_2026_krx_panel.csv;kiwoom_dynamic_top100_2010_2016_panel.csv | 5743 | 3 | True | True |
| 105560 | KB금융 | dynamic_top100_2017_2024_panel.csv;dynamic_top100_2018_2024_panel.csv;dynamic_top100_2025_2026_krx_panel.csv;kiwoom_dynamic_top100_2010_2016_panel.csv | 5743 | 3 | True | True |
| 012330 | 현대모비스 | dynamic_top100_2017_2024_panel.csv;dynamic_top100_2018_2024_panel.csv;dynamic_top100_2025_2026_krx_panel.csv;kiwoom_dynamic_top100_2010_2016_panel.csv | 5741 | 3 | True | True |
| 066570 | LG전자 | dynamic_top100_2017_2024_panel.csv;dynamic_top100_2018_2024_panel.csv;dynamic_top100_2025_2026_krx_panel.csv;kiwoom_dynamic_top100_2010_2016_panel.csv | 5740 | 7 | True | True |
| 005930 | 삼성전자 | dynamic_top100_2017_2024_panel.csv;dynamic_top100_2018_2024_panel.csv;dynamic_top100_2025_2026_krx_panel.csv;kiwoom_dynamic_top100_2010_2016_panel.csv | 5737 | 1 | True | True |
| 055550 | 신한지주 | dynamic_top100_2017_2024_panel.csv;dynamic_top100_2018_2024_panel.csv;dynamic_top100_2025_2026_krx_panel.csv;kiwoom_dynamic_top100_2010_2016_panel.csv | 5736 | 4 | True | True |
| 006400 | 삼성SDI | dynamic_top100_2017_2024_panel.csv;dynamic_top100_2018_2024_panel.csv;dynamic_top100_2025_2026_krx_panel.csv;kiwoom_dynamic_top100_2010_2016_panel.csv | 5736 | 5 | True | True |

## KIS Middle-Class Distribution

| idx_bztp_mcls_cd_name | ticker_count |
| --- | --- |
| (blank) | 272 |
| KODI(배당지수) | 1 |
| KOGI(지배구조지수) | 4 |
| KOSPI 200(유통서비스업) | 1 |
| KOSPI 200(전기통신업) | 1 |
| KOSPI 50 | 2 |
| 건설업 | 30 |
| 금융업 | 44 |
| 기계 | 37 |
| 보험 | 1 |
| 비금속광물 | 23 |
| 서비스업 | 63 |
| 섬유,의복 | 33 |
| 운수장비 | 45 |
| 운수창고 | 20 |
| 유통업 | 45 |
| 음식료품 | 33 |
| 의료정밀 | 6 |
| 의약품 | 36 |
| 전기,전자 | 60 |
| 전기가스업 | 9 |
| 제조업 | 1 |
| 종이,목재 | 23 |
| 증권 | 6 |
| 철강및금속 | 41 |
| 통신업 | 3 |
| 화학 | 83 |
