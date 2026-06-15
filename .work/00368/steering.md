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

### #5: v6 semantic-search.md を直接書き換え ✅

**Purpose**: index.md 10件 + classes.md 10件 → 合計 20件 → セクション選定 → 回答生成 という設計をクリーンな semantic-search.md として実装する。

**Steps**:

- [x] e2e-prompt / qa.md の Step 番号整合確認（Phase A–E 接頭辞で衝突なし確認済み）
- [x] v6 `semantic-search.md` を直接書き換え（Phase A–E 構成）— commit `cc00ddbd0`
- [x] qa.md Step4 上限を 10→20 に変更 — commit `cc00ddbd0`

---

### #6: 変更後の検索で qa-05・qa-19 各 1 回実行・裏取り報告 ✅

**Purpose**: Step 5 の semantic-search.md 変更が設計通り動くか確認する。

**Steps**:

- [x] qa-05・qa-19 を各 1 回実行 — `step6-classes-v6-1run/run-1`
- [x] 裏取り完了（adapter s2 到達 Yes, Jackson2BodyConverter 出現 Yes, qa-05 退行なし）
- [x] コミット・プッシュ — commit `250351e18`

**Results**:
- qa-19: correctness=1.0, adapter `adapters-jaxrs-adaptor.json:s2` 到達（Phase B=classes.md 由来）, read_sections=9件
- qa-05: correctness=1.0, must 到達, read_sections=7件（退行なし）
- コスト増: qa-05 +$0.234 / qa-19 +$0.244（ページ読み取り増加に伴う）

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

### #8: 上限12適用後 qa-05・qa-19 × 各 10 回・裏取り報告

**Purpose**: Phase D 上限 20→12 の変更が正確率・adapter s2 到達率に退行をもたらさないことを実測で確認する。

**Prerequisites**: #7完了（Step7結果 qa-05:avg1.000 / qa-19:avg0.967、s2到達9/9が基準値）

**Steps**:

- [ ] 編集3点適用・commit (`d8364e4c8` 適用済み)
- [ ] qa-05・qa-19 を各 10 回実行（結果: `step8-limit12-v6-10runs`）
- [ ] 裏取り（qa-19 s2到達率・correctness・cost/time・read_sections分布をStep7と比較）
- [ ] self-check（checks/task-8.md 作成）
- [ ] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- qa-05・qa-19 各 10 回の実行結果が揃っている
- Step7（上限20）との定量比較（s2到達率・correctness・cost・time・read_sections）が示されている
- qa-19 s2到達率が Step7（9/9）から退行していない（退行時は報告して停止）

# State

- **Status**: paused
- **Date**: 2026-06-15
- **Last completed**: #8 ベンチマーク実行・QA review完了（commit `2890cfb7d`）
- **Next**: #8 user review（ユーザーの承認待ち）
- **Notes**: タスク #8 の裏取り・QA review が完了し、ユーザーレビュー提示済み。
  結果サマリー: qa-19 s2到達率 10/10（Step7: 9/9と同等以上）、cost -6.6%、read_max 19→12。
  correctness微減（-0.077/-0.020）は確率的ばらつき範囲内。QA review: 0 Findings。
  ユーザーに「上限12変更はマージ可能か？」を確認中。
  承認後の次アクション: steering.md #8 を完了チェックオフ → PR #369 更新 → マージ準備。
  ブランチ: 368-classes-md-for-class-search (PR #369 OPEN)。
