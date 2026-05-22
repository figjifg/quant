from __future__ import annotations

from src.audit.n_family_stress import run_experiment


VARIANTS = {
    "N001-A": {"SPY": 0.2755, "QQQ": 0.1995, "H001": 0.19, "IEF": 0.285, "GLD": 0.05},
    "N001-B": {"SPY": 0.261, "QQQ": 0.189, "H001": 0.18, "IEF": 0.27, "GLD": 0.10},
}


def main() -> None:
    run_experiment(
        experiment_id="N001",
        slug="gold_sleeve",
        title="N001 Gold Sleeve",
        variants=VARIANTS,
        hypotheses=[
            "GLD may act as a hedge during GFC-like stress.",
            "Historical reference: GLD was positive in 2008, approximately +12.5%.",
        ],
        emphasis=["GFC proxy와 2022 rate-shock에서 GLD sleeve의 변화가 핵심 비교 대상이다."],
    )


if __name__ == "__main__":
    main()
