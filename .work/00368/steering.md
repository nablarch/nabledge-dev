# Goal

classes.md を使ったクラス名ベースのページ選定が qa-05（Jackson2BodyConverter を要する REST/JSON 実装質問）と qa-19 の正解率を改善することを、ベースラインとの比較で実証する。そのために v6 `semantic-search.md` を index.md + classes.md の2経路マージ設計に書き換え、効果測定を完了させる。

# Acceptance criteria

- v6 `semantic-search.md` が「index.md 10件 + classes.md 10件 → マージ・重複排除 → セクション選定 → 回答生成」の設計で動作する
- Step 4 ベースライン（qa-05: avg 1.000, qa-19: avg 0.130）と比較した改善・劣化が定量的に示されている
- 実行結果に裏取り（scenario_id / must / 中間記録）が添付されている
- 亜種ファイル（exp-semantic-search 等）を作らず v6 本体のみが変更されている

# Assumptions

- e2e-prompt / qa.md の Step 番号整合確認はユーザーから受け取る（未確認・BLOCKED）— Step 5 の前提条件
- qa-05: avg 1.000 / qa-19: avg 0.130（s2到達 1/10）が Step 4 ベースライン値（確定）
- benchmark は逐次実行（並列起動しない）

# Rules

- 1 task = 1 commit
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- 報告前に必ず敵対的レビュー（結果を自分で疑い実物で裏付け）
- 亜種ファイルを増やさず本体を直接変更
- 各タスク完了後にコミット・プッシュし、次タスク前に停止して報告

# Tasks

### #5: v6 semantic-search.md を直接書き換え

**Purpose**: index.md 10件 + classes.md 10件 → 合計 20件 → セクション選定 → 回答生成 という設計をクリーンな semantic-search.md として実装する。

**Prerequisites**: e2e-prompt / qa.md の Step 番号整合確認をユーザーから受け取ること（現在 BLOCKED）

**Steps**:

- [ ] BLOCKED: e2e-prompt / qa.md の Step 番号整合確認をユーザーから受け取る
- [ ] v6 `semantic-search.md` を直接書き換え（全ステップ番号振り直し）
- [ ] self-check（完了基準を OK/NG で確認、checks/task-5.md に記録）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- v6 `semantic-search.md` が index.md + classes.md の2経路マージ設計になっている
- 全ステップ番号が振り直されており、e2e-prompt / qa.md の Step スキップ指示と番号衝突がない
- 亜種ファイルが作られていない（v6 本体のみ変更）

---

### #6: 変更後の検索で qa-05・qa-19 各 1 回実行・裏取り報告

**Purpose**: Step 5 の semantic-search.md 変更が設計通り動くか確認する。

**Prerequisites**: #5 完了

**Steps**:

- [ ] qa-05・qa-19 を各 1 回実行
- [ ] 裏取り（測定が設計通り動いたか、scenario_id・must・中間記録）
- [ ] self-check（完了基準を OK/NG で確認、checks/task-6.md に記録）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- qa-05・qa-19 各 1 回の実行結果と裏取り（scenario_id / must / 中間記録）が揃っている
- 測定が設計通り動いたことが中間記録で確認できる

---

### #7: classes.md 追加状態で qa-05・qa-19 × 各 10 回・裏取り報告

**Purpose**: classes.md 効果を Step 4（ベースライン）と比較して定量評価する。

**Prerequisites**: #6 完了

**Steps**:

- [ ] qa-05・qa-19 を各 10 回実行
- [ ] 裏取り（scenario_id・must・各ステップ記録）
- [ ] Step 4 ベースライン（qa-05: avg 1.000 / qa-19: avg 0.130）と比較
- [ ] self-check（完了基準を OK/NG で確認、checks/task-7.md に記録）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- qa-05・qa-19 各 10 回の実行結果と裏取りが揃っている
- Step 4 ベースラインとの定量比較（avg correctness、s2到達率）が示されている

# Decisions

## D-1: classes.md 設計方針（完了）
- **Issue**: クラス名ベースのページ選定をどう実現するか
- **Conclusion**: index.md と並列の classes.md を RBKC で生成し、2経路マージ
- **Rationale**: headings への class 名埋め込みはノイズ増加リスクがあり、独立ファイルが安全
- **Evidence**: Task 1〜8 の実装・ベンチマーク結果（95.8%、PR-caused regression: 0件）
- **Sources**: .work/00368/tasks.md Done セクション

## D-2: 実験経緯（完了）
- **Issue**: 単純マージでは qa-05 の adapter 選出率が低い（条件P: 1/10）
- **Conclusion**: semantic-search.md の書き換えで設計を確定させ、効果測定を行う
- **Rationale**: 実験A〜P（Task 12〜22）を経て、2経路マージの基本設計は維持しつつ実装をクリーンにする方針に落ち着いた
- **Evidence**: Task 15（条件20: 10/10）、Task 22（条件P: 1/10）等の実験結果
- **Sources**: .work/00368/tasks.md 過去の実験結果サマリー

# State

- **Status**: suspended
- **Date**: 2026-06-15
- **Last completed**: #4 classes.md なし状態ベースライン取得（qa-05: avg 1.000 / qa-19: avg 0.130）
- **Next**: #5 v6 semantic-search.md 書き換え（BLOCKED: Step 番号整合確認待ち）
- **Notes**: e2e-prompt / qa.md の Step 番号整合をユーザーが確認して渡す必要がある。PR #369 は OPEN 状態。
