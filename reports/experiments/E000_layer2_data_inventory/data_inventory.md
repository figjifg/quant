# E000 Layer 2 Data Inventory

작성일: 2026-05-18

## 결론

판정: **STOP**

사유: `research_input_data/` 안에 종목별 일별 외국인/기관 매매 데이터는 panel 파일에 있으나, Layer 2 섹터 선택에 필요한 종목별 섹터 분류 데이터가 없다. panel 컬럼, 별도 파일명, 문서, CSV 헤더 검색에서 KRX 업종/WICS/GICS/자체 섹터 매핑 또는 과거 섹터 변경 이력을 확인하지 못했다.

## 1. 전체 구조와 파일

전체 파일 카탈로그는 `file_catalog.csv`에 기록했다. 카탈로그에는 모든 파일의 상대경로, 디렉터리, 확장자, 크기, 가능할 경우 컬럼, 행 수, 날짜 범위, 종목 수를 포함했다.

디렉터리 구조:

```text
research_input_data/
  .env
  README.md
  docs/
    DATA_CATALOG.md
    DATA_SOURCES.md
  inputs/
    equity_panels/
      dynamic_top100_2017_2024_panel.csv
      dynamic_top100_2018_2024_panel.csv
      dynamic_top100_2025_2026_krx_panel.csv
      kiwoom_dynamic_top100_2010_2016_panel.csv
    events/
      opendart_kospi_disclosures_20180101_20260505.parquet
    futures/
      kospi200_night_futures_front_features_2010_2017.csv
      kospi200_night_futures_front_features_manual_2018_2026.csv
      kospi200_regular_futures_features_2010_2017.csv
      kospi200_regular_futures_features_2018_2026.csv
      kospi200_regular_futures_manual_source_2018_2026.csv
      global_index_futures/
        nasdaq100_futures_nq_1min_20180101_20260510/
        nikkei225_yen_futures_niy_1min_20180101_20260510/
        russell2000_futures_rty_and_nikkei225_usd_futures_nkd_1min_20180101_20260510/
    macro_features/
      fred_*.csv
      krx_market_breadth_kospi_2010_2026.csv
      sp500_emini_futures_1530_1800_kst_2018_2026.csv
    market_flow/
      kiwoom_market_flow_2010_2017_krx_trading_days.csv
      kiwoom_market_flow_2018_2026_integrated.csv
      kiwoom_market_flow_2025_2026_krx.csv
  오픈API 활용자가이드_금융위원회_주식대차정보.docx
  한국투자증권_오픈API_전체문서_20260511_030000.xlsx
```

Windows `:Zone.Identifier` sidecar 파일도 존재하며 `file_catalog.csv`에 포함했다. `.env`는 존재만 기록했고 내용은 확인하지 않았다.

## 2. Panel 파일 컬럼 확인

| 파일 | 기간 | 행 수 | 종목 수 | 섹터 컬럼 | 외국인/기관 매매 컬럼 |
|---|---:|---:|---:|---|---|
| `inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv` | 2010-01-04..2016-12-29 | 1,093,386 | 713 | 없음 | 있음 |
| `inputs/equity_panels/dynamic_top100_2017_2024_panel.csv` | 2017-01-02..2024-12-30 | 1,087,741 | 840 | 없음 | 있음 |
| `inputs/equity_panels/dynamic_top100_2018_2024_panel.csv` | 2018-01-02..2024-12-30 | 969,208 | 815 | 없음 | 있음 |
| `inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv` | 2025-01-02..2026-05-06 | 172,543 | 538 | 없음 | 있음 |

Panel 공통 컬럼:

- 가격/거래: `날짜`, `종목코드`, `종목명`, `시가`, `고가`, `저가`, `종가`, `거래량`, `Change`
- 투자자 수급: `기관순매매량`, `외국인순매매량`, `기관순매수금액추정`, `외국인순매수금액추정`
- 규모/유동성: `거래대금추정`, `시가총액추정`, `상장주식수`
- 품질/멤버십: `수급금액추정여부`, `거래대금추정여부`, `시가총액추정여부`, `동적유니버스포함`

추가 컬럼:

- `kiwoom_dynamic_top100_2010_2016_panel.csv`: `통합거래량반영여부`, `통합종가반영여부`, `통합종가제외여부`, `가격범위후보정여부`, `KRX종가`
- `dynamic_top100_2025_2026_krx_panel.csv`: 위 통합/KRX 컬럼과 `키움거래대금순위`

확인 결과 `업종`, `섹터`, `sector`, `WICS`, `GICS`, `industry`, `분류` 계열 컬럼은 panel 및 다른 CSV 헤더에서 발견되지 않았다.

## 3. Macro 외 디렉터리의 종목별 외국인 매매 데이터

종목별 일별 외국인/기관 매매 데이터는 `inputs/equity_panels/` 안의 4개 panel 파일에 있다. `macro_features/` 외 다른 디렉터리에서 확인한 외국인 관련 데이터는 다음과 같다.

| 디렉터리 | 파일 | 수준 | 외국인 데이터 |
|---|---|---|---|
| `inputs/equity_panels/` | 4개 dynamic top100 panel | 종목별 일별 | `외국인순매매량`, `외국인순매수금액추정` |
| `inputs/market_flow/` | 3개 market flow CSV | 시장/대형주 aggregate | `kospi_foreign_net`, `large_foreign_net` |
| `inputs/futures/` | KOSPI200 futures CSV | 선물 aggregate | `foreign_*`, `institution_*`, `individual_*`, `corporation_*` |

Layer 2의 종목별 섹터 aggregate에 직접 쓸 수 있는 것은 `inputs/equity_panels/`뿐이다. `market_flow`는 시장/대형주 단위이고, `futures`는 파생상품 투자자 수급이므로 종목별 주식 수급이 아니다.

Panel 내 수급 컬럼 상태:

| 파일 | 외국인 수량 | 외국인 금액 | 기관 수량 | 기관 금액 | 개인 구분 |
|---|---|---|---|---|---|
| `kiwoom_dynamic_top100_2010_2016_panel.csv` | 있음, 일부 결측 | 있음, 일부 결측 | 있음, 일부 결측 | 있음, 일부 결측 | 없음 |
| `dynamic_top100_2017_2024_panel.csv` | 있음 | 있음 | 있음 | 있음 | 없음 |
| `dynamic_top100_2018_2024_panel.csv` | 있음 | 있음 | 있음 | 있음 | 없음 |
| `dynamic_top100_2025_2026_krx_panel.csv` | 있음, 일부 결측 | 있음, 일부 결측 | 있음, 일부 결측 | 있음, 일부 결측 | 없음 |

결측:

- `2017_2024`, `2018_2024`: 외국인/기관 수량 및 금액 컬럼 전 행 nonblank.
- `2025_2026_krx`: 외국인/기관 수량 및 금액 171,315 / 172,543행 nonblank. 1,228행 결측.
- `2010_2016`: 외국인/기관 수량 및 금액 962,589 / 1,093,386행 nonblank. 130,797행 결측.

투자자 구분은 종목별 panel에서 외국인과 기관만 가능하다. 개인 순매매는 별도 컬럼으로 없다. 단순 잔차로 개인을 추정하려면 거래량/금액 정의와 기타 법인/프로그램/회원사 분해가 맞는지 별도 검증이 필요하므로 E000 기준에서는 보유로 보지 않는다.

## 4. 별도 섹터 매핑 파일 여부

별도 섹터 매핑 파일은 없다.

확인 범위:

- 파일명 검색: `sector`, `wics`, `gics`, `업종`, `industry`, `mapping`, `map` 후보 없음.
- CSV 헤더 검색: `업종`, `섹터`, `sector`, `WICS`, `GICS`, `industry`, `분류` 후보 없음.
- 문서 검색: `DATA_CATALOG.md`, `DATA_SOURCES.md`, `README.md`에 섹터 매핑 보유 항목 없음.
- `한국투자증권_오픈API_전체문서_20260511_030000.xlsx`는 API 문서 workbook이며 데이터 테이블이 아니다. sheet 목록에는 업종 관련 API 명세가 있으나 종목별 섹터 매핑 데이터 파일은 아니다.

따라서 source는 KRX/WICS/GICS/자체 어느 것도 보유로 판정할 수 없다. 현재 분류도 없고, 과거 변경 이력도 없다.

## 5. 시점별 멤버십

처리 가능 범위:

- Dynamic Top100 멤버십: panel의 `동적유니버스포함`으로 날짜별 멤버십을 처리할 수 있다.
- `2010_2016`, `2017_2024`, `2018_2024`: 각 거래일마다 True 종목 수가 100개.
- `2025_2026_krx`: True 종목 수가 일별 98..100개.

처리 불가능 또는 불완전:

- 섹터별 point-in-time 멤버십: 섹터 매핑 자체가 없어 불가능.
- 상장/상폐 이력: 별도 listing/delisting 파일 없음. panel에 특정 종목이 나타나는 기간은 관찰 가능하지만, 전체 시장 상장/상폐 이벤트로 해석할 수 없다.
- 거래정지/관리종목: 명시 컬럼 없음. 거래량 0 또는 결측으로 일부 추정은 가능하나 확정 정보가 아니다.
- 전체 KOSPI/KOSDAQ universe 멤버십: dynamic top100 panel에 들어온 종목만 볼 수 있다.

## 6. 섹터 Aggregate 가능성

현재 파일만으로 가능한 것:

- 종목별 수익률, 거래대금, 시가총액, 외국인/기관 순매매량/순매수금액은 panel 범위 내에서 계산 가능.
- Dynamic Top100 안에서 날짜별 구성 종목은 `동적유니버스포함`으로 제한 가능.

현재 파일만으로 불가능한 것:

- 섹터별 수익률
- 섹터별 거래대금 합산
- 섹터별 시가총액 합산
- 섹터별 외국인 순매수 합산
- 섹터 내 종목 수 산출

이유는 모든 섹터 aggregate의 group key인 종목별 섹터 분류가 없기 때문이다.

## 7. 최종 답변 요약

### A. 섹터 분류 데이터

**없음.** KRX/WICS/GICS/자체 분류 모두 확인되지 않았다. 현재 분류도 없고 과거 변경 이력도 없다.

### B. 종목별 일별 외국인 매매

**부분 보유.** `inputs/equity_panels/`의 panel 파일에 종목별 일별 `외국인순매매량`, `외국인순매수금액추정`, `기관순매매량`, `기관순매수금액추정`이 있다. 금액과 수량 둘 다 있다. 투자자 구분은 외국인/기관만 가능하고, 개인은 종목별 컬럼이 없다.

### C. 시점별 멤버십

**부분 처리 가능.** Dynamic Top100 날짜별 멤버십은 `동적유니버스포함`으로 가능하다. 상장/상폐/거래정지/관리종목 정보와 섹터 변경 이력은 없다.

### D. 섹터 Aggregate 만들기

**현재는 불가능.** 종목별 섹터 매핑이 필요하다. 추가 데이터로 최소한 `date`, `종목코드`, `sector_source`, `sector_code`, `sector_name`, `valid_from`, `valid_to` 형태의 매핑이 필요하다. point-in-time 이력이 없으면 현재 분류 기준 prototype은 가능하지만 classification/survivorship bias를 명시해야 한다.

## 다음 단계

E001로 진행하기 전에 섹터 매핑 데이터가 필요하다. 외부 다운로드 또는 수동 수집 후보와 alternative는 `data_gaps.md`에 정리했다.
