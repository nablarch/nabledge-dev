# nabledge-test スキル修正内容

## 変更日
2026-02-26

## 変更の目的
ユーザーからの指摘：
1. 性能目標（Token usage is between 5000 and 15000など）に根拠がない
2. 「コンテンツ品質」という曖昧な言葉は実際には「キーワード出現数」
3. 「合格/不合格」の判定は恣意的
4. すべて測定値として表示すべき

## 主な変更点

### 1. 用語の変更

| 変更前 | 変更後 | 理由 |
|--------|--------|------|
| expectations | detection_items | 期待値ではなく検出項目 |
| passed/failed | detected/not_detected | 合格/不合格ではなく検出/非検出 |
| pass rate | detection rate | 合格率ではなく検出率 |
| コンテンツ品質 | キーワード/コンポーネント検出 | 正直な表記 |
| 総合合格率 | (削除) | 恣意的な判定を排除 |

### 2. 性能目標の削除

**削除した項目**:
```python
# 削除前
expectations.append("Token usage is between 5000 and 15000")
expectations.append("Tool calls are between 10 and 20")
```

**理由**: 根拠のない恣意的な数値。測定はするが合格/不合格の判定には使わない。

### 3. レポート形式の変更

#### 個別シナリオレポート

**変更前**:
```markdown
## Results
**Pass Rate**: 7/8 (87.5%)

### Expectations
- ✓ Response includes 'DataReadHandler'
- ✗ Token usage is between 5000 and 15000
```

**変更後**:
```markdown
## Detection Results
**Detection Rate**: 5/5

### Detection Items
- ✓ Response includes 'DataReadHandler'
- ✓ Response includes 'DataReader'
...

## Metrics (Measured Values)
- **Duration**: 68s
- **Tokens**: 9,480 (IN: 6,780 / OUT: 2,700)
```

#### 統合レポート

**変更前**:
```markdown
| Scenario | 合格率 | 所要時間 | トークン |
|----------|--------|---------|---------|
| processing-005 | 100% ⭐ | 68秒 | 9,480 |
| libraries-001 | 75% | 19秒 | 26,890 |

総合合格率: 93.8% ✓ (目標: 80%)
```

**変更後**:
```markdown
| Scenario | 検出 | 時間 | トークン |
|----------|------|------|---------|
| processing-005 | 5/5 | 68秒 | 9,480 |
| libraries-001 | 5/5 | 19秒 | 26,890 |

統計:
- キーワード/コンポーネント検出: 全シナリオで全項目検出 (57/57)
- 平均実行時間: 84.5秒
- 平均トークン: 25,558
```

### 4. grading.json の構造変更

**変更前**:
```json
{
  "expectations": [...],
  "summary": {
    "passed": 7,
    "failed": 1,
    "total": 8,
    "pass_rate": 0.875
  }
}
```

**変更後**:
```json
{
  "detection_items": [...],
  "summary": {
    "detected": 5,
    "not_detected": 0,
    "total": 5,
    "detection_rate": 1.0
  }
}
```

### 5. scenarios.json メタデータ更新

**追加**:
```json
{
  "metadata": {
    "version": "6.0.0",
    "evaluation_method": "Keyword/component detection via string search. Performance metrics measured but not used for pass/fail."
  }
}
```

## 期待される効果

### Before (旧形式)
```
❌ 不公平: 知識検索だけ性能を判定に含める
❌ 曖昧: 「93.8%合格」が何を意味するか不明
❌ 恣意的: 「5,000-15,000トークン」の根拠なし
❌ 不正確: 「コンテンツ品質」は単なるキーワード検索
```

### After (新形式)
```
✅ 公平: すべて同じ基準（検出数 x/x）
✅ 明確: 「5/5検出」「68秒」「9,480トークン」が一目瞭然
✅ 客観的: 測定値のみ、恣意的判定なし
✅ 正直: キーワード/コンポーネント検出と明記
```

## ファイル変更リスト

1. `.claude/skills/nabledge-test/SKILL.md`
   - description更新
   - Step 3: expectations → detection_items
   - Step 7: Grade → Check detection items
   - Step 8-9: レポート形式変更
   - Step 10: サマリー表示変更

2. `.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json`
   - metadata.version: 5.0.0 → 6.0.0
   - metadata.evaluation_method 追加
   - description更新

## 互換性

### 破壊的変更
- grading.json の構造変更（expectations → detection_items）
- レポート形式の変更
- 用語の変更（合格率 → 検出率）

### 影響範囲
- 新しいテスト実行: 新形式で動作
- 既存のレポート: 旧形式のまま（再生成は不要）
- 外部依存: なし（スキルは独立）

## マイグレーション不要

既存のテスト結果（`.pr/00088/nabledge-test/202602261604/`）は参考資料として保持。
次回のテスト実行から自動的に新形式が適用される。

## まとめ

**変更の本質**:
- 「判定」から「測定」へ
- 「合格/不合格」から「x/x検出 + 測定値」へ
- 恣意的な基準を排除し、事実のみを報告

**開発者へのメリット**:
- 何を最適化すべきか明確（トークン、時間、どこがボトルネック）
- 公平な比較が可能
- 継続的改善の基準が客観的
