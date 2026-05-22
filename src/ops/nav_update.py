from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
USDKRW_CSV = ROOT / "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv"
H001_EQUITY_CSV = ROOT / "reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv"
OUTPUT_DIR = ROOT / "paper_trading/operations/nav_history"

DEFAULT_PORTFOLIOS: dict[str, dict[str, float]] = {
    "P08_IEF30": {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30},
    "P08": {"SPY": 0.40, "QQQ": 0.30, "H001": 0.20, "IEF": 0.10},
    "P07": {"QQQ": 0.50, "H001": 0.30, "IEF": 0.20},
    "P07_IEF30": {"QQQ": 0.40, "H001": 0.30, "IEF": 0.30},
    "QQQ": {"QQQ": 1.00},
    "SPY": {"SPY": 1.00},
    "QQQ_SPY_50_50": {"QQQ": 0.50, "SPY": 0.50},
    "H001": {"H001": 1.00},
    "IEF": {"IEF": 1.00},
}


def compute_daily_nav(
    portfolios: dict[str, dict[str, float]] | None = None,
    as_of_date: str | pd.Timestamp | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """Compute paper daily NAV and rolling metrics for the 9 tracked portfolios."""

    as_of = pd.Timestamp(as_of_date) if as_of_date else None
    portfolio_weights = portfolios or DEFAULT_PORTFOLIOS
    component_nav = load_component_nav(as_of)
    records = []
    for portfolio, weights in portfolio_weights.items():
        nav = sum(component_nav[ticker] * weight for ticker, weight in weights.items())
        frame = pd.DataFrame({"date": component_nav.index, "portfolio": portfolio, "nav": nav.values})
        frame = add_nav_metrics(frame)
        records.append(frame)

    output = pd.concat(records, ignore_index=True)
    path = Path(output_path) if output_path else OUTPUT_DIR / f"nav_update_{output['date'].max():%Y-%m-%d}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(path, index=False)
    return path


def load_component_nav(as_of: pd.Timestamp | None = None) -> pd.DataFrame:
    prices = []
    for ticker in ("SPY", "QQQ", "IEF"):
        frame = pd.read_csv(ETF_DIR / f"yf_{ticker}.csv", parse_dates=["Date"])
        frame = frame.rename(columns={"Date": "date", "Close": ticker})[["date", ticker]]
        prices.append(frame)

    usdk = pd.read_csv(USDKRW_CSV, parse_dates=["observation_date"], na_values=["."])
    usdk["DEXKOUS"] = pd.to_numeric(usdk["DEXKOUS"], errors="coerce")
    usdk = usdk.rename(columns={"observation_date": "date", "DEXKOUS": "USDKRW"})[["date", "USDKRW"]]

    h001 = pd.read_csv(H001_EQUITY_CSV, parse_dates=["date"])
    h001 = h001.rename(columns={"net_value": "H001"})[["date", "H001"]]

    frame = prices[0]
    for price in prices[1:]:
        frame = frame.merge(price, on="date", how="outer")
    frame = frame.merge(usdk, on="date", how="left").merge(h001, on="date", how="left")
    frame = frame.sort_values("date")
    if as_of is not None:
        frame = frame.loc[frame["date"].le(as_of)]
    frame["USDKRW"] = frame["USDKRW"].ffill()
    frame[["SPY", "QQQ", "IEF", "H001"]] = frame[["SPY", "QQQ", "IEF", "H001"]].ffill()
    frame = frame.dropna(subset=["SPY", "QQQ", "IEF", "H001", "USDKRW"]).copy()

    for ticker in ("SPY", "QQQ", "IEF"):
        frame[ticker] = frame[ticker] * frame["USDKRW"]
        frame[ticker] = frame[ticker] / frame[ticker].iloc[0]
    frame["H001"] = frame["H001"] / frame["H001"].iloc[0]
    return frame.set_index("date")[["SPY", "QQQ", "H001", "IEF"]]


def add_nav_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.sort_values("date").copy()
    daily_return = out["nav"].pct_change()
    out["daily_return"] = daily_return
    out["monthly_return"] = out["nav"] / out.groupby(out["date"].dt.to_period("M"))["nav"].transform("first") - 1.0
    out["quarterly_return"] = out["nav"] / out.groupby(out["date"].dt.to_period("Q"))["nav"].transform("first") - 1.0
    out["ytd_return"] = out["nav"] / out.groupby(out["date"].dt.year)["nav"].transform("first") - 1.0
    out["mdd"] = out["nav"] / out["nav"].cummax() - 1.0
    out["rolling_vol_63d"] = daily_return.rolling(63).std() * (252**0.5)
    out["rolling_sharpe_63d"] = daily_return.rolling(63).mean() / daily_return.rolling(63).std() * (252**0.5)
    return out


if __name__ == "__main__":
    print(compute_daily_nav(as_of_date="2026-05-18").relative_to(ROOT))
