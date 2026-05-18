# P004 Paper Trading Protocol

This report artifact mirrors `docs/paper_trading_protocol.md`.

P004 does not run a live or simulated trade backtest. It defines the quarterly D013 paper-trading operating loop:

- generate the quarter-end D013 signal after KRX close;
- record `signal_date`, `regime_on`, `composite`, top-5 tickers, and intended equal weights under `signals/YYYY-Q.json`;
- record intended versus actual execution prices, slippage, and quarter-end portfolio value under `executions/YYYY-Q.json`;
- evaluate only after four completed quarters.
