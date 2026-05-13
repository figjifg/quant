# Data inventory — 2026-05-13 initial survey

Purpose: catalogue data sources that are realistically reachable for the
foreign / institutional flow-following 추격 매수 project, **before**
designing any specific experiment. This list is what we can choose from
when locking each experiment's data set.

This file is a project-level reference. It is **not** a license for any
experiment to use all of these at once. Each experiment must still pick
a small, motivated subset and freeze it before running.

## Provider auth status (smoke-tested 2026-05-13)

| Provider | Key in `.env` | Auth result | Notes |
| --- | --- | --- | --- |
| FRED | `FRED_API_KEY` | OK | Public REST, daily refresh. USD/KRW back to 1981. |
| OpenDART | `OPENDART_API_KEY` | OK | Disclosure metadata + filings text. |
| KIS (한국투자증권) | `KIS_APP_KEY` + `KIS_APP_SECRET` | OK | OAuth `tokenP`, token TTL ~24h. |
| 키움 REST | `KIWOOM_APPKEY` + `KIWOOM_SECRETKEY` | OK | OAuth `token`. Same data the existing `inputs/` panels came from. |
| KRX 정보데이터시스템 | `KRX_API_KEY` + `KRX_AUTH_KEY` | **401** | Endpoint or header form unknown; **공공데이터포털 (data.go.kr) 금융위원회 services cover most of what we'd want from KRX, so this is no longer a blocking gap.** |
| BOK ECOS | `BOK_API_KEY` | OK | 834 통계표 available; USD/KRW (731Y001) verified, 100+ macro series accessible. |
| 공공데이터포털 (data.go.kr) | `DATA_GO_KR_API_KEY` | OK | 금융위원회 카테고리 ~115 services; 주식대차정보 6 sub-functions verified. |

## Historical depth — verified

KIS endpoints probed back to 2000-01-04:

| Endpoint | TR_ID | Earliest verified | Returns | Notes |
| --- | --- | ---: | --- | --- |
| 종목별 일별 OHLC | `FHKST03010100` | 2000-01-04 | ~20-21 rows per call | full price + adj-flag |
| 종목별 투자자 매매동향(일별) | `FHPTJ04160001` | 2000-01-04 | 30 rows ending at requested date | rich institution breakdown (see below) |
| 시장별 투자자 매매동향(일별) | `FHPTJ04040000` | 2000-01-04 | 300 rows per call | KOSPI/KOSDAQ-level |
| 국내업종 일자별 지수 | `FHPUP02120000` | 2000-01-04 | 100 rows ending at requested date | KOSPI = "0001" |
| 국내주식 공매도 일별추이 | `FHPST04830000` | works | output structure needs re-check | for short-sale historical |

Note: "earliest verified" means we successfully pulled data starting at
the listed date; the true earliest data point per endpoint could be
older, just not probed.

### 금융위원회 주식대차정보 (data.go.kr) — all 6 sub-functions verified

Service URL: `https://apis.data.go.kr/1160100/GetStocLendBorrInfoService_V2`.
Earliest data is **2008-01-02** for every endpoint, even though the
official 활용가이드 docx lists 2020-04-01 as the start. The docx is
out-of-date; the API itself returns 2008+ rows.

| Endpoint | Records (totalCount) | Granularity | Key fields |
| --- | ---: | --- | --- |
| `getStLendAndBorrItemRank_V2` (종목순위) | 7,918,063 | per stock × per day | basDt, isinCd, lnbCclStckCnt (체결), lnbRmanStckCnt (잔여), lnbRdptStckCnt (리콜) |
| `getStItemLendAndBorrStatu_V2` (종목별 현황) | 7,925,577 | per stock × per day | same as above |
| `getMontLendAndBorrStatu_V2` (월별 현황) | 221 | market-wide × month | monthly aggregates |
| `getStBusiTypePartStatu_V2` (업종별 참여) | **34,581,614** | per stock × per day × **(외국인/내국인)** | stckLndnBal (대여잔고), stckLndnRto (대여비율), stckBrwBal (차입잔고), stckBrwRto (차입비율) |
| `getNatiAndForeLendAndBorrBalaCo_V2` (내외국인 잔고비교) | 221 | market × month | ntiv*, forg*, brwBalForgRto, lndnBalForgRto |
| `getNatiAndForeLendAndBorrTrad_V2` (내외국인 거래량) | 4,530 | market × day | forgLnbCclStckCnt/Amt, ntivLnbCclStckCnt/Amt |

**The most strategically valuable endpoint for our project is
`getStBusiTypePartStatu_V2`** — it gives per-stock per-day breakdown of
foreign vs domestic stock lending balance and ratio. This lets us see
"is foreign money setting up short positions in this specific name,
right now, before they show up as price action?" That is exactly the
hidden flow context CLAUDE.md asked for.

## Investor-flow detail KIS provides (not in current inputs/)

The existing `inputs/equity_panels/*.csv` only has aggregated
`외국인순매매량` and `기관순매매량`. KIS investor-trade-by-stock-daily
breaks this out per row:

**Foreign**
- `frgn_ntby_qty` — 외국인 순매수 (주식 수)
- `frgn_reg_ntby_qty` — 등록외국인 순매수
- `frgn_nreg_ntby_qty` — 미등록외국인 순매수
- `frgn_ntby_tr_pbmn` — 외국인 순매수 (금액)
- `frgn_seln_vol` / `frgn_shnu_vol` — 매도/매수 분리

**Institution (broken out)**
- `orgn_ntby_qty` — 기관 합산
- `scrt_ntby_qty` — 증권
- `ivtr_ntby_qty` — 투신
- `pe_fund_ntby_vol` — 사모(PE)
- `bank_ntby_qty` — 은행
- `insu_ntby_qty` — 보험
- `mrbn_ntby_qty` — 상호금융
- `fund_ntby_qty` — 연기금
- `etc_corp_ntby_vol` — 일반법인
- `etc_orgt_ntby_vol` — 기타기관

All have a `_tr_pbmn`/`_pbmn` (금액) twin and a `_seln_vol`/`_shnu_vol`
(매도/매수) breakdown.

This matters: CLAUDE.md §4.1 listed exactly these breakdowns as
desirable but said "초기에는 외국인과 기관 합산 데이터로 시작해도
된다." KIS would let us upgrade to the full breakdown at any time.

## Mapping to the 5-layer architecture

| Layer | Question | KIS / other source |
| --- | --- | --- |
| 0 | Per-stock per-day raw | `FHKST03010100` OHLC + `FHPTJ04160001` flow detail |
| 1 | One stock, its time pattern | derived from Layer 0 |
| 2 | All stocks today, cross-section | derived from Layer 0 |
| 3 | Sector aggregates | `FHPUP02120000` per sector + sector code mapping |
| 4 | KOSPI / KOSDAQ aggregate | `FHPTJ04040000` market-level investor flow, plus program trading endpoints, plus existing `inputs/market_flow/*` |
| 5 | Global / macro | FRED (USD/KRW, US yields), existing `inputs/futures/global_index_futures/*`, existing `inputs/macro_features/*` |

Sector code mapping is needed for Layer 3. KIS Excel has a "종목정보파일
- 업종코드 참조" reference; we have not pulled the mapping table yet.

## Known gaps (no key / no source yet)

| Data | Why we may want it | Resolution |
| --- | --- | --- |
| ~~BOK ECOS macro~~ | Layer 5 KR-side macro | **resolved — BOK_API_KEY added, 834 통계표 accessible** |
| ~~외국인 vs 국내 대차잔고~~ | Layer 1/4 short-side signal | **resolved — data.go.kr 금융위 주식대차정보 6 endpoints, 2008+** |
| KRX 정보데이터시스템 raw access | covers what data.go.kr doesn't | Lower priority now that data.go.kr fills the gap. Header form still unknown; defer. |
| 한국 V-KOSPI, 옵션 PCR | Layer 4 sentiment | KIS futures/options endpoints — not probed yet. |
| Sector classification per stock | Layer 2 / Layer 3 bridge | KIS 종목정보파일 endpoint — not probed; can also derive from getStBusiTypePartStatu_V2 industry codes (sicCd/sicNm). |
| Foreign ownership % over time | Layer 1 cumulative flow | Derivable from data.go.kr lending balance + KIS investor flow without a new endpoint. |
| US ETF flows (SPY, QQQ, EWY, EFA) | Layer 5 global cue | yfinance / FinanceDataReader free if needed. |
| News headlines / 빅카인즈 | Layer 1 event filter | Separate API, not currently in scope. |

**Net assessment**: Layer 0~5 are all covered by data sources we can
actually reach. No experiment in the near term is blocked on missing
data. Further exploration of public data portals is deferred until a
specific experiment requires a specific gap to be filled.

## What we do NOT need to pursue right now

These exist but probably duplicate what we have:

- Kiwoom market-flow endpoints — `inputs/market_flow/*` already covers this with the same data.
- 키움 종목별 투자자 — `inputs/equity_panels/*` already covers it (lower granularity vs KIS).

If the next experiment needs higher-granularity flow (e.g. "투신 vs
연기금 분리"), switch to KIS instead of keeping Kiwoom.

## Recommendation for the next experiment's data lock

When you write the next experiment's ticket, the **smallest meaningful
data set** to lock would be:

1. KIS 종목별 일별 OHLC + 종목별 투자자 매매동향(일별) for 2018–2026
   on a fixed universe (e.g. KOSPI200 constituents on each day, or
   the dynamic Top100 as before).
2. KIS 시장별 투자자 매매동향(일별) for KOSPI 2018–2026 (Layer 4).
3. The existing FRED USD/KRW + US 3M yield series.

That alone covers Layers 0, 1, 2, 4 partial, 5 partial — enough for a
first real experiment with the macro context the project requires.

Sector data (Layer 3) and short-sale (Layer 4 sentiment) would be a
deliberate addition for a **later** experiment, not this one.
