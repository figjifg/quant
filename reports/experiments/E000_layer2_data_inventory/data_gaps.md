# E000 Data Gaps

작성일: 2026-05-18

## 판정

**STOP**

Layer 2 섹터 선택 실험은 현재 `research_input_data/`만으로 진행할 수 없다. 종목별 일별 외국인/기관 매매와 가격/거래대금/시가총액은 보유하고 있으나, 종목별 섹터 분류가 없다.

## 누락 데이터

| 데이터 | 상태 | 영향 |
|---|---|---|
| 종목별 섹터 분류 | 없음 | 섹터별 수익률, 거래대금, 시총, 외국인 순매수 aggregate 생성 불가 |
| 섹터 분류 변경 이력 | 없음 | point-in-time 섹터 멤버십 불가 |
| 종목별 개인 순매매 | 없음 | 외국인/기관/개인 3자 분해 불가 |
| 상장/상폐 이벤트 | 없음 | 전체 universe survivorship 점검 불완전 |
| 거래정지/관리종목 플래그 | 없음 | 거래 불가능 종목의 명시적 제외 불가 |
| 전체 시장 universe 멤버십 | 없음 | dynamic top100 밖의 섹터 coverage 확인 불가 |

## 보유 데이터로 가능한 범위

- Dynamic Top100 내부의 종목별 일별 외국인/기관 수급 계산.
- `동적유니버스포함` 기준의 날짜별 Top100 멤버십 제한.
- 종목별 거래대금/시가총액 기반 가중치 계산.
- 섹터 key가 외부에서 들어온 뒤에는 panel 범위 내 섹터 aggregate 계산 가능.

## 외부 Download 또는 수집 후보

새 다운로드는 E000 범위 밖이며, 다음 단계 티켓에서 명시 승인 후 진행해야 한다.

| 후보 | 기대 데이터 | 장점 | 주의점 |
|---|---|---|---|
| KRX 정보데이터시스템 | 종목별 업종, 상장/상폐, 관리종목/거래정지 후보 | 공식 KRX source, KRX 업종 사용 가능 | 과거 업종 변경 이력 확보 가능 여부 확인 필요 |
| pykrx | KRX 종목 목록/업종/상장 관련 데이터 접근 후보 | Python 기반 자동화 가능 | API/웹 소스 안정성, rate limit, 날짜별 업종 이력 지원 여부 검증 필요 |
| FinanceDataReader | 상장 종목 리스트, 시장 구분 후보 | 간단한 종목 universe 보강 가능 | WICS/GICS 또는 point-in-time 업종 이력은 제한적일 수 있음 |
| FnGuide/WICS | WICS 업종 분류 | 한국 주식 섹터 분석에 적합 | 라이선스/접근 권한/과거 이력 여부 확인 필요 |
| KIS API 문서 기반 조회 | 업종/종목 정보 API 후보 | 기존 API 문서 workbook에 업종 관련 명세 존재 | 문서일 뿐 로컬 데이터 없음. credential/API 사용은 별도 승인 필요 |

## Alternative 후보

1. 현재 섹터 분류만 수집해 prototype 수행
   - 판정은 `PROCEED WITH BIAS FLAG`가 된다.
   - bias: 현재 분류를 과거 전체 기간에 소급 적용하는 classification bias.
   - 보고서에는 `sector_mapping_asof_date`, `classification_bias_flag=true`를 명시해야 한다.

2. KRX 업종 point-in-time 매핑 수집 후 진행
   - 판정은 `PROCEED` 가능.
   - E001에서 `date`, `종목코드`, `sector_code`, `sector_name`, `valid_from`, `valid_to`, `source` schema를 먼저 확정해야 한다.

3. 섹터가 아닌 유동성/시총 bucket proxy 사용
   - 섹터 선택 실험의 대체 연구일 뿐 Layer 2 섹터 aggregate는 아니다.
   - 예: dynamic top100 내 시총 분위, 거래대금 분위, 외국인 수급 분위.

4. 시장 aggregate proxy 사용
   - `market_flow`의 KOSPI/대형주 외국인 순매수, `krx_market_breadth`의 breadth를 섹터 proxy처럼 쓰는 것은 가능하다.
   - 그러나 섹터별 foreign flow가 아니므로 E-family 목적과 다르다.

## E001 진행 조건

E001를 진행하려면 다음 중 하나가 필요하다.

- **PROCEED 조건:** point-in-time 섹터 매핑과 상장/상폐/거래정지 처리 기준을 수집한다.
- **PROCEED WITH BIAS FLAG 조건:** 현재 기준 섹터 매핑만 수집하고, 과거 기간 소급 적용 bias를 실험 메타데이터와 report에 명시한다.

최소 섹터 매핑 schema:

```text
date or valid_from/valid_to
종목코드
sector_source  # KRX/WICS/GICS/custom
sector_code
sector_name
asof_date
is_point_in_time
```

E001에서 처리할 데이터 명세 후보:

- 입력: 기존 `inputs/equity_panels/*.csv`
- 신규 입력: 승인된 섹터 매핑 파일
- 출력: `data/processed/sector_membership.parquet` 또는 experiment-local processed artifact
- 검증: 날짜별 종목의 sector null 비율, 중복 매핑, `signal_date` 기준 사용 가능 여부, 현재분류 소급 여부 flag
