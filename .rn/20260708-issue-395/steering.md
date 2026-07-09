Rn version: 0.8.0
Design: .rn/20260708-issue-395/design.md

# Goal

Add section-level links to cited knowledge MD files in skill output. Currently QA answers show bare `参照: file.json:sN` citations and code-analysis Nablarch usage shows file-level-only links; users cannot jump directly to the cited section without manual lookup.

# Acceptance criteria

- QA スキル出力の `参照:` ブロックが、ページタイトル・plain docs パス（VS Code がクリッカブルと認識する形式）・インデントしたセクションタイトルを含む形式で出力される（bare `file.json:sN` が残っていない）
- code-analysis スキル出力の `**詳細**:` フィールドが、docs ファイルへの Markdown リンク＋インデントしたセクションタイトルを含む形式で出力される
- ベンチマークスコアが退行しない：QA run-1 が安定して通過し、フルベンチマークでベースライン比の退行がない
- 変更が全 5 バージョン（nabledge-1.2, 1.3, 1.4, 5, 6）に適用されている

# Assumptions

- Section titles in JSON match the heading text in the corresponding MD file exactly — confirmed for sampled files
- VS Code integrated terminal auto-detects bare `.md` paths as clickable; `path.md#anchor` breaks detection — anchors are not used (confirmed by user testing)
- VS Code editor does not scroll to `#anchor` from a preview link — anchors give no functional benefit
- code-analysis output is written to `.nabledge/YYYYMMDD/` — relative path prefix `../../` is already used for file-level links; same prefix applies here
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

- [x] Present `design.md` to the user (including output sample images)
- [x] Take verdict via `/rn:ty` (approve) or `/rn:gm` (revise)

**Completion criteria**:

- `design.md` is approved by the user including the output sample images
- No open structural questions remain about link format or anchor algorithm

### #2: Implement QA section links — v6 only

**Purpose**: Update `qa.md` in nabledge-6 only so the `参照:` block emits page title + plain docs path + indented section title(s) instead of bare `file.json:sN` citations.

**Prerequisites**: #1 approved

**Steps**:

- [x] Identify exact line(s) to change in `.claude/skills/nabledge-6/workflows/qa.md`
- [x] Draft the new instruction text (anchor algorithm, link format, where section title comes from)
- [x] Apply change to nabledge-6/workflows/qa.md
- [x] Self-check (OK/NG per completion criterion, record in checks/task-2.md)
- [x] Prompt Engineer expert review (subagent)
- [x] Verification expert review (subagent)
- [x] Run pre-01 and confirm output format

**Completion criteria**:

- nabledge-6 QA スキルを pre-01 シナリオで実行したとき、`answer.md` の `参照:` ブロックがページタイトル・plain docs パス（`.claude/skills/nabledge-6/docs/` プレフィックス）・インデントしたセクションタイトルの形式で出力される（bare `file.json:sN` が残っていない）
- `参照:` ブロックに `#anchor` が含まれない
- `nabledge-6/workflows/qa.md` の変更が `参照:` 指示ブロック以外に及んでいない

### #3: Implement code-analysis section links — v6 only

**Purpose**: Update `code-analysis.md` and `code-analysis/template-guide.md` in nabledge-6 only so `**詳細**:` in Nablarch usage includes a Markdown link to the docs file + indented section title(s) instead of a file-level link only.

**Prerequisites**: #1 approved

**Steps**:

- [x] Identify exact line(s) to change in code-analysis.md (Step 3 read-section tracking) and template-guide.md (詳細 format)
- [x] Draft the new instruction: Step 3 reads sections → workflow carries `{file, section_id, title}` forward to Step 4 → 詳細 link uses that info
- [x] Apply change to nabledge-6 code-analysis.md and template-guide.md
- [x] Self-check (OK/NG per completion criterion, record in checks/task-3.md)
- [x] Prompt Engineer expert review (subagent)
- [x] Verification expert review (subagent)
- [x] code-analysis を実行しサンプル出力で format を確認

**Completion criteria**:

- nabledge-6 code-analysis スキルを実行したとき、出力ファイルの `**詳細**:` フィールドがページタイトルの Markdown リンク（`[ページタイトル](../../.claude/skills/nabledge-6/docs/...md)`）＋インデントしたセクションタイトルの形式で出力される（ファイルレベルリンクのみの旧形式が残っていない）
- `**詳細**:` リンクに `#anchor` が含まれない
- `code-analysis.md` と `template-guide.md` の変更が `sections_metadata` ビルド手順と `**詳細**:` 指示以外に及んでいない

### #4: v6 benchmark — QA run1 stability check

**Purpose**: Confirm v6 QA run1 passes stably before running full benchmark.

**Prerequisites**: #2 and #3 completed

**Steps**:

- [x] Run QA benchmark run1: follow the QA benchmark procedure (run1 only)
- [x] Confirm run1 passes stably (no errors, expected output format)
- [x] Self-check (OK/NG per completion criterion, record in checks/task-4.md)

**Completion criteria**:

- QA benchmark run-1（全シナリオ）が終了コード 0 で完了する
- run-1 の全シナリオ `answer.md` に bare `file.json:sN` 形式の `参照:` が残っていない（新フォーマットで出力されている）
- run-1 の全シナリオ `answer.md` に `#anchor` が含まれない

### #5: v6 benchmark — full QA and code-analysis

**Purpose**: Run full v6 benchmark for both QA and code-analysis; confirm no score regression.

**Prerequisites**: #4 completed

**Steps**:

- [x] Run full QA benchmark for v6 per the benchmark procedure
- [x] Run full code-analysis benchmark for v6 per the benchmark procedure
- [x] Compare scores vs pre-change baseline (from `docs/metrics.md`)
- [x] Confirm no regression (QA: 退行なし、実害 0 件)
- [x] Self-check (OK/NG per completion criterion, record in checks/task-5.md)

**Completion criteria**:

- v6 QA フルベンチマーク（3 run）の `crossrun-summary.md` の全シナリオ pass rate が、`tools/benchmark/results/20260612-1404-baseline-current/baseline.json` の各シナリオ `pass_rate` を下回っていない（flaky シナリオは CLEAN 扱い）
- v6 code-analysis フルベンチマークの結果に、変更前の `tools/benchmark/results/20260701-1736-code-analysis-baseline/` と比べて新たな REGRESSION DETECTED がない
- QA フルベンチ `quality-report.md` の確定判定（ナレッジ照合ベース）で実害ありの閾値割れシナリオが 0 件

### #6: Apply to remaining versions (nabledge-5, 1.4, 1.3, 1.2)

**Purpose**: Apply the same workflow changes to the remaining 4 versions after v6 benchmark passes.

**Prerequisites**: #5 completed

**Steps**:

- [x] Apply QA `参照:` change to nabledge-5, 1.4, 1.3, 1.2 (verify diff identical to v6 except version-specific parts)
- [x] Apply code-analysis `**詳細**:` change to nabledge-5, 1.4, 1.3, 1.2
- [x] Self-check (OK/NG per completion criterion, record in checks/task-6.md)
- [x] Prompt Engineer expert review (subagent)

**Completion criteria**:

- nabledge-5, 1.4, 1.3, 1.2 の各バージョンで QA pre-01 相当シナリオを実行したとき、`参照:` ブロックが v6 と同じ形式（ページタイトル・plain docs パス・インデントセクションタイトル）で出力される
- 各バージョンの code-analysis を実行したとき、`**詳細**:` フィールドが v6 と同じ形式（Markdown リンク＋インデントセクションタイトル）で出力される
- `qa.md` の変更差分が v6 との差はバージョン固有のパス名のみで、指示内容は同一である

### #7: Evaluation sign-off

**Purpose**: Final review of all changes against Acceptance criteria.

**Prerequisites**: #6 completed

**Steps**:

- [x] C-2 照合：全 28 件（3 指標 × crossrun mean 閾値割れ）をナレッジ照合して実害有無を判定
- [x] quality-report.md を C-2 照合結果で更新してコミット
- [ ] Present Acceptance criteria run result to the user
- [ ] Take verdict via `/rn:ty` (approve) or `/rn:gm` (revise)

**Completion criteria**:

- Acceptance criteria の各項目が、実際の実行結果（benchmark レポート・スキル出力）に基づいて満たされていることをユーザーが確認し `/rn:ty` で承認している

# State

- **Status**: paused
- **Date**: 2026-07-09
- **Last completed**: C-2 全28件ナレッジ照合完了、quality-report.md 更新・コミット済み（7d477b37）
- **Next**: #7 sign-off。ユーザーへの報告フォーマット指示あり：再開後に閾値割れ28件を1件ずつ「質問文・DeepEvalスコアと理由・再判定結果と根拠」形式で報告し、1件ごとに承認を取ること
- **Notes**: 実害あり3件（いずれも既存問題・今回変更と無関係）: impact-08/faith全run（fixedDate桁数誤り）、qa-19/corr run-3（JaxbBodyConverter誤り）、qa-02/faith run-1（batchInsert排他制御誤転写）。minor1件: qa-13/faith run-1。qa-12・qa-17は評価器の問題（実害なし）。残り24件は評価器の揺らぎ・評価基準の問題（実害なし）
