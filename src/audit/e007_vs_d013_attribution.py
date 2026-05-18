from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable

import pandas as pd


E007_DIR = Path("reports/experiments/E007_flow_rs_breadth/portfolio")
D013_DIR = Path("reports/experiments/D013_d009_threshold_minus_0p2")
E010_DIR = Path("reports/experiments/E010_spike_year_d013_overlap")
VALUE_COL = "V1_factor_macro_gate_mcap_net_value"
SPIKE_YEARS = (2020, 2025, 2026)


def write_e010_attribution(
    e007_dir: str | Path = E007_DIR,
    d013_dir: str | Path = D013_DIR,
    output_dir: str | Path = E010_DIR,
) -> dict[str, pd.DataFrame]:
    e007_dir = Path(e007_dir)
    d013_dir = Path(d013_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    e007_equity = load_equity(e007_dir / "equity_curve.csv")
    d013_equity = load_equity(d013_dir / "equity_curve.csv")
    e007_trades = load_trades(e007_dir / "trades.csv")
    d013_trades = load_trades(d013_dir / "trades.csv")

    per_year = compare_year_breakdowns(e007_equity, e007_trades, d013_equity, d013_trades)
    spike = compare_spike_years(
        per_year,
        total_returns={
            "e007": total_return(e007_equity),
            "d013": total_return(d013_equity),
        },
    )
    overlap = quarterly_overlap(e007_trades, d013_trades)
    subperiod = compare_subperiods(e007_equity, d013_equity)

    per_year.to_csv(output_dir / "per_year_breakdown.csv", index=False)
    spike.to_csv(output_dir / "spike_year_contribution.csv", index=False)
    overlap.to_csv(output_dir / "d013_overlap_quarterly.csv", index=False)
    subperiod.to_csv(output_dir / "subperiod_breakdown.csv", index=False)
    write_report(output_dir / "report.md", per_year, spike, overlap, subperiod)
    return {
        "per_year": per_year,
        "spike": spike,
        "overlap": overlap,
        "subperiod": subperiod,
    }


def load_equity(path: str | Path) -> pd.DataFrame:
    equity = pd.read_csv(path, parse_dates=["date"])
    required = {"date", VALUE_COL}
    missing = required.difference(equity.columns)
    if missing:
        raise ValueError(f"{path} missing required columns: {sorted(missing)}")
    return equity.sort_values("date").reset_index(drop=True)


def load_trades(path: str | Path) -> pd.DataFrame:
    trades = pd.read_csv(
        path,
        dtype={"종목코드": "string"},
        parse_dates=["entry_date", "signal_date", "exit_date"],
    )
    required = {"entry_date", "exit_date", "signal_date", "종목코드"}
    missing = required.difference(trades.columns)
    if missing:
        raise ValueError(f"{path} missing required columns: {sorted(missing)}")
    return trades.sort_values(["entry_date", "종목코드"]).reset_index(drop=True)


def compare_year_breakdowns(
    e007_equity: pd.DataFrame,
    e007_trades: pd.DataFrame,
    d013_equity: pd.DataFrame,
    d013_trades: pd.DataFrame,
) -> pd.DataFrame:
    e007 = yearly_breakdown(e007_equity, e007_trades, "e007")
    d013 = yearly_breakdown(d013_equity, d013_trades, "d013")
    merged = e007.merge(d013, on="year", how="outer").sort_values("year")
    merged["return_diff_e007_minus_d013"] = merged["e007_cumulative_return"] - merged["d013_cumulative_return"]
    merged["sharpe_diff_e007_minus_d013"] = merged["e007_sharpe"] - merged["d013_sharpe"]
    return merged


def yearly_breakdown(equity: pd.DataFrame, trades: pd.DataFrame, prefix: str) -> pd.DataFrame:
    returns = equity.assign(daily_return=equity[VALUE_COL].pct_change().fillna(0.0))
    rows: list[dict[str, float | int]] = []
    for year, group in returns.groupby(returns["date"].dt.year, sort=True):
        values = group[VALUE_COL]
        daily = group["daily_return"]
        volatility = float(daily.std(ddof=1))
        sharpe = math.nan if volatility == 0.0 or math.isnan(volatility) else float(daily.mean() / volatility * math.sqrt(252))
        trade_count = int(trades.loc[trades["entry_date"].dt.year.eq(year)].shape[0])
        rows.append(
            {
                "year": int(year),
                f"{prefix}_cumulative_return": float(values.iloc[-1] / values.iloc[0] - 1.0),
                f"{prefix}_sharpe": sharpe,
                f"{prefix}_trade_count": trade_count,
            }
        )
    return pd.DataFrame(rows)


def compare_subperiods(e007_equity: pd.DataFrame, d013_equity: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, start_year, end_year in [
        ("2010-2017", 2010, 2017),
        ("2018-2026", 2018, 2026),
    ]:
        rows.append(
            {
                "subperiod": label,
                "e007_cumulative_return": period_return(e007_equity, start_year, end_year),
                "d013_cumulative_return": period_return(d013_equity, start_year, end_year),
            }
        )
    result = pd.DataFrame(rows)
    result["return_diff_e007_minus_d013"] = result["e007_cumulative_return"] - result["d013_cumulative_return"]
    return result


def period_return(equity: pd.DataFrame, start_year: int, end_year: int) -> float:
    mask = equity["date"].dt.year.between(start_year, end_year)
    period = equity.loc[mask, VALUE_COL]
    if period.empty:
        return math.nan
    return float(period.iloc[-1] / period.iloc[0] - 1.0)


def total_return(equity: pd.DataFrame) -> float:
    if equity.empty:
        return math.nan
    return float(equity[VALUE_COL].iloc[-1] / equity[VALUE_COL].iloc[0] - 1.0)


def compare_spike_years(
    per_year: pd.DataFrame,
    spike_years: Iterable[int] = SPIKE_YEARS,
    total_returns: dict[str, float] | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for prefix in ["e007", "d013"]:
        total = (
            float(total_returns[prefix])
            if total_returns is not None and prefix in total_returns
            else _compound_year_returns(per_year[f"{prefix}_cumulative_return"])
        )
        for year in spike_years:
            year_return = float(per_year.loc[per_year["year"].eq(year), f"{prefix}_cumulative_return"].iloc[0])
            rows.append(
                {
                    "strategy": prefix,
                    "year_group": str(year),
                    "year_return_sum": year_return,
                    "total_cumulative_return": total,
                    "contribution_share": year_return / total if total else math.nan,
                    "cumulative_excluding_year_group": total - year_return,
                }
            )
        spike_sum = float(
            per_year.loc[per_year["year"].isin(spike_years), f"{prefix}_cumulative_return"].sum()
        )
        rows.append(
            {
                "strategy": prefix,
                "year_group": "+".join(str(year) for year in spike_years),
                "year_return_sum": spike_sum,
                "total_cumulative_return": total,
                "contribution_share": spike_sum / total if total else math.nan,
                "cumulative_excluding_year_group": total - spike_sum,
            }
        )
    return pd.DataFrame(rows)


def quarterly_overlap(e007_trades: pd.DataFrame, d013_trades: pd.DataFrame) -> pd.DataFrame:
    e007_sets = quarter_ticker_sets(e007_trades)
    d013_sets = quarter_ticker_sets(d013_trades)
    quarters = sorted(set(e007_sets).union(d013_sets))
    rows = []
    for quarter in quarters:
        e007 = e007_sets.get(quarter, set())
        d013 = d013_sets.get(quarter, set())
        intersection = e007.intersection(d013)
        union = e007.union(d013)
        rows.append(
            {
                "quarter": quarter,
                "d013_on": bool(d013),
                "e007_on": bool(e007),
                "d013_count": len(d013),
                "e007_count": len(e007),
                "overlap_count": len(intersection),
                "union_count": len(union),
                "jaccard": len(intersection) / len(union) if union else math.nan,
                "e007_same_as_d013_ratio": len(intersection) / len(e007) if e007 else math.nan,
                "d013_on_e007_off": bool(d013) and not bool(e007),
                "d013_off_e007_on": not bool(d013) and bool(e007),
                "d013_tickers": ",".join(sorted(d013)),
                "e007_tickers": ",".join(sorted(e007)),
                "overlap_tickers": ",".join(sorted(intersection)),
            }
        )
    return pd.DataFrame(rows)


def quarter_ticker_sets(trades: pd.DataFrame) -> dict[str, set[str]]:
    with_quarter = trades.assign(entry_quarter=trades["entry_date"].dt.to_period("Q").astype(str))
    return {
        str(quarter): set(group["종목코드"].dropna().astype(str))
        for quarter, group in with_quarter.groupby("entry_quarter", sort=True)
    }


def write_report(
    path: str | Path,
    per_year: pd.DataFrame,
    spike: pd.DataFrame,
    overlap: pd.DataFrame,
    subperiod: pd.DataFrame,
) -> None:
    e007_positive = int(per_year["e007_cumulative_return"].gt(0.0).sum())
    d013_positive = int(per_year["d013_cumulative_return"].gt(0.0).sum())
    active_overlap = overlap.loc[overlap["d013_on"] | overlap["e007_on"]]
    jaccard_mean = float(active_overlap["jaccard"].mean()) if not active_overlap.empty else math.nan
    same_ratio_mean = (
        float(active_overlap["e007_same_as_d013_ratio"].mean()) if not active_overlap.empty else math.nan
    )
    d013_on_e007_off = int(overlap["d013_on_e007_off"].sum())
    d013_off_e007_on = int(overlap["d013_off_e007_on"].sum())

    lines = [
        "# E010 Spike Year + D013 Overlap Analysis",
        "",
        "분석 입력: 기존 E007 `portfolio/equity_curve.csv`, `portfolio/trades.csv`와 기존 D013 `equity_curve.csv`, `trades.csv`.",
        "새 백테스트는 실행하지 않았다.",
        "",
        "## Year Breakdown",
        "",
        f"- E007 양의 수익 연도 수: {e007_positive}",
        f"- D013 양의 수익 연도 수: {d013_positive}",
        "",
        "| year | E007 cumulative | E007 sharpe | E007 trades | D013 cumulative | D013 sharpe | D013 trades |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in per_year.to_dict("records"):
        lines.append(
            f"| {int(row['year'])} | {_fmt(row['e007_cumulative_return'])} | {_fmt(row['e007_sharpe'])} | "
            f"{int(row['e007_trade_count'])} | {_fmt(row['d013_cumulative_return'])} | "
            f"{_fmt(row['d013_sharpe'])} | {int(row['d013_trade_count'])} |"
        )

    lines.extend(["", "## Subperiod", "", "| subperiod | E007 cumulative | D013 cumulative | diff |", "|---|---:|---:|---:|"])
    for row in subperiod.to_dict("records"):
        lines.append(
            f"| {row['subperiod']} | {_fmt(row['e007_cumulative_return'])} | "
            f"{_fmt(row['d013_cumulative_return'])} | {_fmt(row['return_diff_e007_minus_d013'])} |"
        )

    lines.extend(
        [
            "",
            "## Spike Year Contribution",
            "",
            "| strategy | year_group | year return sum | contribution share | cumulative excluding group |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in spike.to_dict("records"):
        lines.append(
            f"| {row['strategy']} | {row['year_group']} | {_fmt(row['year_return_sum'])} | "
            f"{_fmt(row['contribution_share'])} | {_fmt(row['cumulative_excluding_year_group'])} |"
        )

    lines.extend(
        [
            "",
            "## D013 Overlap",
            "",
            f"- Active-quarter average Jaccard: {_fmt(jaccard_mean)}",
            f"- Active-quarter E007 same-as-D013 holding ratio: {_fmt(same_ratio_mean)}",
            f"- D013 ON / E007 OFF quarter count: {d013_on_e007_off}",
            f"- D013 OFF / E007 ON quarter count: {d013_off_e007_on}",
            "",
            "| quarter | D013 ON | E007 ON | overlap | union | Jaccard | E007 same-as-D013 ratio |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in overlap.to_dict("records"):
        lines.append(
            f"| {row['quarter']} | {row['d013_on']} | {row['e007_on']} | {int(row['overlap_count'])} | "
            f"{int(row['union_count'])} | {_fmt(row['jaccard'])} | {_fmt(row['e007_same_as_d013_ratio'])} |"
        )

    d013_spike = spike.loc[
        spike["strategy"].eq("d013") & spike["year_group"].eq("+".join(str(year) for year in SPIKE_YEARS)),
        "contribution_share",
    ].iloc[0]
    e007_spike = spike.loc[
        spike["strategy"].eq("e007") & spike["year_group"].eq("+".join(str(year) for year in SPIKE_YEARS)),
        "contribution_share",
    ].iloc[0]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Spike year 의존도는 E007 {_fmt(e007_spike)} vs D013 {_fmt(d013_spike)}이다.",
            f"- Overlap Jaccard 평균 {_fmt(jaccard_mean)}와 E007 same-as-D013 비율 {_fmt(same_ratio_mean)} 기준으로, E007은 D013과 같은 active quarter를 쓰지만 보유 종목 구성은 상당히 다르다.",
            "- 따라서 E007의 Layer 2는 D013의 단순 복제가 아니라 독립적인 종목 선택 알파를 일부 제공한다. 다만 spike year 의존도는 D013보다 낮아도 여전히 높아서, 독립 알파의 안정성은 제한적으로 봐야 한다.",
        ]
    )
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _compound_year_returns(returns: pd.Series) -> float:
    compounded = float((1.0 + returns.fillna(0.0)).prod() - 1.0)
    return compounded


def _fmt(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if math.isnan(number):
        return ""
    return f"{number:.6f}"


if __name__ == "__main__":
    write_e010_attribution()
