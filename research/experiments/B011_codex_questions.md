# B011 Codex Questions

## Blocking ambiguity: 2018-2024 panel missing from literal config

The ticket's required `configs/backtests/b011.yaml` block lists:

- `research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv`
- `research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv`
- `research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv`

and also applies:

```yaml
panel_date_filters:
  research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv:
    end: 2017-12-31
```

Implemented literally, this creates a timeline with 2010-2015, 2017,
and 2025-2026 only. There is no 2018-2024 equity panel in the run,
so the ticket's completion requirement that "B004 V1 2018-2026 numbers
must match B011 V1's 2018-2026 segment" is impossible to verify.

Question: should B011 add
`research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
to the `panels` list, while keeping the 2017-2024 panel filtered to
2017 only?
