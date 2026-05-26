# Relay file ask-mode — robust Codex→Claude directive transport

Prepared 2026-05-26 (code committed; **NOT yet deployed** — switch at a clean moment per
the steps below). Fixes the root cause of duplicate / replayed relay directives.

## The problem it fixes

`codex_claude_referee_relay.py` transports directives **Codex (Referee) → Claude**. The
legacy detection ("pane" mode) **screen-scrapes the Codex tmux pane** (`capture_pane` +
`extract_blocks`) and dedups by content hash (`seen_asks`). That hash is computed from
**rendered terminal text**, so when the same directive is re-rendered with different line
wrapping / whitespace — on a terminal **resize**, a scroll, or especially **`codex resume`**
(which re-paints the whole transcript) — its hash changes and the **same directive is
re-forwarded as new**. This caused the duplicate re-sends (relay 28/34/39/44) and the
post-`codex resume` replay loop (relay 46–49). (The Claude→Codex reply side was already
file-based — `claude_reply_NN.md` — and was never affected.)

## What changed (backward compatible)

`--ask-mode {pane,file}` was added, **default `pane`** (legacy behavior unchanged, so the
currently-running relay is unaffected until restarted with the new flag):

- **`pane`** (default): the old screen-scrape detection. Fragile, as above.
- **`file`** (recommended): the relay watches an **outbox directory**
  (`<relay_dir>/codex_outbox/` by default, override with `--outbox`) for
  monotonically-numbered directive files `ask_<seq>.md` and processes any with
  `seq > last_seen`. Dedup is by **sequence number**, computed from **exact file bytes** —
  immune to pane re-render / resize / `codex resume` / partial capture. A re-painted pane
  cannot create a new outbox file, so nothing is ever re-forwarded.

The reply path (`claude_reply_NN.md`) and the relay→Codex notification (a one-line pane
paste telling the Referee "reply ready at …") are **unchanged** — neither was a source of
duplicates.

## How to switch (two coordinated steps — do at a clean moment, no directive in flight)

**Step 1 — restart the relay in file mode.** Stop the current relay, then:

```
python3 codex_claude_referee_relay.py \
    --codex codex-session --claude claude-session \
    --workspace . --ask-mode file
```

(Use the same `--codex` / `--claude` tmux targets as now. The relay creates
`.codex-claude-relay/codex_outbox/` and baselines to the highest existing `ask_<seq>.md`
so old files are not reprocessed.)

**Step 2 — tell the Referee (Codex) the new protocol.** Give the Referee this instruction
(once):

> From now on, do NOT emit `<<<ASK_CLAUDE_START>>> … <<<ASK_CLAUDE_END>>>` blocks in your
> terminal. Instead, when you want to send Claude a directive, WRITE the full directive
> (plain text, any length, no markers) to the next sequential file
> `.codex-claude-relay/codex_outbox/ask_<NNNN>.md`, where `<NNNN>` is one greater than the
> highest existing `ask_*.md` in that folder (zero-padded, e.g. `ask_0001.md`,
> `ask_0002.md`, …). Write the whole directive in a single save. The relay watches that
> folder and will forward each new file to Claude exactly once. Claude's reply still comes
> back as `claude_reply_NN.md`, which the relay points you to as before.

That's it — after both steps, pane re-renders / `codex resume` can no longer cause
duplicate or replayed directives.

## Notes

- Backward compatible: omitting `--ask-mode` keeps the legacy pane behavior, so this change
  is safe to land without forcing the switch.
- `read_stable_file` guards against reading a directive mid-write (size-stable across two
  polls).
- If a directive file is malformed/empty it is skipped (size 0 → not processed) and retried
  next tick.
- This does not change the Claude side at all (Claude keeps reading `ask_claude_NN.md` and
  writing `claude_reply_NN.md`).
