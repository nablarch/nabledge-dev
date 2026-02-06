---
name: pr
description: GitHub PRの作成・レビュー対応・マージを統合的に実行する。「PR作って」「レビュー対応して」「マージして」などで使用。サブコマンドで機能を指定可能（create|resolve|merge）。PR番号指定なしの場合、カレントブランチから自動検索。gh CLI必須。
argument-hint: [create|resolve|merge] [PR番号]
allowed-tools: Bash, Task, AskUserQuestion, Read
---

# GitHub PR統合管理（オーケストレーター）

このスキルは、GitHub PRに関する3つの操作を統合的に実行します:
- **create**: カレントブランチからmainへのPRを作成
- **resolve**: レビューコメントに対して修正→コミット→リプライ
- **merge**: PRをマージし、ブランチをクリーンアップ

各操作は、Taskツールで別コンテキストの専用ワークフローを実行します。

## 実行フロー

### 1. 引数解析

`$ARGUMENTS`を解析してモードとPR番号を判定:

```javascript
// パターン1: /pr → 引数なし → AskUserQuestionでモード選択
// パターン2: /pr create → mode="create", pr_number=null
// パターン3: /pr resolve 123 → mode="resolve", pr_number=123
// パターン4: /pr 123 → mode="resolve", pr_number=123
// パターン5: /pr merge → mode="merge", pr_number=null
```

**引数なしの場合**: まずカレントブランチのPRを検索してコンテキストを取得し、AskUserQuestionツールでモードを選択:
- PR検索結果に基づいて推奨オプションを提示
- 質問: "どのPR操作を実行しますか？"
- 選択肢（頻度順、推奨オプションを最初に表示）:
  1. PRが存在する場合: "レビュー対応 (resolve) (推奨)" を最初に表示
  2. PRが存在しない場合: "PR作成 (create) (推奨)" を最初に表示
  3. その他の選択肢を頻度順に表示: "レビュー対応 (resolve)", "PR作成 (create)", "マージ (merge)"

### 2. リポジトリ情報取得

```bash
git remote get-url origin
```

GitHub CLIがリポジトリ情報を自動認識。

### 3. PR自動検索（pr_number=nullの場合）

カレントブランチのPRを検索:

```bash
git branch --show-current
gh pr list --head "{current_branch}" --state open --json number,title,url --jq '.[0]'
```

**判定ロジック**:
- 結果が1件以上 + pr_number=null → pr_number={PR番号}
- 結果が0件 + pr_number=null → エラー（PRが見つからない場合）

### 4. ワークフロー実行

modeに応じて、Taskツールで専用ワークフローを実行:

#### A. create モード

```
Task
  subagent_type: "general-purpose"
  description: "PR作成フローを実行"
  prompt: "以下のワークフローに従って、GitHub PRを作成してください。

{workflows/create.mdの内容を読み込んで展開}

## 入力情報
- カレントブランチ: {current_branch}
"
```

**workflows/create.mdを読み込んで実行**: Readツールで`workflows/create.md`を読み込み、その内容をpromptに含める。

#### B. resolve モード

```
Task
  subagent_type: "general-purpose"
  description: "レビュー対応フローを実行"
  prompt: "以下のワークフローに従って、GitHub PRのレビューコメントに対応してください。

{workflows/resolve.mdの内容を読み込んで展開}

## 入力情報
- PR番号: {pr_number}
- カレントブランチ: {current_branch}
"
```

**workflows/resolve.mdを読み込んで実行**

#### C. merge モード

```
Task
  subagent_type: "general-purpose"
  description: "マージフローを実行"
  prompt: "以下のワークフローに従って、GitHub PRをマージしてください。

{workflows/merge.mdの内容を読み込んで展開}

## 入力情報
- PR番号: {pr_number}
"
```

**workflows/merge.mdを読み込んで実行**

## 実装の注意点

1. **引数なしの場合**: PR検索結果に基づいて推奨オプションを提示し、AskUserQuestionでモードを選択（ユーザーフレンドリー）
2. **エラーハンドリング**: PRが見つからない場合やgh CLIが利用できない場合は、明確なエラーメッセージを表示
3. **ブランチ確認**: mainブランチからcreateを実行しようとした場合はエラー
4. **Taskツールの使用**: 各ワークフローは別コンテキストで実行されるため、オーケストレーター側では結果を受け取るのみ

## エラーハンドリング

| エラー | 対応 |
|--------|------|
| gh CLIが利用不可 | `gh auth login`で認証を実行 |
| GitHubリポジトリでない | GitHubリポジトリであることを確認 |
| PR番号無効/PRが見つからない | 正しいPR番号を確認する |
| mainブランチからcreate実行 | feature/issueブランチから実行するよう案内 |

詳細な使用例は`assets/examples.md`、APIリファレンスは`assets/reference.md`を参照してください。
