# Goal

DeepEvalが自動評価した全34シナリオ×3run=102件の判定結果を全件照合し、false-positive（DeepEval=NG、実際=問題なし）とfalse-negative（DeepEval=OK、実際=問題あり）の両方を計測する。計測結果は評価方法論の実証データとして整備する。

# Acceptance criteria

- 34シナリオ×3run=102件×3指標=306データ点について、各指標のDeepEval判定を人手で照合した確認ファイル（MD）が `.work/00393/checks/` に存在する
- 各確認ファイルに「質問文・回答文・ナレッジリンク・指標スコア表・判定・判定根拠」が記載されている
- false-positive率（指標ごと）とfalse-negative率（指標ごと）が算出され `.work/00393/result.md` に文書化されている

# Assumptions

- 対象: `tools/benchmark/results/20260616-1214-fullbench-classes-v6/` の run-1〜run-3（34シナリオ×3run=102件）
- 閾値: answer_correctness ≥ 0.99 / answer_relevancy ≥ 0.95 / faithfulness ≥ 0.99
- ナレッジMDは `.claude/skills/nabledge-6/docs/` 以下に存在し、JSONのsectionタイトルからアンカーリンクを生成できる
- 判定はスクリプト自動生成部分と私（AI）の手動記入部分に分担する

# Rules

- commit and push every change; one completion marker per task
- 判定根拠は具体的に記述する（「expected_factのX句が回答に含まれる/含まれない」「ナレッジにない記述Xが含まれる」等）
- 判定はDeepEvalのスコアに引きずられず独立して判断する

# Tasks

### #1: 確認ファイル生成スクリプトを作成・実行する ✅

**Purpose**: 102件の確認用MDファイルを自動生成する（質問・回答・リンク・スコア表の空欄まで）。

**Prerequisites**: none

**Steps**:

- [ ] スクリプト `tools/benchmark/scripts/generate_review_files.py` を作成する
- [ ] スクリプトを実行し `.work/00393/checks/{run}-{scenario}.md` を102件生成する
- [ ] 生成結果をサンプル確認する（3件程度）
- [ ] コミット・プッシュ
- [ ] self-check (OK/NG per completion criterion, record in checks-meta/t1.md)

**Completion criteria**:

- `.work/00393/checks/` に102件のMDファイルが存在する
- 各ファイルに質問文・回答文・ナレッジセクションへのリンク・3指標のスコア表（判定欄は空欄）が含まれている
- スクリプトがエラーなく完走する

### #2: 102件の判定を記入する ✅

**Purpose**: 各確認ファイルにAIが判定と根拠を記入する（1エージェント=1ファイル、3並列で102件を処理）。

**Prerequisites**: #1

**Steps**:

- [x] 102ファイルを3並列（1エージェント=1ファイル）で処理する
- [x] コミット・プッシュ
- [x] self-check (OK/NG per completion criterion, record in checks-meta/t2.md)
- [x] QA expert review (subagent)

**Completion criteria**:

- 102件全ての確認ファイルに3指標×判定・根拠が記入されている
- 未記入（空欄）のファイルが0件である

### #3: 集計レポートを作成する

**Purpose**: false-positive率・false-negative率を指標ごとに算出し `.work/00393/result.md` にまとめる。

**Prerequisites**: #2

**Steps**:

- [ ] 102件の判定結果を集計し、指標ごとのfalse-positive数・false-negative数・率を算出する
- [ ] `.work/00393/result.md` を作成する
- [ ] コミット・プッシュ
- [ ] self-check (OK/NG per completion criterion, record in checks-meta/t3.md)

**Completion criteria**:

- `.work/00393/result.md` に3指標×false-positive率・false-negative率が数値で記載されている
- 根拠となる確認ファイルへのリンクが含まれている

### #4: Evaluation sign-off

**Purpose**: 成果物をユーザーに提示し、承認を得る。

**Prerequisites**: #3

**Steps**:

- [ ] `.work/00393/result.md` の内容をユーザーに提示する
- [ ] `/rn:ty` または `/rn:gm` でユーザーの承認を受ける

**Completion criteria**:

- ユーザーが成果物を承認している

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
