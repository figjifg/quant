from __future__ import annotations

import pandas as pd

from src.strategies.b010_old_data_verification import VARIANTS, build_b010_candidates


def test_b010_candidates_build_frozen_carrier_and_cash_variant() -> None:
    features = _features()
    universe = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()

    candidates, exit_kwargs = build_b010_candidates(features, universe)

    assert tuple(candidates) == VARIANTS
    assert exit_kwargs["holding"] == 5
    assert "signal_exit_features" in exit_kwargs

    carrier = candidates["carrier_t3_f3"].reset_index(drop=True)
    baseline = candidates["t3_f1_baseline"].reset_index(drop=True)
    cash = candidates["cash"]

    assert carrier["종목코드"].tolist() == ["000010", "000010"]
    assert carrier["signal_date"].tolist() == [pd.Timestamp("2017-01-06"), pd.Timestamp("2017-01-09")]
    assert baseline["종목코드"].value_counts().to_dict() == {"000010": 6, "000020": 2}
    ticker2_dates = baseline.loc[baseline["종목코드"].eq("000020"), "signal_date"].tolist()
    assert ticker2_dates == [pd.Timestamp("2017-01-06"), pd.Timestamp("2017-01-09")]
    assert cash.empty


def _features() -> pd.DataFrame:
    rows = []
    dates = pd.date_range("2017-01-02", periods=6, freq="B")
    for index, date in enumerate(dates):
        rows.extend(
            [
                _row(date, "000010", fnv_5=0.10 + index * 0.01, inv_5=0.20, combined_flow_1=0.20, combined_flow_5=0.80),
                _row(
                    date,
                    "000020",
                    fnv_5=0.20 + index * 0.01,
                    inv_5=0.10,
                    combined_flow_1=0.20 if index >= 4 else -0.10,
                    combined_flow_5=0.90,
                ),
                _row(date, "000030", fnv_5=-0.10, inv_5=0.30, combined_flow_1=0.30, combined_flow_5=1.00),
            ]
        )
    return pd.DataFrame(rows)


def _row(
    signal_date: pd.Timestamp,
    ticker: str,
    *,
    fnv_5: float,
    inv_5: float,
    combined_flow_1: float,
    combined_flow_5: float,
) -> dict[str, object]:
    return {
        "날짜": signal_date,
        "signal_date": signal_date,
        "execution_date": signal_date + pd.offsets.BDay(1),
        "종목코드": ticker,
        "fnv_5": fnv_5,
        "inv_5": inv_5,
        "combined_flow_1": combined_flow_1,
        "combined_flow_5": combined_flow_5,
    }
