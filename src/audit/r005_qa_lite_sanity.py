from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.audit.r_family_event_backtest import (
    KOSPI_PATH,
    PANEL_PATHS,
    benchmark_return,
    load_kospi,
    load_price_panel,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "reports" / "experiments" / "R005_qa_lite_sanity"
R_EXPERIMENTS = {
    "R001": ROOT / "reports" / "experiments" / "R001_buyback_announcement",
    "R002": ROOT / "reports" / "experiments" / "R002_buyback_cancellation_retirement",
    "R003": ROOT / "reports" / "experiments" / "R003_dividend_increase",
    "R004": ROOT / "reports" / "experiments" / "R004_shareholder_return_composite",
}
R002_LABEL_CATEGORIES = [
    "true_retirement_title",
    "trust_contract_termination",
    "disposal",
    "cancellation_or_withdrawal",
    "mixed_retirement_related_title",
    "other_title_bucket",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="R005-QA-lite closure sanity check for R-family title-based event studies.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    run(args.output_dir)
    return 0


def run(output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    panel = load_price_panel(PANEL_PATHS)
    calendar = pd.DatetimeIndex(sorted(panel["date"].dropna().unique()))
    kospi = load_kospi(KOSPI_PATH, calendar)
    signals = load_all_signals()
    trades = load_all_trades()

    event_label = build_event_label_audit(signals)
    return_calc = build_return_calc_audit(trades, panel, kospi, calendar)
    dividend = build_dividend_caveat(trades)
    duplicate = build_duplicate_audit(signals)

    event_label.to_csv(output_dir / "event_label_audit.csv", index=False)
    return_calc.to_csv(output_dir / "return_calc_audit.csv", index=False)
    dividend.to_csv(output_dir / "dividend_caveat.csv", index=False)
    duplicate.to_csv(output_dir / "duplicate_audit.csv", index=False)
    write_report(output_dir / "report.md", event_label, return_calc, dividend, duplicate)


def load_all_signals() -> pd.DataFrame:
    rows = []
    for experiment, path in R_EXPERIMENTS.items():
        frame = pd.read_csv(path / "signals.csv", dtype={"ticker": str, "rcept_no": str})
        frame["experiment"] = experiment
        rows.append(frame)
    out = pd.concat(rows, ignore_index=True)
    out["signal_date"] = pd.to_datetime(out["signal_date"])
    out["execution_date"] = pd.to_datetime(out["execution_date"])
    return out


def load_all_trades() -> pd.DataFrame:
    rows = []
    for experiment, path in R_EXPERIMENTS.items():
        frame = pd.read_csv(path / "trades.csv", dtype={"ticker": str, "rcept_no": str})
        frame["experiment"] = experiment
        rows.append(frame)
    out = pd.concat(rows, ignore_index=True)
    out["signal_date"] = pd.to_datetime(out["signal_date"])
    out["execution_date"] = pd.to_datetime(out["execution_date"])
    out["exit_date"] = pd.to_datetime(out["exit_date"])
    return out


def build_event_label_audit(signals: pd.DataFrame) -> pd.DataFrame:
    r002 = signals.loc[signals["experiment"].eq("R002")].copy()
    r002["r002_label_category"] = r002["title"].map(classify_r002_title)
    summary = (
        r002.groupby("r002_label_category", dropna=False)
        .agg(
            event_rows=("rcept_no", "size"),
            tradable_rows=("included_in_trade", "sum"),
            sample_titles=("title", sample_values),
            sample_rcept_no=("rcept_no", sample_values),
        )
        .reset_index()
    )
    summary = (
        pd.DataFrame({"r002_label_category": R002_LABEL_CATEGORIES})
        .merge(summary, on="r002_label_category", how="left")
        .fillna({"event_rows": 0, "tradable_rows": 0, "sample_titles": "", "sample_rcept_no": ""})
    )
    summary["event_rows"] = summary["event_rows"].astype(int)
    summary["tradable_rows"] = summary["tradable_rows"].astype(int)
    summary["interpretation"] = summary["r002_label_category"].map(label_interpretation)
    return summary[
        [
            "r002_label_category",
            "event_rows",
            "tradable_rows",
            "sample_titles",
            "sample_rcept_no",
            "interpretation",
        ]
    ]


def classify_r002_title(title: object) -> str:
    text = str(title)
    compact = text.replace(" ", "")
    has_retirement = "소각" in compact
    has_trust_termination = "신탁계약해지" in compact or "계약해지" in compact or "해지" in compact
    has_disposal = "처분" in compact
    has_cancel = "취소" in compact or "철회" in compact
    if has_retirement and not (has_trust_termination or has_disposal or has_cancel):
        return "true_retirement_title"
    if has_retirement:
        return "mixed_retirement_related_title"
    if has_trust_termination:
        return "trust_contract_termination"
    if has_disposal:
        return "disposal"
    if has_cancel:
        return "cancellation_or_withdrawal"
    return "other_title_bucket"


def label_interpretation(category: str) -> str:
    if category == "true_retirement_title":
        return "title contains retirement wording, but legal retirement amount/intensity is not parsed"
    return "mixed title bucket; R002 must be interpreted carefully"


def sample_values(series: pd.Series) -> str:
    values = [str(value) for value in series.dropna().drop_duplicates().head(5)]
    return " | ".join(values)


def build_return_calc_audit(
    trades: pd.DataFrame,
    panel: pd.DataFrame,
    kospi: pd.DataFrame,
    calendar: pd.DatetimeIndex,
) -> pd.DataFrame:
    day_number = pd.Series(range(len(calendar)), index=calendar)
    kospi_nav = kospi.set_index("date")["kospi_nav"]
    entry_panel = panel.set_index(["date", "ticker"]).sort_index()["open"]
    exit_panel = panel.set_index(["date", "ticker"]).sort_index()["close"]

    samples = (
        trades.sort_values(["experiment", "holding_days", "signal_date", "ticker"])
        .groupby(["experiment", "holding_days"], group_keys=False)
        .head(3)
        .copy()
    )
    rows = []
    for row in samples.itertuples(index=False):
        ticker = str(row.ticker).zfill(6)
        signal_date = pd.Timestamp(row.signal_date)
        execution_date = pd.Timestamp(row.execution_date)
        exit_date = pd.Timestamp(row.exit_date)
        expected_execution = next_trading_day(signal_date, calendar)
        expected_exit = calendar[int(day_number.loc[execution_date]) + int(row.holding_days)]
        expected_entry_price = first_float(entry_panel.loc[(execution_date, ticker)])
        expected_exit_price = first_float(exit_panel.loc[(exit_date, ticker)])
        expected_gross = expected_exit_price / expected_entry_price - 1.0
        expected_kospi = benchmark_return(execution_date, exit_date, kospi_nav)
        expected_excess = expected_gross - expected_kospi
        rows.append(
            {
                "experiment": row.experiment,
                "ticker": ticker,
                "rcept_no": row.rcept_no,
                "holding_days": row.holding_days,
                "signal_date": signal_date.date().isoformat(),
                "execution_date": execution_date.date().isoformat(),
                "expected_execution_date": expected_execution.date().isoformat(),
                "execution_alignment_ok": execution_date == expected_execution,
                "exit_date": exit_date.date().isoformat(),
                "expected_exit_date": expected_exit.date().isoformat(),
                "exit_alignment_ok": exit_date == expected_exit,
                "entry_price": row.entry_price,
                "expected_entry_price": expected_entry_price,
                "entry_price_ok": close_enough(row.entry_price, expected_entry_price),
                "exit_price": row.exit_price,
                "expected_exit_price": expected_exit_price,
                "exit_price_ok": close_enough(row.exit_price, expected_exit_price),
                "gross_return": row.gross_return,
                "expected_gross_return": expected_gross,
                "gross_return_ok": close_enough(row.gross_return, expected_gross),
                "kospi_return": row.kospi_return,
                "expected_kospi_return": expected_kospi,
                "kospi_return_ok": close_enough(row.kospi_return, expected_kospi),
                "excess_return": row.excess_return,
                "expected_excess_return": expected_excess,
                "excess_return_ok": close_enough(row.excess_return, expected_excess),
                "same_trading_day_window_ok": execution_date in day_number.index and exit_date in day_number.index,
            }
        )
    return pd.DataFrame(rows)


def next_trading_day(date: pd.Timestamp, calendar: pd.DatetimeIndex) -> pd.Timestamp:
    idx = calendar.searchsorted(pd.Timestamp(date), side="right")
    return calendar[int(idx)]


def close_enough(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def first_float(value: object) -> float:
    if isinstance(value, pd.Series):
        return float(value.iloc[0])
    return float(value)


def build_dividend_caveat(trades: pd.DataFrame) -> pd.DataFrame:
    dividend = trades.loc[trades["event_type"].eq("dividend")].copy()
    grouped = dividend.groupby(["experiment", "holding_days"], dropna=False)
    out = grouped.agg(
        dividend_event_count=("rcept_no", "size"),
        price_only_mean_gross_return=("gross_return", "mean"),
        price_only_mean_excess_return=("excess_return", "mean"),
        price_only_hit_rate=("excess_return", lambda s: float((s > 0).mean())),
    ).reset_index()
    out["total_return_available"] = False
    out["dividend_cash_amount_available"] = False
    out["ex_dividend_date_available"] = False
    out["ex_dividend_gap_measured"] = False
    out["audit_note"] = (
        "R003/R004 are price-return-only because title-based files do not include PIT dividend amount, ex-dividend date, "
        "or total-return series; this caveat does not rescue R001/R002."
    )
    return out


def build_duplicate_audit(signals: pd.DataFrame) -> pd.DataFrame:
    tradable = signals.loc[signals["included_in_trade"].astype(bool)].copy()
    tradable["quarter"] = tradable["signal_date"].dt.to_period("Q").astype(str)

    same_quarter = (
        tradable.groupby(["experiment", "ticker", "quarter"], dropna=False)
        .agg(event_count=("rcept_no", "size"), event_types=("event_type", event_types), sample_rcept_no=("rcept_no", sample_values))
        .reset_index()
    )
    same_quarter = same_quarter.loc[same_quarter["event_count"] > 1].copy()
    same_quarter["audit_type"] = "same_ticker_same_quarter"

    r001 = tradable.loc[tradable["experiment"].eq("R001"), ["ticker", "quarter", "rcept_no"]].drop_duplicates()
    r003 = tradable.loc[tradable["experiment"].eq("R003"), ["ticker", "quarter", "rcept_no"]].drop_duplicates()
    overlap = r001.merge(r003, on=["ticker", "quarter"], how="inner", suffixes=("_r001", "_r003"))
    overlap_summary = (
        overlap.groupby(["ticker", "quarter"], dropna=False)
        .agg(event_count=("ticker", "size"), sample_rcept_no=("rcept_no_r001", sample_values))
        .reset_index()
    )
    overlap_summary["experiment"] = "R001_R003"
    overlap_summary["event_types"] = "buyback_announcement|dividend"
    overlap_summary["audit_type"] = "r001_r003_same_ticker_quarter_overlap"

    columns = ["audit_type", "experiment", "ticker", "quarter", "event_count", "event_types", "sample_rcept_no"]
    return pd.concat([same_quarter[columns], overlap_summary[columns]], ignore_index=True).sort_values(
        ["audit_type", "experiment", "event_count", "ticker"], ascending=[True, True, False, True]
    )


def event_types(series: pd.Series) -> str:
    return "|".join(sorted(set(series.dropna().astype(str))))


def write_report(
    path: Path,
    event_label: pd.DataFrame,
    return_calc: pd.DataFrame,
    dividend: pd.DataFrame,
    duplicate: pd.DataFrame,
) -> None:
    return_bug = has_return_calc_bug(return_calc)
    r002_mixed = bool(((event_label["r002_label_category"] != "true_retirement_title") & (event_label["event_rows"] > 0)).any())
    conclusion = (
        "R-family CLOSED. Return calculation bug found; create a separate issue and consider rerun."
        if return_bug
        else "R-family CLOSED. No bug found. Title-based bucket fails on its own merits."
    )
    lines = [
        "# R005-QA-lite sanity check",
        "",
        "Status: diagnostic closure sanity check only; production X.",
        "",
        "## Verdict",
        "",
        conclusion,
        "",
        "이 감사는 R001-R004 기존 결과를 덮어쓰지 않는다. 샘플 단위 return 재현에서 blocking bug는 발견되지 않았다."
        if not return_bug
        else "샘플 단위 return 재현에서 불일치가 발견되었다. 별도 issue와 재실행 검토가 필요하다.",
        "",
        "## Event label audit",
        "",
        f"- R002 category rows: {len(event_label)}",
        f"- R002 mixed title bucket present: {r002_mixed}",
        "- 해석: R002는 true share-retirement-only 법률 라벨이 아니라 title-based cancellation/retirement-related bucket으로만 기술한다.",
        "- 표현: 소각 실패 X, title-based bucket 실패 O.",
        "",
        "## Return calculation audit",
        "",
        f"- Sample rows reproduced: {len(return_calc)}",
        f"- Alignment/calculation bug found: {return_bug}",
        "- 확인 항목: KOSPI benchmark window와 event-stock window 동일 trading-day, T+1 open 진입, holding end exit, gross/KOSPI/excess return.",
        "",
        "## Dividend caveat audit",
        "",
        f"- Dividend caveat rows: {len(dividend)}",
        "- R003/R004는 price return only다. 현재 title-based 파일에는 PIT dividend amount, ex-dividend date, total-return series가 없어 배당락 gap을 정량 분리하지 못한다.",
        "- 단, 이 caveat는 R001/R002 실패를 살리지 못한다.",
        "",
        "## Duplicate / overlap audit",
        "",
        f"- Duplicate/overlap rows: {len(duplicate)}",
        "- 같은 종목의 같은 분기 내 연속 공시와 R001+R003 중복은 `duplicate_audit.csv`에 기록했다.",
        "- R004 composite 해석 시 event count 과대계상 가능성을 주의한다.",
        "",
        "## Files",
        "",
        "- `event_label_audit.csv`",
        "- `return_calc_audit.csv`",
        "- `dividend_caveat.csv`",
        "- `duplicate_audit.csv`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def has_return_calc_bug(return_calc: pd.DataFrame) -> bool:
    ok_columns = [
        "execution_alignment_ok",
        "exit_alignment_ok",
        "entry_price_ok",
        "exit_price_ok",
        "gross_return_ok",
        "kospi_return_ok",
        "excess_return_ok",
        "same_trading_day_window_ok",
    ]
    return not bool(return_calc[ok_columns].all(axis=None))


if __name__ == "__main__":
    raise SystemExit(main())
