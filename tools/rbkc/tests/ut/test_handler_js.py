"""Tests for scripts/common/handler_js — parse_api_dict, parse_handler_dict, parse_handler_queue, render_handler_table."""
from __future__ import annotations

import pytest

from scripts.common.handler_js import (
    parse_api_dict,
    parse_handler_dict,
    parse_handler_queue,
    render_handler_table,
)


# ---------------------------------------------------------------------------
# parse_api_dict
# ---------------------------------------------------------------------------

_API_JS_SNIPPET = """<script>
var Api = {
RequestMessage: {
  name: 'RequestMessage'
, doc: 'http://example.com/RequestMessage.html'
},
ResponseMessage: {
  name: 'ResponseMessage'
, doc: 'http://example.com/ResponseMessage.html'
}
};
var Handler = {};
</script>"""


class TestParseApiDict:
    def test_basic_entries(self):
        result = parse_api_dict(_API_JS_SNIPPET)
        assert "RequestMessage" in result
        assert result["RequestMessage"]["name"] == "RequestMessage"
        assert "ResponseMessage" in result
        assert result["ResponseMessage"]["name"] == "ResponseMessage"

    def test_empty_api_block(self):
        js = "<script>\nvar Api = {};\nvar Handler = {};\n</script>"
        result = parse_api_dict(js)
        assert result == {}

    def test_no_api_block(self):
        js = "<script>\nvar Handler = {};\n</script>"
        result = parse_api_dict(js)
        assert result == {}


# ---------------------------------------------------------------------------
# parse_handler_dict
# ---------------------------------------------------------------------------

_FULL_JS = """<script>
var Api = {
RequestMessage: {
  name: 'RequestMessage'
, doc: ''
},
ResponseMessage: {
  name: 'ResponseMessage'
, doc: ''
}
};

var Handler = {

SomeHandler: {
  name: "テストハンドラ"
, package: "nablarch.fw.test"
, type: {
    argument: Api.RequestMessage
  , returns:  Api.ResponseMessage
  }
, behavior: {
    inbound:  "往路処理テキスト"
  , outbound: "復路処理テキスト"
  , error:    "例外処理テキスト"
  }
}

};
</script>"""


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

    def test_package_and_type_fields(self):
        """Extended: parse_handler_dict must extract package and type (argument/returns)."""
        api_dict = {
            "RequestMessage": {"name": "RequestMessage"},
            "ResponseMessage": {"name": "ResponseMessage"},
        }
        js = """
var Handler = {
SomeHandler: {
  name: "テストハンドラ"
, package: "nablarch.fw.test"
, type: {
    argument: Api.RequestMessage
  , returns:  Api.ResponseMessage
  }
, behavior: {
    inbound:  "往路"
  , outbound: "復路"
  , error:    "-"
  }
}
};
"""
        result = parse_handler_dict(js, api_dict=api_dict)
        h = result["SomeHandler"]
        assert h["package"] == "nablarch.fw.test"
        assert h["type"]["argument"] == "RequestMessage"
        assert h["type"]["returns"] == "ResponseMessage"

    def test_type_null_argument(self):
        """null type.argument / returns must resolve to None."""
        js = """
var Handler = {
SomeHandler: {
  name: "ハンドラ"
, package: "nablarch.fw"
, type: {
    argument: null
  , returns:  null
  }
, behavior: {
    inbound:  "-"
  , outbound: "-"
  , error:    "-"
  }
}
};
"""
        result = parse_handler_dict(js, api_dict={})
        h = result["SomeHandler"]
        assert h["type"]["argument"] is None
        assert h["type"]["returns"] is None

    def test_api_key_not_in_api_dict(self):
        """Api.Unknown not in api_dict → type field resolves to None."""
        js = """
var Handler = {
SomeHandler: {
  name: "ハンドラ"
, package: "nablarch.fw"
, type: {
    argument: Api.UnknownType
  , returns:  null
  }
, behavior: {
    inbound:  "-"
  , outbound: "-"
  , error:    "-"
  }
}
};
"""
        result = parse_handler_dict(js, api_dict={})
        h = result["SomeHandler"]
        assert h["type"]["argument"] is None

    def test_no_package_field(self):
        """Handlers without package field (old format) still parse without error."""
        js = """
var Handler = {
OldHandler: {
  name: "旧ハンドラ"
, behavior: {
    inbound:  "往路"
  , outbound: "-"
  , error:    "-"
  }
}
};
"""
        result = parse_handler_dict(js)
        h = result["OldHandler"]
        assert h["name"] == "旧ハンドラ"
        assert h.get("package") is None
        assert h.get("type") is None

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
        "package": "nablarch.fw.test",
        "type": {"argument": "RequestMessage", "returns": "ResponseMessage"},
        "behavior": {"inbound": "往路A", "outbound": "復路A", "error": "-"},
    },
    "HandlerB": {
        "name": "ハンドラB",
        "package": "nablarch.fw.test",
        "type": {"argument": None, "returns": None},
        "behavior": {"inbound": "-", "outbound": "復路B", "error": "例外B"},
    },
}

_DICT_WITH_CALLBACK = {
    "HandlerA": {
        "name": "ハンドラA",
        "package": "nablarch.fw.test",
        "type": {"argument": "Request", "returns": "Result"},
        "behavior": {"inbound": "往路A", "outbound": "往路A", "error": "-", "callback": "-"},
    },
    "HandlerB": {
        "name": "ハンドラB",
        "package": "nablarch.fw.test",
        "type": {"argument": None, "returns": None},
        "behavior": {"inbound": "-", "outbound": "復路B", "error": "例外B", "callback": "コールバック処理"},
    },
}


class TestRenderHandlerTable:
    def test_includes_class_name_and_type_columns(self):
        """クラス名・入力型・結果型列がヘッダに含まれる (design §3-1)."""
        result = render_handler_table(_SAMPLE_DICT, ["HandlerA"])
        header = result.strip().splitlines()[0]
        assert "クラス名" in header
        assert "入力型" in header
        assert "結果型" in header

    def test_class_name_is_package_dot_key(self):
        """クラス名 = package + '.' + key."""
        result = render_handler_table(_SAMPLE_DICT, ["HandlerA"])
        assert "nablarch.fw.test.HandlerA" in result

    def test_type_null_renders_dash(self):
        """null type.argument / returns must render as '-'."""
        result = render_handler_table(_SAMPLE_DICT, ["HandlerB"])
        # HandlerB has argument=None, returns=None → both render as "-"
        lines = result.strip().splitlines()
        data_row = lines[2]  # header(0), sep(1), data(2)
        # The "-" for input and result type should appear
        assert "| - |" in data_row or data_row.count("| -") >= 2

    def test_no_callback_base_columns(self):
        result = render_handler_table(_SAMPLE_DICT, ["HandlerA", "HandlerB"])
        lines = result.strip().splitlines()
        # Structure: header, sep, data×2 = 4 lines
        assert len(lines) == 4
        header = lines[0]
        assert "往路処理" in header
        assert "復路処理" in header
        assert "例外処理" in header
        assert "コールバック" not in header
        assert "ハンドラA" in lines[2]
        assert "往路A" in lines[2]

    def test_with_callback_includes_column(self):
        result = render_handler_table(_DICT_WITH_CALLBACK, ["HandlerA", "HandlerB"])
        lines = result.strip().splitlines()
        assert "コールバック" in lines[0]
        assert len(lines) == 4

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

    def test_closing_br_tag_replaced(self):
        """</br/> (invalid but present in Handler.js) must be replaced with ' / '."""
        d = {
            "HandlerA": {
                "name": "ハンドラA",
                "behavior": {
                    "inbound": "-", "outbound": "-", "error": "-",
                    "callback": "処理1<br/>処理2</br/>",
                },
            },
        }
        result = render_handler_table(d, ["HandlerA"])
        assert "</br/>" not in result
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
        # Structure: header, sep, data = 3 lines
        data_row = lines[2]
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
        # lines[0] = header, lines[1] = sep, lines[2] = data
        assert lines[0].startswith("| ハンドラ")
        assert "---" in lines[1]

    def test_empty_queue_returns_empty_string(self):
        result = render_handler_table(_SAMPLE_DICT, [])
        assert result == ""
