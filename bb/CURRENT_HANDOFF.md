# PROJECT HANDOFF — current state for Bull / Bear (neutral)

Version: 2026-05-28. Maintained by the Executor (Claude Code). This is the "project
handoff" the role briefs reference. It supplies BOUNDARIES + FACTS only.

> NEUTRALITY (read first): This handoff does NOT prescribe the next strategy, market,
> family, or mechanism. Per the Bull and Bear role briefs, do NOT let this handoff bias
> the lab toward any predetermined direction. The **lab scope** (what to explore this
> round) is supplied separately by the user/Referee, not by this file. If no lab scope is
> given, ask for it — do not invent one.

## 1. Frozen production boundary (do NOT touch / propose changes to)

- Production candidate (frozen): **P08_IEF30 = SPY 29% / QQQ 21% / H001 20% / IEF 30%**.
  Documentation-complete / live-ready (U000–U003 playbook/dry-run/drawdown/owner's-manual,
  V000 adversarial PASS, N006 shadow rule). No weight changes, no re-optimization.
- Surviving sleeves inside P08: **D013** (Korean macro gate) + **H001** (Korean carry).
  Defensive diagnostic shadows: N002-B (cash 10%), N001-B (GLD 10%).
- All research below is DIAGNOSTIC-ONLY and separate from this production track.

## 2. Closed-family boundaries + documented reopen conditions (do NOT repackage)

From `docs/z000_failure_register.md` (honest record). Reopening requires a NEW verifiable
mechanism — NOT the same idea repackaged.

| Family | What it was | Why it closed | Reopen needs |
|---|---|---|---|
| E014 | KR sector RS/breadth top4 | PIT sector membership absent (look-ahead/survivorship) | PIT sector daily + delisting-safe + regression test |
| F | KR stock ranking (flow/RS/liquidity) | net edge insufficient (cost/turnover/noise/decay) | better PIT universe + total return + execution cost + robust IC + random control |
| G | slow risk overlay (MDD cooldown/stress) | cut returns / worsened timing | only as explicit risk-budget tool, not alpha |
| K | US sector rotation | marginal / regime-dependent / tax | defensive role + explicit stress budget |
| J | EM equity sleeve | static=backlog, momentum=catastrophic | clear role + long history + stress budget + cost |
| Q | US quality/value/shareholder-yield | direct=survivor bias, ETF proxy=marginal | survivorship-safe US PIT universe + PIT fundamentals |
| R | KR shareholder-return events | title-only extraction insufficient | DART **body** parser + event timestamp + amount normalization |
| S | KR short-horizon mean reversion | strong result = measurement artifact | W001 KR engine repair + corrected smoke test |
| X-ETF | tactical ETF (14-ETF momentum/rotation) | no edge over static / simpler shadows | new verifiable mechanism + strict pre-registered gate + beat simple shadow |
| X-KR | KR pair/residual mean reversion | no net edge; KR long-short borrow unrealistic | borrowable KR universe + PIT residual + NEW mechanism (not plain cointegration) |

Hard rule: Korean simple standalone alpha (E/F/G/R/S) + X-KR pair are ALL closed; only
D013/H001 sleeves survived.

## 3. Known failure modes to pre-empt

Look-ahead (signal vs execution timing), survivorship (delisted/halted universe),
corporate-action/unadjusted prices, calendar/tradability, cost+tax+turnover killing
short-horizon edges, regime/year/sector concentration, price-momentum/market-beta
contamination, multiple-testing/data-snooping, capacity/execution, measurement artifacts
(entry/exit alignment, filtered-row execution, per-trade leverage, invalid random control).

## 4. Available infrastructure / data (FACTS — availability ≠ greenlight)

On disk now (a NEW Strategy Card must still prove PIT-feasibility + a new mechanism):
- **KR equity panels** (dynamic top-100, 2010–2026): heavily audited (OHLCV quarantine,
  KRX calendar, listed-universe coverage) via the measurement-layer A0 program.
- **KR market flow** (foreign/institution; NOTE: vendor-ESTIMATED amounts, documented).
- **KR PIT sector daily mapping 2010–2026** (`data/processed/stock_*_pit*.csv`) — exists.
- **KR total-return (dividend-adjusted) 2018–2026** (W000 item 2, yfinance proxy; caveats:
  research-grade proxy, 22 delisted no_data, pre-2018 not covered).
- **KR securities-lending / borrow-balance 2018–2026** (W000 item 6, DATA.GO.KR; caveat:
  BALANCE side only — no borrow fee / short-rebate / restriction list / buy-in).
- **Global ETF** (SPY/QQQ/IEF etc.) — P08 inputs, daily-NAV standardized + V000-stressed.
- **Macro features** (FRED/BOK): USDKRW, KR & US rates, VIX, DXY, JPY, JP10Y, copper,
  brent, KR CPI/CLI/exports, US CPI/M2/PPI/unrate, KOSPI breadth, S&P emini (KST). The
  C-family (C001–C020) already mined these heavily → produced D013/H001.
- **Global index futures 1-minute** (Nikkei/Nasdaq/Russell, 2018–2026) — present; NO
  dedicated quality audit yet (treat as unvalidated until audited).
- **US equity prices/fundamentals** (SEC EDGAR) — for the closed Q-family; survivorship not
  guaranteed (no survivorship-safe US PIT universe yet).
- **OpenDART KOSPI disclosures** (KR-status measurement) — in DECIDED STANDBY; residuals are
  mostly genuine absence/relativity; do not assume the DART body parser exists.

Reopen-condition status note (NEUTRAL — not a recommendation): the recent data work
satisfied some closed-family DATA preconditions (F: total return now exists; E014: PIT
sector exists; X-KR: borrow balance exists). Data-readiness removes ONE blocker only; the
hard rules still require a NEW mechanism, and Bear must still audit any such card on its
own merits.

## 5. Audit standards (every Strategy Card / Bear Review is held to these)

Audit-first 12 items: data lineage, point-in-time availability, survivorship safety,
corporate-action handling, calendar/tradability, daily NAV, no implicit leverage,
benchmark alignment, random/placebo control, concentration/top-contributor, cost/tax/
turnover, capacity/execution. Cost/tax MUST be modeled (no zero-cost except as a labeled
diagnostic). Nothing is a production or paper candidate at this stage — diagnostic only.

## 6. What this handoff does NOT contain

- The lab scope (user supplies it).
- A recommended next family / mechanism (forbidden — see neutrality note).
- Approval for any test, download, production change, or closed-research reopening (those
  are separate user + Referee decisions; the Executor runs tests only after approval).
