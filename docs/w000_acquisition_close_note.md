# W000-DATA-INFRASTRUCTURE-ACQUISITION — Close Note

## Final status (recorded exactly)

CLOSED AS W000 DATA INFRASTRUCTURE ACQUISITION COMPLETED FOR ITEMS 1/2/6 / ITEMS 3/4
DEFERRED BY USER DECISION / ITEM 5 DART PARSER STANDBY PRESERVED / NO STRATEGY OR
EXECUTION REOPENED

Referee formal close verdict (2026-05-28, via file-mode relay): Select A (close the W000
track at the current accepted state) + preserve D (no strategy / backtest / execution /
paper / live / P08 weight / closed-research reopening).

## User decision basis

The user made the final call: **close W000 at items 1/2/6 complete; defer items 3/4/5.**
Rationale (user-accepted): the substantive data gaps are filled (item 2 + item 6 acquired
& validated; item 1 already on disk); items 3/4 are low-value (feed closed research) and
need a source decision that can wait; item 5 stays in measurement-layer standby. Closing
brings the project to a consistent resting point (P08 live-ready / measurement standby /
W000 closed-at-1/2/6).

## Accepted commit references

`88e4da0` (open track + plan) / `b1df5e4` (audit-first verified status) / `ee5a189`
(item 2 acquire) / `2778926` (item 6 acquire) / `b5f83d5` (doc-state correction).

## Accepted item states + caveats

1. **Item 1 — PIT sector membership / daily mapping:** already DONE on disk before W000
   close; no acquisition needed. The earlier "2018 gap" was a stale/sample-based false
   alarm (reading only the first 200k date-sorted rows).

2. **Item 2 — Korean total-return data:** acquired + validated at `ee5a189`. Source:
   yfinance / Yahoo total-return proxy. Accepted as DATA INFRASTRUCTURE ONLY. Caveats:
   research-grade proxy (not an authoritative vendor feed); 22 delisted no_data tickers
   remain fail-closed; pre-2018 not covered. Lineage:
   `docs/w000_korean_total_return_lineage.md`; raw under gitignored
   `data/acquired/w000_korean_total_return/`.

3. **Item 6 — KRX securities-lending / borrow-balance data:** acquired + validated at
   `2778926`. Source: DATA.GO.KR 금융위 주식대차정보. Accepted as DATA INFRASTRUCTURE ONLY.
   Caveats: balance / contract / repaid shares only — no borrow fee, no short-rebate, no
   short-sale restriction list, no buy-in events; those residuals need a separate future
   source decision if ever pursued. Lineage: `docs/w000_kr_borrow_lineage.md`; raw under
   gitignored `data/acquired/w000_kr_borrow/`.

4. **Item 3 — execution data:** DEFERRED by user decision; not acquired; likely infeasible
   without broker fills / a historical quote source; may be reopened only by a new user
   decision + source decision.

5. **Item 4 — survivorship-safe US PIT universe:** DEFERRED by user decision; not acquired;
   needs a chosen PIT membership dataset if ever pursued; may be reopened only by a new
   user decision + source decision.

6. **Item 5 — DART body parser / KR-status measurement:** STANDBY preserved; do not reopen
   here. Any DART parser / KR-status measurement work requires a separate user + Referee
   decision (see the measurement-layer DECIDED STANDBY).

## Hard locks (preserved)

- No `data/raw/` edits.
- No `research_input_data/` edits.
- Acquired raw artifacts remain under gitignored `data/acquired/**`.
- No API key printed, committed, or logged (keys read in-process per call).
- No P08_IEF30 weight change.
- No strategy / backtest / execution / paper / live claim.
- W000 Hard Rule remains active: acquiring data does NOT reopen Q-family, sector research,
  event research, Korean long-short research, or KR-status measurement work.
- The accepted W000 datasets (items 2 & 6) are lineage/coverage evidence ONLY until a
  separate future ticket approves any use.

## Close housekeeping

- `docs/next_actions.md`: W000 moved Active → Closed/Frozen; Active is empty.
- This close note added.
- No next W000 phase opened.
- No downloads / API calls / data-acquisition scripts / acquired-data modification /
  strategy / backtest / execution work performed in this close pass.
