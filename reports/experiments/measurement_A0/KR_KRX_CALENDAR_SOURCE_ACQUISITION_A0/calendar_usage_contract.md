# Calendar Usage Contract

Date: 2026-05-24  
Phase: KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0

## Future calendar usage rules

### Mandatory: official KRX calendar

Any future A0 / measurement-layer analysis that requires:

- a trading-day calendar,
- a next-trading-day mapping,
- a date range filter aligned with KRX trading days,

MUST use the acquired official calendar at
`data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv` as the source
of truth.

### Permitted: union working calendar

The repo union working calendar may continue to be used ONLY for:

- backward-compatibility with prior P0-2 / runtime-phase reports,
- diagnostic comparison against the official calendar,
- documenting historical research artefacts.

It MUST NOT be used as the authoritative calendar in any new diagnostic or
future strategy work.

### Required: official calendar mandatory

- Execution simulation (when eventually permitted by separate Referee verdict).
- Any strategy backtest entry that depends on next-trading-day mapping.
- Any survivorship / lifecycle audit that aligns to KRX trading days.

### Disagreement handling

| case | handling |
|---|---|
| Date present in panel but absent from official calendar | exclude row from any value-bearing computation; flag for manual review |
| Date present in official calendar but absent from panel | record as missing-day defect; do NOT silently fill |
| Date present in both | OK |
| Final date with no next trading day | execution-simulation last day; do NOT extrapolate |
| Date with anomaly_type = repo_only_date | downstream MUST NOT use that row as a price observation without external evidence |

### Future-phase override

If a future phase acquires a fully authoritative KRX 휴장일 endpoint (or
KOSCOM feed) with broader metadata, that source can supersede this one via a
separate Referee verdict. Until then, the cached pykrx 005930-derived calendar
is the canonical KRX calendar.

## Storage policy

- Calendar file: `data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv`
- DO NOT modify in place.
- DO NOT extend manually; re-acquire via the build script if extending.
- Provenance: `acquired_calendar_inventory.csv` carries the fetch metadata.

## Hard locks (preserved)

- No strategy test.
- No execution simulation.
- No production / paper / P08 / live readiness work.
