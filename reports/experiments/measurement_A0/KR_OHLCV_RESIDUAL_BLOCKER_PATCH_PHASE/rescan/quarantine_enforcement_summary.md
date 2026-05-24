# KR-OHLCV Quarantine Enforcement A0 — Summary

Date: 2026-05-23  
Scope: measurement-layer A0 only. Audit-only. **No patches.**

## Headline numbers

- Files scanned (.py only): **244** across `src/`, `research/`, `scripts/`, `configs/`, `paper_trading/`, `reports/`.
- Callsites recorded: **1088**.
- Distinct columns referenced: **43**.
- Classification: PASS=72 / GUARDED=352 / MISSING_GUARD=95 / INVALID_ROW_LEAK=51 / AMBIGUOUS=0 / NOT_APPLICABLE=518.
- Defect candidates (INVALID_ROW_LEAK + MISSING_GUARD): **146**.

## Callsite classification per category

| file_category | total | PASS | GUARDED | MISSING_GUARD | INVALID_ROW_LEAK | AMBIGUOUS | NOT_APPLICABLE |
|---|---:|---:|---:|---:|---:|---:|---:|
| audit | 518 | 0 | 0 | 0 | 0 | 0 | 518 |
| backtest | 10 | 0 | 5 | 2 | 3 | 0 | 0 |
| data | 68 | 0 | 33 | 35 | 0 | 0 | 0 |
| entry_point | 288 | 0 | 283 | 3 | 2 | 0 | 0 |
| features | 63 | 0 | 25 | 10 | 28 | 0 | 0 |
| ops | 4 | 0 | 0 | 0 | 4 | 0 | 0 |
| scripts | 24 | 0 | 5 | 19 | 0 | 0 | 0 |
| strategies | 41 | 0 | 1 | 26 | 14 | 0 | 0 |
| utils | 72 | 72 | 0 | 0 | 0 | 0 | 0 |

## Top columns by callsite count

| column_name | callsites |
|---|---:|
| `KRX종가` | 200 |
| `daily_return` | 115 |
| `시가` | 98 |
| `종가` | 96 |
| `거래대금추정여부` | 82 |
| `수급금액추정여부` | 60 |
| `거래대금추정` | 56 |
| `동적유니버스포함` | 37 |
| `시가총액추정` | 33 |
| `고가` | 27 |
| `저가` | 25 |
| `외국인순매수금액추정` | 23 |
| `기관순매수금액추정` | 21 |
| `거래량` | 17 |
| `kospi_foreign_net` | 16 |
| `adj_close` | 16 |
| `kospi_institution_net` | 15 |
| `Change` | 13 |
| `외국인순매매량` | 12 |
| `기관순매매량` | 10 |

## ALLOW_WITH_GUARD roll-up

- ALLOW_WITH_GUARD columns (per P0-1): **66**.
- Outside-audit consumer with DEFECT (LEAK or MISSING_GUARD): **18**.
- Outside-audit consumer with GUARDED state: **0**.
- Referenced only in audit/reports build context (no downstream consumer): **6**.
- ALLOW_WITH_GUARD columns with NO callsite anywhere: **41**.

Per-column detail in `allow_with_guard_usage_audit.csv`.

## Defect ledger summary

- All callsites classified as `INVALID_ROW_LEAK` or `MISSING_GUARD` are recorded in
  `invalid_row_leak_defect_ledger.csv` with `QENF_NNNNN` IDs.
- Severities: `INVALID_ROW_LEAK = high` / `MISSING_GUARD = medium`.
- Severity reflects audit risk, not patch priority. **No patches applied.**

## Kill-gate evaluation

Referee kill gates evaluated against the inventory:

- **Downstream path uses invalid OHLCV without guard?** YES — 51 LEAK + 95 MISSING_GUARD callsites; see defect ledger
- **OHL=0 / close>0 rows treated as valid price observations?** Cannot be proven by
  static scan alone. The defect ledger flags every callsite that derives a price /
  return-like value without a guard within ±5 lines.
- **Halt / suspension inferred from invalid OHLCV?** Pending — searched for code that
  binds `tradable_state` to OHLCV without consulting `listing_status_events.csv`.
  See defect ledger entries on `tradable_state`.
- **ALLOW_WITH_GUARD field used without documented guard?** See `allow_with_guard_usage_audit.csv` —
  18 ALLOW_WITH_GUARD columns currently have outside-audit defect callsites.
- **Any return / alpha / NAV / Sharpe / strategy metric produced?** Not in this audit run.
- **Any strategy testing started?** No.

## Hard locks (continuing)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / production / paper / P08 / live.
- No invalid OHLCV row treated as valid.
- No ALLOW_WITH_GUARD use without documented guard.
- No strategy reopen.
- No patches implemented (this phase is audit-only).

## Cross references

- `quarantine_enforcement_referee_lock.md` (Output 1)
- `invalid_ohlcv_row_contract.md` (Output 2)
- `downstream_ohlcv_usage_inventory.csv` (Output 3)
- `allow_with_guard_usage_audit.csv` (Output 4)
- `invalid_row_leak_defect_ledger.csv` (Output 6)
- `required_patch_register.md` (Output 7)
- `downstream_blockers_after_quarantine_a0.md` (Output 8)
