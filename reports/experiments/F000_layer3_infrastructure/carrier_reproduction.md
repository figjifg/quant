# F000 Carrier Reproduction

## Verdict

- D013: OK - compared files are byte-identical.
- E014: OK - compared files are byte-identical.

## Headline Metrics

| experiment | sharpe             | cumulative_net_total_return | mdd                  | n_trades | exposure_ratio     |
| ---------- | ------------------ | --------------------------- | -------------------- | -------- | ------------------ |
| D013       | 0.5333654677635088 | 2.5457702903350135          | -0.3392346174957135  |          | 0.3475496688741722 |
| E014       | 0.6311872415922518 | 3.621084739339225           | -0.35641869371448887 |          | 0.3475496688741722 |

## File Hash Comparison

### D013

| file                         | status | base_sha256                                                      | repro_sha256                                                     |
| ---------------------------- | ------ | ---------------------------------------------------------------- | ---------------------------------------------------------------- |
| metrics.json                 | OK     | ba8cf9ff9ea8473c4f899fd11d7b3ab41b60a8eb449435be4d15013d0e380da1 | ba8cf9ff9ea8473c4f899fd11d7b3ab41b60a8eb449435be4d15013d0e380da1 |
| trades.csv                   | OK     | 88dbc1da39674b814a7ee6bf8b32723aee393cf5d11fa349950dc0d81eae3326 | 88dbc1da39674b814a7ee6bf8b32723aee393cf5d11fa349950dc0d81eae3326 |
| signals.csv                  | OK     | b7755fedd6c0817e9756865dc8bed002c4f166a415f72688a2c99e1e1bdd345b | b7755fedd6c0817e9756865dc8bed002c4f166a415f72688a2c99e1e1bdd345b |
| equity_curve.csv             | OK     | c6dedc123af781bb93f83cd704428f703e2f8c18388e1936001469ea32ac2139 | c6dedc123af781bb93f83cd704428f703e2f8c18388e1936001469ea32ac2139 |
| quarterly_regime_log.csv     | OK     | d3ba6dbf60d6f4d8745282135ab7824745227ccae9d9fee20af471d590626b84 | d3ba6dbf60d6f4d8745282135ab7824745227ccae9d9fee20af471d590626b84 |
| quarterly_year_breakdown.csv | OK     | cb86f2b57f8d4de162ee20f203f2e5e6031f2c4c8541243d64c5367e68ea8b38 | cb86f2b57f8d4de162ee20f203f2e5e6031f2c4c8541243d64c5367e68ea8b38 |
| subperiod_breakdown.csv      | OK     | 3d87d8c3d79bfc379978740bd4ac1ca3e3ca7747cab83eca26e3782beeb4d173 | 3d87d8c3d79bfc379978740bd4ac1ca3e3ca7747cab83eca26e3782beeb4d173 |
| report.md                    | OK     | 6d0c918d94d86efcf7c77c6bba9e4f6a681cc4897a38bf5db88d58e6b4fecff6 | 6d0c918d94d86efcf7c77c6bba9e4f6a681cc4897a38bf5db88d58e6b4fecff6 |

### E014

| file                         | status | base_sha256                                                      | repro_sha256                                                     |
| ---------------------------- | ------ | ---------------------------------------------------------------- | ---------------------------------------------------------------- |
| metrics.json                 | OK     | 9d3e8194526411a70f8508ebb3440a603227cfea26c6a4b8f89ff94340f4b0b8 | 9d3e8194526411a70f8508ebb3440a603227cfea26c6a4b8f89ff94340f4b0b8 |
| trades.csv                   | OK     | 3f17ecfc6c787bbd9d47367a344e1e5b0bf54ea70b73d4ba34d1d15a1b80c066 | 3f17ecfc6c787bbd9d47367a344e1e5b0bf54ea70b73d4ba34d1d15a1b80c066 |
| signals.csv                  | OK     | 0ba744ee2a73c955d8955a99b2cf7253c9bbf2a2c707572222e4f91c4cd83bc3 | 0ba744ee2a73c955d8955a99b2cf7253c9bbf2a2c707572222e4f91c4cd83bc3 |
| equity_curve.csv             | OK     | d34ef047d8ab0059ca861431d4f8f1eafacb46e3511425ccda47c05be08243e3 | d34ef047d8ab0059ca861431d4f8f1eafacb46e3511425ccda47c05be08243e3 |
| quarterly_regime_log.csv     | OK     | d3ba6dbf60d6f4d8745282135ab7824745227ccae9d9fee20af471d590626b84 | d3ba6dbf60d6f4d8745282135ab7824745227ccae9d9fee20af471d590626b84 |
| quarterly_year_breakdown.csv | OK     | 8d231debfda7d01e00aba0548fe88f476b592f00dd46c76eb84731781a55a0f8 | 8d231debfda7d01e00aba0548fe88f476b592f00dd46c76eb84731781a55a0f8 |
| subperiod_breakdown.csv      | OK     | a24704f1cd4d036bc16dddb822a912076a65fd978bdf4f2349a6e07a59bfbefc | a24704f1cd4d036bc16dddb822a912076a65fd978bdf4f2349a6e07a59bfbefc |
| report.md                    | OK     | 5d7b071e42ab29f5193532293ad3536dd78669c82d9ddc1fdaf1e8543bfdebdb | 5d7b071e42ab29f5193532293ad3536dd78669c82d9ddc1fdaf1e8543bfdebdb |
