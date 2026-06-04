# Diff Check — PR #365 (Issue #363)

**Date**: 2026-06-04 (updated 2026-06-04)
**Branch**: 363-javadoc-knowledge vs main

## Summary

全 4720 ファイル変更（想定外: 0件）。全バージョン verify FAIL=0（Task 6-A で QO3 false positive 修正済み）。

---

## 変更カテゴリ別件数

| カテゴリ | 件数 | 根拠 |
|---------|------|------|
| knowledge JSON 既存更新（javadoc リンク追加） | 2554 | v6 315, v5 400, v1.4 352, v1.3 231, v1.2 229（RBKC create 出力カウント） |
| knowledge JSON javadoc 新規（v6） | 582 | `ls knowledge/javadoc/*.json \| wc -l` = 582 |
| knowledge JSON javadoc 新規（v5） | 595 | `ls knowledge/javadoc/*.json \| wc -l` = 595 |
| docs MD javadoc 新規（v6） | 582 | `ls docs/javadoc/*.md \| wc -l` = 582（JSON と 1:1 対応、missing 0件確認済み） |
| docs MD javadoc 新規（v5） | 595 | `ls docs/javadoc/*.md \| wc -l` = 595（JSON と 1:1 対応、missing 0件確認済み） |
| index.toon 削除（v1.2/v1.3/v1.4） | 3 | git log で delete mode 確認済み（v6 は main 時点から不在） |
| workflows/semantic-search.md（v6/v5） | 2 | Step 3b Javadoc 拡張追加 |
| tools/rbkc/scripts/（実装） | 12 | javadoc.py/linkfmt.py/verify.py 等 |
| tools/rbkc/tests/ut/（テスト） | 9 | test_javadoc.py/test_verify.py 等 |
| tools/rbkc/lib/（jar） | 1 | source-to-document-converter-0.0.1.jar |
| tools/benchmark/（Task 4/5 成果物） | ~350 | scenarios/qa.json + run-1〜3 結果 |
| .work/00363/（作業ログ） | 4 | notes.md/tasks.md/verify-baseline.md/diff-check.md |

---

## 想定外変更

なし。

---

## verify 実行結果（最終）

| バージョン | FAIL 件数 | 内容 |
|-----------|-----------|------|
| v6 | 0 | All OK（Task 6-A で QO3 false positive 修正済み） |
| v5 | 0 | All OK（Task 6-A で QO3 false positive 修正済み） |
| v1.4 | 0 | All OK |
| v1.3 | 0 | All OK |
| v1.2 | 0 | All OK |

**QO3 対処（Task 6-A 完了）**:
- `docs/javadoc/` を QO3 のページ数カウントから除外する false positive fix を実装
- verify は `docs/javadoc/` 配下をカウント対象外とするよう修正（`85cc4aa00`）
- 全バージョン FAIL=0 確認済み（2026-06-04）

---

---

## knowledge JSON → Javadoc JSON リンク整合性

knowledge JSON に埋め込まれたリンク形式: `[DisplayText](../javadoc/javadoc-{FQCN}.json)`

**確認済み（全件スキャン）:**
- v6: リンク先 `.json` が全件 `knowledge/javadoc/` に存在 → broken link 0件
- v5: リンク先 `.json` が全件 `knowledge/javadoc/` に存在 → broken link 0件
- 確認スクリプト: `scripts/verify.py` の QL1 チェック（`rbkc.sh verify` で自動確認）

---

## docs MD（解説書ページ）からの Javadoc MD 遷移

docs MD に対応する Javadoc MD の存在:
- v6: `knowledge/javadoc/*.json` 582件 ↔ `docs/javadoc/*.md` 582件（missing 0件確認済み）
- v5: `knowledge/javadoc/*.json` 595件 ↔ `docs/javadoc/*.md` 595件（missing 0件確認済み）
- 確認方法: `set(json names) - set(md names)` = 空集合

docs MD からの実遷移は Claude Code が `docs/javadoc/` を MCP でブラウズする形になるため、
ファイルの存在確認が遷移可能性の保証となる。

---

## 備考

- v1.x に javadoc ファイルはない。Issue #363 の success criteria「all 5 versions」は v1.x も対象だが、v1.x の RBKC が javadoc 生成に対応していない。→ Task 6 確認事項として記録
- verify は RBKC 実装から独立して動作（`_build_javadoc_map()` が `knowledge/javadoc/` 配下を直接走査）
