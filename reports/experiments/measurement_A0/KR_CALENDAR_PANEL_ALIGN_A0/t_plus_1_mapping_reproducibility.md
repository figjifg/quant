# T+1 Execution Mapping Reproducibility

Date: 2026-05-23

## Setup

Union calendar (panel ∪ market_flow ∪ S1) = working-trading-day candidate.
Next-day mapping = `next_day_map[d] = next d' in sorted(union)`.
Reproducibility test = for each panel, sample N=200 rows and verify that the mapping
produces a valid candidate execution date in the same calendar.

## Results

| panel | sample_n | mappable | unmappable_last_day | mappable_pct |
|---|---:|---:|---:|---:|
| `kiwoom_2010_2016` | 200 | 200 | 0 | 100.0% |
| `dynamic_top100_2017_2024` | 200 | 200 | 0 | 100.0% |
| `dynamic_top100_2018_2024` | 200 | 200 | 0 | 100.0% |
| `krx_2025_2026` | 200 | 200 | 0 | 100.0% |

## Interpretation

- A `mappable_pct < 100` means at least one sample date is the **last** date in the union
  calendar (no next-day exists). This is expected on terminal dates only.
- The mapping is **deterministic** given the same union calendar. Reproducibility is
  therefore tied to the union-calendar definition above. If a new authoritative KRX
  calendar source is acquired, the union calendar will change, and all t+1 mappings will
  shift accordingly.

## Per-Referee kill gate

Referee verdict: **If t+1 mapping cannot be reproduced, execution simulation remains closed.**

Mapping IS reproducible given a fixed union calendar. **But** the union calendar itself is
not an authoritative KRX calendar (see `krx_calendar_source_check.md`). Therefore:

- mapping reproducibility = `OK_relative_to_union_calendar`
- absolute reproducibility against KRX official = **PENDING** (calendar source not acquired)

Net: execution simulation remains **CLOSED** (unchanged).
