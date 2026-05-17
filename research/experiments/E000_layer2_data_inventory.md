# E000 — Layer 2 데이터 인벤토리 확인

## 상태
계획됨

## 이게 무슨 ticket 인가

E-family (Layer 2 = 섹터 선택) 의 첫 단계. 코드 작성 거의 없고
**가능/불가능 판단** 이 목표.

Layer 2 가 진짜 의미 있으려면 다음 데이터 필수:
1. 종목별 섹터 분류 (가능하면 시점별 멤버십)
2. 종목별 일별 외국인 매매
3. 종목별 시가총액, 거래대금 (이미 있음 — D-family 에서 사용)
4. 결측/상장폐지/거래정지 처리

E000 = 이게 우리 `research_input_data/` 안에 있는지, 어디에 있는지,
어떻게 가공해야 하는지 정직하게 인벤토리.

## 확인 항목

### A. 섹터 분류 데이터

가능 source:
- **KRX 업종** (대분류, 중분류, 소분류)
- **WICS** (FnGuide 표준업종)
- **GICS** (Global Industry Classification)
- **자체 분류**

확인 사항:
- 현재 panel 파일 (kiwoom_dynamic_top100_*.csv, dynamic_top100_*.csv)
  안에 섹터 컬럼 있는지
- 별도 섹터 매핑 파일 있는지
- 과거 변경 이력 (point-in-time 멤버십) 있는지, 현재 분류만 있는지

### B. 종목별 외국인 매매

확인 사항:
- 종목별 일별 외국인 순매수 (금액 또는 수량)
- 어떤 파일에 있는지 (panel 안 컬럼? 별도 파일?)
- 투자자별 구분 가능한지 (외국인 / 기관 / 개인)
- 결측치 처리

### C. 섹터 aggregate 가능성

확인 사항:
- 섹터별 수익률 계산 가능한가 (종목 수익률 + 가중치)
- 섹터별 거래대금 합산 가능한가
- 섹터별 시가총액 합산 가능한가
- 섹터별 외국인 순매수 합산 가능한가
- 섹터 내 종목 수 (너무 적으면 noise)

### D. 시점별 멤버십

확인 사항:
- 상장 / 상폐 이력
- 섹터 분류 변경 이력
- 거래정지, 관리종목 처리
- 현재 분류만 있는 경우 prototype 으로 처리 + bias 명시

## 사전 등록 판정

| 결과 | 판정 | 다음 |
|---|---|---|
| 모든 데이터 보유 + 시점별 처리 가능 | **PROCEED** | E001 (멤버십 인프라) 진행 |
| 섹터 분류는 현재 것만 있음 + 다른 데이터 OK | **PROCEED WITH BIAS FLAG** | E001 진행하되 prototype 으로 명시 |
| 종목별 외국인 매매 누락 | **STOP** | 외부 download 또는 alternative 검토 |
| 섹터 분류 누락 | **STOP** | KRX/FnGuide 등에서 매핑 수집 필요 |

## 구현 작업

새 strategy 코드 없음. 인벤토리 보고서 작성:

추가만:
- `reports/experiments/E000_layer2_data_inventory/data_inventory.md` —
  주요 보고서
- `reports/experiments/E000_layer2_data_inventory/file_catalog.csv` —
  panel 파일별 컬럼 정보
- `reports/experiments/E000_layer2_data_inventory/data_gaps.md` —
  누락 데이터 명시 + 대안 제안

**수정 금지**:
- engine.py
- 기존 strategy 모듈 (a001-a004, b001-b011, c003-c020, d001-d019)
- D013 carrier
- research_input_data/

## 완료 기준

- 보고서 생성
- 다음 항목 명확히 답:
  1. 섹터 분류 데이터: 보유 / 부분 보유 / 없음 (어느 source 인지)
  2. 종목별 일별 외국인 매매: 보유 / 부분 보유 / 없음 (어느 파일, 어느 컬럼)
  3. 시점별 멤버십 처리 가능 여부
  4. 누락 데이터 발견 시 외부 download 또는 alternative 후보
  5. PROCEED / PROCEED WITH BIAS FLAG / STOP 판정

## 범위 외

- 코드 작성 (E001 부터)
- 외부 download (E000 의 판정 결과로 별도 결정)
- 전략 실험 (E003 부터)

## 결과 요약
백테스트 없으니 채우는 항목은 데이터 인벤토리 + 판정.

## Claude 검토
codex 보고 받은 후 작성.
