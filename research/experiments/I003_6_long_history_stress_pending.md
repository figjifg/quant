# I003.6 — Long-history Stress Pending

Status: COMPLETED

## Reason

Long-history US-core stress audit completed from host-collected ETF data.
I003.6 is a proxy validation only: H001 is not reproduced before 2010, and
P08_IEF30 is represented as SPY 40 / QQQ 30 / IEF 30.

## Result Summary

- Reference output: `reports/experiments/I003_6_long_history/`.
- Full-history proxy result: CAGR 10.93%, Sharpe 0.84, MDD -37%.
- The proxy Sharpe 0.84 was the strongest long-history Sharpe among the tested SPY, QQQ, SPY/QQQ 50/50, and IEF comparators.
- Dot-com stress confirmed P07-style catastrophic QQQ concentration risk: QQQ buy-hold had about -41% CAGR and -83% MDD in 2000-2002. The P08_IEF30 proxy is only available from 2002-07 and passed its available dot-com slice with about +5.5% CAGR and -13% MDD.
- GFC 2008-2009 is the main warning: P08_IEF30 proxy showed about -2.5% CAGR and -35% MDD, much deeper than the 2010-2026 P08_IEF30 backtest MDD.
- 2022 rate shock reconfirmed dual-loss risk: P08_IEF30 proxy lost about -22% with about -25% MDD, while Treasury ETFs also lost money.

## Verdict

P08_IEF30 long-history validation passed with a GFC drawdown warning. This
strengthens P08_IEF30 as a formal candidate, but does not remove the remaining
paper-tracking, production-cost, FX/tax/execution, and tax-professional gates.

## Host 복귀 후 절차

Completed:

1. `.venv/bin/python scripts/host_data_collection.py` 실행.
2. Long-history CSV 존재 확인:
   - `research_input_data/inputs/global_etf/yf_QQQ_long.csv`
   - `research_input_data/inputs/global_etf/yf_SPY_long.csv`
   - `research_input_data/inputs/global_etf/yf_IEF_long.csv`
   - `research_input_data/inputs/global_etf/yf_TLT_long.csv`
   - `research_input_data/inputs/global_etf/yf_GLD_long.csv`
3. `research_input_data/docs/DATA_CATALOG.md`에 새 데이터 파일 기록.
4. `.venv/bin/python -m src.audit.i003_6_long_history` 실행.

## Data Collection

- Script: `scripts/host_data_collection.py`.
- Guide: `docs/host_data_collection_guide.md`.
- yfinance: QQQ (1999-03), SPY (1993-01), IEF (2002-07), TLT, GLD 다운로드.
- 저장: `research_input_data/inputs/global_etf/yf_*_long.csv` (별도).
- yfinance 호출은 `auto_adjust=True`를 사용한다.
- pykrx, EM, sector, crypto, FX backlog 데이터도 같은 script에서 함께 수집한다.
- 대체 source 우선순위: yfinance > Stooq > official ETF data > index proxy.

## Audit Script

- Script: `src/audit/i003_6_long_history.py`.
- 데이터가 없으면 명확한 `FileNotFoundError`를 발생시킨다.
- 결과 위치: `reports/experiments/I003_6_long_history/`.
- Test policy: 데이터가 있을 때만 실행한다. 데이터가 없으면 skip하고
  "host data collection not run yet"을 사유로 남긴다.

## Long-history US Core Stress

- QQQ, SPY, IEF buy-hold (long-history).
- SPY/QQQ 50/50, QQQ/SPY/IEF combinations.
- P08_IEF30 proxy (H001 unavailable before 2010; US-core proxy only).
- 2000-2002 dot-com, 2008 GFC, 2022 rate-shock 비교.

## Result Labeling

- "Pre-2010 result = NOT full P08_IEF30 replication"
- "US-core stress approximation"

## Decision Gate

- P08_IEF30 proxy did not show P07-style catastrophic behavior in its available dot-com slice.
- Gate result: PASS with GFC -35% MDD warning.
- Next: maintain P08_IEF30 as strengthened candidate and continue paper tracking, I005 production-style validation, and tax-professional review.
