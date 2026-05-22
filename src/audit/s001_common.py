from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
S000_DIR = ROOT / "reports/experiments/S000_korean_short_mean_reversion_feasibility"
PANEL_PATHS = [
    ROOT / "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv",
    ROOT / "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv",
]
KOSPI_PROXY_PATH = ROOT / "research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv"
MARKET_FLOW_PATH = ROOT / "research_input_data/inputs/market_flow/kiwoom_market_flow_2018_2026_integrated.csv"

COMMISSION = 0.0025
SLIPPAGE = 0.0005
S000_TAX = 0.22

PRIMARY_SIGNALS = ["r1d_lt_m3_hold1", "r1d_lt_m3_hold3", "r1d_lt_m3_hold5"]
CRISIS_SIGNAL = "r3d_lt_m7_hold3"
REJECTED_PREFIX = "volume_z"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_s000_trades() -> pd.DataFrame:
    trades = pd.read_csv(S000_DIR / "trades.csv", dtype={"ticker": str}, parse_dates=["signal_date", "execution_date", "exit_date"])
    trades["ticker"] = trades["ticker"].str.zfill(6)
    return trades


def read_s000_random() -> pd.DataFrame:
    random_path = S000_DIR / "random_control_distribution.csv"
    if not random_path.exists():
        return pd.DataFrame()
    random = pd.read_csv(random_path, dtype={"ticker": str}, parse_dates=["signal_date", "execution_date", "exit_date"])
    random["ticker"] = random["ticker"].str.zfill(6)
    return random


def read_s000_metrics() -> dict:
    with (S000_DIR / "metrics.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def read_panel(filtered: bool = False) -> pd.DataFrame:
    frames = []
    for path in PANEL_PATHS:
        data = pd.read_csv(path, encoding="utf-8-sig", dtype={"종목코드": str}, parse_dates=["날짜"])
        data["종목코드"] = data["종목코드"].str.zfill(6)
        if "KRX종가" not in data.columns:
            data["KRX종가"] = data["종가"]
            data["krx_close_source"] = "synthesized_from_pre_nxt_close"
        else:
            data["krx_close_source"] = "on_disk_krx_close"
        for column in ["시가", "종가", "KRX종가", "거래대금추정", "시가총액추정", "기관순매수금액추정", "외국인순매수금액추정"]:
            if column in data.columns:
                data[column] = pd.to_numeric(data[column], errors="coerce")
        frames.append(data)
    panel = pd.concat(frames, ignore_index=True).sort_values(["종목코드", "날짜"]).reset_index(drop=True)
    if filtered:
        panel = panel.loc[
            panel["동적유니버스포함"].eq(True)
            & panel["거래대금추정여부"].eq(False)
            & panel["시가"].gt(0)
            & panel["KRX종가"].gt(0)
            & panel["거래대금추정"].gt(0)
        ].copy()
    return panel


def trading_calendar(panel: pd.DataFrame) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(sorted(panel.loc[panel["KRX종가"].notna(), "날짜"].drop_duplicates()))


def next_trade_date(calendar: pd.DatetimeIndex, date: pd.Timestamp, n: int = 1) -> pd.Timestamp | pd.NaT:
    pos = calendar.searchsorted(pd.Timestamp(date), side="right") + n - 1
    if pos >= len(calendar):
        return pd.NaT
    return calendar[pos]


def add_panel_features(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.sort_values(["종목코드", "날짜"]).copy()
    group = out.groupby("종목코드", sort=False)
    out["ret_1d"] = group["KRX종가"].pct_change(1)
    out["ret_3d"] = group["KRX종가"].pct_change(3)
    out["ret_5d"] = group["KRX종가"].pct_change(5)
    out["gap_open"] = out["시가"] / group["KRX종가"].shift(1) - 1.0
    out["intraday_return"] = out["KRX종가"] / out["시가"] - 1.0
    out["volatility_20d"] = group["ret_1d"].transform(lambda x: x.rolling(20, min_periods=10).std())
    out["mcap_rank_date"] = out.groupby("날짜")["시가총액추정"].rank(ascending=False, method="first")
    out["mcap_bucket"] = pd.cut(out["mcap_rank_date"], bins=[0, 50, 100, np.inf], labels=["large_top50", "mid_51_100", "other"])
    return out


def cost_adjusted_return(gross_return: float, commission: float = COMMISSION, slippage: float = SLIPPAGE, tax_rate: float = S000_TAX) -> float:
    return float(gross_return - 2.0 * (commission + slippage) - max(gross_return, 0.0) * tax_rate)


def summary_metrics(returns: pd.Series, holding_days: float = 1.0) -> dict[str, float | int]:
    clean = pd.to_numeric(returns, errors="coerce").dropna()
    if clean.empty:
        return {"count": 0, "mean": 0.0, "median": 0.0, "hit_rate": 0.0, "sharpe_like": 0.0}
    std = clean.std(ddof=1)
    return {
        "count": int(clean.size),
        "mean": float(clean.mean()),
        "median": float(clean.median()),
        "hit_rate": float((clean > 0.0).mean()),
        "sharpe_like": float(clean.mean() / std * math.sqrt(252.0 / holding_days)) if std and not np.isnan(std) else 0.0,
    }


def nav_metrics(nav: pd.DataFrame, nav_col: str = "nav") -> dict[str, float | int]:
    if nav.empty:
        return {"days": 0, "total_return": 0.0, "cagr": 0.0, "sharpe": 0.0, "mdd": 0.0}
    values = nav[nav_col].astype(float)
    daily = values.pct_change().fillna(0.0)
    years = max((pd.to_datetime(nav["date"]).max() - pd.to_datetime(nav["date"]).min()).days / 365.25, 1 / 365.25)
    peak = values.cummax()
    dd = values / peak - 1.0
    return {
        "days": int(len(nav)),
        "total_return": float(values.iloc[-1] / values.iloc[0] - 1.0),
        "cagr": float((values.iloc[-1] / values.iloc[0]) ** (1.0 / years) - 1.0),
        "sharpe": float(daily.mean() / daily.std(ddof=1) * math.sqrt(252.0)) if daily.std(ddof=1) else 0.0,
        "mdd": float(dd.min()),
    }


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_empty_"
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for _, row in frame.iterrows():
        vals = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                vals.append(f"{value:.6f}")
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(path: Path, title: str, sections: list[tuple[str, str]]) -> None:
    lines = [f"# {title}", ""]
    for heading, body in sections:
        lines.extend([f"## {heading}", "", body, ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
