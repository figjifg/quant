# U003 P08_IEF30 Owner's Manual

Status: owner manual for the frozen production candidate.

## 전략 철학

`P08_IEF30`는 글로벌 자산배분 전략이다. 미국 주식 core, 한국 단기금리/carry
sleeve, 미국 중기국채 diversifier를 결합한다. 목적은 단기 예측이 아니라
분기 단위로 고정된 위험 노출을 유지하는 것이다.

## 포트폴리오 구성

| Sleeve | Weight | 역할 |
|---|---:|---|
| SPY | 29% | 미국 대형주 core |
| QQQ | 21% | 성장주 수익 엔진 |
| H001 | 20% | 한국 단기금리/carry sleeve |
| IEF | 30% | Treasury diversifier |

이 비중은 frozen spec이다. P08 weight 재최적화, D013 수정, H001 수정은 이
manual의 범위가 아니다.

## 기대 역할

- SPY: 넓은 미국 주식 beta와 장기 수익 기반.
- QQQ: 높은 성장 노출과 상승장 수익 엔진.
- H001: 한국 원화 기반 carry 및 변동성 완충.
- IEF: equity crash와 성장주 drawdown에 대한 완충. 금리 상승기에는 손실 가능.
- USDKRW: 원화 NAV 기준 수익과 위험을 동시에 흔드는 별도 요인.

## 하면 안 되는 것

- QQQ 임의 확대.
- IEF 제거.
- H001 제거.
- drawdown 중 전량 청산.
- N001-B/N002-B shadow를 사후 성과만 보고 즉시 승격.
- 세금 부담을 이유로 목표 비중 자체를 바꾸기.

## 정상적인 고통

- -10%: 정상 변동성. 아무 조치도 필요하지 않다.
- -20%: 고통 구간. 운영 오류와 paper/live 괴리를 점검하되 전략 변경 금지.
- -30%: 위기 구간. 사전 폐기 조건과 pilot 중단 조건을 점검한다.

GFC-like, 2022-like, COVID-like 경로에서 큰 drawdown은 가능하다. 이 전략은
고통을 제거하지 않고, 고통 중 행동을 제한한다.

## 리밸런싱

분기 리밸런싱이 기본이다. 기준일 NAV, 현재 비중, 목표 비중, 주문 수량,
환전 필요액, 세금 lot impact를 모두 남긴다. 시장가 주문은 사용하지 않는다.

## 세금

해외 ETF 매도는 HIFO lot을 기본으로 검토한다. 연간 250만원 기본공제와 배당
원천징수는 별도 기록한다. 세금 추적 실패는 live pilot 중단 조건이다.

## Shadow 해석

N002-B와 N001-B는 live 전략이 아니라 shadow 비교 대상이다. 4개 분기 이상
MDD 개선, CAGR drag, stress day 행동, 2022/equity crash 대응을 비교한 뒤에만
승격 검토가 가능하다.

## Live Pilot

pilot은 작게 시작한다. 증액 조건은 paper/live NAV 괴리, 체결 shortfall,
세금 기록, 규칙 준수로 판단한다. 최근 성과가 좋다는 이유만으로 증액하지
않는다.

## 전략 폐기 조건

- 사전 정의한 stress에서 유사 frontier가 붕괴함.
- live/paper 괴리가 구조적으로 설명되지 않음.
- 세금과 환전 비용 반영 후 net edge가 사라짐.
- 운영 규칙을 반복적으로 지킬 수 없음.
- 더 보수적인 shadow가 명시된 return sacrifice 안에서 4분기 이상 우월함.
