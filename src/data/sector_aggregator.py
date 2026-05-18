from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DEFAULT_CONFIG = Path("configs/backtests/d013.yaml")
DEFAULT_MAPPING = Path("data/processed/stock_sector_mapping_20260518.csv")
DEFAULT_OUTPUT_DIR = Path("reports/experiments/E002_sector_aggregate")
DEFAULT_STOCK_OUTPUT = Path("data/processed/stock_with_sector_daily.csv")
DEFAULT_SECTOR_OUTPUT = Path("data/processed/sector_aggregate_daily.csv")
D013_SIGNALS = Path("reports/experiments/D013_d009_threshold_minus_0p2/signals.csv")
KOSPI_BREADTH = Path("research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv")
SECTOR_CODES_12 = tuple(f"{i:02d}" for i in range(1, 13))


PANEL_COLUMNS = {
    "날짜": "date",
    "종목코드": "ticker",
    "종목명": "stock_name",
    "Change": "daily_return",
    "시가총액추정": "market_cap",
    "거래대금추정": "traded_value",
    "외국인순매수금액추정": "foreign_net_buy_amount",
    "외국인순매매량": "foreign_net_buy_shares",
    "기관순매수금액추정": "institution_net_buy_amount",
    "기관순매매량": "institution_net_buy_shares",
    "동적유니버스포함": "in_universe",
}


@dataclass(frozen=True)
class SectorAggregateResult:
    stock_daily: pd.DataFrame
    sector_daily: pd.DataFrame
    unmapped_stocks: pd.DataFrame
    aggregate_summary: pd.DataFrame
    sanity_diagnostics: pd.DataFrame
    d013_sector_distribution: pd.DataFrame
    validation: dict[str, Any]


def build_sector_aggregate(
    config_path: str | Path = DEFAULT_CONFIG,
    mapping_path: str | Path = DEFAULT_MAPPING,
    kospi_path: str | Path = KOSPI_BREADTH,
    d013_signals_path: str | Path = D013_SIGNALS,
) -> SectorAggregateResult:
    config_path = Path(config_path)
    mapping_path = Path(mapping_path)
    config = _load_yaml(config_path)

    panel = _load_filtered_panels(config_path.parent.parent.parent, config)
    mapping = _load_mapping(mapping_path)
    stock_daily = _join_sector_mapping(panel, mapping)
    unmapped_stocks = _unmapped_stocks(stock_daily)
    sector_daily = _build_sector_daily(stock_daily)
    aggregate_summary = _build_aggregate_summary(sector_daily)
    sanity_diagnostics = _build_sanity_diagnostics(sector_daily)
    universe_daily = _build_universe_daily_return(stock_daily)
    kospi_correlation = _kospi_correlation(universe_daily, Path(kospi_path))
    d013_distribution = _build_d013_sector_distribution(Path(d013_signals_path), mapping)
    validation = _build_validation(
        stock_daily=stock_daily,
        sector_daily=sector_daily,
        aggregate_summary=aggregate_summary,
        sanity_diagnostics=sanity_diagnostics,
        unmapped_stocks=unmapped_stocks,
        kospi_correlation=kospi_correlation,
        d013_distribution=d013_distribution,
    )

    return SectorAggregateResult(
        stock_daily=stock_daily,
        sector_daily=sector_daily,
        unmapped_stocks=unmapped_stocks,
        aggregate_summary=aggregate_summary,
        sanity_diagnostics=sanity_diagnostics,
        d013_sector_distribution=d013_distribution,
        validation=validation,
    )


def write_sector_aggregate_outputs(
    result: SectorAggregateResult,
    stock_output: str | Path = DEFAULT_STOCK_OUTPUT,
    sector_output: str | Path = DEFAULT_SECTOR_OUTPUT,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> None:
    stock_output = Path(stock_output)
    sector_output = Path(sector_output)
    output_dir = Path(output_dir)
    stock_output.parent.mkdir(parents=True, exist_ok=True)
    sector_output.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    result.stock_daily.to_csv(stock_output, index=False, encoding="utf-8-sig")
    result.sector_daily.to_csv(sector_output, index=False, encoding="utf-8-sig")
    result.unmapped_stocks.to_csv(output_dir / "unmapped_stocks.csv", index=False, encoding="utf-8-sig")
    result.aggregate_summary.to_csv(
        output_dir / "aggregate_summary.csv", index=False, encoding="utf-8-sig"
    )
    result.sanity_diagnostics.to_csv(
        output_dir / "sanity_diagnostics.csv", index=False, encoding="utf-8-sig"
    )
    result.d013_sector_distribution.to_csv(
        output_dir / "d013_sector_distribution.csv", index=False, encoding="utf-8-sig"
    )
    _write_validation_report(output_dir / "validation_report.md", result.validation)
    _write_report(output_dir / "report.md", result.validation)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_filtered_panels(repo_root: Path, config: dict[str, Any]) -> pd.DataFrame:
    filters = config.get("panel_date_filters", {})
    frames = []
    for panel_path in config["panels"]:
        path = repo_root / panel_path
        frame = _read_panel(path)
        date_filter = filters.get(panel_path, {})
        if "start" in date_filter:
            frame = frame.loc[frame["date"] >= pd.Timestamp(date_filter["start"])]
        if "end" in date_filter:
            frame = frame.loc[frame["date"] <= pd.Timestamp(date_filter["end"])]
        frames.append(frame)

    panel = pd.concat(frames, ignore_index=True)
    panel = panel.loc[panel["in_universe"]].copy()
    panel = panel.drop_duplicates(["date", "ticker"], keep="last")
    return panel.sort_values(["date", "ticker"]).reset_index(drop=True)


def _read_panel(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, encoding="utf-8-sig", dtype={"종목코드": "string"})
    missing = sorted(set(PANEL_COLUMNS) - set(raw.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns for E002: {missing}")

    frame = raw.loc[:, list(PANEL_COLUMNS)].rename(columns=PANEL_COLUMNS)
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    frame["ticker"] = frame["ticker"].astype("string").str.zfill(6)
    frame["in_universe"] = _coerce_bool(frame["in_universe"], "동적유니버스포함")

    numeric_columns = [
        "daily_return",
        "market_cap",
        "traded_value",
        "foreign_net_buy_amount",
        "foreign_net_buy_shares",
        "institution_net_buy_amount",
        "institution_net_buy_shares",
    ]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    return frame


def _coerce_bool(series: pd.Series, column: str) -> pd.Series:
    valid = {"True": True, "False": False, True: True, False: False}
    mapped = series.map(valid)
    if mapped.isna().any():
        bad = series.loc[mapped.isna()].iloc[0]
        raise ValueError(f"{column} contains non-boolean value: {bad!r}")
    return mapped.astype(bool)


def _load_mapping(path: Path) -> pd.DataFrame:
    mapping = pd.read_csv(
        path,
        encoding="utf-8-sig",
        dtype={"ticker": "string", "final_sector_code": "string"},
    )
    required = {"ticker", "final_sector_code", "final_sector_name"}
    missing = sorted(required - set(mapping.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")
    mapping = mapping.loc[:, ["ticker", "final_sector_code", "final_sector_name"]].copy()
    mapping["ticker"] = mapping["ticker"].astype("string").str.zfill(6)
    mapping["final_sector_code"] = mapping["final_sector_code"].astype("string").str.zfill(2)
    return mapping.drop_duplicates("ticker", keep="last")


def _join_sector_mapping(panel: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    joined = panel.merge(mapping, on="ticker", how="left", validate="many_to_one")
    joined = joined.rename(
        columns={"final_sector_code": "sector_code", "final_sector_name": "sector_name"}
    )
    columns = [
        "date",
        "ticker",
        "sector_code",
        "sector_name",
        "market_cap",
        "traded_value",
        "foreign_net_buy_amount",
        "foreign_net_buy_shares",
        "institution_net_buy_amount",
        "institution_net_buy_shares",
        "daily_return",
    ]
    return joined.loc[:, columns].sort_values(["date", "ticker"]).reset_index(drop=True)


def _unmapped_stocks(stock_daily: pd.DataFrame) -> pd.DataFrame:
    rows = stock_daily.loc[stock_daily["sector_code"].isna(), ["ticker"]]
    if rows.empty:
        return pd.DataFrame(columns=["ticker", "row_count", "first_date", "last_date"])
    grouped = (
        stock_daily.loc[stock_daily["sector_code"].isna()]
        .groupby("ticker", as_index=False)
        .agg(row_count=("ticker", "size"), first_date=("date", "min"), last_date=("date", "max"))
    )
    return grouped.sort_values(["row_count", "ticker"], ascending=[False, True])


def _build_sector_daily(stock_daily: pd.DataFrame) -> pd.DataFrame:
    rows = stock_daily.loc[stock_daily["sector_code"].notna()].copy()
    rows["market_cap_for_sum"] = rows["market_cap"].fillna(0.0)
    rows["traded_value_for_sum"] = rows["traded_value"].fillna(0.0)
    rows["weighted_return_numerator"] = rows["daily_return"].fillna(0.0) * rows["market_cap_for_sum"]

    grouped = (
        rows.groupby(["date", "sector_code", "sector_name"], as_index=False)
        .agg(
            n_stocks=("ticker", "nunique"),
            sum_market_cap=("market_cap_for_sum", "sum"),
            sum_traded_value=("traded_value_for_sum", "sum"),
            sum_foreign_net_buy_amount=("foreign_net_buy_amount", "sum"),
            sum_foreign_net_buy_shares=("foreign_net_buy_shares", "sum"),
            sum_institution_net_buy_amount=("institution_net_buy_amount", "sum"),
            sum_institution_net_buy_shares=("institution_net_buy_shares", "sum"),
            weighted_return_numerator=("weighted_return_numerator", "sum"),
        )
        .sort_values(["date", "sector_code"])
        .reset_index(drop=True)
    )
    grouped["cap_weighted_return"] = grouped["weighted_return_numerator"] / grouped[
        "sum_market_cap"
    ].replace(0, pd.NA)

    dominance = _market_cap_dominance(rows)
    result = grouped.merge(dominance, on=["date", "sector_code"], how="left")
    result = result.drop(columns=["weighted_return_numerator"])
    ordered = [
        "date",
        "sector_code",
        "sector_name",
        "n_stocks",
        "sum_market_cap",
        "sum_traded_value",
        "sum_foreign_net_buy_amount",
        "sum_foreign_net_buy_shares",
        "sum_institution_net_buy_amount",
        "sum_institution_net_buy_shares",
        "cap_weighted_return",
        "top1_market_cap_pct",
        "top2_market_cap_pct",
    ]
    return result.loc[:, ordered]


def _market_cap_dominance(rows: pd.DataFrame) -> pd.DataFrame:
    ranked = rows.sort_values(["date", "sector_code", "market_cap_for_sum"], ascending=[True, True, False])
    ranked["rank_in_sector"] = ranked.groupby(["date", "sector_code"]).cumcount() + 1
    top = ranked.loc[ranked["rank_in_sector"].isin([1, 2])].copy()
    top["pct"] = top["market_cap_for_sum"] / top.groupby(["date", "sector_code"])[
        "market_cap_for_sum"
    ].transform("sum")
    # Recompute percentage against full sector cap, not only against the top-two subset.
    sector_cap = rows.groupby(["date", "sector_code"])["market_cap_for_sum"].sum()
    top = top.join(sector_cap.rename("sector_market_cap"), on=["date", "sector_code"])
    top["pct"] = top["market_cap_for_sum"] / top["sector_market_cap"].replace(0, pd.NA)
    pivot = top.pivot_table(
        index=["date", "sector_code"],
        columns="rank_in_sector",
        values="pct",
        aggfunc="first",
    ).reset_index()
    pivot = pivot.rename(columns={1: "top1_market_cap_pct", 2: "top2_market_cap_pct"})
    if "top2_market_cap_pct" not in pivot.columns:
        pivot["top2_market_cap_pct"] = 0.0
    return pivot.loc[:, ["date", "sector_code", "top1_market_cap_pct", "top2_market_cap_pct"]]


def _build_aggregate_summary(sector_daily: pd.DataFrame) -> pd.DataFrame:
    quarter_end_dates = (
        sector_daily.groupby(sector_daily["date"].dt.to_period("Q"))["date"].max().sort_values()
    )
    quarter_rows = sector_daily.loc[sector_daily["date"].isin(quarter_end_dates.values)].copy()
    sector_12 = quarter_rows.loc[quarter_rows["sector_code"].isin(SECTOR_CODES_12)]
    summary = (
        sector_12.groupby("date", as_index=False)
        .agg(
            quarter=("date", lambda x: x.iloc[0].to_period("Q").strftime("Q%q-%Y")),
            groups_present=("sector_code", "nunique"),
            groups_with_n_ge_3=("n_stocks", lambda x: int((x >= 3).sum())),
            total_n_stocks=("n_stocks", "sum"),
            total_market_cap=("sum_market_cap", "sum"),
            total_traded_value=("sum_traded_value", "sum"),
        )
        .sort_values("date")
    )
    summary["hard_pass_ge_8_non_thin_groups"] = summary["groups_with_n_ge_3"] >= 8
    return summary


def _build_sanity_diagnostics(sector_daily: pd.DataFrame) -> pd.DataFrame:
    rows = sector_daily.loc[sector_daily["sector_code"].isin(SECTOR_CODES_12)].copy()
    rows["quarter"] = rows["date"].dt.to_period("Q").astype(str)
    rows["thin_sector_flag"] = rows["n_stocks"] <= 2
    rows["breadth_feasible_flag"] = rows["n_stocks"] >= 3
    rows["sector_market_cap_weight"] = rows["sum_market_cap"] / rows.groupby("date")[
        "sum_market_cap"
    ].transform("sum")
    return rows.loc[
        :,
        [
            "date",
            "quarter",
            "sector_code",
            "sector_name",
            "n_stocks",
            "thin_sector_flag",
            "breadth_feasible_flag",
            "sum_market_cap",
            "sector_market_cap_weight",
            "sum_foreign_net_buy_amount",
            "sum_traded_value",
            "cap_weighted_return",
            "top1_market_cap_pct",
            "top2_market_cap_pct",
        ],
    ]


def _build_universe_daily_return(stock_daily: pd.DataFrame) -> pd.DataFrame:
    rows = stock_daily.loc[stock_daily["sector_code"].isin(SECTOR_CODES_12)].copy()
    rows["market_cap_for_sum"] = rows["market_cap"].fillna(0.0)
    rows["weighted_return_numerator"] = rows["daily_return"].fillna(0.0) * rows["market_cap_for_sum"]
    daily = (
        rows.groupby("date", as_index=False)
        .agg(
            sum_market_cap=("market_cap_for_sum", "sum"),
            weighted_return_numerator=("weighted_return_numerator", "sum"),
        )
        .sort_values("date")
    )
    daily["cap_weighted_return"] = daily["weighted_return_numerator"] / daily[
        "sum_market_cap"
    ].replace(0, pd.NA)
    return daily.loc[:, ["date", "cap_weighted_return"]]


def _kospi_correlation(universe_daily: pd.DataFrame, kospi_path: Path) -> float:
    kospi = pd.read_csv(kospi_path, encoding="utf-8-sig", usecols=["date", "cap_weighted_return"])
    kospi["date"] = pd.to_datetime(kospi["date"], errors="raise")
    merged = universe_daily.merge(kospi, on="date", how="inner", suffixes=("_universe", "_kospi"))
    return float(merged["cap_weighted_return_universe"].corr(merged["cap_weighted_return_kospi"]))


def _build_d013_sector_distribution(signals_path: Path, mapping: pd.DataFrame) -> pd.DataFrame:
    if not signals_path.exists():
        return pd.DataFrame(columns=["signal_date", "sector_code", "sector_name", "n_holdings", "tickers"])
    signals = pd.read_csv(
        signals_path,
        encoding="utf-8-sig",
        dtype={"ticker": "string"},
        parse_dates=["signal_date"],
    )
    signals = signals.loc[signals["included_in_trade"]].copy()
    signals["ticker"] = signals["ticker"].astype("string").str.zfill(6)
    joined = signals.merge(mapping, on="ticker", how="left", validate="many_to_one")
    joined = joined.rename(
        columns={"final_sector_code": "sector_code", "final_sector_name": "sector_name"}
    )
    return (
        joined.groupby(["signal_date", "sector_code", "sector_name"], dropna=False, as_index=False)
        .agg(n_holdings=("ticker", "size"), tickers=("ticker", lambda x: " ".join(sorted(x))))
        .sort_values(["signal_date", "sector_code"], na_position="last")
    )


def _build_validation(
    stock_daily: pd.DataFrame,
    sector_daily: pd.DataFrame,
    aggregate_summary: pd.DataFrame,
    sanity_diagnostics: pd.DataFrame,
    unmapped_stocks: pd.DataFrame,
    kospi_correlation: float,
    d013_distribution: pd.DataFrame,
) -> dict[str, Any]:
    total_rows = len(stock_daily)
    mapped_rows = int(stock_daily["sector_code"].notna().sum())
    matching_ratio = mapped_rows / total_rows if total_rows else 0.0
    quarter_count = len(aggregate_summary)
    hard_quarter_count = int(aggregate_summary["hard_pass_ge_8_non_thin_groups"].sum())
    hard_quarter_ratio = hard_quarter_count / quarter_count if quarter_count else 0.0
    thin_quarters = int(
        sanity_diagnostics.loc[sanity_diagnostics["thin_sector_flag"], "quarter"].nunique()
    )
    top1_mean = float(sanity_diagnostics["top1_market_cap_pct"].mean())
    top1_max = float(sanity_diagnostics["top1_market_cap_pct"].max())
    top1_p95 = float(sanity_diagnostics["top1_market_cap_pct"].quantile(0.95))
    top2_mean = float(sanity_diagnostics["top2_market_cap_pct"].fillna(0.0).mean())
    top2_max = float(sanity_diagnostics["top2_market_cap_pct"].fillna(0.0).max())
    top2_p95 = float(sanity_diagnostics["top2_market_cap_pct"].fillna(0.0).quantile(0.95))
    hard_pass = (
        hard_quarter_count == quarter_count
        and kospi_correlation >= 0.7
        and d013_distribution["sector_code"].notna().all()
    )
    return {
        "panel_universe_stock_count": int(stock_daily["ticker"].nunique()),
        "panel_universe_day_count": int(stock_daily["date"].nunique()),
        "stock_daily_rows": int(total_rows),
        "mapped_rows": mapped_rows,
        "unmapped_rows": int(total_rows - mapped_rows),
        "unmapped_stock_count": int(unmapped_stocks["ticker"].nunique()) if not unmapped_stocks.empty else 0,
        "sector_mapping_matching_ratio": matching_ratio,
        "sector_aggregate_rows": int(len(sector_daily)),
        "sector_aggregate_day_count": int(sector_daily["date"].nunique()),
        "sector_aggregate_sector_count": int(sector_daily["sector_code"].nunique()),
        "quarter_count": int(quarter_count),
        "hard_quarter_count_ge_8_non_thin_groups": hard_quarter_count,
        "hard_quarter_ratio_ge_8_non_thin_groups": hard_quarter_ratio,
        "kospi_correlation": kospi_correlation,
        "thin_sector_quarter_count": thin_quarters,
        "top1_market_cap_pct_mean": top1_mean,
        "top1_market_cap_pct_p95": top1_p95,
        "top1_market_cap_pct_max": top1_max,
        "top2_market_cap_pct_mean": top2_mean,
        "top2_market_cap_pct_p95": top2_p95,
        "top2_market_cap_pct_max": top2_max,
        "d013_signal_dates": int(d013_distribution["signal_date"].nunique()) if not d013_distribution.empty else 0,
        "d013_unmapped_holding_rows": int(d013_distribution["sector_code"].isna().sum())
        if not d013_distribution.empty
        else 0,
        "verdict": "PROCEED" if hard_pass else "STOP",
    }


def _write_validation_report(path: Path, validation: dict[str, Any]) -> None:
    lines = [
        "# E002 validation report",
        "",
        "## Hard pass",
        f"- Quarter-end non-thin sector pass: {validation['hard_quarter_count_ge_8_non_thin_groups']} / {validation['quarter_count']} ({validation['hard_quarter_ratio_ge_8_non_thin_groups']:.6f})",
        f"- Universe cap-weighted return vs KOSPI correlation: {validation['kospi_correlation']:.6f}",
        f"- D013 unmapped holding rows: {validation['d013_unmapped_holding_rows']}",
        "",
        "## Diagnostics",
        f"- Thin-sector quarters: {validation['thin_sector_quarter_count']}",
        f"- Top1 market-cap pct mean/p95/max: {validation['top1_market_cap_pct_mean']:.6f} / {validation['top1_market_cap_pct_p95']:.6f} / {validation['top1_market_cap_pct_max']:.6f}",
        f"- Top2 market-cap pct mean/p95/max: {validation['top2_market_cap_pct_mean']:.6f} / {validation['top2_market_cap_pct_p95']:.6f} / {validation['top2_market_cap_pct_max']:.6f}",
        "",
        f"Verdict: {validation['verdict']}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_report(path: Path, validation: dict[str, Any]) -> None:
    lines = [
        "# E002 sector aggregate",
        "",
        "## Metrics summary",
        f"- Panel universe stocks: {validation['panel_universe_stock_count']}",
        f"- Panel universe days: {validation['panel_universe_day_count']}",
        f"- Sector mapping matching ratio: {validation['sector_mapping_matching_ratio']:.8f}",
        f"- Sector aggregate rows: {validation['sector_aggregate_rows']}",
        f"- Quarter hard-pass ratio: {validation['hard_quarter_ratio_ge_8_non_thin_groups']:.8f}",
        f"- KOSPI correlation: {validation['kospi_correlation']:.8f}",
        f"- Thin-sector quarter count: {validation['thin_sector_quarter_count']}",
        f"- Single-name top1 mean/max: {validation['top1_market_cap_pct_mean']:.8f} / {validation['top1_market_cap_pct_max']:.8f}",
        "",
        "## Metadata",
        "- Panels: D013 panels with D013 panel_date_filters only.",
        "- Universe: rows where 동적유니버스포함 is True.",
        "- Dedupe: last row by (date, ticker).",
        "- KOSPI baseline: krx_market_breadth_kospi_2010_2026.csv cap_weighted_return, used for validation only.",
        f"- Verdict: {validation['verdict']}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build E002 sector aggregate outputs.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--mapping", default=str(DEFAULT_MAPPING))
    parser.add_argument("--stock-output", default=str(DEFAULT_STOCK_OUTPUT))
    parser.add_argument("--sector-output", default=str(DEFAULT_SECTOR_OUTPUT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    result = build_sector_aggregate(config_path=args.config, mapping_path=args.mapping)
    write_sector_aggregate_outputs(
        result,
        stock_output=args.stock_output,
        sector_output=args.sector_output,
        output_dir=args.output_dir,
    )
    print(f"E002 verdict: {result.validation['verdict']}")
    print(f"KOSPI correlation: {result.validation['kospi_correlation']:.6f}")


if __name__ == "__main__":
    main()
