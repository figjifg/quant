# W001 v2 — Korean Long-Short Residual Engine Certification

## Status

**Backlog only. Not active.**

Build W001 v2 **only if** future user explicitly reopens long-short Korean equity research. There is no current ticket, no current development, no scheduled work.

## W001 v1 Certification Scope (current)

Certified for:
- Korean **long-only sleeve** research
- Daily NAV (long-only)
- KRX calendar / tradability
- Adjusted price / corporate action handling
- Random / placebo engine (long-only)
- Sanity checks (long-only)

**Not certified for:**
- Long-short residual returns
- Borrow availability / short-sale restrictions
- Borrow fee / short rebate
- Per-leg leverage cap
- Margin and financing
- Pair-level PnL lineage
- Gross / net exposure caps
- Forced buy-in / no-borrow handling
- Impossible-return detector for long-short synthetic returns
- Long/short legs separately reconciled daily NAV

## Why W001 v2 Is Backlog (Why Not Build Now)

1. X-KR001 is already closed by pre-registered kill gates (12/12 turnover/tax/slippage, 11/12 two-subperiod, 8/12 after-cost Sharpe < 1).
2. Even with a corrected long-short engine, Korean long-short production realism is low because of structural short/borrow restrictions on KRX.
3. New alpha research ROI is low. Audit-first framework reached 6/6 catches across 6 closed families.
4. Current project need is P08_IEF30 live-readiness, not engine expansion.

## Required Scope If W001 v2 Is Ever Built

| Layer | Requirement |
|---|---|
| Borrow universe | Per-date borrowable set (KRX 대차거래 가능 종목, 사전 등록 필수) |
| Borrow cost | Borrow fee / short rebate by ticker × date |
| Short-sale rules | Up-tick rule / 공매도 제한 / 금지 종목 |
| Margin / financing | Per-leg cost, gross/net exposure cap |
| Leverage cap | Per-trade and per-portfolio leverage detector |
| PnL lineage | Long leg vs short leg separately reconciled |
| Forced buy-in | Recall / no-borrow event handling |
| Sanity | Impossible-return detector for synthetic long-short returns |
| NAV | Daily NAV with long-leg and short-leg sub-NAV |

## Reopen Conditions for W001 v2 Work

All four conditions must be true:

1. User explicitly reopens long-short Korean equity research (no automatic restart).
2. A new audit-first verifiable hypothesis exists (not re-packaging X-KR001 / S-family / closed family).
3. KRX borrow data source is identified and accessible.
4. P08_IEF30 production hardening is not blocked by this work.

## Hard Rule

No long-short Korean equity strategy may be tested or backtested until W001 v2 is completed and audit-certified. W001 v1 long-only engine **must not be used** for long-short residual research.

## Reference

- X-KR001 closure: `x_lab/x_kr/x_kr001_results/report.md`
- X-KR001 A0 sanity 4 FAIL = long-short residual layer artifact evidence
- X-Lab FULL closure: `x_lab/final_status.md`
- Failure register: `docs/z000_failure_register.md` (X-KR001 entry)
