# I000 — I-family: US/Global ETF macro allocation universe + 인프라

## 상태
계획됨

## 이게 무슨 ticket 인가

지피티 권장 Strategy 2. D013/H001 와 독립적 US/Global ETF macro
allocation. 한국 시장 concentration 위험 분산.

## 목표

```
독립 전략 (Strategy 2):
- D013 H001 와 낮은 상관
- 더 나은 portfolio Sharpe
- 더 낮은 combined MDD
- US/Global ETF universe (한국 시장 외)
```

## Candidate universe (지피티 권장)

| 자산 | ETF | 역할 |
|---|---|---|
| US 대형주 | SPY 또는 VOO | risk asset core |
| US 성장 | QQQ | tech/growth |
| US 소형 | IWM | size factor |
| Treasury 단기 | SHY (1-3y) | defensive |
| Treasury 중기 | IEF (7-10y) | defensive |
| Treasury 장기 | TLT (20y+) | defensive duration |
| Gold | GLD | tail hedge |
| Dollar | UUP or USD cash | FX |
| Commodity | DBC | inflation hedge |
| Cash | KRW MMF | fallback |

## I000 작업

1. **Universe 데이터 가용성 확인**:
   - yahoo finance ETF 가격 (pykrx 같은 US lib 없으므로 yfinance 또는 직접 download)
   - 우리 .venv 에 yfinance 설치 시도
   - 또는 직접 yahoo finance CSV URL
   - 또는 FRED 의 US ETF 가격 series (제한적)

2. **데이터 인프라 구성**:
   - I-family universe 9-10 ETF 분기말 가격
   - KRW 환산 (USDKRW 사용)
   - ETF inception 처리 (예: SPY 1993, QQQ 1999, GLD 2004, SHY 2002)

3. **D013/H001 와 상관 분석**:
   - 각 ETF 분기 return vs D013/H001 분기 return
   - 낮은 상관 = portfolio diversification 가치

## 사전 등록 verdict

I000 = 인프라/데이터 확인 + 분기 return 계산.
PROCEED 조건:
- 9-10 ETF 데이터 수집 가능 (yfinance 또는 직접)
- 우리 backtest 기간 (2010-2026) cover
- D013/H001 와 분기 return 상관 가능

## 산출물

- reports/experiments/I000_us_global_etf_universe/
- etf_data_availability.csv (ETF 별 inception, 데이터 수)
- universe_correlation_matrix.csv (ETF 간 + D013/H001 분기 return 상관)
- report.md (PROCEED / STOP 판정 + I001 진행 권고)

## 엄격 제약

- D013, H001 strategy 미수정
- engine.py 미수정
- D-H, P 모두 byte-identical
- 외부 network: yfinance 설치 또는 yahoo finance direct download
- 새 데이터: research_input_data/inputs/global_etf/ (NEW directory)
- 사용자 승인 후 진행
