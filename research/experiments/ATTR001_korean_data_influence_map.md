# ATTR001 — Korean Equity Data Influence Map (PRE-REGISTRATION)

Status: PRE-REGISTERED (locked before running). Diagnostic-only. Version 2026-05-28.
Authors: Executor (Claude Code) + Referee (Codex) design; user-authorized autonomous
diagnostic program ("fresh-start attribution; autonomous until all worthwhile data
processed; analyze but DO NOT discard bad/negative/no-influence results; preserve the full
map; keep audit-first validity").

## 0. Framing (what this is and is NOT)

- This is a **data INFLUENCE MAP**, not a strategy search. Output = per-signal × horizon ×
  regime influence, **preserved in full** (good, bad, negative, no-influence, data-gated).
- **No discard / no kill / no "recommendation".** A ranking, if produced, is an "influence
  map ranking", never a recommendation. Past family failure is NOT a veto; it is recorded
  as a caveat only.
- **Diagnostic-only.** Opens no strategy / backtest-for-deployment / paper / live / P08
  change. The frozen P08_IEF30 is untouched. Korean short leg is treated as a STATISTICAL
  spread only (not executable — no borrow/short infra).
- Universe is the **dynamic_top100 KR panel** → results are "influence WITHIN
  dynamic_top100", explicitly NOT generalized to "the Korean market".

## 1. Sample, universe, KR-specific data rules

- Sample: 2018-01-02 → latest panel date (~2026-05). Panels = existing dynamic_top100
  (the audited KR equity panels).
- Price: **`KRX종가` priority**; `종가` only as pre-NXT fallback. Post-2025-03-04 (NXT)
  rows: record price-source metadata. Open = KRX 09:00 `시가` (metadata-flagged).
- **Signal-time vs execution-time separation (hard rule):** all end-of-day data known at
  close of day T may only drive execution at T+1 or later. Flow (수급) is EOD → t+1 only.
  Macro/FRED/BOK/foreign-futures with ambiguous availability: lag ONE extra trading day.
- `거래대금추정여부 == True` rows: EXCLUDED from headline metrics; preserved as a separate
  diagnostic slice. `수급금액추정여부` is all-True (vendor estimated) → NOT a drop key,
  recorded as a universe-wide caveat.
- OHLCV quarantine (existing S1-S6 invalid-row contract) applied before signal construction.
- Liquidity buckets MANDATORY on every result: 20d avg traded value, market-cap bucket,
  거래대금추정여부.

## 2. Regime split (LOCKED a-priori — defined before any result is seen)

- **PRIMARY split:**
  - PAST = 2018-01-02 … 2021-12-30
  - PRESENT = 2022-01-03 … latest
  - Rationale: 2022 = simultaneous rates/USD/inflation/growth re-pricing regime shift;
    both halves have adequate length; more stable than a single 2025 policy boundary.
- **AUXILIARY regime tags (reported, NOT primary; 2025+ segments too short for strong
  claims):** short_sale_ban≥2023-11-06; short_sale_resumed≥2025-03-31; nxt≥2025-03-04
  (Nextrade); valueup≥2024-02-26. Plus per-year and rolling 2y/3y windows.
- Dates verified against FSC / Nextrade official + recent reporting (Referee, 2026-05-28).

## 3. Signal inventory (FEASIBLE-NOW — measured)

Each signal: single, standard construction (NOT novel alpha). All cross-section signals
are ranked within the daily universe. Expected direction is NOT pre-asserted (we measure,
not assume).

**A. Flow (cross-section):** foreign net-buy amount; institution net-buy amount; foreign &
inst net-buy SHARES; net-buy / traded-value ratio; net-buy / market-cap ratio; 1/3/5/20d
cumulative; change-rate; foreign−institution divergence. (EOD → t+1.)

**B. Price/volume (cross-section):** 1/3/5/10/20/60d momentum; short-horizon reversal
(1/3/5d); realized volatility (20/60d); traded-value change; volume/traded-value surge;
overnight gap; intraday (open→close) return.

**C. Sector (cross-section, PIT sector mapping):** sector relative strength; sector breadth;
stock's within-sector relative strength. (E014 PIT caveat attached; NOT vetoed.)

**D. Total return (cross-section, W000 item2 — yfinance proxy caveat):** dividend-inclusive
momentum (from `adj_close` RETURNS only — never the adjusted price LEVEL as a signal);
trailing dividend yield / post-ex-date uplift.

**E. Borrow balance (cross-section, W000 item6 — balance-only caveat):** borrow_balance /
shares-outstanding; 5/20d change-rate; price-down+borrow-up (pressure) and price-up+
borrow-down (cover) proxies. (NOT short fee / rebate / restriction.)

**F. Market / macro (NOT cross-sectional IC — same value all stocks → conditional eval):**
USDKRW, US short rate, KOSPI breadth, KOSPI200 futures, overnight/global index futures
(1-min futures flagged unaudited). Evaluated via: universe equal-weight forward-return
prediction; market-beta-adjusted return; conditional market return by signal quantile;
interaction with cross-section signals.

**G. Event / disclosure metadata (event-study, NOT body parser):** OPENDART KOSPI
disclosure parquet — event-presence by 접수일/제목/분류 only; rcept_dt+1 onward; title/date
caveat. NO body parser, NO effective-date extraction (those stay standby).

## 4. DATA-GATED (preserved in map, NOT measured this pass)

- KR fundamental factors (value / quality / shareholder-yield): no clean PIT KR fundamentals
  on disk; pykrx fundamental endpoint currently broken → status `data_gated`.
- Borrow fee / short rebate / short-sale restriction list / buy-in events: W000 item6
  residual → `data_gated`.

## 5. Forward-return labels (two, never mixed)

- **Prediction label:** close-to-close forward return over horizon h.
- **Executability label:** signal known at close T → enter T+1 open → exit after h days,
  cost-inclusive (§7). KR short leg NOT claimed executable; long-only top-decile is the
  executable view.
- Horizons h ∈ {1, 3, 5, 10, 20} KRX trading days.

## 6. Metrics

- **Cross-section signals:** daily rank-IC (signal_t vs forward return); mean IC, IC
  t-stat, IC hit-rate, per-year IC; decile spread Q10−Q1 net of cost; long-only top-decile
  excess return (executable view).
- **Market/macro signals:** equal-weight forward-return prediction; beta-adjusted; quantile
  -conditional market return; interaction with cross-section signals (NOT rank-IC).
- **Event signals:** event-study by event dummy / category; matched non-event control
  (same date / sector / cap bucket); t+1.
- **PRIMARY metrics (limited to 3, pre-locked):** (1) 5d rank-IC (or 5d conditional effect
  for market/macro); (2) 10d net decile spread (long-only excess for executability);
  (3) recent-regime (PRESENT) stability vs PAST. Everything else = SECONDARY, preserved.
- **Placebos (≥2 per signal):** within-date ticker permutation; date-block shuffle (and/or
  lagged placebo).
- **Multiple testing:** full signal × horizon × regime × metric list locked in THIS doc
  before running. Report q-value / FDR where p-values exist. NO "discovery"/"alpha"
  language — report effect size + stability only.

## 7. Cost model (minimum, applied to executability metrics)

commission 1.5 bps/leg + tax 20 bps on sell leg + slippage 5 bps/leg. (After-tax is the
project standard.) Zero-cost variant kept only as a labeled diagnostic.

## 8. Validity row-status labels (every result row carries one)

`measured_valid` / `measured_with_caveat` / `data_gated` / `validity_risk_annotated` /
`execution_not_claimed`. Validity problems (look-ahead risk, artifact, proxy) are ANNOTATED,
never used to discard a row.

## 9. Output schema (preserved influence map)

One row per (signal_id, family, horizon, regime, label, metric) with: value, t-stat/CI,
hit-rate, n, placebo_value, q_value(if any), liquidity-bucket breakdown available,
status_label, caveats, source, availability_time, formula_ref. Plus an "influence map
ranking" view (NOT a recommendation). Nothing dropped; data_gated rows present with reason.

## 10. Hard locks

PIT / no look-ahead; after-tax + cost on executability; no P08 weight change; no
production/paper/live; diagnostic-only; raw data (`data/raw`, `research_input_data`) not
modified; closed-family hard rules respected as CAVEATS not vetoes; no body parser / no
KR-status measurement reopen; preserve-all (no discard). Korean long-short = statistical
spread only, not executable.

## 11. Execution plan

1. Referee sign-off on this pre-registration.
2. Executor builds the sweep (reads existing panels + W000 + macro + sector + event data),
   runs all locked signals × horizons × regimes × metrics + placebos, writes the preserved
   influence-map artifact(s) under `reports/experiments/ATTR001_korean_data_influence_map/`.
3. Executor + Referee analyze the map (preserve-all; annotate validity). Report the map to
   the user. NO strategy opened from this; any follow-up is a separate user decision.
