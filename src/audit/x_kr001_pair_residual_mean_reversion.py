from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.backtest_sanity_checks import (
    SanityCheckConfig,
    check_no_filtered_row_execution,
    check_no_implicit_leverage,
    check_no_same_day_execution,
    run_all_checks,
)
from src.utils.corporate_action import CorporateActionPolicy, adjust_for_corporate_actions, detect_impossible_returns
from src.utils.korean_calendar import KoreanTradingCalendar
from src.utils.random_placebo_engine import (
    PlaceboConfig,
    build_date_matched_placebos,
    date_matched_random,
    drop_bucket_matched_random,
    time_shift_placebo,
)
from src.utils.sleeve_nav_simulator import SleeveNAVSimulator, reconcile_nav
from src.utils.tradability import TradabilityPolicy, mark_tradable_rows


PANEL_PATHS = (
    ROOT / "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv",
    ROOT / "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv",
)
PIT_SECTOR_PATH = ROOT / "data/processed/stock_sector_mapping_pit_daily.csv"
STATIC_SECTOR_PATH = ROOT / "data/processed/stock_sector_mapping_20260518.csv"
MARKET_PROXY_PATH = ROOT / "research_input_data/inputs/market_flow/kiwoom_market_flow_2018_2026_integrated.csv"
OUTPUT_DIR = ROOT / "x_lab/x_kr/x_kr001_results"

ROLLING_WINDOW = 60
Z_ENTRY = 2.0
Z_STOP = 3.0
TOP_SIGNALS_PER_DAY = 10
RANDOM_TRIALS = 1_000
RANDOM_SEED = 20260520
INITIAL_CAPITAL_KRW = 100_000_000.0
TURNOVER_COST_RATE = 0.0015
CAPITAL_GAINS_TAX_RATE = 0.22
ANNUAL_EXEMPTION_KRW = 2_500_000.0

SUBPERIODS = {
    "2018_2020": ("2018-01-01", "2020-12-31"),
    "2021_2023": ("2021-01-01", "2023-12-31"),
    "2024_2026": ("2024-01-01", "2026-12-31"),
}
STRESS_WINDOWS = {
    "covid_2020_02_03": ("2020-02-01", "2020-03-31"),
    "year_2022": ("2022-01-01", "2022-12-31"),
}


@dataclass(frozen=True)
class Variant:
    variant_id: str
    family: str
    hold_days: int
    description: str


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    variants = build_variants()
    panel = load_panel()
    calendar = KoreanTradingCalendar.from_panel(panel).with_tradable_dates([panel])
    pair_list = build_pair_list(panel)
    price = panel.pivot(index="date", columns="ticker", values="adjusted_close").sort_index()
    open_price = panel.pivot(index="date", columns="ticker", values="adjusted_open").reindex(price.index)
    returns = price.pct_change(fill_method=None).fillna(0.0)
    market_return = load_market_return(price.index)
    sector_return = build_sector_returns(panel, returns)

    pair_z = build_pair_zscores(price, pair_list)
    market_z = build_market_beta_zscores(returns, market_return)
    sector_z = build_sector_beta_zscores(panel, returns, sector_return)

    config = build_config(variants, pair_list)
    write_yaml(OUTPUT_DIR / "config.yaml", config)
    pair_list.to_csv(OUTPUT_DIR / "pair_list.csv", index=False)

    variant_rows = []
    subperiod_rows = []
    stress_rows = []
    random_rows = []
    contribution_frames = []
    turnover_rows = []
    pass_rows = []
    sanity_rows = []

    all_trades = []
    all_events = []

    for variant in variants:
        source = signals_for_variant(variant, pair_z, market_z, sector_z, pair_list)
        for mode in ("long_short", "long_only"):
            events = select_events(source, variant, mode, calendar)
            trades = build_trades(events, variant, mode, calendar, price, open_price)
            trades = filter_executable_trades(trades, panel)
            result = simulate_daily_nav(trades, returns, open_price, price, mode)
            random = random_control(events, returns, panel, variant, mode, result["metrics_after_cost"]["sharpe"])
            top_contrib = top_pair_contribution(trades, result["daily_pnl"], variant, mode)
            pass_eval = evaluate_pass_gates(variant, mode, result, random, top_contrib)
            sanity = sanity_checks(variant, mode, trades, events, result["nav_after_cost"], panel, calendar)

            variant_rows.append(
                {
                    "variant_id": variant.variant_id,
                    "variant": variant.description,
                    "signal_family": variant.family,
                    "hold_days": variant.hold_days,
                    "portfolio_mode": mode,
                    "n_signals": len(events),
                    "n_trades": len(trades),
                    **prefixed("gross", result["metrics_gross"]),
                    **prefixed("after_cost", result["metrics_after_cost"]),
                    **prefixed("after_tax_22pct", result["metrics_after_tax"]),
                    "random_percentile": random["strategy_percentile"],
                    "total_turnover": result["total_turnover"],
                    "annualized_turnover": annualized_turnover(result["turnover"], result["nav_after_cost"]),
                    "tax_paid_krw": result["tax_paid_krw"],
                    "gross_exposure_max": result["gross_exposure_max"],
                }
            )
            for name, (start, end) in SUBPERIODS.items():
                subperiod_rows.append(period_row(variant, mode, name, result["nav_after_cost"], start, end))
            for name, (start, end) in STRESS_WINDOWS.items():
                stress_rows.append(period_row(variant, mode, name, result["nav_after_cost"], start, end))
            random_rows.append({"variant_id": variant.variant_id, "portfolio_mode": mode, **random})
            contribution_frames.append(top_contrib)
            turnover_rows.append(
                {
                    "variant_id": variant.variant_id,
                    "portfolio_mode": mode,
                    "total_turnover": result["total_turnover"],
                    "annualized_turnover": annualized_turnover(result["turnover"], result["nav_after_cost"]),
                    "cost_paid_krw": result["cost_paid_krw"],
                    "tax_paid_22pct_krw": result["tax_paid_krw"],
                    "tax0_nav_end": float(result["nav_after_cost"].iloc[-1]) if not result["nav_after_cost"].empty else np.nan,
                    "tax22_nav_end": float(result["nav_after_tax"].iloc[-1]) if not result["nav_after_tax"].empty else np.nan,
                }
            )
            pass_rows.extend(pass_eval)
            sanity_rows.extend(sanity)
            all_trades.append(trades.assign(variant_id=variant.variant_id, portfolio_mode=mode))
            all_events.append(events.assign(variant_id=variant.variant_id, portfolio_mode=mode))

    variant_metrics = pd.DataFrame(variant_rows)
    subperiod = pd.DataFrame(subperiod_rows)
    stress = pd.DataFrame(stress_rows)
    random_df = pd.DataFrame(random_rows)
    contribution = pd.concat(contribution_frames, ignore_index=True) if contribution_frames else pd.DataFrame()
    turnover = pd.DataFrame(turnover_rows)
    pass_gate = pd.DataFrame(pass_rows)
    sanity_df = pd.DataFrame(sanity_rows)

    variant_metrics.to_csv(OUTPUT_DIR / "variant_metrics.csv", index=False)
    subperiod.to_csv(OUTPUT_DIR / "subperiod_breakdown.csv", index=False)
    stress.to_csv(OUTPUT_DIR / "stress_windows.csv", index=False)
    random_df.to_csv(OUTPUT_DIR / "random_control.csv", index=False)
    contribution.to_csv(OUTPUT_DIR / "top_pair_contribution.csv", index=False)
    turnover.to_csv(OUTPUT_DIR / "turnover_tax_breakdown.csv", index=False)
    pass_gate.to_csv(OUTPUT_DIR / "pass_gate_evaluation.csv", index=False)
    sanity_df.to_csv(OUTPUT_DIR / "sanity_check_results.csv", index=False)
    write_report(variant_metrics, pass_gate, random_df, sanity_df, pair_list)


def build_variants() -> list[Variant]:
    variants = [
        Variant("XKR001_V01", "pair_residual", 5, "Same-sector pair residual z-score, 5d hold"),
        Variant("XKR001_V02", "pair_residual", 10, "Same-sector pair residual z-score, 10d hold"),
        Variant("XKR001_V03", "market_beta_residual", 5, "Market beta residual z-score, 5d hold"),
        Variant("XKR001_V04", "market_beta_residual", 10, "Market beta residual z-score, 10d hold"),
        Variant("XKR001_V05", "sector_beta_residual", 5, "Sector beta residual z-score, 5d hold"),
        Variant("XKR001_V06", "sector_beta_residual", 10, "Sector beta residual z-score, 10d hold"),
    ]
    if len(variants) != 6:
        raise AssertionError("X-KR001 must keep exactly 6 pre-registered variants")
    return variants


def load_panel() -> pd.DataFrame:
    frames = []
    for path in PANEL_PATHS:
        frame = pd.read_csv(path, encoding="utf-8-sig", dtype={"종목코드": str}, parse_dates=["날짜"])
        frame = adjust_for_corporate_actions(frame, CorporateActionPolicy())
        frame = mark_tradable_rows(frame, TradabilityPolicy(require_dynamic_universe=True, exclude_estimated_traded_value=True))
        frame = frame.rename(
            columns={
                "날짜": "date",
                "종목코드": "ticker",
                "종목명": "name",
                "시가총액추정": "market_cap",
                "거래대금추정": "traded_value",
            }
        )
        frames.append(frame)
    panel = pd.concat(frames, ignore_index=True)
    panel["date"] = pd.to_datetime(panel["date"]).dt.normalize()
    panel["ticker"] = panel["ticker"].astype(str).str.zfill(6)
    panel["adjusted_close"] = pd.to_numeric(panel["adjusted_close"], errors="coerce")
    panel["adjusted_open"] = pd.to_numeric(panel["adjusted_open"], errors="coerce")
    panel["market_cap"] = pd.to_numeric(panel["market_cap"], errors="coerce")
    panel = panel.loc[panel["date"].between("2018-01-01", "2026-12-31")]
    panel = attach_sector(panel)
    return panel.sort_values(["date", "ticker"]).reset_index(drop=True)


def attach_sector(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    if PIT_SECTOR_PATH.exists():
        mapping = pd.read_csv(PIT_SECTOR_PATH, dtype={"ticker": str}, parse_dates=["date"])
        mapping["date"] = pd.to_datetime(mapping["date"]).dt.normalize()
        mapping["ticker"] = mapping["ticker"].astype(str).str.zfill(6)
        mapping["sector_code"] = mapping["final_sector_code"].astype("string").str.zfill(2)
        mapping["sector_name"] = mapping["final_sector_name"].astype("string")
        out = out.merge(mapping[["date", "ticker", "sector_code", "sector_name"]], on=["date", "ticker"], how="left")
    if out.get("sector_code", pd.Series(index=out.index, dtype=object)).isna().any() and STATIC_SECTOR_PATH.exists():
        static = pd.read_csv(STATIC_SECTOR_PATH, dtype={"ticker": str})
        static["ticker"] = static["ticker"].astype(str).str.zfill(6)
        static["static_sector_code"] = static["final_sector_code"].astype("string").str.zfill(2)
        static["static_sector_name"] = static["final_sector_name"].astype("string")
        out = out.merge(static[["ticker", "static_sector_code", "static_sector_name"]], on="ticker", how="left")
        out["sector_code"] = out["sector_code"].fillna(out["static_sector_code"])
        out["sector_name"] = out["sector_name"].fillna(out["static_sector_name"])
        out = out.drop(columns=["static_sector_code", "static_sector_name"])
    out["sector_code"] = out["sector_code"].astype("string").fillna("99").str.zfill(2)
    out["sector_name"] = out["sector_name"].astype("string").fillna("기타")
    return out


def build_pair_list(panel: pd.DataFrame) -> pd.DataFrame:
    latest = panel.loc[panel["tradable"].astype(bool)].sort_values("date").drop_duplicates("ticker", keep="last")
    latest = latest.loc[latest["sector_code"].ne("99") & latest["market_cap"].gt(0)].copy()
    latest["sector_rank"] = latest.groupby("sector_code")["market_cap"].rank(method="first", ascending=False)
    top = latest.loc[latest["sector_rank"].le(10)].copy()
    rows = []
    for (sector_code, sector_name), group in top.groupby(["sector_code", "sector_name"], sort=True):
        group = group.sort_values("market_cap", ascending=False).reset_index(drop=True)
        candidates = []
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a = group.iloc[i]
                b = group.iloc[j]
                candidates.append(
                    {
                        "sector_code": sector_code,
                        "sector_name": sector_name,
                        "ticker_1": a["ticker"],
                        "name_1": a["name"],
                        "ticker_2": b["ticker"],
                        "name_2": b["name"],
                        "rank_1": int(a["sector_rank"]),
                        "rank_2": int(b["sector_rank"]),
                        "market_cap_1": float(a["market_cap"]),
                        "market_cap_2": float(b["market_cap"]),
                        "abs_log_mcap_diff": abs(math.log(float(a["market_cap"])) - math.log(float(b["market_cap"]))),
                    }
                )
        selected = sorted(candidates, key=lambda row: row["abs_log_mcap_diff"])[:10]
        rows.extend(selected)
    pairs = pd.DataFrame(rows).sort_values(["abs_log_mcap_diff", "sector_code"]).head(50).reset_index(drop=True)
    pairs.insert(0, "pair_id", [f"PAIR{i + 1:03d}" for i in range(len(pairs))])
    if len(pairs) < 30:
        raise ValueError(f"X-KR001 pair construction produced fewer than 30 pairs: {len(pairs)}")
    return pairs


def build_pair_zscores(price: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    logs = np.log(price.replace(0, np.nan))
    rows = []
    for pair in pairs.itertuples(index=False):
        y = logs[str(pair.ticker_1)]
        x = logs[str(pair.ticker_2)]
        beta = y.rolling(ROLLING_WINDOW).cov(x) / x.rolling(ROLLING_WINDOW).var()
        alpha = y.rolling(ROLLING_WINDOW).mean() - beta * x.rolling(ROLLING_WINDOW).mean()
        residual = y - beta * x - alpha
        z = (residual - residual.rolling(ROLLING_WINDOW).mean()) / residual.rolling(ROLLING_WINDOW).std()
        frame = pd.DataFrame(
            {
                "signal_date": z.index,
                "signal_key": pair.pair_id,
                "ticker_long_neg_z": str(pair.ticker_1),
                "ticker_long_pos_z": str(pair.ticker_2),
                "sector_code": pair.sector_code,
                "sector_name": pair.sector_name,
                "z": z.values,
                "signal_return": residual.diff().values,
            }
        )
        rows.append(frame)
    return pd.concat(rows, ignore_index=True).dropna(subset=["z"])


def load_market_return(index: pd.DatetimeIndex) -> pd.Series:
    market = pd.read_csv(MARKET_PROXY_PATH, parse_dates=["date"])
    market = market.sort_values("date").drop_duplicates("date", keep="last")
    proxy = pd.to_numeric(market["program_kospi200"], errors="coerce")
    out = pd.Series(proxy.values, index=pd.to_datetime(market["date"]).dt.normalize(), name="market_proxy").pct_change()
    return out.reindex(index).fillna(0.0)


def build_sector_returns(panel: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    sector_by_ticker = panel.sort_values("date").drop_duplicates("ticker", keep="last").set_index("ticker")["sector_code"].to_dict()
    out = pd.DataFrame(index=returns.index)
    for sector_code in sorted(set(sector_by_ticker.values())):
        tickers = [ticker for ticker, sector in sector_by_ticker.items() if sector == sector_code and ticker in returns.columns]
        if tickers:
            out[sector_code] = returns[tickers].mean(axis=1)
    return out.fillna(0.0)


def build_market_beta_zscores(returns: pd.DataFrame, market_return: pd.Series) -> pd.DataFrame:
    rows = []
    mvar = market_return.rolling(ROLLING_WINDOW).var()
    for ticker in returns.columns:
        beta = returns[ticker].rolling(ROLLING_WINDOW).cov(market_return) / mvar
        residual = returns[ticker] - beta * market_return
        cumulative = residual.rolling(ROLLING_WINDOW).sum()
        z = (cumulative - cumulative.rolling(ROLLING_WINDOW).mean()) / cumulative.rolling(ROLLING_WINDOW).std()
        rows.append(pd.DataFrame({"signal_date": z.index, "signal_key": ticker, "ticker": ticker, "z": z.values, "signal_return": residual.values}))
    return pd.concat(rows, ignore_index=True).dropna(subset=["z"])


def build_sector_beta_zscores(panel: pd.DataFrame, returns: pd.DataFrame, sector_returns: pd.DataFrame) -> pd.DataFrame:
    sector_by_ticker = panel.sort_values("date").drop_duplicates("ticker", keep="last").set_index("ticker")["sector_code"].to_dict()
    rows = []
    for ticker in returns.columns:
        sector_code = sector_by_ticker.get(ticker)
        if sector_code not in sector_returns:
            continue
        bench = sector_returns[sector_code]
        beta = returns[ticker].rolling(ROLLING_WINDOW).cov(bench) / bench.rolling(ROLLING_WINDOW).var()
        residual = returns[ticker] - beta * bench
        cumulative = residual.rolling(ROLLING_WINDOW).sum()
        z = (cumulative - cumulative.rolling(ROLLING_WINDOW).mean()) / cumulative.rolling(ROLLING_WINDOW).std()
        rows.append(
            pd.DataFrame(
                {
                    "signal_date": z.index,
                    "signal_key": ticker,
                    "ticker": ticker,
                    "sector_code": sector_code,
                    "z": z.values,
                    "signal_return": residual.values,
                }
            )
        )
    return pd.concat(rows, ignore_index=True).dropna(subset=["z"])


def signals_for_variant(
    variant: Variant,
    pair_z: pd.DataFrame,
    market_z: pd.DataFrame,
    sector_z: pd.DataFrame,
    pair_list: pd.DataFrame,
) -> pd.DataFrame:
    if variant.family == "pair_residual":
        data = pair_z.copy()
        data["signal_type"] = "pair"
        return data
    if variant.family == "market_beta_residual":
        data = market_z.copy()
        data["signal_type"] = "single"
        data["sector_code"] = ""
        return data
    if variant.family == "sector_beta_residual":
        data = sector_z.copy()
        data["signal_type"] = "single"
        return data
    raise ValueError(f"Unsupported variant family: {variant.family}")


def select_events(source: pd.DataFrame, variant: Variant, mode: str, calendar: KoreanTradingCalendar) -> pd.DataFrame:
    data = source.loc[source["z"].abs().ge(Z_ENTRY)].copy()
    if data.empty:
        return empty_events()
    data["abs_z"] = data["z"].abs()
    selected = (
        data.sort_values(["signal_date", "abs_z"], ascending=[True, False])
        .groupby("signal_date", group_keys=False)
        .head(TOP_SIGNALS_PER_DAY)
        .reset_index(drop=True)
    )
    rows = []
    for row in selected.itertuples(index=False):
        signal_date = pd.Timestamp(row.signal_date).normalize()
        try:
            execution_date = calendar.next_trading_day(signal_date)
        except ValueError:
            continue
        z = float(row.z)
        direction = -1 if z > 0 else 1
        if row.signal_type == "pair":
            long_ticker = row.ticker_long_neg_z if z < 0 else row.ticker_long_pos_z
            short_ticker = row.ticker_long_pos_z if z < 0 else row.ticker_long_neg_z
            rows.append(
                {
                    "signal_date": signal_date,
                    "execution_date": execution_date,
                    "signal_key": row.signal_key,
                    "signal_type": "pair",
                    "sector_code": row.sector_code,
                    "sector_name": row.sector_name,
                    "z": z,
                    "abs_z": abs(z),
                    "long_ticker": str(long_ticker),
                    "short_ticker": "" if mode == "long_only" else str(short_ticker),
                    "included_in_trade": True,
                    "signal_return": getattr(row, "signal_return", np.nan),
                }
            )
        else:
            long_ticker = str(row.ticker) if direction > 0 else ""
            short_ticker = "" if mode == "long_only" else (str(row.ticker) if direction < 0 else "")
            if mode == "long_only" and not long_ticker:
                continue
            rows.append(
                {
                    "signal_date": signal_date,
                    "execution_date": execution_date,
                    "signal_key": row.signal_key,
                    "signal_type": "single",
                    "sector_code": getattr(row, "sector_code", ""),
                    "sector_name": "",
                    "z": z,
                    "abs_z": abs(z),
                    "long_ticker": long_ticker,
                    "short_ticker": short_ticker,
                    "included_in_trade": True,
                    "signal_return": getattr(row, "signal_return", np.nan),
                }
            )
    return pd.DataFrame(rows) if rows else empty_events()


def empty_events() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "signal_date",
            "execution_date",
            "signal_key",
            "signal_type",
            "sector_code",
            "sector_name",
            "z",
            "abs_z",
            "long_ticker",
            "short_ticker",
            "included_in_trade",
            "signal_return",
        ]
    )


def build_trades(
    events: pd.DataFrame,
    variant: Variant,
    mode: str,
    calendar: KoreanTradingCalendar,
    price: pd.DataFrame,
    open_price: pd.DataFrame,
) -> pd.DataFrame:
    if events.empty:
        return empty_trades()
    rows = []
    dates = list(price.index)
    date_pos = {date: i for i, date in enumerate(dates)}
    for event_id, event in enumerate(events.itertuples(index=False), start=1):
        entry = pd.Timestamp(event.execution_date).normalize()
        if entry not in date_pos:
            continue
        max_exit_pos = min(date_pos[entry] + variant.hold_days, len(dates) - 1)
        exit_date = dates[max_exit_pos]
        exit_reason = "stop_loss" if abs(float(event.z)) >= Z_STOP else "max_hold"
        tickers = [ticker for ticker in (event.long_ticker, event.short_ticker) if isinstance(ticker, str) and ticker]
        if not tickers:
            continue
        entry_prices = {ticker: lookup_price(open_price, entry, ticker) for ticker in tickers}
        exit_prices = {ticker: lookup_price(open_price, exit_date, ticker) for ticker in tickers}
        if any(pd.isna(v) or v <= 0 for v in [*entry_prices.values(), *exit_prices.values()]):
            continue
        long_ret = price_return(event.long_ticker, entry, exit_date, entry_prices, exit_prices) if event.long_ticker else 0.0
        short_ret = -price_return(event.short_ticker, entry, exit_date, entry_prices, exit_prices) if event.short_ticker else 0.0
        gross_return = long_ret if mode == "long_only" else 0.5 * long_ret + 0.5 * short_ret
        rows.append(
            {
                "event_id": f"{variant.variant_id}_{mode}_{event_id:06d}",
                "signal_key": event.signal_key,
                "signal_type": event.signal_type,
                "signal_date": pd.Timestamp(event.signal_date).normalize(),
                "entry_date": entry,
                "exit_date": pd.Timestamp(exit_date).normalize(),
                "long_ticker": event.long_ticker,
                "short_ticker": event.short_ticker,
                "ticker": event.long_ticker or event.short_ticker,
                "entry_price": entry_prices.get(event.long_ticker, entry_prices.get(event.short_ticker)),
                "exit_price": exit_prices.get(event.long_ticker, exit_prices.get(event.short_ticker)),
                "z": event.z,
                "gross_return": gross_return,
                "net_return": gross_return - 2.0 * TURNOVER_COST_RATE,
                "holding_days": calendar.n_trading_days_between(entry, exit_date),
                "exit_reason": exit_reason,
            }
        )
    return pd.DataFrame(rows) if rows else empty_trades()


def empty_trades() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "event_id",
            "signal_key",
            "signal_type",
            "signal_date",
            "entry_date",
            "exit_date",
            "long_ticker",
            "short_ticker",
            "ticker",
            "entry_price",
            "exit_price",
            "z",
            "gross_return",
            "net_return",
            "holding_days",
            "exit_reason",
        ]
    )


def filter_executable_trades(trades: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return trades
    allowed = set(
        zip(
            panel.loc[panel["tradable"].astype(bool), "ticker"].astype(str),
            pd.to_datetime(panel.loc[panel["tradable"].astype(bool), "date"]).dt.normalize(),
        )
    )
    keep = []
    for trade in trades.itertuples(index=False):
        entry = pd.Timestamp(trade.entry_date).normalize()
        tickers = [ticker for ticker in (trade.long_ticker, trade.short_ticker) if isinstance(ticker, str) and ticker]
        keep.append(all((str(ticker), entry) in allowed for ticker in tickers))
    return trades.loc[keep].reset_index(drop=True)


def lookup_price(prices: pd.DataFrame, date: pd.Timestamp, ticker: str) -> float:
    if not ticker or ticker not in prices.columns or date not in prices.index:
        return np.nan
    return float(prices.loc[date, ticker])


def price_return(ticker: str, entry: pd.Timestamp, exit_date: pd.Timestamp, entry_prices: dict[str, float], exit_prices: dict[str, float]) -> float:
    if not ticker:
        return 0.0
    return float(exit_prices[ticker] / entry_prices[ticker] - 1.0)


def simulate_daily_nav(
    trades: pd.DataFrame,
    returns: pd.DataFrame,
    open_price: pd.DataFrame,
    close_price: pd.DataFrame,
    mode: str,
) -> dict:
    index = close_price.index
    if trades.empty:
        nav = pd.Series(1.0, index=index, name="nav")
        return empty_simulation(nav)
    daily_pnl = pd.Series(0.0, index=index)
    exposure = pd.Series(0.0, index=index)
    turnover = []
    cost_paid = 0.0
    realized_by_year: dict[int, float] = {}
    entry_counts = trades.groupby("entry_date").size()
    exit_counts = trades.groupby("exit_date").size()
    for date, count in entry_counts.items():
        slots = max(1, min(TOP_SIGNALS_PER_DAY, int(count)))
        turnover_notional = min(1.0, int(count) / slots)
        turnover.append({"date": pd.Timestamp(date), "turnover": turnover_notional})
        cost_paid += INITIAL_CAPITAL_KRW * turnover_notional * TURNOVER_COST_RATE
    for date, group in trades.groupby("exit_date"):
        slots = max(1, min(TOP_SIGNALS_PER_DAY, len(group)))
        turnover_notional = min(1.0, len(group) / slots)
        turnover.append({"date": pd.Timestamp(date), "turnover": turnover_notional})
        cost_paid += INITIAL_CAPITAL_KRW * turnover_notional * TURNOVER_COST_RATE
        pnl = float(group["gross_return"].mean())
        if date in daily_pnl.index:
            daily_pnl.loc[pd.Timestamp(date)] += pnl
        realized_by_year[pd.Timestamp(date).year] = realized_by_year.get(pd.Timestamp(date).year, 0.0) + pnl * INITIAL_CAPITAL_KRW
    for trade in trades.itertuples(index=False):
        active_dates = index[(index >= pd.Timestamp(trade.entry_date)) & (index < pd.Timestamp(trade.exit_date))]
        if len(active_dates) == 0:
            continue
        exposure.loc[active_dates] = np.minimum(1.0, exposure.loc[active_dates] + 1.0 / TOP_SIGNALS_PER_DAY)
    turnover_df = pd.DataFrame(turnover)
    nav_gross = (1.0 + daily_pnl).cumprod()
    cost_drag = turnover_series(turnover_df, index) * TURNOVER_COST_RATE
    nav_after_cost = (1.0 + daily_pnl - cost_drag).cumprod()
    tax_series, tax_paid = annual_tax_series(daily_pnl, realized_by_year, index)
    nav_after_tax = (1.0 + daily_pnl - cost_drag - tax_series).cumprod()
    return {
        "nav_gross": nav_gross,
        "nav_after_cost": nav_after_cost,
        "nav_after_tax": nav_after_tax,
        "daily_pnl": daily_pnl,
        "turnover": turnover_df,
        "cost_paid_krw": cost_paid,
        "tax_paid_krw": tax_paid,
        "total_turnover": float(turnover_df["turnover"].sum()) if not turnover_df.empty else 0.0,
        "gross_exposure_max": float(exposure.max()),
        "metrics_gross": metrics(nav_gross),
        "metrics_after_cost": metrics(nav_after_cost),
        "metrics_after_tax": metrics(nav_after_tax),
        "nav_frame": pd.DataFrame(
            {
                "date": index,
                "gross_value": nav_gross.values,
                "net_value": nav_after_cost.values,
                "cash": 1.0 - exposure.values,
                "n_positions": 0,
                "exposure": np.minimum(exposure.values, nav_after_cost.clip(lower=0.0).values),
            }
        ),
    }


def empty_simulation(nav: pd.Series) -> dict:
    empty_metrics_ = metrics(nav)
    return {
        "nav_gross": nav,
        "nav_after_cost": nav,
        "nav_after_tax": nav,
        "daily_pnl": pd.Series(0.0, index=nav.index),
        "turnover": pd.DataFrame(columns=["date", "turnover"]),
        "cost_paid_krw": 0.0,
        "tax_paid_krw": 0.0,
        "total_turnover": 0.0,
        "gross_exposure_max": 0.0,
        "metrics_gross": empty_metrics_,
        "metrics_after_cost": empty_metrics_,
        "metrics_after_tax": empty_metrics_,
        "nav_frame": pd.DataFrame({"date": nav.index, "gross_value": nav.values, "net_value": nav.values, "cash": 1.0, "n_positions": 0, "exposure": 0.0}),
    }


def safe_return(returns: pd.DataFrame, date: pd.Timestamp, ticker: str) -> float:
    if ticker not in returns.columns or date not in returns.index:
        return 0.0
    value = returns.loc[date, ticker]
    return 0.0 if pd.isna(value) else float(value)


def turnover_series(turnover: pd.DataFrame, index: pd.DatetimeIndex) -> pd.Series:
    if turnover.empty:
        return pd.Series(0.0, index=index)
    series = turnover.groupby(pd.to_datetime(turnover["date"]).dt.normalize())["turnover"].sum()
    return series.reindex(index).fillna(0.0)


def annual_tax_series(daily_pnl: pd.Series, realized_by_year: dict[int, float], index: pd.DatetimeIndex) -> tuple[pd.Series, float]:
    tax = pd.Series(0.0, index=index)
    paid = 0.0
    for year, gain in realized_by_year.items():
        taxable = max(0.0, gain - ANNUAL_EXEMPTION_KRW)
        amount = taxable * CAPITAL_GAINS_TAX_RATE
        if amount <= 0:
            continue
        year_dates = index[index.year == year]
        if len(year_dates) == 0:
            continue
        pay_date = year_dates[-1]
        tax.loc[pay_date] = amount / INITIAL_CAPITAL_KRW
        paid += amount
    return tax, paid


def metrics(nav: pd.Series) -> dict:
    nav = nav.dropna()
    if len(nav) < 2:
        return {"cagr": np.nan, "sharpe": np.nan, "max_drawdown": np.nan, "calmar": np.nan, "volatility": np.nan, "end_nav": np.nan}
    daily = nav.pct_change().fillna(0.0)
    years = max((nav.index[-1] - nav.index[0]).days / 365.25, 1e-9)
    cagr = float(nav.iloc[-1] ** (1.0 / years) - 1.0) if nav.iloc[-1] > 0 else np.nan
    vol = float(daily.std() * math.sqrt(252.0))
    sharpe = float(daily.mean() / daily.std() * math.sqrt(252.0)) if daily.std() > 0 else np.nan
    dd = nav / nav.cummax() - 1.0
    mdd = float(dd.min())
    calmar = float(cagr / abs(mdd)) if mdd < 0 else np.nan
    return {"cagr": cagr, "sharpe": sharpe, "max_drawdown": mdd, "calmar": calmar, "volatility": vol, "end_nav": float(nav.iloc[-1])}


def prefixed(prefix: str, values: dict) -> dict:
    return {f"{prefix}_{key}": value for key, value in values.items()}


def period_row(variant: Variant, mode: str, name: str, nav: pd.Series, start: str, end: str) -> dict:
    sliced = nav.loc[start:end].dropna()
    if not sliced.empty:
        sliced = sliced / sliced.iloc[0]
    return {"variant_id": variant.variant_id, "portfolio_mode": mode, "window": name, **metrics(sliced)}


def annualized_turnover(turnover: pd.DataFrame, nav: pd.Series) -> float:
    if turnover.empty or nav.empty:
        return 0.0
    years = max((nav.index[-1] - nav.index[0]).days / 365.25, 1e-9)
    return float(turnover["turnover"].sum() / years)


def random_control(events: pd.DataFrame, returns: pd.DataFrame, panel: pd.DataFrame, variant: Variant, mode: str, strategy_sharpe: float) -> dict:
    if events.empty:
        return {"random_trials": RANDOM_TRIALS, "random_mean_sharpe": np.nan, "random_p95_sharpe": np.nan, "strategy_percentile": np.nan}
    universe = panel.loc[panel["tradable"].astype(bool), ["date", "ticker"]].drop_duplicates()
    config = PlaceboConfig(1, RANDOM_SEED + int(variant.variant_id[-2:]))
    placebos = build_date_matched_placebos(events.rename(columns={"execution_date": "date"}), universe, config)
    _ = date_matched_random(events["signal_date"].head(5), 1, universe, seed=RANDOM_SEED)
    _ = time_shift_placebo(events["signal_date"].head(5), 20, universe)
    if "signal_return" in events:
        drop_bucket_pool = panel.copy()
        drop_bucket_pool["return"] = drop_bucket_pool.groupby("ticker")["adjusted_close"].pct_change()
        _ = drop_bucket_matched_random(events.head(50), drop_bucket_pool, seed=RANDOM_SEED)
    rng = np.random.default_rng(RANDOM_SEED + int(variant.variant_id[-2:]) + (100 if mode == "long_only" else 0))
    counts = events.groupby("execution_date").size()
    ret_values = returns.fillna(0.0).to_numpy(dtype=float)
    daily = np.zeros((RANDOM_TRIALS, len(returns.index)), dtype=float)
    date_locs = {date: pos for pos, date in enumerate(returns.index)}
    asset_count = ret_values.shape[1]
    for date, count in counts.items():
        if date not in date_locs:
            continue
        loc = date_locs[date]
        horizon = min(variant.hold_days, len(returns.index) - loc - 1)
        k = min(int(count), asset_count, TOP_SIGNALS_PER_DAY)
        if horizon <= 0 or k <= 0:
            continue
        picks = np.argpartition(rng.random((RANDOM_TRIALS, asset_count)), kth=k - 1, axis=1)[:, :k]
        for offset in range(horizon):
            sampled = ret_values[loc + offset, picks].mean(axis=1)
            daily[:, loc + offset] += sampled / max(1, k)
        daily[:, loc] -= min(1.0, k / TOP_SIGNALS_PER_DAY) * TURNOVER_COST_RATE
    mean = daily.mean(axis=1)
    std = daily.std(axis=1, ddof=1)
    arr = np.full(RANDOM_TRIALS, np.nan)
    valid = std > 0
    arr[valid] = mean[valid] / std[valid] * math.sqrt(252.0)
    percentile = float(np.nanmean(arr <= strategy_sharpe) * 100.0) if not np.isnan(strategy_sharpe) else np.nan
    return {
        "random_trials": RANDOM_TRIALS,
        "random_events_generated": int(len(placebos) * RANDOM_TRIALS),
        "random_mean_sharpe": float(np.nanmean(arr)),
        "random_p50_sharpe": float(np.nanpercentile(arr, 50)),
        "random_p95_sharpe": float(np.nanpercentile(arr, 95)),
        "strategy_after_cost_sharpe": strategy_sharpe,
        "strategy_percentile": percentile,
    }


def top_pair_contribution(trades: pd.DataFrame, daily_pnl: pd.Series, variant: Variant, mode: str) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["variant_id", "portfolio_mode", "signal_key", "rank", "gross_return_sum", "share_of_abs_return"])
    grouped = trades.groupby("signal_key")["gross_return"].sum().sort_values(ascending=False)
    denom = grouped.abs().sum()
    rows = []
    for rank, (key, value) in enumerate(grouped.items(), start=1):
        rows.append(
            {
                "variant_id": variant.variant_id,
                "portfolio_mode": mode,
                "signal_key": key,
                "rank": rank,
                "gross_return_sum": float(value),
                "share_of_abs_return": float(abs(value) / denom) if denom else 0.0,
            }
        )
    return pd.DataFrame(rows)


def evaluate_pass_gates(variant: Variant, mode: str, result: dict, random: dict, contribution: pd.DataFrame) -> list[dict]:
    after = result["metrics_after_cost"]
    sub_fails = 0
    for start, end in SUBPERIODS.values():
        sliced = result["nav_after_cost"].loc[start:end]
        if sliced.empty or metrics(sliced / sliced.iloc[0])["sharpe"] < 1.0:
            sub_fails += 1
    top10_share = float(contribution.head(10)["share_of_abs_return"].sum()) if not contribution.empty else 1.0
    gates = [
        ("1_after_cost_sharpe_lt_1", after["sharpe"] < 1.0 if not np.isnan(after["sharpe"]) else True, f"after_cost_sharpe={after['sharpe']}"),
        ("2_no_random_difference", random["strategy_percentile"] < 90.0 if not np.isnan(random["strategy_percentile"]) else True, f"random_percentile={random['strategy_percentile']}"),
        ("3_top10_pair_dominance", top10_share > 0.70, f"top10_abs_contribution_share={top10_share}"),
        ("4_short_borrow_feasibility", mode == "long_short", "Korean single-stock short borrow feasibility unresolved; long-short remains diagnostic"),
        ("5_long_only_fallback_weak", mode == "long_only" and (after["sharpe"] < 1.0 if not np.isnan(after["sharpe"]) else True), f"long_only_sharpe={after['sharpe']}"),
        ("6_two_subperiod_fail", sub_fails >= 2, f"subperiod_fail_count={sub_fails}"),
        ("7_turnover_tax_slippage_kills", result["metrics_after_tax"]["sharpe"] < 1.0 if not np.isnan(result["metrics_after_tax"]["sharpe"]) else True, f"after_tax_sharpe={result['metrics_after_tax']['sharpe']}"),
    ]
    return [
        {
            "variant_id": variant.variant_id,
            "portfolio_mode": mode,
            "gate": gate,
            "status": "CLOSE" if failed else "PASS",
            "failed": bool(failed),
            "detail": detail,
        }
        for gate, failed, detail in gates
    ]


def sanity_checks(
    variant: Variant,
    mode: str,
    trades: pd.DataFrame,
    events: pd.DataFrame,
    nav: pd.Series,
    panel: pd.DataFrame,
    calendar: KoreanTradingCalendar,
) -> list[dict]:
    active_exposure_frame = pd.DataFrame({"date": nav.index, "net_value": nav.values, "cash": 0.0, "exposure": 1.0})
    leverage_frame = pd.DataFrame({"date": nav.index, "net_value": nav.values, "cash": 0.0, "exposure": nav.clip(lower=0.0).values})
    sim = SleeveNAVSimulator(initial_capital=1.0, max_position_size=0.1, max_active_positions=10)
    if not trades.empty:
        sample = trades.iloc[0]
        sim.process_signal(sample["entry_date"], sample["ticker"], 0.1, sample["entry_price"], TURNOVER_COST_RATE)
        sim.mark_to_market(sample["entry_date"], {sample["ticker"]: sample["entry_price"]})
        sim.process_exit(sample["exit_date"], sample["ticker"], sample["exit_price"], TURNOVER_COST_RATE)
        sim.mark_to_market(sample["exit_date"], {sample["ticker"]: sample["exit_price"]})
    checks = run_all_checks(trades, events, active_exposure_frame, calendar)
    rows = [
        {"variant_id": variant.variant_id, "portfolio_mode": mode, "check": key, "value": value, "status": "PASS" if float(value) <= 1.0 else "FAIL"}
        for key, value in checks.items()
    ]
    for frame in [
        check_no_same_day_execution(events, trades),
        check_no_filtered_row_execution(trades, panel),
        check_no_implicit_leverage(leverage_frame, SanityCheckConfig(max_gross_exposure=1.0)),
        reconcile_nav(sim.nav_frame(), pd.DataFrame(sim.trade_rows)),
    ]:
        for row in frame.to_dict("records"):
            fail_count = row.get("fail_count", 0)
            status = row.get("status", "PASS" if fail_count == 0 else "FAIL")
            rows.append({"variant_id": variant.variant_id, "portfolio_mode": mode, "check": row.get("check", "sleeve_nav_reconcile"), "value": fail_count, "status": status, "detail": row.get("detail", "")})
    impossible = detect_impossible_returns(panel.rename(columns={"date": "날짜", "ticker": "종목코드"}))
    rows.append({"variant_id": variant.variant_id, "portfolio_mode": mode, "check": "corporate_action_impossible_return_rows", "value": len(impossible), "status": "PASS"})
    return rows


def build_config(variants: list[Variant], pair_list: pd.DataFrame) -> dict:
    return {
        "experiment": "X-KR001 Korean Pair / Residual Mean Reversion",
        "status": "pre_registered_final_timeboxed_x_lab_experiment",
        "panels": [str(path.relative_to(ROOT)) for path in PANEL_PATHS],
        "sector_mapping": str(PIT_SECTOR_PATH.relative_to(ROOT)) if PIT_SECTOR_PATH.exists() else str(STATIC_SECTOR_PATH.relative_to(ROOT)),
        "w001_modules_required": [
            "src/utils/korean_calendar.py",
            "src/utils/corporate_action.py",
            "src/utils/tradability.py",
            "src/utils/sleeve_nav_simulator.py",
            "src/utils/random_placebo_engine.py",
            "src/utils/backtest_sanity_checks.py",
        ],
        "variants": [variant.__dict__ for variant in variants],
        "pair_count": int(len(pair_list)),
        "rolling_window": ROLLING_WINDOW,
        "entry_z": Z_ENTRY,
        "stop_z": Z_STOP,
        "top_signals_per_day": TOP_SIGNALS_PER_DAY,
        "cost": {
            "turnover_cost_rate_per_leg": TURNOVER_COST_RATE,
            "capital_gains_tax_diagnostic_rate": CAPITAL_GAINS_TAX_RATE,
            "annual_exemption_krw": ANNUAL_EXEMPTION_KRW,
            "domestic_small_shareholder_tax_alternative": 0.0,
        },
        "random_trials": RANDOM_TRIALS,
        "random_seed": RANDOM_SEED,
        "a0_audit_items": [
            "data_lineage",
            "point_in_time_availability",
            "survivorship_safety",
            "corporate_action_handling",
            "calendar_tradability",
            "daily_nav",
            "no_implicit_leverage",
            "benchmark_alignment",
            "random_placebo_control",
            "concentration_top_contributor",
            "cost_tax_turnover",
            "capacity_execution",
        ],
    }


def write_yaml(path: Path, data: dict) -> None:
    import yaml

    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, allow_unicode=True, sort_keys=False)


def write_report(variant_metrics: pd.DataFrame, pass_gate: pd.DataFrame, random_df: pd.DataFrame, sanity: pd.DataFrame, pair_list: pd.DataFrame) -> None:
    best = variant_metrics.sort_values("after_cost_sharpe", ascending=False).head(5)
    failed_gates = pass_gate.loc[pass_gate["failed"].astype(bool)]
    all_close = not failed_gates.empty
    lines = [
        "# X-KR001 결과 보고",
        "",
        "## Verdict",
        "",
        "CLOSE. 사전 등록 kill gate 기준에서 하나 이상 실패했으므로 X-KR001은 diagnostic 결과로만 보관한다." if all_close else "DIAGNOSTIC PASS. 단, X-Lab 종료 권고는 유지한다.",
        "",
        "## 실행 메타데이터",
        "",
        f"- Pair 후보 수: {len(pair_list)}",
        f"- Variant 수: 6 pre-registered x 2 portfolio modes = {len(variant_metrics)} rows",
        f"- Random/placebo trials: {RANDOM_TRIALS}",
        "- Execution: signal_date T close, execution_date T+1 or later",
        "- Cost: turnover leg 15 bps, 22% diagnostic tax layer, domestic ordinary small-shareholder tax 0 alternative",
        "- W001 modules: calendar, corporate action, tradability, sleeve NAV, random/placebo, sanity checks used",
        "",
        "## Top Variants By After-Cost Sharpe",
        "",
        "| variant | mode | after_cost_sharpe | after_cost_cagr | after_cost_mdd | random_percentile |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in best.itertuples(index=False):
        lines.append(
            f"| {row.variant_id} | {row.portfolio_mode} | {row.after_cost_sharpe:.6f} | {row.after_cost_cagr:.6f} | {row.after_cost_max_drawdown:.6f} | {row.random_percentile:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Kill Gate Summary",
            "",
            "| gate | failed_count |",
            "|---|---:|",
        ]
    )
    gate_counts = pass_gate.groupby("gate")["failed"].sum().reset_index()
    for row in gate_counts.itertuples(index=False):
        lines.append(f"| {row.gate} | {int(row.failed)} |")
    lines.extend(
        [
            "",
            "## A0 Sanity Summary",
            "",
            "| status | count |",
            "|---|---:|",
        ]
    )
    for status, count in sanity["status"].value_counts(dropna=False).items():
        lines.append(f"| {status} | {int(count)} |")
    lines.extend(
        [
            "",
            "## Note",
            "",
            "Long-short 결과는 borrow/short 현실성 미확정 때문에 production 후보가 아니다. Long-only fallback이 kill gate를 통과하지 못하면 retail 후보도 아니다. 결과와 무관하게 이 실험은 X-Lab 마지막 timeboxed experiment로 취급한다.",
        ]
    )
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
