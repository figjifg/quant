from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class SleeveNavConfig:
    initial_nav: float = 1.0
    max_gross_exposure: float = 1.0
    allow_leverage: bool = False


@dataclass
class Position:
    ticker: str
    quantity: float
    entry_price: float
    market_price: float
    cost_basis: float
    entry_date: pd.Timestamp


@dataclass
class SleeveNAVSimulator:
    initial_capital: float
    max_position_size: float
    max_active_positions: int
    cash_idle_allowed: bool = True
    cash: float = field(init=False)
    positions: dict[str, Position] = field(default_factory=dict, init=False)
    nav_rows: list[dict] = field(default_factory=list, init=False)
    trade_rows: list[dict] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.cash = float(self.initial_capital)

    def _nav(self) -> float:
        return self.cash + sum(position.quantity * position.market_price for position in self.positions.values())

    def total_exposure(self, date: object | None = None) -> float:
        return sum(position.quantity * position.market_price for position in self.positions.values())

    def process_signal(self, date: object, ticker: str, weight: float, price: float | None = None, cost_rate: float = 0.0) -> bool:
        if ticker in self.positions or len(self.positions) >= self.max_active_positions:
            return False
        price = float(price if price is not None else 1.0)
        if price <= 0:
            return False
        target = min(float(weight) * self.initial_capital, self.max_position_size * self.initial_capital)
        available = min(target, self.cash / (1.0 + cost_rate))
        max_exposure_left = max(0.0, self.initial_capital - self.total_exposure())
        notional = min(available, max_exposure_left)
        if notional <= 0:
            return False
        fee = notional * cost_rate
        quantity = notional / price
        self.cash -= notional + fee
        self.positions[ticker] = Position(str(ticker), quantity, price, price, notional, pd.Timestamp(date).normalize())
        self.trade_rows.append({"date": pd.Timestamp(date).normalize(), "ticker": ticker, "action": "entry", "notional": notional, "cost_paid": fee})
        return True

    def process_exit(self, date: object, ticker: str, price: float | None = None, cost_rate: float = 0.0) -> bool:
        ticker = str(ticker)
        if ticker not in self.positions:
            return False
        position = self.positions.pop(ticker)
        price = float(price if price is not None else position.market_price)
        proceeds = position.quantity * price
        fee = proceeds * cost_rate
        self.cash += proceeds - fee
        self.trade_rows.append({"date": pd.Timestamp(date).normalize(), "ticker": ticker, "action": "exit", "notional": proceeds, "cost_paid": fee})
        return True

    def mark_to_market(self, date: object, prices: dict[str, float] | pd.Series | None = None) -> dict:
        if prices is not None:
            for ticker, position in self.positions.items():
                if ticker in prices and pd.notna(prices[ticker]):
                    position.market_price = float(prices[ticker])
        exposure = self.total_exposure(date)
        if exposure > self.initial_capital * (1.0 + 1e-9):
            raise ValueError(f"implicit leverage detected: exposure={exposure}")
        row = {
            "date": pd.Timestamp(date).normalize(),
            "gross_value": self.cash + exposure,
            "net_value": self.cash + exposure,
            "cash": self.cash,
            "n_positions": len(self.positions),
            "exposure": exposure,
        }
        self.nav_rows.append(row)
        return row

    def daily_nav_series(self) -> pd.Series:
        if not self.nav_rows:
            return pd.Series(dtype=float)
        frame = pd.DataFrame(self.nav_rows).drop_duplicates("date", keep="last").sort_values("date")
        return pd.Series(frame["net_value"].values, index=pd.to_datetime(frame["date"]), name="net_value")

    def turnover_by_period(self, freq: str) -> pd.Series:
        if not self.trade_rows:
            return pd.Series(dtype=float)
        trades = pd.DataFrame(self.trade_rows)
        trades["date"] = pd.to_datetime(trades["date"])
        return trades.groupby(trades["date"].dt.to_period(freq))["notional"].sum()

    def nav_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.nav_rows)


def simulate_sleeve_nav(trades: pd.DataFrame, prices: pd.DataFrame, config: SleeveNavConfig) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["date", "gross_value", "net_value", "cash", "n_positions", "exposure"])
    simulator = SleeveNAVSimulator(
        initial_capital=float(config.initial_nav),
        max_position_size=float(config.max_gross_exposure),
        max_active_positions=max(1, len(trades)),
        cash_idle_allowed=True,
    )
    price_lookup = {}
    if not prices.empty:
        date_col = "date" if "date" in prices.columns else "날짜"
        ticker_col = "ticker" if "ticker" in prices.columns else "종목코드"
        close_col = "adjusted_close" if "adjusted_close" in prices.columns else "KRX종가"
        price_lookup = {
            (pd.Timestamp(row[date_col]).normalize(), str(row[ticker_col])): float(row[close_col])
            for _, row in prices[[date_col, ticker_col, close_col]].dropna().iterrows()
        }
    for row in trades.sort_values(["entry_date", "exit_date"]).itertuples(index=False):
        entry_date = pd.Timestamp(getattr(row, "entry_date", getattr(row, "execution_date", None))).normalize()
        exit_date = pd.Timestamp(row.exit_date).normalize()
        ticker = str(row.ticker)
        entry_price = float(getattr(row, "entry_price", price_lookup.get((entry_date, ticker), 1.0)))
        exit_price = float(getattr(row, "exit_price", price_lookup.get((exit_date, ticker), entry_price)))
        simulator.process_signal(entry_date, ticker, 1.0 / max(1, len(trades)), entry_price)
        simulator.mark_to_market(entry_date, {ticker: entry_price})
        simulator.process_exit(exit_date, ticker, exit_price)
        simulator.mark_to_market(exit_date, {ticker: exit_price})
    return simulator.nav_frame()


def reconcile_nav(nav: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
    if nav.empty:
        return pd.DataFrame([{"check": "nav_nonempty", "status": "FAIL", "detail": "empty nav"}])
    rows = [
        {"check": "nav_nonempty", "status": "PASS", "detail": f"{len(nav)} rows"},
        {"check": "cash_nonnegative", "status": "PASS" if nav["cash"].min() >= -1e-6 else "FAIL", "detail": f"min_cash={nav['cash'].min()}"},
        {"check": "trade_count", "status": "PASS", "detail": str(len(trades))},
    ]
    return pd.DataFrame(rows)
