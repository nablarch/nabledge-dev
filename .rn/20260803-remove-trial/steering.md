Rn version: 0.8.0

# Goal

1.0リリースに伴い、全プラグイン README から「評価版について」注意書きブロックを削除する。対象は nabledge-6/5/1.4/1.3/1.2 の5つ。

# Acceptance criteria

- `.claude/skills/nabledge-6/plugin/README.md` に「評価版について」ブロックが存在しない
- `.claude/skills/nabledge-5/plugin/README.md` に「評価版について」ブロックが存在しない
- `.claude/skills/nabledge-1.4/plugin/README.md` に「評価版について」ブロックが存在しない
- `.claude/skills/nabledge-1.3/plugin/README.md` に「評価版について」ブロックが存在しない
- `.claude/skills/nabledge-1.2/plugin/README.md` に「評価版について」ブロックが存在しない
- 各 README の他のコンテンツ（`## 機能` 以降）は変更されていない
- `grep -r "評価版について" .claude/skills/` が0件を返す

# Assumptions

- 削除対象は各 README の 3〜11行目（`> **⚠️ 評価版について**` から `> ワークフローは今後も継続的に拡充していきます。ぜひフィードバックをお寄せください。` まで）および後続の空行
- `docs/development-status.md` と `docs/articles/` 内の「評価版」言及は開発内部資料のため変更不要
- `CHANGELOG.md` の `[0.1]` エントリ内「評価版として」は変更履歴の事実記述のため変更不要

# Rules

- commit and push every change; one completion marker per task
- ファイルはバージョン間で構造が同一なので5ファイルを一括処理してよい
- 各バージョン間でブロックの文言が同一であることを確認してから削除する

# Tasks

### #1: 5つのプラグイン README から評価版ブロックを削除する

**Purpose**: nabledge-6/5/1.4/1.3/1.2 の README それぞれから「評価版について」注意書きブロック（9行 + 空行）を削除する

**Prerequisites**: none

**Steps**:

- [ ] nabledge-6 README から評価版ブロックを削除
- [ ] nabledge-5 README から評価版ブロックを削除
- [ ] nabledge-1.4 README から評価版ブロックを削除
- [ ] nabledge-1.3 README から評価版ブロックを削除
- [ ] nabledge-1.2 README から評価版ブロックを削除
- [ ] `grep -r "評価版について" .claude/skills/` が0件であることを確認
- [ ] self-check (OK/NG per completion criterion, record in checks/task-1.md)
- [ ] commit and push

**Completion criteria**:

- `grep -r "評価版について" .claude/skills/` が0件を返す
- 5つの README それぞれで `## 機能` が2行目（タイトル行の次）になっている
- `grep -r "評価版について" .claude/skills/` 以外の既存コンテンツは変更されていない（diff が削除のみ）

### #2: Evaluation sign-off

**Purpose**: Acceptance criteria の達成を確認してユーザーの承認を得る

**Prerequisites**: #1

**Steps**:

- [ ] Acceptance criteria 全項目の充足を確認
- [ ] 結果をユーザーに提示し `/rn:ty` または `/rn:gm` で承認を得る

**Completion criteria**:

- ユーザーが `/rn:ty` で承認した

# State

- **Status**: not suspended
- **Date**: 2026-08-03
- **Last completed**: (none)
- **Next**: #1 5つのプラグイン README から評価版ブロックを削除する
- **Notes**: ブランチ `worktree-remove-trial`、タスクは単純削除のみで設計判断なし
