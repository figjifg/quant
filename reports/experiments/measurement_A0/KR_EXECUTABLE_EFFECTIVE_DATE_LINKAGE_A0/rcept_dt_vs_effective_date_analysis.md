# rcept_dt vs effective_date Analysis

Date: 2026-05-25  
Phase: KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0

## Headline

- Samples audited: **113**
- Effective date extracted (any confidence): **2**
- Extraction rate: **1.8%**

## Relation distribution

| relation | count |
|---|---:|
| `effective_date_unknown` | 111 |
| `effective_date_after_rcept_dt` | 1 |
| `effective_date_unparseable` | 1 |

## Interpretation

- `effective_date_equal_rcept_dt`: rcept_dt == extracted effective date.
  Approximating rcept_dt as effective would be safe HERE — but only for the
  audited sample, NOT generalisable.
- `effective_date_after_rcept_dt`: most common pattern for suspension /
  delisting events (filing precedes the action). Using rcept_dt would
  fire the event a day or more EARLY in any future execution simulation.
- `effective_date_before_rcept_dt`: filed AFTER the event already took
  effect (rare, but observed in correction-replacement chains).
- `effective_date_unknown`: regex / body extraction failed. Conservative
  rule MUST treat these as unknown — not as `rcept_dt` fallback.
- `effective_date_unparseable`: regex matched but format could not be parsed.

## Critical finding

Even when an effective date IS extracted, it is NOT always equal to
rcept_dt. The conservative future linkage rule must:

- use the explicit body / title effective date when extractable,
- mark `effective_date_unknown` rows as untrusted (fail-closed),
- NOT fall back to rcept_dt by default,
- treat correction-flagged rows as superseding prior events.

## Hard locks (preserved)

- No `rcept_dt` treated as effective status date by default.
- No panel / OHLCV used as effective-date proof.
- No execution simulation.
