# Token Efficiency

## Split tasks at commit boundaries

Each step in tasks.md must map to exactly one `git commit`. This keeps
`/sv` + `/re` cycles short and prevents context window accumulation.

**Good**: step = one commit
**Bad**: one step spans multiple commits, or one step covers multiple concerns

When creating or updating tasks.md, ensure every `- [ ] Step N` can be
completed and committed in a single work unit.

## Run /sv automatically after each commit

After completing a commit, immediately run the `/sv` skill without waiting
for the user to ask. The user does not need to type `/sv` manually.

After `/sv` completes, tell the user:

> 「{step name} 完了 (`{short_hash}`)。`/re` でコンテキストをリセットして次のステップへ進んでください。」

Do not proceed to the next step automatically — wait for the user to `/re`.
This keeps each session focused on one commit and avoids context window growth.
