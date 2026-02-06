# ワークツリー作成ワークフロー

このワークフローは、新しいワークツリーを作成します。

## 必要なツール

- Bash
- AskUserQuestion

## 実行ステップ

### 1. 現在のディレクトリ情報を取得

**1.1 カレントディレクトリとリポジトリ名を取得**

```bash
pwd
basename $(pwd)
```

- カレントディレクトリ: `<workspace-path>/nab-agents`
- リポジトリ名: `nab-agents`

**1.2 親ディレクトリを取得**

```bash
dirname $(pwd)
```

- 親ディレクトリ: `<workspace-parent-path>`

### 2. ブランチ名の提案

**2.1 作業目的のヒアリング**

AskUserQuestionで作業目的をヒアリング:

```
質問: このワークツリーで何を実装・修正しますか？
header: "作業内容"
options:
  - label: "新機能の追加"
    description: "新しい機能を実装する"
  - label: "バグ修正"
    description: "既存のバグを修正する"
  - label: "リファクタリング"
    description: "コードの構造を改善する"
  - label: "ドキュメント更新"
    description: "ドキュメントを更新する"
```

**2.2 詳細のヒアリング**

選択された作業内容に応じて、詳細をヒアリング（自由入力）:
```
「{作業内容}」の詳細を教えてください。
例: ユーザー認証機能、ログイン画面のバグ、API層のリファクタリング等
```

**2.3 ブランチ名の生成**

ヒアリングした内容から、3つのブランチ名候補を生成:

**生成ルール**:
- プレフィックス: `add-`（新機能）, `fix-`（バグ修正）, `refactor-`（リファクタリング）, `docs-`（ドキュメント）
- 本体: 詳細から抽出したキーワードを`-`で連結
- 全て小文字、英数字とハイフンのみ

**2.4 ブランチ名の選択**

AskUserQuestionで候補から選択:

```
質問: ブランチ名を選択してください。
header: "ブランチ名"
options:
  - label: "{候補1}"
    description: "推奨"
  - label: "{候補2}"
    description: ""
  - label: "{候補3}"
    description: ""
```

ユーザーが"Other"を選択した場合、自由入力を受け付ける。

**2.5 ブランチ名の重複確認**

```bash
git branch --list "{branch_name}"
```

既に存在する場合はエラー終了:
```
エラー: ブランチ「{branch_name}」は既に存在します。

別のブランチ名を使用するか、既存ブランチを削除してください:
git branch -d {branch_name}
```

### 3. ワークツリーパスの決定

**3.1 パスの生成**

```bash
parent_dir=$(dirname $(pwd))
repo_name=$(basename $(pwd))
worktree_path="${parent_dir}/${repo_name}-${branch_name}"
```

例:
- 現在: `<workspace-path>/nab-agents`
- ワークツリー: `<workspace-path>/nab-agents-<branch-name>`

**3.2 パスの存在確認**

```bash
test -e {worktree_path}
```

既に存在する場合はエラー終了:
```
エラー: パス「{worktree_path}」は既に存在します。

別のブランチ名を使用するか、既存のディレクトリを削除してください。
```

**3.3 パスの確認**

AskUserQuestionでパスを確認:

```
質問: 以下のパスにワークツリーを作成します。よろしいですか？
header: "パス確認"
options:
  - label: "はい、作成する"
    description: "{worktree_path}"
  - label: "いいえ、キャンセル"
    description: ""

表示する情報:
パス: {worktree_path}
ブランチ: {branch_name}
ベース: main
```

### 4. ワークツリーの作成

**4.1 mainブランチの更新**

```bash
git fetch origin main
git pull origin main
```

**4.2 ワークツリーの作成**

```bash
git worktree add -b {branch_name} {worktree_path} main
```

作成に失敗した場合:
```
エラー: ワークツリーの作成に失敗しました。

以下を確認してください:
- ディスク容量が十分にあること
- パスへの書き込み権限があること
- ブランチ名が有効であること
```

### 5. 結果表示

```
## ワークツリー作成完了

**パス**: {worktree_path}
**ブランチ**: {branch_name}
**ベースブランチ**: main

### 移動コマンド
cd {worktree_path}

移動後、作業を開始できます。
変更をコミットする際は `/git commit` を使用してください。
```

## エラーハンドリング

| エラー | 対応 |
|--------|------|
| ブランチ名が既に存在 | 別の名前を使用するか、既存ブランチを削除するよう案内 |
| パスが既に存在 | 別の名前を使用するか、既存ディレクトリを削除するよう案内 |
| mainの更新に失敗 | コンフリクトを解決するよう案内 |
| 権限不足 | パスへの書き込み権限を確認するよう案内 |
| 容量不足 | ディスク容量を確認するよう案内 |

## 注意事項

1. **絵文字の使用**: ユーザーが明示的に要求しない限り、絵文字を使わない
2. **パスの命名規則**: `{親ディレクトリ}/{リポジトリ名}-{ブランチ名}`
3. **ブランチ名の品質**: ユーザーの入力から適切なブランチ名を生成する
4. **ベースブランチ**: 常にmainブランチから分岐
