# D013 Paper Trading Protocol

## 목적

P004는 D013를 실거래 전 4개 분기 동안 종이매매로 검증하기 위한 운영 절차다. 실제 주문을 내지 않으며, 신호 산출, 의도 포트폴리오, 체결 가정, 분기말 포트폴리오 가치를 기록한다.

## 분기별 절차

1. 분기 마지막 KRX 거래일 장 마감 후 D013 신호를 산출한다.
2. `regime_on`을 확인한다. OFF면 해당 분기는 현금 유지로 기록한다.
3. ON이면 D013 universe 상위 5개 종목과 동일가중 목표비중을 확정한다.
4. `scripts/quarterly_signal_generator.py`를 실행해 `signals/YYYY-Q.json`을 저장한다.
5. 다음 KRX 거래일 시가 기준으로 모의 체결가를 기록한다.
6. 체결 후 `executions/YYYY-Q.json`에 intended price, actual price, slippage를 기록한다.
7. 분기말 portfolio value를 기록한다.
8. 4개 분기 기록이 누적되면 D013 baseline 대비 성과, slippage, 미체결/부분체결 여부를 평가한다.

## 체크리스트

- [ ] 사용 config가 `configs/backtests/d013.yaml` 또는 승인된 P005 production config인지 확인
- [ ] `signal_date`가 분기 마지막 KRX 거래일인지 확인
- [ ] `execution_date`가 `signal_date`보다 늦은 KRX 거래일인지 확인
- [ ] `regime_on` OFF 분기는 종목 리스트와 목표비중이 비어 있는지 확인
- [ ] `regime_on` ON 분기는 종목 5개와 동일가중이 기록됐는지 확인
- [ ] 체결 기록에는 intended price, actual price, slippage가 모두 있는지 확인
- [ ] 분기말 portfolio value가 기록됐는지 확인
- [ ] 4개 분기 누적 전에는 production deploy 판단을 내리지 않음

## 파일 위치

- 신호: `reports/experiments/P004_paper_trading_protocol/signals/YYYY-Q.json`
- 체결: `reports/experiments/P004_paper_trading_protocol/executions/YYYY-Q.json`
- 운영 문서: `docs/paper_trading_protocol.md`
