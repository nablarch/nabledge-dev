# Tasks: Limit dependency graphs to 15 classes

**PR**: TBD
**Issue**: #176
**Updated**: 2026-05-29

## Workflow rules

- 1コミット = 1タスク
- SCを満たすよう実装する（依存グラフが最大15クラス、ビジネスロジックに最関連するクラスに集中）
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する
- **後方互換**: 変更はStep 3.4 Dependency diagramセクションへの追加のみ。既存の指示・構造・他セクションには一切手を加えない

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

### T4: Create PR
**Steps:**
- [ ] `Skill(skill: "pr", args: "create")`

## Done

- [x] T1: Update code-analysis.md Step 3.4 Dependency diagram — v6 — committed `dbe3cb101`
- [x] T2: Apply same change to v5/v1.4/v1.3/v1.2 — committed `08890f13c`
- [x] T3: Expert review (0 Findings) + diff check (PASS) — committed `6480f61d6`
