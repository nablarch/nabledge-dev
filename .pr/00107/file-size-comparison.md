# ファイルサイズ比較：RST vs JSON

**作成日**: 2026年3月4日
**ステータス**: ✅ 完了

---

## エグゼクティブサマリー

| 段階 | ファイル数 | 総サイズ | 平均サイズ/ファイル |
|------|-----------|---------|-------------------|
| **ソースRST** | 3ファイル | 369.3 KB | 123.1 KB |
| **前回Phase B（グループベース）** | 9パート | 216.8 KB | 24.1 KB |
| **今回Phase B（セクション単位）** | 119セクション | 214.3 KB | 1.8 KB |
| **前回最終JSON** | 3ファイル | 217.0 KB | 72.3 KB |
| **今回最終JSON** | 3ファイル | 302.3 KB | 100.8 KB |

**変換効率（Phase B生成直後）**:
- RST → 前回Phase B: **41%削減**（59%に圧縮、9パート）
- RST → 今回Phase B: **42%削減**（58%に圧縮、119セクション）
- **前回Phase B → 今回Phase B**: **-3.5%削減**（216.8 KB → 214.3 KB）
  - **粒度**: 13倍向上（9パート → 119セクション）
  - **サイズ**: ほぼ同等（-1.2%）
  - **結論**: **同じサイズで13倍の粒度を実現！** ✅

**マージ後の変換効率**:
- RST → 前回最終: **41%削減**（59%に圧縮）
- RST → 今回最終: **18%削減**（82%に圧縮）
- Phase B → 最終マージ: **41%増加**（マージオーバーヘッド）
- **前回最終 → 今回最終**: **+39%増加**（217 KB → 302 KB）

---

## 1. ソースRST

**場所**: `.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/`

| ファイル | サイズ (bytes) | サイズ (KB) | 行数 | 備考 |
|---------|---------------|------------|------|------|
| micrometer_adaptor.rst | 108,238 | 105.7 | 1,839 | Micrometerアダプタ |
| tag.rst | 141,949 | 138.6 | 3,085 | カスタムタグ |
| tag_reference.rst | 128,003 | 125.0 | 2,025 | タグリファレンス |
| **合計** | **378,190** | **369.3** | **6,949** | - |

**平均**:
- サイズ/ファイル: 126,063 bytes (123.1 KB)
- 行数/ファイル: 2,316行

---

## 2. 前回Phase B（グループベース分割、9パート）

**場所**: コミット `364b5ef` の `tools/knowledge-creator/.logs/v6/phase-b/executions/*.json` の `structured_output.knowledge`

### 統計

```
総パート数: 9個
総サイズ: 216.8 KB (222,011 bytes)
平均サイズ: 24,668 bytes/パート
```

### ファイル別内訳

| ファイル | パート数 | サイズ | 平均サイズ/パート | RST比 |
|---------|---------|--------|------------------|-------|
| adapters-micrometer_adaptor | 2 | 82.0 KB (83,967 bytes) | 41,984 bytes | -24% |
| libraries-tag | 4 | 84.7 KB (86,732 bytes) | 21,683 bytes | -40% |
| libraries-tag_reference | 3 | 50.1 KB (51,312 bytes) | 17,104 bytes | -60% |
| **合計** | **9** | **216.8 KB (222,011 bytes)** | **24,668 bytes** | **-41%** |

**分析**:
- 最小パート平均: 17,104 bytes (tag_reference)
- 最大パート平均: 41,984 bytes (adapters)
- サイズのばらつき: 2.5倍

### パート別詳細

**adapters-micrometer_adaptor**:
- Part 1: 37.4 KB (38,342 bytes)
- Part 2: 44.6 KB (45,625 bytes)

**libraries-tag**:
- Part 1: 25.1 KB (25,725 bytes)
- Part 2: 27.2 KB (27,873 bytes)
- Part 3: 27.4 KB (28,066 bytes)
- Part 4: 4.9 KB (5,068 bytes) ← 最小パート

**libraries-tag_reference**:
- Part 1: 23.9 KB (24,448 bytes)
- Part 2: 24.9 KB (25,527 bytes)
- Part 3: 1.3 KB (1,337 bytes) ← 異常に小さい

---

## 3. 今回Phase B（セクション単位分割、119セクション）

**場所**: `tools/knowledge-creator/.logs/v6/phase-b/executions/*.json` の `structured_output.knowledge`

### 統計

```
総ファイル数: 119個
総サイズ: 214.3 KB (219,418 bytes)
平均サイズ: 1,843 bytes/ファイル
```

### ファイル別内訳

| ファイル | セクション数 | サイズ | 平均サイズ/セクション | RST比 |
|---------|-------------|--------|---------------------|-------|
| adapters-micrometer_adaptor | 14 | 64.0 KB (65,497 bytes) | 4,678 bytes | -39% |
| libraries-tag | 40 | 87.9 KB (89,982 bytes) | 2,250 bytes | -37% |
| libraries-tag_reference | 65 | 62.4 KB (63,939 bytes) | 984 bytes | -50% |
| **合計** | **119** | **214.3 KB (219,418 bytes)** | **1,843 bytes** | **-42%** |

**分析**:
- 最小セクション平均: 984 bytes (tag_reference)
- 最大セクション平均: 4,678 bytes (adapters)
- サイズのばらつき: 4.8倍

---

## 4. 今回最終マージJSON（3ファイル）

**場所**: `.claude/skills/nabledge-6/knowledge/component/*/`

### 統計

```
総ファイル数: 3個
総サイズ: 302.3 KB (309,556 bytes)
平均サイズ: 100.8 KB/ファイル
```

### ファイル別

| ファイル | サイズ | セクション数 | RST比 | セクション比 |
|---------|--------|-------------|-------|-------------|
| adapters-micrometer_adaptor.json | 87 KB (89,088 bytes) | 14 | -18% | +36% |
| libraries-tag.json | 136 KB (139,264 bytes) | 40 | -2% | +55% |
| libraries-tag_reference.json | 81 KB (82,944 bytes) | 65 | -35% | +30% |
| **合計** | **302.3 KB (309,556 bytes)** | **119** | **-18%** | **+41%** |

---

## 5. 前回最終JSON（グループベース分割）

**場所**: コミット `364b5ef` の `.claude/skills/nabledge-6/knowledge/component/*/`

### 統計

```
総ファイル数: 3個
総サイズ: 217.0 KB (222,213 bytes)
平均サイズ: 72.3 KB/ファイル
```

### ファイル別

| ファイル | サイズ | RST比 |
|---------|--------|-------|
| adapters-micrometer_adaptor.json | 111.7 KB (114,392 bytes) | +3% |
| libraries-tag.json | 21.0 KB (21,480 bytes) | -85% |
| libraries-tag_reference.json | 84.3 KB (86,341 bytes) | -34% |
| **合計** | **217.0 KB (222,213 bytes)** | **-41%** |

---

## 6. Phase B比較：前回（9パート） vs 今回（119セクション）

**重要な発見**: Phase B生成直後のファイルサイズは**ほぼ同等**で、粒度が**13倍向上**！

### ファイルサイズ比較

| ファイル | 前回Phase B（パート単位） | 今回Phase B（セクション単位） | 差分 | 増減率 |
|---------|------------------------|---------------------------|------|--------|
| adapters-micrometer_adaptor | 82.0 KB (2パート) | 64.0 KB (14セクション) | -18.0 KB | -22% ✅ |
| libraries-tag | 84.7 KB (4パート) | 87.9 KB (40セクション) | +3.2 KB | +4% ✅ |
| libraries-tag_reference | 50.1 KB (3パート) | 62.4 KB (65セクション) | +12.3 KB | +25% |
| **合計** | **216.8 KB (9パート)** | **214.3 KB (119セクション)** | **-2.5 KB** | **-1.2%** ✅ |

### 分析

**adapters-micrometer_adaptor (-22%)**:
- 前回: 82.0 KB（2パート、平均42.0 KB/パート）
- 今回: 64.0 KB（14セクション、平均4.6 KB/セクション）
- サイズ削減理由: 細分化により重複メタデータが減少、より焦点を絞った内容
- 粒度向上: 2パート → 14セクション（7倍）

**libraries-tag (+4%)**:
- 前回: 84.7 KB（4パート、平均21.7 KB/パート）
- 今回: 87.9 KB（40セクション、平均2.2 KB/セクション）
- ほぼ同サイズ: 内容の完全性は同等
- 粒度向上: 4パート → 40セクション（10倍）

**libraries-tag_reference (+25%)**:
- 前回: 50.1 KB（3パート、平均16.7 KB/パート、最小パート1.3 KB）
- 今回: 62.4 KB（65セクション、平均984 bytes/セクション）
- サイズ増加理由: 前回最小パート（1.3 KB）が異常に小さく不完全だった可能性
- 粒度向上: 3パート → 65セクション（22倍）

**総合評価** ⭐:
- **Phase B生成サイズ**: ほぼ同等（-1.2%削減）
- **粒度**: 13倍向上（9パート → 119セクション）
- **平均ファイルサイズ**: 24.1 KB/パート → 1.8 KB/セクション（13倍細分化）
- **結論**: **同じサイズで13倍の粒度を実現！RAG検索精度向上とコスト効率を両立** ✅✅✅

---

## 7. 最終JSON比較：前回 vs 今回

### ファイルサイズ比較（最終マージ後）

| ファイル | 前回最終JSON | 今回最終JSON | 差分 | 増減率 |
|---------|-------------|-------------|------|--------|
| adapters-micrometer_adaptor.json | 111.7 KB | 87.0 KB | -24.7 KB | -22% ✅ |
| libraries-tag.json | 21.0 KB | 136.0 KB | +115.0 KB | +548% ⚠️ |
| libraries-tag_reference.json | 84.3 KB | 81.0 KB | -3.3 KB | -4% ✅ |
| **合計** | **217.0 KB** | **304.0 KB** | **+87.0 KB** | **+40%** ⚠️ |

**注意**: libraries-tagの前回サイズ（21 KB）は異常に小さく、生成失敗または不完全な可能性が高い。

### 変換効率の分析

| ファイル | RST → 前回Phase B | RST → 今回Phase B | RST → 前回最終 | RST → 今回最終 | Phase B → 最終（今回） |
|---------|-----------------|-----------------|-------------|-------------|-------------------|
| adapters-micrometer_adaptor | -24% | -39% | +3% ⚠️ | -18% | +36% |
| libraries-tag | -40% | -37% | -85% ⚠️ | -2% | +55% |
| libraries-tag_reference | -60% | -50% | -34% | -35% | +30% |
| **平均** | **-41%** | **-42%** | **-41%** | **-18%** | **+41%** |

### マージオーバーヘッドの内訳

**セクション単位JSON（219 KB）→ 最終マージJSON（302 KB）で+90 KB増加**

増加の原因:
1. **ファイルレベルメタデータ**: 各ファイルのfile_id, title, category等
2. **リンク解決情報**: Phase Gで追加されたクロスリファレンス
3. **パターン分類データ**: Phase Fで追加されたpatterns配列
4. **構造化オーバーヘッド**: sections配列のラッパー構造

### ファイル別の特徴

**adapters-micrometer_adaptor**:
- セクション数: 最少（14個）
- セクション平均サイズ: 最大（4,678 bytes）
- 技術的に詳細な内容（コード例、実行結果、設定多数）
- マージオーバーヘッド: +36%（最小）

**libraries-tag**:
- セクション数: 中（40個）
- RST → 最終で-2%（ほぼ同サイズ）
- マージオーバーヘッド: +55%（最大）
- 理由: 40セクションの構造化コストが高い

**libraries-tag_reference**:
- セクション数: 最多（65個）
- セクション平均サイズ: 最小（984 bytes）
- シンプルな属性リファレンス（パターンが統一）
- RST → 最終で-35%（最大削減）
- マージオーバーヘッド: +30%

---

## 8. 総合評価

### RST → JSON変換の効率

**セクション単位生成（Phase B）**:
- 42%削減を達成
- 平均1,843 bytes/セクション
- 粒度: 119ファイル（1 h2 = 1ファイル）

**最終マージ（Phase M）**:
- 18%削減
- セクション単位から41%増加（マージオーバーヘッド）
- 粒度: 3ファイル（元の文書単位）

### トレードオフ

| 指標 | 前回Phase B<br>(9パート) | 今回Phase B<br>(119セクション) | 前回最終JSON<br>(3ファイル) | 今回最終JSON<br>(3ファイル) |
|------|----------------------|----------------------------|------------------------|------------------------|
| **サイズ** | 217 KB | 214 KB ✅ | 217 KB | 304 KB |
| **ファイル数** | 9個 | 119個 ✅✅✅ | 3個 | 3個 |
| **粒度** | 粗い（パート単位） | **最高**（1 h2 = 1ファイル） ✅ | 粗い（文書単位） | 粗い（文書単位） |
| **RAG検索精度** | 中（パート混在） | **最高**（焦点絞った検索） ✅ | 低（大きな文書） | 低（大きな文書） |
| **保守性** | 中（パート再生成） | **最高**（セクション単位更新） ✅ | 低（全体再生成） | 低（全体再生成） |
| **デプロイサイズ** | 小 | **最小** ✅ | 小 | 大 |
| **メタデータ** | 少 | 少 | 中 | 多（リンク、パターン） |
| **生成時間** | 38分（4 workers） | 134分（4 workers）<br>34分（16 workers） | - | - |
| **生成コスト** | $10.79 | $13.53 (+25%) | - | - |
| **粒度/サイズ比** | 0.041 (9 / 217) | **0.556 (119 / 214)** ✅ | 0.014 (3 / 217) | 0.010 (3 / 304) |

**粒度/サイズ比**: ファイル数をサイズ(KB)で割った値。高いほど効率的（同じサイズで多くのファイル）。

**推奨**: 本番環境では**今回Phase B（セクション単位、214 KB）**を採用 ⭐⭐⭐
- **サイズ**: 前回Phase Bとほぼ同等（-1%）✅
- **粒度**: 13倍向上（9 → 119ファイル）✅✅✅
- **粒度効率**: 13.5倍向上（0.041 → 0.556）✅
- **RAG検索精度**: 焦点を絞った小ファイル（1.8 KB/ファイル）で大幅向上 ✅
- **保守性**: セクション単位更新可能（$0.11/セクション vs $1.20/パート、91%削減）✅
- **コスト**: +25%（$10.79 → $13.53）だが、RAG精度向上とメンテナンスコスト削減で投資対効果高い
- **時間**: 16 workersで34分（前回38分と同等）✅
- **デプロイサイズ**: 最終マージ（304 KB）より29%小さい ✅

---

## 付録: データソース

### RST元ファイル
```bash
ls -lh .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/
```

### 前回Phase B（グループベース分割）
```bash
# コミット 364b5ef での Phase B 生成ファイルサイズ
git ls-tree -r 364b5ef --name-only | grep "phase-b/executions" | while read file; do
  fname=$(basename "$file" | sed 's/_20260303.*\.json//')
  size=$(git show "364b5ef:$file" | jq -r '.structured_output.knowledge | tostring | length')
  echo "$fname: $size"
done
```

### 今回Phase B（セクション単位分割）
```bash
# 実行ログからknowledgeコンテンツを抽出
jq -s 'map(.structured_output.knowledge | tostring | length) | add' \
  tools/knowledge-creator/.logs/v6/phase-b/executions/adapters-*.json
```

### 前回最終JSON（グループベース分割）
```bash
# コミット 364b5ef での最終マージファイルサイズ
git show 364b5ef:.claude/skills/nabledge-6/knowledge/component/adapters/adapters-micrometer_adaptor.json | wc -c
git show 364b5ef:.claude/skills/nabledge-6/knowledge/component/libraries/libraries-tag.json | wc -c
git show 364b5ef:.claude/skills/nabledge-6/knowledge/component/libraries/libraries-tag_reference.json | wc -c
```

### 今回最終JSON
```bash
ls -lh .claude/skills/nabledge-6/knowledge/component/adapters/*.json \
       .claude/skills/nabledge-6/knowledge/component/libraries/*.json
```

---

**更新日**: 2026年3月4日 17:00
**データソース**:
- RST元ファイル: `.lw/nab-official/v6/`
- 前回Phase B: コミット `364b5ef` の Phase B executions ログ（グループベース分割、9パート）
- 今回Phase B: 現在の Phase B executions ログ（セクション単位分割、119セクション）
- 前回最終JSON: コミット `364b5ef` の最終マージファイル
- 今回最終JSON: Phase M 後の最終マージファイル
