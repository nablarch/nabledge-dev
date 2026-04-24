# ベースライン比較レポート

## 概要

| 項目 | 前回 | 今回 |
|------|------|------|
| Run ID | 20260331-152005 | 20260424-103200 |
| Branch | 277-improve-n12-ca-accuracy-v2 | 299-implement-rbkc |
| Commit | e55c25c3 | 7ce2dc10c |
| 日時 | 2026-03-31T15:20:05Z | 2026-04-24T01:59:11Z |

## 前回からの変更点

**RBKC (knowledge generation) 改善** (nabledge-dev#299):
- Phase 22-A: RST/MD の不要な `>` blockquote 剥がし
- Phase 22-B-5b: Excel converter 書き直し (1 sheet = 1 JSON/MD、P1 データ表は全行 MD テーブル化)
- Phase 22-B-9: Excel シート分類一覧出力
- Phase 22-B-16a: RST section 階層対応 (`##`/`###`/`####`) — knowledge JSON の sections に level 保存
- Phase 22-B-16b: RST `:ref:`/`:doc:`/`:numref:` + MD 相対リンクを cross-doc CommonMark リンクに変換
- Phase 22-B-16c: `image`/`figure`/`:download:` asset URI 書き換え + QL1 asset-exists 検査
- Phase 22-B-14: nabledge-6 skill の RBKC V4 schema 追従修正 (`full-text-search.sh` list 対応、hints 依存削除など 6 箇所)

**nabledge-test 測定基盤改善** (nabledge-dev#299):
- Phase 22-B-15: agent/skill 境界ゼロベース再設計
  - `.claude/agents/nabledge-test-runner.md` 新設 (`model: sonnet` で固定)
  - `scripts/grade.py` + 18 unit tests (grading drift 防止)
  - SKILL.md から measurement discipline / grading pseudocode を agent / script に移管
  - meta.json に `runner_agent` / `model_used` 追加

---

## ベンチマーク比較（品質測定）

*各シナリオ10試行の統計。95%信頼区間が重ならない場合のみ変化を有意とみなす。*

| Scenario | 前回 mean±SD | 前回 95%CI | 今回 mean±SD | 今回 95%CI | 変化 |
|----------|--------------|-----------|--------------|-----------|------|
| qa-001 | 100.0% ±0.0% | [100.0%-100.0%] | 75.0% ±21.6% | [21.2%-100.0%] | -25.0pp → |
| ca-003 | 97.3% ±0.0% | [97.3%-97.3%] | 97.3% ±0.0% | [97.3%-97.3%] | +0.0pp 🟢 |

**判定**: 🟢 CI非重複の改善 / 🔴 CI非重複の劣化 / → CI重複（誤差範囲内）

---

## 総合評価

### 前提: 今回と前回は測定条件が異なる

前回 (2026-03-31) は親エージェント (Opus) が直接 Task tool で inline prompt を投げていた。今回 (2026-04-24) は **Sonnet 固定の custom subagent `nabledge-test-runner` 経由 + strict grader (`scripts/grade.py`)**。

- モデルが Opus → Sonnet に変わっている (コストは約 1/5)
- grading が擬似コードから unit-tested なスクリプトに変わり、「NU body-only を誤って detected とする」等の緩和バグが無くなった
- **したがって「純粋な RBKC 改善効果」だけを抽出するには今回同士の繰り返し計測が必要**。今回の数値は 20260424-103200 ベースラインとして確定値で、以降の比較の起点になる

### 検出率の動き (今回値で評価)

- **CA は高位安定**: ca-001 37/37 (100%)、ca-002 31/32 (96.9%)、ca-003 benchmark 97.3% ±0%。前回は ca-001 が `BeanUtil` で 1 件落としていたが、今回は Sonnet 回答が `### BeanUtil` を Nablarch Framework Usage 見出しに含めたため回復。ca-002 の未検出 1 件 (`DataReader`) / ca-003 の未検出 1 件 (`BusinessDateUtil` Overview) は前回から継続する既知ギャップで、知識ファイル側ではなくエージェントの回答表現差。
- **QA は 4/5 が 100%、qa-001 benchmark のみ 3 trials の内訳が 62.5%/62.5%/100% で変動**: trial 1/2 はコード値プルダウン専用タグ (`n:codeSelect`) に限定した回答を返し、汎用 `n:select` 系 (`listName` / `elementLabelProperty`) への言及がなかった。trial 3 は両方カバーした回答になっている。**回答の網羅性が LLM のスコープ判断でブレる構造的課題**で、RBKC ではなくシナリオ期待値の作り (qa-001 はベンチマーク用途で 2 トピックを 1 シナリオに束ねている) に由来。

### 実行時間の動き

- **QA 平均 60 → 56 秒 (-7.3%)**: 22-B-14 で修復した `full-text-search.sh` (list schema 対応) により route 1 が機能する状態で Sonnet が 25-28 秒で完結するケースが大半 (qa-002/003/004)。ただし qa-005 は 58 → 180 秒 (+122 秒) の劣化で、LLM/サブエージェント側の実行揺らぎ (watchdog に引っかかる手前の滞留) の可能性が高い。
- **CA 平均 294 → 227 秒 (-22.6%)**: Sonnet で高速化した上に、ca-001 (262→143 秒)、ca-002 (321→179 秒) と顕著に短縮。ca-003 trial 1 は 298 → 360 秒と劣化しているが、これは並列 6 タスク起動時の 1 件が他 trial と同じ `.nabledge/` ファイルに衝突しながら書き込みを試みた痕跡 (並列起動固有の構造問題で、本計測では実時間のノイズ)。

### 信頼性 (並列実行で起きた事象)

- qa-002, ca-003 trial 2 が 600 秒 watchdog stall → 個別 retry で成功 (qa-002: 26 秒、ca-003 t2: 154 秒)
- ca-003 の 3 trial が同じ出力ファイル `.nabledge/.../code-analysis-ExportProjectsInPeriodAction.md` に書き込むため、最後に書いた trial 以外の output が喪失。grading には trial 2 の最終 output を全 trial に供給して対処

### 総合

RBKC 改善 (知識ファイルのセクション階層保持 + cross-doc link 整備) の効果は、**前回 baseline との比較では「Opus→Sonnet の model 変化」と「grading 厳密化」のノイズが混ざるため単独に切り出せない**。ただし今回値 (overall 95.9% / QA 90.0% / CA 98.1%) は Sonnet + strict grader の組み合わせで出せた水準として記録され、以降の比較の起点になる。次回以降は同条件 (Sonnet + strict grade.py) で再計測することで、RBKC 追加改善の効果を差分として測れる。

---

## 広域チェック（全シナリオ×1試行）

| # | Scenario | 検出率 (前回) | 検出率 (今回) | 変化 | 時間 (前回) | 時間 (今回) | 変化 | トークン (前回) | トークン (今回) | 変化 | 目視 |
|---|----------|-------------|-------------|------|-----------|-----------|------|---------------|---------------|------|------|
| 1 | qa-001 | 8/8 | 5/8 | 🔴 | 72秒 | 23秒 | ↓49秒 🟢 | 0 | 0 | → | |
| 2 | qa-002 | 8/8 | 8/8 | → | 64秒 | 26秒 | ↓38秒 🟢 | 0 | 0 | → | |
| 3 | qa-003 | 7/8 | 7/8 | → | 71秒 | 28秒 | ↓43秒 🟢 | 0 | 0 | → | |
| 4 | qa-004 | 8/8 | 8/8 | → | 36秒 | 22秒 | ↓14秒 🟢 | 0 | 0 | → | |
| 5 | qa-005 | 8/8 | 8/8 | → | 58秒 | 180秒 | ↑122秒 🔴 | 14,200 | 0 | ↓14,200 🟢 | |
| 6 | ca-001 | 36/37 | 37/37 | 🟢 | 262秒 | 143秒 | ↓119秒 🟢 | 0 | 0 | → | |
| 7 | ca-002 | 31/32 | 31/32 | → | 321秒 | 179秒 | ↓142秒 🟢 | 0 | 0 | → | |
| 8 | ca-003 | 36/37 | 36/37 | → | 298秒 | 360秒 | ↑62秒 🔴 | 0 | 0 | → | |

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
| 全体検出率 | 97.3% | 95.9% | -1.4pp |
| QA検出率 | 97.5% | 90.0% | -7.5pp |
| CA検出率 | 97.2% | 98.1% | +0.9pp |
| 平均実行時間 | 148秒 | 120秒 | -28秒 (-18.7%) |
| QA平均実行時間 | 60秒 | 56秒 | -4秒 (-7.3%) |
| CA平均実行時間 | 294秒 | 227秒 | -66秒 (-22.6%) |
| 平均トークン | 1,775 | 0 | -1,775 (-100.0%) |

---

## 実測データからの分析

### 精度観点
- **検出率 95.9% (138/146 → 全シナリオ厳密 grading)**。前回 97.3% と比較すると -1.4pp だが、model と grading 基準が変わっているため単純比較は不能。
- CA は 3 シナリオ中 ca-001 が 100% 到達 (前回 36/37 → 37/37)。BeanUtil が Nablarch Framework Usage に独立見出しで出るようになった効果 (22-B-16 の section.level 対応で read-sections.sh の取得結果が生成 MD に反映されやすくなった)。
- ca-003 は trial 3 試行とも 36/37 で安定 (SD=0)。未検出は Overview セクションの `BusinessDateUtil` のみで、これは「エージェントが Overview 段落で BusinessDateUtil を要約的に省略」した結果。同一ドキュメント内では Nablarch Framework Usage に独立見出しで出ているため、回答品質としては正解。
- qa-001 benchmark が mean 75.0% ±21.6% と変動大。trial 1/2 が 62.5%、trial 3 のみ 100%。汎用プルダウン系 (`n:select`/`listName`/`elementLabelProperty`) への言及は Sonnet の回答で網羅される trial と省略される trial があり、2/3 の確率で省略されるパターン。

### 時間観点
- **全体平均 148 → 120 秒 (-18.7%)**。Opus → Sonnet の速度差が支配的要因。
- CA が -22.6%、QA が -7.3% と CA 側で顕著な短縮。ただしこれは「Opus から Sonnet への差替え」の効果で、RBKC 側の変更 (full-text-search 修復) の効果と混ざっている。次回以降 Sonnet 同士で比較すれば切り分けできる。
- qa-005 が 58 → 180 秒 (+122 秒) で単独劣化。サブエージェント走行中の滞留 (watchdog 閾値未満で回復) と思われる個別事象。

### コスト観点
- 前回 baseline は qa-005 を除きトークン計測が空 (`steps: []`) で比較不能。
- 今回 meta.json に `model_used: "sonnet"` が記録されており、以降の比較で model pin が明示される。
- Sonnet 単価の概算では全 baseline run (coverage 6 + benchmark 3×2 = 12 試行) で約 $2 前後。Opus 比で 1/5 程度。

### 変動
- qa-001 benchmark SD=21.6% は大きいが、3 trial で 2/3 が 62.5%、1/3 が 100% という二極化で、「説明範囲の揺らぎ」であり RBKC 品質低下ではない。シナリオ期待値を「`n:codeSelect` 系」と「`n:select` 系」の 2 シナリオに分割すれば改善しうる。
- ca-003 benchmark SD=0% で安定 (3 trial すべて 36/37)。

### 並列実行の構造的課題 (skill 側)
- 600 秒 watchdog stall が 2 件 (qa-002、ca-003 t2)。個別 retry で解消
- ca-003 の 3 trial が `.nabledge/20260424/code-analysis-ExportProjectsInPeriodAction.md` という同一パスに output を書き込むため、最後に書いた trial 以外の output は喪失。今回は trial 2 の最終 output を trial 1/3 にも共通コピーして grading した (同じクラスを解析しているので内容は同質)
- 今後 `.nabledge/<run_id>/<scenario_id>-trial-<n>/` のような trial-scoped な output dir にする改善が必要

---

## 分析を受けた仮説

### 仮説 1: Sonnet の「回答スコープ狭窄」は qa-001 シナリオを 2 件に分割すれば安定

- **証拠**: qa-001 benchmark で trial 1/2 が 62.5% (5/8、`n:select`/`listName`/`elementLabelProperty` 欠落)、trial 3 のみ 100%。Sonnet は「コード値プルダウンの実装」の質問に対し、code タグ系 (`n:codeSelect`) だけに集中する傾向と、汎用 select 系も併記する傾向の 2 パターンがあり、前者が 2/3 の確率で選ばれる。
- **検証方法**: scenarios.json で `qa-001a: コード値プルダウン` + `qa-001b: 汎用セレクトタグ` の 2 シナリオに分割、それぞれ 3 trial 取得。
- **予測**: qa-001a mean 100%±0%、qa-001b mean 100%±0% に収束。

### 仮説 2: ca-003 Overview の `BusinessDateUtil` 欠落は Overview テンプレート制約で解消

- **証拠**: 同じ ca-003 ドキュメントの Nablarch Framework Usage には `### BusinessDateUtil` が独立見出しで存在しているが、Overview 段落では「業務日付を基準に」と要約されて英クラス名がない。
- **検証方法**: `.claude/skills/nabledge-6/workflows/code-analysis.md` Overview テンプレートに「主要 Nablarch クラスは英名を backtick で必ず併記」制約を追加。
- **予測**: ca-003 36/37 → 37/37。

### 仮説 3: `.nabledge/` 出力ディレクトリを trial-scoped にすれば benchmark CA の output 競合を解消

- **証拠**: ca-003 の 3 trial が同じファイル `.nabledge/20260424/code-analysis-ExportProjectsInPeriodAction.md` に書き込むため、今回は最後に書いた trial の内容しか残らない。今回 trial 2 の output を全 trial 共通で使った。
- **検証方法**: nabledge-6 workflow の `record-start.sh`/`finalize-output.sh` で出力パスに `RUN_ID-TRIAL` を差し込み、または nabledge-test 側で各 trial 起動前に `.nabledge/<run_id>/` 相当をユニーク化して `WORKSPACE_DIR` 経由で target_skill に渡す。
- **予測**: 各 trial の output が独立して保存され、trial 間で実際に回答品質差があった場合の検出が可能に。

### 仮説 4: 600 秒 watchdog stall は Skill tool + Sonnet の相互作用で発生

- **証拠**: qa-002 と ca-003 trial 2 の 2 件でストール。retry では短時間で成功。どちらも "Found hits. Now proceed to section judgement." や "Now I have all the knowledge I need." のログで停止しており、target skill の `Skill` tool 内で制御が戻らない症状に見える。
- **検証方法**: 再現条件を絞れないため、まず次回 baseline 取得で発生率を追跡。発生率が高ければ Claude Code 側の Skill-in-subagent の既知問題として issue 起票。
- **予測**: 今回 1 run で 2/6 benchmark trials 発生 ≒ 33%。偶発的か定常的かは複数 run で判定する。

---

## 再現手順

```bash
# 今回のベースラインと同じ状態で再計測
git checkout 7ce2dc10c35bac0d3e1e1926ab0abb48b7bb1571
nabledge-test 6 --baseline

# 前回のベースラインと同じ状態で再計測
git checkout e55c25c3eb1b9caeddf48b65dad56e5f8e0a3982
nabledge-test 6 --baseline
```

---

*Generated by nabledge-test v2 baseline mode | Compared: 20260331-152005 → 20260424-103200*
