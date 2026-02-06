# PR スキル APIリファレンス

このドキュメントでは、prスキルの技術的な詳細を説明します。

## コマンド構文

```
/pr [mode] [pr_number]
```

### パラメータ

- `mode`: 実行モード（`create`, `resolve`, `merge`）。省略可能。
- `pr_number`: PR番号。省略可能（カレントブランチから自動検索）。

### モードの判定ロジック

```javascript
// パターン1: /pr → 引数なし
//   → PR検索 → AskUserQuestionでモード選択
if (args === null) {
  const pr = searchPRForCurrentBranch();
  const mode = askUserQuestion(pr ? "resolve" : "create");
}

// パターン2: /pr create
//   → mode="create", pr_number=null
if (args === "create") {
  mode = "create";
  pr_number = null;
}

// パターン3: /pr resolve 123
//   → mode="resolve", pr_number=123
if (args.startsWith("resolve ")) {
  mode = "resolve";
  pr_number = parseInt(args.split(" ")[1]);
}

// パターン4: /pr 123
//   → mode="resolve", pr_number=123
if (/^\d+$/.test(args)) {
  mode = "resolve";
  pr_number = parseInt(args);
}

// パターン5: /pr merge
//   → mode="merge", pr_number=null
if (args === "merge") {
  mode = "merge";
  pr_number = null;
}
```

## GitHub CLI コマンド

prスキルが内部で使用するgh CLIコマンド一覧。

### リポジトリ情報取得

```bash
# リポジトリの情報を取得
gh repo view --json defaultBranchRef,owner,name

# デフォルトブランチ名のみ取得
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

### PR一覧取得

```bash
# カレントブランチのPRを検索
gh pr list --head "{branch_name}" --state open --json number,title,url --jq '.[0]'

# 全てのopenなPRを取得
gh pr list --state open --json number,title,headRefName,url
```

### PR情報取得

```bash
# PR詳細を取得
gh pr view {pr_number} --json number,title,state,headRefName,baseRefName,url,author,mergeable,mergeStateStatus

# PRのコメントとレビューを取得
gh pr view {pr_number} --json comments,reviews
```

### PR作成

```bash
gh pr create \
  --title "{title}" \
  --body "{body}" \
  --base {base_branch} \
  --head {head_branch}
```

### PRコメント

```bash
gh pr comment {pr_number} --body "{comment_body}"
```

### PRマージ

```bash
# Squashマージ（リモートブランチを自動削除）
gh pr merge {pr_number} --squash --delete-branch

# 通常のマージ
gh pr merge {pr_number} --merge --delete-branch

# Rebaseマージ
gh pr merge {pr_number} --rebase --delete-branch
```

## 内部データ構造

### PR情報

```json
{
  "number": 123,
  "title": "feat: ユーザー認証機能を追加",
  "state": "OPEN",
  "headRefName": "feature/add-user-auth",
  "baseRefName": "main",
  "url": "https://github.com/owner/repo/pull/123",
  "author": {
    "login": "username"
  },
  "mergeable": "MERGEABLE",
  "mergeStateStatus": "CLEAN"
}
```

### レビュー情報

```json
{
  "reviews": [
    {
      "author": {
        "login": "reviewer"
      },
      "state": "CHANGES_REQUESTED",
      "body": "レビューコメント本文",
      "createdAt": "2024-01-01T12:00:00Z",
      "comments": [
        {
          "path": "src/auth.ts",
          "line": 42,
          "body": "変数名をより明確にしてください"
        }
      ]
    }
  ]
}
```

## ワークフロー実行

各モードは、Taskツールで専用ワークフローを実行します。

### create モード

```
Task
  subagent_type: "general-purpose"
  description: "PR作成フローを実行"
  prompt: """
以下のワークフローに従って、GitHub PRを作成してください。

{workflows/create.mdの内容}

## 入力情報
- カレントブランチ: {current_branch}
"""
```

### resolve モード

```
Task
  subagent_type: "general-purpose"
  description: "レビュー対応フローを実行"
  prompt: """
以下のワークフローに従って、GitHub PRのレビューコメントに対応してください。

{workflows/resolve.mdの内容}

## 入力情報
- PR番号: {pr_number}
- カレントブランチ: {current_branch}
"""
```

### merge モード

```
Task
  subagent_type: "general-purpose"
  description: "マージフローを実行"
  prompt: """
以下のワークフローに従って、GitHub PRをマージしてください。

{workflows/merge.mdの内容}

## 入力情報
- PR番号: {pr_number}
"""
```

## エラーコード

| エラーコード | 説明 | 対応 |
|------------|------|------|
| GH_AUTH_ERROR | gh CLI認証エラー | `gh auth login`を実行 |
| GH_NOT_FOUND | gh CLIが見つからない | gh CLIをインストール |
| REPO_NOT_GITHUB | GitHubリポジトリでない | GitHubリポジトリで実行 |
| BRANCH_INVALID | ブランチが不正 | 正しいブランチから実行 |
| PR_NOT_FOUND | PRが見つからない | PR番号を確認 |
| PR_CLOSED | PRがCLOSEDまたはMERGED | OPENのPRを指定 |
| PR_CONFLICT | マージコンフリクト | コンフリクトを解決 |
| NO_COMMITS | コミットがない | 変更をコミット |
| PUSH_REJECTED | プッシュが拒否された | `git pull --rebase`して再プッシュ |

## 設定

prスキルは、以下の環境変数を使用できます（将来的な拡張）:

```bash
# デフォルトのマージ方法（squash/merge/rebase）
export PR_MERGE_METHOD="squash"

# PR作成時のレビュアー自動割り当て
export PR_DEFAULT_REVIEWERS="user1,user2"

# PR作成時のラベル自動付与
export PR_DEFAULT_LABELS="enhancement,needs-review"
```

## 制限事項

1. **gh CLI依存**: GitHub CLIが必須
2. **認証**: `gh auth login`で認証済みであること
3. **権限**: リポジトリへの書き込み権限が必要
4. **ブランチ保護**: 保護ブランチへのマージは追加の権限設定が必要
5. **レビューコメント**: ファイル単位のコメントのみ対応（行コメントも取得可能だが、複雑な場合は手動対応を推奨）

## トラブルシューティング

### gh CLIが見つからない

```bash
# インストール（macOS）
brew install gh

# インストール（Linux）
sudo apt install gh

# 認証
gh auth login
```

### 認証エラー

```bash
# 認証状態を確認
gh auth status

# 再認証
gh auth login

# トークンを使用
gh auth login --with-token < token.txt
```

### PR番号がわからない

```bash
# カレントブランチのPRを確認
gh pr view

# 全てのPRを一覧表示
gh pr list
```

## 開発者向け情報

### スキル構造

```
.claude/skills/pr/
├── SKILL.md           # スキルのメタ情報とオーケストレーター
├── workflows/
│   ├── create.md      # PR作成ワークフロー
│   ├── resolve.md     # レビュー対応ワークフロー
│   └── merge.md       # マージワークフロー
└── assets/
    ├── examples.md    # 使用例
    └── reference.md   # このファイル
```

### 拡張方法

新しいモードを追加する場合:
1. `workflows/`に新しいワークフローファイルを追加
2. `SKILL.md`の引数解析ロジックに新しいモードを追加
3. `SKILL.md`のワークフロー実行セクションに新しいモードを追加
4. `assets/examples.md`に使用例を追加

### テスト

各ワークフローは独立しているため、個別にテスト可能:

```bash
# PR作成のテスト
/pr create

# レビュー対応のテスト（PRが存在する場合）
/pr resolve

# マージのテスト（PRがマージ可能な場合）
/pr merge
```
