"""W000 item 2 — Korean total-return acquisition (autonomous data track).

Authorized 2026-05-26 by explicit user decision ("W000 외부 취득까지 자율 — 다운로드
사전승인"). Acquires dividend-adjusted (total-return) price series + dividend/split
event ledgers for the Korean research universe via yfinance, because the existing
adjusted OHLC (pykrx adjusted=True) is split/rights-adjusted ONLY (no dividends), and
pykrx fundamental (DPS) is currently broken (KRX endpoint returns empty).

yfinance for a Korean ticker provides:
  - 'Adj Close'  = dividend + split adjusted -> total-return price series
  - 'Close'      = split-adjusted close (compare vs pykrx adjusted for validation)
  - 'Dividends'  = cash dividend events with ex-dates
  - 'Stock Splits'

HARD LOCKS (W000 track): raw acquired artifacts go under data/acquired/** (gitignored);
no modification of data/raw or research_input_data; this is DATA INFRASTRUCTURE only —
acquiring it does NOT reopen any closed Korean-equity research (W000 Hard Rule); no
strategy / backtest / execution use. Source + adjustment convention documented in the
lineage note.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
ADJ_OHLC = REPO / "data/acquired/round4/s1_adjusted_ohlc/adjusted_ohlc_all_tickers_2018_2026.csv"
PIT_CLASS = REPO / "data/processed/krx_pit_sector_classifications.csv"
OUT = REPO / "data/acquired/w000_korean_total_return"

START, END = "2018-01-01", "2026-05-10"


def build_universe() -> pd.DataFrame:
    adj = pd.read_csv(ADJ_OHLC, usecols=["종목코드"], dtype=str, low_memory=False)
    tickers = sorted(adj["종목코드"].str.zfill(6).unique())
    cls = pd.read_csv(PIT_CLASS, dtype=str)
    cls["ticker"] = cls["종목코드"].str.zfill(6)
    mkt = (cls.sort_values("date").drop_duplicates("ticker", keep="last")
           .set_index("ticker")["market"])
    rows = [{"ticker": t, "market": mkt.get(t, "UNKNOWN")} for t in tickers]
    return pd.DataFrame(rows)


def yahoo_symbols(ticker: str, market: str) -> list[str]:
    # try the market-implied suffix first, then the other (handles mis-labeled rows)
    ks, kq = f"{ticker}.KS", f"{ticker}.KQ"
    return [ks, kq] if market != "KOSDAQ" else [kq, ks]


def fetch_one(ticker: str, market: str):
    import yfinance as yf
    for sym in yahoo_symbols(ticker, market):
        try:
            h = yf.Ticker(sym).history(start=START, end=END, auto_adjust=False)
        except Exception:
            h = None
        if h is not None and len(h) > 0:
            h = h.reset_index()
            h["date"] = pd.to_datetime(h["Date"]).dt.tz_localize(None).dt.strftime("%Y-%m-%d")
            return sym, h
    return None, None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="cap tickers (0=all) for smoke test")
    ap.add_argument("--sleep", type=float, default=0.15)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    uni = build_universe()
    if args.limit:
        uni = uni.head(args.limit)
    n = len(uni)
    print(f"[w000-tr] acquiring {n} tickers via yfinance {START}..{END}", flush=True)

    price_rows, div_rows, split_rows, manifest = [], [], [], []
    ok = 0
    for i, r in enumerate(uni.itertuples(index=False), 1):
        t, mkt = r.ticker, r.market
        sym, h = fetch_one(t, mkt)
        if h is None:
            manifest.append({"ticker": t, "market": mkt, "yahoo_symbol": "", "status": "no_data",
                             "rows": 0, "date_min": "", "date_max": "", "n_dividends": 0, "n_splits": 0})
        else:
            for _, row in h.iterrows():
                price_rows.append({"date": row["date"], "ticker": t,
                                   "close": row.get("Close"), "adj_close": row.get("Adj Close"),
                                   "volume": row.get("Volume")})
            dv = h[h["Dividends"] > 0]
            for _, row in dv.iterrows():
                div_rows.append({"ticker": t, "ex_date": row["date"], "dividend": row["Dividends"]})
            sp = h[h["Stock Splits"] > 0]
            for _, row in sp.iterrows():
                split_rows.append({"ticker": t, "date": row["date"], "split": row["Stock Splits"]})
            manifest.append({"ticker": t, "market": mkt, "yahoo_symbol": sym, "status": "ok",
                             "rows": len(h), "date_min": h["date"].min(), "date_max": h["date"].max(),
                             "n_dividends": int(len(dv)), "n_splits": int(len(sp))})
            ok += 1
        if i % 50 == 0:
            print(f"[w000-tr] {i}/{n} done (ok={ok})", flush=True)
        time.sleep(args.sleep)

    pd.DataFrame(price_rows).to_csv(OUT / "kr_total_return_prices_2018_2026.csv", index=False, lineterminator="\n")
    pd.DataFrame(div_rows).to_csv(OUT / "kr_dividend_ledger.csv", index=False, lineterminator="\n")
    pd.DataFrame(split_rows).to_csv(OUT / "kr_split_ledger.csv", index=False, lineterminator="\n")
    pd.DataFrame(manifest).to_csv(OUT / "acquisition_manifest.csv", index=False, lineterminator="\n")
    print(f"[w000-tr] DONE: {ok}/{n} tickers ok; "
          f"prices={len(price_rows)} divs={len(div_rows)} splits={len(split_rows)}", flush=True)


if __name__ == "__main__":
    main()
