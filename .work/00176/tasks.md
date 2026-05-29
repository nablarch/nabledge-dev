# Tasks: Limit dependency graphs to 15 classes

**PR**: TBD
**Issue**: #176
**Updated**: 2026-05-29

## Workflow rules

- 1コミット = 1タスク
- SCを満たすよう実装する（依存グラフが最大15クラス、ビジネスロジックに最関連するクラスに集中）
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する

## Design decision

**Approach**: LLM (Step 3.4) handles class filtering — not the script.

- `generate-mermaid-skeleton.sh` generates all classes as-is (no change needed)
- Step 3.4 Dependency diagram section in `code-analysis.md` gets new rule:
  "If skeleton has more than 15 classes, reduce to 15 by dropping lowest-priority classes"
- Priority order (LLM judges from code already read in Step 1):
  1. Target class itself
  2. Classes directly called in the main business logic path
  3. Nablarch framework classes central to the feature
  4. Other project classes (helpers, utilities, entities)
  5. Peripheral imports not involved in main flow
- All 5 versions (v6/v5/v1.4/v1.3/v1.2) must be updated (same content)

## In Progress

## Not Started

### T1: Update code-analysis.md Step 3.4 Dependency diagram — v6
**File**: `.claude/skills/nabledge-6/workflows/code-analysis.md`

**Steps:**
- [ ] In Step 3.4 "Dependency diagram" section, add after "Step 2: Refine skeleton":
  - A "Step 3: Limit to 15 classes" block with the priority rule and instructions
- [ ] Verify: section order and wording match the SC exactly
- [ ] Commit: `docs: limit dependency graph to 15 classes in code-analysis workflow (v6) (#176)`

### T2: Apply same change to v5/v1.4/v1.3/v1.2
**Files**:
- `.claude/skills/nabledge-5/workflows/code-analysis.md`
- `.claude/skills/nabledge-1.4/workflows/code-analysis.md`
- `.claude/skills/nabledge-1.3/workflows/code-analysis.md`
- `.claude/skills/nabledge-1.2/workflows/code-analysis.md`

**Steps:**
- [ ] Confirm all 4 files have identical content to v6 at the target section (diff check)
- [ ] Apply identical change to all 4 files
- [ ] Verify: diff between v6 and each other version at the changed section is empty
- [ ] Commit: `docs: limit dependency graph to 15 classes in code-analysis workflow (v5/v1.4/v1.3/v1.2) (#176)`

### T3: Expert review + diff check
**Steps:**
- [ ] Run expert review (Prompt Engineer) on changed workflow files
- [ ] Address all Findings
- [ ] Diff check: confirm only the expected sections changed across all 5 versions
- [ ] Output diff check result to `.work/00176/diff-check.md`
- [ ] Present results to user for confirmation

### T4: Create PR
**Steps:**
- [ ] `Skill(skill: "pr", args: "create")`

## Done
