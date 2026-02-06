# レビュー対応ワークフロー

このワークフローは、レビューコメントに対して修正→コミット→リプライを行います。

## 必要なツール

- Bash
- Read
- Edit
- Write
- AskUserQuestion
- Skill (gitスキルを使用)

## 実行ステップ

### 1. PR情報取得

**1.1 PR情報を取得**

```bash
gh pr view {pr_number} --json number,title,state,headRefName,baseRefName,url,author,mergeable
```

**1.2 PR状態の確認**

PRが`OPEN`であることを確認。CLOSEDまたはMERGEDの場合はエラー終了。

**1.3 ブランチ確認**

カレントブランチを取得:
```bash
git branch --show-current
```

カレントブランチが`headRefName`と異なる場合、AskUserQuestionで確認:
```
現在のブランチ '{current_branch}' は、PRのソースブランチ '{head_branch}' と異なります。
'{head_branch}' にチェックアウトしますか？
```

選択肢:
- "はい、チェックアウトする" → `git checkout {head_branch}`
- "いいえ、このまま続行"

### 2. レビューコメントの取得

**2.1 全コメントを取得**

```bash
gh pr view {pr_number} --json comments,reviews --jq '.reviews[] | select(.state == "CHANGES_REQUESTED" or .state == "COMMENTED") | {body: .body, author: .author.login, createdAt: .createdAt, comments: .comments}'
```

**2.2 未解決コメントのフィルタリング**

以下の条件を満たすコメントを抽出:
- レビュー状態が`CHANGES_REQUESTED`または`COMMENTED`
- レビューコメントに対するリプライがない、または最新のコメントがレビュアーからのもの

レビューコメントが0件の場合:
```
## レビュー対応完了

**PR**: {pr_url}

未解決のコメントはありません。
```

終了する。

### 3. 各コメントの処理

各レビューコメントについて、以下の処理を実行:

**3.1 分析**

コメント情報を取得:
- コメント本文
- 該当ファイルと行番号（可能な場合）
- レビュアー名

Readツールでファイルを読み込み、該当箇所を確認。

**3.2 判断**

以下のいずれかを選択:

1. **修正が必要で内容が明確**
   - 自律的に修正へ進む
   - 例: 「タイポを修正してください」「変数名を変更してください」

2. **不明点あり**
   - 質問をリプライ
   - 例: 「パフォーマンスを改善してください」→「具体的にどの部分が懸念でしょうか？」

3. **同意できない/対応不要**
   - スキップして報告
   - 例: 「アーキテクチャを全面的に見直してください」→ユーザーに判断を委ねる

4. **判断が困難**
   - AskUserQuestionで確認
   - 選択肢: 修正する / 質問する / スキップ

**3.3 修正・コミット・プッシュ（修正する場合）**

**3.3.1 ファイルの修正**

EditまたはWriteツールでファイルを修正。

複数ファイルの修正が必要な場合、すべて修正してから1回のコミットにまとめる。

**3.3.2 gitスキルでコミット・プッシュ**

Skillツールを使用してgitスキルのcommitサブコマンドを実行:

```
Skill
  skill: "git"
  args: "commit"
```

gitスキルが自動的に以下を実行:
- 変更ファイルの分析
- コミットメッセージの生成（`fix: {レビュー指摘の要約}`形式）
- ステージング（git add）
- コミット
- プッシュ

**3.3.3 コミットSHAの取得**

```bash
git rev-parse HEAD
```

**3.4 リプライ**

**修正の場合**:

```bash
gh pr comment {pr_number} --body "修正しました

**コミット**: https://github.com/{owner}/{repo}/commit/{commit_sha}

{修正内容の簡潔な説明}

Co-Authored-By: Claude (jp.anthropic.claude-sonnet-4-5-20250929-v1:0) <noreply@anthropic.com>"
```

**質問の場合**:

```bash
gh pr comment {pr_number} --body "確認させてください

{質問内容}

Co-Authored-By: Claude (jp.anthropic.claude-sonnet-4-5-20250929-v1:0) <noreply@anthropic.com>"
```

### 4. サマリー

全コメントの処理が完了したら、サマリーを表示:

```
## PRレビュー対応完了

**PR**: {pr_url}

### 結果
- 修正してリプライ: {n}件
- 質問してリプライ: {n}件
- スキップ: {n}件

レビュアーによる確認をお願いします。
```

## エラーハンドリング

| エラー | 対応 |
|--------|------|
| PRが見つからない | 正しいPR番号を確認 |
| PRがCLOSED/MERGED | OPENのPRを指定 |
| プッシュ失敗 | `git pull --rebase`して再プッシュ |
| コンフリクト | 手動でコンフリクトを解決してから再実行 |
| gh CLI認証エラー | `gh auth login`で認証 |

## 注意事項

1. **絵文字の使用**: ユーザーが明示的に要求しない限り、絵文字を使わない
2. **自律的な判断**: コメントの修正内容が明確な場合は自律的に対応し、AskUserQuestionは判断が困難な場合のみ使用
3. **テスト実行**: 修正後、関連するテストがある場合は実行して確認
4. **複数ファイル**: 1つのコメントで複数ファイルの修正が必要な場合、全て修正してから1回のコミットにまとめる
5. **会話履歴の考慮**: コメントスレッドに複数のコメントがある場合、最新のコメントから意図を汲み取る
