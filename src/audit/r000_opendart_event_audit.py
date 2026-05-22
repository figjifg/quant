from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "research_input_data" / "inputs" / "events" / "opendart_kospi_disclosures_20180101_20260505.parquet"
OUTPUT_DIR = ROOT / "reports" / "experiments" / "R000_opendart_event_data_audit"

EVENT_KEYWORDS = {
    "buyback_acquisition": ["자기주식취득", "자사주취득", "자사주 취득", "취득결정"],
    "buyback_disposal": ["자기주식처분", "자사주처분", "자사주 처분", "처분결정"],
    "buyback_retirement": ["자기주식소각", "자사주소각", "자사주 소각", "소각결정"],
    "cash_dividend": ["현금ㆍ현물배당", "현금/현물배당", "현금배당", "현물배당", "배당결정"],
    "interim_dividend": ["중간배당"],
    "quarterly_dividend": ["분기배당"],
    "shareholder_return_policy": ["주주환원정책", "주주 환원 정책", "주주환원"],
    "value_up_plan": ["기업가치 제고", "기업가치제고", "밸류업", "value-up", "value up"],
}

CORRECTION_KEYWORDS = ["정정", "첨부정정", "기재정정"]
CANCELLATION_KEYWORDS = ["취소", "철회"]
TIME_COLUMN_CANDIDATES = ["rcept_dt", "rcept_time", "접수시간", "공시시간", "disclosure_time", "time"]
DATE_COLUMN_CANDIDATES = ["rcept_dt", "공시일", "접수일", "disclosure_date", "date"]
TITLE_COLUMN_CANDIDATES = ["report_nm", "공시제목", "공시명", "title", "report_name"]
TICKER_COLUMN_CANDIDATES = ["stock_code", "종목코드", "ticker", "corp_code"]
NAME_COLUMN_CANDIDATES = ["corp_name", "종목명", "company_name", "name"]


def main() -> int:
    parser = argparse.ArgumentParser(description="R000 OPENDART shareholder-return event data audit.")
    parser.add_argument("--input", type=Path, default=INPUT_PATH)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    run(args.input, args.output_dir)
    return 0


def run(input_path: Path = INPUT_PATH, output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    config = build_config(input_path, output_dir)

    try:
        df = pd.read_parquet(input_path)
    except ImportError as exc:
        write_blocked_outputs(output_dir, config, f"{type(exc).__name__}: {exc}")
        return
    except Exception as exc:
        write_blocked_outputs(output_dir, config, f"{type(exc).__name__}: {exc}")
        return

    title_col = first_existing(df, TITLE_COLUMN_CANDIDATES)
    ticker_col = first_existing(df, TICKER_COLUMN_CANDIDATES)
    name_col = first_existing(df, NAME_COLUMN_CANDIDATES)
    date_col = first_existing(df, DATE_COLUMN_CANDIDATES)
    time_col = detect_time_column(df)

    if title_col is None:
        write_blocked_outputs(output_dir, config, "No disclosure title/report-name column was detected.")
        return

    audit = df.copy()
    audit["_event_text"] = build_event_text(audit, title_col)
    audit["_event_type"] = audit["_event_text"].map(classify_event)
    audit["_is_target_event"] = audit["_event_type"].ne("other")
    audit["_is_correction"] = audit["_event_text"].map(lambda value: contains_any(value, CORRECTION_KEYWORDS))
    audit["_is_cancellation"] = audit["_event_text"].map(lambda value: contains_any(value, CANCELLATION_KEYWORDS))

    if date_col is not None:
        audit["_event_date"] = parse_event_date(audit[date_col])
    else:
        audit["_event_date"] = pd.NaT

    if time_col is not None:
        audit["_event_time"] = parse_event_time(audit[time_col])
        audit["_session"] = audit["_event_time"].map(classify_session)
    else:
        audit["_event_time"] = pd.NA
        audit["_session"] = "missing_time"

    events = audit.loc[audit["_is_target_event"]].copy()
    write_config(output_dir / "config.yaml", config, df, title_col, ticker_col, name_col, date_col, time_col, events)
    build_event_type_distribution(events).to_csv(output_dir / "event_type_distribution.csv", index=False)
    build_ticker_distribution(events, ticker_col, name_col).to_csv(output_dir / "ticker_distribution.csv", index=False)
    build_time_distribution(events).to_csv(output_dir / "time_distribution.csv", index=False)
    sample_events(events, ["buyback_acquisition", "buyback_disposal", "buyback_retirement"], title_col, ticker_col, name_col).to_csv(
        output_dir / "sample_buyback_events.csv", index=False
    )
    sample_events(events, ["cash_dividend", "interim_dividend", "quarterly_dividend"], title_col, ticker_col, name_col).to_csv(
        output_dir / "sample_dividend_events.csv", index=False
    )
    write_report(output_dir / "report.md", df, events, title_col, ticker_col, name_col, date_col, time_col)


def build_config(input_path: Path, output_dir: Path) -> dict[str, str]:
    return {
        "experiment": "R000_opendart_event_data_audit",
        "input_path": str(input_path.relative_to(ROOT) if input_path.is_relative_to(ROOT) else input_path),
        "output_dir": str(output_dir.relative_to(ROOT) if output_dir.is_relative_to(ROOT) else output_dir),
        "network": "disabled",
        "strategy_changes": "none",
        "engine_changes": "none",
    }


def first_existing(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lowered = {str(col).lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    return None


def detect_time_column(df: pd.DataFrame) -> str | None:
    for candidate in TIME_COLUMN_CANDIDATES:
        col = first_existing(df, [candidate])
        if col is not None:
            return col
    return None


def build_event_text(df: pd.DataFrame, title_col: str) -> pd.Series:
    parts = [df[title_col].fillna("").astype(str)]
    for col in df.columns:
        col_text = str(col)
        if col != title_col and any(token in col_text.lower() for token in ["type", "kind", "유형", "종류"]):
            parts.append(df[col].fillna("").astype(str))
    text = parts[0]
    for part in parts[1:]:
        text = text.str.cat(part, sep=" ")
    return text.str.lower()


def classify_event(text: str) -> str:
    for event_type, keywords in EVENT_KEYWORDS.items():
        if contains_any(text, keywords):
            return event_type
    return "other"


def contains_any(text: str, keywords: list[str]) -> bool:
    lowered = str(text).lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def parse_event_date(series: pd.Series) -> pd.Series:
    values = series.astype(str).str.extract(r"(\d{8}|\d{4}[-./]\d{2}[-./]\d{2})", expand=False)
    return pd.to_datetime(values, errors="coerce")


def parse_event_time(series: pd.Series) -> pd.Series:
    text = series.astype(str)
    hhmmss = text.str.extract(r"(\d{2}:\d{2}(?::\d{2})?|\d{6}|\d{4})", expand=False)
    compact = hhmmss.str.replace(":", "", regex=False)
    compact = compact.where(compact.str.len().isin([4, 6]))
    compact = compact.str.slice(0, 2) + ":" + compact.str.slice(2, 4)
    return compact


def classify_session(value: object) -> str:
    if pd.isna(value):
        return "missing_time"
    text = str(value)
    if text < "09:00":
        return "pre_open"
    if text <= "15:30":
        return "intraday"
    return "after_close"


def build_event_type_distribution(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["event_type", "count", "pct", "correction_count", "cancellation_count", "missing_time_count"])
    grouped = events.groupby("_event_type", dropna=False)
    out = grouped.agg(
        count=("_event_type", "size"),
        correction_count=("_is_correction", "sum"),
        cancellation_count=("_is_cancellation", "sum"),
        missing_time_count=("_session", lambda s: int((s == "missing_time").sum())),
    ).reset_index(names="event_type")
    out["pct"] = out["count"] / out["count"].sum()
    return out[["event_type", "count", "pct", "correction_count", "cancellation_count", "missing_time_count"]].sort_values(
        ["count", "event_type"], ascending=[False, True]
    )


def build_ticker_distribution(events: pd.DataFrame, ticker_col: str | None, name_col: str | None) -> pd.DataFrame:
    columns = ["ticker", "name", "event_count", "event_types", "correction_count", "cancellation_count"]
    if events.empty or ticker_col is None:
        return pd.DataFrame(columns=columns)
    name_series = events[name_col] if name_col is not None else ""
    tmp = events.assign(_ticker=events[ticker_col].astype(str), _name=name_series)
    grouped = tmp.groupby("_ticker", dropna=False)
    out = grouped.agg(
        name=("_name", "first"),
        event_count=("_ticker", "size"),
        event_types=("_event_type", lambda s: "|".join(sorted(set(s.astype(str))))),
        correction_count=("_is_correction", "sum"),
        cancellation_count=("_is_cancellation", "sum"),
    ).reset_index(names="ticker")
    return out[columns].sort_values(["event_count", "ticker"], ascending=[False, True]).head(100)


def build_time_distribution(events: pd.DataFrame) -> pd.DataFrame:
    columns = ["year", "month", "event_count", "intraday_count", "after_close_count", "missing_time_count"]
    if events.empty:
        return pd.DataFrame(columns=columns)
    dated = events.dropna(subset=["_event_date"]).copy()
    if dated.empty:
        return pd.DataFrame(columns=columns)
    dated["year"] = dated["_event_date"].dt.year
    dated["month"] = dated["_event_date"].dt.month
    out = dated.groupby(["year", "month"]).agg(
        event_count=("_event_type", "size"),
        intraday_count=("_session", lambda s: int((s == "intraday").sum())),
        after_close_count=("_session", lambda s: int((s == "after_close").sum())),
        missing_time_count=("_session", lambda s: int((s == "missing_time").sum())),
    ).reset_index()
    return out[columns].sort_values(["year", "month"])


def sample_events(
    events: pd.DataFrame,
    event_types: list[str],
    title_col: str,
    ticker_col: str | None,
    name_col: str | None,
) -> pd.DataFrame:
    columns = ["event_date", "event_time", "session", "ticker", "name", "event_type", "title", "is_correction", "is_cancellation"]
    subset = events.loc[events["_event_type"].isin(event_types)].copy()
    if subset.empty:
        return pd.DataFrame(columns=columns)
    subset = subset.sort_values(["_event_date", title_col], na_position="last").head(30)
    return pd.DataFrame(
        {
            "event_date": subset["_event_date"].dt.date.astype(str),
            "event_time": subset["_event_time"].astype(str),
            "session": subset["_session"].astype(str),
            "ticker": subset[ticker_col].astype(str) if ticker_col is not None else "",
            "name": subset[name_col].astype(str) if name_col is not None else "",
            "event_type": subset["_event_type"].astype(str),
            "title": subset[title_col].astype(str),
            "is_correction": subset["_is_correction"].astype(bool),
            "is_cancellation": subset["_is_cancellation"].astype(bool),
        }
    )[columns]


def write_config(
    path: Path,
    config: dict[str, str],
    df: pd.DataFrame,
    title_col: str | None,
    ticker_col: str | None,
    name_col: str | None,
    date_col: str | None,
    time_col: str | None,
    events: pd.DataFrame,
) -> None:
    lines = [f"{key}: {value}" for key, value in config.items()]
    lines.extend(
        [
            f"row_count: {len(df)}",
            "columns:",
            *[f"  - {col}" for col in df.columns],
            "dtypes:",
            *[f"  {col}: {dtype}" for col, dtype in df.dtypes.items()],
            f"title_column: {title_col or ''}",
            f"ticker_column: {ticker_col or ''}",
            f"name_column: {name_col or ''}",
            f"date_column: {date_col or ''}",
            f"time_column: {time_col or ''}",
            f"target_event_count: {len(events)}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_blocked_outputs(output_dir: Path, config: dict[str, str], reason: str) -> None:
    config_lines = [f"{key}: {value}" for key, value in config.items()]
    config_lines.extend(["status: NEEDS DATA", "blocker: |"])
    config_lines.extend([f"  {line}" for line in reason.splitlines()])
    (output_dir / "config.yaml").write_text(
        "\n".join(config_lines) + "\n",
        encoding="utf-8",
    )
    pd.DataFrame(columns=["event_type", "count", "pct", "correction_count", "cancellation_count", "missing_time_count"]).to_csv(
        output_dir / "event_type_distribution.csv", index=False
    )
    pd.DataFrame(columns=["ticker", "name", "event_count", "event_types", "correction_count", "cancellation_count"]).to_csv(
        output_dir / "ticker_distribution.csv", index=False
    )
    pd.DataFrame(columns=["year", "month", "event_count", "intraday_count", "after_close_count", "missing_time_count"]).to_csv(
        output_dir / "time_distribution.csv", index=False
    )
    sample_columns = ["event_date", "event_time", "session", "ticker", "name", "event_type", "title", "is_correction", "is_cancellation"]
    pd.DataFrame(columns=sample_columns).to_csv(output_dir / "sample_buyback_events.csv", index=False)
    pd.DataFrame(columns=sample_columns).to_csv(output_dir / "sample_dividend_events.csv", index=False)
    (output_dir / "report.md").write_text(
        "\n".join(
            [
                "# R000 OPENDART 이벤트 데이터 감사",
                "",
                "Verdict: NEEDS DATA",
                "",
                "## 결과",
                "",
                "현재 실행 환경에서 OPENDART parquet 파일을 로드하지 못했다.",
                "",
                "## Blocker",
                "",
                reason,
                "",
                "## 평가",
                "",
                "- 데이터 quality: 판정 보류.",
                "- 이벤트 분류 가능 여부: 판정 보류.",
                "- PIT 가능성: 공시일 기반으로 설계 가능하지만 실제 컬럼 검증 전에는 확정 불가.",
                "- R001-R006 진행 정당성: R000 재실행 후 `PASS`가 필요하다.",
                "",
                "## 다음 조치",
                "",
                "parquet 로드 엔진(`pyarrow` 또는 `fastparquet`)이 있는 환경에서 `src/audit/r000_opendart_event_audit.py`를 재실행한다.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_report(
    path: Path,
    df: pd.DataFrame,
    events: pd.DataFrame,
    title_col: str | None,
    ticker_col: str | None,
    name_col: str | None,
    date_col: str | None,
    time_col: str | None,
) -> None:
    missing_time = int((events["_session"] == "missing_time").sum()) if not events.empty else 0
    correction_count = int(events["_is_correction"].sum()) if not events.empty else 0
    cancellation_count = int(events["_is_cancellation"].sum()) if not events.empty else 0
    has_time = time_col is not None and missing_time < len(events)
    verdict = "PASS" if len(events) > 0 and date_col is not None and title_col is not None else "NEEDS DATA"
    if len(events) == 0:
        verdict = "FAIL"
    lines = [
        "# R000 OPENDART 이벤트 데이터 감사",
        "",
        f"Verdict: {verdict}",
        "",
        "## 데이터 구조",
        "",
        f"- 전체 row count: {len(df)}",
        f"- column count: {len(df.columns)}",
        f"- 공시 제목 column: {title_col or 'MISSING'}",
        f"- 종목 코드 column: {ticker_col or 'MISSING'}",
        f"- 종목명 column: {name_col or 'MISSING'}",
        f"- 공시일 column: {date_col or 'MISSING'}",
        f"- 공시 시간 column: {time_col or 'MISSING'}",
        "",
        "## 이벤트 분류",
        "",
        f"- 대상 이벤트 row count: {len(events)}",
        f"- 정정공시 후보 count: {correction_count}",
        f"- 취소공시 후보 count: {cancellation_count}",
        f"- 공시 시간 누락 count: {missing_time}",
        "",
        "## Quality 평가",
        "",
        "- 공시 제목 기반 이벤트 분류는 가능하다." if title_col else "- 공시 제목 column이 없어 이벤트 분류가 불가능하다.",
        "- 공시일 기반 PIT 정렬은 가능하다." if date_col else "- 공시일 column이 없어 PIT 정렬 검증이 불가능하다.",
        "- 공시 시간 기반 장중/장후 구분은 가능하다." if has_time else "- 공시 시간 기반 장중/장후 구분은 현재 데이터/컬럼만으로 제한적이다.",
        "- 정정/취소 공시는 제목 키워드로 1차 flag 처리 가능하다.",
        "",
        "## R001-R006 진행 정당성",
        "",
    ]
    if verdict == "PASS":
        lines.extend(
            [
                "R000은 이벤트 분류와 공시일 기반 PIT audit gate를 통과한다. R001-R006은 각 ticket의 별도 timing test와 execution-date shift를 전제로 진행 가능하다.",
            ]
        )
    elif verdict == "NEEDS DATA":
        lines.extend(
            [
                "핵심 컬럼 일부가 부족하거나 공시 시간 검증이 제한적이다. R001-R006 진행 전 데이터 보강 또는 컬럼 해석 확정이 필요하다.",
            ]
        )
    else:
        lines.extend(["대상 이벤트가 검출되지 않아 R001-R006 진행 근거가 없다."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
