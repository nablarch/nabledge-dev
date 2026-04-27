# Token Efficiency

## Split tasks at commit boundaries

Each step in tasks.md must map to exactly one `git commit`. This keeps
`/sv` + `/re` cycles short and prevents context window accumulation.

**Good**: step = one commit
**Bad**: one step spans multiple commits, or one step covers multiple concerns

When creating or updating tasks.md, ensure every `- [ ] Step N` can be
completed and committed in a single work unit.

## Run /sv automatically after each commit

**STOP after every commit. Do not continue to the next step.**

After completing a commit:

1. Immediately run the `/sv` skill — do not wait for the user to ask.
2. Tell the user:
   > 「{step name} 完了 (`{short_hash}`)。`/clear` → `/re` でコンテキストをリセットして次のステップへ進んでください。」
3. Wait for the user to run `/clear` → `/re`. Do not proceed on your own.

**Why stop here**: each commit = one session boundary. Crossing that boundary
without a `/re` accumulates context and defeats the purpose of this rule.
