# Standup Report Generation Workflow

This workflow automatically generates standup meeting messages.

## Required Tools

- Bash
- AskUserQuestion

## Execution Steps

### 1. Fetch Today's Closed Issues

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

**1.4 Parse Results**

- If result is empty array `[]`: Treat issue list as "今日クローズしたIssueはありません"
- If result has issues: Save issue information and proceed to next step

### 2. Interview User for Discoveries and Notes

**2.1 Collect Discoveries**

Use AskUserQuestion tool:

```
Question: "今日の発見は何ですか？(技術的な気づき、学び、改善点など)"
Options:
  - "Other: {free text input}"
multiSelect: false
```

Save user's answer as `discoveries`.

**2.2 Collect Other Notes**

Use AskUserQuestion tool:

```
Question: "その他共有したいことはありますか？(予定、相談事項など。なければ「なし」と入力してください)"
Options:
  - "Other: {free text input}"
multiSelect: false
```

Save user's answer as `other_notes`.
If answer is empty or "なし", set `other_notes = "なし"`.

### 3. Generate Reflection

**3.1 Analyze Achievements**

Analyze from today's closed issue titles and content:
- What are the main achievements?
- What problems were solved?
- What features were added?
- What is the impact going forward?

**3.2 Generate Reflection Text**

Generate reflection with following criteria:
- **Length**: ~200 Japanese characters (180-220 characters as guideline)
- **Structure**: Composed of 3 parts
  1. Today's achievements (what was accomplished)
  2. Its significance (why important, who benefits)
  3. Future impact (what becomes possible next)
- **Tone**: Positive, constructive, specific expressions
- **Language**: Japanese

**Generation Approach**:
1. Extract main themes from issue titles
2. Find common themes or relationships if multiple issues
3. Sentence 1: State today's specific achievements
4. Sentences 2-3: Explain significance and who/how it helps
5. Sentence 4: Describe future developments or impact

**Example Output**:
```
今日はユーザー認証機能の実装を完了し、セキュリティレビューも通過しました。
これによりユーザーが安全にログインできる基盤が整い、次フェーズの権限管理機能の
開発に着手できます。また、認証フローのテスト自動化により品質保証も強化されました。
```

### 4. Output Teams Message

**4.1 Message Format**

Output in the following format (Japanese):

```
## アウトプット

{Issue list}

## 発見

{User input}

## 振り返り

{Auto-generated reflection (~200 characters)}

## その他

{User input, or "なし" if none}
```

**4.2 Issue List Format**

When issues exist:
```
- #{number}: {title} ({url})
- #{number}: {title} ({url})
...
```

When zero issues:
```
今日クローズしたIssueはありません
```

**4.3 Complete Output Example**

```
## アウトプット

- #68: 開発者として、1日の終わりに翌朝の朝会用メッセージを自動生成したい。なぜなら効率的に進捗を共有するため (https://github.com/owner/repo/issues/68)
- #67: バグ修正: ログイン時のセッションタイムアウト問題 (https://github.com/owner/repo/issues/67)

## 発見

Task toolの使い方について理解が深まりました。特にサブエージェントを使った
ワークフロー分離のパターンが効果的だと感じました。

## 振り返り

今日は朝会用メッセージ生成スキルの実装を完了しました。これにより毎日の
振り返り作成が自動化され、開発者は本来の開発作業に集中できるようになります。
また、GitHub APIを活用した自動情報収集のパターンを確立できたことで、今後の
類似機能開発にも応用できる見込みです。

## その他

明日は新しいスキルのテストを実施する予定です。
```

## Error Handling

| Error | Response |
|-------|----------|
| gh CLI not available | Guide user to run `gh auth login` |
| Not a GitHub repository | Guide user to check current directory |
| Issue fetch failed | Display error message and abort |
| User input empty | Treat as "なし" and continue |

## Important Notes

1. **Japanese output**: All messages and formats output in Japanese
2. **Issue limit**: Fetch up to 100 issues (usually sufficient)
3. **Date format**: Use ISO 8601 format (YYYY-MM-DD)
4. **Reflection quality**: Include significance and impact, not just facts
5. **Copy-ready**: Output format is ready to paste directly into Teams

## Implementation Points

### Issue Fetch Filtering

Using `--search` option with `closed:>=` in `gh issue list` command efficiently fetches issues closed today or later.

### Reflection Generation Logic

1. Extract main themes from issue titles
2. Find common themes or relationships if multiple issues
3. Consider significance of achievements (why important, who benefits)
4. Consider future impact (what becomes possible, what changes)
5. Summarize in ~200 Japanese characters

### User Experience Optimization

- Questions are clear and concise
- Provide default values ("なし" etc.)
- Error messages include specific remediation steps
- Output format is easy to copy
