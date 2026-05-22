# Research Freeze v2 To Q-family Handoff

Status: handoff memo

## Context

Research Freeze v2 closed the previous alpha-search phase and protected
`P08_IEF30` as the frozen formal candidate. Q-family is allowed only because
the user supplied an explicit new data source and hypothesis:

> Q-family = US 개별주 fundamental sleeve. P08_IEF30 와 완전 분리.
> Q000 = PIT data audit 가장 먼저, gate. PIT 데이터 부족 시 Q-family 멈춤.
> SEC EDGAR companyfacts API 활용. survivorship-free universe 필수.
> 첫 composite = Quality (ROIC + FCF margin - leverage) + Value (FCF yield + earnings yield) + Shareholder Yield (buyback + dividend - dilution).
> 한국 X (F-family 종목 단위 가격/수급 랭킹 이미 실패).

This qualifies as a reopening under the mission rule: clear new data source /
hypothesis.

## Separation Enforcement

- `P08_IEF30` remains frozen.
- D013, H001, and `P08_IEF30` strategy logic must not be modified.
- Q-family is a separate US individual-stock fundamental sleeve.
- Q-family results do not directly promote, replace, or alter `P08_IEF30`.
- Q008 may evaluate portfolio combination only after Q000-Q007 gates pass.

## Gate Logic

Q000 is first and mandatory. It must verify:

- Filing-date based point-in-time SEC fundamentals.
- Stable enough XBRL tag mapping.
- Survivorship-free historical universe feasibility.
- Dividend, buyback, and share-count timestamp accuracy.
- Split, merger, ticker-change, and delisting handling.

If Q000 fails, stop Q-family individual-stock research and use ETF proxy
diagnostics only: `QUAL`, `VLUE`, `MTUM`, `USMV`, `SCHD`, `COWZ`.

## Main Risks

- Survivorship bias: using current S&P 500 constituents for past tests.
- Look-ahead bias: using financial statements before their SEC filing date.
- Overfitting: searching many factor combinations or sleeve weights for the
  highest Sharpe.

## Implementation Boundary

This handoff authorizes only the pre-registered Q-family documents and the
host-run Q000 audit script. It does not authorize backtests, strategy changes,
engine changes, or modification of frozen D/H/P-family results.

