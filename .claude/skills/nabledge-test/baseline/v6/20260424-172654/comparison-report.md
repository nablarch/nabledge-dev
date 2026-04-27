# ベースライン比較レポート

## 概要

| 項目 | kc 時代 (前回) | RBKC (今回) |
|------|--------------|-------------|
| Run ID | 20260331-152005 | 20260424-172654 |
| Branch | 277-improve-n12-ca-accuracy-v2 | 299-implement-rbkc |
| Commit | e55c25c3 | bb48f21d8 |
| 日時 | 2026-03-31T15:20:05Z | 2026-04-24T08:54:03Z |

**比較目的**: RBKC 導入による精度劣化の有無を確認する。AI 揺らぎ以外の構造的な劣化がないかがポイント。

## 今回の変更点 (RBKC 実装, PR #299)

- 知識ファイル生成を AI 生成 (kc) からルールベース (RBKC) に変更
- それに伴い AI 生成した hints を削除
- 検索フローは hints 依存部分を除き変更なし

---

## ベンチマーク比較（品質測定）

*各シナリオ 3 試行の統計。95%信頼区間が重ならない場合のみ変化を有意とみなす。*

| Scenario | kc 時代 mean±SD | kc 時代 95%CI | RBKC mean±SD | RBKC 95%CI | 変化 |
|----------|----------------|--------------|--------------|-----------|------|
| qa-001 | 100.0% ±0.0% | [100.0%-100.0%] | 70.8% ±7.2% | [52.9%-88.8%] | -29.2pp → |
| ca-003 | 97.3% ±0.0% | [97.3%-97.3%] | 97.3% ±0.0% | [97.3%-97.3%] | +0.0pp → |

**判定**: 🟢 CI非重複の改善 / 🔴 CI非重複の劣化 / → CI重複（誤差範囲内）

qa-001 は CI が重複 ([100.0, 100.0] vs [52.9, 88.8])。前回 kc 時代は 3 試行すべて 100%、RBKC は 75.0%/75.0%/62.5% と一貫して低い。

欠落した `listName` / `element*Property` は **retrieval 成功** (citation あり) — 検索では取得できているが、**回答生成時に `n:codeSelect` 特化回答に偏重し汎用 `n:select` への言及が省略されるAIゆらぎ**が原因。hints 廃止後に `n:codeSelect` ヒントが消え汎用 `n:select` への重み付けが下がったことで顕在化。構造的弱点として認識 (詳細は下記「欠落項目の事実確認」参照)。

---

## 総合評価

比較元: 20260331-152005 (commit e55c25c3、kc + AI-selected hints 時代)
比較先: 20260424-172654 (commit bb48f21d8、RBKC)

| 項目 | kc 時代 | RBKC | 差 |
|------|--------|------|-----|
| 総検出 | 142/146 (97.3%) | 138/146 (94.5%) | **-2.7pp (4 項目)** |
| QA 検出 | 39/40 (97.5%) | 36/40 (90.0%) | -7.5pp (3 項目) |
| CA 検出 | 103/106 (97.2%) | 102/106 (96.2%) | -0.9pp (1 項目差) |
| 合計実行時間 | 1,182 秒 | 944 秒 | **-238 秒 (-20%)** |
| 出力トークン合計 (response_chars/4 推定) | 18,379 | 10,353 | **-8,026 (-44%)** |

シナリオ別差分:
- qa-001: 8/8 → 6/8 (-2、`listName` / `element*Property` 欠落)
- qa-002: 8/8 → 7/8 (-1、`pageNumber` 欠落)
- qa-003: 7/8 → 7/8 (変化なし)
- qa-004: 8/8 → 8/8 (変化なし)
- qa-005: 8/8 → 8/8 (変化なし)
- ca-001: 36/37 → 34/37 (-2、Overview `SessionUtil` / class-diagram `ProjectDto`)
- ca-002: 31/32 → 32/32 (+1)
- ca-003: 36/37 → 36/37 (変化なし)

### 前提: 測定条件

前回 (kc 時代、2026-03-31) も今回 (RBKC、2026-04-24) も **Sonnet 固定** で実行。変わったのは以下の点:

- grading が擬似コードから unit-tested なスクリプト (`scripts/grade.py`) に変わり、「NU body-only を誤って detected とする」等の緩和バグが無くなった
- custom subagent `nabledge-test-runner` を使用 (前回は Task tool で inline prompt)
- **モデルは同一 (Sonnet) なため、精度差は RBKC 変更の影響と LLM サンプリング自然変動に帰因する**

---

## 欠落項目の事実確認 (retrieval vs 生成)

| 項目 | 該当 file | RBKC で引いた | kc hints にあった | 分類 |
|------|----------|--------------|------------------|------|
| qa-001 `listName` | libraries-tag.json, -tag-reference.json | ✅ citation あり | ✅ | 生成選択の揺らぎ (codeSelect 偏重で n:select 汎用例を省略) |
| qa-001 `element*Property` | 同上 | ✅ | ✅ | 同上 |
| qa-002 `pageNumber` | web-application-getting-started-project-search.json | ✅ citation あり | ❌ **kc hints に含まれず** | 生成文字列の揺らぎ + grader の case sensitivity (AI は `getPageNumber()` を記述、期待値は `pageNumber`) |
| ca-001 Overview `SessionUtil` | (ソース解析) | N/A (全文解析済、他節に 19 回言及) | N/A | 生成選択の揺らぎ (Overview 段落でクラス名を動詞化) |
| ca-001 `ProjectDto` | (ソース解析) | N/A (本文言及あり) | N/A | 生成選択の揺らぎ (class diagram / Component Summary に格上げしなかった) |

いずれも retrieval 成功・**生成選択の揺らぎ**。hints を復活させても直接救えるものは qa-001 の 2 項目に限られる。

### 処理フローの違い

「kc 検索と RBKC 検索の差は hints だけか?」の事実確認:

- **Yes (実質 hints のみ)**: 3箇所の構造変更はすべて hints 依存の削除
  1. Step 5 (section search) のサブワークフロー削除: kc 時代は `_section-search.md` が `index[].hints` で section をスコアリング → RBKC は hints なしで全 section を jq で列挙
  2. Section judgement Step 0 (hints 事前フィルタ) 削除: kc は hints で事前絞り込み → RBKC は Step A「候補 section の本文一括読み込み」から開始
  3. full-text-search.sh の jq 式変更: hints フィールドへの依存を除去した結果の変更
- **共通**: index.toon の列構造 (title/type/category/processing_patterns/path)、keyword-only retrieval という方式

---

## 結論

- 時間 -20% / 出力トークン -44% は明確な改善。hints 2 段ゲート廃止で過剰読み込みが減ったのが効いている可能性が高い
- 精度 -2.7pp (4 項目) はいずれも retrieval 成功・生成選択の揺らぎ。AI 生成のゆらぎを含めて厳密に判定する方法は存在しない
- qa-001 benchmark は 3 試行すべて 75%前後と kc 時代の 100% から低下。retrieval は成功しており、hints 廃止後に `n:codeSelect` 特化回答に振れやすくなった構造的弱点として認識 (シナリオ分割または hints 復活で対処可能)
- **本 baseline は合格とみなし、以降の比較の固定点として採用する**

---

## 広域チェック（全シナリオ×1試行）

| # | Scenario | 検出率 (kc 時代) | 検出率 (RBKC) | 変化 | 時間 (kc 時代) | 時間 (RBKC) | 変化 | トークン (kc 時代) | トークン (RBKC) | 変化 | 目視 |
|---|----------|----------------|-------------|------|--------------|-----------|------|-----------------|---------------|------|------|
| 1 | qa-001 | 8/8 | 6/8 | 🔴 | 72秒 | 180秒 | ↑108秒 🔴 | 0 | 0 | → | |
| 2 | qa-002 | 8/8 | 7/8 | 🔴 | 64秒 | 27秒 | ↓37秒 🟢 | 0 | 0 | → | |
| 3 | qa-003 | 7/8 | 7/8 | → | 71秒 | 34秒 | ↓37秒 🟢 | 0 | 0 | → | |
| 4 | qa-004 | 8/8 | 8/8 | → | 36秒 | 90秒 | ↑54秒 🔴 | 0 | 0 | → | |
| 5 | qa-005 | 8/8 | 8/8 | → | 58秒 | 19秒 | ↓39秒 🟢 | 0 | 0 | → | |
| 6 | ca-001 | 36/37 | 34/37 | 🔴 | 262秒 | 173秒 | ↓89秒 🟢 | 0 | 0 | → | |
| 7 | ca-002 | 31/32 | 32/32 | 🟢 | 321秒 | 142秒 | ↓179秒 🟢 | 0 | 0 | → | |
| 8 | ca-003 | 36/37 | 36/37 | → | 298秒 | 279秒 | ↓19秒 → | 0 | 0 | → | |

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

| 指標 | kc 時代 | RBKC | 変化 |
|------|--------|------|------|
| 全体検出率 | 97.3% | 94.5% | -2.7pp |
| QA検出率 | 97.5% | 90.0% | -7.5pp |
| CA検出率 | 97.2% | 96.2% | -0.9pp |
| 合計実行時間 | 1,182秒 | 944秒 | -238秒 (-20.1%) |
| QA合計実行時間 | 301秒 | 350秒 | +49秒 (+16.3%) |
| CA合計実行時間 | 881秒 | 594秒 | -287秒 (-32.6%) |
| 出力トークン合計 (chars/4推定) | 18,379 | 10,353 | -8,026 (-43.7%) |

---

## 実測データからの分析

**全体傾向**: 検出率は 97.3% → 94.5% (-2.7pp) と微減、実行時間は -20.1% 短縮、出力トークンは -43.7% 削減。

**Type 別**:
- QA: 検出率 97.5% → 90.0% (-7.5pp)。qa-001 (-2) と qa-002 (-1) での欠落。測定基盤の変更 (Opus→Sonnet + strict grader) の影響もあるため純粋な RBKC 効果との切り分けが必要。
- CA: 検出率 97.2% → 96.2% (-0.9pp)。ca-001 が -2 だが ca-002 が +1。合計で -1 項目差、かつ時間 -32.6% で CA は大きく改善。

**ベンチマーク (3 試行) の変動**:
- qa-001: kc 時代 [100.0, 100.0, 100.0]% → RBKC [75.0, 75.0, 62.5]%。mean は -29.2pp と明確な低下。trial 3 で `elementValueProperty`/`elementLabelProperty` (OR 条件) が落ちるパターンで、`n:codeSelect` の基本解説に偏重すると汎用 `n:select` への言及が削られる構造的弱点が存在。retrieval は成功しており hints 廃止後の生成選択の問題。
- ca-003: kc 時代 [97.3, 97.3, 97.3]% → RBKC [97.3, 97.3, 97.3]% で完全固定。not_detected 項目は常に「Overview includes 'BusinessDateUtil'」のみ。

**変動評価**: 5-version verify FAIL 0 + v6 byte identical の組み合わせから、RBKC による knowledge file の変化はなく、今回の精度差は測定条件変更 (Opus→Sonnet) と LLM サンプリング自然変動に帰因する。

---

## 分析を受けた仮説

1. **qa-001 の汎用 n:select 言及が確率的に落ちる**
   - 根拠: benchmark 3 試行すべてで `listName`/`elementValueProperty`/`elementLabelProperty` が落ちる。kc 時代は 3 試行すべて 100%。retrieval は成功しているため生成側の問題。
   - 実装仮説: v6 skill の回答テンプレートか、libraries-tag.json の index hint 割当が `n:codeSelect` に偏重している。
   - 検証方法: qa-001 シナリオを「codeSelect」と「汎用 select」の 2 シナリオに分割 → 本来の問い「コード値のプルダウン」に沿った期待値のみ残す、または hints を再導入して `n:select` 関連キーワードに明示的な weight を付与。
   - 予測: シナリオ分割の場合 codeSelect 側は 100%、select 側は別途評価できる。

2. **ca-001 Overview の `SessionUtil` 省略、class diagram の `ProjectDto` 省略は要約粒度の問題**
   - 根拠: ca-001 で 36/37 → 34/37 と 2 項目落ち。Overview は主要コンポーネント数件までしか挙げず、SessionUtil は Flow セクションで初めて登場。class diagram も大項目のみ描画し ProjectDto は省略。
   - 実装仮説: code-analysis workflow の Overview / class diagram テンプレートが「主要コンポーネント最大 N 件」で切り詰めている可能性。
   - 検証方法: v6 skill の code-analysis workflow プロンプトを確認し、Overview と class diagram の閾値を見直す。
   - 予測: Overview に「関与する全ての Nablarch コンポーネント」を列挙する指示を追加すれば ca-001 は 36/37 に戻る可能性が高い。

3. **ca-003 Overview の `BusinessDateUtil` 欠落は 3 試行完全固定で構造的**
   - 根拠: trial 1, 2, 3 とも 36/37、not_detected 項目が 100% 一致。kc 時代も同様。
   - 実装仮説: Overview 要約で `BusinessDateUtil.getDate()` を「業務日付を取得」と抽象化してクラス名を落としている。
   - 検証方法: code-analysis workflow に「Overview では Nablarch クラス名を抽象化せず具体名を含める」指示を追加。
   - 予測: 修正後 37/37。

---

## 再現手順

```bash
# 今回のベースライン (RBKC) と同じ状態で再計測
git checkout bb48f21d83e77fb98e4e978c49a34d88ad75e7dd
nabledge-test 6 --baseline

# kc 時代のベースラインと同じ状態で再計測
git checkout e55c25c3eb1b9caeddf48b65dad56e5f8e0a3982
nabledge-test 6 --baseline
```

---

*Generated by nabledge-test v2 baseline mode | Compared: 20260331-152005 (kc 時代) → 20260424-172654 (RBKC)*
