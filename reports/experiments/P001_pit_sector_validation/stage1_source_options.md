# P001 Stage 1: PIT Sector Source Options

작성일: 2026-05-18

범위:
- `research/experiments/P001_pit_sector_validation.md` 확인
- KIS workbook `research_input_data/한국투자증권_오픈API_전체문서_20260511_030000.xlsx` sheet/field 확인
- `.venv` 설치 패키지 확인
- `research_input_data/.env` credential key 이름 확인. 값은 열람/기록하지 않음
- 저장소 코드/문서/기존 E000 산출물 확인
- 외부 API 호출, 외부 network 접속, 새 데이터 download 없음
- `engine.py`, strategy 코드, `research_input_data/inputs/`, `data/raw/` 수정 없음

## Executive Summary

PIT historical sector mapping의 1순위 후보는 **KRX 정보데이터시스템 또는 pykrx를 통한 KRX 원천 조회**다. 이유는 P001의 목적이 "현재 KIS snapshot bias 제거"이므로, KIS의 현재분류 endpoint를 반복 호출하는 것보다 기준일별 KRX 종목/업종분류 테이블을 확보하는 쪽이 직접적이다.

다만 이번 Stage 1은 외부 접속 금지라 KRX 화면 `bld`/download URL pattern과 일자별 조회 가능 여부를 로컬 근거만으로 확정하지 못했다. Stage 2 첫 작업은 사용자의 외부 network 승인 아래 KRX/pykrx의 기준일 조회 가능성을 짧게 검증하는 것이다.

KIS는 현재분류 snapshot source로는 이미 유효하다. `.env`에 `KIS_APP_KEY`, `KIS_APP_SECRET`가 있고, 기존 E000 수집 결과 `data/processed/sector_membership_kis_snapshot_20260518.csv`는 923개 ticker 성공으로 기록되어 있다. 그러나 KIS workbook 기준 `주식기본조회(CTPF1002R)` request에는 기준일자/as-of-date가 없어서 PIT source로는 **Partial**이다.

## Source Comparison

| Source | 가능성 | 비용 | 작업량 | 추천 우선순위 | 한 줄 판단 |
|---|---|---:|---:|---:|---|
| KRX 정보데이터시스템 | Partial | 무료 | medium | 1 | 원천 후보. Stage 2에서 기준일별 종목 업종분류 download 가능 여부 검증 필요 |
| pykrx | Partial | 무료 | small-medium | 2 | KRX scrape wrapper 후보. 현재 미설치라 network/install 승인 필요 |
| KIS API 추가 endpoint | Partial | 무료/계정 보유 | small | 3 | 현재분류와 업종지수는 가능. PIT 종목별 sector 이력은 문서상 확인 안 됨 |
| Manual approach | Partial | 무료 | medium-large | 4 | 변경 종목 수가 작으면 보조 검증용으로 가능. 923개 전체 PIT의 주 source로는 약함 |
| FnGuide WICS | Partial | 유료 | medium | 5 | PIT WICS를 살 수 있으면 품질은 좋을 수 있으나 credential/가입 근거 없음 |

## 1. KIS API

### 로컬 credential 및 기존 산출물

- `research_input_data/.env`에 `KIS_APP_KEY`, `KIS_APP_SECRET` 존재.
- 기존 코드: `src/data/kis_sector_fetcher.py`, `scripts/fetch_kis_sector_snapshot.py`.
- 기존 E000 로그: `reports/experiments/E000_layer2_data_inventory/api_fetch_log.md`
  - `total_unique_tickers: 923`
  - `kis_api_success_count: 923`
  - `count_coverage_pct: 100.000000`
  - 판정: `PROCEED WITH BIAS FLAG`
- 따라서 KIS credential 자체는 현재분류 snapshot 수집에는 충분했던 것으로 보인다.

### historical/PIT 관련 workbook 확인

KIS workbook에서 확인한 종목/업종 관련 endpoint:

| Sheet | TR_ID | URL | PIT 관련성 |
|---|---|---|---|
| `주식기본조회` | `CTPF1002R` | `/uapi/domestic-stock/v1/quotations/search-stock-info` | 종목별 현재 기본정보/업종분류 후보. 기준일자 query 없음 |
| `국내주식업종기간별시세(일_주_월_년)` | `FHKUP03500100` | `/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice` | 업종 지수 OHLC 기간조회. 종목별 구성원 아님 |
| `국내업종 일자별지수` | `FHPUP02120000` | `/uapi/domestic-stock/v1/quotations/inquire-index-daily-price` | 업종 지수 일자별 조회. 종목별 구성원 아님 |
| `국내업종 구분별전체시세` | `FHPUP02140000` | `/uapi/domestic-stock/v1/quotations/inquire-index-category-price` | 업종 코드/현재 업종 시세 목록 후보. 기준일별 구성원 아님 |
| `예탁원정보(상장정보일정)` | `HHKDB669107C0` | `/uapi/domestic-stock/v1/ksdinfo/list-info` | 상장/증자 등 일정. sector 변경 이력 아님 |
| `예탁원정보(합병_분할일정)` | `HHKDB669104C0` | `/uapi/domestic-stock/v1/ksdinfo/merger-split` | 분할/합병 이벤트. manual 변경 후보 탐지 보조용 |

`주식기본조회(CTPF1002R)`:
- Request query는 `PRDT_TYPE_CD=300`, `PDNO=<종목번호>`만 확인됨.
- Response에는 `pdno`, `prdt_name`, `mket_id_cd`, `scty_grp_id_cd`, `idx_bztp_lcls_cd`, `idx_bztp_mcls_cd`, `idx_bztp_scls_cd`, `std_idst_clsf_cd`, `std_idst_clsf_cd_name`, 상장/폐지 관련 date field가 있음.
- 기준일자, 조회일자, valid_from/valid_to, 업종변경 이력 field는 확인되지 않음.

업종 지수 endpoint:
- `FHKUP03500100`은 `FID_INPUT_DATE_1`, `FID_INPUT_DATE_2`, `FID_PERIOD_DIV_CODE`가 있어 업종 지수의 기간조회는 가능.
- `FHPUP02120000`은 `FID_INPUT_DATE_1` 기준 100건 조회 가능.
- 둘 다 response의 date는 `stck_bsop_date`이고, 종목별 sector membership이 아니라 업종 지수 가격/거래량/거래대금이다.

### KIS 판단

- 가능성: **Partial**
- 비용: 무료/기존 계정 보유
- 작업량: small
- bias 한계:
  - 현재분류 snapshot이라 classification look-ahead bias가 남는다.
  - KIS 중분류에는 `KOGI(지배구조지수)`, `KODI(배당지수)` 같은 index-like label이 섞일 수 있어 operating sector로 바로 쓰면 왜곡 가능.
  - 업종 지수 endpoint는 sector return proxy에는 쓸 수 있으나 종목별 PIT membership 검증에는 부족하다.
- 추천 우선순위: **3**

## 2. pykrx

### 설치 상태

- `.venv/bin/python -m pip list`: `pykrx` 없음.
- `requirements.txt`: `pykrx` 없음.
- `importlib.util.find_spec("pykrx")`: `not_installed`.
- 로컬 wheel/cache/코드 흔적도 확인되지 않음.

### historical 가능성

로컬에 pykrx 문서나 package가 없어서 실제 함수 signature는 확인하지 못했다. 사용자가 예시로 든 `pykrx.stock.get_market_sector_classifications` 계열 함수가 기준일자 인자를 지원한다면, KRX 종목별 업종분류를 가장 적은 코드로 받을 수 있는 후보가 된다.

단, 이번 Stage 1에서는 설치도 외부 network가 필요하고, 함수 검증도 package 설치 또는 외부 문서 확인이 필요하다. 따라서 확정은 Stage 2 승인 후로 넘겨야 한다.

### pykrx 판단

- 가능성: **Partial**
- 비용: 무료. 설치에는 외부 network 필요
- 작업량: small-medium
- bias 한계:
  - KRX scrape wrapper라 내부적으로 현재 KRX 화면 구조에 의존할 수 있다.
  - 함수가 기준일자를 받더라도 과거 특정일의 "그날 유효한 분류"인지, 조회 시점 분류를 과거 가격 날짜에 붙이는 것인지 반드시 smoke test가 필요하다.
  - pykrx source/response metadata를 저장해 재현성을 보강해야 한다.
- 추천 우선순위: **2**

## 3. KRX 정보데이터시스템

### 로컬 확인 결과

- `.env`에 `KRX_API_KEY`, `KRX_AUTH_KEY` 존재.
- 기존 `research/data_inventory/2026-05-13_initial_survey.md`에는 KRX 정보데이터시스템 raw access가 401로 막혔고 header form이 unknown이었다는 기록이 있다.
- 저장소 안에는 `data.krx.co.kr` 호출 코드, 종목 업종분류 download URL, `bld` pattern 문서가 없다.
- 이번 Stage 1 제약상 외부 접속/다운로드를 하지 않았으므로 KRX 화면의 `generate.cmd`/`download.cmd` payload와 기준일자 parameter는 확정하지 않았다.

### 판단

KRX가 원천 source이므로 구조상 가장 좋은 후보지만, 현재 로컬 근거만으로는 "종목 업종분류가 특정 기준일자로 다운로드 가능한지"를 확정할 수 없다. Stage 2에서 해야 할 최소 검증은 다음이다.

1. KRX 정보데이터시스템의 전종목 기본정보/업종분류 화면에서 기준일자 입력 여부 확인.
2. CSV download payload의 `bld`, `mktId`, `trdDd` 또는 유사 기준일자 parameter 확인.
3. 서로 다른 기준일 두 개(예: 2018-12-28, 2026-05-06)를 조회해서 NAVER/카카오/LG에너지솔루션/한화오션 같은 known-risk 종목의 sector 값이 날짜에 따라 독립적으로 재현되는지 확인.
4. 다운로드 산출물에 기준일자를 명시하고 `data/processed/`로만 저장.

### KRX 판단

- 가능성: **Partial**
- 비용: 무료
- 작업량: medium
- bias 한계:
  - 화면 download가 current classification만 반환하면 KIS snapshot과 같은 문제가 남는다.
  - KRX 업종분류는 WICS/GICS와 분류 체계가 다르므로 E014 snapshot mapping과 코드 체계 crosswalk가 필요할 수 있다.
  - 웹 scrape/download endpoint는 화면 개편에 취약하다.
- 추천 우선순위: **1**

## 4. FnGuide WICS

### credential/가입 확인

- `research_input_data/.env`에서 `FNGUIDE_*`, `FN_GUIDE_*`, `WICS_*` credential key는 발견되지 않음.
- 저장소 내 `FnGuide`, `WICS` 관련 구현/데이터 파일 없음.
- `research/experiments/E000_layer2_data_inventory.md`에서 WICS는 후보 source로만 언급됨.

### 판단

WICS historical membership를 계약/API/파일로 받을 수 있다면 PIT sector source로는 품질이 좋을 수 있다. 하지만 현재 저장소에는 가입/credential/파일 근거가 없고 유료 source이므로 바로 진행할 수 없다.

- 가능성: **Partial**
- 비용: 유료
- 작업량: medium
- bias 한계:
  - 접근 권한과 라이선스가 없으면 사용 불가.
  - WICS 분류는 KRX/KIS 업종과 체계가 다르므로 기존 E014 sector 정의와 비교하려면 crosswalk 또는 전략 재정의가 필요하다.
  - 유료 데이터의 재배포/저장 위치/카탈로그 정책을 별도로 확인해야 한다.
- 추천 우선순위: **5**

## 5. Manual Approach

### 로컬 universe와 후보

- 기존 E000 KIS snapshot 대상 universe는 923개 ticker.
- 로컬 panel union을 직접 확인하면 dynamic universe 포함 ticker는 panel 조합에 따라 923~925개 수준으로 보인다.
- 문제 가능성이 큰 대형주/이벤트 종목은 별도 manual audit 후보가 된다:
  - `005930` 삼성전자, `000660` SK하이닉스: 장기 대형 benchmark 성격.
  - `035420` NAVER, `035720` 카카오: 서비스/인터넷/platform 분류 및 KIS index-like label 이슈.
  - `373220` LG에너지솔루션: 2022 신규상장, 전기전자/2차전지 분류 영향.
  - `042660` 한화오션: 대우조선해양에서 사명/지배구조 변경, 운수장비/조선 분류 확인 필요.
  - `005490` POSCO홀딩스, `003670` 포스코퓨처엠, `010060` OCI홀딩스, `402340` SK스퀘어: 지주/분할/소재/서비스 분류 변경 가능성이 있는 후보.

### manual 가능성

Manual은 전체 923개 PIT table을 처음부터 만들기에는 크다. 그러나 KRX/pykrx/KIS snapshot 차이에서 "분류가 바뀐 종목" 후보가 작게 나오면, 변경 이력 검증과 예외 override table 작성에는 현실적이다.

권장 manual 산출물 형태:
- `ticker`
- `company_name`
- `valid_from`
- `valid_to`
- `sector_source`
- `sector_code`
- `sector_name`
- `evidence_url_or_doc`
- `confidence`
- `notes`

### Manual 판단

- 가능성: **Partial**
- 비용: 무료
- 작업량: medium-large
- bias 한계:
  - 사람이 known large caps 위주로 수집하면 coverage bias가 생긴다.
  - Wiki/뉴스 기반 변경일은 실제 KRX 업종 적용일과 다를 수 있다.
  - 누락된 중소형 sector 변경이 E014 sector aggregate에 누적 영향을 줄 수 있다.
- 추천 우선순위: **4**

## Recommended Stage 2 Plan

1순위는 **KRX 정보데이터시스템 직접 검증**이다. P001의 핵심은 현재 snapshot bias 제거이므로, 원천 KRX에서 기준일별 종목 업종분류가 되는지 먼저 확인해야 한다. pykrx는 같은 목적의 빠른 wrapper 후보라서 KRX 직접 검증과 병행 또는 직후에 확인한다.

Stage 2 최소 승인 요청:
- 외부 network 접속 승인: `data.krx.co.kr`, pykrx 설치/문서 확인에 필요한 PyPI/GitHub 또는 package source.
- 새 데이터 생성 승인: 검증용 small sample과 최종 산출물은 `data/processed/` 및 `reports/experiments/P001_pit_sector_validation/` 아래에만 저장.
- KIS API 호출 승인(선택): KIS는 PIT source가 아니라 KRX/pykrx 결과와 current snapshot 비교용으로만 추가 호출.
- FnGuide 승인(선택): 사용자가 WICS 가입/credential 보유 여부를 확인해 주면 별도 검토.
- Manual 작업 승인(선택): KRX/pykrx 결과가 불완전할 때 대형 이벤트 종목부터 수동 evidence table 작성.

## Open Questions

현재 Stage 1에서 막힌 문제는 없다. `P001_codex_questions.md`는 작성하지 않았다.
