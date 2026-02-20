---
name: op
description: 朝会用メッセージを自動生成。今日クローズしたIssueを取得し、発見・その他をヒアリングして、振り返りを生成します。
argument-hint: (no arguments needed)
allowed-tools: Bash, Task, AskUserQuestion
---

# 朝会用メッセージ生成スキル (op)

このスキルは1日の終わりに翌朝の朝会用メッセージを自動生成します。

## 機能

- 今日クローズしたGitHub Issueを自動取得
- ユーザーから「発見」と「その他」をヒアリング
- 今日の成果から振り返りを自動生成 (200文字程度)
- Teamsにコピペできる形式で出力

## 実行フロー

### 1. ワークフロー実行

Task toolを使って `workflows/generate.md` を実行します。

```
Task
  subagent_type: "general-purpose"
  description: "朝会用メッセージ生成ワークフローを実行"
  prompt: "朝会用メッセージを生成してください。以下のワークフローに従ってください。

{workflows/generate.mdの内容をReadツールで読み込んで展開}

## 実行コンテキスト
- 実行日: {today's date}
- リポジトリ: {current repository}
"
```

## 実装ノート

1. **引数不要**: `/op` だけで実行可能
2. **日本語出力**: すべてのメッセージは日本語
3. **エラーハンドリング**: Issueが0件の場合も適切に処理
4. **Task tool使用**: ワークフローは別コンテキストで実行

## エラーハンドリング

| エラー | 対応 |
|-------|------|
| gh CLIが利用できない | `gh auth login` の実行を案内 |
| GitHubリポジトリではない | 現在のディレクトリがGitHubリポジトリか確認を案内 |
| 今日のIssueが0件 | 「今日クローズしたIssueはありません」と表示して続行 |

詳細な使用例は `assets/examples.md` を参照してください。
