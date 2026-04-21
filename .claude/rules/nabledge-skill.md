# Nabledge Skill Rules

## Cross-Version Consistency

Nabledge skills (nabledge-1.2, nabledge-1.3, nabledge-1.4, nabledge-5, nabledge-6) share identical structure for prompts, workflows, templates, and scripts (path substitution only).

- When modifying skill prompts (workflows/, assets/, scripts/), apply the same change to all versions
- When modifying nabledge-test skill (scenarios/, evaluation logic), apply the same change to all versions
- Apply cross-version changes in a single commit or PR — do not split by version
- If a change is version-specific, document the reason in the commit message or .work/xxxxx/notes.md
- After modifying skill prompts, re-run baseline (`nabledge-test <version> --baseline`) for affected versions to keep detection rates current

## test-setup.sh Change Impact

When modifying CC command files (`.claude/commands/n${v}.md`) or GHC prompt files (`.github/prompts/n${v}.prompt.md`), check whether the change affects `tools/tests/test-setup.sh` in the nabledge-dev repository.

`test-setup.sh` depends on these marker strings:

- **CC**: `Delegate the following task` — extracts from this line onward as the prompt
- **GHC**: `#runSubagent` — extracts from this line onward as the prompt

If these markers are removed or changed, the dynamic checks in `test-setup.sh` will FAIL.
