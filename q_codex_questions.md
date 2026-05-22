# Q001 Codex Questions

## Blocker

Q001 신규 SEC EDGAR 다운로드가 현재 Codex 실행 환경에서 실패했습니다.

- Command: `python3 -m src.audit.q001_universe_construction`
- User-Agent: `claude-code-q001 <q001@example.com>`
- Rate limit: 0.15초/request
- Failure: `SEC request failed: [Errno -3] Temporary failure in name resolution`
- Impact: 기존 Q000 10종목 파일은 audit 가능하지만, 신규 90개 ticker의 `companyfacts` JSON 다운로드와 sector audit은 완료되지 않았습니다.

## Needed Action

DNS/network가 열려 있는 host에서 아래 명령을 재실행해야 합니다.

```bash
python3 -m src.audit.q001_universe_construction
```

성공 조건은 `reports/experiments/Q001_universe_construction/universe_list.csv`에서 `download_status`가 `existing` 또는 `downloaded`인 ticker가 90% 이상이고, `coverage_matrix.csv`가 90개 이상 종목을 포함하는 것입니다.

## Research Risk Note

Q001의 현재 hard-coded large-cap ticker list는 survivorship-free universe가 아닙니다. 성공적으로 다운로드되더라도 historical Q-family backtest의 production 판단에는 별도 survivorship-free membership, delisting, ticker-change 처리가 필요합니다.
