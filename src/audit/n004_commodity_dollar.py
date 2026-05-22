from __future__ import annotations

from src.audit.n_family_stress import run_experiment


VARIANTS = {
    "N004-A": {"SPY": 0.2755, "QQQ": 0.1995, "H001": 0.19, "IEF": 0.285, "DBC": 0.05},
    "N004-B": {"SPY": 0.2755, "QQQ": 0.1995, "H001": 0.19, "IEF": 0.285, "UUP": 0.05},
    "N004-C": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "DBC": 0.05, "UUP": 0.05},
}


def main() -> None:
    run_experiment(
        experiment_id="N004",
        slug="commodity_dollar_sleeve",
        title="N004 Commodity / Dollar Sleeve",
        variants=VARIANTS,
        hypotheses=[
            "DBC may act as an inflation hedge.",
            "UUP may act as a strong-dollar hedge.",
        ],
        emphasis=[
            "2022 stress에서 DBC inflation hedge와 UUP dollar-strength hedge 효과를 비교한다.",
            "Local ETF standalone 2022 reference: DBC +18.88%, UUP +8.78% in USD close-to-close data.",
        ],
    )


if __name__ == "__main__":
    main()
