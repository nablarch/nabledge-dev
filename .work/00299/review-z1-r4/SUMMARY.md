# Z-1 四次 QA レビュー (r4) サマリー

**目的**: パターン A-E 横並び修正 (commit `d53d04f4f`) 後、bias-avoidance 明示で再検証。

---

## 判定表 (r1 → r2 → r3 → r4)

| ID | r1 | r2 | r3 | **r4** | 変化 |
|---|---|---|---|---|---|
| QC1 | ⚠️ | ⚠️ | ⚠️ | **⚠️** | High 2 件 (substitution / parse error 負テスト) 未対応 |
| QC2 | ⚠️ | ❌ | ⚠️ | **⚠️** | `.xls` High 未対応 (v1.2/1.3 ブロッカー) |
| QC3 | ⚠️ | ⚠️ | ⚠️ | **✅** | r3 High 解消、OR assert Medium のみ |
| QC4 | ⚠️ | ⚠️ | ❌ | **✅** | r3 ❌ 解消、discriminator Medium のみ |
| QC5 | ⚠️ | ⚠️ | ⚠️ | **✅ 5/5** | r3 Medium 2 件解消 |
| QL1 | ⚠️ | ⚠️ | ❌ | **❌** | **High 未解消: named ref 実装が実 docutils で dead code (refname 0 件)** |
| QL2 | ⚠️ | ✅ | ⚠️ | **✅** | parens circular / RST bare URL Medium のみ |
| QO1 | ✅ | ⚠️ | ⚠️ | **✅ 5/5** | r3 Medium 3 件解消 |
| QO2 | ⚠️ | ❌ | ❌ | **✅** | r3 High 解消、circular rewrite test Medium |
| QO3 | ⚠️ | ✅ | ⚠️ | **✅** | loose assert Medium のみ |
| QO4 | ⚠️ | ⚠️ | ✅ | **✅** | TOON parser Medium のみ |

### 合否
- **✅: 8 件** (QC3/QC4/QC5/QL2/QO1/QO2/QO3/QO4)
- **⚠️: 2 件** (QC1/QC2)
- **❌: 1 件** (QL1)

---

## r3 → r4 の解消状況

### 解消 ✅
- QC4 r3 ❌ (QC3/QC4 境界) → r4 ✅ (テスト追加)
- QO2 r3 ❌ (top-level 位置) → r4 ✅ (実装追加)
- QC5 r3 Medium 2 → r4 ✅
- QO1 r3 Medium 3 → r4 ✅
- QC3 r3 High (短 CJK / top×section) → r4 ✅ (テスト追加)

### 未解消 ❌
- **QL1 High**: `nodes.reference` の `refname` で walk していたが、実 docutils は `` `Text`_ `` を `refid` で emit する (200 v6 RST 測定: refname=0 / refid=1008)。実装が**完全に dead code**。テストも monkey-patch で実 docutils を通していないため検出できず。
- **QC2 High**: `.xls` (xlrd) 経路が unit test 0。v6 には `.xls` が無いので v6 PASS は証拠にならない。v1.2/1.3 では `.xls` あり → **展開ブロッカー**。
- **QC1 High**: 未解決 substitution / parse error level≥3 の負テスト未追加。

---

## 🔴 critical: QL1 named reference の本質問題

**r2 で指摘 → r3 で「circular 形を変えただけ」と指摘 → r4 でも「実装が dead code」と新規発覚**

### 経緯

1. r2 で「`nodes.reference` (refid/refname) walk」を追加
2. r3 で「monkey-patch でテストしている」(circular) と指摘
3. r4 で「実 docutils は `refid` を使う。`refname` 条件は実データで 0 件マッチ、dead code」と確定

### 根本原因
私が **docutils の実際の出力を確認せずに spec §3-2 の文面をそのまま実装**したこと。spec は "refid / refname" と併記しているが、docutils 実装では parse 時に即座に `refname` → `refid` に変換される。

### 修正方針
- 実装を `refid` に基づいて書き直す (`doctree.ids[refid]` で target section 取得、title を検証)
- テストを実 RST ソースで駆動する (monkey-patch 撤廃)
- spec §3-2 row 1 を「refid または refname」から「refid (docutils 解決後)」に更新

---

## r4 で残る作業 (r5 まで)

### 実装修正 2 件
1. **QL1**: `refid` ベースで native reference を検証、monkey-patch テスト → 実 RST 駆動テストに書き直し
2. **QC1**: Excel empty-JSON silent return の仕様確認 + 修正

### テスト追加 4 件
3. **QC1**: 未解決 substitution 負テスト
4. **QC1**: parse error level≥3 負テスト
5. **QC2**: `.xls` (xlrd) 経路の FAIL/PASS テスト (openpyxl ではなく xlrd で書き込み)
6. **QL1**: scheme filter (`javascript:` / empty href) テスト

### Medium 類 (任意、次 PR でも可)
- QO4 TOON parser 頑健性 3 件
- QC4 QC3/QC4 discriminator / cross-class exclusion
- QO2 circular rewrite test / empty section 扱い
- QO3 loose assert 強化 / README `N ページ` 複数宣言
- QC3 whitespace-only test / OR assert strip
- QL2 parens circular / RST bare URL

---

## 次の動き
方針 A: critical 3 件 (QL1 / QC2 / QC1) を潰して r5 で最終確認 → ✅ 7+ 件確保後マトリクス復元。
