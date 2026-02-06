# マージワークフロー

このワークフローは、PRをマージし、ブランチをクリーンアップします。

## 必要なツール

- Bash
- AskUserQuestion
- Skill (gitスキルを使用)

## 実行ステップ

### 1. PR情報取得と確認

**1.1 PR情報を取得**

```bash
gh pr view {pr_number} --json number,title,state,headRefName,baseRefName,url,mergeable,mergeStateStatus,statusCheckRollup
```

**1.2 マージ可能性チェック**

以下をすべて確認:
- `state === "OPEN"`
- `mergeable === "MERGEABLE"`
- すべてのステータスチェックが成功している

いずれかが満たされない場合、エラーメッセージを表示して終了:

```
エラー: PRはマージできない状態です

以下を確認してください:
- PRがOPENであること
- マージコンフリクトがないこと（mergeable: {actual_status}）
- CI/CDパイプラインが成功していること
- 必要なレビュー承認が得られていること
```

**1.3 ユーザー確認**

AskUserQuestionで最終確認:
```
以下のPRをマージします。よろしいですか？

**PR**: {pr_url}
**タイトル**: {title}
**ブランチ**: {head_branch} → {base_branch}
```

選択肢:
- "はい、マージする"
- "いいえ、キャンセル"

### 2. マージ実行

ユーザーが承認した場合、マージを実行:

```bash
gh pr merge {pr_number} --squash --delete-branch
```

`--squash`: PRの全コミットを1つにまとめてマージ
`--delete-branch`: マージ後にリモートブランチを自動削除

### 3. ローカルブランチのクリーンアップ

Skillツールを使用してgitスキルのbranch-deleteサブコマンドを実行:

```
Skill
  skill: "git"
  args: "branch-delete {head_branch}"
```

gitスキルが自動的に以下を実行:
- mainブランチに切り替え（必要な場合）
- mainブランチの更新（fetch + pull）
- リモートブランチ情報の更新（fetch --prune）
- ローカルブランチの削除

### 4. 結果表示

```
## マージ完了

**PR**: {pr_url}
**ブランチ**: {head_branch} → {base_branch}

### 実行内容
- PRをマージしました
- リモートブランチ '{head_branch}' を削除しました
- ローカルブランチ '{head_branch}' を削除しました
- ブランチを '{base_branch}' に切り替えました
- 最新のコードを取得しました

お疲れ様でした。
```

## エラーハンドリング

| エラー | 対応 |
|--------|------|
| PRが見つからない | 正しいPR番号を確認 |
| state !== "OPEN" | PRがすでにCLOSEDまたはMERGEDされている |
| mergeable !== "MERGEABLE" | マージコンフリクトを解決してから再実行 |
| ステータスチェック失敗 | CI/CDを修正してから再実行 |
| マージ権限不足 | リポジトリの権限を確認 |
| ブランチ削除失敗 | `git branch -D`で強制削除 |

## 注意事項

1. **絵文字の使用**: ユーザーが明示的に要求しない限り、絵文字を使わない
2. **マージ権限**: PRマージにはリポジトリへの書き込み権限が必要
3. **ステータスチェック**: すべてのCIチェックが成功していることを確認
4. **リモートブランチ削除**: `--delete-branch`により、GitHub側で自動的にリモートブランチが削除される
5. **保護ブランチ**: ターゲットブランチが保護されている場合、追加の権限設定が必要
6. **Squashマージ**: `--squash`により、PRの全コミットが1つにまとめられてマージされる
