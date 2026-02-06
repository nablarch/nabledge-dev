# PR作成ワークフロー

このワークフローは、カレントブランチからmainへのPRを作成します。

## 必要なツール

- Bash
- Read

## 実行ステップ

### 1. 事前確認

**1.1 カレントブランチの確認**

```bash
git branch --show-current
```

カレントブランチが`main`または`master`の場合はエラー終了:
```
エラー: mainブランチからPRは作成できません。
feature/issueブランチを作成してから実行してください。
```

**1.2 デフォルトブランチの取得**

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

デフォルトブランチ名を取得（通常は"main"または"master"）。

**1.3 コミット履歴の確認**

```bash
git log {default_branch}..HEAD --oneline
```

コミットがない場合はエラー終了:
```
エラー: {default_branch}からの新しいコミットがありません。
変更をコミットしてから実行してください。
```

**1.4 リモートへのプッシュ確認**

```bash
git status
```

"Your branch is ahead of"または"branch and 'origin/xxx' have diverged"がある場合、プッシュが必要:
```bash
git push -u origin {current_branch}
```

プッシュが失敗（rejected）した場合:
```bash
git pull --rebase origin {current_branch}
git push
```

### 2. PRタイトルと説明を生成

**2.1 コミット履歴とdiffを取得**

```bash
git log {default_branch}..HEAD --format="%s"
git diff {default_branch}...HEAD --stat
```

**2.2 タイトルと説明の生成**

コミット履歴とdiffを分析し、以下の形式で生成:

**タイトル**: 主要な変更を要約（70文字以内）
- 例: "feat: ユーザー認証機能を追加"
- 例: "fix: ログイン時のセッションタイムアウトを修正"

**説明**:
```markdown
## 変更概要
{変更の目的と内容を1-3文で説明}

## 変更内容
{主要な変更点を箇条書き}

## テスト
- [ ] 動作確認完了
- [ ] テスト追加/更新（必要な場合）
```

### 3. PR作成

生成したタイトルと説明でPRを作成:

```bash
gh pr create --title "{generated_title}" --body "{generated_description}" --base {default_branch} --head {current_branch}
```

### 4. 結果表示

```
## PR作成完了

**PR**: {pr_url}
**ブランチ**: {source_branch} → {target_branch}
**タイトル**: {title}

レビュアーにレビューを依頼してください。
```

## エラーハンドリング

| エラー | 対応 |
|--------|------|
| mainブランチから実行 | feature/issueブランチから実行するよう案内 |
| コミットがない | 変更をコミットしてから実行するよう案内 |
| プッシュ失敗 | `git pull --rebase`して再プッシュ |
| gh CLI認証エラー | `gh auth login`で認証 |

## 注意事項

1. **絵文字の使用**: ユーザーが明示的に要求しない限り、絵文字を使わない
2. **タイトルの品質**: コミットメッセージが不適切な場合、自分で適切なタイトルを生成
3. **gh CLI**: GitHub CLIが必要。未インストールの場合はインストールを案内
