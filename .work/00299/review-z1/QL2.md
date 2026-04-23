# QL2 外部リンクの一致 — QA レビュー

対象: `tools/rbkc/scripts/verify/verify.py` の `check_external_urls` / `_source_urls` と、
`tests/ut/test_verify.py` の `TestVerifyFileQL2`。

---

## 1. 実装の有無

### 1-1. 本体実装 ✅

- `_source_urls` — `verify.py:278-310`
- `check_external_urls` — `verify.py:313-339`
- 統合 — `verify.py:935`（`_verify_file_checks` から呼び出し）

RST 抽出（`verify.py:286-298`）:

- `docutils` で `doctree` を生成し、`doctree.findall(nodes.reference)` を巡回
- `ref.get("refuri")` が `http://` / `https://` で始まるもののみ収集
- 仕様書 §3-2 の AST-only 原則に準拠

MD 抽出（`verify.py:300-308`）:

- `md_ast.parse()` → `md_ast_visitor.extract_document()`
- `external_urls` は `md_ast_visitor.py:394-411` で `link_open` トークンから `href` を収集（`http://`/`https://` のみ）
- markdown-it-py は `[text](url)` と autolink `<https://...>` の両方を `link_open`/`link_close` として生成するため、同じ経路で両方をカバー

### 1-2. regex 禁止原則 ✅

- `verify.py` 内に `_URL_RE` やモジュールレベルの `re.compile(...http...)` は存在しない
  （`grep -n "_URL_RE\|re\.compile.*http\|re\.findall.*http" verify.py` → ヒット 0）
- URL 収集は全て AST ノード属性（`refuri` / `href`）からのみ
- JSON 側の存在確認は「完全文字列の部分一致（`url in json_text`）」で行っており、正規表現の境界問題（括弧・クエリ・CJK 末尾句読点等）を原理的に回避できる設計（`verify.py:316-320` コメントで明記）

**判定**: AST-only 原則を完全に遵守。regex ベースの脆弱性は排除されている。

---

## 2. ユニットテストのカバレッジ

`test_verify.py:343-418` の `TestVerifyFileQL2` は 10 ケース（全 `fmt="rst"` or `xlsx`）。

| 観点 | カバー状況 | 該当テスト / 備考 |
|------|-----------|------------------|
| RST `reference.refuri` http(s) が JSON 欠落 → FAIL | ✅ | `test_fail_url_missing_from_json` (L355) |
| RST `reference.refuri` http(s) が JSON 存在 → PASS | ✅ | `test_pass_url_in_json` (L350) |
| RST inline code (``` ``http://...`` ```) 末尾バッククォート混入なし | ✅ | `test_pass_rst_inline_code_url_trailing_backtick_trimmed` (L404) |
| RST substitution 内のみの URL はスキップ | ✅ | `test_pass_rst_substitution_only_url_skipped` (L410) — §3-2 スコープ外仕様に整合 |
| RST target definition URL はスキップ（converter 側で落ちる） | ✅ | `test_pass_rst_target_def_url_excluded` (L368) |
| 同一 URL 重複 → 1 回のみ報告 / 片方でも JSON にあれば PASS | ✅ | `test_pass_duplicate_url_reported_once` (L361) + `verify.py:332-336` (`seen` set) |
| Section content 配下での missing 検知 | ✅ | `test_fail_url_in_section_content_missing` (L389) |
| Section content 配下の URL 存在で PASS | ✅ | `test_pass_url_in_section_content` (L397) |
| xlsx / no_knowledge_content スキップ | ✅ | `test_pass_xlsx_skipped` / `test_pass_no_knowledge_content_skipped` |
| **MD `[text](https://...)` missing → FAIL** | ⚠️ | **専用テストなし**（実装は `md_ast_visitor` で動作、ただしテストで回帰検知できない） |
| **MD autolink `<https://...>` missing → FAIL** | ⚠️ | **専用テストなし**（markdown-it-py 挙動依存。autolink が `link_open` に変換される前提は明示検証されていない） |
| **URL with query string `?a=1&b=2` / fragment `#frag`** | ⚠️ | **regex 非使用のため実装上は安全だが、回帰テストなし** |
| **URL with 括弧 `https://en.wikipedia.org/wiki/Foo_(bar)`** | ⚠️ | **regex 非使用のため安全だが、テスト未存在** |
| **URL 直後に CJK 句読点 `https://example.com。`** | ⚠️ | **regex 非使用のため安全だが、テスト未存在**（AST 属性なら句読点を拾わないが、仕様の明示検証がない） |
| **同一 URL が JSON 内で複数回出現** | ⚠️ | 暗黙にテストされていない（`in` 判定なので自明ではあるが） |
| **http / https バリアント（別 URL として扱うこと）** | ⚠️ | テスト未存在。`http://example.com` と `https://example.com` を混同しないことの明示検証なし |

**判定**: ⚠️ 主要経路（RST + JSON missing）は堅いが、**MD 専用の単体テストが 0 本**。実装が `md_ast_visitor` に委譲されているため `md_ast_visitor` 側の単体テストでカバーされている可能性はあるが、`check_external_urls(fmt="md", ...)` の E2E パスに対する直接テストが欠けている。

---

## 3. v6 verify 実行結果

```
$ bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0

$ bash rbkc.sh verify 6 2>&1 | tail -3
All files verified OK

$ python3 -m pytest tests/ 2>&1 | tail -3
tests/ut/test_verify.py ................................................ [ 76%]
...........................                                              [ 95%]
tests/ut/test_xlsx_converters.py ......                                  [100%]
============================= 138 passed in 2.86s ==============================
```

✅ v6 verify FAIL 0 / ユニットテスト 138 件全 PASS。

---

## 4. 総合判定

| 項目 | 判定 |
|------|------|
| 実装存在 | ✅ |
| AST-only 原則遵守（regex 禁止） | ✅ |
| ユニットテストカバレッジ | ⚠️ MD 経路・URL 特殊形のテスト不足 |
| v6 verify 0 FAIL | ✅ |
| 全 UT PASS | ✅ |

**総合**: ⚠️ **条件付き合格**。実装は AST-only 原則に完全準拠し品質ゲートとしての信頼性は高いが、MD 経路と URL 特殊形に対する回帰テストが不足している。現時点で v6 は RST 主体のため実被害はないが、v5/v1.x では MD ソースが混在し得るため、将来の回帰リスクを残している。

---

## 5. 改善案（High / Medium / Low）

### 🔴 High: MD 経路の単体テスト追加

`TestVerifyFileQL2` に以下を追加する（最小 3 ケース）:

| # | ケース | 期待 |
|---|--------|------|
| H1 | `test_fail_md_inline_link_missing_from_json` — `src = "[公式](https://example.com)を参照\n"` で JSON に URL なし | FAIL |
| H2 | `test_pass_md_inline_link_in_json` — 同じ src で JSON に URL あり | PASS |
| H3 | `test_fail_md_autolink_missing_from_json` — `src = "<https://example.com>\n"` で JSON に URL なし | FAIL |

**理由**: 実装は `md_ast_visitor` へ委譲されているが、`check_external_urls(fmt="md", ...)` という境界での動作保証が欠けている。markdown-it-py のバージョン更新で autolink の token 型が変わった場合、現状のテストでは検知できない。

### 🟡 Medium: URL 特殊形の回帰テスト

AST-only 実装のおかげで現状 PASS するはずだが、実装変更時の保険として追加:

| # | ケース |
|---|--------|
| M1 | `test_pass_url_with_query_fragment` — `https://example.com/path?a=1&b=2#frag` |
| M2 | `test_pass_url_with_parentheses` — `https://en.wikipedia.org/wiki/Foo_(bar)` |
| M3 | `test_pass_url_followed_by_cjk_punctuation` — `参照: https://example.com。続き` |
| M4 | `test_fail_http_vs_https_distinct` — ソース `http://example.com` / JSON `https://example.com` → FAIL |

**理由**: QL2 仕様書 §3-2 が「完全同一」を要求しているため、http/https の区別や句読点除外の挙動は明示テストで固定化すべき。

### 🟢 Low: docstring の整備

- `_source_urls` の docstring に「autolink `<https://...>` も `link_open` として収集される」ことを明記し、markdown-it-py 依存を可視化する
- `check_external_urls` のテストドキュメントに「JSON 側 substring 検索は regex 不使用のため括弧/クエリで破綻しない」ことを明記

これらは仕様の固定化に寄与し、将来の回帰を防ぐ。
