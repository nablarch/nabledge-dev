# 品質比較レポート：グループベース分割 vs セクション単位分割

**作成日**: 2026年3月4日
**目的**: 分割方式による生成品質の比較

---

## 前回（グループベース分割）の品質

### Phase B: 生成
```
生成パート数: 9
  - adapters-micrometer_adaptor: 2パート
  - libraries-tag: 4パート
  - libraries-tag_reference: 3パート
```

### Phase C: 構造チェック
```
総数: 3ファイル
合格: 3 (100%)
不合格: 0 (0%)
```

### Phase D: 内容チェック
```
チェック済み: 1ファイル（adapters-micrometer_adaptor のみ）
クリーン: 1 (100%)
問題あり: 0 (0%)

Total findings: 0 件
```

**⚠️ 重要**: libraries-tag と libraries-tag_reference は Phase D 未実行
（Phase D findings ファイルが空）

### Phase E: 修正
```
修正実行: 2ファイル
  - libraries-tag: 実行済み
  - libraries-tag_reference: 実行済み
```

**注**: adapters-micrometer_adaptor は問題なしのため Phase E スキップ

### Phase F: パターン分類
```
分類済み: 3ファイル
  - adapters-micrometer_adaptor
  - libraries-tag
  - libraries-tag_reference
```

### Phase G: リンク解決
```
解決済み: 3ファイル
  - component/adapters/adapters-micrometer_adaptor.json
  - component/libraries/libraries-tag.json
  - component/libraries/libraries-tag_reference.json
```

### 前回のサマリー

| フェーズ | 実行 | 結果 |
|---------|------|------|
| Phase B (生成) | 9パート | 完了 |
| Phase C (構造) | 3ファイル | 全て合格 (100%) |
| Phase D (内容) | 1ファイル | 全てクリーン (100%) ⚠️ 不完全 |
| Phase E (修正) | 2ファイル | 実行済み |
| Phase F (分類) | 3ファイル | 完了 |
| Phase G (解決) | 3ファイル | 完了 |

**⚠️ Phase D の問題**:
- adapters-micrometer_adaptor のみチェック実行
- libraries-tag と libraries-tag_reference は findings ファイルが空
- 完全な品質比較データなし

---

## 今回（セクション単位分割）の品質

### Phase B: 生成
```
生成セクション数: 119
  - adapters-micrometer_adaptor: 14セクション
  - libraries-tag: 40セクション
  - libraries-tag_reference: 65セクション
```

### Phase C: 構造チェック
```
【完了待ち】
```

### Phase D: 内容チェック（80/119セクション完了時点）

```
チェック済み: 80セクション (67%)
クリーン: 44 (55%)
問題あり: 36 (45%)

Total findings: 54件
  Critical: 12件
  Minor: 42件

【カテゴリ別】
  omission (重要情報の省略): 22件 (critical: 9件)
  hints_missing (検索ヒント不足): 20件 (critical: 0件)
  fabrication (誤情報): 9件 (critical: 3件)
  section_issue (構造問題): 3件 (critical: 0件)
```

#### ファイル別（80セクション中）

| ファイル | セクション数 | クリーン | 問題あり | Critical | Minor |
|---------|-------------|---------|---------|----------|-------|
| adapters-micrometer_adaptor | 14 | 【集計中】 | 【集計中】 | 【集計中】 | 【集計中】 |
| libraries-tag | 40 | 【集計中】 | 【集計中】 | 【集計中】 | 【集計中】 |
| libraries-tag_reference | 65 | 【集計中】 | 【集計中】 | 【集計中】 | 【集計中】 |

### Phase E: 修正
```
【完了待ち】
```

### Phase F: パターン分類
```
【完了待ち】
```

### Phase G: リンク解決
```
【完了待ち】
```

---

## 比較サマリー（暫定）

| 指標 | 前回（グループベース） | 今回（セクション単位） | 差分 |
|------|---------------------|---------------------|------|
| **生成ファイル数** | 9パート | 119セクション | +110 (13倍) |
| **Phase C 合格率** | 100% (3/3) | 【完了待ち】 | - |
| **Phase D チェック済み** | 1ファイル ⚠️ 不完全 | 80セクション (67%) | - |
| **Phase D クリーン率** | 100% (1/1) | 55% (44/80) | -45% |
| **Phase D Critical** | 0件 | 12件 | +12件 |
| **Phase D Total findings** | 0件 | 54件 | +54件 |

**⚠️ 注意**: 前回は Phase D が不完全実行のため、直接比較は困難

---

## 主要な発見

### 1. Phase D で大量の findings（今回）

**事実**:
- 80セクション中、45%に問題（36セクション）
- Critical findings 12件（重大な省略・誤情報）
- omission（省略）が最多：22件

**具体例**:
- `adapters-micrometer_adaptor--micrometer`: 実行結果サンプル40行が完全欠落（critical）
- `adapters-micrometer_adaptor--defaultmeterbinderlistprovider`: JavaDoc URL パス誤り（critical）
- `libraries-tag--sec-502d909c`: クラス名（MessageUtil, MessageLevel）がhintsに不足

### 2. セクション単位でも品質問題は発生

**仮説「小さなプロンプト = 高品質」は不成立**

考えられる原因:
1. **文脈不足**: セクションが小さすぎて周辺情報を参照できない
2. **プロンプト未最適化**: セクション単位に特化した指示が不足
3. **Layer A/B/C 抽出ルールの影響**: 簡潔さを求めすぎて重要情報を省略
4. **出力トークン削減圧力**: プロンプトで簡潔さを求めた結果、必要情報も削除

### 3. 前回との直接比較は困難

**理由**:
- 前回は adapters-micrometer_adaptor のみ Phase D 実行
- libraries-tag と libraries-tag_reference は Phase D スキップまたは未記録
- 完全な品質ベースラインなし

---

## 完了待ちの分析タスク

### パイプライン完了後に実施

1. **完全な Phase D 集計** (119セクション)
   - ファイル別の問題率
   - Critical findings の詳細内訳
   - 最悪のセクション TOP 10

2. **Phase E 修正成功率**
   - 修正試行セクション数
   - 修正成功/失敗の割合
   - カテゴリ別修正成功率

3. **Phase F/G の完了状況**
   - 最終的なナレッジファイル数
   - 最終品質（clean率）

4. **根本原因分析**
   - セクションサイズと findings の相関
   - プロンプトの問題箇所特定
   - Haiku モデルの限界検証

---

## 次のアクション

1. ✅ 前回データの集計完了（このドキュメント）
2. ⏳ パイプライン完了を待つ
3. ⏳ `analyze_quality.sh` で今回の完全データ集計
4. ⏳ 比較分析と根本原因特定
5. ⏳ レポート更新（推奨事項の見直し）

**更新日時**: 【パイプライン完了後に更新】
