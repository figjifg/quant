# Q006.6 Factor ETF Proxy Benchmark

## 목적

직접 Q002/Q006 stock sleeve가 factor ETF proxy보다 명확히 우월한지 검증한다. ETF가 비슷하거나 더 좋으면 survivorship-safe universe가 없는 direct Q-family보다 ETF proxy를 production 후보로 우선한다.

## 사전 등록

1. ETF buy-hold standalone: QUAL, COWZ, SCHD, VLUE, MTUM, SPY, QQQ를 USD NAV 기준으로 비교한다.
2. Q002/Q006 direct sleeve 비교: ETF별 공통 기간 및 전체 factor ETF 공통 기간에서 Q002/Q006와 ETF sleeve를 비교한다.
3. P08_IEF30 + ETF sleeve preview: P08_IEF30 baseline에서 SPY 10%를 factor ETF 10%로 대체하는 gross preview를 계산한다.

## 제약

- 기존 Q-family, P08, H001 산출물은 수정하지 않고 읽기만 한다.
- 외부 network를 사용하지 않는다.
- 직접 Q-family는 survivor universe diagnostic이며 production 후보가 아니다.
- COWZ 상장일 때문에 모든 factor ETF의 완전 공통 기간은 2016-12 이후로 제한된다.
