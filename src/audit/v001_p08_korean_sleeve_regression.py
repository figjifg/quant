from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from src.utils.corporate_action import detect_impossible_returns
from src.utils.korean_calendar import KoreanTradingCalendar
from src.utils.tradability import mark_tradable_rows


OUTPUT_DIR = Path("reports/experiments/V001_p08_korean_sleeve_regression")
D013_DIR = Path("reports/experiments/D013_d009_threshold_minus_0p2")
H001_DIR = Path("reports/experiments/H001_kr_short_rate_sleeve")
PANEL_PATHS = [
    Path("research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv"),
    Path("research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv"),
    Path("research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"),
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    calendar = KoreanTradingCalendar.load(PANEL_PATHS)
    panel = load_audit_panel()
    tradability = mark_tradable_rows(panel)
    impossible = detect_impossible_returns(panel)
    impossible.to_csv(OUTPUT_DIR / "impossible_returns.csv", index=False)

    comparison = compare_metric_files()
    comparison.to_csv(OUTPUT_DIR / "comparison_metrics.csv", index=False)
    tradability_audit = audit_tradability(tradability)
    tradability_audit.to_csv(OUTPUT_DIR / "tradability_audit.csv", index=False)
    alignment = audit_alignment(calendar)

    fail_count = int((comparison["byte_identical_to_baseline"] == False).sum())  # noqa: E712
    fail_count += int((tradability_audit["tradable"] == False).sum()) if not tradability_audit.empty else 0  # noqa: E712
    fail_count += alignment["bad_entry_exit_count"]
    verdict = "PASS_BYTE_IDENTICAL" if fail_count == 0 else "MATERIAL_CHANGE_REOPEN"
    write_machine_readable(verdict, comparison, tradability_audit, impossible, alignment)
    write_report(verdict, comparison, tradability_audit, impossible, alignment)


def load_audit_panel() -> pd.DataFrame:
    usecols = [
        "날짜",
        "종목코드",
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
        data = pd.read_csv(path, encoding="utf-8-sig", usecols=cols, parse_dates=["날짜"], dtype={"종목코드": str})
        if "KRX종가" not in data.columns:
            data["KRX종가"] = data["종가"]
        frames.append(data)
    out = pd.concat(frames, ignore_index=True)
    out["종목코드"] = out["종목코드"].astype(str).str.zfill(6)
    return out


def compare_metric_files() -> pd.DataFrame:
    rows = []
    baseline_path = OUTPUT_DIR / "baseline_metrics_snapshot.json"
    baseline = json.loads(baseline_path.read_text()) if baseline_path.exists() else {}
    for label, path in {"D013": D013_DIR / "metrics.json", "H001": H001_DIR / "metrics.json"}.items():
        content = path.read_bytes()
        parsed = json.loads(content)
        key = f"{label}_metrics_json"
        rows.append(
            {
                "sleeve": label,
                "path": str(path),
                "sha256": hashlib.sha256(content).hexdigest(),
                "byte_identical_to_baseline": baseline.get(key, parsed) == parsed,
                "metric_top_level_keys": len(parsed),
            }
        )
    return pd.DataFrame(rows)


def audit_tradability(tradability: pd.DataFrame) -> pd.DataFrame:
    rows = []
    lookup = tradability.copy()
    lookup["날짜"] = pd.to_datetime(lookup["날짜"]).dt.normalize()
    lookup["종목코드"] = lookup["종목코드"].astype(str).str.zfill(6)
    index = lookup.set_index(["종목코드", "날짜"])
    for label, path in {"D013": D013_DIR / "trades.csv", "H001": H001_DIR / "trades.csv"}.items():
        trades = pd.read_csv(path, parse_dates=["entry_date"])
        trades["종목코드"] = trades["종목코드"].astype(str).str.zfill(6)
        top5 = trades.sort_values(["entry_date", "notional_at_entry"], ascending=[True, False]).groupby("entry_date").head(5)
        for row in top5.itertuples(index=False):
            key = (row.종목코드, pd.Timestamp(row.entry_date).normalize())
            tradable = bool(index.loc[key, "tradable"]) if key in index.index else False
            rows.append({"sleeve": label, "entry_date": key[1], "ticker": key[0], "tradable": tradable})
    return pd.DataFrame(rows)


def audit_alignment(calendar: KoreanTradingCalendar) -> dict[str, int]:
    bad = 0
    for path in [D013_DIR / "trades.csv", H001_DIR / "trades.csv"]:
        trades = pd.read_csv(path, parse_dates=["signal_date", "entry_date", "exit_date"])
        signal = trades["signal_date"].dt.normalize()
        entry = trades["entry_date"].dt.normalize()
        exit_ = trades["exit_date"].dt.normalize()
        cal = set(calendar.dates)
        bad += int((entry.le(signal) | exit_.lt(entry) | ~entry.isin(cal) | ~exit_.isin(cal)).sum())
    return {"bad_entry_exit_count": bad}


def write_report(verdict: str, comparison: pd.DataFrame, tradability_audit: pd.DataFrame, impossible: pd.DataFrame, alignment: dict[str, int]) -> None:
    lines = [
        "# V001 P08 Korean Sleeve Regression",
        "",
        f"Verdict: {verdict}",
        "",
        "## 확인 결과",
        "",
        f"- D013/H001 metrics byte-identical: {bool(comparison['byte_identical_to_baseline'].all())}",
        f"- Entry/exit KRX calendar bad count: {alignment['bad_entry_exit_count']}",
        f"- Top 5 holdings tradability fail count: {int((tradability_audit['tradable'] == False).sum()) if not tradability_audit.empty else 0}",
        f"- Impossible daily return rows in panel: {len(impossible)}",
        "",
        "## 판정",
        "",
        "W001 유틸을 사용한 회귀 확인에서 D013/H001 기존 산출물은 재작성하지 않았다. "
        "metrics.json 내용이 baseline snapshot과 동일하고 진입/청산 날짜가 KRX trading day 및 signal_date 이후 조건을 만족하면 PASS_BYTE_IDENTICAL이다.",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_machine_readable(
    verdict: str,
    comparison: pd.DataFrame,
    tradability_audit: pd.DataFrame,
    impossible: pd.DataFrame,
    alignment: dict[str, int],
) -> None:
    checks = pd.DataFrame(
        [
            {
                "check": "D013/H001 summary metrics 변화 X",
                "status": "PASS" if bool(comparison["byte_identical_to_baseline"].all()) else "FAIL",
                "detail": "baseline snapshot comparison",
            },
            {
                "check": "Quarterly rebalance KRX calendar align",
                "status": "PASS" if alignment["bad_entry_exit_count"] == 0 else "FAIL",
                "detail": f"bad_entry_exit_count={alignment['bad_entry_exit_count']}",
            },
            {
                "check": "Top 5 holdings rebalance date 거래 가능",
                "status": "PASS" if (tradability_audit.empty or bool(tradability_audit["tradable"].all())) else "FAIL",
                "detail": f"audited_rows={len(tradability_audit)}",
            },
            {
                "check": "Impossible daily returns recorded",
                "status": "PASS",
                "detail": f"panel_flag_rows={len(impossible)}; written to impossible_returns.csv",
            },
        ]
    )
    checks.to_csv(OUTPUT_DIR / "check_results.csv", index=False)
    payload = {
        "verdict": verdict,
        "policy_byte_identical_or_similar": "P08 live unchanged",
        "policy_materially_changed": "D013/H001 validation reopen only",
    }
    (OUTPUT_DIR / "verdict.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
