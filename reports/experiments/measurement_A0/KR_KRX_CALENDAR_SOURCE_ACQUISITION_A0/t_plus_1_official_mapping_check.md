# T+1 Official Mapping Check

Date: 2026-05-24  
Phase: KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0  
Method: build next-day map from acquired official calendar; compare to prior
union-calendar t+1 map.

## Headline

- Common from-dates (in both calendars): **4021**
- Next-day matches: **4021**
- Next-day mismatches: **0**
- From-dates only in official: **12**
- From-dates only in union: **0**

Mismatch detail per row in `t_plus_1_mapping_delta.csv`.

## Interpretation

Mismatches indicate that for the same date `d`, the official calendar's next
trading day differs from the repo union's next trading day. This typically
occurs when the union contained a `repo_only_date` between `d` and the
official next day, OR when the official calendar contained an
`official_only_date` that the union missed.

**Materiality**: if mismatches are frequent or systematic, execution simulation
must remain CLOSED until the mismatches are individually classified. Per
`execution_simulation_gate_status.md`, the gate decision factors this count.

## Hard locks (preserved)

- No execution simulation.
- No strategy test.
- No performance metric.
