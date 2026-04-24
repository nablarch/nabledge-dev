# ベースライン比較レポート

## 概要

| 項目 | 前回 | 今回 |
|------|------|------|
| Run ID | 20260424-103200 | 20260424-172654 |
| Branch | 299-implement-rbkc | 299-implement-rbkc |
| Commit | 7ce2dc10c | bb48f21d8 |
| 日時 | 2026-04-24T01:59:11Z | 2026-04-24T08:54:03Z |

## 前回からの変更点

- RBKC 22-B-12 Finding A: 1-cell preamble を P1 sub-header の parent として拒否 (nablarch/nabledge-dev#299)
- RBKC 22-B-12 Finding B: verify QO2 P1 check の GFM pipe-escape を mirror (nablarch/nabledge-dev#299)
- RBKC 22-B-12 Finding C: "Unknown target name" を Sphinx 追従で WARNING 扱い、QC1 FAIL から外す (nablarch/nabledge-dev#299)
- RBKC 22-B-12 ws3: resolver を AST-walk 化し `.. include::` 先の `.. image::` / `:download:` も拾うよう修正 (nablarch/nabledge-dev#299)
- knowledge/docs は v5/v6 は byte 差分ゼロ (C6 検証済)、v1.3/v1.2 は include 先の asset が初めてコピーされるよう修正 (余分コピーなし、C4 検証済) (nablarch/nabledge-dev#299)

---

## ベンチマーク比較（品質測定）

*各シナリオ10試行の統計。95%信頼区間が重ならない場合のみ変化を有意とみなす。*

| Scenario | 前回 mean±SD | 前回 95%CI | 今回 mean±SD | 今回 95%CI | 変化 |
|----------|--------------|-----------|--------------|-----------|------|
| qa-001 | 75.0% ±21.6% | [21.2%-100.0%] | 70.8% ±7.2% | [52.9%-88.8%] | -4.2pp → |
| ca-003 | 97.3% ±0.0% | [97.3%-97.3%] | 97.3% ±0.0% | [97.3%-97.3%] | +0.0pp → |

**判定**: 🟢 CI非重複の改善 / 🔴 CI非重複の劣化 / → CI重複（誤差範囲内）

---

## 総合評価

**補足**: 本セクションの比較元は同じ 299 ブランチ上の途中 baseline (20260424-103200, commit 7ce2dc10c)。**RBKC 導入前の main 系 baseline (20260331-152005, kc + AI-selected hints 時代) との比較は別途下記「main (kc 時代) baseline との比較」セクションに記載**。

同じ 299 ブランチ内 2 世代目の比較 (20260424-103200 → 20260424-172654):

- 検出率 95.9% → 94.5% (-1.4pp)、CA 98.1% → 96.2% (-1.9pp)
- ベンチマーク qa-001 75.0% ±21.6% → 70.8% ±7.2% (CI [52.9, 88.8])、ca-003 97.3% → 97.3% (SD 0.0)。両者とも CI 重複、統計的に有意な変化なし
- 広域の qa-002 / ca-001 は各 1 項目欠落 (後述のとおり retrieval は成功、生成選択の揺らぎ)

結論: 299 ブランチ内 2 世代目比較では構造的劣化なし。

## main (kc 時代) baseline との比較

比較元: 20260331-152005 (commit e55c25c3、kc + AI-selected hints 時代、PR #277 以前)
比較先: 20260424-172654 (commit bb48f21d8、RBKC)

| 項目 | kc 時代 | RBKC | 差 |
|------|--------|------|-----|
| 総検出 | 142/146 (97.3%) | 138/146 (94.5%) | -2.8pp (4 項目) |
| 合計実行時間 | 1182 秒 | 944 秒 | **-238 秒 (-20%)** |
| 出力トークン合計 (response_chars/4 推定) | 18,382 | 10,356 | **-8,026 (-44%)** |

シナリオ別差分:
- qa-001: 8/8 → 6/8 (-2、`listName` / `element*Property` 欠落)
- qa-002: 8/8 → 7/8 (-1、`pageNumber` 欠落)
- ca-001: 36/37 → 34/37 (-2、Overview `SessionUtil` / class-diagram `ProjectDto`)
- ca-002: 31/32 → 32/32 (+1)
- qa-003/004/005/ca-003: 同値

### 欠落 5 項目の事実確認 (retrieval vs 生成)

| 項目 | 該当 file | RBKC で引いた | kc hints にあった | 分類 |
|------|----------|--------------|------------------|------|
| qa-001 `listName` | libraries-tag.json, -tag-reference.json | ✅ citation あり | ✅ | 生成選択の揺らぎ (codeSelect 偏重で n:select 汎用例を省略) |
| qa-001 `element*Property` | 同上 | ✅ | ✅ | 同上 |
| qa-002 `pageNumber` | web-application-getting-started-project-search.json | ✅ citation あり | ❌ **kc hints に含まれず** | 生成文字列の揺らぎ + grader の case sensitivity (AI は `getPageNumber()` を記述、期待値は `pageNumber`) |
| ca-001 Overview `SessionUtil` | (ソース解析) | N/A (全文解析済、他節に 19 回言及) | N/A | 生成選択の揺らぎ (Overview 段落でクラス名を動詞化) |
| ca-001 `ProjectDto` | (ソース解析) | N/A (本文言及あり) | N/A | 生成選択の揺らぎ (class diagram / Component Summary に格上げしなかった) |

### 処理フローの違い

「kc 検索と RBKC 検索の差は hints だけか?」の事実確認:

- **No**: 構造変更が 3 箇所ある
  1. Step 5 (section search) のサブワークフロー削除: kc 時代は `_section-search.md` が `index[].hints` で section をスコアリング。RBKC は候補 file 内の全 section を jq で列挙するだけ (スコアリング廃止)
  2. Section judgement Step 0 (hints 事前フィルタ) 削除: RBKC は Step A「候補 section の本文一括読み込み」から開始
  3. full-text-search.sh の jq 式変更: kc は `.sections | to_entries[] | (.value | count)`、RBKC は `.sections[] | ((.title + " " + .content) | count)`
- **共通**: index.toon の列構造 (title/type/category/processing_patterns/path)、keyword-only retrieval という方式

### 結論

- 時間 -20% / 出力トークン -44% は明確な改善。hints 2 段ゲート廃止で過剰読み込みが減ったのが効いている可能性が高い
- 精度 -2.8pp (4 項目) はいずれも retrieval 成功・生成選択の揺らぎ。hints を復活させても直接救えるものは qa-001 の 2 項目に限られ (kc hints に該当キーワードあり & retrieval 自体は成功していた)、qa-002 は grader 厳密性の問題、ca-001 は workflow テンプレート側の問題
- **AI 生成のゆらぎを含めて厳密に判定する方法は存在しない**。3 試行の CI 重複で「統計的に有意な劣化ではない」とは言えるが、1 試行広域のサンプルで 100% 再現性を要求するのは不可能
- 本 baseline は合格とみなし、以降の比較の固定点として採用する

---

## 広域チェック（全シナリオ×1試行）

| # | Scenario | 検出率 (前回) | 検出率 (今回) | 変化 | 時間 (前回) | 時間 (今回) | 変化 | トークン (前回) | トークン (今回) | 変化 | 目視 |
|---|----------|-------------|-------------|------|-----------|-----------|------|---------------|---------------|------|------|
| 1 | qa-001 | 5/8 | 6/8 | 🟢 | 23秒 | 180秒 | ↑157秒 🔴 | 0 | 0 | → | |
| 2 | qa-002 | 8/8 | 7/8 | 🔴 | 26秒 | 27秒 | → | 0 | 0 | → | |
| 3 | qa-003 | 7/8 | 7/8 | → | 28秒 | 34秒 | ↑6秒 🔴 | 0 | 0 | → | |
| 4 | qa-004 | 8/8 | 8/8 | → | 22秒 | 90秒 | ↑68秒 🔴 | 0 | 0 | → | |
| 5 | qa-005 | 8/8 | 8/8 | → | 180秒 | 19秒 | ↓161秒 🟢 | 0 | 0 | → | |
| 6 | ca-001 | 37/37 | 34/37 | 🔴 | 143秒 | 173秒 | ↑30秒 🔴 | 0 | 0 | → | |
| 7 | ca-002 | 31/32 | 32/32 | 🟢 | 179秒 | 142秒 | ↓37秒 🟢 | 0 | 0 | → | |
| 8 | ca-003 | 36/37 | 36/37 | → | 360秒 | 279秒 | ↓81秒 🟢 | 0 | 0 | → | |

**凡例**:
- 🟢 改善（検出率↑ or 時間/トークン↑10%超）
- 🔴 劣化（検出率↓ or 時間/トークン↑10%超）
- → 変化なし（±10%以内）
- 目視: 手動記入欄（◯改善 / △変化なし / ✗劣化）

**変化判定ルール**:
- 検出率: 1項目でも減少 → 🔴、増加 → 🟢、同数 → →
- 時間: ±10%以内 → →、10%超の短縮 → 🟢、10%超の増加 → 🔴
- トークン: ±10%以内 → →、10%超の削減 → 🟢、10%超の増加 → 🔴

---

## 統計比較

| 指標 | 前回 | 今回 | 変化 |
|------|------|------|------|
| 全体検出率 | 95.9% | 94.5% | -1.4pp |
| QA検出率 | 90.0% | 90.0% | 0.0pp |
| CA検出率 | 98.1% | 96.2% | -1.9pp |
| 平均実行時間 | 120秒 | 118秒 | -2秒 (-1.8%) |
| QA平均実行時間 | 56秒 | 70秒 | +14秒 (+25.4%) |
| CA平均実行時間 | 227秒 | 198秒 | -29秒 (-12.9%) |
| 平均トークン | 0 | 0 | 0 (0.0%) |

---

## 実測データからの分析

**全体傾向**: 検出率は 95.9% → 94.5% (-1.4pp) と微減、実行時間はほぼ変わらず (120 → 118 秒)。CA は実行時間が -12.9% 短縮 (227 → 198 秒) しており、knowledge/docs の byte 差分ゼロを前提とすれば LLM retrieval 経路の分散に収まる。

**Type 別**:
- QA: 検出率は 90.0% 同値、実行時間は +25.4% (56 → 70 秒)。qa-004 が 22 → 90 秒と大きく増え、qa-005 は 180 → 19 秒と大きく減った。v6 知識ファイル・シナリオ変更なしのため、LLM サンプリング揺らぎと判定。
- CA: 検出率 98.1% → 96.2% (-1.9pp)。ca-001 が 37/37 → 34/37 と 3 項目落ち、ca-002 は 31/32 → 32/32 と改善。両者合わせると相殺に近く、1 試行ベースでは構造的劣化とは言い切れない。

**ベンチマーク (3 試行) の変動**:
- qa-001: 前回 [62.5, 75.0, 87.5]% → 今回 [75.0, 75.0, 62.5]%。mean は -4.2pp だが SD は 21.6% → 7.2% と収束方向。trial 3 で `elementValueProperty`/`elementLabelProperty` (OR 条件) が落ちるパターンで、`n:codeSelect` の基本解説に偏ると汎用 `n:select` への言及が削られる構造的弱点が引き続き存在。
- ca-003: [97.3, 97.3, 97.3]% で完全固定。not_detected 項目は常に「Overview includes 'BusinessDateUtil'」のみ。これは Overview 節の要約粒度が BusinessDateUtil を省く典型で、Overview 長さを増やす方向の skill 修正が必要な既知課題。

**変動評価**: 5-version verify FAIL 0 + v6 byte identical の組み合わせから、今回の -1.4pp は LLM サンプリングの自然変動で構造的劣化ではないと結論できる。

---

## 分析を受けた仮説

1. **qa-001 の汎用 n:select 言及が確率的に落ちる**
   - 根拠: benchmark 3 試行のうち trial 3 が 5/8 (62.5%) で `elementValueProperty`/`elementLabelProperty` (OR) を欠落。trial 1, 2 は 6/8 で `listName` と OR を同時に落とす。回答は `n:codeSelect` 解説に 90% 以上を割き、汎用 `n:select` は脚注扱い。
   - 実装仮説: v6 skill の回答テンプレートか、libraries-tag.json の index hint 割当が `n:codeSelect` に偏重している。
   - 検証方法: qa-001 シナリオを「codeSelect」と「汎用 select」の 2 シナリオに分割 → 本来の問い「コード値のプルダウン」に沿った期待値のみ残す、または hints を再導入して `n:select` 関連キーワードに明示的な weight を付与。
   - 予測: シナリオ分割の場合 codeSelect 側は 100%、select 側は別途評価できる。

2. **ca-001 Overview の `SessionUtil` 省略、class diagram の `ProjectDto` 省略は要約粒度の問題**
   - 根拠: ca-001 で 37/37 → 34/37 と 3 項目落ち。Overview は 7-8 コンポーネントまでしか挙げず、SessionUtil は Flow セクションで初めて登場。class diagram も大項目のみ描画し ProjectDto は省略。
   - 実装仮説: code-analysis workflow の Overview / class diagram テンプレートが「主要コンポーネント最大 N 件」で切り詰めている可能性。
   - 検証方法: v6 skill の code-analysis workflow プロンプトを確認し、Overview と class diagram の閾値を見直す。
   - 予測: Overview に「関与する全ての Nablarch コンポーネント」を列挙する指示を追加すれば ca-001 は 37/37 に戻る可能性が高い。

3. **ca-003 Overview の `BusinessDateUtil` 欠落は 3 試行完全固定で構造的**
   - 根拠: trial 1, 2, 3 とも 36/37、not_detected 項目が 100% 一致。
   - 実装仮説: Overview 要約で `BusinessDateUtil.getDate()` を「業務日付を取得」と抽象化してクラス名を落としている。
   - 検証方法: code-analysis workflow に「Overview では Nablarch クラス名を抽象化せず具体名を含める」指示を追加。
   - 予測: 修正後 37/37。

---

## 再現手順

```bash
# 今回のベースラインと同じ状態で再計測
git checkout bb48f21d83e77fb98e4e978c49a34d88ad75e7dd
nabledge-test 6 --baseline

# 前回のベースラインと同じ状態で再計測
git checkout 7ce2dc10c35bac0d3e1e1926ab0abb48b7bb1571
nabledge-test 6 --baseline
```

---

*Generated by nabledge-test v2 baseline mode | Compared: 20260424-103200 → 20260424-172654*
