#!/usr/bin/env python3
"""
Codex -> Claude referee relay for tmux.

Use this when the human talks only to Codex, and Codex calls Claude only when it
explicitly emits an ASK_CLAUDE block. The script is a dumb transport layer:
Codex remains the referee/orchestrator.

Requires: tmux, Python 3.9+
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import secrets
import subprocess
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Set, Tuple


# Delay (seconds) between pasting into a pane and sending Enter. Tunable via
# --submit-delay; some TUIs drop an Enter that lands in the same instant as paste.
SUBMIT_DELAY_S = 0.4


def sh(cmd: List[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def require_tmux_target(target: str) -> str:
    try:
        result = sh(["tmux", "display-message", "-p", "-t", target, "#{pane_id}"])
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"tmux target not found: {target}\n{e.stderr.strip()}") from e
    return result.stdout.strip()


# TUI gutter normalization. Claude Code / Codex render text inside bordered boxes;
# capture-pane -p strips ANSI colour but NOT box-drawing characters. We strip only
# Unicode box-vertical gutters at line start/end (NOT ASCII '|', which markdown
# tables use) plus NBSP / zero-width noise, so relayed block bodies stay clean.
_BOX_VERTICALS = "│┃┆┇┊┋║"
_LEADING_GUTTER = re.compile(r"^[ \t]*[" + _BOX_VERTICALS + r"][ \t]?")
_TRAILING_GUTTER = re.compile(r"[ \t]?[" + _BOX_VERTICALS + r"][ \t]*$")
_INVISIBLE = {" ": " ", "​": "", "﻿": "", " ": " ", " ": " "}


def normalize_pane_text(text: str) -> str:
    out_lines: List[str] = []
    for line in text.splitlines():
        for bad, good in _INVISIBLE.items():
            if bad in line:
                line = line.replace(bad, good)
        line = _LEADING_GUTTER.sub("", line)
        line = _TRAILING_GUTTER.sub("", line)
        out_lines.append(line.rstrip())
    return "\n".join(out_lines)


def capture_pane(target: str, history_lines: int) -> str:
    # -J joins wrapped lines. -S negative starts that many lines back in history.
    # Resilient: a transient tmux error during a long poll loop must NOT kill the
    # relay. Return "" so the caller simply sees no new blocks this tick.
    try:
        result = sh([
            "tmux",
            "capture-pane",
            "-t",
            target,
            "-p",
            "-J",
            "-S",
            f"-{history_lines}",
        ])
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"[relay] capture-pane transient error on {target}: {e.stderr.strip()}\n")
        return ""
    return normalize_pane_text(result.stdout)


def send_line(target: str, text: str, buffer_name: str, *, retries: int = 2) -> bool:
    # Keep terminal input single-line. Long/multiline payloads are written to files.
    # Resilient: retry transient tmux errors; soft-fail (return False) instead of
    # raising so one bad paste never kills the relay loop.
    one_line = " ".join(text.strip().splitlines())
    for attempt in range(retries + 1):
        try:
            sh(["tmux", "load-buffer", "-b", buffer_name, "-"], input_text=one_line)
            sh(["tmux", "paste-buffer", "-t", target, "-b", buffer_name])
            # Some TUIs (e.g. the Codex node composer) drop an Enter that arrives in
            # the same instant as the paste. Give the composer a moment to commit the
            # pasted text, then submit. Harmless for panes that submit instantly.
            time.sleep(SUBMIT_DELAY_S)
            sh(["tmux", "send-keys", "-t", target, "Enter"])
            sh(["tmux", "delete-buffer", "-b", buffer_name], check=False)
            return True
        except subprocess.CalledProcessError as e:
            sys.stderr.write(
                f"[relay] send-line attempt {attempt + 1}/{retries + 1} failed on {target}: {e.stderr.strip()}\n"
            )
            time.sleep(1.0)
    sys.stderr.write(f"[relay] send-line GAVE UP on {target}; message not delivered\n")
    return False


def block_hash(body: str) -> str:
    return hashlib.sha256(body.strip().encode("utf-8", errors="replace")).hexdigest()


def _marker_core(marker: str) -> str:
    # Strip the surrounding angle brackets and whitespace, leaving e.g. ASK_CLAUDE_START.
    return marker.strip().strip("<>").strip()


def extract_blocks(text: str, start_marker: str, end_marker: str) -> List[str]:
    # Tolerate TUI rendering damage: terminals sometimes wrap/clip a marker so the
    # bracket count varies (e.g. ">>" instead of ">>>"). Match the marker CORE with
    # one-or-more brackets on each side and optional surrounding whitespace, so a
    # corrupted closing marker still closes its block instead of letting the
    # non-greedy span swallow several rounds.
    sc = re.escape(_marker_core(start_marker))
    ec = re.escape(_marker_core(end_marker))
    start_pat = r"<+\s*" + sc + r"\s*>+"
    end_pat = r"<+\s*" + ec + r"\s*>+"
    pattern = re.compile(start_pat + r"(.*?)" + end_pat, re.DOTALL)
    return [m.group(1).strip() for m in pattern.finditer(text)]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_log(path: Path, title: str, body: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n## {title}\n\n")
        f.write(body.rstrip())
        f.write("\n")


def marker_instruction(marker_core: str) -> str:
    return f"three '<' characters + {marker_core} + three '>' characters"


def make_protocol_files(relay_dir: Path, run_id: str) -> Tuple[Path, Path]:
    codex_protocol = relay_dir / "protocol_codex_referee.md"
    claude_protocol = relay_dir / "protocol_claude_consultant.md"

    # NOTE: run_id is intentionally NOT embedded in markers. The detection side in
    # main() uses fixed run_id-less markers, so the protocol must match exactly.
    ask_start_core = "ASK_CLAUDE_START"
    ask_end_core = "ASK_CLAUDE_END"
    reply_start_core = "CLAUDE_TO_CODEX_START"
    reply_end_core = "CLAUDE_TO_CODEX_END"

    write_text(
        codex_protocol,
        textwrap.dedent(
            f"""
            # Codex referee relay protocol

            You are the user-facing Codex/referee. The human talks only to you.
            Claude is a private consultant that you may ask for review, critique, or an independent solution.
            You remain responsible for the final answer, file changes, and judgment.

            Run id: {run_id}

            When Claude input would materially help, emit exactly one request block and then stop your turn.
            The relay script will send the block to Claude and later send you a file path containing Claude's answer.

            Request opening marker: {marker_instruction(ask_start_core)}
            Request closing marker: {marker_instruction(ask_end_core)}

            Inside the request block, include:
            - Request id: a small increasing number if you know it
            - Goal
            - Relevant context
            - Specific question for Claude
            - Constraints, files, tests, or risks Claude should consider

            Do not use the request markers for any other purpose.
            Do not pretend Claude answered before the relay gives you Claude's answer file.
            After receiving Claude's answer, evaluate it critically. Do not copy it blindly.

            Claude's answer will be wrapped with these marker cores in Claude's terminal, but the relay will normally
            return it to you as a file path:
            - opening core: {reply_start_core}
            - closing core: {reply_end_core}
            """
        ).strip()
        + "\n",
    )

    write_text(
        claude_protocol,
        textwrap.dedent(
            f"""
            # Claude private consultant protocol

            You are Claude, a private consultant to Codex. The human is not talking to you directly.
            Codex is the referee/orchestrator and will decide what to tell the human.

            Run id: {run_id}

            For each relay request from Codex, answer only inside the required markers.

            Reply opening marker: {marker_instruction(reply_start_core)}
            Reply closing marker: {marker_instruction(reply_end_core)}

            Your answer should be useful to Codex:
            - State your conclusion first.
            - Point out risks, edge cases, or false assumptions.
            - Propose concrete next steps or patches when relevant.
            - Do not ask the human for clarification.
            - Do not modify files unless Codex explicitly asked you to and permissions allow it.
            - If you are unsure, say exactly what is uncertain.

            Do not use the reply markers for any other purpose.
            """
        ).strip()
        + "\n",
    )

    return codex_protocol, claude_protocol


def wait_for_new_block(
    *,
    target: str,
    start_marker: str,
    end_marker: str,
    seen: Set[str],
    timeout_s: float,
    poll_s: float,
    history_lines: int,
) -> str:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        text = capture_pane(target, history_lines)
        blocks = extract_blocks(text, start_marker, end_marker)
        for body in blocks:
            h = block_hash(body)
            if h not in seen:
                seen.add(h)
                return body
        time.sleep(poll_s)
    raise TimeoutError(f"Timed out waiting for block {start_marker} ... {end_marker} in {target}")


def wait_for_reply_file(
    *,
    path: Path,
    since_ts: float,
    timeout_s: float,
    poll_s: float,
) -> str:
    """Wait for Claude to WRITE its reply directly to `path`.

    This is the Claude->Codex transport. Claude Code is an alt-screen TUI, so
    tmux capture-pane only exposes the visible viewport — long marker blocks
    scroll off-screen and are never captured. Reading the reply from a file that
    Claude writes removes the length limit entirely and needs no markers.

    Accept the file only when it is FRESH (mtime >= since_ts), non-empty, and
    SIZE-STABLE across two consecutive polls (guards against reading mid-write,
    though Claude's editor writes atomically).
    """
    deadline = time.time() + timeout_s
    last_size = -1
    stable = 0
    while time.time() < deadline:
        try:
            st = path.stat()
            fresh = st.st_mtime >= since_ts - 1.0 and st.st_size > 0
        except FileNotFoundError:
            fresh = False
            st = None
        if fresh and st is not None:
            if st.st_size == last_size:
                stable += 1
                if stable >= 2:
                    return path.read_text(encoding="utf-8", errors="replace")
            else:
                stable = 0
                last_size = st.st_size
        time.sleep(poll_s)
    raise TimeoutError(f"Timed out waiting for Claude to write reply file {path}")


_OUTBOX_RE = re.compile(r"ask_(\d+)\.md$")


def list_outbox_asks(outbox: Path) -> List[Tuple[int, Path]]:
    """File ask-mode: return [(seq, path), ...] sorted by seq for ask_<seq>.md files."""
    found: List[Tuple[int, Path]] = []
    if not outbox.exists():
        return found
    for p in outbox.glob("ask_*.md"):
        m = _OUTBOX_RE.search(p.name)
        if m:
            found.append((int(m.group(1)), p))
    return sorted(found, key=lambda t: t[0])


def read_stable_file(path: Path, poll_s: float) -> str | None:
    """Read path only if size-stable across two checks (guards against reading a
    directive mid-write). Returns None if missing, empty, or still changing."""
    try:
        s1 = path.stat().st_size
    except FileNotFoundError:
        return None
    time.sleep(min(poll_s, 0.5))
    try:
        s2 = path.stat().st_size
    except FileNotFoundError:
        return None
    if s2 == 0 or s1 != s2:
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="tmux relay: Codex is referee; Claude is called only by explicit Codex ASK_CLAUDE blocks."
    )
    parser.add_argument("--codex", required=True, help="tmux target for the Codex CLI pane, e.g. cc:0.0 or %%1")
    parser.add_argument("--claude", required=True, help="tmux target for the Claude Code CLI pane, e.g. cc:0.1 or %%2")
    parser.add_argument("--workspace", default=".", help="directory for relay files; default: current directory")
    parser.add_argument("--max-calls", type=int, default=300, help="maximum Claude calls before exiting")
    parser.add_argument("--timeout", type=float, default=10800, help="seconds to wait for Claude per call (default 3h)")
    parser.add_argument("--poll", type=float, default=1.0, help="poll interval in seconds")
    parser.add_argument("--submit-delay", type=float, default=0.4, help="seconds between paste and Enter (raise if a TUI does not auto-submit)")
    parser.add_argument("--history-lines", type=int, default=4000, help="tmux scrollback lines to scan (pane ask-mode only)")
    parser.add_argument("--ask-mode", choices=["pane", "file"], default="pane",
                        help="how Codex directives are detected: 'pane' (legacy) scrapes the Codex tmux pane for "
                             "ASK_CLAUDE blocks — fragile: a pane re-render (resize / codex resume) reflows the "
                             "text so the same directive hashes differently and is re-forwarded. 'file' watches an "
                             "outbox dir for monotonically-numbered ask_<seq>.md directive files — robust dedup by "
                             "sequence, immune to pane re-render. Recommended.")
    parser.add_argument("--outbox", default=None,
                        help="file ask-mode: dir the Referee writes ask_<seq>.md directives to; "
                             "default <relay_dir>/codex_outbox")
    parser.add_argument("--responder-name", default="claude",
                        help="name of the responder agent; sets the responder-facing file prefixes "
                             "ask_<name>_NN.md / <name>_reply_NN.md (default 'claude'). Use 'bull'/'bear' "
                             "for the Bull/Bear channels so multiple relays do not collide.")
    parser.add_argument("--io-dir", default=None,
                        help="dir for the responder-facing ask_<name>_NN.md / <name>_reply_NN.md files; "
                             "default <relay_dir> (.codex-claude-relay). Use e.g. 'bb' for Bull/Bear.")
    parser.add_argument("--prime", action="store_true", help="opt-in: send protocol setup messages to Codex/Claude (default off — protocol files ignored)")
    parser.add_argument("--run-id", default=None, help="optional fixed run id; default random")
    args = parser.parse_args()

    global SUBMIT_DELAY_S
    SUBMIT_DELAY_S = args.submit_delay

    codex_target = require_tmux_target(args.codex)
    claude_target = require_tmux_target(args.claude)

    workspace = Path(args.workspace).expanduser().resolve()
    relay_dir = workspace / ".codex-claude-relay"
    relay_dir.mkdir(parents=True, exist_ok=True)

    run_id = (args.run_id or secrets.token_hex(4)).upper()
    ask_start = "<<<ASK_CLAUDE_START>>>"
    ask_end = "<<<ASK_CLAUDE_END>>>"
    reply_start = "<<<CLAUDE_TO_CODEX_START>>>"
    reply_end = "<<<CLAUDE_TO_CODEX_END>>>"

    # Protocol files are only written/used when --prime is set. By default the
    # relay ignores them entirely and just transports marked blocks.
    codex_protocol = claude_protocol = None
    if args.prime:
        codex_protocol, claude_protocol = make_protocol_files(relay_dir, run_id)
    log_path = relay_dir / f"relay_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{run_id}.md"
    write_text(
        log_path,
        textwrap.dedent(
            f"""
            # Codex-Claude referee relay log

            Run id: {run_id}
            Codex pane: {codex_target}
            Claude pane: {claude_target}
            Started: {datetime.now().isoformat(timespec='seconds')}
            """
        ).strip()
        + "\n",
    )

    buffer_name = f"codex_claude_relay_{run_id.lower()}"

    print(f"Run id: {run_id}")
    print(f"Codex pane: {codex_target}")
    print(f"Claude pane: {claude_target}")
    print(f"Relay dir: {relay_dir}")
    print(f"Log: {log_path}")
    print("Mode: Codex is referee; only explicit ASK_CLAUDE blocks are forwarded.")
    print(f"ASK detect (Codex pane): {ask_start} … {ask_end}")
    print("REPLY (Claude->Codex): file-based — Claude writes claude_reply_NN.md (no markers, no length limit)")
    print(f"Priming: {'on' if args.prime else 'off (protocol files ignored)'}")

    if args.prime:
        send_line(
            codex_target,
            f"Relay setup: read {codex_protocol} and follow it for this session. Acknowledge briefly, then continue as the user-facing referee.",
            buffer_name,
        )
        send_line(
            claude_target,
            f"Relay setup: read {claude_protocol} and follow it for this session. Acknowledge briefly; wait for relay requests from Codex.",
            buffer_name,
        )

    # Baseline existing ASK blocks so old text in the Codex scrollback is not
    # reprocessed. The Claude->Codex direction is file-based (claude_reply_NN.md),
    # so no reply-marker baseline is needed.
    time.sleep(1.0)
    seen_asks: Set[str] = {block_hash(b) for b in extract_blocks(capture_pane(codex_target, args.history_lines), ask_start, ask_end)}

    # File ask-mode: watch an outbox dir for monotonically-numbered directive files.
    # Baseline = highest existing seq, so pre-existing directives are not reprocessed.
    io_dir = (Path(args.io_dir).expanduser().resolve() if args.io_dir else relay_dir)
    io_dir.mkdir(parents=True, exist_ok=True)
    rname = args.responder_name
    outbox = (Path(args.outbox).expanduser().resolve() if args.outbox else relay_dir / "codex_outbox")
    last_outbox_seq = 0
    if args.ask_mode == "file":
        outbox.mkdir(parents=True, exist_ok=True)
        existing = list_outbox_asks(outbox)
        last_outbox_seq = existing[-1][0] if existing else 0
        print(f"ASK detect: FILE mode — watching {outbox} (baseline seq={last_outbox_seq}); pane scraping DISABLED")

    calls = 0
    try:
        while calls < args.max_calls:
            try:
                if args.ask_mode == "file":
                    # Robust: process the next directive file with seq > last seen.
                    # A pane re-render cannot create a new outbox file, so there is no
                    # re-forward of already-handled directives.
                    new_ask = None
                    for seq, p in list_outbox_asks(outbox):
                        if seq <= last_outbox_seq:
                            continue
                        body = read_stable_file(p, args.poll)
                        if body is None:
                            break  # still being written; retry next tick (do NOT advance seq)
                        last_outbox_seq = seq
                        new_ask = body.strip()
                        break
                    if new_ask is None:
                        time.sleep(args.poll)
                        continue
                else:
                    codex_text = capture_pane(codex_target, args.history_lines)
                    ask_blocks = extract_blocks(codex_text, ask_start, ask_end)
                    new_ask = None
                    for body in ask_blocks:
                        h = block_hash(body)
                        if h not in seen_asks:
                            seen_asks.add(h)
                            new_ask = body
                            break

                    if new_ask is None:
                        time.sleep(args.poll)
                        continue

                calls += 1
                ask_path = io_dir / f"ask_{rname}_{calls:02d}.md"
                reply_path = io_dir / f"{rname}_reply_{calls:02d}.md"
                write_text(ask_path, new_ask + "\n")
                append_log(log_path, f"Codex request {calls}", new_ask)
                print(f"[{calls}/{args.max_calls}] Codex requested Claude: {ask_path}")

                # File-based reply: Claude WRITES its full answer to reply_path.
                # No length limit, no markers, immune to alt-screen capture loss.
                # Remove any stale reply file so the freshness check is unambiguous.
                try:
                    reply_path.unlink()
                except FileNotFoundError:
                    pass
                request_ts = time.time()
                send_line(
                    claude_target,
                    f"Relay request {calls} from Codex: read {ask_path} and WRITE your full reply "
                    f"(plain text, any length, no markers needed) to {reply_path} — overwrite it, "
                    f"write nothing else there. The relay forwards that file to Codex once you save it.",
                    buffer_name,
                )

                try:
                    claude_answer = wait_for_reply_file(
                        path=reply_path,
                        since_ts=request_ts,
                        timeout_s=args.timeout,
                        poll_s=args.poll,
                    )
                except TimeoutError as e:
                    err_text = f"Claude did not write a reply file before timeout. Error: {e}"
                    write_text(reply_path, err_text + "\n")
                    append_log(log_path, f"Claude timeout {calls}", err_text)
                    send_line(
                        codex_target,
                        f"Relay error for Claude request {calls}: Claude did not write a reply before timeout. See {reply_path}. Continue as referee without Claude if possible.",
                        buffer_name,
                    )
                    continue

                # reply_path was written by Claude; do NOT overwrite it. Just log + notify.
                append_log(log_path, f"Claude answer {calls}", claude_answer)
                print(f"[{calls}/{args.max_calls}] Claude replied (file): {reply_path}")

                send_line(
                    codex_target,
                    f"Claude reply for relay request {calls} is ready at {reply_path}. Read it, evaluate it critically as referee, and continue with the human.",
                    buffer_name,
                )
            except KeyboardInterrupt:
                raise
            except Exception as e:  # noqa: BLE001 — relay must survive any single-iteration error
                sys.stderr.write(f"[relay] iteration error (continuing): {type(e).__name__}: {e}\n")
                try:
                    append_log(log_path, "Relay iteration error", f"{type(e).__name__}: {e}")
                except Exception:
                    pass
                time.sleep(args.poll)
                continue

        print(f"Reached --max-calls={args.max_calls}. Exiting.")
        append_log(log_path, "Relay stopped", f"Reached max calls: {args.max_calls}")
    except KeyboardInterrupt:
        print("Interrupted. Exiting.")
        append_log(log_path, "Relay stopped", "Interrupted by user")

    return 0


if __name__ == "__main__":
    sys.exit(main())
