# E000 Codex Questions

- KIS API 호출이 HTTP status 없이 실패했습니다. 첫 실제 실행에서 `000020`, `000030`, `000040`, `000050`, `000070` 등이 모두 `fetch_status=fail`, `http_status_code=None`으로 반환되었습니다.
- 현재 Codex 실행 샌드박스가 outbound network 제한 상태라 KIS endpoint에 연결하지 못하는 것으로 보입니다.
- credential 값은 출력하거나 저장하지 않았습니다.
- 동일 스크립트를 네트워크 접근 가능한 로컬 터미널에서 실행하거나, Codex 세션에 KIS endpoint outbound 접근이 가능한 환경을 제공해 주세요.

실행 준비는 완료되어 있습니다.

```bash
.venv/bin/python scripts/fetch_kis_sector_snapshot.py
```

dry-run 기준 `동적유니버스포함=True` unique 종목 수는 923개입니다.
