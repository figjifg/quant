# H001 Operations

H001 carrier는 D013 ON 구간의 주식 포트폴리오를 그대로 쓰고, D013 OFF 구간의 KRW cash를 KR short-rate carry sleeve로 대체한다.

## Frozen Carrier

- ON sleeve: D013 macro gate + dynamic top 100 + market-cap top 5 equal weight.
- OFF sleeve: `KR_short_rate_carry`.
- KR rate source: FRED `IR3TIB01KRM156N`.
- Formula: `quarter_return = (1 + annual_rate / 12)^3 - 1`.
- Rebalance: 분기말 신호일 다음 KRX 거래일 실행.

## OFF Sleeve Assets

운영 상품은 분기 시작 전에 하나를 선택하고 분기 중 임의 변경하지 않는다.

- MMF: 운영 편의성이 높고 duration risk가 낮다.
- 단기채 ETF: 거래 편의성이 높지만 가격 변동과 스프레드가 있다.
- 정기예금: 금리 확정성이 높지만 중도해지 제약이 있다.
- 한국 국채 단기물: credit risk가 낮지만 실행 단위와 mark-to-market 변동을 확인해야 한다.

## Quarterly Procedure

1. 분기말 KRX 장 마감 후 `scripts/quarterly_signal_generator.py`로 신호 JSON을 생성한다.
2. `regime_on = true`이면 D013 주식 basket을 실행한다.
3. `regime_on = false`이면 주식 basket 대신 사전 선택한 carry asset을 보유한다.
4. 분기 평가에는 `estimated_quarter_carry`, 실제 carry, 차이, 실행 비용을 기록한다.
5. D013 original cash baseline을 병렬 가상 추적하고 4 분기 후 H001 carrier와 비교한다.

## Controls

- H001 carrier 정의, rate source, formula는 재등록 전까지 변경하지 않는다.
- 기존 `paper_trading/signals/*.json`은 사후 수정하지 않는다.
- OFF sleeve 실제 수익이 추정 carry와 다르면 원인을 evaluation 문서에만 기록한다.
