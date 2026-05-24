# Executable-Status Taxonomy

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0

## Canonical status labels

| label | definition | official source coverage | acceptable proxy fallback |
|---|---|---|---|
| `executable` | Trading was possible on date d (no event, listed, not surveillance/limit-locked) | KRX official | NONE (cannot be inferred from data presence alone) |
| `full_day_suspension` | Stock was suspended for the entire trading day | S3 KRX status events: `suspension_related` | tradable_state=`true_suspension` (proxy; requires S3 backing) |
| `intraday_halt` | Stock was halted within the day (resumed same day) | KOSCOM / KRX intraday log — NOT in repo | NONE — out of scope |
| `resumption_day` | Day after a suspension when trading resumed | S3 KRX `resumption_related` | NONE (proxy unreliable) |
| `delisting_transition` | In the delisting process (post-decision, pre-permanent) | S3 KRX `delisting` + W001 v2 terminal | tradable_state=`delisting_transition` (proxy) |
| `liquidation_trading` | 정리매매 period | S3 KRX `liquidation` (rare; only 1 in dataset) | NONE |
| `managed_stock` | 관리종목 (managed stock for risk reasons) | S3 KRX `managed` | NONE (pykrx managed-list not available) |
| `investment_attention` | 투자주의 | S3 KRX `investment_alert` subset | NONE |
| `investment_warning` | 투자경고 | S3 KRX `investment_alert` subset | NONE |
| `investment_danger` | 투자위험 | S3 KRX `investment_alert` subset | NONE |
| `short_term_overheated` | 단기과열 | S3 KRX (regex on `단기과열`) | NONE |
| `upper_limit_lock_candidate` | 상한가 lock (OHLCV pattern) | NONE — KRX limit log not in repo | tradable_state=`limit_lock_candidate` (proxy) |
| `lower_limit_lock_candidate` | 하한가 lock (OHLCV pattern) | NONE | tradable_state=`limit_lock_candidate` |
| `panel_absent_or_not_in_universe` | Stock not in repo panel for that date (NOT proof of non-tradability) | n/a | tradable_state=`panel_absence` |
| `data_missing` | Source data not available; status genuinely unknown | n/a | tradable_state=`data_missing` |
| `unknown` | Cannot determine — MUST NOT be treated as executable | n/a | (default for un-evidenced cases) |

## Critical separations

- `panel_absent_or_not_in_universe` is **NOT** the same as non-tradable. The
  stock may have been tradable but not selected by vendor dynamic_top100.
- `unknown` MUST remain unknown. Downstream code MUST NOT assume executable
  when status is unknown.
- `proxy_only` status (from tradable_state) MUST be flagged separately from
  `official` status (from S3 / DART).
- OHLCV signatures (OHL=0/close>0, zero volume, etc.) are **supporting
  evidence only**. They DO NOT prove suspension or halt — see the invariant
  contract in `KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/invalid_ohlcv_row_contract.md`.

## Status confidence levels

| confidence | meaning |
|---|---|
| `official` | S3 KRX status event directly supports the label |
| `semi_official_derived` | W001 v2 derivation from S3 (consolidated) |
| `proxy` | W001 v2 tradable_state assignment |
| `unsourced` | inferred from OHLCV pattern alone — INSUFFICIENT |
| `unknown` | no evidence |

## Hard locks

- Downstream code MUST consult source confidence before any execution-time
  decision.
- `unsourced` and `unknown` MUST trigger fail-closed gates, not silent
  assumption.
- `panel_absent_or_not_in_universe` MUST NOT be promoted to any tradability
  conclusion.
