from __future__ import annotations

from pathlib import Path

from src.ops.nav_update import ROOT

OUTPUT_DIR = ROOT / "paper_trading/operations"


def generate_quarterly_evaluation(quarter: str, output_path: str | Path | None = None) -> Path:
    """Generate the O005 quarterly evaluation markdown template."""

    text = f"""# {quarter} Global Allocation Paper Evaluation

Tax professional confirmation is required before any live implementation.

## 성과

| version | quarter_return | ytd_return | mdd | rolling_vol | rolling_sharpe |
| --- | ---: | ---: | ---: | ---: | ---: |
| Gross P08_IEF30 | TBD | TBD | TBD | TBD | TBD |
| V1 taxable P08_IEF30 | TBD | TBD | TBD | TBD | TBD |
| MIX1 practical shadow | TBD | TBD | TBD | TBD | TBD |
| V4 pension-only shadow | TBD | TBD | TBD | TBD | TBD |

## 세금

| item | quarter | ytd |
| --- | ---: | ---: |
| realized gain/loss | TBD | TBD |
| used 2.5M exemption | TBD | TBD |
| remaining 2.5M exemption | TBD | TBD |
| estimated capital gains tax | TBD | TBD |
| dividend withholding | TBD | TBD |

## 리밸런싱

| ticker | action | amount_krw | quantity | slippage_bps | note |
| --- | --- | ---: | ---: | ---: | --- |
| SPY | TBD | TBD | TBD | TBD | HIFO lot check required |
| QQQ | TBD | TBD | TBD | TBD | HIFO lot check required |
| H001 | TBD | TBD | TBD | TBD | Korean sleeve |
| IEF | TBD | TBD | TBD | TBD | HIFO lot check required |

## Tracking Error

| item | model | actual | difference |
| --- | ---: | ---: | ---: |
| NAV | TBD | TBD | TBD |
| FX | TBD | TBD | TBD |
| tax | TBD | TBD | TBD |

## 실제 vs paper

- Actual deployment status: paper only until separately authorized.
- Paper tracking versions: Gross / V1 taxable / MIX1 practical / V4 pension-only shadow.

## 주요 이벤트

- Market events: TBD.
- Tax/account events: TBD.
- Data issues: TBD.

## 다음 분기 액션

- Refresh O000 daily NAV.
- Refresh O001 four-version NAV comparison.
- Refresh O002 tax ledger.
- Generate O003 rebalance report.
- Review O004 drift/risk alerts.
- Confirm tax assumptions with a qualified tax professional before live action.
"""
    path = Path(output_path) if output_path else OUTPUT_DIR / f"evaluations_template_{quarter}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


if __name__ == "__main__":
    print(generate_quarterly_evaluation("2026-Q2").relative_to(ROOT))
