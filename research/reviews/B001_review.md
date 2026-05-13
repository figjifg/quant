# Review — B001 (Market-cap-normalized ranking)

## Verdict
**kill** — the ranking switch successfully shifts trade composition
toward smaller caps (mechanism check passed), but at a severe alpha
cost (net dropped −79 % vs A002). The most important finding is
**not** that B001 fails: it is that **A002's alpha is largely a
size factor in disguise**.

## One-line conclusion
거래대금 정규화는 결과적으로 시가총액 큰 종목을 골라줬고, 그 size
효과가 A002 알파의 큰 부분이었다. 시가총액 정규화로 작은 종목으로
옮기면 같은 신호도 거의 통하지 않는다.

## 4 success criteria — pass / fail

| # | Criterion | Result | Pass |
|---|---|---:|:-:|
| 1 | OOS median entry mcap of (A) ≤ (B) − 30 % | **−73.7 %** | ✓ |
| 2 | OOS net (A) ≥ (B) − 0.05 | (A) +0.143 vs (B) +0.688 → −0.545 | ✗ |
| 3 | OOS hit_rate (A) ≥ (B) − 0.02 | 0.439 vs 0.493 → −0.054 | ✗ |
| 4 | trade_count (A) ≥ 50 AND (B) ≥ 50 | both 205 | ✓ |

Kill criterion 1 (`net (A) < net (B) − 0.10`) triggered → `kill`.

## Diagnostic — trade-composition shift

`trade_mcap_composition.csv` shows the shift is consistent across all
years (median entry mcap, in 조 KRW = trillion KRW):

| Year | A002 cap_only | B001 (mcap-normalized) | Shift |
|---|---:|---:|---:|
| 2018 IS | 4.21 | 2.25 | −47 % |
| 2019 IS | 5.71 | 3.00 | −47 % |
| 2020 IS | 4.61 | 2.05 | −56 % |
| 2021 IS | 8.07 | 1.58 | −80 % |
| 2022 IS | 6.49 | 1.72 | −74 % |
| 2023 OOS | 7.69 | 2.17 | −72 % |
| 2024 OOS | 9.75 | 2.25 | −77 % |
| 2025 OOS | 9.30 | 2.68 | −71 % |
| 2026 OOS | 13.35 | 5.69 | −57 % |
| All IS | 5.94 | 2.05 | −65 % |
| **All OOS** | **9.21** | **2.42** | **−73.7 %** |

Mechanism confirmed: the ranking metric is **the** source of size
concentration. Universe alone (Top 100 by 거래대금) doesn't explain
it — switching the ranking changes the size profile by ~2.5–4×
across every year.

## Reading the numbers — what we actually learned

This is one of the more informative experiments in the project, even
though it failed its own success criteria.

1. **A002's alpha is size-loaded.** When forced into smaller caps
   within the same universe, OOS net dropped from +0.688 to +0.143.
   The signal still works (B001 is positive, not negative), but its
   pure-signal contribution is only ~+0.14 OOS over 3+ years — much
   weaker than the +0.69 we thought we had.
2. **Where the missing alpha lives**: the +0.69 − 0.14 ≈ **+0.55**
   "extra" return in A002 over 3+ years OOS is the **size factor
   premium** in our universe — large caps in a chase-buy environment
   outperform smaller caps when both are chosen by foreign+
   institutional flow signals. That premium may be real and
   persistent, or it may be specific to 2023–2026 KR market regime.
3. **Hit rate barely moved (49 → 44 %)** despite return collapse.
   This means win-size shrunk a lot more than win-frequency. Same
   percentage of trades wins, but the winners are smaller in
   smaller-cap names.
4. **The cost structure didn't save B001 either** — trade_count
   and turnover are similar to A002 (205 vs 205, turnover both
   around 40+), so the gap is in per-trade economics, not in
   how many trades or how much we paid.

## Implications for the project

We need to **honestly re-rate A002's alpha**.

A002 cap_only OOS +0.688 = roughly:
- ~+0.14 from "flow signal works in foreign+institution chase-buy"
- ~+0.55 from "large-cap exposure was good in 2023–2026 KR market"

If you ran A002 in a different regime where large caps underperform,
you'd get ~+0.14, not +0.688. That's a much weaker headline.

This is not a kill of A002 — it's a re-calibration of expectations.
The signal still has a small positive edge net of costs, just much
smaller than A002's apparent number suggested.

## Possible biases

- look-ahead: low. 시가총액(T) at signal date only; tests confirm
  prior-row safety.
- survivorship: same as A 가족.
- data snooping: low. Single-point parameters, pre-frozen.
- multiple testing: low. One headline + one direct baseline (A002
  replay). The trade_mcap_composition diagnostic is purely
  descriptive.
- estimate-flag noise on 시가총액추정: present (some rows have
  estimated mcap). Not filtered — see Expected Weaknesses in ticket.
  Unlikely to dominate.

## Most likely failure mechanisms

Several non-exclusive explanations for why smaller-cap signal is
weak:
1. **Foreign+institution flow into small caps is more noise**: large
   caps are where foreigners actually deploy capital meaningfully.
   Small-cap "foreign buying" can be 1-2 funds and erratic.
2. **Small-cap forward returns are noisier**: 20-day forward return
   of a small cap has higher variance, so even with a real edge,
   win-size is smaller after losses.
3. **Liquidity penalty**: smaller caps cost more to enter/exit
   relative to their notional (slippage is bigger fraction); our
   fixed 5 bps slippage may understate this for smaller names.
4. **Cap=20 day may be too long for small caps**: short-term effects
   may dissipate faster in small caps. Longer hold dilutes signal.

## What survived

- **Mechanism check**: the ranking metric is the size-source. This
  is a clear factual finding usable in any future experiment.
- **B001 module + tests**: 96 passing tests, A-family fully
  preserved. Engine, universe, baselines, costs, metrics all
  unchanged.
- **Diagnostic infra**: trade_mcap_composition.csv format works,
  decomposing trade composition by year. Reusable for future
  experiments.

## Next experiment direction

User's other proposal — **entry trigger (당일 vs 5일 평균)** — was
deferred from this round. It's now the natural next step:

**B002 candidate** — same A002 cap_only (large-cap-friendly ranking
preserved), add entry trigger: only enter when today's `fnv_1`
(외국인 매수금액 / 거래대금, 1일 비율) is **strictly greater than
the previous 5 days' average `fnv_5/5`**. Single new condition,
single direction (today is hotter than recent average).

Why this is interesting independently of B001:
- B001 showed the size factor matters. B002 doesn't fight that —
  it just adds a separate time-axis filter on top of A002.
- Tests whether a "fresh acceleration" entry beats "any-time
  positive flow" entry.
- New time scale (1-day vs 5-day) — different dimension from
  intensity (A004) or magnitude (A002 vs A004).
- Risk: if the trigger is too strict, trade count drops below kill
  threshold.

## Alternative next directions to consider

- **Re-do A002-style with smaller caps deliberately excluded**:
  e.g., require entry mcap ≥ some threshold. This would make the
  "A002 alpha is in large caps" claim explicit, but it locks the
  strategy into large-cap deployment, which has capacity but also
  more crowding.
- **Switch universe**: instead of Top 100 by 거래대금, try Top 50
  or top by some other criterion. This is a more invasive change
  and would require careful spec re-write.

I lean toward **B002 = entry trigger** as the cleanest next test
because it is a single additive change and doesn't require
re-thinking the universe.

## Do not do next

- Do **not** try a different normalization basis (log mcap, sqrt
  mcap, 5-day-avg mcap) just to see which works. That's parameter
  hunting on a hypothesis we now have evidence against.
- Do **not** combine B001's mcap-normalized ranking with the entry
  trigger in a single experiment. The user already cautioned against
  multi-variable experiments; B001 has shown the ranking shift hurts
  alpha materially, so combining adds confusion not clarity.
- Do **not** promote B001 even though some criteria passed —
  passing 1, 4 with 2, 3 failing badly is not a "revise" candidate.
  The mechanism finding is useful, but the strategy variant itself
  is rejected.
