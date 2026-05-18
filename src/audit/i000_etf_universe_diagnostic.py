from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


ETF_TICKERS = ("SPY", "QQQ", "IWM", "SHY", "IEF", "TLT", "GLD", "UUP", "DBC")

ETF_DIR = Path("research_input_data/inputs/global_etf")
MACRO_DIR = Path("research_input_data/inputs/macro_features")
D013_DIR = Path("reports/experiments/D013_d009_threshold_minus_0p2")
H001_DIR = Path("reports/experiments/H001_kr_short_rate_sleeve")
OUTPUT_DIR = Path("reports/experiments/I000_us_global_etf_universe")

D013_VALUE_COL = "V1_factor_macro_gate_mcap_net_value"
H001_VALUE_COL = "net_value"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    quarter_dates = load_d013_quarter_dates()
    availability = build_availability()
    quarterly_returns = build_quarterly_returns(quarter_dates)
    correlation_matrix = build_correlation_matrix(quarterly_returns)
    correlation_ranking = build_correlation_ranking(quarterly_returns)

    availability.to_csv(OUTPUT_DIR / "etf_data_availability.csv", index=False)
    quarterly_returns.to_csv(OUTPUT_DIR / "etf_quarterly_returns.csv", index=False)
    correlation_matrix.to_csv(OUTPUT_DIR / "correlation_matrix.csv")
    correlation_ranking.to_csv(OUTPUT_DIR / "correlation_with_d013_h001.csv", index=False)
    write_report(availability, quarterly_returns, correlation_matrix, correlation_ranking)


def load_d013_quarter_dates() -> pd.DataFrame:
    regime = pd.read_csv(D013_DIR / "quarterly_regime_log.csv", parse_dates=["signal_date"])
    required = {"signal_date"}
    missing = required.difference(regime.columns)
    if missing:
        raise ValueError(f"{D013_DIR / 'quarterly_regime_log.csv'} missing columns: {sorted(missing)}")
    dates = regime[["signal_date"]].drop_duplicates().sort_values("signal_date").reset_index(drop=True)
    dates["quarter"] = dates["signal_date"].dt.to_period("Q").astype(str)
    return dates


def build_availability() -> pd.DataFrame:
    rows = []
    for ticker in ETF_TICKERS:
        data = load_etf_prices(ticker)
        rows.append(
            {
                "ticker": ticker,
                "file": str(ETF_DIR / f"yf_{ticker}.csv"),
                "first_date": data["Date"].min().date().isoformat(),
                "last_date": data["Date"].max().date().isoformat(),
                "row_count": int(data.shape[0]),
                "close_non_null_count": int(data["Close"].notna().sum()),
                "all_required_columns_present": True,
            }
        )
    return pd.DataFrame(rows)


def load_etf_prices(ticker: str) -> pd.DataFrame:
    path = ETF_DIR / f"yf_{ticker}.csv"
    data = pd.read_csv(path, parse_dates=["Date"])
    required = {"Date", "Open", "High", "Low", "Close", "Volume"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    data["Close"] = pd.to_numeric(data["Close"], errors="coerce")
    return data.dropna(subset=["Date", "Close"]).sort_values("Date").reset_index(drop=True)


def build_quarterly_returns(quarter_dates: pd.DataFrame) -> pd.DataFrame:
    result = quarter_dates.copy()
    usdk_rw = load_daily_series(MACRO_DIR / "fred_dexkous_usdkrw.csv", "observation_date", "DEXKOUS")
    result = result.merge(
        align_nearest(quarter_dates, usdk_rw, "DEXKOUS", "usdk_rw", "usdk_rw_date"),
        on=["signal_date", "quarter"],
        how="left",
    )
    result["usdk_rw_quarter_change"] = result["usdk_rw"].pct_change()

    for ticker in ETF_TICKERS:
        prices = load_etf_prices(ticker).rename(columns={"Date": "date"})
        aligned = align_nearest(quarter_dates, prices, "Close", f"{ticker}_close_usd", f"{ticker}_price_date")
        result = result.merge(aligned, on=["signal_date", "quarter"], how="left")
        result[f"{ticker}_return_usd"] = result[f"{ticker}_close_usd"].pct_change()
        result[f"{ticker}_return_krw"] = (
            (1.0 + result[f"{ticker}_return_usd"]) * (1.0 + result["usdk_rw_quarter_change"]) - 1.0
        )

    d013 = load_equity_curve(D013_DIR / "equity_curve.csv", D013_VALUE_COL, "D013_value")
    h001 = load_equity_curve(H001_DIR / "equity_curve.csv", H001_VALUE_COL, "H001_value")
    result = result.merge(
        align_nearest(quarter_dates, d013, "D013_value", "D013_value", "D013_value_date"),
        on=["signal_date", "quarter"],
        how="left",
    )
    result = result.merge(
        align_nearest(quarter_dates, h001, "H001_value", "H001_value", "H001_value_date"),
        on=["signal_date", "quarter"],
        how="left",
    )
    result["D013_return"] = result["D013_value"].pct_change()
    result["H001_return"] = result["H001_value"].pct_change()
    return result


def load_daily_series(path: Path, date_col: str, value_col: str) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=[date_col], na_values=["."])
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")
    return (
        data.dropna(subset=[date_col, value_col])
        .rename(columns={date_col: "date"})
        .sort_values("date")
        .reset_index(drop=True)
    )


def load_equity_curve(path: Path, value_col: str, output_col: str) -> pd.DataFrame:
    equity = pd.read_csv(path, parse_dates=["date"])
    required = {"date", value_col}
    missing = required.difference(equity.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    equity[output_col] = pd.to_numeric(equity[value_col], errors="coerce")
    return equity.dropna(subset=["date", output_col])[["date", output_col]].sort_values("date").reset_index(drop=True)


def align_nearest(
    quarter_dates: pd.DataFrame,
    data: pd.DataFrame,
    value_col: str,
    output_col: str,
    date_output_col: str,
) -> pd.DataFrame:
    frames = []
    source = data[["date", value_col]].dropna().sort_values("date").reset_index(drop=True)
    for direction in ["backward", "forward"]:
        aligned = pd.merge_asof(
            quarter_dates.sort_values("signal_date"),
            source,
            left_on="signal_date",
            right_on="date",
            direction=direction,
        )
        aligned = aligned.rename(columns={"date": f"{direction}_date", value_col: f"{direction}_value"})
        frames.append(aligned[["signal_date", "quarter", f"{direction}_date", f"{direction}_value"]])

    merged = frames[0].merge(frames[1], on=["signal_date", "quarter"], how="outer")
    backward_gap = (merged["signal_date"] - merged["backward_date"]).abs()
    forward_gap = (merged["forward_date"] - merged["signal_date"]).abs()
    use_forward = merged["backward_value"].isna() | (
        merged["forward_value"].notna() & forward_gap.lt(backward_gap)
    )
    merged[output_col] = merged["backward_value"].where(~use_forward, merged["forward_value"])
    merged[date_output_col] = merged["backward_date"].where(~use_forward, merged["forward_date"])
    return merged[["signal_date", "quarter", date_output_col, output_col]]


def build_correlation_matrix(quarterly_returns: pd.DataFrame) -> pd.DataFrame:
    returns = select_correlation_returns(quarterly_returns)
    return returns.corr(method="pearson")


def select_correlation_returns(quarterly_returns: pd.DataFrame) -> pd.DataFrame:
    columns = [f"{ticker}_return_krw" for ticker in ETF_TICKERS] + ["D013_return", "H001_return"]
    returns = quarterly_returns[columns].copy()
    return returns.rename(columns={f"{ticker}_return_krw": ticker for ticker in ETF_TICKERS})


def build_correlation_ranking(quarterly_returns: pd.DataFrame) -> pd.DataFrame:
    returns = select_correlation_returns(quarterly_returns)
    rows = []
    for ticker in ETF_TICKERS:
        pair_d013 = returns[[ticker, "D013_return"]].dropna()
        pair_h001 = returns[[ticker, "H001_return"]].dropna()
        rows.append(
            {
                "ticker": ticker,
                "pearson_d013": pair_d013[ticker].corr(pair_d013["D013_return"], method="pearson"),
                "spearman_d013": pair_d013[ticker].corr(pair_d013["D013_return"], method="spearman"),
                "n_d013": int(pair_d013.shape[0]),
                "pearson_h001": pair_h001[ticker].corr(pair_h001["H001_return"], method="pearson"),
                "spearman_h001": pair_h001[ticker].corr(pair_h001["H001_return"], method="spearman"),
                "n_h001": int(pair_h001.shape[0]),
            }
        )
    ranking = pd.DataFrame(rows)
    ranking["max_abs_pearson_vs_d013_h001"] = ranking[["pearson_d013", "pearson_h001"]].abs().max(axis=1)
    ranking["low_correlation_candidate"] = ranking["max_abs_pearson_vs_d013_h001"].le(0.3)
    return ranking.sort_values(["max_abs_pearson_vs_d013_h001", "ticker"]).reset_index(drop=True)


def cumulative_krw_returns(quarterly_returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ticker in ETF_TICKERS:
        returns = quarterly_returns[f"{ticker}_return_krw"].dropna()
        rows.append(
            {
                "ticker": ticker,
                "n_quarters": int(returns.shape[0]),
                "cumulative_krw_return": float((1.0 + returns).prod() - 1.0),
            }
        )
    return pd.DataFrame(rows).sort_values("cumulative_krw_return", ascending=False).reset_index(drop=True)


def proceed_verdict(availability: pd.DataFrame, quarterly_returns: pd.DataFrame, ranking: pd.DataFrame) -> str:
    all_data_ok = availability["row_count"].ge(1).all() and availability["close_non_null_count"].ge(1).all()
    krw_ok = all(quarterly_returns[f"{ticker}_return_krw"].notna().sum() > 0 for ticker in ETF_TICKERS)
    corr_ok = ranking[["pearson_d013", "spearman_d013", "pearson_h001", "spearman_h001"]].notna().all().all()
    has_low_corr = ranking["low_correlation_candidate"].any()
    return "PROCEED" if all_data_ok and krw_ok and corr_ok and has_low_corr else "STOP"


def write_report(
    availability: pd.DataFrame,
    quarterly_returns: pd.DataFrame,
    correlation_matrix: pd.DataFrame,
    ranking: pd.DataFrame,
) -> None:
    cumulative = cumulative_krw_returns(quarterly_returns)
    verdict = proceed_verdict(availability, quarterly_returns, ranking)
    top3 = ranking.head(3)

    lines = [
        "# I000 — US/Global ETF Universe Diagnostic",
        "",
        "## Verdict",
        "",
        f"- 판정: {verdict}",
        "- I001 권고: ETF별 buy-and-hold KRW baseline 및 D013/H001 결합 포트폴리오 baseline으로 진행",
        "",
        "## Data Availability",
        "",
        f"- ETF 수: {availability.shape[0]}",
        f"- 공통 요청 구간: {quarterly_returns['signal_date'].min().date()} ~ {quarterly_returns['signal_date'].max().date()}",
        f"- D013 분기 기준일 수: {quarterly_returns.shape[0]}",
        f"- ETF KRW return 유효 분기 수: {int(quarterly_returns[[f'{ticker}_return_krw' for ticker in ETF_TICKERS]].notna().min(axis=1).sum())}",
        "- ETF 가격 기준: Yahoo Finance auto-adjusted Close",
        "- 환산 기준: ETF_KRW_return = (1 + ETF_USD_return) * (1 + USDKRW_quarter_change) - 1",
        "- 분기말 정렬: D013 quarterly_regime_log.signal_date별 가장 가까운 ETF/USDKRW 관측치",
        "",
        "## KRW Cumulative Returns",
        "",
        markdown_table(
            cumulative,
            ["ticker", "n_quarters", "cumulative_krw_return"],
            percent_cols={"cumulative_krw_return"},
        ),
        "",
        "## Correlation With D013/H001",
        "",
        markdown_table(
            ranking,
            [
                "ticker",
                "pearson_d013",
                "spearman_d013",
                "pearson_h001",
                "spearman_h001",
                "max_abs_pearson_vs_d013_h001",
                "low_correlation_candidate",
            ],
        ),
        "",
        "## Lowest Correlation Top 3",
        "",
        markdown_table(
            top3,
            ["ticker", "pearson_d013", "pearson_h001", "max_abs_pearson_vs_d013_h001"],
        ),
        "",
        "## Files",
        "",
        "- etf_data_availability.csv",
        "- etf_quarterly_returns.csv",
        "- correlation_matrix.csv",
        "- correlation_with_d013_h001.csv",
        "",
        "## Notes",
        "",
        "- D013/H001 strategy code and engine code were not modified.",
        "- This is a diagnostic analysis only; no new strategy code was added.",
        f"- Correlation matrix shape: {correlation_matrix.shape[0]}x{correlation_matrix.shape[1]}",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_table(
    frame: pd.DataFrame,
    columns: list[str],
    percent_cols: set[str] | None = None,
) -> str:
    percent_cols = percent_cols or set()
    rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                if math.isnan(value):
                    values.append("")
                elif column in percent_cols:
                    values.append(f"{value:.6f}")
                else:
                    values.append(f"{value:.6f}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


if __name__ == "__main__":
    main()
