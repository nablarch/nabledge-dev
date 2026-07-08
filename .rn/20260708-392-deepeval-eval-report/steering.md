Rn version: 0.8.0

# Goal

Issue #392: #394 の全量手動検証結果（`docs/reports/20260707-deepeval-accuracy/result.md`）を実証データとして、DeepEval ベースの評価方法論をエキスパートがレビューし、評価設計の妥当性・改善点・継続的改善アクションを文書化した再利用可能な評価レポートを作成する。

# Acceptance criteria

- エキスパートが以下の観点を検討し、結果が文書化されている:
  - 期待事実 (ground truth) の定義アプローチ
  - DeepEval の信頼性（OK 判定の見逃しリスクを含む）
  - 閾値設定とその根拠
  - 現アプローチが最適かどうか
- ベストプラクティスが存在する領域: ギャップと改善アクションが特定されている
- ベストプラクティスが不明確な領域: 継続的改善のためのアクション（実験・検証計画等）が文書化されている
- #394 の全量手動検証結果が実証データとして組み込まれている
- 他の AI 品質評価イニシアチブへの入力として再利用可能な構造になっている
- レポートが `docs/reports/` 以下に配置されている
- PR 本文に `Closes #392` が含まれている

# Assumptions

- #394 の result.md は確定値（2026-07-08 ステップ2完了済み）である
- エキスパートは AI エージェントとして実行する（`.claude/rules/expert-review.md` に従う）
- レポートは日本語で作成する（エンドユーザー向けドキュメントとして機能させる場合も含め、開発者向け分析レポートのため英語でも可 — ユーザー確認不要、benchmark-design.md が日本語なので日本語に合わせる）
- `docs/reports/20260707-deepeval-accuracy/` ディレクトリはすでに存在し、result.md が含まれる

# Rules

- commit and push every change; one completion marker per task
- レポートは `docs/reports/20260707-deepeval-accuracy/` に配置する
- `.work/00392/` に作業ログを記録する
- PR 本文には必ず `Closes #392` を含める

# Tasks

### #1: エキスパートレビューの実施とレポート作成

**Purpose**: AI エキスパート（QA Engineer）が評価方法論を検討し、評価レポートを作成する

**Prerequisites**: none

**Steps**:

- [ ] `.work/00392/` ディレクトリを作成し、`tasks.md` と `notes.md` を作成
- [ ] `docs/reports/20260707-deepeval-accuracy/result.md` の全文を読み込む
- [ ] `docs/benchmark-design.md` の DeepEval セクションを読み込む
- [ ] QA Engineer / AI Quality Expert エキスパートとして評価方法論をレビュー（subagent）
- [ ] レビュー結果に基づき評価レポートを `docs/reports/20260707-deepeval-accuracy/eval-methodology-report.md` に作成
- [ ] self-check: Success Criteria と照合（checks/01.md に記録）
- [ ] Technical Writer expert review（subagent）
- [ ] フィードバック反映

**Completion criteria**:

- `docs/reports/20260707-deepeval-accuracy/eval-methodology-report.md` が存在し、Success Criteria の全項目を満たしている
- レポートが他の AI 品質評価イニシアチブへの入力として読める独立した構造になっている（読者が #394 の詳細を参照しなくても概要を把握できる）
- 誤った評価設計の根拠が示されている箇所がない（主観的推測ではなく実証データに基づく記述になっている）

### #2: PR 作成

**Purpose**: レビュー用 PR を作成し、`Closes #392` を含む PR 本文で提出する

**Prerequisites**: #1

**Steps**:

- [ ] `Skill(skill: "pr", args: "create")` で PR 作成
- [ ] PR 本文に `Closes #392` が含まれることを確認

**Completion criteria**:

- PR が作成されており、`Closes #392` が PR 本文に含まれている
- PR の Expert Review セクションに #1 のレビュー結果へのリンクが含まれている

### #3: Evaluation sign-off

**Purpose**: Acceptance criteria の達成を確認し、ユーザーの最終承認を得る

**Prerequisites**: #2

**Steps**:

- [ ] Acceptance criteria を全項目照合して結果を提示
- [ ] `/rn:ty`（承認）または `/rn:gm`（修正）でユーザー判定を取得

**Completion criteria**:

- ユーザーが `/rn:ty` で承認している
- Acceptance criteria の全項目が充足されている

# State

- **Status**: not suspended
- **Date**: 2026-07-08
- **Last completed**: (none)
- **Next**: #1 エキスパートレビューの実施とレポート作成
- **Notes**: worktree: ai-quality、ブランチ: 392-deepeval-eval-report（作成予定）。result.md は GitHub 上に存在（`docs/reports/20260707-deepeval-accuracy/result.md`）。このワークツリーには未同期のため、ブランチ作成後に確認が必要。
