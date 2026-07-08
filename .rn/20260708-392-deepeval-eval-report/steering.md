Rn version: 0.8.0

# Goal

Issue #392: 現行の DeepEval ベースのベンチマーク設計と再検証結果（#394）をエキスパートと照らし合わせ、2本の成果物を作る。

1. **現行ベンチマーク評価レポート** — 実証データをエキスパートと認識合わせした結果。現状・ギャップ・改善アクションを記録。
2. **AI 精度評価設計ガイド** — #1 を素材に、他のエージェント開発でも使える「あるべき姿」の知見文書。

# Acceptance criteria

- 現行ベンチマーク評価レポートが作成されている
  - 実証データ（result.md）はリンクで参照（二重メンテなし）
  - エキスパートとの認識合わせ結果が反映されている
  - 改善アクションが具体的に記載されている
- AI 精度評価設計ガイドが作成されている
  - 他のエージェント開発者が自分のプロジェクトに当てはめられる構造になっている
  - 現行ベンチマーク評価レポートを素材として導出されている
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

# Tasks

### #1: 2本の成果物のアウトライン作成

**Purpose**: エキスパートへの相談と最終成果物の方向性をユーザーと合意する

**Prerequisites**: none

**Steps**:

- [ ] 現行ベンチマーク評価レポートのアウトライン作成
- [ ] AI 精度評価設計ガイドのアウトライン作成
- [ ] ユーザー確認

**Completion criteria**:

- 2本のアウトラインについてユーザーが承認している
- アウトラインからエキスパートへの相談事項が導ける構造になっている

### #2: エキスパートへの相談インプット準備

**Purpose**: ユーザーがエキスパートにヒアリングするための材料を作る

**Prerequisites**: #1

**Steps**:

- [ ] 相談インプット文書の作成（背景・実証データ要約・相談事項）
- [ ] ユーザー確認

**Completion criteria**:

- エキスパートに渡す文書が1本にまとまっている
- 相談事項がアウトラインの空白部分と対応している

### #3: 現行ベンチマーク評価レポート作成

**Purpose**: エキスパートとの認識合わせ結果を反映して1本目を完成させる

**Prerequisites**: #2 + ユーザーからヒアリング結果の共有

**Steps**:

- [ ] ヒアリング結果を受け取る
- [ ] レポート本文を作成
- [ ] ユーザー確認

**Completion criteria**:

- Acceptance criteria の現行ベンチマーク評価レポート項目を満たしている

### #4: AI 精度評価設計ガイド作成

**Purpose**: #3 を素材に2本目を完成させる

**Prerequisites**: #3

**Steps**:

- [ ] ガイド本文を作成
- [ ] ユーザー確認

**Completion criteria**:

- Acceptance criteria の AI 精度評価設計ガイド項目を満たしている

### #5: PR 作成

**Purpose**: レビュー用 PR を作成する

**Prerequisites**: #4

**Steps**:

- [ ] `Skill(skill: "pr", args: "create")` で PR 作成
- [ ] `Closes #392` が PR 本文に含まれることを確認

**Completion criteria**:

- PR が作成されており `Closes #392` が含まれている

### #6: Evaluation sign-off

**Purpose**: Acceptance criteria の達成を確認しユーザーの最終承認を得る

**Prerequisites**: #5

**Steps**:

- [ ] Acceptance criteria を全項目照合して結果を提示
- [ ] `/rn:ty`（承認）または `/rn:gm`（修正）でユーザー判定を取得

**Completion criteria**:

- ユーザーが `/rn:ty` で承認している

# State

- **Status**: not suspended
- **Date**: 2026-07-08
- **Last completed**: (none)
- **Next**: #1 アウトライン作成（ユーザー指示待ち）
- **Notes**: branch: 392-deepeval-eval-report、PR: #397（draft）
