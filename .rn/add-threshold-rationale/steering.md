# Goal

`docs/benchmark-design.md` の「PASS/FAILしきい値」セクションに、閾値が高い理由の説明を追記する。
具体的には次の2点を加える:
1. Nablarchの要件（ミッションクリティカルな金融系システム）から高い閾値を設定していること
2. DeepEvalのデフォルト値や公式ドキュメントの例示値と比較して、なぜ高く設定しているかの説明

# Acceptance criteria

- `docs/benchmark-design.md` の「PASS/FAILしきい値」セクションに、Nablarchの要件（金融系ミッションクリティカル）を根拠とした説明が追記されている
- DeepEvalのデフォルト閾値（0.5）と本プロジェクトの閾値（answer_correctness: 0.99、answer_relevancy: 0.95、faithfulness: 0.99）の比較が示されている
- 追記内容が既存の根拠テキスト（「実装に必要な事実の欠落は誤実装に直結する」等）と矛盾していない
- 日本語で記述されている（既存ドキュメントの言語スタイルに合わせる）
- docs/benchmark-design.md 以外のファイルは変更されていない

# Assumptions

- DeepEvalのデフォルト閾値は 0.5（GEval/AnswerRelevancyMetric/FaithfulnessMetric すべて共通）と仮定する。追記前に確認する。
- 既存の根拠テキスト（「実装に必要な事実の欠落は誤実装に直結する」等）はそのまま残す。追記は補足説明として加える。

# Rules

- commit and push every change; one completion marker per task
- docs/benchmark-design.md のみ変更する（スコープ外のファイルに触れない）
- 既存の根拠テキストを削除・書き換えしない（追記のみ）

# Tasks

### #1: DeepEvalデフォルト閾値を確認して説明を追記する

**Purpose**: DeepEvalのデフォルト閾値を調査し、`docs/benchmark-design.md` の「PASS/FAILしきい値」セクションに Nablarch要件とデフォルト比較の説明を追記する。

**Prerequisites**: none

**Steps**:

- [x] DeepEvalの公式ドキュメントまたはソースコードでデフォルト閾値を確認する
- [x] `docs/benchmark-design.md` の「PASS/FAILしきい値」セクションを読む
- [x] Nablarch要件の背景説明とDeepEvalデフォルトとの比較を追記する
- [x] self-check（OK/NG per completion criterion、checks/task-1.md に記録）
- [x] QA expert review（subagent）
- [ ] user review

**Completion criteria**:

- PASS/FAILしきい値セクションに Nablarch要件（金融系ミッションクリティカル）を根拠とした説明が追記されている
- DeepEvalのデフォルト閾値と本プロジェクトの閾値の比較が数値で示されている
- 追記内容が既存の根拠テキストと整合している
- docs/benchmark-design.md 以外のファイルは変更されていない

# Decisions

# State

- **Status**: not suspended
- **Date**: 2026-06-30
- **Last completed**: #1 DeepEvalデフォルト閾値を確認して説明を追記する
- **Next**: user review 待ち（全タスク完了後）
- **Notes**: task #1 完了。commit e95af301。QA PASS。
