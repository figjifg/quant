from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

from src.utils.backtest_sanity_checks import run_all_checks
from src.utils.corporate_action import adjust_for_corporate_actions
from src.utils.korean_calendar import KoreanTradingCalendar
from src.utils.random_placebo_engine import date_matched_random
from src.utils.sleeve_nav_simulator import SleeveNAVSimulator
from src.utils.tradability import mark_tradable_rows


PANEL_PATHS = [
    Path("research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv"),
    Path("research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv"),
    Path("research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"),
]
S000_METRICS = Path("reports/experiments/S000_korean_short_mean_reversion_feasibility/gross_net_metrics.csv")
OUTPUT_DIR = Path("reports/experiments/S001_G_corrected_smoke_test")
INITIAL_CAPITAL = 1_000_000_000.0
ROUND_TRIP_COST = 0.0030
SELL_TAX = 0.0018
RANDOM_SEED = 20260520
SIGNALS = [
    {"signal": "r1d_lt_m3_hold1", "hold_days": 1},
    {"signal": "r1d_lt_m3_hold3", "hold_days": 3},
    {"signal": "r1d_lt_m3_hold5", "hold_days": 5},
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = load_panel()
    calendar = KoreanTradingCalendar.from_panel(panel)
    data = prepare_panel(panel)
    metrics_rows = []
    placebo_rows = []
    all_trades = []
    all_events = []
    sanity_rows = []
    for spec in SIGNALS:
        events = select_events(data, spec)
        trades = build_trades(data, events, spec, calendar)
        placebo_events = build_placebo_events(events, data)
        placebo_trades = build_trades(data, placebo_events, spec, calendar, signal_name=spec["signal"] + "_placebo")
        nav = build_sleeve_nav(trades)
        metrics = {"signal": spec["signal"], **calc_metrics(trades), **prefixed("placebo_", calc_metrics(placebo_trades))}
        metrics["verdict"] = classify(metrics)
        metrics_rows.append(metrics)
        placebo_rows.append({"signal": spec["signal"], **calc_metrics(placebo_trades)})
        all_trades.append(trades)
        all_events.append(events)
        sanity = run_all_checks(trades, events=events, simulator_or_nav=nav, calendar=calendar)
        sanity_rows.append({"signal": spec["signal"], **sanity})

    corrected = pd.DataFrame(metrics_rows)
    placebo = pd.DataFrame(placebo_rows)
    sanity = pd.DataFrame(sanity_rows)
    trades_all = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    events_all = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    corrected.to_csv(OUTPUT_DIR / "corrected_metrics.csv", index=False)
    compare_to_s000(corrected).to_csv(OUTPUT_DIR / "s000_vs_s001g_delta.csv", index=False)
    sanity.to_csv(OUTPUT_DIR / "sanity_check_results.csv", index=False)
    placebo.to_csv(OUTPUT_DIR / "placebo_comparison.csv", index=False)
    trades_all.to_csv(OUTPUT_DIR / "trades.csv", index=False)
    events_all.to_csv(OUTPUT_DIR / "signals.csv", index=False)
    write_report(corrected, sanity, placebo)


def load_panel() -> pd.DataFrame:
    usecols = [
        "날짜",
        "종목코드",
        "종목명",
        "시가",
        "고가",
        "저가",
        "종가",
        "KRX종가",
        "거래대금추정",
        "거래대금추정여부",
        "동적유니버스포함",
    ]
    frames = []
    for path in PANEL_PATHS:
        header = pd.read_csv(path, nrows=0, encoding="utf-8-sig")
        cols = [column for column in usecols if column in header.columns]
        frame = pd.read_csv(path, encoding="utf-8-sig", usecols=cols, parse_dates=["날짜"], dtype={"종목코드": str})
        if "KRX종가" not in frame.columns:
            frame["KRX종가"] = frame["종가"]
        frames.append(frame)
    out = pd.concat(frames, ignore_index=True).sort_values(["종목코드", "날짜"]).reset_index(drop=True)
    out["종목코드"] = out["종목코드"].astype(str).str.zfill(6)
    return out


def prepare_panel(panel: pd.DataFrame) -> pd.DataFrame:
    adjusted = adjust_for_corporate_actions(panel)
    marked = mark_tradable_rows(adjusted)
    marked["ret_1d"] = marked.groupby("종목코드", sort=False)["adjusted_close"].pct_change()
    marked["quarter"] = marked["날짜"].dt.to_period("Q")
    marked["signal_value"] = -marked["ret_1d"]
    return marked


def select_events(data: pd.DataFrame, spec: dict) -> pd.DataFrame:
    candidates = data.loc[data["tradable"] & data["ret_1d"].lt(-0.03)].copy()
    candidates = candidates.sort_values(["quarter", "signal_value", "거래대금추정"], ascending=[True, False, False])
    events = candidates.groupby("quarter", group_keys=False).head(20).reset_index(drop=True)
    events["signal"] = spec["signal"]
    events["signal_date"] = events["날짜"]
    events["included_in_trade"] = True
    return events[["signal", "signal_date", "종목코드", "signal_value", "ret_1d", "included_in_trade"]].copy()


def build_placebo_events(events: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
    counts = events["signal_date"].dt.normalize().value_counts().to_dict()
    universe = data.loc[data["tradable"], ["날짜", "종목코드"]].rename(columns={"날짜": "date", "종목코드": "ticker"})
    placebo = date_matched_random(counts.keys(), counts, universe, RANDOM_SEED)
    placebo = placebo.rename(columns={"ticker": "종목코드"})
    placebo["signal"] = events["signal"].iloc[0] + "_placebo" if not events.empty else "placebo"
    placebo["signal_value"] = 0.0
    placebo["ret_1d"] = 0.0
    placebo["included_in_trade"] = True
    return placebo[["signal", "signal_date", "종목코드", "signal_value", "ret_1d", "included_in_trade"]]


def build_trades(data: pd.DataFrame, events: pd.DataFrame, spec: dict, calendar: KoreanTradingCalendar, signal_name: str | None = None) -> pd.DataFrame:
    by_ticker = {ticker: frame.reset_index(drop=True) for ticker, frame in data.groupby("종목코드", sort=False)}
    rows = []
    for event in events.itertuples(index=False):
        ticker = str(event.종목코드).zfill(6)
        if ticker not in by_ticker:
            continue
        ticker_frame = by_ticker[ticker]
        next_krx = calendar.next_trading_day(event.signal_date)
        entry_mask = ticker_frame["날짜"].dt.normalize().eq(next_krx) & ticker_frame["tradable"].astype(bool)
        matches = ticker_frame.index[entry_mask].tolist()
        if not matches:
            continue
        entry_pos = matches[0]
        entry = ticker_frame.iloc[entry_pos]
        try:
            exit_date = pd.Timestamp(entry["날짜"]).normalize() if int(spec["hold_days"]) == 1 else calendar.add_trading_days(entry["날짜"], int(spec["hold_days"]) - 1)
        except ValueError:
            continue
        exit_matches = ticker_frame.index[
            ticker_frame["날짜"].dt.normalize().eq(exit_date) & ticker_frame["tradable"].astype(bool)
        ].tolist()
        if not exit_matches:
            continue
        exit_row = ticker_frame.iloc[exit_matches[0]]
        gross_return = float(exit_row["adjusted_close"] / entry["adjusted_open"] - 1.0)
        net_return = gross_return - ROUND_TRIP_COST - SELL_TAX
        rows.append(
            {
                "signal": signal_name or spec["signal"],
                "ticker": ticker,
                "signal_date": pd.Timestamp(event.signal_date).date().isoformat(),
                "entry_date": pd.Timestamp(entry["날짜"]).date().isoformat(),
                "exit_date": pd.Timestamp(exit_row["날짜"]).date().isoformat(),
                "entry_price": float(entry["adjusted_open"]),
                "exit_price": float(exit_row["adjusted_close"]),
                "cost_paid": ROUND_TRIP_COST + SELL_TAX,
                "holding_days": int(spec["hold_days"]),
                "exit_reason": f"hold_{spec['hold_days']}",
                "gross_return": gross_return,
                "net_return": net_return,
            }
        )
    return pd.DataFrame(rows)


def build_sleeve_nav(trades: pd.DataFrame) -> pd.DataFrame:
    simulator = SleeveNAVSimulator(INITIAL_CAPITAL, max_position_size=0.02, max_active_positions=20, cash_idle_allowed=True)
    if trades.empty:
        simulator.mark_to_market(pd.Timestamp("2010-01-01"))
        return simulator.nav_frame()
    events = []
    for row in trades.itertuples(index=False):
        events.append((pd.Timestamp(row.entry_date), "entry", row))
        events.append((pd.Timestamp(row.exit_date), "exit", row))
    for date, action, row in sorted(events, key=lambda item: (item[0], item[1] == "entry")):
        if action == "exit":
            simulator.process_exit(date, row.ticker, row.exit_price, cost_rate=SELL_TAX)
        else:
            simulator.process_signal(date, row.ticker, 0.02, row.entry_price, cost_rate=ROUND_TRIP_COST / 2.0)
        simulator.mark_to_market(date, {row.ticker: row.exit_price if action == "exit" else row.entry_price})
    return simulator.nav_frame()


def calc_metrics(trades: pd.DataFrame) -> dict[str, float | int]:
    if trades.empty:
        return {"trade_count": 0, "gross_mean": 0.0, "net_mean": 0.0, "sharpe": 0.0, "hit_rate": 0.0}
    gross = pd.to_numeric(trades["gross_return"], errors="coerce")
    net = pd.to_numeric(trades["net_return"], errors="coerce")
    std = net.std()
    hold = pd.to_numeric(trades["holding_days"], errors="coerce").mean()
    return {
        "trade_count": int(len(trades)),
        "gross_mean": float(gross.mean()),
        "net_mean": float(net.mean()),
        "sharpe": float(net.mean() / std * math.sqrt(252.0 / hold)) if std and not math.isnan(std) else 0.0,
        "hit_rate": float(net.gt(0).mean()),
    }


def prefixed(prefix: str, values: dict) -> dict:
    return {prefix + key: value for key, value in values.items()}


def classify(metrics: dict) -> str:
    placebo_edge = metrics["net_mean"] > metrics["placebo_net_mean"]
    if metrics["gross_mean"] > 0.03 and metrics["sharpe"] > 3.0 and placebo_edge:
        return "STRONG_REQUIRES_S2_PREREG"
    if metrics["gross_mean"] >= 0.01 and metrics["sharpe"] >= 1.5 and placebo_edge:
        return "MILD_DIAGNOSTIC_ONLY"
    return "NULL_WEAK_CLOSE_S_FAMILY"


def compare_to_s000(corrected: pd.DataFrame) -> pd.DataFrame:
    if not S000_METRICS.exists():
        return corrected[["signal", "gross_mean", "net_mean", "sharpe"]].assign(s000_missing=True)
    s000 = pd.read_csv(S000_METRICS)
    merged = corrected.merge(s000[["signal", "gross_mean", "net_mean", "sharpe"]], on="signal", how="left", suffixes=("_s001g", "_s000"))
    for column in ["gross_mean", "net_mean", "sharpe"]:
        merged[column + "_delta"] = merged[column + "_s001g"] - merged[column + "_s000"]
    return merged


def write_report(metrics: pd.DataFrame, sanity: pd.DataFrame, placebo: pd.DataFrame) -> None:
    if metrics["verdict"].eq("STRONG_REQUIRES_S2_PREREG").any():
        family_verdict = "S2-family 가능성: 새 preregistration 필요"
    else:
        family_verdict = "S-family permanently CLOSED"
    payload = {
        "experiment": "S001_G_corrected_smoke_test",
        "family_verdict": family_verdict,
        "signals": metrics.to_dict(orient="records"),
    }
    (OUTPUT_DIR / "metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# S001-G Corrected Smoke Test",
        "",
        f"Verdict: {family_verdict}",
        "",
        "## Corrected Metrics",
        "",
        markdown_table(metrics),
        "",
        "## Placebo",
        "",
        markdown_table(placebo),
        "",
        "## Sanity Checks",
        "",
        markdown_table(sanity),
        "",
        "## 판정 기준",
        "",
        "Null/weak는 gross < 1%, Sharpe < 1.5, 또는 placebo edge 없음 중 하나라도 해당할 때 적용했다. "
        "Strong가 나오더라도 S000 재활용 없이 S2-family를 새로 사전 등록해야 한다.",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_empty_"
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for _, row in frame.iterrows():
        values = []
        for column in columns:
            value = row[column]
            values.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
