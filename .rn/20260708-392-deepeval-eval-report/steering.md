Rn version: 0.8.0

# Goal

Issue #392: 現行の DeepEval ベースのベンチマーク設計と再検証結果（#394）をエキスパートと照らし合わせ、2本の成果物を作る。

1. **現行ベンチマーク評価レポート** — 実証データをエキスパートと認識合わせした結果。現状・ギャップ・改善アクションを記録。
2. ~~**AI 精度評価設計ガイド**~~ — ユーザー判断により取り止め（2026-07-22）

# Acceptance criteria

- 現行ベンチマーク評価レポートが作成されている
  - 実証データ（result.md）はリンクで参照（二重メンテなし）
  - エキスパートとの認識合わせ結果が反映されている
  - 改善アクションが具体的に記載されている
- PR 本文に `Closes #392` が含まれている

# Assumptions

- エキスパートへのヒアリングはユーザーが実施する
- エキスパートは RAG・大企業社内向け AI チャット開発の責任者レベル
- 成果物は `docs/reports/20260707-deepeval-accuracy/` に配置する
- 各タスクはユーザーからの指示を受けて開始する

# Rules

- commit and push every change; one completion marker per task
- PR 本文には必ず `Closes #392` を含める
- 実証データは result.md へのリンクで参照し、内容を転記しない
- ドキュメントに水平線（`---`）を入れない
- ~~**AI 精度評価設計ガイドはユーザーの明示的な GO まで作成しない。ファイルを作ることも、内容を書くことも、ドラフトすることも禁止。**~~ — 取り止め済み

# Tasks

### ~~#1: 相談用ドラフト作成~~ ✅

**Purpose**: 既知の情報（実証データ・ベストプラクティス・具体例）を埋めたドラフトを作り、空白部分をエキスパートへの相談事項として明示する

**Prerequisites**: none

**Steps**:

- [ ] 2本の成果物の骨格をドラフトに展開
- [ ] 既知部分を埋める（実証データは result.md リンク、ベストプラクティス・具体例は調査して記載）
- [ ] 空白部分をエキスパートへの相談事項として明示
- [ ] ユーザー確認

**Completion criteria**:

- ドラフトの既知部分が埋まっており、空白＝相談事項が明確になっている
- ユーザーが承認している

### ~~#2: 現行ベンチマーク評価レポート作成~~ ✅

**Purpose**: エキスパートとの認識合わせ結果を反映して1本目を完成させる

**Prerequisites**: #1 + ユーザーからヒアリング結果の共有

**Steps**:

- [ ] ヒアリング結果を受け取る
- [ ] レポート本文を作成
- [ ] ユーザー確認

**Completion criteria**:

- Acceptance criteria の現行ベンチマーク評価レポート項目を満たしている

### ~~#3: AI 精度評価設計ガイド作成~~ ❌ 取り止め（2026-07-22 ユーザー判断）

### ~~#4: PR 作成~~ ✅

**Purpose**: レビュー用 PR を作成する

**Prerequisites**: #2

**Steps**:

- [ ] `Skill(skill: "pr", args: "create")` で PR 作成
- [ ] `Closes #392` が PR 本文に含まれることを確認

**Completion criteria**:

- PR が作成されており `Closes #392` が含まれている

### #5: Evaluation sign-off

**Purpose**: Acceptance criteria の達成を確認しユーザーの最終承認を得る

**Prerequisites**: #4

**Steps**:

- [ ] Acceptance criteria を全項目照合して結果を提示
- [ ] `/rn:ty`（承認）または `/rn:gm`（修正）でユーザー判定を取得

**Completion criteria**:

- ユーザーが `/rn:ty` で承認している

# State

Status: paused
Date: 2026-07-22
Last completed: #4 PR 作成・更新（PR #397）
Next: #5 Evaluation sign-off — Acceptance criteria 全項目照合してユーザー承認を取得
Notes: none
