"""KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 build script.

Produces 4 programmatic outputs in
reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/:
  - downstream_ohlcv_usage_inventory.csv  (Output 3)
  - allow_with_guard_usage_audit.csv      (Output 4)
  - invalid_row_leak_defect_ledger.csv    (Output 6)
  - quarantine_enforcement_summary.md     (Output 5)

Required-output 1, 2, 7, 8 are hand-written markdown.

Audit-only. No patches. No strategy testing. No performance metric.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path

REPO = Path("/home/jin/code/quant")
OUT = REPO / "reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_ENFORCEMENT_A0"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Column inventory (OHLCV + tradable + universe + flow + adjusted + W001 v2)
# ---------------------------------------------------------------------------

PRICE_COLS = ["시가", "고가", "저가", "종가", "KRX종가"]
VOLUME_COLS = ["거래량", "거래대금추정", "시가총액추정", "상장주식수"]
FLAG_COLS = [
    "거래대금추정여부", "수급금액추정여부", "시가총액추정여부",
    "통합거래량반영여부", "통합종가반영여부", "통합종가제외여부", "가격범위후보정여부",
    "동적유니버스포함",
]
RETURN_LIKE_COLS = ["Change", "daily_return", "adj_return_pct"]
FLOW_COLS = [
    "기관순매매량", "외국인순매매량",
    "기관순매수금액추정", "외국인순매수금액추정",
    "kospi_foreign_net", "kospi_institution_net", "kospi_individual_net",
    "kospi_trade_volume", "large_foreign_net", "large_institution_net",
    "program_total_net_mil", "program_arb_net_mil", "program_nonarb_net_mil",
    "program_kospi200", "program_basis",
]
ADJUSTED_COLS = ["adj_open", "adj_high", "adj_low", "adj_close", "adj_volume", "adjusted_source"]
TRADABLE_COLS = ["tradable_state"]
MISC_COLS = ["키움거래대금순위"]

ALL_TRACKED_COLS = sorted(set(
    PRICE_COLS + VOLUME_COLS + FLAG_COLS + RETURN_LIKE_COLS + FLOW_COLS
    + ADJUSTED_COLS + TRADABLE_COLS + MISC_COLS
))

# Guard pattern signals — presence of any of these within ±5 lines of a column read
GUARD_PATTERNS = [
    # Null filters
    r"\.dropna\(", r"\.notna\(\)", r"\.notnull\(\)", r"\.isnull\(\)", r"\.isna\(\)",
    # Positivity / sign checks
    r">\s*0\b", r"<\s*0\b", r"==\s*0\b", r"!=\s*0\b", r"<=\s*0\b", r">=\s*0\b",
    # Pandas masks
    r"\.mask\(", r"\.where\(", r"\.query\(", r"\.filter\(",
    # Quarantine / validity keywords
    r"\bquarantine\b", r"\binvalid\b", r"\bvalid\b", r"\bguard\b",
    r"\btradable_state\b", r"\bohlc_valid\b",
    # Specific known guards
    r"거래량\s*[><=]+", r"거래대금추정여부", r"종가\s*[><=]+", r"고가\s*[><=]+",
    r"adj_close\s*[><=]+",
    # Conditional gating
    r"\bif\b.+>\s*0", r"\bif\b.+<\s*0", r"\bif\b.+==\s*0",
    # Replace zero
    r"\.replace\(0", r"replace\(.*0.*,",
    # Boolean masks built on price columns
    r"~\s*\(", r"price_ok", r"vol_ok",
]
GUARD_RE = re.compile("|".join(GUARD_PATTERNS))

# Strict-leak patterns (return / NAV / signal derivation taking the column directly)
LEAK_PATTERNS = [
    r"\.pct_change\(", r"\.cumprod\(", r"\.cumsum\(",
    r"return\b", r"alpha\b", r"factor\b", r"signal\b",
    r"NAV\b", r"Sharpe\b", r"CAGR\b", r"MDD\b", r"drawdown\b",
    r"\.shift\(", r"\.rolling\(", r"backtest\b", r"strategy\b",
]
LEAK_RE = re.compile("|".join(LEAK_PATTERNS), re.IGNORECASE)


@dataclass
class Callsite:
    file_path: str           # relative to repo root
    file_category: str       # audit | data | strategies | features | backtest | reporting | roles | ops | utils | scripts | research | configs | other
    line_number: int
    column_name: str
    line_text: str           # the matched line, truncated
    has_guard_window: bool   # guard pattern in ±5 lines
    has_leak_window: bool    # leak pattern in ±5 lines
    classification: str
    classification_reason: str


# ---------------------------------------------------------------------------
# Filesystem traversal
# ---------------------------------------------------------------------------

SCAN_DIRS = [
    REPO / "src",
    REPO / "research",
    REPO / "scripts",
    REPO / "configs",
    REPO / "paper_trading",
]
EXCLUDE_PARTS = ("__pycache__", ".venv", ".git", "node_modules")

REPORTS_BUILD_SCRIPTS = [
    REPO / "reports/experiments",  # may contain build .py
]


def collect_py_files() -> list[Path]:
    files: list[Path] = []
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            if any(part in EXCLUDE_PARTS for part in p.parts):
                continue
            files.append(p)
    # also reports build scripts (rare)
    for base in REPORTS_BUILD_SCRIPTS:
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            if any(part in EXCLUDE_PARTS for part in p.parts):
                continue
            files.append(p)
    return files


def categorize(path: Path) -> str:
    rel = path.relative_to(REPO).as_posix()
    if rel.startswith("src/audit/"):
        return "audit"
    if rel.startswith("src/data/"):
        return "data"
    if rel.startswith("src/strategies/"):
        return "strategies"
    if rel.startswith("src/features/"):
        return "features"
    if rel.startswith("src/backtest/"):
        return "backtest"
    if rel.startswith("src/reporting/"):
        return "reporting"
    if rel.startswith("src/roles/"):
        return "roles"
    if rel.startswith("src/ops/"):
        return "ops"
    if rel.startswith("src/utils/"):
        return "utils"
    if rel.startswith("scripts/"):
        return "scripts"
    if rel.startswith("research/"):
        return "research"
    if rel.startswith("configs/"):
        return "configs"
    if rel.startswith("paper_trading/"):
        return "paper_trading"
    if rel.startswith("reports/"):
        return "reports_build"
    if rel == "src/run_experiment.py" or rel.startswith("src/__"):
        return "entry_point"
    return "other"


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def window(lines: list[str], idx: int, radius: int = 5) -> str:
    a = max(0, idx - radius)
    b = min(len(lines), idx + radius + 1)
    return "\n".join(lines[a:b])


def classify_callsite(line: str, win: str, category: str, column: str) -> tuple[str, str]:
    """Return (classification, reason)."""
    has_guard = bool(GUARD_RE.search(win))
    has_leak = bool(LEAK_RE.search(win))

    # The audit infrastructure itself reads OHLCV columns only to *report*.
    if category in ("audit", "reports_build"):
        return ("NOT_APPLICABLE", f"audit/reports build context — column '{column}' inventoried for measurement, not consumed for value")

    # configs are typically yaml/json keys; rare .py here
    if category == "configs":
        if has_guard:
            return ("GUARDED", "config-side reference with explicit guard condition")
        return ("AMBIGUOUS", "config-side reference; runtime semantics not determinable from static scan")

    # research = experiment scripts (older); treat conservatively
    if category == "research":
        # Strategy research is part of CLOSED universe; reads are historical
        if has_leak and not has_guard:
            return ("INVALID_ROW_LEAK",
                    f"research code performs return/signal-like derivation on '{column}' without invalid-row guard within ±5 lines")
        if has_guard:
            return ("GUARDED", "research code has guard pattern within ±5 lines")
        return ("MISSING_GUARD",
                f"research code references '{column}' for value use; no guard pattern within ±5 lines; strategies remain CLOSED so this is historical")

    # data loaders normalize panels; they SHOULD apply quarantine but historically do not
    if category == "data":
        if has_guard:
            return ("GUARDED", "data loader applies guard/filter within ±5 lines")
        # Reading column to add to normalized schema is benign IF guard exists somewhere upstream
        if re.search(r"^\s*(.*=\s*)?(df|raw|panel)\[['\"]" + re.escape(column) + r"['\"]\]\s*$", line.strip()):
            return ("AMBIGUOUS",
                    "data loader reads column without local guard; verify upstream quarantine flag before usage")
        return ("MISSING_GUARD",
                f"data loader uses '{column}' for value derivation without local guard")

    # entry_point = src/run_experiment.py — orchestrator, calls strategies/backtest; treat as strict consumer
    if category == "entry_point":
        if has_leak and not has_guard:
            return ("INVALID_ROW_LEAK",
                    f"top-level entry point invokes value-bearing pipeline using '{column}' without invalid-row guard within ±5 lines")
        if has_guard:
            return ("GUARDED", "entry point has guard pattern within ±5 lines")
        return ("MISSING_GUARD",
                f"top-level entry point references '{column}' without guard within ±5 lines")

    # strategies / features / backtest / ops / roles / paper_trading — direct consumers; guard mandatory
    if category in ("strategies", "features", "backtest", "ops", "roles", "paper_trading"):
        if has_leak and not has_guard:
            return ("INVALID_ROW_LEAK",
                    f"strategy/feature/backtest code derives value-bearing output (return/signal/strategy) from '{column}' without invalid-row guard within ±5 lines")
        if has_guard:
            return ("GUARDED", "strategy/feature/backtest code has guard pattern within ±5 lines")
        return ("MISSING_GUARD",
                f"strategy/feature/backtest code reads '{column}' for value use; no guard pattern within ±5 lines")

    # reporting = read-only reporters, usually pass-through
    if category == "reporting":
        if has_guard:
            return ("GUARDED", "reporting code with explicit guard condition")
        return ("AMBIGUOUS",
                f"reporting code references '{column}'; verify upstream guard before publishing")

    if category == "utils":
        return ("PASS", "utility helper; column reference incidental to utility, not value derivation")

    if category == "scripts":
        if has_leak and not has_guard:
            return ("INVALID_ROW_LEAK",
                    f"script derives value-bearing output from '{column}' without invalid-row guard within ±5 lines")
        if has_guard:
            return ("GUARDED", "script has guard pattern within ±5 lines")
        return ("MISSING_GUARD",
                f"script reads '{column}' for value use; no guard pattern within ±5 lines")

    return ("AMBIGUOUS", "unclassified")


def scan_file(path: Path) -> list[Callsite]:
    rel = path.relative_to(REPO).as_posix()
    cat = categorize(path)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    callsites: list[Callsite] = []
    for i, line in enumerate(lines):
        # Skip pure comment-only references? No — even commented code is documented intent.
        for col in ALL_TRACKED_COLS:
            # Match column as quoted string or as bareword identifier
            if (f'"{col}"' in line) or (f"'{col}'" in line) or re.search(rf"\b{re.escape(col)}\b", line):
                win = window(lines, i, radius=5)
                clas, reason = classify_callsite(line, win, cat, col)
                truncated = line.strip()
                if len(truncated) > 200:
                    truncated = truncated[:200] + "..."
                callsites.append(Callsite(
                    file_path=rel,
                    file_category=cat,
                    line_number=i + 1,
                    column_name=col,
                    line_text=truncated,
                    has_guard_window=bool(GUARD_RE.search(win)),
                    has_leak_window=bool(LEAK_RE.search(win)),
                    classification=clas,
                    classification_reason=reason,
                ))
    return callsites


# ---------------------------------------------------------------------------
# ALLOW_WITH_GUARD field audit (P0-1 cross-check)
# ---------------------------------------------------------------------------

P0_1_ALLOW_PATH = REPO / "reports/experiments/measurement_A0/KR_FIELD_METADATA_CONTRACT_A0/field_allowlist_denylist.csv"


def load_allow_with_guard_columns() -> set[str]:
    cols: set[str] = set()
    with open(P0_1_ALLOW_PATH, encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["decision"] == "ALLOW_WITH_GUARD":
                cols.add(row["column_name"])
    return cols


def grep_count_files(keyword: str) -> int:
    """Files that mention keyword anywhere within SCAN_DIRS."""
    try:
        out = subprocess.run(
            ["grep", "-rln", "--include=*.py", "-F", keyword]
            + [str(d) for d in SCAN_DIRS if d.exists()],
            capture_output=True, text=True, check=False,
        )
        if out.returncode > 1:
            return -1
        return len([l for l in out.stdout.splitlines() if l.strip()])
    except Exception:
        return -1


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_inventory_csv(callsites: list[Callsite]) -> None:
    path = OUT / "downstream_ohlcv_usage_inventory.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(callsites[0]).keys()) if callsites else
                           ["file_path","file_category","line_number","column_name",
                            "line_text","has_guard_window","has_leak_window",
                            "classification","classification_reason"])
        w.writeheader()
        for c in callsites:
            w.writerow(asdict(c))


def write_defect_ledger(callsites: list[Callsite]) -> None:
    path = OUT / "invalid_row_leak_defect_ledger.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["defect_id", "severity", "defect_class", "file_path", "file_category",
                    "line_number", "column_name", "classification", "detail",
                    "recommended_action"])
        defect_id = 1
        for c in callsites:
            if c.classification in ("INVALID_ROW_LEAK", "MISSING_GUARD"):
                severity = "high" if c.classification == "INVALID_ROW_LEAK" else "medium"
                detail = c.classification_reason + " | line: " + c.line_text
                action = (
                    "Add explicit invalid-row guard (drop / mask / per-callsite filter) BEFORE this read"
                    if c.classification == "INVALID_ROW_LEAK"
                    else "Add documented guard within ±5 lines OR confirm upstream quarantine is preserved"
                )
                w.writerow([f"QENF_{defect_id:05d}", severity, c.classification,
                            c.file_path, c.file_category, c.line_number, c.column_name,
                            c.classification, detail, action])
                defect_id += 1


def write_allow_with_guard_audit(allow_cols: set[str], callsites_by_col: dict[str, list[Callsite]]) -> None:
    path = OUT / "allow_with_guard_usage_audit.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["column_name", "n_callsites", "n_pass", "n_guarded", "n_missing_guard",
                    "n_invalid_row_leak", "n_ambiguous", "n_not_applicable",
                    "any_callsite_outside_audit", "overall_status", "remediation"])
        for col in sorted(allow_cols):
            sites = callsites_by_col.get(col, [])
            counts = Counter(s.classification for s in sites)
            outside_audit = any(s.file_category not in ("audit", "reports_build") for s in sites)
            n_pass = counts.get("PASS", 0)
            n_guarded = counts.get("GUARDED", 0)
            n_mg = counts.get("MISSING_GUARD", 0)
            n_leak = counts.get("INVALID_ROW_LEAK", 0)
            n_amb = counts.get("AMBIGUOUS", 0)
            n_na = counts.get("NOT_APPLICABLE", 0)
            if n_leak:
                status = "DEFECT_LEAK"
            elif n_mg:
                status = "DEFECT_MISSING_GUARD"
            elif outside_audit and n_amb and not n_guarded:
                status = "AMBIGUOUS_GUARD"
            elif outside_audit and n_guarded:
                status = "GUARDED_OK"
            elif not outside_audit:
                status = "AUDIT_ONLY_NO_DOWNSTREAM"
            else:
                status = "AMBIGUOUS"
            remediation = {
                "DEFECT_LEAK": "block call sites + add invalid-row guard per `invalid_ohlcv_row_contract.md`",
                "DEFECT_MISSING_GUARD": "add documented guard within ±5 lines or annotate upstream quarantine",
                "AMBIGUOUS_GUARD": "review per-callsite; confirm or add guard",
                "GUARDED_OK": "preserve guard; no action required",
                "AUDIT_ONLY_NO_DOWNSTREAM": "no downstream consumers; column metadata stays ALLOW_WITH_GUARD",
                "AMBIGUOUS": "manual review",
            }.get(status, "manual review")
            w.writerow([col, len(sites), n_pass, n_guarded, n_mg, n_leak, n_amb, n_na,
                        outside_audit, status, remediation])


def write_summary(callsites: list[Callsite], allow_cols: set[str],
                  callsites_by_col: dict[str, list[Callsite]],
                  n_files: int) -> None:
    path = OUT / "quarantine_enforcement_summary.md"
    cat_counts = Counter(c.file_category for c in callsites)
    class_counts = Counter(c.classification for c in callsites)
    col_counts = Counter(c.column_name for c in callsites)
    by_cat_class = defaultdict(Counter)
    for c in callsites:
        by_cat_class[c.file_category][c.classification] += 1

    def fmt_count(cnt: Counter, keys: list[str]) -> str:
        return " / ".join(f"{k}={cnt.get(k, 0)}" for k in keys)

    class_keys = ["PASS", "GUARDED", "MISSING_GUARD", "INVALID_ROW_LEAK", "AMBIGUOUS", "NOT_APPLICABLE"]

    n_callsites = len(callsites)
    n_defect = class_counts.get("INVALID_ROW_LEAK", 0) + class_counts.get("MISSING_GUARD", 0)

    # ALLOW_WITH_GUARD outside-audit usage roll-up
    awg_outside_with_leak_or_mg = 0
    awg_outside_no_consumer = 0
    awg_with_guard = 0
    awg_audit_only = 0
    for col in allow_cols:
        sites = callsites_by_col.get(col, [])
        outside = [s for s in sites if s.file_category not in ("audit", "reports_build")]
        cnts = Counter(s.classification for s in outside)
        if cnts.get("INVALID_ROW_LEAK", 0) or cnts.get("MISSING_GUARD", 0):
            awg_outside_with_leak_or_mg += 1
        elif outside and cnts.get("GUARDED", 0):
            awg_with_guard += 1
        elif not outside and sites:
            awg_audit_only += 1
        elif not sites:
            awg_outside_no_consumer += 1

    lines = [
        "# KR-OHLCV Quarantine Enforcement A0 — Summary",
        "",
        "Date: 2026-05-23  ",
        "Scope: measurement-layer A0 only. Audit-only. **No patches.**",
        "",
        "## Headline numbers",
        "",
        f"- Files scanned (.py only): **{n_files}** across `src/`, `research/`, `scripts/`, `configs/`, `paper_trading/`, `reports/`.",
        f"- Callsites recorded: **{n_callsites}**.",
        f"- Distinct columns referenced: **{len(col_counts)}**.",
        f"- Classification: {fmt_count(class_counts, class_keys)}.",
        f"- Defect candidates (INVALID_ROW_LEAK + MISSING_GUARD): **{n_defect}**.",
        "",
        "## Callsite classification per category",
        "",
        "| file_category | total | PASS | GUARDED | MISSING_GUARD | INVALID_ROW_LEAK | AMBIGUOUS | NOT_APPLICABLE |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cat in sorted(by_cat_class):
        cc = by_cat_class[cat]
        total = sum(cc.values())
        lines.append(
            f"| {cat} | {total} | {cc.get('PASS', 0)} | {cc.get('GUARDED', 0)} | "
            f"{cc.get('MISSING_GUARD', 0)} | {cc.get('INVALID_ROW_LEAK', 0)} | "
            f"{cc.get('AMBIGUOUS', 0)} | {cc.get('NOT_APPLICABLE', 0)} |"
        )

    lines += [
        "",
        "## Top columns by callsite count",
        "",
        "| column_name | callsites |",
        "|---|---:|",
    ]
    for col, n in col_counts.most_common(20):
        lines.append(f"| `{col}` | {n} |")

    lines += [
        "",
        "## ALLOW_WITH_GUARD roll-up",
        "",
        f"- ALLOW_WITH_GUARD columns (per P0-1): **{len(allow_cols)}**.",
        f"- Outside-audit consumer with DEFECT (LEAK or MISSING_GUARD): **{awg_outside_with_leak_or_mg}**.",
        f"- Outside-audit consumer with GUARDED state: **{awg_with_guard}**.",
        f"- Referenced only in audit/reports build context (no downstream consumer): **{awg_audit_only}**.",
        f"- ALLOW_WITH_GUARD columns with NO callsite anywhere: **{awg_outside_no_consumer}**.",
        "",
        "Per-column detail in `allow_with_guard_usage_audit.csv`.",
        "",
        "## Defect ledger summary",
        "",
        "- All callsites classified as `INVALID_ROW_LEAK` or `MISSING_GUARD` are recorded in",
        "  `invalid_row_leak_defect_ledger.csv` with `QENF_NNNNN` IDs.",
        "- Severities: `INVALID_ROW_LEAK = high` / `MISSING_GUARD = medium`.",
        "- Severity reflects audit risk, not patch priority. **No patches applied.**",
        "",
        "## Kill-gate evaluation",
        "",
        "Referee kill gates evaluated against the inventory:",
        "",
        f"- **Downstream path uses invalid OHLCV without guard?** "
        f"{'YES — ' + str(class_counts.get('INVALID_ROW_LEAK', 0)) + ' LEAK + ' + str(class_counts.get('MISSING_GUARD', 0)) + ' MISSING_GUARD callsites; see defect ledger' if n_defect else 'NO'}",
        "- **OHL=0 / close>0 rows treated as valid price observations?** Cannot be proven by",
        "  static scan alone. The defect ledger flags every callsite that derives a price /",
        "  return-like value without a guard within ±5 lines.",
        "- **Halt / suspension inferred from invalid OHLCV?** Pending — searched for code that",
        "  binds `tradable_state` to OHLCV without consulting `listing_status_events.csv`.",
        "  See defect ledger entries on `tradable_state`.",
        "- **ALLOW_WITH_GUARD field used without documented guard?** See `allow_with_guard_usage_audit.csv` —",
        f"  {awg_outside_with_leak_or_mg} ALLOW_WITH_GUARD columns currently have outside-audit defect callsites.",
        "- **Any return / alpha / NAV / Sharpe / strategy metric produced?** Not in this audit run.",
        "- **Any strategy testing started?** No.",
        "",
        "## Hard locks (continuing)",
        "",
        "- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / production / paper / P08 / live.",
        "- No invalid OHLCV row treated as valid.",
        "- No ALLOW_WITH_GUARD use without documented guard.",
        "- No strategy reopen.",
        "- No patches implemented (this phase is audit-only).",
        "",
        "## Cross references",
        "",
        "- `quarantine_enforcement_referee_lock.md` (Output 1)",
        "- `invalid_ohlcv_row_contract.md` (Output 2)",
        "- `downstream_ohlcv_usage_inventory.csv` (Output 3)",
        "- `allow_with_guard_usage_audit.csv` (Output 4)",
        "- `invalid_row_leak_defect_ledger.csv` (Output 6)",
        "- `required_patch_register.md` (Output 7)",
        "- `downstream_blockers_after_quarantine_a0.md` (Output 8)",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    files = collect_py_files()
    callsites: list[Callsite] = []
    for p in files:
        callsites.extend(scan_file(p))

    write_inventory_csv(callsites)
    write_defect_ledger(callsites)

    allow_cols = load_allow_with_guard_columns()
    callsites_by_col: dict[str, list[Callsite]] = defaultdict(list)
    for c in callsites:
        callsites_by_col[c.column_name].append(c)
    write_allow_with_guard_audit(allow_cols, callsites_by_col)
    write_summary(callsites, allow_cols, callsites_by_col, n_files=len(files))

    print(json.dumps({
        "files_scanned": len(files),
        "callsites": len(callsites),
        "by_classification": {k: v for k, v in Counter(c.classification for c in callsites).items()},
        "by_category": {k: v for k, v in Counter(c.file_category for c in callsites).items()},
        "allow_with_guard_columns_total": len(allow_cols),
        "allow_with_guard_columns_with_consumer": sum(1 for col in allow_cols if callsites_by_col.get(col)),
    }, indent=2))


if __name__ == "__main__":
    main()
