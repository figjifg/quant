from __future__ import annotations

from src.audit.n_family_stress import run_experiment


VARIANTS = {
    "N003-A": {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "TLT": 0.30},
    "N003-B": {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "SHY": 0.15, "IEF": 0.15},
    "N003-C": {"SPY": 0.29, "QQQ": 0.21, "H001": 0.20, "SHY": 0.10, "IEF": 0.10, "TLT": 0.10},
}


def main() -> None:
    run_experiment(
        experiment_id="N003",
        slug="duration_mix",
        title="N003 Duration Mix",
        variants=VARIANTS,
        hypotheses=[
            "Long duration TLT may improve GFC-like stress response.",
            "Short/medium duration mixes may reduce 2022 rate-shock damage.",
        ],
        emphasis=[
            "Primary comparison is 2022 rate-shock response: TLT long-duration risk versus SHY short-duration defense.",
            "Local ETF standalone 2022 reference: TLT -29.38%, SHY -3.77% in USD close-to-close data.",
        ],
    )


if __name__ == "__main__":
    main()
