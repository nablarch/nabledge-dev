# Z-1 QA レビュー サマリー

**目的**: 設計書 §4 品質マトリクスの ❌→✅ 更新判定のため、11 品質観点を QA Engineer 視点で別コンテキスト評価。

**評価 3 条件** (全て揃えば ✅ 化可):
1. verify に実装があるか
2. ユニットテストで FAIL 条件とエッジケースをカバーしているか
3. v6 verify 0 FAIL / unit test 全 PASS か

**実行環境**: 11 エージェントを別々のコンテキストで並列実行。各エージェントは品質基準 (ゼロトレランス) と対象観点の仕様箇所を与えられた上で独立判定。

---

## 総合判定表

| ID | 観点 | 実装 | テスト | v6 実行 | 総合 |
|---|---|---|---|---|---|
| QC1 | 完全性 | ✅ | ⚠️ High gap | ✅ | ⚠️ |
| QC2 | 正確性 | ✅ | ⚠️ Excel 完全欠落 | ✅ | ⚠️ |
| QC3 | 非重複性 | ✅ | ⚠️ 5 パス中 4 パス無テスト | ✅ | ⚠️ |
| QC4 | 配置正確性 | ✅ | ⚠️ RST title 1 ケースのみ | ✅ | ⚠️ |
| QC5 | 形式純粋性 | ✅ | ⚠️ エッジ 5 件不足 | ✅ | ⚠️ |
| QL1 | 内部リンク | ⚠️ 仕様乖離疑い | ⚠️ figure/image テスト無 | ✅ | ⚠️ |
| QL2 | 外部リンク | ✅ | ⚠️ MD 経路 UT 0 件 | ✅ | ⚠️ |
| QO1 | docs MD 構造整合性 | ✅ | ⚠️ エッジ 4 件不足 | ✅ | ✅ 条件付き |
| QO2 | docs MD 本文整合性 | ✅ | ⚠️ エッジ 4 件不足 | ✅ | ⚠️ |
| QO3 | docs MD 存在 | ✅ | ⚠️ エッジ 4 件不足 | ✅ | ⚠️ |
| QO4 | index.toon 網羅 | ⚠️ 仕様曖昧 2 件 | ⚠️ CJK/壊れ JSON 無 | ✅ | ⚠️ |

**v6 verify FAIL 0 / unit test 138 PASS** は全 11 観点で共通 (全員 ✅)。

**結論**: **現状では ❌→✅ 化できる観点は 0 件**。ゼロトレランス基準に照らすと全観点に gap がある。

---

## 観点別の重要 gap (High 優先度のみ)

### QC1 完全性
- **実装上の整合性問題**: `verify.py:354` で RST normaliser に `strict_unknown=False` を渡しており、MD 側 (strict_unknown=True) と非対称。設計書 §3-1b「未登録 node → FAIL, silent 禁止」と矛盾の可能性 → **要ユーザー判断**
- MD parse error 経路 (`verify.py:708`) を fixate するテスト皆無
- RST 未登録 node / 未解決 reference / substitution の verify 層 FAIL テスト無
- Excel `.xls` 経路 (`verify.py:815-825`) テスト皆無

### QC2 正確性
- **Excel QC2 FAIL の unit test が完全欠落** (TDD 原則違反)
- 複数捏造 / top-level 捏造 / near-miss のエッジケース無

### QC3 非重複性
- 検出パス 5 本 (RST title/content, MD title/content, Excel cell) のうち **4 パスが無テスト**
- CJK 短文字列衝突、top-level/section 間重複、空白 unit 誤発火のテスト無

### QC4 配置正確性
- テストが RST title の 2-section-swap 1 ケースのみ
- MD 経路・content misplacement・top-level 混在・QC3/QC4 境界のテスト無

### QC5 形式純粋性
- 仕様記載のエッジケース 3 件未カバー: heading underline in content (allowed), inline code with role syntax, Japanese punctuation false positives
- `<summary>` `<br>` `<a>` `\_` `\[` が個別 parametrize されていない

### QL1 内部リンク
- **仕様乖離疑い**: 設計書 §3-2 は MD inline `image` を QL1 対象として記載。実装では独立検査されていない → **要ユーザー判断**
- RST figure / image の bug-revealing テスト完全欠落 (`_has_visible_text` 含む `verify.py:1016-1044` が一度もテストされていない)

### QL2 外部リンク
- `TestVerifyFileQL2` 10 ケース全て RST/xlsx。**MD `[text](url)` / autolink 専用テストが 0**
- URL 特殊形 (query/fragment/括弧/CJK 末尾句読点/http vs https) テスト無

### QO1 docs MD 構造整合性
- エッジケース 4 件未カバー (H1 欠落、空 title、特殊文字、複数 H1)

### QO2 docs MD 本文整合性
- whitespace-only diff / コードブロック / Markdown 特殊文字 / 複数 sections 混在 テスト無

### QO3 docs MD 存在
- nested-dir path-preservation negative、CJK filename、empty-knowledge-dir、README page-count mismatch テスト無

### QO4 index.toon 網羅性
- **仕様曖昧 2 件要決定**:
  1. index.toon 不在時: 現実装は 1 件のみ報告。spec 意図「listing ALL JSONs」との乖離
  2. dangling entry (index に載っているが JSON 無し) が片方向チェックで検出不能
- CJK / 空白ファイル名 / 壊れた JSON (silent skip) テスト無

---

## 対応方針案

### 方針 A: gap を全て埋めてから ✅ 化

各観点の High gap を TDD で埋める。作業量の粗見積もり:

- テスト追加のみ: **約 40 件** (各観点 High 3–5 件平均)
- 仕様乖離解消 (QL1 MD image / QC1 strict_unknown / QO4 仕様曖昧): 設計書更新 + 実装調整

### 方針 B: ✅ 条件を明文化してから部分的 ✅ 化

設計書 §4 に「✅ の成立条件」を明記 (例: 実装存在 + 仕様準拠 + v6 実行 PASS + 主要 FAIL ケース test + エッジ ≥ 80%) し、満たした ID のみ ✅ 化。

### 方針 C: 各 gap を個別に優先度判定

観点ごとに High gap のみ優先で埋め、Low / Medium は別 Issue 化。

---

## ユーザーレビュー依頼事項

1. **方針 A / B / C のどれで進めるか**
2. **QC1 の strict_unknown=False 問題** (RST Visitor エラーを silent に飲み込む実装)
   - 設計書 §3-1b 例外禁止原則と矛盾するように見える
   - `strict_unknown=True` に直すと v6 で FAIL が出るか未検証
3. **QL1 の MD image 仕様乖離**
   - 設計書は QL1 対象として記載、実装は独立検査せず
   - 設計書を正として実装を追加するか、実装を正として設計書を縮小するか
4. **QO4 の仕様曖昧 2 件**
   - index.toon 不在時の出力形式
   - dangling entry (JSON が無い index.toon エントリ) を検出対象にするか

各観点の詳細レビュー: `.work/00299/review-z1/{QC1..QO4}.md` 参照
