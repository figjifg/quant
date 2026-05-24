# Panel vs Official Reconciliation Summary

Date: 2026-05-24  
Phase: KR-LISTED-UNIVERSE-COVERAGE-A0

## Headline

- Official universe (monthly snapshots): **3653** unique tickers ever listed
- Union of repo panel tickers: **925** unique tickers
- Matched (in both): **925**
- Panel-only (panel has ticker but official does NOT): **0**
- Official-only (official has ticker but no panel covers): **2728**

## Per-panel reconciliation

| panel | matched_to_official | panel_only_vs_official |
|---|---:|---:|
| `kiwoom_2010_2016` | 713 | 0 |
| `dynamic_top100_2017_2024` | 840 | 0 |
| `dynamic_top100_2018_2024` | 815 | 0 |
| `krx_2025_2026` | 538 | 0 |

## Interpretation

- `panel_only_vs_official > 0` indicates panel tickers that the monthly KRX
  snapshots did NOT capture. Most likely causes:
  1. Ticker listed AND delisted within a single calendar month (would miss
     the monthly snapshot in both directions).
  2. Vendor mis-coded ticker.
  3. KONEX or other market-segment ticker (excluded from this scope).
  4. Pre-2010 listing that delisted before first snapshot.
- `official_only` indicates tickers KRX listed during the audit window but
  the repo's dynamic_top100 selection never included them (low-liquidity
  names). This is the survivorship blind spot.
- The size of `official_only` is the headline indicator of how survivor-biased
  the panel is.

## Survivorship implication

Repo panel = `union_panel_size` ≪ official `official_universe_size`. The
dynamic_top100 panels include only liquid names; delisted small caps are
absent. **Survivorship-safe claim cannot be made** from panel data alone.
See `survivorship_safety_assessment.md` for the full assessment.

## Hard locks (preserved)

- No survivorship-safe claim authorised yet.
- No strategy testing.
- No execution simulation.
