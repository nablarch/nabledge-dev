# Z-1 三次 QA レビュー (r3) サマリー

**目的**: r2 critical 5 件 + circular test 5 件の修正後、bias-avoidance 明示で再検証。

---

## 判定表 (r2 → r3)

| ID | r1 | r2 | r3 | 主な残 gap |
|---|---|---|---|---|
| QC1 | ⚠️ | ⚠️ | **⚠️** | spec-derived test 未実装 7 件 (未解決 substitution / :ref: / 未登録 node / parse error level≥3 / 空 / `.xls` / truncation)、dead code 残留 |
| QC2 | ⚠️ | ❌ real bug | **⚠️** | r2 H1 (1 文字 drop) 解消 ✅、**`.xls` 完全未テスト** 残 |
| QC3 | ⚠️ | ⚠️ | **⚠️** | r2 High 2 件 (短 CJK PASS / top×section 重複) **未対応** + OR assert circular smell |
| QC4 | ⚠️ | ⚠️ | **❌** | QC3/QC4 境界 / 3 section cascade / MD content swap テスト必須 |
| QC5 | ⚠️ | ⚠️ | **⚠️** | self-closing tag 解消 ✅、MD inline-code 内の `<br>`/`\*` false positive + directive regex 過剰 |
| QL1 | ⚠️ | ⚠️ | **❌** | **High: named ref テストが monkey-patch circular (実 docutils 未検証) / MD 非外部リンク判定緩すぎ (mailto/tel/# 等)** |
| QL2 | ⚠️ | ✅ | **⚠️** | 軽度 circular (parens URL 期待値が AST 出力ミラー) + RST bare URL テスト欠 |
| QO1 | ✅ | ⚠️ | **⚠️** | 重複 H2 greedy 突破 / extra H2 が sections 非空時未検出 / `_H2_RE` が h4+ も受入 |
| QO2 | ⚠️ | ❌ | **❌** | **High: top-level content の `#` 見出し直下チェック未実装 (spec §3-3 line 290)** + Medium circular 1 |
| QO3 | ⚠️ | ✅ | **⚠️** | loose assert + `N ページ` 無し silent PASS |
| QO4 | ⚠️ | ⚠️ | **✅ 条件付き** | r2 High 解消、Medium 3 件 (index.toon parser 頑健性) のみ |

---

## 🔴 r3 新規または未解消の critical

### 未解消 (r2 → r3 で手付かず)
- **QC3**: 短 CJK PASS + top×section 重複テスト (r2 指摘)
- **QC2**: `.xls` 経路の unit test (r2 指摘、v1.2/1.3 展開でブロッカー)

### r3 新規発見
- **QC4 ❌**: QC3/QC4 境界で `_in_consumed` ブランチが条件反転しても silent に通る
- **QO2 High**: top-level content の**位置** (`#` 見出しと最初の `##` の間) 未チェック。`verify.py:130-134` が単純 substring で、spec §3-3 line 290 「`#` 見出し直下」違反
- **QL1 High**: 
  - `test_fail_rst_named_reference_target_title_missing` (test_verify.py:1321-1357) が `rst_ast.parse` を monkey-patch して手製 doctree を返す → 実 docutils パーサの `.. _label:` + `` `Text`_ `` 挙動が一度もテストされていない = **r2 で指摘した circular の形を変えただけ**
  - `md_ast_visitor.py:410-413` 内部リンク判定が「http/https 以外すべて」→ `mailto:` / `tel:` / `#anchor` / 空 href まで QL1 対象になり spurious FAIL / noise の原因
- **QC1 Medium**: dead code 残留 (`_normalize_md_unit` / `_strip_md_to_plain_lines` / `_RST_STRUCTURAL_DIRECTIVES` 等、no-tolerance 原則採用後の旧許容リスト遺物)

---

## 🟡 合計 circular / 緩度テスト

- QL1 named ref (r3 新規発見): monkey-patch circular
- QL2 parens URL (Medium): 期待値を AST 出力から derive
- QC3 OR assert: spec 文字列と実装文字列の OR で緩い
- QC1 admonition PASS テスト: JSON 期待値を Visitor 出力に合わせている

---

## 判定

**✅ 条件付き合格は QO4 のみ** (1/11)。

**❌ 2 件、⚠️ 8 件**。全観点 ✅ までにはさらに 1 ラウンドの修正が必要。

---

## 対応方針案

### 方針 A: r3 gap を潰して r4 レビュー

1. **QL1**: 
   - named ref テストを実 RST ソースベースに書き直し (構造的に label + text が doctree で refname 付き reference になるケースを見つける)
   - MD 内部リンク判定に `mailto:` / `tel:` / `#` / 空 href を除外
2. **QO2**: top-level content 位置チェック追加 (`#` と最初の `##` の間に含むか)
3. **QC4**: QC3/QC4 境界 + 3-section cascade + MD content swap テスト
4. **QC3**: 短 CJK PASS + top×section 重複 (r2 未対応分)
5. **QC2**: `.xls` 経路 unit test 追加 (`xlrd` 経路)
6. **QC1**: 未解決 reference/substitution / 未登録 node / parse error level≥3 / 空 / .xls / truncation の unit test 追加、dead code 削除
7. **QC5**: MD inline-code false positive / directive regex 厳格化
8. **QO1**: 重複 H2 順序チェック / extra H2 検出 / `_H2_RE` を `##`/`###` に
9. **QO3**: assert 厳格化 / `N ページ` 無し時の挙動明記
10. **QL2**: parens URL 期待値を hard-code / RST bare URL テスト追加
11. **QO4**: index.toon parser 頑健性 (header validation / row count / path with comma)

作業量: テスト追加 ~25 件 + 実装修正 ~5 件

### 方針 B: 今回 PR でできる範囲でマージ + 残 gap を別 Issue 化

r2 で「全 critical 潰す」と合意したので、方針 A が妥当。

詳細: `.work/00299/review-z1-r3/{QC1..QO4}.md`
