# S001-F Mechanism Analysis

## Verdict

DIAGNOSTIC_ONLY

## Breakdown

| bucket | value | count | mean | median | hit_rate | sharpe_like |
| --- | --- | --- | --- | --- | --- | --- |
| d013_state | unknown_not_in_s000_artifact | 1622 | 0.100165 | 0.049673 | 0.666461 | 1.667185 |
| kospi_day | down | 726 | 0.133985 | 0.051170 | 0.672176 | 1.626359 |
| kospi_day | up_or_flat | 896 | 0.072763 | 0.046302 | 0.661830 | 2.283824 |
| drop_type | market_drop | 87 | 0.414513 | 0.109227 | 0.781609 | 1.958644 |
| drop_type | stock_specific | 1535 | 0.082349 | 0.046601 | 0.659935 | 2.333880 |
| foreign_flow | foreign_net_sell | 1146 | 0.098375 | 0.056185 | 0.689354 | 2.688404 |
| foreign_flow | foreign_not_sell | 476 | 0.104475 | 0.032480 | 0.611345 | 1.097692 |
| institution_flow | institution_net_sell | 1005 | 0.114039 | 0.044827 | 0.651741 | 1.560879 |
| institution_flow | institution_not_sell | 617 | 0.077566 | 0.060306 | 0.690438 | 2.722616 |
| mcap_bucket | large_top50 | 15 | -0.037270 | -0.035772 | 0.200000 | -9.510867 |
| mcap_bucket | mid_51_100 | 37 | -0.017948 | -0.024450 | 0.378378 | -1.859361 |
| mcap_bucket | other | 1570 | 0.104262 | 0.053718 | 0.677707 | 1.710268 |
| gap_bucket | gapdown_gt3pct | 368 | 0.110476 | 0.010585 | 0.565217 | 0.989272 |
| gap_bucket | gapdown_0_3pct | 470 | 0.067436 | 0.061336 | 0.674468 | 2.684775 |
| gap_bucket | flat_or_gapup | 784 | 0.114946 | 0.065511 | 0.709184 | 3.111462 |
| intraday_bucket | intraday_rebound | 968 | 0.100006 | 0.059409 | 0.700413 | 2.846591 |
| intraday_bucket | intraday_weak | 654 | 0.100402 | 0.031007 | 0.616208 | 1.181844 |
| vol_regime | low_vol | 542 | 0.111883 | 0.072054 | 0.750923 | 3.797366 |
| vol_regime | mid_vol | 540 | 0.096587 | 0.059005 | 0.688889 | 2.529521 |
| vol_regime | high_vol | 540 | 0.091982 | 0.013733 | 0.559259 | 0.993070 |

## Hypotheses

| hypothesis | support | evidence |
| --- | --- | --- |
| forced_selling_liquidity_rebound | diagnostic | compare foreign/institution net-sell buckets and intraday rebound buckets |
| large_cap_panic_overshoot | diagnostic | compare mcap buckets and market-drop buckets |
| individual_stock_microstructure_bounce | diagnostic | compare stock_specific and gap/intraday buckets |
| index_program_flow_reversal | unproven | requires explicit program/index flow data not in S000 artifacts |

## Limitations

D013 ON/OFF and sector classifications are not present in S000 artifacts. Sector split remains pending unless a PIT sector map is supplied.
