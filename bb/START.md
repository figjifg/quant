# Bull/Bear workflow — startup runbook

Version: 2026-05-28. Roles: Referee=Codex (`codex-session`, hub) · Bull=Claude
(`bull-session`, hypotheses) · Bear=Codex (`bear-session`, critique) · Executor=Claude
(`claude-session`, runs approved tests). Transport = file-mode relays.

Recommended: bring up **Bull first**, validate the Referee→Bull→Referee loop, then add Bear.

## Step 1 — launch the agent sessions  (USER does this; needs CLI login/auth)

These are interactive (login + initial prompt), so you run them:

```
# Bull = Claude Code
tmux new-session -d -s bull-session -c /home/jin/code/quant
tmux attach -t bull-session        # then run:  claude   (log in if prompted)
# once Claude is up, paste this one line to prime Bull:
#   Read bb/bull_role_brief.md, bb/CURRENT_HANDOFF.md, bb/bull_comms_protocol.md.
#   That is your role + boundaries + comms. Acknowledge briefly, then wait for relay requests.

# Bear = Codex   (only after Bull loop is validated)
tmux new-session -d -s bear-session -c /home/jin/code/quant
tmux attach -t bear-session        # then run:  codex    (log in if prompted)
# prime Bear:
#   Read bb/bear_role_brief.md, bb/CURRENT_HANDOFF.md, bb/bear_comms_protocol.md.
#   That is your role + boundaries + comms. Acknowledge briefly, then wait for relay requests.
```

## Step 2 — launch the channel relays  (Executor/Claude can do this once sessions exist)

```
# Bull channel (Referee codex-session -> Bull bull-session), file mode
tmux new-session -d -s relay-bull-session -c /home/jin/code/quant \
  '.venv/bin/python codex_claude_referee_relay.py --codex codex-session --claude bull-session \
     --workspace /home/jin/code/quant --ask-mode file --outbox bb/bull_inbox \
     --responder-name bull --io-dir bb'

# Bear channel (after Bull validated)
tmux new-session -d -s relay-bear-session -c /home/jin/code/quant \
  '.venv/bin/python codex_claude_referee_relay.py --codex codex-session --claude bear-session \
     --workspace /home/jin/code/quant --ask-mode file --outbox bb/bear_inbox \
     --responder-name bear --io-dir bb'
```

The existing Executor relay (`relay-session`, codex↔claude, `codex_outbox`) stays as-is.

## Step 3 — prime the Referee with the orchestration protocol  (Executor can do via bridge)

Tell Codex (the Referee) once: read `bb/referee_orchestration_protocol.md` and follow it —
ask Bull by writing `bb/bull_inbox/ask_<seq>.md`; ask Bear via `bb/bear_inbox/ask_<seq>.md`;
synthesize Bull cards + Bear reviews for the user; run tests only via the Executor after
user approval.

## File conventions (per channel)

- Referee → Bull directive: `bb/bull_inbox/ask_<NNNN>.md`  → relay → Bull reads
  `bb/ask_bull_<NN>.md`, writes `bb/bull_reply_<NN>.md` → relay notifies Referee.
- Referee → Bear directive: `bb/bear_inbox/ask_<NNNN>.md`  → relay → Bear reads
  `bb/ask_bear_<NN>.md`, writes `bb/bear_reply_<NN>.md` → relay notifies Referee.
- Each relay dedups by sequence (file-mode) — immune to pane re-render. Multiple relays
  write reply-notifications into the Codex pane; keep an eye that they don't interleave a
  composer mid-type (notifications are short + infrequent, so low risk).

## Boundaries (unchanged)
Frozen P08 off-limits; diagnostic-only; closed families need a NEW mechanism; the user
makes the final call; the Executor runs approved tests; nothing is production/paper.
