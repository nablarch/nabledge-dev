# Goal

DeepEvalが自動評価した全34シナリオの回答を人手で照合し、DeepEvalのfalse-negative率（ツールがOKと判定したが実際は不正確な回答）を計測する。計測結果は評価方法論のエキスパートレビュー向けの実証データとして整備する。

# Acceptance criteria

- 全34シナリオ（run-1 of 20260616-1214-fullbench-classes-v6）の回答が人手で照合済みである
- 各シナリオについて「DeepEval判定」「人手判定」「判定根拠」が記録されている
- false-negative数（DeepEval=OK、人手=NG）とfalse-negative率（false-negative数/全OK数）が算出されている
- 調査結果が `.work/00393/deepeval-false-negative-report.md` に文書化されている

# Assumptions

- 対象runは `tools/benchmark/results/20260616-1214-fullbench-classes-v6/run-1/` とする（34シナリオの完全な1回実行）
- 「DeepEval OK」の定義: answer_correctness ≥ 0.99 かつ answer_relevancy ≥ 0.95 かつ faithfulness ≥ 0.99
- 「人手NG」の判定: 回答がexpected_factsを満たさない、または誤った情報を含む場合
- run-1のOK件数は12件（impact-06, oos-impact-01, pre-02, qa-02, qa-04, qa-05, qa-08, qa-09, qa-13, qa-19, review-06, review-08）
- 人手照合は `answer.md`（実際の回答）と `evaluation.json`（expected_facts、スコア根拠）を対照して行う

# Rules

- commit and push every change; one completion marker per task
- 照合根拠は具体的に記述する（「expected_factのXが回答に含まれている/いない」）
- 人手判定はexpected_factsを基準とする（DeepEvalのスコアに引きずられない）
- 全34件を対象とする（OKのみでなくNG件数も記録し、false-negative率の分母を確定させる）

# Tasks

### #1: 34シナリオ全件の人手照合を実施する

**Purpose**: 全34シナリオの回答をexpected_factsと照合し、DeepEval判定と人手判定を記録する。

**Prerequisites**: none

**Steps**:

- [ ] 各シナリオのanswer.md・evaluation.json・expected_factsを確認し照合表を作成する
- [ ] 照合結果を `.work/00393/deepeval-false-negative-report.md` に記録する
- [ ] self-check (OK/NG per completion criterion, record in checks/t1.md)
- [ ] QA expert review (subagent)

**Completion criteria**:

- `.work/00393/deepeval-false-negative-report.md` が存在し、全34件の「DeepEval判定 / 人手判定 / 根拠」が記載されている
- false-negative数とfalse-negative率（false-negative数/12）が算出されている
- 根拠が「expected_factのX句が回答に含まれる/含まれない」という形で具体的に示されている

### #2: Evaluation sign-off

**Purpose**: 成果物をユーザーに提示し、承認を得る。

**Prerequisites**: #1

**Steps**:

- [ ] `.work/00393/deepeval-false-negative-report.md` の内容をユーザーに提示する
- [ ] `/rn:ty` または `/rn:gm` でユーザーの承認を受ける

**Completion criteria**:

- ユーザーが成果物を承認している

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: —
- **Next**: #1 34シナリオ全件の人手照合
- **Notes**: 対象run: tools/benchmark/results/20260616-1214-fullbench-classes-v6/run-1/. OK件数12件（impact-06, oos-impact-01, pre-02, qa-02, qa-04, qa-05, qa-08, qa-09, qa-13, qa-19, review-06, review-08）。NG件数22件。
