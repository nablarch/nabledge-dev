"""Tests for scripts/common/handler_js — parse_handler_dict, parse_handler_queue, render_handler_table."""
from __future__ import annotations

import pytest

from scripts.common.handler_js import (
    parse_handler_dict,
    parse_handler_queue,
    render_handler_table,
)


# ---------------------------------------------------------------------------
# parse_handler_dict
# ---------------------------------------------------------------------------

class TestParseHandlerDict:
    def test_basic_entry(self):
        js = """
var Handler = {
SomeHandler: {
  name: "テストハンドラ"
, behavior: {
    inbound:  "往路処理テキスト"
  , outbound: "復路処理テキスト"
  , error:    "例外処理テキスト"
  }
}
};
"""
        result = parse_handler_dict(js)
        assert "SomeHandler" in result
        h = result["SomeHandler"]
        assert h["name"] == "テストハンドラ"
        assert h["behavior"]["inbound"] == "往路処理テキスト"
        assert h["behavior"]["outbound"] == "復路処理テキスト"
        assert h["behavior"]["error"] == "例外処理テキスト"

    def test_multiline_concatenation(self):
        js = """
var Handler = {
SomeHandler: {
  name: "ハンドラ"
, behavior: {
    inbound:  "テキストA"
            + "テキストB"
  , outbound: "-"
  , error:    "-"
  }
}
};
"""
        result = parse_handler_dict(js)
        assert result["SomeHandler"]["behavior"]["inbound"] == "テキストAテキストB"

    def test_empty_string_value(self):
        js = """
var Handler = {
RetryHandler: {
  name: "リトライハンドラ"
, behavior: {
    inbound:  ""
  , outbound: ""
  , error:    "エラー処理"
  }
}
};
"""
        result = parse_handler_dict(js)
        assert result["RetryHandler"]["behavior"]["inbound"] == ""
        assert result["RetryHandler"]["behavior"]["outbound"] == ""

    def test_callback_present(self):
        js = """
var Handler = {
TxHandler: {
  name: "トランザクションハンドラ"
, behavior: {
    inbound:  "開始"
  , outbound: "コミット"
  , error:    "ロールバック"
  , callback: "コミット後処理"
  }
}
};
"""
        result = parse_handler_dict(js)
        assert result["TxHandler"]["behavior"]["callback"] == "コミット後処理"

    def test_dash_value(self):
        js = """
var Handler = {
SimpleHandler: {
  name: "シンプルハンドラ"
, behavior: {
    inbound:  "-"
  , outbound: "-"
  , error:    "-"
  }
}
};
"""
        result = parse_handler_dict(js)
        assert result["SimpleHandler"]["behavior"]["inbound"] == "-"

    def test_trailing_whitespace_stripped(self):
        js = """
var Handler = {
Handler1: {
  name: "ハンドラ"
, behavior: {
    inbound:  "テキスト   "
  , outbound: "-"
  , error:    "-"
  }
}
};
"""
        result = parse_handler_dict(js)
        assert result["Handler1"]["behavior"]["inbound"] == "テキスト"

    def test_suffixed_key(self):
        js = """
var Handler = {
ThreadContextHandler_main: {
  name: "スレッドコンテキストハンドラ(メイン)"
, behavior: {
    inbound:  "初期化"
  , outbound: "-"
  , error:    "-"
  }
}
};
"""
        result = parse_handler_dict(js)
        assert "ThreadContextHandler_main" in result
        assert result["ThreadContextHandler_main"]["name"] == "スレッドコンテキストハンドラ(メイン)"

    def test_single_quote_values(self):
        js = """
var Handler = {
Handler1: {
  name: 'シングルクォートハンドラ'
, behavior: {
    inbound:  'inbound text'
  , outbound: '-'
  , error:    '-'
  }
}
};
"""
        result = parse_handler_dict(js)
        assert result["Handler1"]["name"] == "シングルクォートハンドラ"
        assert result["Handler1"]["behavior"]["inbound"] == "inbound text"


# ---------------------------------------------------------------------------
# parse_handler_queue
# ---------------------------------------------------------------------------

class TestParseHandlerQueue:
    def test_basic_queue(self):
        script = """<script>
var Context      = 'handler'
  , HandlerQueue = [
      "ThreadContextClearHandler"
    , "ThreadContextHandler_main"
    ];
</script>"""
        context, queue = parse_handler_queue(script)
        assert context == "handler"
        assert queue == ["ThreadContextClearHandler", "ThreadContextHandler_main"]

    def test_multiline_handlerqueue(self):
        script = """<script>
var Context      = 'handler sub_thread'
  , HandlerQueue = [
      "HandlerA"
    , "HandlerB"
    , "HandlerC"
    , "HandlerD"
    , "HandlerE"
    ];
</script>"""
        context, queue = parse_handler_queue(script)
        assert context == "handler sub_thread"
        assert queue == ["HandlerA", "HandlerB", "HandlerC", "HandlerD", "HandlerE"]

    def test_single_element_queue(self):
        script = """<script>
var Context      = 'handler web'
  , HandlerQueue = ["SomeHandler"];
</script>"""
        context, queue = parse_handler_queue(script)
        assert context == "handler web"
        assert queue == ["SomeHandler"]


# ---------------------------------------------------------------------------
# render_handler_table
# ---------------------------------------------------------------------------

_SAMPLE_DICT = {
    "HandlerA": {
        "name": "ハンドラA",
        "behavior": {"inbound": "往路A", "outbound": "復路A", "error": "-"},
    },
    "HandlerB": {
        "name": "ハンドラB",
        "behavior": {"inbound": "-", "outbound": "復路B", "error": "例外B"},
    },
}

_DICT_WITH_CALLBACK = {
    "HandlerA": {
        "name": "ハンドラA",
        "behavior": {"inbound": "往路A", "outbound": "復路A", "error": "-", "callback": "-"},
    },
    "HandlerB": {
        "name": "ハンドラB",
        "behavior": {"inbound": "-", "outbound": "復路B", "error": "例外B", "callback": "コールバック処理"},
    },
}


class TestRenderHandlerTable:
    def test_no_callback_four_columns(self):
        result = render_handler_table(_SAMPLE_DICT, ["HandlerA", "HandlerB"])
        lines = result.strip().splitlines()
        # Structure: preamble, empty, header, sep, data×2 = 6 lines
        assert len(lines) == 6
        header = lines[2]
        assert "往路処理" in header
        assert "復路処理" in header
        assert "例外処理" in header
        assert "コールバック" not in header
        assert "ハンドラA" in lines[4]
        assert "往路A" in lines[4]

    def test_with_callback_five_columns(self):
        result = render_handler_table(_DICT_WITH_CALLBACK, ["HandlerA", "HandlerB"])
        lines = result.strip().splitlines()
        assert "コールバック" in lines[2]
        assert len(lines) == 6

    def test_br_in_callback_replaced(self):
        d = {
            "HandlerA": {
                "name": "ハンドラA",
                "behavior": {
                    "inbound": "-", "outbound": "-", "error": "-",
                    "callback": "処理1<br/>処理2<br/>処理3",
                },
            },
        }
        result = render_handler_table(d, ["HandlerA"])
        assert "処理1 / 処理2 / 処理3" in result
        assert "<br/>" not in result

    def test_unknown_key_renders_unknown(self):
        result = render_handler_table(_SAMPLE_DICT, ["HandlerA", "UnknownHandler"])
        assert "(不明)" in result

    def test_empty_string_behavior_renders_dash(self):
        d = {
            "HandlerA": {
                "name": "ハンドラA",
                "behavior": {"inbound": "", "outbound": "", "error": ""},
            },
        }
        result = render_handler_table(d, ["HandlerA"])
        # Empty string → render as "-"
        lines = result.strip().splitlines()
        # Structure: preamble, empty, header, sep, data = 5 lines
        data_row = lines[4]
        assert data_row.count("- |") >= 3 or data_row.count("| -") >= 1

    def test_all_callback_dash_omits_column(self):
        d = {
            "HandlerA": {
                "name": "ハンドラA",
                "behavior": {"inbound": "往路", "outbound": "-", "error": "-", "callback": "-"},
            },
            "HandlerB": {
                "name": "ハンドラB",
                "behavior": {"inbound": "-", "outbound": "復路", "error": "-", "callback": "-"},
            },
        }
        result = render_handler_table(d, ["HandlerA", "HandlerB"])
        assert "コールバック" not in result

    def test_header_row_format(self):
        result = render_handler_table(_SAMPLE_DICT, ["HandlerA"])
        lines = result.strip().splitlines()
        # lines[0] = preamble, lines[1] = empty, lines[2] = header, lines[3] = sep
        assert lines[2].startswith("| ハンドラ")
        assert "---" in lines[3]

    def test_empty_queue_returns_empty_string(self):
        result = render_handler_table(_SAMPLE_DICT, [])
        assert result == ""

    def test_preamble_present(self):
        result = render_handler_table(_SAMPLE_DICT, ["HandlerA"])
        assert "**ハンドラ処理概要**" in result
