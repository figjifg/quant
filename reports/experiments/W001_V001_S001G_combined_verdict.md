# W001 / V001 / S001-G Combined Verdict

## W001 implementation status

W001 6개 utility module을 실제 구현으로 전환했다.

- `src/utils/korean_calendar.py`: local panel 기반 KRX calendar, stock-specific tradable dates, next/prev/range API.
- `src/utils/corporate_action.py`: adjusted OHLC alias, `KRX종가` validation/synthesis, impossible return detector.
- `src/utils/tradability.py`: 거래정지 proxy, 추정 거래대금, missing OHLC, dynamic universe, limit-up/down execution filter.
- `src/utils/sleeve_nav_simulator.py`: no-leverage sleeve NAV, cash/position accounting, turnover.
- `src/utils/random_placebo_engine.py`: date/drop-bucket/time-shift/stock-matched placebo.
- `src/utils/backtest_sanity_checks.py`: impossible return, exposure, duplicate signal, lineage, benchmark alignment checks.

## V001 P08 impact

Verdict: `PASS_BYTE_IDENTICAL`

- D013/H001 `metrics.json`는 baseline snapshot과 동일하다.
- D013/H001 entry/exit 날짜는 KRX calendar와 signal_date 이후 execution 조건을 만족한다.
- Top 5 holdings tradability audit fail count는 0이다.
- 기존 D013/H001/P08 primary 산출물은 재작성하지 않았다.

## S001-G corrected result

Verdict: `S-family permanently CLOSED`

Corrected smoke metrics:

- `r1d_lt_m3_hold1`: gross mean 0.4071%, Sharpe -0.1465, verdict `NULL_WEAK_CLOSE_S_FAMILY`.
- `r1d_lt_m3_hold3`: gross mean 1.2319%, Sharpe 0.4659, verdict `NULL_WEAK_CLOSE_S_FAMILY`.
- `r1d_lt_m3_hold5`: gross mean 3.0571%, Sharpe 0.8964, verdict `NULL_WEAK_CLOSE_S_FAMILY`.

Placebo edge가 일부 남아도 사전 등록 gate의 Sharpe 기준을 넘지 못했다. Strong 조건이 없으므로 S000을 재활용하지 않고 S-family를 종료한다.

## Audit-first framework effect

W001 전 corrected smoke에서 발생할 수 있던 filtered-row jump와 over-optimistic hold-day 해석이 W001 lineage/tradability/sanity check로 드러났다. Entry는 signal_date 다음 KRX trading day의 tradable row로 제한했고, exit는 정확한 KRX hold-date에 tradable row가 있는 경우만 인정했다.

## Next step

S-family closed. 더 이상 한국 단기 alpha 시도는 진행하지 않는다. S2-family는 이번 결과로 열지 않는다.
