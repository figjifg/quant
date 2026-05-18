from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.data.sector_aggregator import (
    DEFAULT_CONFIG,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SECTOR_OUTPUT,
    DEFAULT_STOCK_OUTPUT,
    KOSPI_BREADTH,
    PANEL_COLUMNS,
    SECTOR_CODES_12,
    SectorAggregateResult,
    _build_aggregate_summary,
    _build_d013_sector_distribution,
    _build_sanity_diagnostics,
    _build_sector_daily,
    _build_universe_daily_return,
    _build_validation,
    _coerce_bool,
    _kospi_correlation,
    _read_panel,
    _unmapped_stocks,
)


DEFAULT_PIT_CLASSIFICATIONS = Path("data/processed/krx_pit_sector_classifications.csv")
DEFAULT_PIT_MAPPING_YAML = Path("configs/krx_pit_to_12group.yaml")
DEFAULT_PIT_STOCK_OUTPUT = Path("data/processed/stock_with_sector_daily_pit.csv")
DEFAULT_PIT_SECTOR_OUTPUT = Path("data/processed/sector_aggregate_daily_pit.csv")
DEFAULT_PIT_MAPPING_OUTPUT = Path("data/processed/stock_sector_mapping_pit_daily.csv")
DEFAULT_P001_OUTPUT_DIR = Path("reports/experiments/P001_pit_sector_validation")
D013_SIGNALS = Path("reports/experiments/D013_d009_threshold_minus_0p2/signals.csv")


@dataclass(frozen=True)
class PitSectorAggregateResult:
    base: SectorAggregateResult
    mapping_daily: pd.DataFrame
    stage3_mapping_table: pd.DataFrame
    stage4_summary: pd.DataFrame
    manual_review: dict[str, str]


def build_pit_sector_aggregate(
    *,
    config_path: str | Path = DEFAULT_CONFIG,
    pit_classifications_path: str | Path = DEFAULT_PIT_CLASSIFICATIONS,
    mapping_yaml_path: str | Path = DEFAULT_PIT_MAPPING_YAML,
    kospi_path: str | Path = KOSPI_BREADTH,
    d013_signals_path: str | Path = D013_SIGNALS,
) -> PitSectorAggregateResult:
    config_path = Path(config_path)
    config = _load_yaml(config_path)
    panel = _load_filtered_panels(config_path.parent.parent.parent, config)
    mapping_yaml = _load_yaml(Path(mapping_yaml_path))
    pit_classifications = _load_pit_classifications(Path(pit_classifications_path), mapping_yaml)
    stock_daily = _join_pit_sector_mapping(panel, pit_classifications)
    unmapped_stocks = _unmapped_stocks(stock_daily)
    sector_daily = _build_sector_daily(stock_daily)
    aggregate_summary = _build_aggregate_summary(sector_daily)
    sanity_diagnostics = _build_sanity_diagnostics(sector_daily)
    universe_daily = _build_universe_daily_return(stock_daily)
    kospi_correlation = _kospi_correlation(universe_daily, Path(kospi_path))
    mapping_daily = _stock_sector_mapping_daily(stock_daily)
    d013_distribution = _build_d013_sector_distribution(Path(d013_signals_path), _latest_mapping(mapping_daily))
    validation = _build_validation(
        stock_daily=stock_daily,
        sector_daily=sector_daily,
        aggregate_summary=aggregate_summary,
        sanity_diagnostics=sanity_diagnostics,
        unmapped_stocks=unmapped_stocks,
        kospi_correlation=kospi_correlation,
        d013_distribution=d013_distribution,
    )
    base = SectorAggregateResult(
        stock_daily=stock_daily,
        sector_daily=sector_daily,
        unmapped_stocks=unmapped_stocks,
        aggregate_summary=aggregate_summary,
        sanity_diagnostics=sanity_diagnostics,
        d013_sector_distribution=d013_distribution,
        validation=validation,
    )
    return PitSectorAggregateResult(
        base=base,
        mapping_daily=mapping_daily,
        stage3_mapping_table=_stage3_mapping_table(mapping_yaml),
        stage4_summary=_stage4_summary(stock_daily, sector_daily, aggregate_summary),
        manual_review={str(k): str(v) for k, v in mapping_yaml.get("manual_review", {}).items()},
    )


def write_pit_sector_aggregate_outputs(
    result: PitSectorAggregateResult,
    *,
    stock_output: str | Path = DEFAULT_PIT_STOCK_OUTPUT,
    sector_output: str | Path = DEFAULT_PIT_SECTOR_OUTPUT,
    mapping_output: str | Path = DEFAULT_PIT_MAPPING_OUTPUT,
    output_dir: str | Path = DEFAULT_P001_OUTPUT_DIR,
) -> None:
    stock_output = Path(stock_output)
    sector_output = Path(sector_output)
    mapping_output = Path(mapping_output)
    output_dir = Path(output_dir)
    stock_output.parent.mkdir(parents=True, exist_ok=True)
    sector_output.parent.mkdir(parents=True, exist_ok=True)
    mapping_output.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    result.base.stock_daily.to_csv(stock_output, index=False, encoding="utf-8-sig")
    result.base.sector_daily.to_csv(sector_output, index=False, encoding="utf-8-sig")
    result.mapping_daily.to_csv(mapping_output, index=False, encoding="utf-8-sig")
    result.stage4_summary.to_csv(output_dir / "stage4_pit_aggregate_summary.csv", index=False, encoding="utf-8-sig")
    result.base.unmapped_stocks.to_csv(output_dir / "stage4_unmapped_stocks.csv", index=False, encoding="utf-8-sig")
    result.base.sanity_diagnostics.to_csv(output_dir / "stage4_sanity_diagnostics.csv", index=False, encoding="utf-8-sig")
    _write_stage3_mapping_table(output_dir / "stage3_mapping_table.md", result.stage3_mapping_table)
    _write_manual_review_log(output_dir / "manual_review_log.md", result.manual_review)


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


def _load_pit_classifications(path: Path, mapping_yaml: dict[str, Any]) -> pd.DataFrame:
    raw = pd.read_csv(path, encoding="utf-8-sig", dtype={"종목코드": "string"})
    required = {"date", "market", "종목코드", "종목명", "업종명"}
    missing = sorted(required - set(raw.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")

    industry_mapping = {str(k): str(v) for k, v in mapping_yaml["krx_industry_mapping"].items()}
    groups = {str(k): str(v) for k, v in mapping_yaml["groups"].items()}
    unmapped = sorted(set(raw["업종명"].dropna().astype(str)) - set(industry_mapping))
    if unmapped:
        raise ValueError(f"KRX PIT industries are missing from mapping yaml: {unmapped}")

    frame = raw.loc[:, ["date", "market", "종목코드", "종목명", "업종명"]].copy()
    frame["classification_date"] = pd.to_datetime(frame["date"], format="%Y%m%d", errors="raise")
    frame["ticker"] = frame["종목코드"].astype("string").str.zfill(6)
    frame["final_sector_code"] = frame["업종명"].astype(str).map(industry_mapping).astype("string").str.zfill(2)
    frame["final_sector_name"] = frame["final_sector_code"].map(groups)
    if frame["final_sector_name"].isna().any():
        bad = sorted(frame.loc[frame["final_sector_name"].isna(), "final_sector_code"].dropna().unique())
        raise ValueError(f"Mapping yaml refers to unknown group codes: {bad}")
    frame = frame.sort_values(["ticker", "classification_date"])
    return frame.loc[
        :,
        [
            "classification_date",
            "ticker",
            "종목명",
            "market",
            "업종명",
            "final_sector_code",
            "final_sector_name",
        ],
    ].drop_duplicates(["classification_date", "ticker"], keep="last")


def _join_pit_sector_mapping(panel: pd.DataFrame, pit: pd.DataFrame) -> pd.DataFrame:
    left = panel.sort_values(["date", "ticker"]).copy()
    right = pit.sort_values(["classification_date", "ticker"]).copy()
    joined = pd.merge_asof(
        left,
        right,
        left_on="date",
        right_on="classification_date",
        by="ticker",
        direction="backward",
        allow_exact_matches=True,
    )
    joined = joined.rename(
        columns={"final_sector_code": "sector_code", "final_sector_name": "sector_name"}
    )
    columns = [
        "date",
        "ticker",
        "sector_code",
        "sector_name",
        "classification_date",
        "업종명",
        "market_cap",
        "traded_value",
        "foreign_net_buy_amount",
        "foreign_net_buy_shares",
        "institution_net_buy_amount",
        "institution_net_buy_shares",
        "daily_return",
    ]
    return joined.loc[:, columns].sort_values(["date", "ticker"]).reset_index(drop=True)


def _stock_sector_mapping_daily(stock_daily: pd.DataFrame) -> pd.DataFrame:
    rows = stock_daily.loc[stock_daily["sector_code"].notna()].copy()
    result = rows.loc[:, ["date", "ticker", "sector_code", "sector_name", "classification_date", "업종명"]].copy()
    result = result.rename(
        columns={
            "sector_code": "final_sector_code",
            "sector_name": "final_sector_name",
            "업종명": "krx_industry_name",
        }
    )
    return result.sort_values(["date", "ticker"]).drop_duplicates(["date", "ticker"], keep="last")


def _latest_mapping(mapping_daily: pd.DataFrame) -> pd.DataFrame:
    return (
        mapping_daily.sort_values(["date", "ticker"])
        .drop_duplicates("ticker", keep="last")
        .loc[:, ["ticker", "final_sector_code", "final_sector_name"]]
    )


def _stage3_mapping_table(mapping_yaml: dict[str, Any]) -> pd.DataFrame:
    groups = {str(k): str(v) for k, v in mapping_yaml["groups"].items()}
    industry_mapping = {str(k): str(v) for k, v in mapping_yaml["krx_industry_mapping"].items()}
    review = {str(k): str(v) for k, v in mapping_yaml.get("manual_review", {}).items()}
    rows = []
    for industry, code in sorted(industry_mapping.items()):
        rows.append(
            {
                "krx_industry": industry,
                "custom_group_code": code,
                "custom_group": f"{code} {groups[code]}",
                "manual_review": review.get(industry, ""),
            }
        )
    return pd.DataFrame(rows)


def _stage4_summary(
    stock_daily: pd.DataFrame,
    sector_daily: pd.DataFrame,
    aggregate_summary: pd.DataFrame,
) -> pd.DataFrame:
    quarter_rows = stock_daily.loc[stock_daily["date"].isin(aggregate_summary["date"])].copy()
    mapped_ratio = float(stock_daily["sector_code"].notna().mean()) if len(stock_daily) else 0.0
    return pd.DataFrame(
        [
            {
                "stock_daily_rows": int(len(stock_daily)),
                "stock_daily_dates": int(stock_daily["date"].nunique()),
                "stock_daily_tickers": int(stock_daily["ticker"].nunique()),
                "mapped_row_ratio": mapped_ratio,
                "sector_daily_rows": int(len(sector_daily)),
                "sector_daily_dates": int(sector_daily["date"].nunique()),
                "sector_count": int(sector_daily["sector_code"].nunique()),
                "quarter_count": int(len(aggregate_summary)),
                "quarter_end_universe_rows": int(len(quarter_rows)),
                "quarter_end_sector_count_min": int(
                    quarter_rows.groupby("date")["sector_code"].nunique().min()
                )
                if not quarter_rows.empty
                else 0,
                "quarter_end_sector_count_max": int(
                    quarter_rows.groupby("date")["sector_code"].nunique().max()
                )
                if not quarter_rows.empty
                else 0,
                "quarters_ge_8_non_thin_groups": int(aggregate_summary["hard_pass_ge_8_non_thin_groups"].sum()),
            }
        ]
    )


def _write_stage3_mapping_table(path: Path, table: pd.DataFrame) -> None:
    lines = ["# Stage 3 KRX PIT 41 Industry Mapping", ""]
    columns = list(table.columns)
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
    for _, row in table.iterrows():
        values = [str(row[column]).replace("|", "\\|") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_manual_review_log(path: Path, manual_review: dict[str, str]) -> None:
    lines = ["# P001 Manual Review Log", ""]
    if not manual_review:
        lines.append("- No ambiguous mappings recorded.")
    else:
        for industry, reason in sorted(manual_review.items()):
            lines.append(f"- {industry}: {reason}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build P001 PIT sector aggregate outputs.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--pit-classifications", default=str(DEFAULT_PIT_CLASSIFICATIONS))
    parser.add_argument("--mapping-yaml", default=str(DEFAULT_PIT_MAPPING_YAML))
    parser.add_argument("--stock-output", default=str(DEFAULT_PIT_STOCK_OUTPUT))
    parser.add_argument("--sector-output", default=str(DEFAULT_PIT_SECTOR_OUTPUT))
    parser.add_argument("--mapping-output", default=str(DEFAULT_PIT_MAPPING_OUTPUT))
    parser.add_argument("--output-dir", default=str(DEFAULT_P001_OUTPUT_DIR))
    args = parser.parse_args()

    result = build_pit_sector_aggregate(
        config_path=args.config,
        pit_classifications_path=args.pit_classifications,
        mapping_yaml_path=args.mapping_yaml,
    )
    write_pit_sector_aggregate_outputs(
        result,
        stock_output=args.stock_output,
        sector_output=args.sector_output,
        mapping_output=args.mapping_output,
        output_dir=args.output_dir,
    )
    print(f"P001 PIT rows: {len(result.base.stock_daily)}")
    print(f"P001 mapped ratio: {result.base.validation['sector_mapping_matching_ratio']:.8f}")


if __name__ == "__main__":
    main()
