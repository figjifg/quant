# U001 Quarterly Rebalance Dry-run Procedure

Status: operations procedure. Dry-run output is not an order instruction.

## 목적

매 분기 말 live 리밸런싱 전에 같은 입력과 같은 순서로 리허설을 수행한다.
결과물은 `paper_trading/operations/dryrun/YYYY-Q.md`에 저장한다.

## 실행 명령

```bash
.venv/bin/python -m src.ops.u001_quarterly_dryrun --quarter 2026-Q2
```

옵션:

- `--nav-krw`: 기준 NAV. 기본값은 100,000,000원.
- `--cash-krw`: 현재 KRW 현금.
- `--cash-usd`: 현재 USD 현금.
- `--output`: 기본 출력 경로를 덮어쓸 때만 사용.

## 분기 절차

1. 분기 말 장마감 후 SPY/QQQ/IEF 종가, USDKRW, H001 NAV를 확인한다.
2. 브로커 계좌별 보유수량, 현금, 미체결 주문을 export한다.
3. dry-run 스크립트를 실행한다.
4. 출력 파일의 10 step이 모두 채워졌는지 확인한다.
5. 주문장 초안의 수량과 환전 필요액을 브로커 화면의 실시간 호가로 재검산한다.
6. 세금 lot impact가 비어 있으면 live 주문 전 HIFO lot export를 붙인다.
7. paper execution price와 다음 날 실제 체결가 괴리를 기록한다.

## 승인 전 체크

- 기준일과 실행일이 분리되어 있는가.
- 시장가 주문이 없는가.
- 매도 체결 가능액을 환전 필요액에서 먼저 차감했는가.
- 부분 체결 시 남은 주문 재계산 규칙이 적혀 있는가.
- 세금/수수료/환전 비용이 NAV에 반영되어 있는가.

## 실패 처리

데이터 오류, 환전 지연, 상품 거래 불가, lot export 누락이 있으면 dry-run
상태를 `BLOCKED`로 남기고 live 주문으로 진행하지 않는다.
