#!/usr/bin/env python3
"""Claude -> Codex bridge (Claude-initiated direction).

Lets Claude push a message INTO the Codex (Referee) tmux pane and read Codex's
reply back. This is the complement to codex_claude_referee_relay.py: the relay
handles Codex-initiated ASK_CLAUDE directives; this handles Claude-initiated
messages (e.g. the human, on mobile, talks only to Claude and wants Claude to
relay to/from Codex).

Codex keeps terminal scrollback, so capture-pane can read its reply reliably
(unlike Claude Code's alt-screen). "Done" = pane output unchanged for --idle-secs
and the idle footer is visible.

Usage:
  claude_to_codex_bridge.py --message-file MSG.txt [--codex codex-session]
      [--submit-delay 0.5] [--idle-secs 8] [--timeout 300] [--history-lines 3000]

Prints Codex's reply (the new content after the sent message) to stdout.
"""
from __future__ import annotations

import argparse
import re
import secrets
import subprocess
import sys
import time
from pathlib import Path

# Reuse the hardened tmux helpers + gutter normalizer from the relay.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from codex_claude_referee_relay import (  # noqa: E402
    capture_pane,
    normalize_pane_text,
    require_tmux_target,
    sh,
)

# Codex idle footer signature (model line shown when ready for input).
IDLE_FOOTER_RE = re.compile(r"(gpt-[\w.]+|~/code/quant|·)")


def send_message(target: str, text: str, buffer_name: str, submit_delay: float) -> None:
    one_line = " ".join(text.strip().splitlines())
    sh(["tmux", "load-buffer", "-b", buffer_name, "-"], input_text=one_line)
    sh(["tmux", "paste-buffer", "-t", target, "-b", buffer_name])
    time.sleep(submit_delay)
    sh(["tmux", "send-keys", "-t", target, "Enter"])
    sh(["tmux", "delete-buffer", "-b", buffer_name], check=False)


def wait_until_idle(target: str, history_lines: int, idle_secs: float,
                    timeout_s: float, poll_s: float = 2.0) -> str:
    """Poll the Codex pane until output is unchanged for idle_secs, then return
    the final capture. Bounded by timeout_s."""
    deadline = time.time() + timeout_s
    last_text = None
    last_change = time.time()
    while time.time() < deadline:
        text = capture_pane(target, history_lines)
        if text != last_text:
            last_text = text
            last_change = time.time()
        elif time.time() - last_change >= idle_secs:
            return text
        time.sleep(poll_s)
    return last_text or ""


def extract_reply(final_text: str, end_token: str) -> str:
    """Return the pane content AFTER the message's end sentinel, trimmed of the
    trailing idle composer/footer lines. Anchoring on a unique sentinel appended
    to the sent message makes this robust to how Codex wraps the echoed message."""
    lines = final_text.splitlines()
    cut = 0
    for i, ln in enumerate(lines):  # FIRST occurrence = end of my echoed message
        if end_token in ln:
            cut = i + 1
            break
    reply_lines = lines[cut:]
    # Trim trailing idle footer, composer prompt (›), separators, blanks.
    while reply_lines:
        tail = reply_lines[-1].strip()
        is_composer = tail.startswith("›")  # Codex input line; response bullets use •
        is_footer = bool(IDLE_FOOTER_RE.search(tail)) and ("~/code/quant" in tail or tail.startswith("gpt-"))
        is_sep = bool(tail) and set(tail) <= set("─-—")
        if (not tail) or is_composer or is_footer or is_sep:
            reply_lines.pop()
        else:
            break
    # Strip leading prompt gutters left on each kept line.
    cleaned = [re.sub(r"^[ \t]*[›•]\s?", "", ln) for ln in reply_lines]
    return "\n".join(cleaned).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Push a message to Codex and read its reply.")
    ap.add_argument("--message-file", required=True, help="file containing the message to send to Codex")
    ap.add_argument("--codex", default="codex-session", help="tmux target for the Codex pane")
    ap.add_argument("--submit-delay", type=float, default=0.5)
    ap.add_argument("--idle-secs", type=float, default=8.0, help="treat Codex as done after this many seconds of no output change")
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--history-lines", type=int, default=3000)
    args = ap.parse_args()

    target = require_tmux_target(args.codex)
    msg = Path(args.message_file).read_text(encoding="utf-8")
    if not msg.strip():
        print("[bridge] empty message; nothing sent", file=sys.stderr)
        return 2

    # Append a unique end sentinel so we can anchor exactly where the echoed
    # message ends and Codex's reply begins (robust to line wrapping).
    end_token = f"[[bridge-end {secrets.token_hex(3)}]]"
    sent = msg.rstrip() + " " + end_token

    buffer_name = "claude_to_codex_bridge"
    send_message(target, sent, buffer_name, args.submit_delay)
    # Give Codex a moment to start rendering before idle-tracking.
    time.sleep(2.0)
    final_text = wait_until_idle(target, args.history_lines, args.idle_secs, args.timeout)
    reply = extract_reply(final_text, end_token)
    print("===CODEX_REPLY_START===")
    print(reply)
    print("===CODEX_REPLY_END===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
