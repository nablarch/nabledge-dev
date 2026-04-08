# Nabledge Skill Maintenance

## Cross-Version Consistency

Nabledge skills (nabledge-1.2, nabledge-1.3, nabledge-1.4, nabledge-5, nabledge-6) share identical structure for prompts, workflows, templates, and scripts (path substitution only).

- When modifying skill prompts (workflows/, assets/, scripts/), apply the same change to all versions
- When modifying nabledge-test skill (scenarios/, evaluation logic), apply the same change to all versions
- Apply cross-version changes in a single commit or PR — do not split by version
- If a change is version-specific, document the reason in the commit message or .pr/xxxxx/notes.md
- After modifying skill prompts, re-run baseline (`nabledge-test <version> --baseline`) for affected versions to keep detection rates current
