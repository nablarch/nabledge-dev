# QL1 内部リンクの正確性 — QA Review

**Scope**: RST / MD (Excel 対象外). AST-only per `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2.

## 1. 実装の有無

**Entry point**: `tools/rbkc/scripts/verify/verify.py:954` `check_source_links(source_text, fmt, data, label_map, source_path)`

Dispatcher at `verify.py:966` short-circuits for `xlsx` / `no_knowledge_content`.

### RST (file:line)

| Node type | Location | Behavior | Verdict |
|---|---|---|---|
| `:ref:` with display `text <label>` | `verify.py:986-1005` (iterates `doctree.findall(nodes.inline)` filtered by `classes` starting with `role-ref`) | display 文字列を JSON に substring 検索。無ければ FAIL | ✅ |
| `:ref:` bare label | `verify.py:1006-1013` | `label_map.get(label)` で resolve 成功したタイトルを JSON に substring 検索 | ✅ |
| `figure` node | `verify.py:1016-1032` | caption があればそれ、無ければ image uri の filename を JSON 検索。`_has_visible_text` (`verify.py:1069-1085`) で inline-only caption (例 `[1]_`) は filename fallback | ✅ |
| `image` node (figure 外) | `verify.py:1035-1044` | `alt` → filename の優先で JSON 検索 | ✅ |
| `literal_block` (`.. literalinclude::` 等) | `verify.py:1046-1047` コメントのみ、実装なし | 設計書 §3-2 どおり **QC1 側でカバー**する旨を明記 | ✅ (設計通り) |

AST は `scripts/common/rst_ast.parse` (`verify.py:978`) 経由。regex なし。label_map は `scripts/common/labels.build_label_map` (`verify.py:22` import、run.py で構築される) で cross-document `:ref:` も解決可能。

### MD (file:line)

| Node type | Location | Behavior | Verdict |
|---|---|---|---|
| `[text](path)` non-external | `verify.py:1049-1064`、`md_ast_visitor.extract_document(tokens).internal_links` 経由 | link text を JSON に substring 検索。重複は `seen_link_texts` で一度だけ | ✅ |
| inline `image` (`![alt](src)`) | **実装なし** — `extract_document().internal_links` に image が含まれるかは `md_ast_visitor` 依存。QL1 経路では `internal_links` のみ参照 | ⚠️ 設計書は「MD inline `image`」も QL1 対象。コード上 image alt/filename を独立に QL1 で検査していない。画像 alt は QC1/QC2 (sequential-delete) が fallback で拾う前提に見えるが、設計書 §3-2 の AST node table に明示記載があるため **仕様と実装の乖離** | ⚠️ |

External link (`http://`/`https://`) は `internal_links` に入らない設計で、QL2 の管轄 — `test_pass_md_external_link_skipped` で確認されている。

## 2. ユニットテストのカバレッジ

`tests/ut/test_verify.py:693` `TestCheckSourceLinks` (9 tests, all passing).

| 要求ケース | テスト | file:line | Verdict |
|---|---|---|---|
| RST `:ref:` display text missing | `test_fail_rst_ref_display_text_missing` | `test_verify.py:712` | ✅ |
| RST `:ref:` bare label, target title missing | `test_fail_rst_ref_plain_label_title_missing` | `test_verify.py:724` | ✅ |
| RST figure caption missing | **なし** | — | ❌ |
| RST figure inline-only caption (fallback to filename) | **なし** (`_has_visible_text` も直接テストなし) | — | ❌ |
| RST image alt / filename missing | **なし** | — | ❌ |
| RST `literalinclude` 本体 (仕様上 QC1 管轄の認識) | **なし** — split を明示するテスト/コメントは test 側に無し (実装側 `verify.py:1046` にコメントあり) | — | ⚠️ |
| MD `[text](path)` text missing | `test_fail_md_internal_link_text_missing` | `test_verify.py:743` | ✅ |
| MD image alt / src missing | **なし** | — | ❌ |
| CJK caption のエッジ | `:ref:` 日本語 display は `test_pass_rst_ref_display_text_in_json` (`test_verify.py:707`) でカバー。figure caption CJK は未検査 | — | ⚠️ |
| cross-document `:ref:` via `build_label_map` | `test_pass_rst_ref_plain_label_resolved` / `test_pass_rst_ref_unknown_label_skipped` (`test_verify.py:718, 731`) は label_map 経由の resolution をカバー。ただし `build_label_map` そのものの統合テストはこのクラスにはない | — | ⚠️ |
| `no_knowledge_content` skip | `test_pass_no_knowledge_content_skipped` (`test_verify.py:755`) | ✅ |
| MD external link skipped (QL2 側) | `test_pass_md_external_link_skipped` (`test_verify.py:749`) | ✅ |

**総評**: `:ref:` 系と MD internal link は網羅されているが、**figure / image（RST・MD とも）がユニットテスト完全欠落**。v6 実データで FAIL が出ていないのは偶々で、regression に対して脆弱。

## 3. v6 verify 実行結果 & unit test 実行結果

```
$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0
$ tail -3 output
All files verified OK

$ python3 -m pytest tests/ 2>&1 | tail -3
tests/ut/test_xlsx_converters.py ......                                  [100%]
============================= 138 passed in 3.85s ==============================
```

✅ v6 FAIL 0 / ✅ 138 passed

## 4. 総合判定

**⚠️ Partial** — 実装は設計に概ね忠実 (RST AST ベース、regex 排除、literalinclude の QC1 委譲も明示) だが、以下 2 点で品質ゲートとしての完全性を欠く:

1. **MD inline `image` の QL1 検査なし** (設計書 §3-2 node table との乖離)
2. **RST figure / image、MD image のユニットテスト完全欠落** — bug-revealing ケース不足。v6 でたまたま違反が無いだけ、今後のソース追加や converter 変更で regression を見逃しうる

ゼロトレランス方針下では ❌ 寄りの ⚠️。修正必須扱いを推奨。

## 5. 改善案 (Priority 付き)

**[High] RST figure/image の bug-revealing テストを追加**
- Description: `verify.py:1016-1044` の実装パスが一度もテストされておらず、`_has_visible_text` の fallback ロジックも未検証。converter や docutils 側の挙動変更で silent regression する
- Proposed fix: `TestCheckSourceLinks` に最小限 4 件追加:
  - `test_fail_rst_figure_caption_missing` — caption が JSON に無い
  - `test_pass_rst_figure_inline_only_caption_filename_fallback` — caption が `[1]_` のみで uri の filename で検査される
  - `test_fail_rst_image_alt_missing` / `test_fail_rst_image_filename_fallback_missing`
  - CJK caption 版も 1 件

**[High] MD image の QL1 実装 + テスト**
- Description: 設計書 §3-2 は MD inline `image` を QL1 対象と明記しているが、`verify.py:1049-1064` は `internal_links` のみ参照し image alt/src を独立には検査していない
- Proposed fix: 設計と実装どちらが should-be か user 確認が必要 (verify 仕様の解釈に関わる). 設計書が正なら `md_ast_visitor.extract_document` に images を追加し QL1 で検査 + `test_fail_md_image_alt_missing` を追加。実装が正 (QC1 が網羅する前提) なら設計書 §3-2 の node table から MD image を削除

**[Medium] literalinclude split を test 側でも明示**
- Description: 実装コメント (`verify.py:1046-1047`) のみで、test 側には「QL1 では literalinclude を検査しない — QC1 の管轄」を示すテストがない。設計意図を test が守る形にしたい
- Proposed fix: `test_pass_rst_literalinclude_body_not_checked_by_ql1` を追加 — literalinclude の本体テキストが JSON に無くても QL1 は PASS、QC1 が検知する別テストへリンク

**[Medium] `build_label_map` 経由の cross-document ref を E2E 的にカバー**
- Description: 既存の `test_pass_rst_ref_plain_label_resolved` は label_map を手書き dict で渡しており、実際の `build_label_map` との整合は取れていない
- Proposed fix: 2 ファイル fixture (`tests/ut/fixtures/` 配下) を用意し、`build_label_map` → `check_source_links` の経路を 1 本 E2E で通す

**[Low] `_has_visible_text` の単体テスト**
- Description: RST inline 構文剥がし regex が複数あり、壊れやすい
- Proposed fix: `TestHasVisibleText` を新設し `[1]_` / `:ref:\`x\`` / `\`foo\`_` / 通常テキスト / 空文字 / CJK の 6 ケース

---

**Files cited**:
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/verify/verify.py:954-1086`
- `/home/tie303177/work/nabledge/work2/tools/rbkc/tests/ut/test_verify.py:693-759`
- `/home/tie303177/work/nabledge/work2/tools/rbkc/docs/rbkc-verify-quality-design.md` §3-2
- `/home/tie303177/work/nabledge/work2/tools/rbkc/scripts/common/rst_ast.py`, `md_ast.py`, `md_ast_visitor.py`, `labels.py`
