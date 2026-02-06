# ワークツリー削除ワークフロー

このワークフローは、既存のワークツリーを削除します。

## 必要なツール

- Bash
- AskUserQuestion

## 実行ステップ

### 1. ワークツリー一覧の取得

**1.1 ワークツリーリストを取得**

```bash
git worktree list
```

出力例:
```
<workspace-path>/nab-agents         abc1234 [main]
<workspace-path>/nab-agents-<branch-name> def5678 [add-feature]
<workspace-path>/nab-agents-<branch-name>  ghi9012 [fix-bug]
```

**1.2 削除可能なワークツリーの抽出**

メインワークツリー（最初の行）を除外し、削除可能なワークツリーのリストを作成。

ワークツリーがない場合:
```
情報: 削除可能なワークツリーがありません。

現在のワークツリー一覧:
{worktree_list}
```

### 2. 削除対象ワークツリーの決定

**2.1 引数の確認**

引数が指定されている場合、それを削除対象とする。
引数がない場合、次のステップでユーザーに選択させる。

**2.2 削除対象の選択（引数がない場合）**

AskUserQuestionでワークツリーを選択:

```
質問: 削除するワークツリーを選択してください。
header: "ワークツリー削除"
options:
  - label: "{path1}"
    description: "ブランチ: {branch1}"
  - label: "{path2}"
    description: "ブランチ: {branch2}"
  - label: "{path3}"
    description: "ブランチ: {branch3}"
```

### 3. 削除前チェック

**3.1 メインワークツリーの保護**

削除対象がメインワークツリー（カレントリポジトリ）の場合はエラー終了:
```
エラー: メインワークツリーは削除できません。
```

**3.2 パスの存在確認**

```bash
test -d {worktree_path}
```

パスが存在しない場合はエラー終了:
```
エラー: ワークツリー「{worktree_path}」が見つかりません。

ワークツリー一覧を確認:
git worktree list
```

**3.3 未コミット変更の確認**

削除対象ワークツリーのステータスを確認:

```bash
git -C {worktree_path} status --porcelain
```

未コミットの変更がある場合、警告を表示:

AskUserQuestionで確認:
```
質問: ワークツリー「{worktree_path}」に未コミットの変更があります。
削除すると、これらの変更は失われます。本当に削除しますか？
header: "警告"
options:
  - label: "はい、削除する"
    description: "未コミットの変更が失われます"
  - label: "いいえ、キャンセル"
    description: "変更を保存してから削除してください"

表示する変更一覧:
{git_status_output}
```

ユーザーが"キャンセル"を選択した場合、処理を中断:
```
処理をキャンセルしました。

変更を保存するには:
cd {worktree_path}
/git commit
```

### 4. ワークツリーの削除

**4.1 ワークツリーを削除**

```bash
git worktree remove {worktree_path}
```

削除に失敗した場合（ロックされている等）、強制削除:
```bash
git worktree remove --force {worktree_path}
```

それでも失敗した場合:
```
エラー: ワークツリーの削除に失敗しました。

手動で削除してください:
rm -rf {worktree_path}
git worktree prune
```

### 5. ブランチの削除確認

**5.1 ブランチの取得**

削除したワークツリーのブランチ名を取得。

**5.2 マージ済み確認**

```bash
git branch --merged main | grep "^  {branch_name}$"
```

**5.3 ブランチ削除の確認**

マージ済みの場合、AskUserQuestionでブランチ削除を確認:

```
質問: ブランチ「{branch_name}」はマージ済みです。
このブランチも削除しますか？
header: "ブランチ削除"
options:
  - label: "はい、削除する"
    description: "ローカルとリモートから削除"
  - label: "ローカルのみ削除"
    description: "リモートは残す"
  - label: "いいえ、残す"
    description: "ブランチは残す"
```

**5.4 ブランチの削除**

ユーザーの選択に応じて:

**「はい、削除する」の場合**:
```bash
git push origin --delete {branch_name}
git branch -d {branch_name}
```

**「ローカルのみ削除」の場合**:
```bash
git branch -d {branch_name}
```

**「いいえ、残す」の場合**:
削除しない。

### 6. 結果表示

```
## ワークツリー削除完了

**削除したワークツリー**: {worktree_path}
**ブランチ**: {branch_name}

### 実行内容
- ワークツリー '{worktree_path}' を削除しました
{ブランチ削除した場合}
- ローカルブランチ '{branch_name}' を削除しました
- リモートブランチ 'origin/{branch_name}' を削除しました
{/ブランチ削除した場合}
```

## エラーハンドリング

| エラー | 対応 |
|--------|------|
| 削除可能なワークツリーがない | ワークツリー一覧を表示 |
| メインワークツリーの削除試行 | エラーメッセージを表示して終了 |
| パスが存在しない | 正しいパスを確認 |
| 未コミット変更あり | 警告を表示してユーザーに確認 |
| 削除失敗 | 強制削除を試行、それでも失敗した場合は手動削除を案内 |

## 注意事項

1. **絵文字の使用**: ユーザーが明示的に要求しない限り、絵文字を使わない
2. **安全性優先**: 未コミット変更がある場合は警告を表示
3. **メインワークツリーの保護**: メインワークツリーは削除を拒否
4. **ブランチ削除**: マージ済みブランチは自動的に削除を提案
