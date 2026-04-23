"""Tests for stream-json parsing in bench.claude."""

from __future__ import annotations

import json

import pytest

from tools.benchmark.bench.claude import parse_stream


def _stream(*events: dict) -> str:
    return "\n".join(json.dumps(e) for e in events)


def test_parse_clean_result_extracts_structured_and_cost():
    stdout = _stream({
        "type": "result",
        "total_cost_usd": 0.1234,
        "num_turns": 3,
        "structured_output": {"answer": "hi", "cited": []},
    })
    r = parse_stream(stdout, returncode=0, stderr="", duration_s=1.0)
    assert r.structured == {"answer": "hi", "cited": []}
    assert r.cost_usd == pytest.approx(0.1234)
    assert r.turns == 3
    assert r.error == ""


def test_parse_falls_back_to_tool_use_when_structured_output_missing():
    stdout = _stream(
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "name": "StructuredOutput",
                     "input": {"answer": "from_tool_use", "cited": []}},
                ],
            },
        },
        {"type": "result", "total_cost_usd": 0.05, "num_turns": 2},
    )
    r = parse_stream(stdout, returncode=0, stderr="", duration_s=0.5)
    assert r.structured == {"answer": "from_tool_use", "cited": []}


def test_parse_returns_error_when_claude_exited_nonzero_and_no_structured():
    stdout = ""
    r = parse_stream(stdout, returncode=1, stderr="boom", duration_s=0.1)
    assert r.structured is None
    assert r.error and "claude exited 1" in r.error


def test_parse_error_when_no_result_event():
    stdout = _stream({"type": "assistant", "message": {"content": []}})
    r = parse_stream(stdout, returncode=0, stderr="", duration_s=0.1)
    assert r.structured is None
    assert r.error == "no result event in stream"


def test_parse_ignores_unparseable_lines():
    stdout = "not-json\n" + json.dumps({
        "type": "result",
        "total_cost_usd": 0.01,
        "num_turns": 1,
        "structured_output": {"k": "v"},
    })
    r = parse_stream(stdout, returncode=0, stderr="", duration_s=0.1)
    assert r.structured == {"k": "v"}
