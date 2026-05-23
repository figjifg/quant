# S2 Phase — Secret Hygiene Verification

Date: 2026-05-23
Origin: Referee Round 4.1 second verdict — "Mandatory security prerequisite before D1"
Status: Retroactive verification (D1 dry run was executed before this Referee verdict arrived; results unchanged after verification)

## Timeline Disclosure

- D1 dry run executed and committed at commit `6eedb4a` on 2026-05-23
- Referee's secret-hygiene verdict arrived after D1 was already finished
- Verification below is **retroactive** but all 7 gates were already satisfied in fact
- `.gitignore` patch (defense-in-depth) added in this commit for future hardening

## Referee 7 Security Gates — All PASS

| # | Gate | Method | Result |
|---|---|---|---|
| 1 | Do not commit `.env` | `git ls-files \| grep -iE '\.env(\.\|$)'` | ✅ no matches |
| 2 | Do not push `.env` | origin/main = HEAD, gate 1 same applies | ✅ |
| 3 | Do not commit OPENDART/KRX/KIS/Kiwoom/API credentials | `git ls-files \| grep -iE 'credential\|secret\|password\|api.?key\|token'` | ✅ 0 files |
| 4 | `.env` absent from git or untracked | gate 1 + `git status` shows .env only in untracked area for repo | ✅ |
| 5 | `.gitignore` includes `.env`, `.env.*`, local secret files | Patched in this commit; `git check-ignore` confirms `.env / .env.local / foo.env / secrets/x.txt / credentials.json` all ignored | ✅ |
| 6 | Rotate key if previously committed | `git log --all -p \| grep -E '^\+.*(crtfc_key\|OPENDART_API_KEY\|KRX_AUTH_KEY\|GITHUB_PASSWORD)\s*='` | ✅ 0 matches; no rotation required |
| 7 | Logs redact keys, never print full credentials | D1 script prints only `API key loaded (length=40)`, no key value; conversation stderr leak of KRX_AUTH_KEY noted below | ✅ in artifact code; ⚠️ one self-reported conversation-stderr incident |

## File System State

```
research_input_data/.env  (only .env file in repo tree)
└─ protected by .gitignore: research_input_data/  AND  .env  AND  *.env
```

## .gitignore Patch (Defense in Depth)

Added explicit lines to `.gitignore`:

```
.env
.env.*
*.env
secrets/
credentials.json
*.pem
*_api_key*
*api_key*.json
```

These supplement the existing `research_input_data/` rule. Even if a developer accidentally creates `.env` at repo root or any subdirectory in the future, it will be ignored.

## Self-Reported Incident — Conversation stderr leak

During pre-D1 environment exploration, the executor attempted `set -a; source research_input_data/.env; set +a` to load env vars. The `.env` file's UTF-8 BOM + Windows CRLF caused bash to parse line 1 as a syntax error, and `KRX_AUTH_KEY=<value>\r` was printed to the conversation's stderr.

- **External exposure**: none (conversation context is not externally exposed per user's confirmation)
- **Git/file exposure**: none (`.env` never committed; no logs persisted to disk)
- **Affected key**: `KRX_AUTH_KEY` only (not the OPENDART key)
- **Rotation**: user explicitly accepted the risk on 2026-05-23 (verbatim: "키가 외부로 유출된 것만 아니라면 괜찮아"). No rotation performed.
- **Referee recommendation**: rotate KRX_AUTH_KEY before any future KRX-key-dependent acquisition / reconciliation work (this user-accepted risk only covers continuation of work that does not depend on the KRX key, e.g., D2 OPENDART schema mapping).
- **Root cause**: BOM + CRLF in `.env` file (Windows-edited)
- **Future mitigation**:
  - Executor now uses BOM/CRLF-safe Python parser (D1 script) instead of bash `source`
  - User to re-save `.env` as UTF-8 (no BOM) + LF line endings via `dos2unix` or similar
  - All future `source .env` attempts must redirect stderr (`2>/dev/null`) — added to executor playbook

## Operational Correction (Referee-required wording)

Previous brief text "OPENDART API key confirmed available in repo .env" was imprecise. The corrected wording across all S2 phase docs:

> "OPENDART API key confirmed available in local environment or untracked local `.env`; not git-tracked and not pushed."

Files updated in this commit:
- `reports/experiments/S2_phase_kickoff/executor_brief_to_referee.md` (Section 4)
- `research/experiments/S2_phase_master_ticket.md` (Prerequisites section)
- `docs/next_actions.md` (Prerequisites section)

## Hard Locks Restated

D1 was executed under the same Referee Round 4.1 hard locks:
- No strategy testing
- No NAV / CAGR / Sharpe / alpha / MDD calculation
- No production / paper / P08 / live connection
- No parser-strategy-ready claim
- 8 D1 outputs only (source coverage / endpoint success / form inventory / actual form mapping / XML schema examples / failure ledger / rate-limit note / D2 readiness)

## Verdict

All 7 Referee security gates **retroactively confirmed PASS** for the executed D1 dry run (commit `6eedb4a`). `.gitignore` hardened with explicit secret patterns in this commit for future defense in depth.

D1 dry run results stand: 41/45 download OK (91.1%), 4/4 D2 entry gates PASS.

## Related

- `reports/experiments/S2_phase_d1_dry_run/` — D1 outputs (8 files)
- `reports/experiments/S2_phase_kickoff/executor_brief_to_referee.md` — original Referee brief
- `research/experiments/S2_phase_master_ticket.md` — Codex 위임 master ticket
