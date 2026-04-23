# Z-1 五次 QA レビュー (r5) サマリー

**目的**: r4 critical 3 件修正後 (commit `d6e4a40b0`) の bias-avoidance 再検証。

---

## 判定表 (r1 → r5)

| ID | r1 | r2 | r3 | r4 | **r5** | |
|---|---|---|---|---|---|---|
| QC1 | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **✅** | 合格 |
| QC2 | ⚠️ | ❌ | ⚠️ | ⚠️ | **✅** | 4/5 |
| QC3 | ⚠️ | ⚠️ | ⚠️ | ✅ | **✅** | 4/5 |
| QC4 | ⚠️ | ⚠️ | ❌ | ✅ | **✅** | 4/5 |
| QC5 | ⚠️ | ⚠️ | ⚠️ | ✅ | **✅ 5/5** | 完全合格 |
| QL1 | ⚠️ | ⚠️ | ❌ | ❌ | **✅** | 4.5/5 (r4 High 解消) |
| QL2 | ⚠️ | ✅ | ⚠️ | ✅ | **✅** | 4.5/5 |
| QO1 | ✅ | ⚠️ | ⚠️ | ✅ 5/5 | **⚠️** | **High 新規: `~~~` fence 未対応** |
| QO2 | ⚠️ | ❌ | ❌ | ✅ | **✅** | 4/5 |
| QO3 | ⚠️ | ✅ | ⚠️ | ✅ | **✅** | 4/5 |
| QO4 | ⚠️ | ⚠️ | ✅ | ✅ | **✅** | PASS |

### 合否
- **✅: 10 件**
- **⚠️: 1 件** (QO1: `~~~` fence 未対応 High 新規発覚)
- **❌: 0 件**

---

## 🟡 r5 新規発覚 (1 件のみ)

### QO1: `~~~` tilde-fenced code block 未対応

- **現象**: `_FENCE_BLOCK_RE` が `` ``` `` のみを対象としており、`~~~` 形式を strip しない
- **結果**: `~~~md\n## fake\n~~~` の中の `## fake` が section title として誤検出される可能性
- **影響**: CommonMark 仕様では `~~~` も fenced code delimiter。v6 の実データに `~~~` は使われていないので実害は出ていない
- **修正**: `_FENCE_BLOCK_RE` を `(?:```|~~~)` に拡張 + テスト追加

これは「パターン B (regex 網羅)」の横並びチェックで漏れた一件。 QA r5 レビューが catch。

---

## 🟡 QC2 新規発覚 (Medium)

### `.xls` テストの `pytest.importorskip` 相当パターン

- **現象**: r4 で追加した `.xls` 4 テストが `try: import xlwt, xlrd; except ImportError: pytest.skip(...)` 形式
- **ルール違反**: `.claude/rules/development.md` は `pytest.importorskip` / `pytest.skip` 形式を禁止
- **修正**: `xlwt` を dev 必須依存にするか (setup.sh で既にインストール済)、`.xls` fixture を commit して skip 撤廃

---

## 残 Medium (非ブロッカー、次 PR 可)

- **QC3**: OR assert (`"QC3" in i or "duplicate content" in i`) 4 箇所の strip
- **QC4**: QC3/QC4 境界テストの docstring と assertion の不整合修正、3-section rotation test
- **QL1**: `javascript:` / empty-href / figure alt-only fallback テスト、RST substitution-image dedup 欠
- **QL2**: parens circular / RST bare URL
- **QO1**: fenced `##` inside top-region / code-fence 直接テスト
- **QO2**: symmetric rewrite 本物化 / top-region fence test
- **QO3**: loose assert 厳格化 / `N ページ` 複数宣言
- **QO4**: TOON parser 頑健性 (header / row count / comma path)

合計 ~15 件の Medium。全て非ブロッカー。

---

## 判定

**r5 残ブロッカー 2 件**:
1. QO1 `~~~` fence High 発覚 → 5 分で修正可能
2. QC2 `pytest.skip` ルール違反 → skip 撤廃で修正可能

この 2 件を潰せば全 ID 合格 → **§4 マトリクス ✅ 復元条件を満たす**。

### 収束しているか
- r3(✅1/⚠️8/❌2) → r4(✅8/⚠️2/❌1) → r5(✅10/⚠️1/❌0)
- **critical は収束完了**。QO1 の `~~~` は既知パターン B の漏れ分、QC2 は test infra の細かい話
- r6 で復元を阻むブロッカーはない

---

## 次のアクション

1. QO1 `~~~` fence 追加
2. QC2 `.xls` テストの skip 撤廃
3. r6 レビューで 11 件 ✅ 確認
4. §4 マトリクス ✅ 復元
5. Z-1 完了
