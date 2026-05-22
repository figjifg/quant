# Z000 Failure Register

Status: closed-family failure register. 표현은 방어적이지 않고 정직하게 유지한다.

## E014: PIT Sector Fail

1. 원래 가설: sector RS/breadth top4가 시장 구조 변화를 포착해 D013 이후의 alpha를 확장할 수 있다.
2. 왜 그럴듯했나: sector rotation은 직관적이고, top sector 집중은 상승 구간에서 강하게 보일 수 있다.
3. 어떤 결과: PIT sector membership 문제로 결과 신뢰가 훼손되었다.
4. 실패 원인: 날짜별 sector membership을 재현하지 못해 look-ahead/survivorship 위험이 남았다.
5. 다시 열려면 필요 조건: PIT sector membership, delisting-safe mapping, regression test.
6. 다시 열면 안 되는 조건: 현재 sector mapping만으로 재시도.
7. 앞으로 hard rule: Sector PIT 없이 sector family 재개 금지.

## F-family: Stock Ranking Null

1. 원래 가설: 외국인/기관 수급, RS, liquidity를 종목 ranking으로 결합하면 sector보다 직접적인 alpha가 나온다.
2. 왜 그럴듯했나: 종목 단위 정보가 더 세밀하고, top-ranked stock selection은 직관적으로 강해 보였다.
3. 어떤 결과: ranking signal의 독립 edge가 충분하지 않았다.
4. 실패 원인: 비용, turnover, noisy cross-section, signal decay가 결합되었다.
5. 다시 열려면 필요 조건: 더 나은 PIT universe, total return, execution cost, robust IC evidence.
6. 다시 열면 안 되는 조건: 단순 top-N ranking 재사용.
7. 앞으로 hard rule: ranking family는 net IC와 random control 통과 전 paper candidate로 올리지 않는다.

## G-family: Slow Overlay Null

1. 원래 가설: MDD cooldown/stress filter 같은 slow overlay가 D013의 tail risk를 줄인다.
2. 왜 그럴듯했나: 큰 하락 후 위험 축소는 심리적으로도 통계적으로도 설득력 있어 보였다.
3. 어떤 결과: overlay가 수익을 깎거나 timing을 악화시켰다.
4. 실패 원인: 느린 신호가 반등을 놓치고, 비용/기회비용을 만들었다.
5. 다시 열려면 필요 조건: 사전 stress budget과 live action rule이 명확한 defensive 목적.
6. 다시 열면 안 되는 조건: 최근 drawdown에 대한 사후 반응.
7. 앞으로 hard rule: overlay는 alpha 개선이 아니라 명시적 risk budget 도구일 때만 검토.

## K-family: Sector Momentum Reject, Defensive Backlog

1. 원래 가설: US sector rotation이 global sleeve의 보조 수익원이 될 수 있다.
2. 왜 그럴듯했나: sector ETF는 구현이 쉽고 macro regime과 연결하기 좋았다.
3. 어떤 결과: production candidate로 충분하지 않았다.
4. 실패 원인: marginal improvement, regime dependence, 세금/회전 비용.
5. 다시 열려면 필요 조건: defensive sleeve 목적과 명시적 stress role.
6. 다시 열면 안 되는 조건: sector momentum standalone 재포장.
7. 앞으로 hard rule: K-family는 defensive backlog이지 live allocation 변경 근거가 아니다.

## J-family: EM Static Backlog, Momentum Catastrophic

1. 원래 가설: EM equity sleeve가 미국 중심 portfolio에 diversification을 제공한다.
2. 왜 그럴듯했나: 지역 분산은 장기 포트폴리오 이론상 자연스럽다.
3. 어떤 결과: static은 backlog 수준, momentum은 catastrophic으로 판정.
4. 실패 원인: EM crash risk, currency/regime exposure, trend signal 불안정.
5. 다시 열려면 필요 조건: 명확한 역할, 긴 history, stress budget, 비용 반영.
6. 다시 열면 안 되는 조건: valuation이나 지역 분산 직관만으로 재개.
7. 앞으로 hard rule: EM momentum은 재개 금지에 가깝게 취급한다.

## Q-family: Direct Survivor Bias, ETF Marginal

1. 원래 가설: quality/value/shareholder yield가 US equity sleeve를 개선할 수 있다.
2. 왜 그럴듯했나: 잘 알려진 factor이고 장기 문헌이 존재한다.
3. 어떤 결과: direct stock 결과는 survivor bias 위험, ETF proxy는 marginal.
4. 실패 원인: PIT universe 부재, factor data 품질, 비용과 turnover.
5. 다시 열려면 필요 조건: survivorship-safe US universe와 PIT fundamentals.
6. 다시 열면 안 되는 조건: 현재 surviving tickers로 direct backtest 재개.
7. 앞으로 hard rule: Q-family direct 재개 금지. ETF proxy는 marginal로만 기록.

## R-family: Title-based Event Fail

1. 원래 가설: 자사주, 소각, 배당 증가 공시 이벤트가 단기 alpha를 만들 수 있다.
2. 왜 그럴듯했나: 주주환원 이벤트는 경제적 의미가 있고 시장 반응도 기대된다.
3. 어떤 결과: title-based event 추출은 충분하지 않았다.
4. 실패 원인: 본문 금액/조건/시점 파싱 부재, event lag, 비용.
5. 다시 열려면 필요 조건: DART body parser, event timestamp, amount normalization, QA sample.
6. 다시 열면 안 되는 조건: 공시 제목 키워드만으로 재개.
7. 앞으로 hard rule: R-family는 body parser 전까지 closed.

## S-family: Measurement Artifact

1. 원래 가설: large-cap short-horizon panic mean reversion이 Korean standalone alpha가 될 수 있다.
2. 왜 그럴듯했나: S000 strong result가 매우 강했고, 단기 과매도 반등 직관과 맞아 보였다.
3. 어떤 결과: S000 strong result = measurement artifact.
4. 실패 원인: entry/exit alignment, filtered-row execution, unadjusted corporate action, per-trade leverage, invalid random control.
5. 다시 열려면 필요 조건: W001 Korean equity backtest engine repair 후 S001-G corrected smoke test 1회.
6. 다시 열면 안 되는 조건: S-family alpha 재시도, production, paper, P08 satellite.
7. 앞으로 hard rule: S-family는 CLOSED_DIAGNOSTIC_ARTIFACT. W001 후 단일 smoke test는 infrastructure QA, alpha X.

## X-ETF (track): Tactical ETF No Edge

1. 원래 가설: 14 ETF universe (SPY/QQQ/IWM/IEF/TLT/SHY/GLD/UUP/DBC/VWO/EWY/EWJ/EWZ/MCHI)에서 time-series momentum / dual momentum / defensive rotation / risk budget이 P08_IEF30 또는 simple fixed shadow를 개선할 수 있다.
2. 왜 그럴듯했나: ETF는 데이터 깨끗하고 capacity 크고 momentum 문헌 풍부했다.
3. 어떤 결과: X-ETF001 40/40 variants + X-ETF900 24/24 variants = 64/64 variants 모두 close. V10 (best dynamic) Sharpe 1.149 < N001-B GLD 10% 1.184 / N002-B cash 10% 1.166.
4. 실패 원인: turnover/tax 가 alpha 잠식, dynamic rotation 의 added complexity 가 simpler fixed shadow 보다 못함.
5. 다시 열려면 필요 조건: 새 verifiable mechanism (volatility targeting + cost-aware rebalance, etc.), 사전 등록 strict gate, simple shadow 직접 beat 증명.
6. 다시 열면 안 되는 조건: 동일 universe + 동일 momentum/rotation 재포장, in-sample optimization.
7. 앞으로 hard rule: ETF tactical = no actionable edge over static allocation or simpler fixed shadows. V10 = marginal diagnostic only.

## X-KR001: Korean Pair/Residual Mean Reversion No Edge

1. 원래 가설: KRX 종목 간 cointegrated pair 또는 sector-neutral residual mean reversion이 단기 alpha가 될 수 있다.
2. 왜 그럴듯했나: pair trading은 통계적 정합성이 명확하고 sector-neutral 구조가 beta exposure 제거에 적합해 보였다.
3. 어떤 결과: 6 pre-registered variants × long-only/long-short = 12/12 variants 모두 close. Top XKR001_V02 long_only Sharpe 1.497 / CAGR 175.78% / MDD -99.7% = impossible-return artifact 잔존.
4. 실패 원인: turnover/tax 가 모든 variant alpha 소멸 (gate 7 = 12/12), 2 subperiod 불안정 (gate 6 = 11/12), long-short borrow 한국 시장 비현실, long-only fallback weak. A0 sanity 4 FAIL = W001 engine 후에도 long-short residual 측정 layer 일부 artifact 잔존.
5. 다시 열려면 필요 조건: borrow 가능 KR pair universe (실제 가능 종목 사전 등록), residual definition 의 PIT 정합 재검증, 새 alpha hypothesis (단순 cointegration X), W001 layer 추가 repair.
6. 다시 열면 안 되는 조건: 동일 pair list + 동일 mean reversion 재포장, long-short borrow 가정만 변경.
7. 앞으로 hard rule: X-KR pair/residual = no actionable edge. Korean simple standalone alpha 5 family (E/F/G/R/S) + X-KR pair = 모두 close. D013/H001 sleeve 만 생존.
