"""Claude CLI wrapper: invoke `claude -p --output-format stream-json` and parse the result."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from .types import ClaudeInvocation


def invoke(
    *,
    prompt: str,
    schema: dict,
    model: str,
    max_turns: int,
    log_path: Path,
    cwd: Path,
    allowed_tools: list[str] | None = None,
    timeout_s: int = 300,
) -> ClaudeInvocation:
    """Run claude-cli, persist raw stream-json to log_path, and extract structured output.

    `allowed_tools=None` leaves tool access unrestricted (default CLI behavior).
    `allowed_tools=[]` disables all tools (structured output only).
    `allowed_tools=[...]` enables only those tools.
    """
    cmd = [
        "claude", "-p",
        "--model", model,
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--max-turns", str(max_turns),
        "--json-schema", json.dumps(schema),
        "--permission-mode", "bypassPermissions",
    ]
    if allowed_tools is not None:
        cmd += ["--tools", ",".join(allowed_tools)]

    log_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True,
            cwd=cwd, timeout=timeout_s,
        )
    except subprocess.TimeoutExpired as e:
        log_path.write_text(
            _as_text(e.stdout) + "\n---TIMEOUT---\n" + _as_text(e.stderr),
            encoding="utf-8",
        )
        return ClaudeInvocation(
            structured=None, cost_usd=0.0, duration_s=time.time() - t0,
            turns=None, error=f"timeout after {timeout_s}s",
        )
    duration = time.time() - t0
    log_path.write_text(proc.stdout or "", encoding="utf-8")
    if proc.stderr:
        log_path.with_suffix(log_path.suffix + ".stderr").write_text(
            proc.stderr, encoding="utf-8"
        )
    return parse_stream(proc.stdout or "", proc.returncode, proc.stderr or "", duration)


def parse_stream(stdout: str, returncode: int, stderr: str, duration_s: float) -> ClaudeInvocation:
    """Parse a claude stream-json NDJSON payload into a ClaudeInvocation.

    Uses the final `result` event for cost/structured_output. Falls back to
    the last StructuredOutput tool_use input if the stream truncated after the
    structured output was already emitted.
    """
    final_envelope: dict = {}
    structured: dict | None = None
    tool_use_structured: dict | None = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("type") == "result":
            final_envelope = evt
            structured = evt.get("structured_output") or structured
        elif evt.get("type") == "assistant":
            for block in (evt.get("message", {}) or {}).get("content", []) or []:
                if block.get("type") == "tool_use" and block.get("name") == "StructuredOutput":
                    inp = block.get("input")
                    if isinstance(inp, dict) and inp:
                        tool_use_structured = inp
    if structured is None and tool_use_structured is not None:
        structured = tool_use_structured

    if returncode != 0 and structured is None:
        return ClaudeInvocation(
            structured=None, cost_usd=0.0, duration_s=duration_s,
            turns=final_envelope.get("num_turns"),
            error=f"claude exited {returncode}: {stderr[-500:]}",
        )
    if not final_envelope:
        return ClaudeInvocation(
            structured=structured, cost_usd=0.0, duration_s=duration_s,
            turns=None, error="no result event in stream",
        )
    return ClaudeInvocation(
        structured=structured,
        cost_usd=final_envelope.get("total_cost_usd") or 0.0,
        duration_s=duration_s,
        turns=final_envelope.get("num_turns"),
        error="",
    )


def _as_text(x) -> str:
    if x is None:
        return ""
    if isinstance(x, bytes):
        return x.decode("utf-8", errors="replace")
    return x
