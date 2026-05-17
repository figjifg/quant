# E000 follow-up: API sector options

작성일: 2026-05-18

범위:
- 한국투자증권 Open API workbook(`research_input_data/한국투자증권_오픈API_전체문서_20260511_030000.xlsx`)의 sheet 목록/키워드 검색/관련 sheet 구조 확인
- 저장소 내 Kiwoom/KIS credential 및 호출 코드 흔적 확인
- 외부 network/API 호출 없음
- `src/backtest/engine.py`, strategy 모듈, `research_input_data/` 수정 없음

## 요약 결론

추천은 KIS다.

KIS workbook에는 종목별 섹터/업종 매핑에 쓸 수 있는 `주식기본조회` endpoint가 명확히 있다. 응답에 `pdno`(상품번호/종목코드), `prdt_name`, `idx_bztp_lcls_cd`, `idx_bztp_mcls_cd`, `idx_bztp_scls_cd`, `std_idst_clsf_cd`, `std_idst_clsf_cd_name`가 포함된다. 즉 종목코드별 지수업종 대/중/소분류 코드와 표준산업분류 코드를 받을 수 있다.

다만 KIS `주식기본조회`는 request에 기준일자가 없다. 문서 기준으로는 point-in-time historical sector membership 조회가 아니라 현재 또는 조회 시점의 종목 기본정보 조회로 봐야 한다. 과거 섹터 변경 이력까지 필요하면 별도 source가 필요하다.

Kiwoom은 이 저장소 안에서 실제 REST 호출 코드나 endpoint 문서를 찾지 못했다. `research_input_data/.env`에는 `KIWOOM_APPKEY`, `KIWOOM_SECRETKEY`가 있고, 기존 panel/market-flow 파일은 Kiwoom REST로 만들어졌다는 문서 기록이 있다. 하지만 로컬 증거만으로는 Kiwoom이 종목별 업종 매핑 endpoint를 제공하는지 확인할 수 없다.

## KIS API 검토

### 관련 sheet 목록

KIS workbook에서 `sector`, `섹터`, `업종`, `industry`, `classification`, `분류` 키워드로 확인한 국내주식 관련 후보:

| Sheet | API ID | TR_ID | URL | 용도 |
| --- | --- | --- | --- | --- |
| `주식기본조회` | `v1_국내주식-067` | `CTPF1002R` | `/uapi/domestic-stock/v1/quotations/search-stock-info` | 종목별 기본정보. 종목코드별 업종/산업분류 매핑 후보 |
| `국내주식업종기간별시세(일_주_월_년)` | `v1_국내주식-021` | `FHKUP03500100` | `/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice` | 업종 지수 기간별 OHLC |
| `국내업종 구분별전체시세` | `v1_국내주식-066` | `FHPUP02140000` | `/uapi/domestic-stock/v1/quotations/inquire-index-category-price` | 업종 구분별 현재/전체 시세 및 업종 코드 목록성 응답 |
| `국내업종 현재지수` | `v1_국내주식-063` | `FHPUP02100000` | `/uapi/domestic-stock/v1/quotations/inquire-index-price` | 단일 업종 현재 지수 |
| `국내업종 일자별지수` | `v1_국내주식-065` | `FHPUP02120000` | `/uapi/domestic-stock/v1/quotations/inquire-index-daily-price` | 단일 업종 일자별 지수 |
| `종목별 투자자매매동향(일별)` | `종목별 투자자매매동향(일별)` | `FHPTJ04160001` | `/uapi/domestic-stock/v1/quotations/investor-trade-by-stock-daily` | 섹터는 아니지만 종목별 수급 보강 후보 |

### KIS: 종목별 업종 매핑 후보

Endpoint:
- API 명: `주식기본조회`
- TR_ID: `CTPF1002R`
- Method/domain: `GET https://openapi.koreainvestment.com:9443`
- URL: `/uapi/domestic-stock/v1/quotations/search-stock-info`
- 모의투자: 미지원

Request:

| 위치 | 필드 | 설명 |
| --- | --- | --- |
| Header | `authorization` | Bearer access token |
| Header | `appkey` / `appsecret` | KIS app credential |
| Header | `tr_id` | `CTPF1002R` |
| Header | `custtype` | `P` 또는 `B` |
| Query | `PRDT_TYPE_CD` | `300`: 주식/ETF/ETN/ELW |
| Query | `PDNO` | 종목번호 6자리 |

업종/분류 관련 response fields:

| 필드 | 한글명 | 용도 |
| --- | --- | --- |
| `pdno` | 상품번호 | 종목코드 매핑 key |
| `prdt_name` | 상품명 | 종목명 |
| `mket_id_cd` | 시장ID코드 | STK/KSQ/KNX 등 시장 구분 |
| `scty_grp_id_cd` | 증권그룹ID코드 | 주권/ETF/ETN 등 instrument filter |
| `idx_bztp_lcls_cd` | 지수업종대분류코드 | KIS/KRX 계열 업종 대분류 후보 |
| `idx_bztp_mcls_cd` | 지수업종중분류코드 | 업종 중분류 후보 |
| `idx_bztp_scls_cd` | 지수업종소분류코드 | 업종 소분류 후보 |
| `std_idst_clsf_cd` | 표준산업분류코드 | 산업분류 코드 |
| `std_idst_clsf_cd_name` | 표준산업분류코드명 | 산업분류명 |
| `idx_bztp_lcls_cd_name` | 지수업종대분류코드명 | 지수업종 대분류명 |

평가:
- 종목코드 + 업종 코드/명 매핑은 가능해 보인다.
- request에 `as_of_date` 또는 기준일자 파라미터가 없다.
- historical point-in-time 업종 이력 조회 가능성은 문서상 낮다. 이 endpoint로 받는 값은 다운로드 시점 기준 snapshot으로 취급해야 한다.
- `lstg_*_dt`, `*_lstg_abol_dt`, `lstg_abol_dt`, `tr_stop_yn`, `admn_item_yn`도 같이 받아서 상장/상폐/거래정지/관리종목 보조 필드로 쓸 수 있다.

### KIS: 업종 지수/업종 코드 후보

업종별 return proxy 자체는 KIS 업종 지수 endpoint로 받을 수 있다.

`국내업종 일자별지수`
- TR_ID: `FHPUP02120000`
- URL: `/uapi/domestic-stock/v1/quotations/inquire-index-daily-price`
- Query: `FID_COND_MRKT_DIV_CODE=U`, `FID_INPUT_ISCD=<업종코드>`
- 응답: `stck_bsop_date`, `bstp_nmix_prpr`, `bstp_nmix_oprc`, `bstp_nmix_hgpr`, `bstp_nmix_lwpr`, `acml_vol`, `acml_tr_pbmn`
- 문서상 한 번의 조회에 100건까지 확인 가능

`국내주식업종기간별시세(일_주_월_년)`
- TR_ID: `FHKUP03500100`
- URL: `/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice`
- Query: `FID_COND_MRKT_DIV_CODE=U`, `FID_INPUT_ISCD=<업종 상세코드>`, `FID_INPUT_DATE_1`, `FID_INPUT_DATE_2`, `FID_PERIOD_DIV_CODE=D/W/M/Y`
- 응답: `stck_bsop_date`, 업종 지수 OHLC, `acml_vol`, `acml_tr_pbmn`, `mod_yn`
- 문서상 한 번의 호출에 최대 50건까지 확인 가능

`국내업종 구분별전체시세`
- TR_ID: `FHPUP02140000`
- URL: `/uapi/domestic-stock/v1/quotations/inquire-index-category-price`
- Query: `FID_COND_MRKT_DIV_CODE=U`, `FID_INPUT_ISCD=0001/1001/2001/...`, `FID_COND_SCR_DIV_CODE=20214`, `FID_MRKT_CLS_CODE=K/Q/K2`, `FID_BLNG_CLS_CODE`
- 응답 배열에 `bstp_cls_code`, `hts_kor_isnm`, 업종 지수 현재가/등락/거래량/거래대금 등이 포함된다.
- 업종코드 목록을 bootstrap하는 데 쓸 수 있다.

### KIS: 일일 호출 제한

workbook 안에서 확인된 제한:
- access token은 일반 고객 기준 유효기간 1일, 1일 1회 발급 원칙, 6시간 이내 재호출 시 기존 토큰 반환.
- `국내업종 일자별지수`: 한 번 조회에 100건.
- `국내주식업종기간별시세`: 한 번 호출에 최대 50건.

workbook 안에서 `주식기본조회`의 명시적 일일 호출 제한 또는 초당/분당 제한 값은 찾지 못했다. 실제 다운로드 전 KIS portal 또는 승인된 smoke test로 rate-limit를 별도 확인해야 한다.

## Kiwoom API 검토

### 로컬 코드/문서에서 확인한 것

Credential 위치:
- `research_input_data/.env`
- key 이름: `KIWOOM_APPKEY`, `KIWOOM_SECRETKEY`
- 실제 값은 보고서에 기록하지 않는다.

저장소 내 Kiwoom 관련 로컬 산출물:
- `research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv`
- `research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv`
- `research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
- `research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv`
- `research_input_data/inputs/market_flow/kiwoom_market_flow_*.csv`

기존 panel fields:
- `날짜`, `종목코드`, `종목명`, OHLCV
- `기관순매매량`, `외국인순매매량`
- `기관순매수금액추정`, `외국인순매수금액추정`
- `거래대금추정`, `시가총액추정`, `상장주식수`
- 품질/통합거래 관련 flags

확인 결과:
- panel headers에는 `업종`, `섹터`, `sector`, `industry`, `classification`, `분류`, WICS/GICS 계열 컬럼이 없다.
- `src/`, `configs/`, `tests/`, `research/`, `docs/`에서 Kiwoom REST 호출 구현, endpoint URL, TR code, 종목정보/업종 endpoint 문서는 찾지 못했다.
- `research/data_inventory/2026-05-13_initial_survey.md`에는 Kiwoom REST auth가 OK였고 기존 inputs panel/market-flow가 Kiwoom REST에서 왔다는 기록이 있다. 다만 종목별 업종 endpoint에 대한 검증 기록은 없다.

### Kiwoom: 업종 endpoint 존재 여부

현재 저장소 근거만으로는 확인 불가.

가능성은 있지만, 로컬에 Kiwoom REST API 문서나 호출 코드가 없어서 다음 항목을 확정할 수 없다.
- 종목코드 + 업종 매핑 response 존재 여부
- historical 기준일 조회 가능 여부
- 업종 코드/업종명 field 명세
- 일일/분당 호출 제한

Kiwoom은 기존 수급/market-flow 수집 source였으므로 계정과 인증은 존재한다. 하지만 이번 목표인 종목별 sector mapping만 놓고 보면, 현재 검토 가능한 로컬 evidence는 KIS 쪽이 훨씬 강하다.

## 추천 작업 명세

승인 후 1차 다운로드는 KIS로 진행하는 것이 가장 깔끔하다.

1. 대상 universe 확정
   - 최소: 기존 panel에 등장한 unique `종목코드`
   - 권장: E000/E001용으로 `dynamic_top100_2018_2024_panel.csv` + `dynamic_top100_2025_2026_krx_panel.csv` unique 종목부터 시작

2. KIS `주식기본조회` 호출
   - endpoint: `/uapi/domestic-stock/v1/quotations/search-stock-info`
   - TR_ID: `CTPF1002R`
   - query: `PRDT_TYPE_CD=300`, `PDNO=<6-digit ticker>`
   - 저장 필드: `pdno`, `prdt_name`, `mket_id_cd`, `scty_grp_id_cd`, `idx_bztp_lcls_cd`, `idx_bztp_mcls_cd`, `idx_bztp_scls_cd`, `idx_bztp_lcls_cd_name`, `std_idst_clsf_cd`, `std_idst_clsf_cd_name`, listing/delisting/status fields

3. 결과 저장
   - raw API response는 `data/raw/`가 read-only 규칙상 금지 대상이므로 쓰지 않는다.
   - 처리 산출물은 `data/processed/sector_membership_kis_snapshot_<YYYYMMDD>.csv` 또는 parquet 후보.
   - 새 데이터 파일 추가 시 `research_input_data/docs/DATA_CATALOG.md` 또는 equivalent catalog 업데이트가 필요하다. 단 `research_input_data/`는 현재 read-only 규칙이 있으므로 카탈로그 업데이트는 별도 승인/티켓으로 처리해야 한다.

4. metadata 명시
   - `source=KIS_CTPF1002R`
   - `classification_asof_date=<download date>`
   - `point_in_time_available=false`
   - `classification_bias_flag=true` unless historical membership source is added

5. 검증
   - panel unique ticker 대비 mapping coverage
   - `idx_bztp_*` null/`000` 비율
   - `std_idst_clsf_cd` null/`000000` 비율
   - 보통주 필터 후보: `scty_grp_id_cd`, `stck_kind_cd`
   - 상장폐지/거래정지/관리종목 fields sanity check

## 사용자 승인 필요한 부분

아직 하지 않은 작업:
- KIS token 발급
- KIS `주식기본조회` 실제 호출
- Kiwoom token 발급 또는 endpoint 탐색 호출
- 외부 network 접속
- 새 데이터 파일 생성

다음 단계로 진행하려면 외부 network/API 호출 승인이 필요하다. 승인 범위는 `KIS 주식기본조회 CTPF1002R을 기존 panel unique 종목코드에 대해 호출하고, 결과를 data/processed에 snapshot으로 저장`처럼 endpoint와 저장 위치를 명시하는 방식이 적절하다.
