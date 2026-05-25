# Nabledge Skill Rules

## Cross-Version Consistency

Nabledge skills (nabledge-1.2, nabledge-1.3, nabledge-1.4, nabledge-5, nabledge-6) share identical structure for prompts, workflows, templates, and scripts (path substitution only).

- When modifying skill prompts (workflows/, assets/, scripts/), apply the same change to all versions
- Apply cross-version changes in a single commit or PR — do not split by version
- If a change is version-specific, document the reason in the commit message or .work/xxxxx/notes.md
- `workflows/qa.md` contains a hardcoded processing type list that differs per version — do NOT copy this file across versions; update each version's list manually

## test-setup.sh Change Impact

When modifying CC command files (`.claude/commands/n${v}.md`) or GHC prompt files (`.github/prompts/n${v}.prompt.md`), check whether the change affects `tools/tests/test-setup.sh` in the nabledge-dev repository.

`test-setup.sh` dynamic checks work as follows:

- **CC**: runs `claude -p "/n${v} <query>"` directly — no marker dependency
- **GHC**: reads the full prompt file and substitutes `$ARGUMENTS` — no marker dependency

## GHC Prompt Filename Change

`setup-ghc.sh` copies `.github/prompts/n${v}.prompt.md` by exact filename. If the filename ever changes, the old file is **not** automatically removed from the user's `.github/prompts/` — it becomes dead weight.

`setup-ghc.sh` handles this with `rm -f "$PROJECT_ROOT/.github/prompts/n${v}"*.prompt.md` before copying. If the filename pattern changes (e.g. prefix changes), update this glob in `setup-ghc.sh` accordingly.
