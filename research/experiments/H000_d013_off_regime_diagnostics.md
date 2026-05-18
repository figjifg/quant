# H000 — D013 OFF regime 진단 (H-family 첫 ticket)

## 상태
계획됨

## 이게 무슨 ticket 인가

지피티 + 우리 합의: 다음 프로젝트 = **D013 OFF Sleeve 연구**.
H000 = sleeve 선택 전 OFF regime 의 성격 진단.

D013 ON 약 23%, **OFF 약 77%** → cash 보유 시간 큰 빈 공간.
OFF 시기 성격에 따라 sleeve 후보 결정:
- **Risk-off** → USD, Treasury, Gold, defensive basket
- **Sideways** → cash 가 합리적, sleeve 효과 작음
- **Missed rally** → D013 macro gate 자체 문제 (그러나 동결 원칙)

## 필수 산출물 (사전 등록)

### A. OFF regime 통계
- D013 OFF 분기 수, %
- 평균 OFF duration (연속 OFF 분기)
- 최장 OFF streak
- ON/OFF 전환 빈도

### B. Return 분포 비교 (분기 단위)
| 시점 | KOSPI | D013 top 5 | USDKRW (yoy) | US 10y yield 변화 | Gold | KR 단기금리 |
| OFF | ? | - | ? | ? | ? | ? |
| ON | ? | ? | ? | ? | ? | ? |

각각 mean, median, std, min, max, % positive

### C. Missed rally / avoided crash
- OFF 분기 중 KOSPI 가장 큰 양수 (missed rally) top 5
- OFF 분기 중 KOSPI 가장 큰 음수 (avoided crash) top 5
- OFF 인데 KOSPI > +10% 인 분기 수 / 비율
- OFF 이면서 KOSPI < -10% 인 분기 수 / 비율

### D. Sleeve 후보 OFF 시기 성과
- USDKRW OFF 시기 평균 yoy
- Gold OFF 시기 평균 yoy
- US Treasury (DGS10 변화) OFF 시기
- KR 단기금리 OFF 시기 carry

### E. Diagnostic: KOSPI inverse (H006 대체, 간단)
- OFF 시기 KOSPI 평균 return = 강한 음수?
- OFF 시기 short return 가정 (KOSPI return × -1)
- Inverse ETF decay 가정 없이 단순 short return 분포

## 사전 등록 verdict (sleeve 선택 framework)

| OFF 성격 | 권장 sleeve |
|---|---|
| KOSPI 평균 < -3% (risk-off) | USD, Treasury, Gold, defensive basket 강한 후보 |
| KOSPI 평균 -3% ~ +3% (sideways) | cash 합리적, carry sleeve (KR short rate) 만 |
| KOSPI 평균 > +3% (missed rally) | sleeve 못 해결, backlog |
| 분포 양극 (큰 ± 둘 다 많음) | static defensive basket 가 안정 |

## 데이터 필요

기존 보유:
- D013 quarterly_regime_log.csv (분기별 ON/OFF)
- USDKRW (FRED dexkous_usdkrw.csv)
- US Treasury (FRED dgs2/10)
- KOSPI cap_weighted_return (market_breadth_kospi)
- VIX, etc

새 download 필요:
- **Gold** (FRED GOLDPMGBD228NLBM 또는 GOLDAMGBD228NLBM, 일별)
- **한국 단기금리** (FRED IR3TIB01KRM156N, monthly 또는 일별 시도)

## 산출물

- reports/experiments/H000_off_regime_diagnostics/
- A_off_regime_stats.csv
- B_return_distribution.csv (OFF vs ON 비교 표)
- C_missed_rally_avoided_crash.csv
- D_sleeve_candidate_returns.csv
- E_kospi_inverse_diagnostic.csv
- report.md (sleeve 선택 권고)

## 엄격 제약

- 새 backtest 없음 (분석 + 추가 data download 만)
- D013 strategy 미수정 (D-family 모든 결과 byte-identical)
- E014, F-family, G-family 결과 미수정
- Gold / 한국 단기금리 데이터 download = 외부 network (FRED 만)
- sleeve 후보 선택 전 H000 결과 본 후 (사후 fitting 회피)

## 완료 기준

- 5 산출물 모두 생성
- sleeve 선택 권고 명확
- H001-H005 우선순위 결정 (어느 sleeve 부터 정식 등록)
