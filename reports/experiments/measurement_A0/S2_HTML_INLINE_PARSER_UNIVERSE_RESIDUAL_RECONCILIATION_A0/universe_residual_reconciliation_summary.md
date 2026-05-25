# Universe Residual Reconciliation — Summary

Date: 2026-05-26
Phase: S2-HTML-INLINE-PARSER-UNIVERSE-RESIDUAL-RECONCILIATION-A0
Parser: `krx_status_html_inline-1.1.0` (used as-is).

## In-scope universe: **12187** rows (suspension_related + resumption_related)

## Reconciled body-format distribution (cached rows)

| body_format | count |
|---|---:|
| `html_inline` | 12145 |
| `zip_unparseable` | 42 |

## Reconciled parse_status distribution (all in-scope rows)

| parse_status | count |
|---|---:|
| `extracted` | 11434 |
| `no_label_match` | 511 |
| `label_no_value` | 200 |
| `body_unavailable` | 42 |

## Usable vs residual

- Usable html_inline bodies: **12145**
- Universe-level residual (not usable html_inline): **42**

## Residual class counts

| residual_class | count |
|---|---:|
| `zip_unparseable` | 42 |

Residual subtotal = 42; usable = 12145; sum = 12187 = universe 12187. ✓
