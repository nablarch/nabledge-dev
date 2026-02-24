# Daily Standup Report Generation Workflow

This workflow automatically generates daily standup meeting messages.

## Required Tools

- Bash
- AskUserQuestion

## Execution Steps

### 1. Fetch Today's Closed Issues and Open PRs

**1.1 Get Today's Date**

```bash
today=$(date -I)
echo "今日の日付: $today"
```

**1.2 Verify GitHub Repository**

```bash
gh repo view --json nameWithOwner -q .nameWithOwner
```

If repository information cannot be retrieved:
```
エラー: GitHubリポジトリが見つかりません。

確認事項:
1. 現在のディレクトリがGitリポジトリか確認してください
2. gh CLIが認証されているか確認してください (gh auth login)
```

**1.3 Fetch Today's Closed Issues**

```bash
gh issue list \
  --state closed \
  --search "closed:>=$today" \
  --json number,title,closedAt,url \
  --limit 100
```

**1.4 Fetch Open PRs**

```bash
gh pr list \
  --search "author:@me is:open" \
  --json number,title,url \
  --limit 50
```

**1.5 Parse Results**

- If closed issues result is empty array `[]`: No closed issues today
- If open PRs result is empty array `[]`: No open PRs
- Save both issue and PR information for later use

### 2. Present Closed Issues and Open PRs

Present a summary to help user recall their work:

**Format:**
```
今日の作業を確認します:

【クローズしたIssue】
- #{number}: {title} ({url})
...
(or "今日クローズしたIssueはありません" if none)

【オープン中のPR】
- PR #{number}: {title} ({url})
...
(or "オープン中のPRはありません" if none)

これらの情報をもとに、発見について教えてください。
```

### 3. Interview User for Discoveries

Use AskUserQuestion tool:

```
Question: "今日の発見は何ですか？(技術的な気づき、学び、改善点など)"
Options:
  - "Other: {free text input}"
multiSelect: false
```

Save user's answer as `discoveries`.

### 4. Categorize Issues

Categorize closed issues into two groups:

**4.1 Identify Process Improvement Issues**

Check issue **titles only** for keywords (case-insensitive matching). See "Implementation Points > Process Improvement Detection" section below for the complete keyword list.

**4.2 Regular Completed Issues**

All other closed issues that are not process improvements.

### 5. Link PRs to Issues

For each open PR, check if it references a closed issue:

**5.1 Fetch PR Details**

For each PR, check the PR body and commits for issue references like:
- "Closes #123"
- "Fixes #123"
- "Resolves #123"

**5.2 Match with Closed Issues**

If a PR references a closed issue from today, link them together for the output format.

### 6. Output Teams Message

**6.1 Message Format**

Output in the following format (Japanese):

```
## {YYYY-MM-DD} 開発共有

### 🎯 成果

{Completed regular issues with ✅}

### 🔧 開発プロセス改善

{Process improvement issues, or "特になし"}

### 📝 作業中

{Open PRs with 🚧}

### 💡 発見

{User input}
```

**6.2 Completed Issues Format (Teams Markdown Links)**

For completed issues WITHOUT linked PR:
```
- [Title text](issue_url) (#issue_number) ✅
```

For completed issues WITH linked PR:
```
- [Title text](issue_url) (#issue_number, [PR #pr_number](pr_url)) ✅
```

**6.3 Open PRs Format (Teams Markdown Links)**

For PRs that reference a closed issue:
```
- [Issue title](issue_url) (#issue_number, [PR #pr_number](pr_url)) 🚧
```

For PRs without a clear issue reference:
```
- [PR title](pr_url) (PR #pr_number) 🚧
```

**6.4 Complete Output Example**

```
## 2026-02-24 開発共有

### 🎯 成果

- [開発者として、1日の終わりに翌朝の朝会用メッセージを自動生成したい](https://github.com/owner/repo/issues/68) (#68) ✅
- [バグ修正: ログイン時のセッションタイムアウト問題](https://github.com/owner/repo/issues/67) (#67) ✅

### 🔧 開発プロセス改善

特になし

### 📝 作業中

- [Nablarch v6知識ファイル作成基盤の整備](https://github.com/owner/repo/issues/78) (#78, [PR #82](https://github.com/owner/repo/pull/82)) 🚧

### 💡 発見

Task toolの使い方について理解が深まりました。特にサブエージェントを使った
ワークフロー分離のパターンが効果的だと感じました。
```

## Error Handling

| Error | Response |
|-------|----------|
| gh CLI not available | Guide user to run `gh auth login` |
| Not a GitHub repository | Guide user to check current directory |
| Issue fetch failed | Display error message and abort |
| PR fetch failed | Display issue summary only, skip PR section, continue |
| User input empty | Treat as "なし" and continue |

## Important Notes

1. **Japanese output**: All messages and formats output in Japanese
2. **Issue limit**: Fetch up to 100 issues, 50 PRs (usually sufficient)
3. **Date format**: Use ISO 8601 format (YYYY-MM-DD) in header
4. **Teams markdown**: Use `[text](url)` format for clickable links
5. **Emoji icons**: Use ✅ for completed, 🚧 for in-progress
6. **Copy-ready**: Output format is ready to paste directly into Teams

## Implementation Points

### Issue and PR Fetch Filtering

- **Closed issues**: Use `--search "closed:>=$today"` to fetch issues closed today or later
- **Open PRs**: Use `--search "author:@me is:open"` to fetch user's open PRs

### Process Improvement Detection

Check issue **titles only** (not body) for keywords using case-insensitive substring matching:

**Japanese keywords**: "改善", "プロセス", "ワークフロー", "効率", "最適化"

**English keywords**: "improve", "improvement", "process", "workflow", "efficiency", "optimize", "optimization"

Example matches:
- "プロセス改善の提案" → matches "プロセス" and "改善"
- "Improve test workflow" → matches "improve" and "workflow"
- "Code optimization for performance" → matches "optimization"

### PR-Issue Linking Logic

1. Fetch PR details with `gh pr view {number} --json body`
2. Check PR body for patterns: `Closes #\d+`, `Fixes #\d+`, `Resolves #\d+`
3. Match extracted issue numbers with closed issues
4. Include PR link in issue output if matched

### User Experience Optimization

- Present work summary before asking questions to help recall
- Questions are clear and concise
- Error messages include specific remediation steps
- Output format is easy to copy and paste into Teams
- Teams markdown links are clickable and user-friendly
