Rn version: 0.8.0
Design: .rn/20260708-issue-395/design.md

# Goal

Add section-level links to cited knowledge MD files in skill output. Currently QA answers show bare `参照: file.json:sN` citations and code-analysis Nablarch usage shows file-level-only links; users cannot jump directly to the cited section without manual lookup.

# Acceptance criteria

- QA (SC and QA mode) answer `参照:` lines are rendered as `[セクションタイトル](docs/path.md#anchor)` links pointing to the exact section
- code-analysis Nablarch usage `**詳細**:` fields include a section-level link for each knowledge section read during Step 3
- Linked anchors are reachable: following a link opens the correct section in the knowledge MD (anchor matches GitHub Markdown heading anchor for that section's title)
- Benchmark scores do not degrade: QA run1 passes stably, then full benchmark shows no regression vs baseline
- Change is applied to all 5 skill versions (nabledge-1.2, 1.3, 1.4, 5, 6)

# Assumptions

- GitHub Markdown anchor generation rule: lowercase the heading text, remove `[^\w -]` characters (keeping CJK, alphanumeric, hyphens, underscores, spaces), replace runs of spaces with single hyphens — verified empirically against existing docs
- Section titles in JSON match the heading text in the corresponding MD file exactly — confirmed for sampled files
- QA output is rendered in GitHub Markdown (Claude Code chat) where `[text](path.md#anchor)` links are clickable
- code-analysis output is written to `.nabledge/YYYYMMDD/` — relative path prefix `../../` is already used for file-level links; section links use the same prefix + `#anchor`
- All 5 versions share identical `qa.md` structure (processing-type list differs but citation format is the same); `code-analysis.md` differs only in version-specific path names

# Rules

- commit and push every change; one completion marker per task
- v6 first: implement and benchmark v6 only; only after v6 benchmark passes, apply to remaining versions
- Benchmark sequence: QA run1 stable first → QA full benchmark → code-analysis full benchmark (never skip steps)
- No manual edits to RBKC-generated files (knowledge JSON, docs MD)

# Tasks

### #1: Design sign-off

**Purpose**: Confirm the anchor-generation approach, link format for QA and code-analysis, and scope before implementation begins.

**Prerequisites**: none

**Steps**:

- [ ] Present `design.md` to the user (including output sample images)
- [ ] Take verdict via `/rn:ty` (approve) or `/rn:gm` (revise)

**Completion criteria**:

- `design.md` is approved by the user including the output sample images
- No open structural questions remain about link format or anchor algorithm

### #2: Implement QA section links — v6 only

**Purpose**: Update `qa.md` in nabledge-6 only so the `参照:` line emits `[セクションタイトル](docs/path.md#anchor)` links instead of bare `file.json:sN` citations.

**Prerequisites**: #1 approved

**Steps**:

- [ ] Identify exact line(s) to change in `.claude/skills/nabledge-6/workflows/qa.md`
- [ ] Draft the new instruction text (anchor algorithm, link format, where section title comes from)
- [ ] Apply change to nabledge-6/workflows/qa.md
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-2.md)
- [ ] Prompt Engineer expert review (subagent)
- [ ] Verification expert review (subagent)

**Completion criteria**:

- `参照:` instruction in `nabledge-6/workflows/qa.md` specifies Markdown link format `[title](path#anchor)` for each cited section
- Anchor algorithm matches GitHub Markdown spec (lowercase, strip non-word except hyphens/spaces, spaces→hyphens)
- No existing QA instruction content removed or altered beyond the citation format change

### #3: Implement code-analysis section links — v6 only

**Purpose**: Update `code-analysis.md` and `code-analysis/template-guide.md` in nabledge-6 only so `**詳細**:` in Nablarch usage includes a section-level link to each knowledge section read in Step 3.

**Prerequisites**: #1 approved

**Steps**:

- [ ] Identify exact line(s) to change in code-analysis.md (Step 3 read-section tracking) and template-guide.md (詳細 format)
- [ ] Draft the new instruction: Step 3 reads sections → workflow carries `{file, section_id, title}` forward to Step 4 → 詳細 link uses that info
- [ ] Apply change to nabledge-6 code-analysis.md and template-guide.md
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-3.md)
- [ ] Prompt Engineer expert review (subagent)
- [ ] Verification expert review (subagent)

**Completion criteria**:

- `**詳細**:` instruction in `nabledge-6` specifies section-level link format `[file title](docs/path.md) > [section title](docs/path.md#anchor)` (or equivalent)
- Workflow instruction explains how to carry section-id metadata from Step 3 to Step 4 for link generation
- No existing code-analysis instruction content removed or altered beyond the link format change

### #4: v6 benchmark — QA run1 stability check

**Purpose**: Confirm v6 QA run1 passes stably before running full benchmark.

**Prerequisites**: #2 and #3 completed

**Steps**:

- [ ] Run QA benchmark run1: follow the QA benchmark procedure (run1 only)
- [ ] Confirm run1 passes stably (no errors, expected output format)
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-4.md)

**Completion criteria**:

- QA benchmark run1 completes without errors
- Output includes `参照:` links in Markdown link format (not bare file.json:sN)
- Links are well-formed (path and anchor present)

### #5: v6 benchmark — full QA and code-analysis

**Purpose**: Run full v6 benchmark for both QA and code-analysis; confirm no score regression.

**Prerequisites**: #4 completed

**Steps**:

- [ ] Run full QA benchmark for v6 per the benchmark procedure
- [ ] Run full code-analysis benchmark for v6 per the benchmark procedure
- [ ] Compare scores vs pre-change baseline (from `docs/metrics.md`)
- [ ] Confirm no regression
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-5.md)

**Completion criteria**:

- Full QA benchmark pass rate ≥ baseline
- Full code-analysis benchmark pass rate ≥ baseline
- Any difference is explainable (format improvement) or within noise

### #6: Apply to remaining versions (nabledge-5, 1.4, 1.3, 1.2)

**Purpose**: Apply the same workflow changes to the remaining 4 versions after v6 benchmark passes.

**Prerequisites**: #5 completed

**Steps**:

- [ ] Apply QA `参照:` change to nabledge-5, 1.4, 1.3, 1.2 (verify diff identical to v6 except version-specific parts)
- [ ] Apply code-analysis `**詳細**:` change to nabledge-5, 1.4, 1.3, 1.2
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-6.md)
- [ ] Prompt Engineer expert review (subagent)

**Completion criteria**:

- All 5 versions have the same citation format instruction (processing-type lists may differ)
- The 4 newly updated files differ from v6 only in version-specific path names

### #7: Evaluation sign-off

**Purpose**: Final review of all changes against Acceptance criteria.

**Prerequisites**: #6 completed

**Steps**:

- [ ] Present Acceptance criteria run result to the user
- [ ] Take verdict via `/rn:ty` (approve) or `/rn:gm` (revise)

**Completion criteria**:

- All Acceptance criteria verified as met
- User approves the changes via `/rn:ty`

# State

<!-- template placeholder -->
