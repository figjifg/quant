from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.ops.nav_update import DEFAULT_PORTFOLIOS, ROOT, load_component_nav
from src.ops.rebalance_report import drifted_weights, quarter_end_proxy, quarter_start_proxy


OUTPUT_DIR = ROOT / "paper_trading/operations/dryrun"
TARGET = DEFAULT_PORTFOLIOS["P08_IEF30"]
US_ETFS = ("SPY", "QQQ", "IEF")
COMMISSION_RATE = 0.0025
FX_SPREAD_RATE = 0.001
SLIPPAGE_RATE = 0.0005
ANNUAL_EXEMPTION_KRW = 2_500_000.0


def generate_dryrun(
    quarter: str,
    nav_krw: float = 100_000_000.0,
    cash_krw: float = 0.0,
    cash_usd: float = 0.0,
    output_path: str | Path | None = None,
) -> Path:
    as_of = quarter_end_proxy(quarter)
    component_nav = load_component_nav(as_of)
    quarter_nav = component_nav.loc[component_nav.index >= quarter_start_proxy(quarter)]
    if quarter_nav.empty:
        raise ValueError(f"No component NAV rows for {quarter}")

    current_weights = drifted_weights(quarter_nav, TARGET)
    latest = quarter_nav.iloc[-1]
    previous = quarter_nav.iloc[-2] if len(quarter_nav) > 1 else quarter_nav.iloc[-1]
    rows = build_order_rows(current_weights, latest, previous, nav_krw)
    order_sheet = pd.DataFrame(rows)
    usd_buy_need = order_sheet.loc[
        order_sheet["ticker"].isin(US_ETFS) & order_sheet["trade_krw"].gt(0), "trade_krw"
    ].sum()
    usd_sell_source = -order_sheet.loc[
        order_sheet["ticker"].isin(US_ETFS) & order_sheet["trade_krw"].lt(0), "trade_krw"
    ].sum()
    fx_needed = max(0.0, usd_buy_need - usd_sell_source - cash_usd_to_krw(cash_usd))
    costs = estimate_costs(order_sheet, fx_needed)

    path = Path(output_path) if output_path else OUTPUT_DIR / f"{quarter}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_report(
            quarter=quarter,
            as_of=as_of,
            nav_krw=nav_krw,
            cash_krw=cash_krw,
            cash_usd=cash_usd,
            current_weights=current_weights,
            order_sheet=order_sheet,
            fx_needed=fx_needed,
            costs=costs,
        ),
        encoding="utf-8",
    )
    return path


def build_order_rows(
    current_weights: dict[str, float],
    latest_nav: pd.Series,
    previous_nav: pd.Series,
    nav_krw: float,
) -> list[dict]:
    rows = []
    for ticker, target_weight in TARGET.items():
        current_weight = current_weights[ticker]
        target_krw = nav_krw * target_weight
        current_krw = nav_krw * current_weight
        trade_krw = target_krw - current_krw
        proxy_price = float(latest_nav[ticker])
        paper_execution_price = proxy_price
        next_day_proxy = float(latest_nav[ticker])
        prior_proxy = float(previous_nav[ticker])
        quantity_proxy = 0.0 if proxy_price == 0 else trade_krw / proxy_price
        rows.append(
            {
                "ticker": ticker,
                "current_weight": current_weight,
                "target_weight": target_weight,
                "current_krw": current_krw,
                "target_krw": target_krw,
                "trade_krw": trade_krw,
                "action": "BUY" if trade_krw > 0 else "SELL" if trade_krw < 0 else "HOLD",
                "quantity_proxy": quantity_proxy,
                "paper_execution_price": paper_execution_price,
                "next_day_fill_discrepancy_proxy": next_day_proxy / prior_proxy - 1.0 if prior_proxy else 0.0,
            }
        )
    return rows


def cash_usd_to_krw(cash_usd: float) -> float:
    return cash_usd


def estimate_costs(order_sheet: pd.DataFrame, fx_needed_krw: float) -> dict[str, float]:
    traded_notional = order_sheet["trade_krw"].abs().sum()
    sell_notional = -order_sheet.loc[order_sheet["trade_krw"].lt(0), "trade_krw"].sum()
    commission = traded_notional * COMMISSION_RATE
    slippage = traded_notional * SLIPPAGE_RATE
    fx_spread = fx_needed_krw * FX_SPREAD_RATE
    return {
        "traded_notional_krw": traded_notional,
        "sell_notional_krw": sell_notional,
        "commission_krw": commission,
        "slippage_krw": slippage,
        "fx_spread_krw": fx_spread,
        "total_estimated_cost_krw": commission + slippage + fx_spread,
    }


def render_report(
    quarter: str,
    as_of: pd.Timestamp,
    nav_krw: float,
    cash_krw: float,
    cash_usd: float,
    current_weights: dict[str, float],
    order_sheet: pd.DataFrame,
    fx_needed: float,
    costs: dict[str, float],
) -> str:
    return "\n".join(
        [
            f"# U001 Quarterly Dry-run {quarter}",
            "",
            "Status: DRY-RUN ONLY. This file is not live order authorization.",
            "",
            "## 1. 기준 NAV",
            "",
            f"- 기준일: {as_of.date()}",
            f"- 기준 NAV: {nav_krw:,.0f} KRW",
            f"- 현금: {cash_krw:,.0f} KRW / {cash_usd:,.2f} USD",
            "",
            "## 2. 현재 비중",
            "",
            markdown_table(
                pd.DataFrame(
                    [{"ticker": k, "current_weight": v, "target_weight": TARGET[k]} for k, v in current_weights.items()]
                )
            ),
            "",
            "## 3. 목표 비중",
            "",
            "- SPY 29% / QQQ 21% / H001 20% / IEF 30%.",
            "",
            "## 4. 매수/매도 수량",
            "",
            markdown_table(order_sheet),
            "",
            "## 5. 환전 필요액",
            "",
            f"- 예상 KRW->USD 환전 필요액: {fx_needed:,.0f} KRW",
            "- 매도 체결 가능 USD를 먼저 반영한 뒤 부족분만 환전한다.",
            "",
            "## 6. 세금 lot impact",
            "",
            f"- HIFO lot 기준으로 해외 ETF 매도분을 확인한다.",
            f"- 연간 기본공제 기준값: {ANNUAL_EXEMPTION_KRW:,.0f} KRW.",
            "- 이 dry-run은 lot export가 없으므로 세액을 확정하지 않는다.",
            "",
            "## 7. 예상 수수료/환전",
            "",
            markdown_table(pd.DataFrame([costs])),
            "",
            "## 8. 주문장 작성",
            "",
            "- 시장가 주문 금지.",
            "- 지정가 또는 VWAP 근사 분할 주문.",
            "- 부분 체결 시 남은 수량은 재계산 후 다음 세션에서 처리.",
            "",
            "## 9. Paper execution price",
            "",
            "- `paper_execution_price`는 component NAV index 기준 proxy다.",
            "- live 주문 전 broker quote로 수량을 다시 산출한다.",
            "",
            "## 10. 다음 날 fill discrepancy",
            "",
            "- 다음 거래일 실제 체결가와 paper proxy의 차이를 이 파일에 append한다.",
            "- 괴리 누적이 설명되지 않으면 live 증액 금지.",
            "",
        ]
    ) + "\n"


def markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for _, row in frame.iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                values.append(f"{value:.6f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate U001 quarterly rebalance dry-run.")
    parser.add_argument("--quarter", required=True, help="Quarter label, e.g. 2026-Q2")
    parser.add_argument("--nav-krw", type=float, default=100_000_000.0)
    parser.add_argument("--cash-krw", type=float, default=0.0)
    parser.add_argument("--cash-usd", type=float, default=0.0)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = generate_dryrun(args.quarter, args.nav_krw, args.cash_krw, args.cash_usd, args.output)
    try:
        print(path.relative_to(ROOT))
    except ValueError:
        print(path)


if __name__ == "__main__":
    main()
