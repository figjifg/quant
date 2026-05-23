# D1 Rate Limit / Retry / Timeout Policy

D1 dry run applied policy:
- Sleep between requests: 0.3 s
- Per-request timeout: 30 s
- Retry on failure: exponential backoff (2^attempt s), max 3 attempts
- Total expected wall time for 50 disclosures (success path): ~ 50 × (0.3 + avg_response) seconds

OPENDART official rate limit (documented):
- Free key default: 10,000 requests / day
- Per-second: not officially documented, conservative 0.3 s sleep applied

Observation in D1:
- See `endpoint_success_rate.md` for actual results.
