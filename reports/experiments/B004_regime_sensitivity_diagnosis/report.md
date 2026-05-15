# B004 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| is_start | 2018-01-02 |
| is_end | 2022-12-30 |
| oos_start | 2023-01-02 |
| oos_end | 2026-05-04 |
| regime_gate | KOSPI proxy level > same-day 200-day SMA; entry-side only for signal variants; gate-off exit for gate-only variant |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| calendar_source | derived from panel non-null KRX종가 rows |

## IS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| signal_plus_gate | -0.720912971282 | 0.372272143774 | 779 | -0.430011790835 |
| signal_only | -0.84017404875 | 0.391268533773 | 1214 | -0.47070942317 |
| gate_only_equal_weight | -0.692151355812 | 0.411464968153 | 785 | -0.415609297443 |
| cash | 0 | 0 | 0 | 0 |

## OOS Variant Metrics

| variant | total_return | hit_rate | trade_count | return_before_cost |
| --- | ---: | ---: | ---: | ---: |
| signal_plus_gate | 0.406820629199 | 0.410404624277 | 692 | 0.816698190474 |
| signal_only | 0.64064021429 | 0.419178082192 | 730 | 1.11906742853 |
| gate_only_equal_weight | 0.240572688603 | 0.457692307692 | 780 | 0.64734708967 |
| cash | 0 | 0 | 0 | 0 |

## Regime Year Breakdown

| year | signal_plus_gate_net_total_return | signal_only_net_total_return | gate_only_equal_weight_net_total_return | cash_net_total_return | delta_signal_plus_gate_minus_gate_only | delta_signal_plus_gate_minus_signal_only | gate_on_days | gate_off_days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2018 | -0.297875452782 | -0.378176494798 | -0.458078135348 | 0 | 0.160202682566 | 0.0803010420154 | 124 | 120 |
| 2019 | -0.109721576732 | -0.0738095269343 | -0.0841652968242 | 0 | -0.0255562799077 | -0.0359120497976 | 170 | 76 |
| 2020 | -0.260493045018 | -0.387065820441 | 0.218726965812 | 0 | -0.47922001083 | 0.126572775423 | 202 | 46 |
| 2021 | -0.275164703632 | -0.2486087019 | -0.358964654656 | 0 | 0.083799951024 | -0.0265560017318 | 212 | 36 |
| 2022 | -0.190394556725 | -0.407001823979 | -0.206274338831 | 0 | 0.0158797821054 | 0.216607267254 | 18 | 228 |
| 2023 | -0.19372974694 | -0.106365338055 | -0.29275151357 | 0 | 0.0990217666299 | -0.0873644088848 | 227 | 18 |
| 2024 | -0.202115787536 | -0.206194685497 | -0.0887649550691 | 0 | -0.113350832466 | 0.00407889796163 | 213 | 31 |
| 2025 | 0.868495999103 | 0.883187298208 | 0.279738447598 | 0 | 0.588757551505 | -0.0146912991052 | 236 | 6 |
| 2026 | 0.128486334693 | 0.128486334693 | 0.462471946542 | 0 | -0.333985611849 | -2.22044604925e-16 | 82 | 0 |

## Cost Sensitivity

| variant | multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- | --- |
| signal_plus_gate | 0 | -0.53226721987 | 1.21794987737 | 0.0374078623326 | 0 |
| signal_only | 0 | -0.64349117319 | 1.65955863147 | -0.0649966318124 | 0 |
| gate_only_equal_weight | 0 | -0.48245661697 | 1.07677805353 | 0.074822739626 | 0 |
| signal_plus_gate | 1 | -0.720912971282 | 0.406820629199 | -0.607374610657 | 0.405292691161 |
| signal_only | 1 | -0.84017404875 | 0.64064021429 | -0.741426173052 | 0.444867358381 |
| gate_only_equal_weight | 1 | -0.692151355812 | 0.240572688603 | -0.618091379797 | 0.401767006228 |
| signal_plus_gate | 2 | -0.833866657145 | -0.109537188853 | -0.852064436496 | 0.58169287927 |
| signal_only | 2 | -0.928617457078 | 0.00980936511732 | -0.928920257644 | 0.612552200886 |
| gate_only_equal_weight | 2 | -0.817201444502 | -0.260202625741 | -0.864766108624 | 0.558870083675 |
| signal_plus_gate | 3 | -0.901341025335 | -0.437566321437 | -0.944510869956 | 0.667356351204 |
| signal_only | 3 | -0.968239798477 | -0.379881006841 | -0.980579376452 | 0.690265578157 |
| gate_only_equal_weight | 3 | -0.89164519156 | -0.559590312777 | -0.952279492706 | 0.625467639788 |
