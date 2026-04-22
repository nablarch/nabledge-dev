# Tasks: Benchmark + streamlined search flow

**Issue**: #307
**Branch**: 307-benchmark-search-flow
**PR**: #310 (draft)
**Updated**: 2026-04-22 (30件の模範回答作成完了。次は Stage 2 スクリプト判定の実装)

## 計測設計（ユーザー合意済み）

### 検索フロー（ファセット検索へピボット）

旧フロー（AI キーワード抽出 → BM25 全文検索 → AI section 判定）は「ドキュメント語彙に寄せる方法」の改善余地が「出来レース」の懸念を招くため廃止。

新フロー:

```
質問
  ↓ AI-1 (facet 抽出: type / category のみ、2軸)
  ↓ 機械 filter (index.toon を type×category で AND 絞込)
  ↓ AI-2 (title + path から section 選択) ※初回は hints 渡さず
  ↓ read-sections
  ↓ 最終回答
```

※ 2軸に簡略化した理由: index.toon の `processing_patterns` 列は `type=processing-pattern` の 70 行で category の複製、残り 225 行は空 — 軸としての情報量ゼロ。処理パターンは「type=processing-pattern ∧ category={web-application|nablarch-batch|...}」で完全に表現できる。5 シナリオで simulation 済み (type×category のみで recall=1.0、候補 56–124 行)。

設計書: [review-by-prompt-engineer-stage1-facet-design.md](review-by-prompt-engineer-stage1-facet-design.md)

### 3段階の粒度で別コンテキスト独立判定

| 段階 | 測定対象 | 判定方法 | 判定コンテキスト |
|------|---------|---------|----------------|
| Stage 1 | AI-1 facet 抽出の精度 | script: `expected_facets` との Jaccard（軸別） | メイン内完結 |
| Stage 2 | 機械 filter の候補選び | **LLM judge (別 sub-agent)** が 4段階判定 | 別 sub-agent |
| Stage 3 | AI-2 section 選択 + 最終回答 | **LLM judge (別 sub-agent)** が回答品質を 4段階判定 | 別 sub-agent |

### Stage 2 / 3 LLM judge レベル定義

| レベル | 定義 |
|-------|------|
| 3 (full) | 候補/回答だけで質問に十分答えられる。情報が揃っている |
| 2 (partial) | 主要な部分は答えられるが、一部補足情報が足りない |
| 1 (insufficient) | 関連ファイル/回答はあるが、答えるには情報不足 |
| 0 (miss) | 関連ファイル/回答が含まれていない。答えようがない |

合格基準は設けない。全 Round 後、結果を見てユーザーと認識合わせ → 次進むか改善するか判断。

### Round 運用

1. 計測実行（5件 × 対象 Stage）
2. 実行ログを `.results/` に全保存、サマリを `.work/00307/rounds/stage{N}-round{M}.md` に記録
3. **Prompt Engineer Expert レビュー**（結果 + 改善案）
4. AI が「結果 + 改善案 + どうするかの提案」をユーザーに提示
5. ユーザー合意 → 修正 → 次 Round

### パターン網羅サンプル 5件（ユーザー承認済み）

| id | カテゴリ | 狙い |
|----|---------|------|
| review-01 | review / アーキテクチャ | 失敗ケース再現性（前回 recall 40%） |
| review-04 | review / セキュリティ | 遅延主原因（前回 452秒） |
| impact-01 | impact / 影響分析 | 横断トピック |
| req-02 | req / 要件 | 単純な機能問い合わせ |
| req-09 | req | expected_sections 0件（「情報なし」挙動 / out-of-scope） |

### スケーリング段取り

1. **5件でパターン網羅** — Stage 1 → Stage 2 → Stage 3 各 Round を回し改善
2. **15件で中間確認** — 5件で確定したプロンプトで拡張
3. **30件ベースライン** — 最終計測

### 実行と出力

- Runner: `tools/benchmark/run.py`
- モデル: Round 2 初回に **Haiku vs Sonnet** を同じ5件で並走 → 結果を見て固定
- Output: `claude -p --output-format stream-json` で AI-1 / AI-2 / judge すべての実行ログを保存
- Permission: `--permission-mode bypassPermissions`
- Prompt 渡し: stdin

### 出力ディレクトリ構造

```
tools/benchmark/.results/{timestamp}-stage{N}-{model}/
├── summary.json                     # 集計 (mean/median/min/max)
├── summary.md                       # 人間用レポート
└── {scenario_id}/
    ├── ai1_facet_extract.json       # AI-1 stream-json 全ログ
    ├── ai1_result.json              # AI-1 抽出ファセット
    ├── filter_result.json           # filter 候補 + fallback_used
    ├── ai2_section_select.json      # AI-2 stream-json 全ログ
    ├── ai2_result.json              # AI-2 選択セクション
    ├── judge_stage2.json            # Stage 2 LLM judge (level + 理由)
    ├── judge_stage3.json            # Stage 3 LLM judge (level + 理由)
    └── final_answer.md              # 最終回答テキスト
```

### Round 記録ファイル

`.work/00307/rounds/stage{N}-round{M}.md`:

1. 計測条件（date / sample / model / options / prompt / results dir へのリンク）
2. 結果サマリ（Stage 1 Jaccard / Stage 2 level / Stage 3 level / cost / time、シナリオ別）
3. Prompt Engineer Expert Review へのリンク
4. 改善提案と判断（Implement / Defer / Reject）
5. 次 Round への変更

## ユーザー決定済み方針（2026-04-22）

| # | 決定 |
|---|------|
| 1 | Round 2 初回に **Haiku vs Sonnet 5件比較** → 勝った方に固定 |
| 2 | **v6 で合格後、同 PR で v1.2 / 1.3 / 1.4 / 5 に複製** |
| 3 | Stage 2 / 3 は **LLM judge（別 sub-agent）で 4段階レベル判定**。合格基準は設けずユーザーと認識合わせ |
| 4 | AI-2 には初回 **title + path のみ**（hints 渡さず）。駄目なら hints 追加 |
| 5 | `--output-format stream-json` で **AI-1 / AI-2 / judge の実行ログを全保存** |

## In Progress

### 正解データ作成 + 採点方式の切り替え

**背景**:
Stage 2 / Stage 3 の LLM judge は正解データなしで Sonnet が自己推定採点していた。
Nablarch の知識を持っているかどうか不明な LLM の推測判断であり、信頼できない。
正解データ（模範回答文）を作り、それとの照合に切り替える。

**方針（ユーザー合意済み 2026-04-22）**:
- 正解データ = **模範回答文（自然文）を1シナリオ1ファイル**。key_facts のリスト化はしない
- 回答文の citation から「正解パス集合」が機械抽出できる
- **Stage 2 はスクリプト判定**（正解パスが filter 候補に含まれるかを `in` で判定）→ `judge_stage2.md` は廃止
- **Stage 3 のみ LLM judge**（模範回答と生成回答を並べて 4段階判定）
- **順序**: Stage 2 を先に全 30件チェック → 落ちた件数が多ければ Stage 3 judge には進まず、フロー改善（filter / facet / AI-2）に戻る
- 既存の `20260422-143411-stage3-sonnet/` の `final_answer.md` / `filter_result.json` を流用、再計測不要

**実行結果の保存場所**:
- 30件ベースライン: `tools/benchmark/.results/20260422-143411-stage3-sonnet/`
- 30件ベースライン保存: `tools/benchmark/baseline/20260422-stage3-sonnet/`
- 各シナリオの回答テキスト: `{result_dir}/{scenario_id}/final_answer.md`
- 各シナリオの filter 候補: `{result_dir}/{scenario_id}/filter_result.json`
- 各シナリオの cited: `{result_dir}/{scenario_id}/ai3_result.json`

**Steps:**
- [x] review-01 の模範回答を1本書いて format / 粒度 / 長さ感を確定
- [x] `qa-v6-answers/README.md` に format spec を明文化（in-scope / out-of-scope / citation regex / ドリフト対策ルール）
- [x] 残り 29 件の模範回答を作成（review-02..10 / impact-01..10 / req-01..10）
- [x] Prompt Engineer スポットレビュー 3回実施（review-02..05 / impact-01..10 / req-01..10）、指摘は全て反映
- [x] Stage 2 スクリプト判定を実装
  - `tools/benchmark/grading/reference_answer.py`（citation 抽出 + スクリプト採点）
  - `tools/benchmark/score_stage2.py`（既存 `.results/` を再利用した judge-only モード）
  - TDD: `tests/test_reference_answer.py` 15 tests → 全 GREEN (合計 34 tests)
- [x] Stage 2 を全 30件で実行 → level=3 率 25/30 (83%)、level≥2 率 27/30 (90%)
  - 結果: `tools/benchmark/.results/20260422-143411-stage3-sonnet/stage2_script.json`
  - 記録: `.work/00307/rounds/stage2-script-round1.md`
- [DECISION: Stage 2 合格率 83% を受け入れ Stage 3 judge に進むか、先に facet 抽出改善するか]
- [ ] (Stage 2 OK なら) `judge_stage3.md` を「模範回答との比較」方式に改訂
- [ ] (Stage 2 OK なら) Stage 3 judge を合格分で再実行
- [ ] 結果を `.work/00307/rounds/` に記録

### Stage 3 section 選択 + 最終回答 + Round 制

**Steps:**
- [x] `tools/benchmark/prompts/stage3_section_select.md` 作成（AI-2）
- [x] `prompts/stage3_answer.md` 作成（AI-3）
- [x] `prompts/judge_stage3.md` 作成（別 sub-agent、4段階）
- [x] `run.py` に Stage 3 pipeline 追加 (AI-2 → read-sections → AI-3 → judge)
- [x] Prompt Engineer Review（pre-run）→ `.work/00307/review-by-prompt-engineer-stage3-prompts.md`
- [x] Stage 3 Round 1 計測（5件）→ 全 judge=3
- [x] 結果を `.work/00307/rounds/stage3-round1.md` に記録
- [x] Prompt Engineer Review（Round 1 結果）→ `.work/00307/review-by-prompt-engineer-stage3-round1.md`
- [x] Review High fix 適用（anti-verbosity / AI-2 soft-cap / synthesis grounding）

## Done (this session)

### Stage 1 Round 2（facet 抽出）— AI-1 を先に実測して設計判断

**Status**: 旧 Round 2 案（index.toon 語彙 anchor）は廃止。ファセット検索ピボット設計はエキスパートレビュー完了。ただし **設計書は机上**なので、mapping 拡張等の仕込みに入る前に、まず **AI-1 facet 抽出プロンプトだけを 5件で実測** → 出てきた facet を見て「filter が機能しそうか」「processing_patterns 列を埋める必要があるか」を実データで判断する自然な順序に補正（2026-04-22）。

**Steps:**
- [x] Round 1: 5件実行 → `.work/00307/rounds/stage1-round1.md`
- [x] Round 1: Prompt Engineer Expert Review → `.work/00307/review-by-prompt-engineer-stage1-round1.md`
- [x] Round 1: 改善提案をユーザー提示、議論
- [x] ファセット検索へのピボット設計 → `.work/00307/review-by-prompt-engineer-stage1-facet-design.md`
- [x] ユーザー決定（モデル比較 / rollout / judge レベル / hints / stream-json）
- [x] `tools/benchmark/prompts/stage1_facet.md` 作成（2軸: type / category / coverage）
- [x] Stage 1 JSON schema（`{type[], category[], coverage}`）を prompt に同梱
- [x] Prompt Engineer レビュー（2軸 prompt） → `.work/00307/review-by-prompt-engineer-stage1-facet-2axis.md`
- [x] `tools/benchmark/scenarios/qa-v6-sample5.json` に `expected_facets` 追加
- [x] `tools/benchmark/run.py` を Stage 1 (facet) 対応に修正（stream-json ログ保存、軸別 Jaccard）
- [x] Stage 1 Round 2 計測: Haiku / Sonnet で5件並走 → Sonnet 採用
- [x] 結果を `.work/00307/rounds/stage1-round2.md` に記録
- [x] Round 2 Prompt Engineer Review → `.work/00307/review-by-prompt-engineer-stage1-round2-results.md`
- [x] Round 3: 3 prompt edits + scenario 修正 → 全 5件で Jaccard=1.0 達成 (`.work/00307/rounds/stage1-round3.md`)

### Stage 2 機械 filter 実装 + Round 制

**Steps:**
- [x] `tools/benchmark/filter/facet_filter.py` 実装（index.toon 読込、AND filter、fallback ladder）
- [x] `tests/test_facet_filter.py` 19 tests（parsing / AND / OR / wildcard / fallback / 5 scenarios）
- [x] `prompts/judge_stage2.md` 作成（4段階 + 近傍ファイル容認 + reason ≤300）
- [x] `run.py` に Stage 2 (filter + judge) 対応追加
- [x] `invoke_claude_stream` max_turns リカバリ fix (`96402a071`)
- [x] Stage 2 Round 1 計測（Sonnet、5件 → 全 judge=3、fallback=none）
- [x] `.work/00307/rounds/stage2-round1.md` 記録
- [x] Prompt Engineer Review → `.work/00307/review-by-prompt-engineer-stage2-round1.md`
- [x] Review fix 適用（primary 定義 / reason format / 言語 / 近傍例）→ 再実行でも全 judge=3

### [CONDITIONAL] processing_patterns back-propagation

**前提**: 上記 DECISION で「processing_patterns 列を埋める必要がある」と判断された場合のみ実施。不要と判断されたら削除。

**Steps:**
- [ ] `tools/knowledge-creator/mappings/v6.json` に `processing_patterns` フィールド追加
- [ ] `step2_classify.py` で mapping → catalog へ transit
- [ ] `phase_f_finalize.py::_build_index_toon` を mapping 由来に変更
- [ ] index.toon 再生成 → 4列目が埋まっていることを確認

## Not Started

### 15件で中間確認

**Steps:**
- [ ] 5件で確定したプロンプト・パラメータで 15件実行（Stage 1/2/3）
- [ ] 分散・異常値チェック
- [ ] ユーザーに結果提示 → 合意

### 30件ベースライン測定

**Steps:**
- [ ] 30件実行（Stage 1/2/3, new flow）
- [ ] 30件実行（current flow）— baseline
- [ ] `summary.json` に段階別 level / time(mean,median) / cost(mean,median) 出力
- [ ] 妥当なら `tools/benchmark/baseline/{timestamp}/` にコピーして git commit

### 検索フロー改修（本番 skill へ反映、全5バージョン: 1.2 / 1.3 / 1.4 / 5 / 6）

**Steps:**
- [ ] `.claude/skills/nabledge-6/workflows/_knowledge-search.md` をファセット検索に wholesale 置換
- [ ] 新規: `_facet-extract.md` / `_section-select.md`
- [ ] 新規: `.claude/skills/nabledge-6/scripts/facet-filter.py`（benchmark filter と共通化 or 同等実装）
- [ ] 削除: `_section-judgement.md`, `_file-search.md`, `_section-search.md`, `_index-based-search.md`
- [ ] 削除: search 経路からの `keyword-search.sh` 呼び出し
- [ ] `scripts/get-hints.sh` は残すが search 経路からの参照は消す（AI-2 hints なしで十分な場合）
- [ ] `full-text-search.sh` → `keyword-search.sh` リネーム（public エントリとしてのみ残す）
- [ ] v1.2 / v1.3 / v1.4 / v5 に同じ変更を適用（cross-version consistency rule）
- [ ] 改修 PR 1本で全バージョン一括コミット（nabledge-skill rule）

### qa.md に「情報不足時の1回ヒアリング」追加（H-B, スコープ内）

**仮説**: 漠然とした質問に対して facet 抽出前に1回だけヒアリングすると精度 up。

**Steps:**
- [ ] 「情報不足」判定基準設計
- [ ] `qa.md` Step 0 として追加案 → Prompt Engineer レビュー
- [ ] 実装（全5バージョン）
- [ ] Stage 3 benchmark に hearing シナリオ追加して比較

### キーワード検索の公開（新エントリーポイント）

**Steps:**
- [ ] `plugin/GUIDE-CC.md` に「キーワード検索」追記（全5バージョン）
- [ ] `plugin/GUIDE-GHC.md` に同じく追記（全5バージョン）

### 改修後 30件で再測定 + baseline 比較

**Steps:**
- [ ] 30件で Stage 1/2/3 改修後計測
- [ ] baseline と比較
- [ ] 改善/同等 → 採用、後退 → 原因分析してユーザー相談

### tools/benchmark/README.md 作成

**目的**: 開発者＆AI が後から読めるように、ベンチマークツールの目的・実行方法・運用規則を一箇所にまとめる。

**Steps:**
- [ ] README.md 作成、以下を含める:
  - 目的: なぜ作ったか、何を測るか
  - 3 Stage の定義とファセット検索フロー全体像
  - LLM judge 4段階レベル定義
  - 実行方法（`python3 run.py --stage N --scenarios-file ... --scenario ... --limit N --model ...`）
  - scenarios JSON スキーマ（expected_facets / expected_candidate_paths / expected_sections）
  - prompt ファイルと各 Stage の対応
  - 出力ディレクトリ構造（stream-json 全保存）
  - `.results/` vs `baseline/` の運用（gitignore と commit 方針）
  - Round 運用（計測 → expert review → ユーザー合意 → 修正）
  - 再現性の担保範囲（AI 非決定性のみブレる、他はすべて固定）
  - 改善記録ファイル（`.work/00307/rounds/stage{N}-round{M}.md`）の読み方

### 仕上げ

**Steps:**
- [ ] `CHANGELOG.md` に新エントリーポイント「キーワード検索」追加、フロー改修の user-facing 記述
- [ ] Expert review 実施 → `.work/00307/review-by-*.md`
- [ ] `Skill(skill: "pr", args: "create")` で PR 作成

## Done

- [x] 現状検索フロー把握
- [x] シナリオJSONスキーマ確定
- [x] 30件シナリオを `.work/00307/scenarios-all-30.json` と `tools/benchmark/scenarios/qa-v6.json` に配置
- [x] `tools/benchmark/` scaffolding
- [x] 1件実行検証（`review-04` with current flow）— 452秒問題確認
- [x] 計測設計合意: 3段階 × 別コンテキスト独立判定
- [x] Round制ワークフロー合意
- [x] 5件サンプル選定合意（review-01/review-04/impact-01/req-02/req-09）
- [x] Stage 1 `run.py` 実装（stdin prompt, recall/precision script判定）
- [x] Stage 1 試行計測（3件）— 動作確認OK
- [x] Stage 1 Round 1（5件）計測・記録・expert review 完了
- [x] `.claude/rules/development.md` に「プロンプト変更は expert-review 起点でない場合必ず Prompt Engineer レビュー」を追記
- [x] ファセット検索ピボット設計（Prompt Engineer）→ `.work/00307/review-by-prompt-engineer-stage1-facet-design.md`
- [x] ユーザー方針決定（モデル比較 / rollout / judge 4段階 / hints なし / stream-json）
