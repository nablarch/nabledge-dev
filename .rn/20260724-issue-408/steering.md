Rn version: 0.8.0

# Goal

nabledge 全プラグインとマーケットプレイスのバージョンを 1.0 に上げ、各プラグインの CHANGELOG に安定版宣言セクション [1.0] を追加してリリース PR を作成する。機能変更は一切なく、1.0 は品質水準が本番利用に達したことの宣言である。

# Acceptance criteria

- nabledge-6 の `plugin.json` に `"version": "1.0"` が記録されている
- nabledge-5 の `plugin.json` に `"version": "1.0"` が記録されている
- nabledge-1.4 の `plugin.json` に `"version": "1.0"` が記録されている
- nabledge-1.3 の `plugin.json` に `"version": "1.0"` が記録されている
- nabledge-1.2 の `plugin.json` に `"version": "1.0"` が記録されている
- `marketplace.json` に `"version": "1.0"` が記録されている
- nabledge-6 の `CHANGELOG.md` に `## [1.0]` セクションが存在し、安定版宣言の文言が含まれる
- nabledge-5 の `CHANGELOG.md` に `## [1.0]` セクションが存在し、安定版宣言の文言が含まれる
- nabledge-1.4 の `CHANGELOG.md` に `## [1.0]` セクションが存在し、安定版宣言の文言が含まれる
- nabledge-1.3 の `CHANGELOG.md` に `## [1.0]` セクションが存在し、安定版宣言の文言が含まれる
- nabledge-1.2 の `CHANGELOG.md` に `## [1.0]` セクションが存在し、安定版宣言の文言が含まれる
- marketplace `CHANGELOG.md` の対応表に `1.0` 行が追加されている
- Keep a Changelog フォーマットに準拠している（`[1.0]: https://...` タグリンクが各プラグインCHANGELOGの末尾にある）
- PR が作成されており、issue #408 を閉じる

# Assumptions

- [Unreleased] セクションは存在しない（issue に明記）
- 機能変更はなく、バージョン上げと安定版宣言のみ
- marketplace version = 1.0（全プラグインの最高バージョンと等しい）
- リリース日は 2026-07-24

# Rules

- commit and push every change; one completion marker per task
- Never edit RBKC-generated files
- Stage files individually by purpose; never `git add -A`
- Commit message format: `<type>: <description>` — max 70 chars first line

# Tasks

### #1: Update all plugin.json and CHANGELOG files to version 1.0

**Purpose**: 全6ファイル（5プラグイン plugin.json + marketplace.json）のバージョンを 1.0 に更新し、全5プラグインの CHANGELOG に [1.0] 安定版宣言セクションを追加し、marketplace CHANGELOG の対応表を更新する。

**Prerequisites**: none

**Steps**:

- [ ] nabledge-6/plugin/plugin.json: `"version": "1.0"` に更新
- [ ] nabledge-5/plugin/plugin.json: `"version": "1.0"` に更新
- [ ] nabledge-1.4/plugin/plugin.json: `"version": "1.0"` に更新
- [ ] nabledge-1.3/plugin/plugin.json: `"version": "1.0"` に更新
- [ ] nabledge-1.2/plugin/plugin.json: `"version": "1.0"` に更新
- [ ] marketplace.json: `"version": "1.0"` に更新
- [ ] nabledge-6/plugin/CHANGELOG.md: `## [1.0] - 2026-07-24` セクション追加 + タグリンク追加
- [ ] nabledge-5/plugin/CHANGELOG.md: `## [1.0] - 2026-07-24` セクション追加 + タグリンク追加
- [ ] nabledge-1.4/plugin/CHANGELOG.md: `## [1.0] - 2026-07-24` セクション追加 + タグリンク追加
- [ ] nabledge-1.3/plugin/CHANGELOG.md: `## [1.0] - 2026-07-24` セクション追加 + タグリンク追加
- [ ] nabledge-1.2/plugin/CHANGELOG.md: `## [1.0] - 2026-07-24` セクション追加 + タグリンク追加
- [ ] marketplace/CHANGELOG.md: 対応表に `1.0` 行を追加
- [ ] self-check (OK/NG per completion criterion, record in checks/task-1.md)

**Completion criteria**:

- 全5プラグインの `plugin.json` の `version` フィールドが `"1.0"` である
- `marketplace.json` の `metadata.version` が `"1.0"` である
- 全5プラグインの `CHANGELOG.md` に `## [1.0] - 2026-07-24` セクションが存在し、安定版宣言の文言を含む
- 全5プラグインの `CHANGELOG.md` の末尾に `[1.0]: https://github.com/nablarch/nabledge/releases/tag/1.0` タグリンクが存在する
- marketplace `CHANGELOG.md` の対応表に `1.0` 行があり、全5プラグインのリンクが含まれている
- Keep a Changelog フォーマット違反がない（新しいバージョン番号は既存の最新バージョンより上にある）

### #2: Create PR

**Purpose**: 変更内容をコミット・プッシュし、issue #408 を閉じる PR を作成する。

**Prerequisites**: #1

**Steps**:

- [ ] git diff で変更内容を確認
- [ ] 各ファイルを個別にステージして commit & push
- [ ] `Skill(skill: "pr", args: "create")` で PR を作成

**Completion criteria**:

- PR が draft でない状態で開かれており、タイトルに `feat:` が含まれ issue #408 を参照している
- PR body に `Closes #408` が含まれている

### #3: Evaluation sign-off

**Purpose**: Acceptance criteria の全項目が満たされていることをユーザーに確認してもらい、セッションを完了する。

**Prerequisites**: #2

**Steps**:

- [ ] Acceptance criteria の各項目をファイル内容で確認
- [ ] 結果を提示してユーザーの承認を `/rn:ty` で受け取る

**Completion criteria**:

- ユーザーが `/rn:ty` で承認している

# State

- **Status**: not suspended
- **Date**: 2026-07-24
- **Last completed**: (none)
- **Next**: #1 Update all plugin.json and CHANGELOG files to version 1.0
- **Notes**: branch: worktree-issue-408. No functional changes — version bump + stable release declaration only.
