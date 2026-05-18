# G000 — Layer 4 설계 + 첫 risk overlay 구성요소 결정

## 상태
계획됨

## 이게 무슨 ticket 인가

Layer 3 (F-family) fail. D013 / E014 위에서 Layer 4 직접 진입.

지피티 권장 핵심 원칙:
> Layer 4 는 알파 레이어가 아닌 방어층. 수익 추가 X, MDD/변동성/집중도/비용 통제 O.

## G-family 의 첫 ticket

G000 = 인프라 + 첫 구성요소 결정:
1. 두 carrier (D013, E014) baseline 확인 (재현)
2. Layer 4 의 8 개 구성요소 중 첫 우선순위 결정
3. 첫 구성요소 적용 결과

## Layer 4 8 개 구성요소 (지피티 정의)

| # | 구성요소 | 작동 방식 |
|---|---|---|
| 1 | 매크로 익스포저 캡 | D013 신호 강/약/꺼짐에 따라 max gross 100/50/0~20% |
| 2 | 변동성 타겟팅 | vol_scalar = min(1, target/realized) |
| 3 | MDD 쿨다운 | 전략 손실폭 깊으면 자동 축소 |
| 4 | 스트레스 필터 | VIX + USDKRW + 변동성 동시 급등 시 축소 |
| 5 | 섹터 집중도 제한 | max weight per sector |
| 6 | 종목 집중도 제한 | max weight per stock |
| 7 | 유동성 제한 | 일평균 거래대금 기준 |
| 8 | 회전율 / 비용 제한 | no-trade zone, score 우위 조건 매수 |

## 첫 구성요소 우선순위 (G000 결정)

D-family findings + F-family findings 기반:
- D013 MDD = COVID 2020-03 (-34%, 23 거래일 급락) — **변동성 타겟팅 + 스트레스 필터** 가 가장 직접
- E014 MDD = 2021-2022 긴 회복 (-36%) — **MDD 쿨다운** 도 필요
- 두 carrier 가 시총 top 5 라 종목/섹터 집중도 자동 — 6,7 은 sector 단위 영향 작음

**G000 첫 ticket 추천**: **변동성 타겟팅** (구성요소 2)
- 가장 직접 MDD 보호
- 단일 변수 (realized vol) 만 사용
- target_vol = 20% (예시, 사전 등록)
- vol_scalar = min(1, target_vol / realized_vol_60d)
- 두 carrier 위에서 적용

## 사전 등록 verdict

| 결과 | 판정 |
|---|---|
| MDD 개선 (≥ 5pp) + 누적 수익 감소 ≤ 30pp | 변동성 타겟팅 효과 — G001 다음 |
| MDD 개선 + 누적 감소 ≤ 50pp | 트레이드오프 acceptable |
| MDD 개선 < 5pp | 효과 미미 — 다른 구성요소 |
| 누적 감소 > 50pp + MDD 개선 작음 | over-control — parameter 조정 또는 다른 방식 |

## 산출물

- reports/experiments/G000_layer4_design/
- baseline_reproduction.md (D013, E014 재현)
- vol_targeting_results.csv (두 carrier 위에서)
- report.md

## 엄격 제약

- engine.py 수정 가능성 있음 (vol_scalar 가 portfolio weights 곱하기) — 필요시 사용자 승인 받기
- 기존 strategy 미수정 (D013, E014 wrappers 그대로 둘러쓰기)
- D001-D015, E003-E015, F002-F012 byte-identical
- sandbox pandas 없으면 직접 실행 OK
