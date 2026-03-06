---
name: nabledge-test
description: Benchmark framework for nabledge skills. Runs scenarios in isolated sub-agent contexts to eliminate bias. Supports baseline mode for improvement verification.
---

# Nabledge-Test

Benchmark framework for nabledge skills. Detects expected keywords/components and measures performance metrics.
Each scenario runs in an isolated sub-agent context (Task tool) to eliminate cross-scenario bias.

## Usage

```bash
nabledge-test 6 qa-001                          # Single scenario (1 trial)
nabledge-test 6 --all                           # All scenarios (1 trial each)
nabledge-test 6 --list                          # List all scenarios
nabledge-test 6 qa-001 --trials 3               # Single scenario (3 trials)
nabledge-test 6 --all --trials 5                # All scenarios (5 trials each)
nabledge-test 6 "知識検索系を全部実行して"        # Free-form instruction
nabledge-test 6 --baseline                      # Baseline mode: run all, save baseline, generate comparison report
```

**Trial count**: Use `--trials N` to run each scenario N times (default: 1). Results are averaged across trials.

## Key Principles

- **Measure everything, judge nothing**: Report detection rates and measured values without arbitrary targets
- **Isolated execution**: Each scenario runs in a separate Task tool context to prevent cross-contamination
- **Measurement discipline**: You are a measurement instrument, not a helper

### Measurement Discipline Rules

- Follow target skill workflows exactly — do NOT improvise
- Record actual execution — do NOT fabricate steps
- Let failures be failures — do NOT mask with workarounds
- Always complete the measurement — do NOT stop execution early
- No self-imposed limits — token usage and execution time may vary significantly (3,000-70,000+)

## When invoked

### Step 1: Parse arguments

Format: `nabledge-test <version> [<scenario-id> | --all | --list | --baseline | "<free-form>"] [--trials N]`

**If no arguments provided**: Display usage and exit.

```
Usage: nabledge-test <version> [<scenario-id> | --all | --list | --baseline | "<free-form>"] [--trials N]

Examples:
  nabledge-test 6 qa-001                          # Single scenario (1 trial)
  nabledge-test 6 --all                           # All scenarios (1 trial each)
  nabledge-test 6 --list                          # List all available scenarios
  nabledge-test 6 --baseline                      # Baseline mode (all scenarios, save + compare)
  nabledge-test 6 qa-001 --trials 3               # Single scenario (3 trials)
  nabledge-test 6 --all --trials 5                # All scenarios (5 trials each)
  nabledge-test 6 "知識検索系を全部実行して"        # Free-form instruction

Arguments:
  <version>              Required. Version number (6 or 5)
  <scenario-id>          Optional. Specific scenario to test (e.g., qa-001, ca-001)
  --all                  Optional. Test all scenarios
  --list                 Optional. List all available scenarios
  --baseline             Optional. Baseline mode: run all scenarios, save to baseline/, generate comparison
  "<free-form>"          Optional. Free-form instruction for test selection
  --trials N             Optional. Number of trials per scenario (default: 1)
```

**If `--list` is provided**: Display scenario list and exit.

1. Read scenarios file: `.claude/skills/nabledge-test/scenarios/nabledge-<version>/scenarios.json`
2. Group scenarios by type (qa-* for qa, ca-* for code-analysis)
3. Display formatted list:

```
Available scenarios for nabledge-<version>:

QA (QA) - <count> scenarios:
  - qa-001: <question>
  - qa-002: <question>

Code Analysis (CA) - <count> scenarios:
  - ca-001: <question>
  - ca-002: <question>

Total: <total_count> scenarios
```

**Parse modes**:

| Argument | Mode | Scenarios | Baseline |
|----------|------|-----------|----------|
| `qa-001` | single | 1個 | No |
| `--all` | all | 全件 | No |
| `--baseline` | baseline | 全件 | Yes |
| `"free text"` | free-form | AI判断 | No |

**`--baseline` implies `--all`**: Baseline mode always runs all scenarios. `--trials N` can be combined.

### Step 2: Resolve PR number

PR番号は作業記録の保存先 `.pr/xxxxx/` を決定するために必要。

**Resolve from current branch name**:

```bash
# Get current branch name
branch=$(git rev-parse --abbrev-ref HEAD)

# Extract PR number from branch name pattern: <number>-<description>
# Examples: 125-improve-search-performance → 00125
#           88-redesign-index-hints → 00088
pr_number=$(echo "$branch" | grep -oP '^\d+' | xargs printf '%05d')

# Verify .pr directory exists
if [ ! -d ".pr/${pr_number}" ]; then
  mkdir -p ".pr/${pr_number}"
fi
```

**If branch is `main` or has no number prefix**: Use `00000` as fallback and warn the user.

Store as `$PR_NUMBER` (5-digit zero-padded string) for use in subsequent steps.

### Step 3: Load scenarios

From `.claude/skills/nabledge-test/scenarios/nabledge-<version>/scenarios.json`:

```json
{
  "id": "qa-001",
  "question": "バッチの起動方法を教えてください",
  "keywords": ["keyword1", "keyword2", ...],
  "sections": ["section1", "section2"]
}
```

For code-analysis scenarios (ca-*), additional fields:
```json
{
  "id": "ca-001",
  "question": "ExportProjectsInPeriodActionの実装を理解したい",
  "target_file": "path/to/file.java",
  "expectations": ["expectation1", "expectation2", ...]
}
```

**Build detection items**:

For qa (qa-*):
```
detection_items = []
for keyword in scenario.keywords:
    detection_items.append(f"Response includes '{keyword}'")
if scenario.sections:
    for section in scenario.sections:
        detection_items.append(f"Response references '{section}' section")
```

For code-analysis (ca-*):
```
detection_items = []
for expectation in scenario.expectations:
    detection_items.append(expectation)
```

### Step 4: Execute scenarios via sub-agents

**CRITICAL**: Each scenario MUST run in a separate Task tool invocation. This ensures:
- No context bleeding between scenarios (bias elimination)
- Each scenario starts from a clean state
- Metrics reflect true isolated performance

**For each scenario**, spawn a Task tool with the following prompt:

```
You are a measurement instrument executing a nabledge skill test.

## Rules
- Follow target skill workflows EXACTLY — do NOT improvise
- Record actual execution — do NOT fabricate steps
- Let failures be failures — do NOT mask with workarounds
- Complete all steps without stopping
- No self-imposed limits on token usage or execution time

## Task
1. Read `.claude/skills/nabledge-<version>/SKILL.md` and follow its instructions
2. Execute the following question: "<scenario.question>"
3. Record timing for each step (use `date '+%Y-%m-%dT%H:%M:%S'`)

## Output
When complete, output the following clearly delimited sections:

### RESPONSE_START
<paste the complete response/answer from nabledge-<version> here>
### RESPONSE_END

### METRICS_START
```json
{
  "total_duration_seconds": <number>,
  "steps": [
    {
      "step": <number>,
      "name": "<step name>",
      "duration_seconds": <number>,
      "in_tokens_estimate": <number>,
      "out_tokens_estimate": <number>
    }
  ],
  "tool_calls": {
    "Read": <count>,
    "Bash": <count>,
    "Grep": <count>,
    "Write": <count>
  },
  "total_tool_calls": <number>,
  "response_chars": <number>
}
```
### METRICS_END

### OUTPUT_FILES_START
<list any files created by the skill, with their full paths, one per line>
<if no files created, write "none">
### OUTPUT_FILES_END
```

**Execution strategy**:

- Launch scenarios **one at a time** (sequential), not in parallel
- Wait for each Task to complete before starting the next
- This is because Task tool results must be parsed and saved per scenario

**For multiple trials** (`--trials N`):

- Run each scenario N times sequentially
- Each trial is a separate Task tool invocation
- Collect all trial results, then average metrics

**After each Task completes**:

1. Parse the delimited output sections (RESPONSE, METRICS, OUTPUT_FILES)
2. Save results to the workspace (see Step 5)
3. Run detection check (see Step 6)

### Step 5: Save workspace results

**Workspace location**: `.tmp/nabledge-test/run-<YYYYMMDD-HHMMSS>/`

For each completed scenario:

```
.tmp/nabledge-test/run-<YYYYMMDD-HHMMSS>/
  <scenario-id>/
    response.md          # Full response text from RESPONSE section
    metrics.json         # Parsed from METRICS section
    grading.json         # Detection check results (Step 6)
    output/              # Output files (ca-* only, copied from paths in OUTPUT_FILES)
```

**Save response.md**: Extract text between `### RESPONSE_START` and `### RESPONSE_END`.

**Save metrics.json**: Parse JSON from between `### METRICS_START` and `### METRICS_END`. If parsing fails (sub-agent didn't output clean JSON), extract what's available and note the error.

**Save output files** (ca-* scenarios only): Copy files listed in OUTPUT_FILES section to `output/` directory.

### Step 6: Check detection items

For each scenario, evaluate detection items against the response:

**QA (qa-*)**:

```python
for item in detection_items:
    if "includes" in item:
        keyword = extract_keyword(item)  # e.g., "DataReadHandler"
        detected = keyword in response_text
    elif "references" in item:
        section = extract_section(item)  # e.g., "request-path"
        detected = section in response_text
```

**Code-analysis (ca-*)**:

Each expectation is checked by examining the response text and output files:
- "Finds target file X" → check if filename appears in response
- "Identifies X" → check if X appears in response or output
- "Creates dependency diagram" → check for "classDiagram" or "graph" in output
- "Creates sequence diagram" → check for "sequenceDiagram" in output
- "Output includes X" → check output files for X
- "Output file saved to" → check if output files exist
- "Analysis duration calculated" → check if duration appears in response

**Write grading.json**:

```json
{
  "scenario_id": "<id>",
  "detection_items": [
    {
      "text": "Response includes 'DataReadHandler'",
      "detected": true,
      "evidence": "Found in response: 'DataReadHandler（nablarch.fw.handler.DataReadHandler）'"
    },
    {
      "text": "Response includes 'DataReader'",
      "detected": false,
      "evidence": "Not found in response text"
    }
  ],
  "summary": {
    "detected": 5,
    "not_detected": 1,
    "total": 6,
    "detection_rate": 0.833
  }
}
```

### Step 7: Generate individual scenario reports

Write to `.pr/<PR_NUMBER>/nabledge-test/<YYYYMMDDHHMM>/<scenario-id>.md`:

```markdown
# Test: <scenario-id>

**Date**: <timestamp>
**Question**: <scenario.question>

## Scenario
- **Type**: Knowledge-Search / Code-Analysis
- **Keywords** (<count>): <list>
- **Sections** (<count>): <list>

## Detection Results

**Detection Rate**: <detected>/<total> (<percentage>%)

### Detection Items
- ✓ Response includes 'DataReadHandler'
  Evidence: Found in response
- ✗ Response includes 'XYZ'
  Evidence: Not found in response

## Metrics
- **Duration**: <seconds>秒
- **Tool Calls**: <count>
- **Response Length**: <chars> chars
- **Tokens (estimate)**: <total> (IN: <in> / OUT: <out>)

### Step Breakdown
| Step | Name | Duration | IN Tokens | OUT Tokens |
|------|------|----------|-----------|------------|
| 1 | <name> | <seconds>秒 | <count> | <count> |
| 2 | <name> | <seconds>秒 | <count> | <count> |

## 目視判定

| 観点 | 判定 | メモ |
|------|------|------|
| 回答の正確性 | ◯ / △ / ✗ | （手動記入） |
| 回答の網羅性 | ◯ / △ / ✗ | （手動記入） |
| コード例の品質 | ◯ / △ / ✗ | （手動記入） |
| 日本語の自然さ | ◯ / △ / ✗ | （手動記入） |

## Files
- **Response**: <workspace>/<scenario-id>/response.md
- **Metrics**: <workspace>/<scenario-id>/metrics.json
- **Grading**: <workspace>/<scenario-id>/grading.json
```

**目視判定テンプレート**: 自動実行では空欄のまま生成する。改善検証時にkiyohomeが手動で埋める用途。

### Step 8: Generate aggregate report

**This step runs for `--all` mode and `--baseline` mode.**

Write `.pr/<PR_NUMBER>/nabledge-test/report-<YYYYMMDDHHMM>.md`:

```markdown
# Nabledge-<version> Test Run: YYYY-MM-DD HH:MM

| 項目 | 値 |
|------|-----|
| Run ID | YYYYMMDD-HHMMSS |
| Branch | <branch_name> |
| Commit | <git_commit_sha_short> |
| 実行シナリオ | <count> (QA: <qa_count>, CA: <ca_count>) |
| 実行方式 | サブエージェント逐次実行 |
| Trials | <trials_count> |

---

## 📊 結果サマリー

| # | Scenario | 質問 | Type | 検出 | 時間 | トークン |
|---|----------|------|------|------|------|---------|
| 1 | <id> | <question> | QA/CA | <detected>/<total> | <seconds>秒 | <tokens> |
...

**凡例**: QA=QA, CA=Code-Analysis, ⚡=最速, 🐢=最遅, 🔥=最大トークン, ⭐=100%検出

### 統計
- **キーワード/コンポーネント検出**: <total_detected>/<total_items> (<rate>%)
  - QA: <qa_detected>/<qa_total> (<qa_rate>%)
  - CA: <ca_detected>/<ca_total> (<ca_rate>%)
- **平均実行時間**: <avg>秒 (QA: <qa_avg>秒 / CA: <ca_avg>秒)
  - 最速: <id> (<time>秒)
  - 最遅: <id> (<time>秒)
- **平均トークン**: <avg> (推定値)
  - 最少: <id> (<tokens>)
  - 最多: <id> (<tokens>)

---

## ⚡ パフォーマンス分析

### Knowledge-Search: ステップ別平均時間

| ステップ | 名称 | 平均 | 中間値 | 割合 | 範囲 | 推定トークン (IN/OUT) |
|----------|------|------|--------|------|------|-----------------------|
| 1 | <name> | <avg>秒 | <med>秒 | <pct>% | <min>-<max>秒 | <in>/<out> |
...

ボトルネック: Step <n> (<name>) が時間の<pct>%を占める 🔥

<details>
<summary>Code-Analysis: ステップ別詳細</summary>

| ステップ | 名称 | 平均 | 中間値 | 割合 | 範囲 | 推定トークン (IN/OUT) |
|----------|------|------|--------|------|------|-----------------------|
| 1 | <name> | <avg>秒 | <med>秒 | <pct>% | <min>-<max>秒 | <in>/<out> |
...

ボトルネック: Step <n> (<name>) が時間の<pct>%を占める 🔥
</details>

**Step name mapping** (use actual step names from metrics, fallback to these):
- Knowledge-Search: ワークフロー読込, キーワード抽出, ファイルマッチング, セクション抽出, 関連性スコアリング, コンテンツ読込, セクション判定, 回答生成
- Code-Analysis: ターゲット特定, 知識検索, テンプレート読込, データ事前入力, 図表生成, コンテンツ構築, 出力完成, 実行時間計算

注: トークン数は推定値 (文字数÷4)。正確な測定にはClaude API responseのusageフィールドが必要。

---

## 💡 主要な発見

<Analyze data for patterns, anomalies, key findings. Write 2-3 sections.>

---

## 🔬 仮説と改善提案

### 仮説1: <title>
**根拠**: <evidence>
**検証**: <how>
**期待**: <outcome>

### 仮説2: <title>
...

---

## 📎 詳細データ

### 個別シナリオレポート
- [<id>](<YYYYMMDDHHMM>/<id>.md) - <rate>% - <question>
...

### ワークスペース
- `.tmp/nabledge-test/run-<YYYYMMDD-HHMMSS>/`

---

*Generated by nabledge-test v2 | Run: YYYYMMDD-HHMMSS | Commit: <sha_short>*
```

**Statistics calculation**:

1. Read all metrics.json and grading.json from workspace
2. Filter by scenario type (qa-*, ca-*)
3. For step-by-step analysis:
   - Group by step name across scenarios of same type
   - Calculate: average, median, range, percentage of total
4. Identify bottleneck (step with highest percentage) → add 🔥
5. Apply ⚡ to fastest, 🐢 to slowest, ⭐ to 100% detection

### Step 9: Baseline mode — save baseline

**This step runs ONLY when `--baseline` flag is provided.**

#### 9a: Create baseline directory

```bash
BASELINE_DIR=".claude/skills/nabledge-test/baseline"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TARGET_DIR="${BASELINE_DIR}/${TIMESTAMP}"
mkdir -p "${TARGET_DIR}"
```

#### 9b: Save meta.json

```json
{
  "timestamp": "2026-03-06T14:30:00Z",
  "run_id": "20260306-143000",
  "version": 6,
  "branch": "<branch_name>",
  "commit": "<full_git_commit_sha>",
  "commit_short": "<7-char_sha>",
  "scenarios_count": 10,
  "trials": 1,
  "scenarios": {
    "qa": ["qa-001", "qa-002", "qa-003", "qa-004", "qa-005"],
    "code-analysis": ["ca-001", "ca-002", "ca-003", "ca-004", "ca-005"]
  }
}
```

#### 9c: Copy per-scenario data

For each scenario, copy from workspace to baseline:

```bash
for scenario_id in $(ls .tmp/nabledge-test/run-${TIMESTAMP}/); do
  mkdir -p "${TARGET_DIR}/${scenario_id}"

  # Copy metrics
  cp ".tmp/nabledge-test/run-${TIMESTAMP}/${scenario_id}/metrics.json" \
     "${TARGET_DIR}/${scenario_id}/metrics.json"

  # Copy response
  cp ".tmp/nabledge-test/run-${TIMESTAMP}/${scenario_id}/response.md" \
     "${TARGET_DIR}/${scenario_id}/response.md"

  # Copy grading
  cp ".tmp/nabledge-test/run-${TIMESTAMP}/${scenario_id}/grading.json" \
     "${TARGET_DIR}/${scenario_id}/grading.json"

  # Copy output files (ca-* only)
  if [ -d ".tmp/nabledge-test/run-${TIMESTAMP}/${scenario_id}/output" ]; then
    cp -r ".tmp/nabledge-test/run-${TIMESTAMP}/${scenario_id}/output" \
       "${TARGET_DIR}/${scenario_id}/output"
  fi
done
```

#### 9d: Update latest symlink

```bash
cd "${BASELINE_DIR}"
rm -f latest
ln -s "${TIMESTAMP}" latest
```

#### 9e: Generate comparison report (if previous baseline exists)

**Check for previous baseline**:

```bash
# Count baseline directories (excluding 'latest' symlink)
BASELINE_COUNT=$(ls -d ${BASELINE_DIR}/2* 2>/dev/null | wc -l)

if [ "${BASELINE_COUNT}" -le 1 ]; then
  echo "No previous baseline found. Generating initial baseline report."
  PREV=""
else
  # Get second-to-last (= previous) baseline directory
  PREV=$(ls -d ${BASELINE_DIR}/2* | sort | tail -2 | head -1)
fi

CURR="${TARGET_DIR}"
```

**Generate `comparison-report.md`** in `${TARGET_DIR}/`:

**If no previous baseline (PREV is empty)**:

```markdown
# ベースライン比較レポート

## 概要

| 項目 | 値 |
|------|-----|
| 今回 | <TIMESTAMP> |
| 前回 | （初回ベースライン） |
| Branch | <branch_name> |
| Commit | <commit_short> |

---

初回ベースラインのため、比較データはありません。
次回 `--baseline` 実行時に、このベースラインとの比較レポートが生成されます。
```

**If previous baseline exists**:

Read `${PREV}/meta.json` for previous run info. Read all `${PREV}/<scenario-id>/metrics.json` and `${PREV}/<scenario-id>/grading.json` for previous data.

Write comparison-report.md:

```markdown
# ベースライン比較レポート

## 概要

| 項目 | 前回 | 今回 | 差分 |
|------|------|------|------|
| Run ID | <prev_run_id> | <curr_run_id> | |
| Branch | <prev_branch> | <curr_branch> | |
| Commit | <prev_commit> | <curr_commit> | |
| 日時 | <prev_timestamp> | <curr_timestamp> | |

---

## 総合評価

<ここに第三者視点でフラットに改善効果を評価する文章を書く。>

ポイント:
- 改善したことと改善していないことを公平に記述
- 数値の変化を根拠に、「改善」「横ばい」「劣化」を判定
- 統計的にサンプル1回の場合はばらつきの可能性に言及
- 特定のシナリオだけ改善/劣化している場合はその偏りを指摘

---

## シナリオ別比較表

| # | Scenario | 検出率 (前回) | 検出率 (今回) | 変化 | 時間 (前回) | 時間 (今回) | 変化 | トークン (前回) | トークン (今回) | 変化 | 目視 |
|---|----------|-------------|-------------|------|-----------|-----------|------|---------------|---------------|------|------|
| 1 | qa-001 | 6/6 | 6/6 | → | 48秒 | 42秒 | ↓6秒 🟢 | 7,019 | 6,500 | ↓519 🟢 | |
...

**凡例**:
- 🟢 改善（検出率↑ or 時間/トークン↓10%超）
- 🔴 劣化（検出率↓ or 時間/トークン↑10%超）
- → 変化なし（±10%以内）
- 目視: 手動記入欄（◯改善 / △変化なし / ✗劣化）

**変化判定ルール**:
- 検出率: 1項目でも減少 → 🔴、増加 → 🟢、同数 → →
- 時間: ±10%以内 → →、10%超の短縮 → 🟢、10%超の増加 → 🔴
- トークン: ±10%以内 → →、10%超の削減 → 🟢、10%超の増加 → 🔴

---

## 統計比較

| 指標 | 前回 | 今回 | 変化 |
|------|------|------|------|
| 全体検出率 | <prev>% | <curr>% | <diff>pp |
| QA検出率 | <prev>% | <curr>% | <diff>pp |
| CA検出率 | <prev>% | <curr>% | <diff>pp |
| 平均実行時間 | <prev>秒 | <curr>秒 | <diff>秒 (<pct>%) |
| QA平均実行時間 | <prev>秒 | <curr>秒 | <diff>秒 |
| CA平均実行時間 | <prev>秒 | <curr>秒 | <diff>秒 |
| 平均トークン | <prev> | <curr> | <diff> (<pct>%) |

---

## 実測データからの分析

<全シナリオの実測データを俯瞰して、パターンや傾向を分析する。>

分析の観点:
- 全体的なトレンド（改善/劣化の方向性）
- シナリオタイプ別の傾向（QA vs CA）
- 特異なシナリオの特定（他と異なる動きをしたもの）
- ステップ別の変化（ボトルネックの移動）
- ばらつきの変化

---

## 分析を受けた仮説

<実測データの分析結果を踏まえて、実装を見た上での仮説を立てる。>

### 仮説1: <title>
**根拠**: <実測データのどの数値が根拠か>
**実装の該当箇所**: <ワークフローやスクリプトのどこが関連するか>
**予測**: <この仮説が正しければ、次に何が起きるか>

### 仮説2: <title>
...

---

## 再現手順

```bash
# 今回のベースラインと同じ状態で再計測
git checkout <commit_sha>
nabledge-test <version> --baseline

# 前回のベースラインと同じ状態で再計測
git checkout <prev_commit_sha>
nabledge-test <version> --baseline
```

---

*Generated by nabledge-test v2 baseline mode | Compared: <prev_timestamp> → <curr_timestamp>*
```

### Step 10: Display summary

**For single/all mode**:

```
✓ qa-001: 5/5 keywords + 1/1 sections detected | 48s | 7,019 tokens
✓ qa-002: 5/5 keywords + 1/1 sections detected | 14s | 15,200 tokens
✗ ca-004: 8/12 expectations detected | 64s | 8,820 tokens

Aggregate report: .pr/<PR_NUMBER>/nabledge-test/report-<YYYYMMDDHHMM>.md
Workspace: .tmp/nabledge-test/run-<YYYYMMDD-HHMMSS>/
```

**For baseline mode** (append to above):

```
Baseline saved: .claude/skills/nabledge-test/baseline/<TIMESTAMP>/
Latest symlink: .claude/skills/nabledge-test/baseline/latest → <TIMESTAMP>/
Comparison report: .claude/skills/nabledge-test/baseline/<TIMESTAMP>/comparison-report.md
```

## Dependencies

- **Task tool**: Required for sub-agent execution (Claude Code Task tool)
- **nabledge-6 / nabledge-5**: Target skill to be tested
- **git**: For branch name and commit SHA resolution

Does NOT depend on skill-creator. nabledge-test v2 is self-contained.
