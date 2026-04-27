# Token Efficiency

## Split tasks at commit boundaries

Each step in tasks.md must map to exactly one `git commit`. This keeps
`/sv` + `/re` cycles short and prevents context window accumulation.

**Good**: step = one commit
**Bad**: one step spans multiple commits, or one step covers multiple concerns

When creating or updating tasks.md, ensure every `- [ ] Step N` can be
completed and committed in a single work unit.

## Suggest /sv + /re after each commit

After completing a commit, always tell the user:

> 「{step name} 完了 (`{short_hash}`)。`/sv` → `/re` でコンテキストをリセットして次のステップへ進むことを推奨します。」

Do not proceed to the next step automatically — wait for the user to `/re`.
This keeps each session focused on one commit and avoids context window growth.
