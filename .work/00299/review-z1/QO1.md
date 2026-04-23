# QO1 docs MD 構造整合性 — QA Review

## 1. 実装の有無

✅ 実装あり。

- `tools/rbkc/scripts/verify/verify.py:50` `check_json_docs_md_consistency(data, docs_md_text)` で QO1+QO2 を統合実装。
- QO1 該当箇所:
  - `verify.py:46-47` H1/H2 正規表現 (`_H1_RE`, `_H2_RE`)
  - `verify.py:62-65` タイトル整合 (JSON `title` == docs MD `#` heading)
  - `verify.py:68-84` セクションタイトルの存在・順序チェック (inorder 走査)
  - `verify.py:71-72` `sections=[]` かつ docs MD に `##` がある場合は FAIL
- `no_knowledge_content` スキップは `verify.py:52-53` で対応。

Spec (`tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3) の QO1 三要素 (タイトル一致/セクションタイトル一致/順序一致/空 sections 時の `##` 非出現) を網羅。

**注意点**: `verify.py:47` は `_H2_RE = r'^#{2,}\s+(.+)$'` であり、`##` だけでなく `###`+ も同じリストに入る。Spec は「`##`/`###` に存在」と記述しているので設計意図とは整合。ただし H2 と H3 を区別せずフラット走査するため、「H3 を H2 として扱う」誤検出耐性は検証テストで担保されていない (下記改善案参照)。

## 2. ユニットテストのカバレッジ

`tests/ut/test_verify.py:15` `TestCheckJsonDocsMdConsistency_QO1` に 7 テスト。

| ケース | テスト | 判定 |
|---|---|---|
| title mismatch → FAIL | `test_fail_title_mismatch` (L32) | ✅ |
| section title mismatch → FAIL | `test_fail_section_title_missing` (L38) | ✅ |
| section title order swap → FAIL | `test_fail_section_order_reversed` (L48) | ✅ |
| JSON に section あり・docs MD にはなし | `test_fail_section_title_missing` 内包 | ✅ |
| docs MD `##` あり・JSON `sections=[]` → FAIL | `test_fail_extra_h2_in_docs_md` (L70) | ✅ |
| title+sections 完全一致 → PASS | `test_pass_title_and_sections_match` (L22) | ✅ |
| `sections=[]` + `##` なし → PASS | `test_pass_no_sections_no_h2` (L64) | ✅ |
| `no_knowledge_content` スキップ | `test_pass_no_knowledge_content_skipped` (L60) | ✅ |
| **`#` heading 完全欠落** | なし | ⚠️ |
| **空 title (JSON `title=""`) エッジケース** | なし | ⚠️ |
| **CJK + 特殊文字 (括弧/コロン等)** | なし (CJK は通常タイトル `タイトル` のみ、特殊文字未検証) | ⚠️ |
| **複数 `#` 見出し** (`_H1_RE.search` は最初の 1 件のみ採用) | なし | ⚠️ |
| H3 のみの docs を `sections` ありの JSON と比較した場合の挙動 | なし | ⚠️ |

総合テスト結果:
```
138 passed in 2.80s
```
✅ 全テストパス (`cd tools/rbkc && python3 -m pytest tests/`).

## 3. v6 verify 実行結果

```
$ bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0
$ bash rbkc.sh verify 6 2>&1 | tail -3
All files verified OK
```

✅ v6 全ファイル 0 FAIL。QO1 実装が実データでも通っている。

## 4. 総合判定

✅ **合格 (条件付き)**。

- Spec §3-3 QO1 の必須ケース (title/section title/順序/空 sections の扱い) は実装・テスト共に完備。
- v6 本番データで 0 FAIL、ユニットテスト全 138 件パス。
- 一方でエッジケース 4 件 (H1 欠落・空 title・特殊文字・複数 H1) がテストで未検証。現状のロジック (`verify.py:62-65`) を読むと:
  - `#` heading 欠落時: `docs_title=""`, `json_title` が非空なら mismatch で FAIL 検出される (ロジック的には OK だが回帰防止テストなし)。
  - `json_title=""`: L64 の `if json_title and ...` ガードにより検出スキップ (意図的か要確認)。
  - 複数 `#`: `_H1_RE.search` が最初のマッチのみ採用。2 つ目以降の H1 と JSON タイトルの不一致は検出不可。
- ゼロトレランス原則に照らすと、上記 4 件はテストで固定化すべき。実害は現 v6 データでは表面化していないが、将来のリグレッション対策として不足。

## 5. 改善案

**[Medium] エッジケーステスト 4 件追加** (ゼロトレランス / 回帰防止)
- 対応: `TestCheckJsonDocsMdConsistency_QO1` に以下を追加
  - `test_fail_h1_heading_missing`: docs MD に `#` が一切ない → title mismatch FAIL を期待
  - `test_behavior_empty_json_title`: `json_title=""` の時にスキップされることを明示テスト (仕様を固定)
  - `test_pass_cjk_title_with_special_chars`: `"設定ファイル（nablarch.xml）: 概要"` のようなタイトルで通ること
  - `test_fail_multiple_h1_first_matches`: docs MD に `#` が 2 つある場合、最初が JSON と一致していれば PASS / 2 つ目のみ一致なら FAIL (現状仕様を固定)

**[Low] H2/H3 区別方針のテスト固定化**
- 対応: JSON `sections` が H2 相当のみを列挙する前提なら、docs MD が H3 だけで構造化されたケース (H2 が無く H3 に JSON section title がある) の期待挙動をテストで明示 (PASS にすべきか FAIL にすべきかは RBKC 設計次第)。設計で PASS とするなら現行 `_H2_RE` で良いが、テスト欠如は解釈の揺れを残す。

**[Low] 空 `json_title` のガード仕様をドキュメント化**
- 対応: `verify.py:64` の `if json_title` ガードについて、`rbkc-verify-quality-design.md` §3-3 に「JSON `title` が空文字の場合は QO1 をスキップする」旨を明記。もしくは JSON 側で `title` 必須制約とし、RBKC 出力時点で空 title を不可とする。現状は暗黙のゆるい仕様。

いずれも現 v6 出力に対する FAIL は発生しないため、コード/テスト追加のみで verify を弱めるリスクはない。
