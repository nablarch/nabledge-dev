# Tasks: Allow scripts no-permission-prompt (#178)

**PR**: #305
**Issue**: #178
**Branch**: 178-allow-scripts-no-permission-prompt
**Updated**: 2026-04-14

## In Progress

### Fix setup-cc.sh permission patterns (2 issues found 2026-04-14)

**Root causes** identified by re-running `/n6 code-analysis ImportZipCodeFileAction`:

1. **`Write(.nabledge/*)` missing** — Step 3.5 uses the Write tool to overwrite the pre-filled template created by `prefill-template.sh`. Since the file exists, Claude Code shows "Do you want to overwrite...?". Pattern `Write(.nabledge/*)` is not in `add_skill_permissions()`.

2. **`Bash(OUTPUT_PATH=*)` is stale** — Workflow was changed (commit `af1bbae2`) so `prefill-template.sh` is now called as `bash .../prefill-template.sh ...` (output path read from stdout). The old pattern `OUTPUT_PATH=*` no longer matches. Missing: `Bash(bash .claude/skills/nabledge-{v}/scripts/prefill-template.sh *)`.

**Steps:**
- [ ] Fix `setup-cc.sh` `add_skill_permissions()`: replace `Bash(OUTPUT_PATH=*)` with `Bash(bash .claude/skills/nabledge-{v}/scripts/prefill-template.sh *)` and add `Write(.nabledge/*)`
- [ ] Re-run `/n6 code-analysis ImportZipCodeFileAction` end-to-end to confirm no permission prompts

## Not Started

### Cross-version propagation: scripts + workflows

**Steps:**
- [ ] Copy 3 new scripts to each version:
  - `get-hints.sh` (nabledge-5, 1.2, 1.3, 1.4 have version-specific KNOWLEDGE_DIR paths)
  - `record-start.sh` (identical across versions)
  - `finalize-output.sh` (identical across versions)
- [ ] Update `code-analysis.md` for nabledge-5, 1.2, 1.3, 1.4 to replace inline bash with script calls (same as done for nabledge-6 in commits `3e18e857`, `0eab2c7e`)
- [ ] Fix `bash` prefix for `generate-mermaid-skeleton.sh` and `prefill-template.sh` calls (same as `99aa64d8`)
- [ ] Commit per version

**Context**: nabledge-6 scripts are at `.claude/skills/nabledge-6/scripts/`. The new scripts use `SKILL_DIR=.claude/skills/nabledge-{v}` internally — need to adjust paths when copying. `record-start.sh` and `finalize-output.sh` use `.nabledge/` output dir and are version-agnostic. `get-hints.sh` references knowledge dir which is version-specific.

### Cross-version propagation: `GUIDE-GHC.md`

**Steps:**
- [ ] Apply GHC settings notes (done for nabledge-6 in commit `92b60602`) to nabledge-5, 1.2, 1.3, 1.4
- [ ] Commit

### CHANGELOG update

**Steps:**
- [ ] Add entries to `[Unreleased]` in each affected version's `CHANGELOG.md`
- [ ] Focus on user-facing impact (Japanese, per `.claude/rules/changelog.md`)

### Expert Review → PR creation

**Steps:**
- [ ] Run expert review per `.claude/rules/expert-review.md`
- [ ] Save to `.pr/00178/review-by-*.md`
- [ ] Create PR with `Skill(skill: "pr", args: "create")`

## Done

- [x] Fix `prefill-template.sh` escape_sed() bug (`/` as sed delimiter) — commit `a40e1d23`
- [x] Add `add_skill_permissions()` to `setup-cc.sh` with correct patterns — commits `f401497b`, `2ef28263`
- [x] Add GHC no-prompt-confirmation notes to `nabledge-6/plugin/GUIDE-GHC.md` — commit `92b60602`
- [x] Revert `allowed-tools: Bash` from nabledge-6 SKILL.md (ineffective via sub-agent) — commit `55418b9e`
- [x] Extract inline bash into dedicated scripts for nabledge-6 (`get-hints.sh`, `record-start.sh`, `finalize-output.sh`) — commit `3e18e857`
- [x] Use full-path script calls in nabledge-6 workflows — commit `0eab2c7e`
- [x] Fix bash prefix for `generate-mermaid-skeleton.sh` and `prefill-template.sh` — commit `99aa64d8`
- [x] Fix `finalize-output.sh` using lowercase target name for output path — commit `30a92c0f`
- [x] Fix `prefill-template.sh` call as single-line command (no pipe/multiline) — commit `af1bbae2`
- [x] Prevent agent from absolutizing script paths in workflows — commit `07a943b5`
- [x] Add required target confirmation step before code-analysis — commit `ff69d5a1`
- [x] Consolidate bash command rules and use run-verbatim fence in nabledge-6 — commit `ad561b6d`
