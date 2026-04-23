# QC1 完全性 — 独立 QA レビュー (Z-1 r3)

**対象**: RBKC verify QC1 (削除手順 → 手順 3: 残存判定 no-tolerance / §3-1b zero-exception)

**評価日**: 2026-04-23

**Bias-avoidance**: 本レビューは spec (`tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 / §3-1b) を唯一の正とし、実装のコメント主張は一次証拠としない。

---

## 1. 実装

### 1.1 spec §3-1 手順 0–3 の準拠

| spec 要件 | 実装 | 評価 |
| --- | --- | --- |
| 手順 0: docutils AST 経由で原文を正規化 | `verify.py:405-413` → `rst_normaliser.normalise_rst` | ✅ |
| 手順 0: AST / node→MD 対応表は共通モジュール | `scripts/common/rst_ast_visitor.py` / `md_ast_visitor.py` | ✅ |
| 手順 1: 抽出順 (top title → top content → sections[i] title → content) | `verify.py:_build_rst_search_units` 637-655 / `_check_md_content_completeness` 789-802 | ✅ |
| 手順 2: 削除位置記録 + 逆行検出 | `verify.py:719-738` (RST) / `814-833` (MD) | ✅ |
| 手順 3 残存チェック: 空白・改行・タブ**以外**の残存は QC1 FAIL | `verify.py:754-756` (RST) / `855-859` (MD) | ✅ |
| 手順 3 許容リストを**設けない** (no-tolerance) | `_is_rst_syntax_line` 等は**定義のみで未参照** | ⚠️ dead code 残置 |

### 1.2 §3-1b zero-exception

| 要件 | 実装 | 評価 |
| --- | --- | --- |
| 未登録 node → FAIL | `rst_ast_visitor.py:146-147, 560-561` `raise UnknownNodeError` | ✅ |
| 未登録 role → FAIL | `rst_ast_visitor.py:586` `raise UnknownRoleError` | ✅ |
| 未解決 reference/substitution → FAIL | `rst_ast_visitor.py:599-655` `raise UnresolvedReferenceError` | ✅ |
| docutils parse error (level≥3) → FAIL | `rst_ast_visitor.py:161` `raise VisitorError(f"RST parse error (level={level})")` | ✅ |
| silent fallback 禁止 | verify の callsite は **両方 `strict_unknown=True`** (`verify.py:413, 774`) | ✅ |
| 未登録 MD token → FAIL | `md_ast_visitor.py:219-220, 462-463` `raise UnknownTokenError` | ✅ |

**silent fallback の残存チェック**: `grep -n "strict_unknown=False"` — 0 件 (verify パスでは使用されない)。create/verify 両方とも strict。

### 1.3 気になる点 (High/Medium)

- ⚠️ **[Medium] dead code**: `verify.py:416-608` に `_normalize_md_unit` / `_strip_md_to_plain_lines` / `_is_rst_syntax_line` / `_is_md_syntax_line` / `_RST_STRUCTURAL_DIRECTIVES` が定義されているが、どこからも呼ばれていない (`grep` で確認済み、テストからも未参照)。旧「許容構文要素リスト」時代の遺物。存在自体が no-tolerance 原則と矛盾するように読め、将来誰かが再利用すると spec 違反を導入する risk がある。
- ⚠️ **[Medium] RST 残存パスでの URL strip (`verify.py:700-706`)**: 正規化後に `![alt](url)` / `[text](url)` を再度置換している。現在は JSON 側 (`_build_rst_search_units._norm`) と**対称**なので QC1 を弱めない。ただし「Visitor が揃えた MD 記法を後工程で再加工」しているため、将来片方だけ変更されるとドリフト発生。spec §3-1 は「Visitor で揃える」方針なので、この再加工は Visitor 側に吸収すべき。
- ⚠️ **[Low] 画像 QC1 穴**: `_norm` で `![alt](url)` は空文字に置換 (verify.py:632)。JSON で alt が欠落しても QC1 で検出不能 (QL1 でカバーしているのが前提)。spec §3-2 と組み合わせで整合しているが、「QC1 単独では画像 alt の欠落を見逃す」点は明示的に認識すべき。

---

## 2. テストカバレッジ

### 2.1 対応状況 (`tests/ut/test_verify.py` `TestCheckContentCompleteness`)

| spec パス | テストケース | 評価 |
| --- | --- | --- |
| QC1 残存 (RST) | `test_fail_qc1_residual_content` (L805) | ✅ |
| QC1 残存 (MD) — JSON 側の非網羅 | `test_pass_md_heading_captured_as_title` (L826, PASS のみ) | ⚠️ FAIL ケース不足 |
| QC1 未登録 RST role → FAIL | `test_fail_qc1_rst_unknown_role_surfaces` (L979) | ✅ (spec 由来) |
| QC1 未登録 MD token → FAIL | `test_fail_qc1_md_unknown_token_surfaces` (L955) monkeypatch 注入 | ⚠️ 軽度 circular |
| QC1 未解決 substitution (`\|undef\|`) → FAIL | **未実装** | ❌ |
| QC1 未解決 `:ref:` (label 無し) → FAIL | **未実装** (PASS 系は L880/896 あり) | ❌ |
| QC1 未登録 RST node → FAIL | **未実装** (role のみ) | ❌ |
| QC1 docutils parse error (level≥3) → FAIL | **未実装** | ❌ |
| QC1 空ソース | **未実装** (`test_pass_empty_data_no_issues` は JSON 側) | ❌ |
| QC1 whitespace-only ソース | **未実装** | ❌ |
| QC1 CJK 境界残存 | 近傍のみ (`test_fail_qc2_near_miss_one_char_differs` は QC2) | ⚠️ |
| QC1 residue truncation (80 字超) | **未実装** | ❌ |

### 2.2 Excel 側

| spec パス | テスト | 評価 |
| --- | --- | --- |
| Excel QC1 欠落 | `test_fail_cell_missing_from_json` (L1094) | ✅ |
| Excel QC1 1 文字欠落 | カバー範囲内 (`test_fail_qc2_one_char_fabrication_detected` の対と対称) | ✅ |
| **`.xls` (xlrd) 経路** | **未実装** (全ケースが `.xlsx`) | ❌ |
| 空セル値 (whitespace-only cell) | **未実装** | ❌ |

### 2.3 circular test 判定

- 🟡 **`test_pass_rst_syntax_in_residual_allowed` (L814)**: JSON content として `"本文。\n\n> **Note:**\n> 注記内容。"` を与え、PASS を期待。これは**ソース仕様**でなく**Visitor の現在の admonition 出力**に合わせた期待値。Visitor が `> **注:** ...` に変わると、期待値も同じ方向に変わるまで detection fail する。spec §3-1 の「Visitor と JSON 側 MD を揃える」原則上はテストとしては「現在の約束ごと」の固定でしかない → **軽度 circular**。
- 🟡 **`test_fail_qc1_md_unknown_token_surfaces` (L955)**: `md_ast.parse` を monkeypatch し人工的な unknown token を注入。実装の strict 経路を確認するテストとしては有効だが、source-format-derived ではない (実在の MD 記法から unknown token が出る例を持っていない)。circular ではないが「実装 hook の存在確認」の域。
- 🟢 `test_fail_qc1_rst_unknown_role_surfaces` (L979): 実在する「未登録 role」から駆動 → spec-driven で OK。
- 🟢 `test_fail_qc1_residual_content` (L805): ソースに情報があり JSON に無い、という素直な FAIL 構成 → OK。

---

## 3. v6 実行

```
cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
→ 0
```

```
cd tools/rbkc && bash rbkc.sh verify 6 | tail -3
→ All files verified OK
```

```
python3 -m pytest tests/ 2>&1 | tail -3
→ 197 passed in 3.94s
```

**解釈**: v6 FAIL 0 + 全 unit test GREEN。ただし bias-avoidance 原則 (§4 末尾) に従い、**v6 PASS は弱い証拠**。具体的には:

- v6 データは本番ソース。現状の Visitor 対応表で取りこぼし無く正規化できるケースが集まっている (それ自体は良いが、今後ソースに新記法が追加された際の fault injection テストが薄い)
- ↑ 2.1 で挙げた 6 件の ❌ (未解決 substitution/ref, 未登録 node, parse error level≥3, 空ソース, whitespace-only, `.xls` 経路) は v6 ランでは踏まれないため、v6 GREEN ≠ 保護範囲

---

## 4. 総合判定

**⚠️ (改善が必要 — critical ではない)**

- 実装本体 (§3-1 手順 0–3 / §3-1b zero-exception) は **spec に準拠**。silent fallback は verify 経路に存在しない。verify は create と両方向に無依存。
- unit test カバレッジに **spec-derived な抜け穴が 6 件**存在 (未解決 substitution, 未解決 `:ref:`, 未登録 RST node, parse error 深刻度, 空/whitespace ソース, `.xls` 経路)。いずれも §3-1b の zero-exception 原則が正しく働くかを固定するテストであり、「verify が spec 要件を満たしている」と宣言するには不足。
- 1 件軽度 circular test (`test_pass_rst_syntax_in_residual_allowed`) と 1 件 hook-confirmation test (`test_fail_qc1_md_unknown_token_surfaces`) は置き換えまたは補強が望ましい。
- dead code (L416-608) は no-tolerance 原則の誤読を誘発する risk。削除すべき。

Z-1 r3 段階では **✅ 付与は時期尚早**。上記テスト追加と dead code 除去を終えるまでは ⚠️ 維持が spec §4 末尾注の bias-avoidance 規定に合致する。

---

## 5. 改善案

### [High] テスト追加 (spec-derived, RED→GREEN TDD で固定)

1. **未解決 substitution → QC1 FAIL**: `|undef|` を本文に含み `substitution_definition` を与えないソースで `UnknownSyntaxError` 経由の `[QC1] RST parse/visitor error` が出ること
2. **未解決 `:ref:` (bare label, label_map 未提供) → QC1 FAIL**: content completeness 経路で `[QC1] RST parse/visitor error: unresolved :ref:` が出ること (現在は QL1 側 L1218 で skip PASS のみ)
3. **未登録 RST node → QC1 FAIL**: `nodes.document` に docutils が通常出さない合成 node を足して `UnknownNodeError` → `[QC1]` を確認 (monkey-patch で doctree を差し替え)
4. **docutils parse error (level≥3) → QC1 FAIL**: 破壊された RST (例: 未閉鎖の grid table) で `rst_ast_visitor.py:161` の `VisitorError` 経路が発火すること
5. **空 / whitespace-only ソース**: 正規化残存が空なら QC1 PASS (JSON 側も空) / JSON に内容がある場合は QC2 — 両分岐を明示
6. **`.xls` 経路**: xlrd ブランチ (`_xlsx_source_tokens` L882-892) をカバーする小さな `.xls` を `tmp_path` で生成 (困難なら最小バイナリ固定ファイルを `tests/ut/fixtures/` に置く)
7. **residue truncation 80 字**: 長大 residue が切り捨て付きでレポートされること (実装 `snippet[:80]`)

### [Medium] circular test 解消

- `test_pass_rst_syntax_in_residual_allowed` (L814): 期待値を「Visitor が今こう出す」ではなく「ソースの情報量が JSON に保存されている」仕様で書き直す (例: JSON content に "注記内容。" が含まれていることを assert し、admonition 記号の形は問わない)。
- `test_fail_qc1_md_unknown_token_surfaces`: 可能なら monkey-patch ではなく、markdown-it-py が実際に未登録として扱う記法 (custom container 等) を入力としてドライブ。

### [Medium] dead code 除去

- `verify.py:416-608` の 5 要素 (`_normalize_md_unit`, `_strip_md_to_plain_lines`, `_is_rst_syntax_line`, `_is_md_syntax_line`, `_RST_STRUCTURAL_DIRECTIVES`) を削除。旧許容リスト実装の残骸で、no-tolerance 原則と矛盾する読み取りを生む。

### [Low] 残存 URL strip の移動

- `verify.py:700-706` の再加工 (`![..](..)` / `[..](..)` strip) は Visitor 側 (`rst_ast_visitor.to_flat_md` 相当) で完了させるべき。現状は対称なので FAIL は起きないが、将来のドリフト耐性を損なう。

---

## 付記: 独立性原則 (§2-2)

- `scripts/verify/verify.py` は `scripts/common/*` のみを参照 (`grep -n "from scripts" verify.py` → labels / rst_ast / rst_normaliser / md_ast / md_ast_visitor / md_normaliser)。create 側 (`scripts/create/`) への import 無し — OK。
