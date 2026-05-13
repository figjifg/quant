from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Costs:
    commission_bps: float
    tax_bps_sell: float
    slippage_bps: float


def buy_cost(notional: float, costs: Costs) -> float:
    return float(notional) * (costs.commission_bps + costs.slippage_bps) / 1e4


def sell_cost(notional: float, costs: Costs) -> float:
    return (
        float(notional)
        * (costs.commission_bps + costs.slippage_bps + costs.tax_bps_sell)
        / 1e4
    )
