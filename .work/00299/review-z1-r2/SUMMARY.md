# Z-1 二次 QA レビュー サマリー

**目的**: Z-1 完了宣言 (commit `e3a68e37a`) に対して、**bias-avoidance を明示**した別コンテキスト QA Engineer 11 並列レビュー。

**bias-avoidance 指示**:
- 設計書を真とし、実装に合わせない
- circular test (実装の挙動をテスト期待にしている形) を指摘
- v6 verify PASS は弱い証拠 (fault injection 無しには不十分)
- 「実装が [] を返す」と「チェックが十分」を区別

---

## 総合判定表 (r2)

| ID | 評価 | r1 判定 | r2 判定 | 差分 |
|---|---|---|---|---|
| QC1 | 4/5 ⚠️ | ⚠️ | **⚠️ 条件付き ✅** | Excel silent tolerance (real bug) + circular test 1 |
| QC2 | 3/5 ⚠️ | ⚠️ | **❌ real bug** | **Excel QC2 で 1 文字捏造 silent drop (`verify.py:926 len(t)>=2`)** + .xls 未テスト |
| QC3 | 4/5 ⚠️ | ⚠️ | ⚠️ | High 2 件 (短 CJK 衝突 / top-level-section 重複) + OR assert |
| QC4 | 3/5 ⚠️ | ⚠️ | ⚠️ | QC3/QC4 境界テスト欠如 |
| QC5 | 4/5 ⚠️ | ⚠️ | ⚠️ | **High: `<br/>` / `<hr/>` 自己閉じタグ未検出 regex bug** + circular test 1 |
| QL1 | 3/5 ⚠️ | ⚠️ | ⚠️ | **High: RST named reference (`refid`/`refname` のみ) 未実装** |
| QL2 | 4/5 ✅ | ⚠️ | ✅ 条件付き | High 無し |
| QO1 | 4/5 ⚠️ | ✅ | ⚠️ | circular test (empty title skip) + spec drift (`_H2_RE` が h4+ も受入れ) |
| QO2 | **2/5 ❌** | ⚠️ | **❌ unauthorised weakening** | **`assets/` 含む content を silent skip = verify を弱めている (verify.py:87,95)** + circular test |
| QO3 | 4/5 ✅ | ⚠️ | ✅ 条件付き | circular test 無し、Medium 3 件のみ |
| QO4 | 4/5 ⚠️ | ⚠️ | ⚠️ | circular test (broken JSON silent skip) + silent tolerance |

---

## 🔴 critical findings (Z-1 完了宣言を覆す重大事項)

### 1. QO2: `assets/` 含む content の silent skip (verify.py:87, 95)

- **影響**: JSON content に `"assets/"` という文字列が含まれていれば QO2 全体を skip
- **違反**: 設計書 §3-3 は「完全一致」と明記、§2-2 例外は 1 種類のみ、§5 は「verify を弱める変更」を禁止
- **経緯**: `scripts/create/docs.py` が `assets/...` → `../assets/...` を書き換える都合に verify を合わせたもの
- **対応**: skip を削除し converter 側で対応するか、§5 プロセスで例外を仕様に明記
- **circular test**: `test_pass_assets_section_skipped` (test_verify.py:153) が skip ブランチを pin

### 2. QC2 Excel: 1 文字捏造の silent drop (verify.py:926)

- **現象**: `if t and len(t) >= 2:` で **1 文字の残存を無視**
- **検証**: cell `"A"` + JSON content `"X"` で QC2 発火せず (fault injection で確認済み)
- **違反**: 設計書 §3-1 Excel 節 手順 3 は「空白・空行以外の残存は QC2」

### 3. QL1: RST named reference (`refid`/`refname` のみ) 未実装

- **Spec**: §3-2 table 行 1 「RST reference (`refid` / `refname`, refuri なし)」
- **実装**: `check_source_links` は `:ref:` role 付き inline しか見ず、`nodes.reference` のネイティブ named reference (`.. _usage:` + `` `Usage`_ ``) を無視
- **v6 で露見しない理由**: Sphinx prod では `:ref:` role が支配的

### 4. QC5: self-closing HTML tag 未検出

- **現象**: `_MD_RAW_HTML_RE` が `[\s>]` を要求するため `<br/>` `<hr/>` `<img/>` (スペースなし) が検出されない
- **Fix**: `[\s/>]` に変更

### 5. QC1 Excel: 1 文字残存 silent tolerance (QC2 と同じ箇所)

- **現象**: `verify.py:926` の `len(t) >= 2` 制限により、cell が無くて 1 文字残存した場合も QC1 FAIL しない (※ QC2 と同じ根本原因)

---

## 🟡 circular tests (spec ではなく implementation を pin)

1. **QO1** `test_empty_title_is_not_checked` (test_verify.py:85) — 空 title skip を明示的に固定、コメントに「spec 変更時は同期必要」と明記 (rules/rbkc.md 違反)
2. **QO2** `test_pass_assets_section_skipped` (test_verify.py:153) — skip ブランチをそのまま pin
3. **QO4** `test_broken_json_silently_skipped` — silent skip を pin
4. **QC1** `test_fail_qc1_md_parse_visitor_error` — `extract_document` を monkey-patch するのみで実 MD 誘発ゼロ
5. **QC5** `test_pass_rst_role_marker_without_backtick_arg` — regex の backtick 要求を独立 oracle なしでミラー

---

## 📊 実装者 (私) のバイアス分析

r1 (バイアス注意なし) は 11/11 が基本 ⚠️ 止まり、r2 (バイアス明示) は **❌ 2 件 + 重大 real bug 3 件** を新規指摘しました。

r1 が見逃した主な理由:
- 私 (実装者) が書いたテストをレビュー対象としたため、実装の前提を「正しい仕様」として受容
- 「v6 FAIL 0 = 機能している」という私の結論を r1 エージェントが追認
- 設計書を引用しつつも、実装コメントで「per spec X」と書かれた箇所を spec 本文と照らさなかった

r2 の bias-avoidance 指示で:
- `verify.py:87` の `assets/` skip → spec 該当記述なしと判断
- `verify.py:926` の `len(t) >= 2` → spec 該当記述なしと判断
- monkey-patch / 実挙動ミラー型テストを circular と判定

---

## 対応方針案

### 方針 A: 全 critical 5 件を先に潰す (推奨)

1. QO2 `assets/` skip 撤去 + converter 側修正 (rules/rbkc.md 違反の解消)
2. QC2/QC1 Excel `len(t) >= 2` 撤去 → FAIL が出たら converter 側修正
3. QL1 RST named reference 対応追加
4. QC5 `_MD_RAW_HTML_RE` の `<br/>` 対応
5. circular test 5 件の書き直し
6. v6 FAIL 0 維持を確認

### 方針 B: 設計書 §4 から ✅ を戻す → gap 埋め後に再度 ✅

r2 で critical が出た項目 (QO2, QC2, QL1, QC5, QC1) は暫定 ⚠️ に戻し、対応完了後に ✅ 化。

---

## 要ユーザー判断事項

1. **方針 A / B どちらで進めるか**
2. **QO2 `assets/` 問題**: converter を直して verify を厳格化するか、§5 プロセスで例外を正式化するか
3. **QC2 Excel 1 文字 silent drop の背景確認**: 意図あるなら spec 明文化、無意図ならバグとして削除

各観点の詳細: `.work/00299/review-z1-r2/{QC1..QO4}.md`
