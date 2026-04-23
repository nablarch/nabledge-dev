# QC1 完全性 レビュー (Z1-R5)

**Reviewer**: QA Engineer (independent context, bias-avoidance)
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 + §3-1b
**Date**: 2026-04-23

Bias-avoidance 原則: spec を authoritative とし、v6 PASS は弱い証拠としてのみ扱う。circular test (実装自身を期待値として参照するテスト) を重点的に確認する。

---

## 1. 実装評価

### spec 要求と実装の一致

| spec 要求 | 実装箇所 | 判定 |
| --- | --- | --- |
| docutils parse error (level ≥ 3) → QC1 FAIL | `scripts/common/rst_normaliser.py:58-61` — warning stream を scan し `(ERROR/3)` / `(SEVERE/4)` で `UnknownSyntaxError` raise | ✅ |
| 未登録 node → FAIL, silent fallback 禁止 | `scripts/common/rst_ast_visitor.py:147` (`raise UnknownNodeError("unmapped node: ...")`) / `:561` (inline) / `:449` (image without uri/alt) | ✅ |
| 未登録 role → FAIL | `rst_ast_visitor.py:586` (`raise UnknownRoleError`) | ✅ |
| 未解決 reference / substitution → FAIL | `rst_ast_visitor.py:599`, `:603`, `:646`, `:655` (`raise UnresolvedReferenceError`) | ✅ |
| QC1 として verify に伝播 | `scripts/verify/verify.py:543-548` (`except UnknownSyntaxError → [QC1] RST parse/visitor error`) / `:621-627` (md 側) | ✅ |
| 残存判定 no-tolerance (空白・改行以外の残存は FAIL) | `verify.py:595-606` — 許容リストなし、単純に `residue.strip()` | ✅ |
| JSON 側 MD と正規化ソースで共通 helper を使う | `rst_normaliser.normalise_rst` → `rst_ast_visitor.extract_document` (create と共通) | ✅ |

### silent fallback の追加検査

`rst_ast_visitor.py` 内の `raise` 呼び出しを全列挙 (line 147/161/449/561/586/599/603/646/655) し、silent な `pass` / `return ""` による迂回がないことを確認した。`strict_unknown=False` 経路 (`rst_normaliser.py:66-68`) は verify の completeness 経路では使われておらず (`verify.py:458` は `strict_unknown=True` を明示)、QC1 ゲートを弱めない。

### 実装判定: ✅

zero-exception 原則が visitor・normaliser・verify 呼び出し元のすべてで一貫して守られている。警告ストリーム scan は docutils が `Undefined substitution referenced` 等を doctree に埋め込まずに stderr だけへ出すケースに対する正しいフォールバックで、spec §3-1b 原則 4 と整合する。

---

## 2. テスト評価

### spec 要求項目 vs 実装済みテスト

| spec 要求項目 | テスト | file:line | 判定 |
| --- | --- | --- | --- |
| unknown MD token → QC1 FAIL | `test_fail_qc1_md_unknown_token_surfaces` | `tests/ut/test_verify.py:1011` | ✅ |
| unresolved substitution → QC1 FAIL | `test_fail_qc1_rst_unresolved_substitution_surfaces` | `:1035` | ✅ |
| parse error level ≥ 3 → QC1 FAIL | `test_fail_qc1_rst_parse_error_level_3` | `:1044` | ✅ |
| unknown role → QC1 FAIL | `test_fail_qc1_rst_unknown_role_surfaces` | `:1053` | ✅ |
| 残存テキストによる QC1 FAIL | `test_fail_qc1_residual_content` | `:861` | ✅ |
| CJK 文字短トークン | `test_pass_qc3_short_cjk_repeated_in_source_and_json` | `:1106` | ⚠ (QC3 観点のみ。QC1 CJK 残存単独テストなし) |
| `.xls` (xlrd) path | `test_pass_xls_cell_in_json` ほか | `:1292`, `:1308`, `:1322`, `:1338` | ✅ |
| 1-char 残存が silently drop されない | `test_fail_xls_qc2_one_char_fabrication_detected` | `:1275` (QC2 方向、Excel) | ⚠ (RST/MD の QC1 1-char 残存を直接覆うテストは無い) |
| empty source | (明示的テストなし) | — | ⚠ 不足 |
| whitespace-only source | (明示的テストなし) | — | ⚠ 不足 |

### circular test (バイアス) 検査

- `test_fail_qc1_md_unknown_token_surfaces` (`:1011`) は `markdown_it.token.Token` を直接構築し、`md_ast_mod.parse` を monkey-patch して未登録 token を注入する。実装側の token 列挙を参照せず、**外部パーサーの token 型のみに依存**しており非 circular。✅
- `test_fail_qc1_rst_unresolved_substitution_surfaces` / `_parse_error_level_3` / `_unknown_role_surfaces` はソース RST をそのまま与え、結果文字列に `[QC1]` および `"RST parse/visitor error"` が含まれることのみを assert。実装の内部構造に依存しない spec-derivable な assertion で非 circular。✅
- `test_pass_rst_syntax_in_residual_allowed` (`:870`) は JSON content として `"> **Note:**\n> 注記内容。"` を期待値とし、これは visitor が note を blockquote MD に変換するという **実装挙動を期待値化** している。spec (§3-1a / converter 設計書) 由来の契約として扱われるならば許容範囲だが、converter 挙動が変わると連動破壊する circular risk がある。⚠
- 他の QC1 PASS テスト群 (`test_pass_rst_field_list_with_*`, `test_pass_rst_comment_*`) も同様に converter 出力形式を期待値化している箇所がある。spec §3-1a で形式が明示されていれば非 circular だが、そうでなければ circular。⚠

### 欠落テスト

1. **empty source** (`source_text=""`) を RST/MD 双方で通した場合の挙動。spec §3-1 手順 0 は empty 入力についての挙動を明言していないが、zero-exception 原則 (no silent fallback) の観点から "異常なく空の正規化を返し QC1 FAIL にならない" 契約を明示テストで固定すべき。
2. **whitespace-only source** (`"   \n\n  \t\n"`)。`test_fail_whitespace_only_diff` (`:239`) は QO2 観点のみで、QC1 completeness 経路を通っていない。
3. **residue truncation boundary**。`verify.py:605` は `residue.strip()[:80]` で短縮するが、長文残存時に "80 字以内なら全残存が同一メッセージに含まれる / 80 字超で truncate" の振る舞いが固定されていない。残存がメッセージから見えなくなる silent loss を防ぐための境界テストが欲しい。
4. **CJK 文字単体の QC1 残存** (短 CJK が JSON に欠落するケース)。QC3 では `:1106` でカバーされているが QC1 単独は無い。

### テスト判定: ✅ (合格、ただし上記 4 件は ⚠ gap)

コア zero-exception 4 経路 (unknown node / unknown role / unresolved ref / parse-level-3) はすべて明示テストがあり、circular ではない。PASS 側テスト (rst_syntax_in_residual / field_list / comment 等) は一部 converter 出力形式に依存するが、spec 側で converter 挙動が契約化されているため致命ではない。empty / whitespace / residue truncation / CJK QC1 の 4 件は将来の回帰防止として追加推奨 (非ブロッカー)。

---

## 3. v6 実行結果

- `bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"` → **0**
- `bash rbkc.sh verify 6 2>&1 | tail -3` → `All files verified OK`
- `python3 -m pytest tests/ 2>&1 | tail -3` → `219 passed in 1.87s`

v6 PASS は弱い証拠 (bias-avoidance 原則)。重要なのは zero-exception ゲートが発動することを単体テストで確認できている点であり、これは満たされている。

---

## 4. 総合判定

### ✅ 合格

**根拠**:
- spec §3-1b の 4 つの zero-exception 経路 (未登録 node / 未登録 role / 未解決 ref / parse error level≥3) すべてに対して、
  - 実装が silent fallback なく raise → QC1 FAIL に伝播する (`rst_ast_visitor.py`, `rst_normaliser.py:58-61`, `verify.py:543-548`)
  - 非 circular な単体テストが存在する (`test_verify.py:1011-1059`)
- 残存判定が no-tolerance (空白のみ許容) で実装され (`verify.py:595-606`)、`test_fail_qc1_residual_content` (`:861`) が回帰を防ぐ
- `strict_unknown=False` 経路が verify content-completeness からは使われず QC1 ゲートを迂回できない
- v6 実データで FAIL 0 件、全 219 unit tests が PASS

**留意**: v6 PASS は弱い証拠として扱う (bias-avoidance)。品質の根拠はあくまで spec-derivable な単体テスト群。

---

## 5. 改善案

### High 優先度

なし (現時点の QC1 完全性ゲートとして spec 要求を満たしている)。

### Medium 優先度

1. **empty / whitespace-only ソーステストの追加**
   - 現状: 明示カバレッジなし
   - 提案: `TestCheckContentCompleteness` に以下を追加
     - `test_pass_empty_source_and_empty_json_no_issues` (`""` + `no_knowledge_content=False` + 空 sections)
     - `test_pass_whitespace_only_source_and_empty_json_no_issues`
     - `test_fail_empty_source_but_json_has_content` (empty source + 非空 JSON → QC2 fabricated 発火確認)
   - 目的: zero-exception 原則に対する境界回帰テスト

2. **residue 切り詰め境界テスト**
   - 現状: `verify.py:605` の `[:80]` 切り詰めに対する明示テストなし
   - 提案: 81-char 残存ケースで "QC1 が発火し、メッセージに先頭 80 字が含まれる" ことを assert
   - 目的: 長文残存が silently 見えなくなる劣化を防ぐ

### Low 優先度

3. **converter 出力形式期待値の spec 引用明示**
   - 現状: `test_pass_rst_syntax_in_residual_allowed` (`:870`) 等が `"> **Note:**\n> 注記内容。"` のような converter 出力文字列を期待値化しており、契約の所在が docstring からは読み取りにくい
   - 提案: 当該テストの docstring に「spec §3-1a note MD 表現」等の参照を追記 (converter 設計書の該当行でもよい)
   - 目的: circular test vs spec-derivable test の区別を明示

4. **QC1 単独の CJK 残存テスト**
   - 現状: QC3 CJK は `:1106` にあるが QC1 CJK 残存単独は無い
   - 提案: 短 CJK (`"主要"` 等) が JSON に取り込まれない場合の QC1 FAIL テスト追加
   - 目的: CJK 境界での false negative 回帰防止

---

## 参考: レビュー範囲内のファイル

- `tools/rbkc/scripts/common/rst_normaliser.py`
- `tools/rbkc/scripts/common/rst_ast_visitor.py`
- `tools/rbkc/scripts/verify/verify.py` (QC1 関連 450-660 行)
- `tools/rbkc/tests/ut/test_verify.py` (`TestCheckContentCompleteness` クラス、特に `:861-1059`)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 + §3-1b
