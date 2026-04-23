# QO2 docs MD 本文整合性 — QA Review

**Target**: QO2 — JSON の `content`(top-level / sections) が docs MD に完全一致で含まれることの検証
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 "QO2 本文整合性"
**Scope**: RST / MD / Excel (フォーマット非依存、JSON×docs MD のテキスト照合のみ)

---

## 1. 実装の有無 ✅

**Location**: `tools/rbkc/scripts/verify/verify.py:50-100` `check_json_docs_md_consistency()`

- **Top-level content verbatim**: `verify.py:86-89`
  - `top_content = data.get("content","")` を取得し、`assets/` を含まない場合のみ `top_content not in docs_md_text` を判定 → FAIL メッセージ `[QO2] {file_id}: top-level content not found verbatim in docs MD`
- **Section content verbatim**: `verify.py:91-98`
  - 各 `sections[*].content` を走査し、`assets/` を含まない場合に `content not in docs_md_text` を判定 → FAIL メッセージ `[QO2] {file_id}: section '{title}' content not found verbatim in docs MD`
- **Assets スキップ**: 画像/添付パスが docs MD 側で `../assets/` へ書き換えられる仕様（docs.py）に合わせ、`assets/` を含む content は照合対象外 (`verify.py:87, 95`)

判定: **Top-level / section の両方とも実装済み**。Spec §3-3 の要件をカバーしている。

---

## 2. ユニットテストのカバレッジ ⚠️

**Location**: `tests/ut/test_verify.py:82-127` `TestCheckJsonDocsMdConsistency_QO2`

| # | 必須観点 | テスト | 判定 |
|---|----------|--------|------|
| 1 | section content がずれている (FAIL) | `test_fail_section_content_missing` (L109-117) | ✅ |
| 2 | section content が丸ごと欠落 (FAIL) | `test_fail_section_content_missing` が兼用 | ✅ |
| 3 | top-level content が docs MD に無い (FAIL) | `test_fail_top_content_missing` (L94-98) | ✅ |
| 4 | top-level content の正常系 (PASS) | `test_pass_top_content_in_docs` (L89-92) | ✅ |
| 5 | section content の正常系 (PASS) | `test_pass_section_content_in_docs` (L100-107) | ✅ |
| 6 | assets/ を含む content のスキップ (PASS) | `test_pass_assets_section_skipped` (L119-127) | ✅ |
| 7 | 空白のみ差分 (半角/全角スペース、改行、末尾空白) — strict 一致なら FAIL | **欠落** | ❌ |
| 8 | CJK content（全角・多バイト）での pass/fail | 部分的 (正常系のみ L91 で「トップレベル本文。」) | ⚠️ |
| 9 | コードブロック/fenced (` ``` ` を含む content) | **欠落** | ❌ |
| 10| Markdown 特殊文字 (`*`, `_`, `[`, `` ` ``, `<`) を含む content | **欠落** | ❌ |
| 11| `no_knowledge_content: true` の早期スキップ | `TestCheckJsonDocsMdConsistency_QO1` 側で `test_pass_no_knowledge_content` にて共通関数として検証済 | ✅ (共通) |
| 12| top-level content が空文字のときに誤検知しない | 間接的に L100-107 で空 `content: ""` を与えており OK | ✅ |
| 13| content 内に docs MD の前後空白込みで一致 (例: 末尾改行の扱い) | **欠落** | ❌ |
| 14| Multiple sections (順序影響なしで全部 verbatim) | **欠落**（正常系は 1 section のみ） | ⚠️ |

**欠落観点の要約**:
- **Whitespace-only diff**: 「完全一致」が strict (Python `in` 演算子) であることの保護テストがない。将来「tolerant 一致」へ差し替わってもテストが素通りする
- **コードブロック・Markdown 特殊文字**: docs.py の変換が特殊文字をエスケープする場合に verbatim 一致が崩れる現実的リスクあり
- **複数セクション**: 現行実装は section 順序を考慮せず `in` で素直に探すため、順序不問を担保するテストが欲しい

---

## 3. v6 verify 実行結果 ✅

```
$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | tail -3
All files verified OK

$ grep -c "^FAIL" /tmp/verify6.log
0

$ python3 -m pytest tests/ 2>&1 | tail -3
tests/ut/test_verify.py ................................................ [ 76%]
tests/ut/test_xlsx_converters.py ......                                  [100%]
============================= 138 passed in 4.29s ==============================
```

- v6 verify: **0 FAIL** (All files verified OK)
- Unit tests: **138 passed, 0 failed**

---

## 4. 総合判定 ⚠️ (Good but improvable)

| 条件 | 結果 |
|------|------|
| 1. 実装の有無 (top-level + section 両方) | ✅ |
| 2. Unit tests カバレッジ | ⚠️ (基本 6 ケース完備、エッジケース 4 種が欠落) |
| 3. v6 verify 0 FAIL + unit tests pass | ✅ |

**結論**: QO2 の**コア機能は正しく実装・動作し、v6 での品質ゲートとして機能している**。ただしゼロトレランス基準に照らすと、ユニットテストは「完全一致」が将来弱められないことを守る保護テストが不足している。

---

## 5. 改善案 (QA Engineer 提案)

**[High] whitespace-only diff の FAIL を固定化するテスト追加**
- 説明: 現状「完全一致」は Python `in` による strict だが、これを保護するテストが無い。将来 `strip()` や正規化が入っても気付けない
- 提案修正: `test_fail_whitespace_only_diff` を追加。例: JSON `content="概要の説明。"`, docs に `"概要の説明。 "` (末尾全角スペース) → FAIL を assert

**[High] コードブロック / fenced content のテスト追加**
- 説明: 知識ファイルはコード例を含み、docs.py 変換で ` ``` ` やインデントの扱いが崩れると本番で QO2 FAIL する。リグレッション保護が必要
- 提案修正: `test_pass_code_block_verbatim` と `test_fail_code_block_indent_changed` を追加

**[Medium] Markdown 特殊文字を含む content のテスト追加**
- 説明: `*`, `_`, `[text](url)`, バックティックを含む content が、docs MD でエスケープや変換されると一致しなくなる
- 提案修正: `test_pass_markdown_special_chars` を 1 ケース追加（実運用で頻出する `n:xxx` タグや `@Annotation` 表記を含むもの）

**[Medium] 複数セクション網羅性のテスト追加**
- 説明: 現行の正常系は 1 section のみ。複数 sections のうち一部だけが FAIL する混在ケースを担保したい
- 提案修正: `test_fail_only_one_of_many_sections_mismatch` を追加（3 section のうち 2 番目だけずれる → その section 名のみが issues に出ることを assert）

**[Low] top-level content が空文字の明示テスト**
- 説明: `top_content and ...` のガード (L87) が落ちないことを明示的に守るテスト
- 提案修正: `test_pass_empty_top_content_skipped` を追加

いずれもコード変更を伴わず、TDD でテスト追加のみで実施可能 (RBKC 本体は現状で Spec を満たしている)。
