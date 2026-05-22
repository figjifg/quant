from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.ops.nav_update import ROOT, add_nav_metrics, load_component_nav

T004_NAV_CSV = ROOT / "reports/experiments/T004_account_vehicle_study/daily_nav_by_vehicle.csv"
ETF_DIR = ROOT / "research_input_data/inputs/global_etf"
USDKRW_CSV = ROOT / "research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv"
OUTPUT_DIR = ROOT / "paper_trading/operations/nav_history"
P08_IEF30 = {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "IEF": 0.30}
DEFENSIVE_SHADOW_CANDIDATES = {
    "N002_B_cash_10_shadow": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "CASH": 0.10},
    "N001_B_GLD_10_shadow": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "GLD": 0.10},
}


def compute_gross_tax_nav(
    p08_ief30: dict[str, float] | None = None,
    as_of_date: str | pd.Timestamp | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """Track primary 4 NAV versions plus N-family defensive shadow candidates."""

    as_of = pd.Timestamp(as_of_date) if as_of_date else None
    weights = p08_ief30 or P08_IEF30
    component_nav = load_component_nav(as_of)
    gross = sum(component_nav[ticker] * weight for ticker, weight in weights.items())

    tax_nav = pd.read_csv(T004_NAV_CSV, parse_dates=["date"])
    if as_of is not None:
        tax_nav = tax_nav.loc[tax_nav["date"].le(as_of)]

    frame = pd.DataFrame(
        {
            "date": gross.index,
            "Gross_P08_IEF30": gross.values,
        }
    ).merge(
        tax_nav[["date", "T004-V1_net_nav", "T004-MIX1_net_nav", "T004-V4_net_nav"]],
        on="date",
        how="inner",
    )
    frame = frame.rename(
        columns={
            "T004-V1_net_nav": "V1_taxable_P08_IEF30",
            "T004-MIX1_net_nav": "MIX1_practical_shadow",
            "T004-V4_net_nav": "V4_pension_only_shadow",
        }
    )

    shadow_component_nav = load_defensive_shadow_component_nav(as_of)
    for version, shadow_weights in DEFENSIVE_SHADOW_CANDIDATES.items():
        shadow_nav = sum(shadow_component_nav[ticker] * weight for ticker, weight in shadow_weights.items())
        shadow_frame = pd.DataFrame({"date": shadow_nav.index, version: shadow_nav.values})
        frame = frame.merge(shadow_frame, on="date", how="inner")

    records = []
    for column in frame.columns.drop("date"):
        item = add_nav_metrics(frame[["date", column]].rename(columns={column: "nav"}))
        item.insert(1, "version", column)
        records.append(item)
    output = pd.concat(records, ignore_index=True)
    path = Path(output_path) if output_path else OUTPUT_DIR / f"gross_tax_nav_{output['date'].max():%Y-%m-%d}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(path, index=False)
    return path


def load_defensive_shadow_component_nav(as_of: pd.Timestamp | None = None) -> pd.DataFrame:
    base = load_component_nav(as_of).copy()

    gld = pd.read_csv(ETF_DIR / "yf_GLD.csv", parse_dates=["Date"])
    gld = gld.rename(columns={"Date": "date", "Close": "GLD"})[["date", "GLD"]]

    usdk = pd.read_csv(USDKRW_CSV, parse_dates=["observation_date"], na_values=["."])
    usdk["DEXKOUS"] = pd.to_numeric(usdk["DEXKOUS"], errors="coerce")
    usdk = usdk.rename(columns={"observation_date": "date", "DEXKOUS": "USDKRW"})[["date", "USDKRW"]]

    frame = (
        base.reset_index()
        .merge(gld, on="date", how="left")
        .merge(usdk, on="date", how="left")
        .sort_values("date")
    )
    if as_of is not None:
        frame = frame.loc[frame["date"].le(as_of)]
    frame["USDKRW"] = frame["USDKRW"].ffill()
    frame["GLD"] = frame["GLD"].ffill()
    frame = frame.dropna(subset=["SPY", "QQQ", "H001", "IEF", "GLD", "USDKRW"]).copy()
    frame["GLD"] = frame["GLD"] * frame["USDKRW"]
    frame["GLD"] = frame["GLD"] / frame["GLD"].iloc[0]
    frame["CASH"] = 1.0
    return frame.set_index("date")[["SPY", "QQQ", "H001", "IEF", "GLD", "CASH"]]


if __name__ == "__main__":
    print(compute_gross_tax_nav(as_of_date="2026-05-18").relative_to(ROOT))
