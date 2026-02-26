---
name: nabledge-test
description: Test nabledge-6/5 by detecting keywords/components in responses. Measures performance metrics without pass/fail judgment. Saves results to .pr/xxxxx/.
---

# Nabledge-Test

Benchmark framework for nabledge skills. Detects expected keywords/components and measures performance metrics.

## Usage

```bash
nabledge-test 6 handlers-001                    # Single test (1 trial)
nabledge-test 6 --all                           # All tests (1 trial each)
nabledge-test 6 --category handlers             # Category (1 trial each)
nabledge-test 6 handlers-001 --trials 3         # Single test (3 trials)
nabledge-test 6 --all --trials 5                # All tests (5 trials each)
```

**Trial count**: Use `--trials N` to run each scenario N times (default: 1). Results are averaged across trials.

## How it works

1. Load scenario from `scenarios/nabledge-6/scenarios.json`
2. Build detection items list (keywords + sections for KS, components for CA)
3. Execute nabledge-<version> inline and track metrics
4. Check detection items via string search in response
5. Save individual results to `.pr/xxxxx/nabledge-test/YYYYMMDDHHMM/<scenario-id>-HHMMSS.md`
6. Generate aggregate report to `.pr/xxxxx/nabledge-test/report-YYYYMMDDHHMM.md`

**Key principle**: Measure everything, judge nothing. Report detection rates (x/x) and measured values without arbitrary targets.

## When invoked

### Step 1: Parse arguments

Format: `nabledge-test <version> [<scenario-id> | --all | --category <cat>] [--trials N]`

**Parse options**:
- `<version>`: Required. Version number (6 or 5)
- `<scenario-id>`: Optional. Specific scenario to test
- `--all`: Optional. Test all scenarios
- `--category <cat>`: Optional. Test scenarios by category
- `--trials N`: Optional. Number of trials per scenario (default: 1)

**Examples**:
- `nabledge-test 6 handlers-001` → Test handlers-001, 1 trial
- `nabledge-test 6 handlers-001 --trials 3` → Test handlers-001, 3 trials
- `nabledge-test 6 --all --trials 5` → Test all, 5 trials each

### Step 2: Load scenario

From `scenarios/nabledge-6/scenarios.json`:

```json
{
  "id": "handlers-001",
  "question": "データリードハンドラでファイルを読み込むには？",
  "keywords": ["DataReadHandler", "DataReader", ...],
  "sections": ["overview", "usage"]
}
```

### Step 3: Build detection items list

Build detection items list (no performance targets):

```python
detection_items = []

# Keyword checks
for keyword in scenario.keywords:
    detection_items.append(f"Response includes '{keyword}'")

# Section checks
if scenario.sections:
    section_list = " or ".join([f"'{s}'" for s in scenario.sections])
    detection_items.append(f"Response mentions {section_list} sections")

# Note: No performance targets (token/tool call ranges)
# Performance is measured but not used for pass/fail judgment
```

### Step 4: Read skill-creator procedures

Read skill-creator eval-mode documentation:

```
Read .claude/skills/skill-creator/references/eval-mode.md
Read .claude/skills/skill-creator/references/schemas.md
Read .claude/skills/skill-creator/agents/executor.md
Read .claude/skills/skill-creator/agents/grader.md
```

### Step 5: Setup workspace

**Workspace location**: `.tmp/nabledge-test/eval-<scenario-id>-HHMMSS/` (temporary workspace, timestamp-based to avoid conflicts)

Create structure:
```
.tmp/nabledge-test/
└── eval-<scenario-id>-HHMMSS/
    ├── with_skill/
    │   ├── outputs/
    │   │   ├── transcript.md
    │   │   └── metrics.json
    │   ├── grading.json
    │   └── timing.json
```

```bash
mkdir -p .tmp/nabledge-test/eval-<scenario-id>-$(date +%H%M%S)/with_skill/outputs
```

### Step 6: Execute nabledge-6 inline - Follow executor.md

**CRITICAL**: Do NOT use the Skill tool. Execute nabledge-<version> instructions directly in this conversation to maintain workflow continuity.

**Record start time**:
```bash
date -u +%Y-%m-%dT%H:%M:%SZ > start_time.txt
```

**Load nabledge-<version> skill procedures**:
```bash
Read .claude/skills/nabledge-<version>/SKILL.md
Read .claude/skills/nabledge-<version>/workflows/knowledge-search.md
Read .claude/skills/nabledge-<version>/workflows/keyword-search.md
Read .claude/skills/nabledge-<version>/workflows/section-judgement.md
Read .claude/skills/nabledge-<version>/knowledge/index.toon
```

**Execute the question <scenario.question> by following nabledge-<version> procedures**:
- Apply keyword-search workflow to identify relevant knowledge files
- Use section-judgement workflow to select appropriate sections
- Generate response following nabledge-<version> guidelines
- **Track every tool call** (Read, Bash, Grep) for metrics

**While executing, track**:
- Tool calls made (Read, Bash, Grep, etc.)
- Steps executed
- Response content

**Write transcript** to `workspace/eval-<id>/with_skill/outputs/transcript.md`:

```markdown
# Eval Execution Transcript

## Eval Prompt
<scenario.question>

## Skill
- Path: .claude/skills/nabledge-<version>
- Name: nabledge-<version>
- Description: Nablarch <version> Knowledge Base

## Input Files
None provided

## Execution

### Step 1: Load skill workflows and knowledge index
**Start**: <timestamp in ISO 8601 format>
**Action**: Read nabledge-<version> skill procedures
**Tool**: Read (4 calls)
- SKILL.md
- workflows/keyword-search.md
- workflows/section-judgement.md
- knowledge/index.toon

**INPUT**: None (initial load)
**IN Tokens**: 0

**OUTPUT**: Successfully loaded workflows and knowledge index
**OUT Tokens**: <approx character count / 4>

**End**: <timestamp in ISO 8601 format>
**Duration**: <seconds>s

---

### Step 2: Execute knowledge search (keyword-search workflow)
**Start**: <timestamp>
**Action**: Extract keywords and match against index

**INPUT**:
```
Query: <scenario.question>
```
**IN Tokens**: <approx character count / 4>

**Tool**: Mental analysis + Read
**Result**: <summary of keyword extraction and file selection>

**OUTPUT**:
```
Keywords extracted:
- L1: [...]
- L2: [...]

Files selected:
- <file1> (score: X)
- <file2> (score: Y)
```
**OUT Tokens**: <approx character count / 4>

**End**: <timestamp>
**Duration**: <seconds>s

---

### Step 3: Read candidate sections (section-judgement workflow)
**Start**: <timestamp>
**Action**: Read specific sections from knowledge files

**INPUT**:
```
Files: [<file1>, <file2>]
```
**IN Tokens**: <approx character count / 4>

**Tool**: Bash (jq)
**Result**: <summary of sections read>

**OUTPUT**:
```
Sections extracted:
- <file1>: [section1, section2]
- <file2>: [section3]
```
**OUT Tokens**: <approx character count / 4>

**End**: <timestamp>
**Duration**: <seconds>s

---

(... continue for each significant action with same format ...)

## Output Files
None created (response was inline)

## Final Result
<Copy the full response from nabledge-6 here>

## Token Summary
- **Total IN Tokens**: <sum of all IN tokens>
- **Total OUT Tokens**: <sum of all OUT tokens>
- **Total Tokens**: <IN + OUT>

## Issues
None
```

**Write metrics.json**:

Extract data from transcript.md:
- IN/OUT tokens from each step
- Duration from each step (calculate from Start and End timestamps if needed)

```json
{
  "tool_calls": {
    "Read": <count>,
    "Bash": <count>,
    "Grep": <count>
  },
  "total_tool_calls": <total>,
  "total_steps": <count>,
  "files_created": [],
  "errors_encountered": 0,
  "output_chars": <char count of response>,
  "transcript_chars": <char count of transcript>,
  "tokens": {
    "total_in": <sum of all IN tokens>,
    "total_out": <sum of all OUT tokens>,
    "total": <IN + OUT>,
    "by_step": [
      {
        "step": 1,
        "name": "Load skill workflows",
        "in_tokens": <count from transcript>,
        "out_tokens": <count from transcript>,
        "duration_seconds": <duration from transcript>
      },
      {
        "step": 2,
        "name": "Execute knowledge search",
        "in_tokens": <count from transcript>,
        "out_tokens": <count from transcript>,
        "duration_seconds": <duration from transcript>
      }
    ]
  }
}
```

**IMPORTANT**: Ensure duration_seconds is populated for each step. This data is used for aggregate statistics (median, range) in the final report.

**Record end time and calculate duration**:
```bash
date -u +%Y-%m-%dT%H:%M:%SZ > end_time.txt
# Calculate duration_seconds
```

**Write timing.json**:
```json
{
  "executor_start": "<start_time>",
  "executor_end": "<end_time>",
  "executor_duration_seconds": <duration>,
  "grader_start": null,
  "grader_end": null,
  "grader_duration_seconds": 0,
  "total_duration_seconds": <duration>
}
```

**After writing timing.json, immediately proceed to Step 7 without stopping. This is a continuous evaluation workflow.**

### Step 7: Check detection items

**Record grader start time**

**Read transcript and outputs**:
```bash
Read workspace/eval-<id>/with_skill/outputs/transcript.md
```

**Evaluate each detection item**:

For each detection item in detection_items list:
1. Check if item is detected by examining transcript
2. Record detected/not_detected with evidence
3. Extract relevant quotes as evidence

**Write grading.json**:
```json
{
  "detection_items": [
    {
      "text": "Response includes 'DataReadHandler'",
      "detected": true,
      "evidence": "Found in transcript: 'DataReadHandler（nablarch.fw.handler.DataReadHandler）'"
    },
    {
      "text": "Response includes 'DataReader'",
      "detected": true,
      "evidence": "Found multiple times in response"
    },
    ...
  ],
  "summary": {
    "detected": <count>,
    "not_detected": <count>,
    "total": <count>,
    "detection_rate": <rate>
  },
  "execution_metrics": {
    "tool_calls": { ... },
    "total_tool_calls": <count>,
    "total_steps": <count>,
    "errors_encountered": 0,
    "output_chars": <count>,
    "transcript_chars": <count>
  },
  "timing": {
    "executor_duration_seconds": <duration>,
    "grader_duration_seconds": <duration>,
    "total_duration_seconds": <total>
  }
}
```

**Update timing.json** with grader times.

### Step 8: Generate individual scenario report

**Read data from workspace files**:
1. Read `grading.json` for expectations and summary
2. Read `metrics.json` for tool_calls, tokens, and by_step data
3. Read `timing.json` for total duration

**Extract step-by-step data**:
- From `metrics.json`, extract `tokens.by_step` array
- Each entry contains: step, name, in_tokens, out_tokens, duration_seconds

Write `.pr/xxxxx/nabledge-test/YYYYMMDDHHMM/<scenario-id>-HHMMSS.md`:

```markdown
# Test: <scenario-id>

**Date**: <timestamp>
**Question**: <scenario.question>

## Scenario
- **Keywords** (<count>): <list>
- **Sections** (<count>): <list>

## Detection Results

**Detection Rate**: <detected>/<total>

### Detection Items
- ✓ Response includes 'DataReadHandler'
  Evidence: Found in response
- ✓ Response includes 'DataReader'
  Evidence: Found in response
- ✗ Response includes 'XYZ'
  Evidence: Not found in response

## Metrics (Measured Values)
- **Duration**: <seconds>s
- **Tool Calls**: <count>
- **Response Length**: <chars> chars
- **Tokens**: <total> (IN: <in> / OUT: <out>)

### Token Usage by Step
| Step | Name | IN Tokens | OUT Tokens | Total | Duration |
|------|------|-----------|------------|-------|----------|
| 1 | Load workflows | <in_tokens> | <out_tokens> | <in+out> | <duration_seconds>s |
| 2 | Knowledge search | <in_tokens> | <out_tokens> | <in+out> | <duration_seconds>s |
| 3 | Read sections | <in_tokens> | <out_tokens> | <in+out> | <duration_seconds>s |
| ... | ... | ... | ... | ... | ... |

## Files
- **Transcript**: .tmp/nabledge-test/eval-<id>-HHMMSS/with_skill/outputs/transcript.md
- **Grading**: .tmp/nabledge-test/eval-<id>-HHMMSS/with_skill/grading.json
- **Metrics**: .tmp/nabledge-test/eval-<id>-HHMMSS/with_skill/outputs/metrics.json
```

### Step 9: Generate aggregate report

**Calculate statistics from metrics.json files**:

For each scenario type (knowledge-search, code-analysis):

1. **Read all metrics.json files**:
   ```bash
   find .tmp/nabledge-test/eval-*-*/with_skill/outputs/metrics.json
   ```

2. **Filter by scenario type**:
   - Knowledge-Search: processing-*, libraries-*, handlers-*
   - Code-Analysis: code-analysis-*

3. **Extract by_step data**:
   ```bash
   jq '.tokens.by_step' <metrics.json>
   ```

4. **Group by step name** and calculate for each step:
   - **Average duration**: mean of all duration_seconds values
   - **Median duration**: median (middle value when sorted)
   - **Range**: "min-max秒" format (e.g., "3-8秒")
   - **Percentage**: (avg_duration / total_avg_duration) * 100
   - **Avg IN tokens**: mean of all in_tokens values
   - **Avg OUT tokens**: mean of all out_tokens values

5. **Identify bottleneck**:
   - Find step with highest percentage
   - Add 🔥 emoji in 割合 column
   - Add bottleneck note after table

6. **Generate insights**:
   - For 💡 主要な発見: Analyze data for patterns, anomalies, key findings
   - For 🔬 仮説と改善提案: Based on bottlenecks and patterns, propose testable hypotheses

**Example calculation for Knowledge-Search Step 1**:
```
Scenarios: processing-005, processing-002, libraries-001, handlers-001, processing-004
Step 1 durations: [5, 4, 8, 6, 7] seconds
- Average: (5+4+8+6+7)/5 = 6秒
- Median: sort([5,4,8,6,7]) = [4,5,6,7,8], middle value = 6秒
- Range: "4-8秒" (min=4, max=8)
- Percentage: 6/48 * 100 = 12.5%
- Tokens: average IN/OUT from all scenarios
```

**Step name mapping** (use actual step names from metrics.json):
- If steps have generic names like "Step 1", "Step 2", map to meaningful names:
  - Knowledge-Search: ワークフロー読込, キーワード抽出, ファイルマッチング, セクション抽出, 関連性スコアリング, コンテンツ読込, セクション判定, 回答生成
  - Code-Analysis: ターゲット特定, 知識検索, テンプレート読込, データ事前入力, 図表生成, コンテンツ構築, 出力完成, 実行時間計算

Write `.pr/xxxxx/nabledge-test/report-YYYYMMDDHHMM.md`:

```markdown
# Nabledge-<version> Test Run: YYYY-MM-DD HH:MM:SS

| 項目 | 値 |
|------|-----|
| Run ID | YYYYMMDD-HHMMSS |
| 実行シナリオ | <count> (knowledge-search: <ks_count>, code-analysis: <ca_count>) |
| 実行方式 | 並列実行 (<count>エージェント) |

---

## 📊 結果サマリー

| # | Scenario | 質問 | Type | 検出 | 時間 | トークン |
|---|----------|------|------|------|------|---------|
| 1 | <scenario-id> | <question> | KS/CA | <detected>/<total> | <seconds>秒 | <tokens> |
| 2 | <scenario-id> | <question> | KS/CA | <detected>/<total> | <seconds>秒 | <tokens> |
...

**凡例**: KS=Knowledge-Search, CA=Code-Analysis, ⚡=最速, 🐢=最遅

### 統計
- **キーワード/コンポーネント検出**: 全シナリオで全項目検出 (<total_detected>/<total_items>)
- **平均実行時間**: <avg_seconds>秒 (KS: <ks_avg>秒 / CA: <ca_avg>秒)
  - 最速: <fastest_scenario> (<fastest_time>秒)
  - 最遅: <slowest_scenario> (<slowest_time>秒)
- **平均トークン**: <avg_tokens> (推定値)
  - 最少: <min_scenario> (<min_tokens>)
  - 最多: <max_scenario> (<max_tokens>)

### 検出項目について
- **知識検索**: 想定キーワード (5個) + セクション参照 (2個) = 7項目
- **コード解析**: コンポーネント/メソッド/アノテーション/図表/構造 = 11-15項目
- **測定方法**: 応答テキスト内での文字列検索

---

## 💡 主要な発見

### 1. 全シナリオで検出項目を確認 ✓
すべてのシナリオで、想定したキーワード/コンポーネントが応答に含まれていることを確認。
- 知識検索: キーワード5個 + セクション参照2個 = 7/7検出
- コード解析: メソッド/アノテーション/図表など = 11-15項目検出

### 2. <Performance observation title>
<Description based on measured data>
- <Metric 1>: <value> (range: <min>-<max>)
- <Metric 2>: <value> (range: <min>-<max>)

### 3. <Bottleneck or pattern title>
<Description of performance bottlenecks>
- ボトルネック: <step name> が<percent>%を占める
- 改善余地: <specific optimization opportunity>

---

## ⚡ パフォーマンス分析

### Knowledge-Search: ステップ別平均時間

| ステップ | 名称 | 平均時間 | 中間値 | 割合 | 範囲 | 推定トークン (IN/OUT) |
|----------|------|---------|--------|------|------|-----------------------|
| 1 | ワークフロー読込 | <avg>秒 | <median>秒 | <percent>% | <min-max>秒 | <in>/<out> (推定) |
| 2 | キーワード抽出 | <avg>秒 | <median>秒 | <percent>% | <min-max>秒 | <in>/<out> (推定) |
| 3 | ファイルマッチング | <avg>秒 | <median>秒 | <percent>% | <min-max>秒 | <in>/<out> (推定) |
| ... | ... | ... | ... | ... | ... | ... |
| 8 | 回答生成 | <avg>秒 | <median>秒 | <percent>% 🔥 | <min-max>秒 | <in>/<out> (推定) |

ボトルネック: Step <n> (<name>) が時間の<percent>%を占める

注: トークン数は推定値 (文字数÷4)。正確な測定にはClaude API responseのusageフィールドが必要。

<details>
<summary>Code-Analysis: ステップ別詳細</summary>

| ステップ | 名称 | 時間 | 中間値 | 割合 | 範囲 | 推定トークン (IN/OUT) |
|----------|------|------|--------|------|------|-----------------------|
| 1 | ターゲット特定 | <avg>秒 | <median>秒 | <percent>% | - | <in>/<out> (推定) |
| 2 | 知識検索 | <avg>秒 | <median>秒 | <percent>% | - | <in>/<out> (推定) |
| ... | ... | ... | ... | ... | ... | ... |
| 6 | コンテンツ構築 | <avg>秒 | <median>秒 | <percent>% 🔥 | - | <in>/<out> (推定) |

ボトルネック: Step <n> (<name>) が全体の<percent>%

注: トークン数は推定値 (文字数÷4)。正確な測定にはClaude API responseのusageフィールドが必要。
</details>

**IMPORTANT**:
- Add 🔥 emoji to the step with highest percentage
- Use <details> tag to collapse Code-Analysis table

---

## 🔬 仮説と改善提案

### 仮説1: <Hypothesis title>
**根拠**: <Evidence from data>
**検証**: <How to verify>
**期待**: <Expected outcome>

### 仮説2: <Hypothesis title>
**根拠**: <Evidence from data>
**検証**: <How to verify>
**期待**: <Expected outcome>

### 仮説3: <Hypothesis title>
**根拠**: <Evidence from data>
**検証**: <How to verify>
**期待**: <Expected outcome>

**Examples from report-202602260800.md**:
- "回答生成を段階化すれば並列化可能"
- "トークン推定値と実測値に乖離"
- "index.toon読み込みがオーバーヘッド"

---

## 📎 詳細データ

### 個別シナリオレポート
各シナリオの詳細な実行ログ、期待値評価、コード例は個別レポートを参照：

- [<scenario-id>](YYYYMMDDHHMM/<scenario-id>-HHMMSS.md) - <percent>% - <description>
- [<scenario-id>](YYYYMMDDHHMM/<scenario-id>-HHMMSS.md) - <percent>% ⭐ - <description>
...

### メトリクスデータ
JSON形式の詳細メトリクス（トークン使用量、ツール呼び出し、タイミング）は、各シナリオのワークスペースを参照。

### ワークスペース
実行時の詳細なトランスクリプトとグレーディング結果：

- `.tmp/nabledge-test/eval-<scenario-id>-HHMMSS/`
- `.tmp/nabledge-test/eval-<scenario-id>-HHMMSS/`
...

---

## 🧪 テスト実施方法

<details>
<summary>実行環境と設定 (オプション)</summary>

### 実行環境
- **ツール**: nabledge-test
- **ターゲット**: nabledge-<version>
- **並列実行**: <count>エージェント同時起動
- **ワークスペース**: \`.tmp/nabledge-test/eval-<id>-<timestamp>/\`

### エージェント構成
| Agent ID | Scenario | Start |
|----------|----------|-------|
| <agent_id> | <scenario-id> | HH:MM:SS |
...

### 測定方法
- **実行時間**: 各ステップの開始・終了時刻を記録（実測）
- **トークン数**: 文字数÷4で推定（⚠️ 近似値）
- **ツール呼び出し**: Read/Bash/Grep/Writeの実行回数（実測）

### 制約事項
- トークン数は推定値（実際のAPI使用量ではない）
- 並列実行のため個別エージェントのトークン消費は合算されない
- タイムスタンプの精度は秒単位
</details>

---

## 🔄 再現手順

\```bash
# 同じテストを再実行
nabledge-test <version> --all

# 特定のシナリオのみ
nabledge-test <version> <scenario-id>

# カテゴリ別
nabledge-test <version> --category <category>
\```

**注意**: 並列実行のため、個別シナリオのタイムスタンプは若干異なります。

---

*Generated by nabledge-test | Run: YYYYMMDD-HHMMSS | Duration: ~<minutes>min*
```

**Note**: The 🧪 テスト実施方法 section is optional and can be omitted for simpler reports.

### Step 10: Display summary

```
✓ handlers-001: 5/5 keywords + 2/2 sections detected | 68s | 9,480 tokens
  Report: .pr/xxxxx/nabledge-test/202602260800/handlers-001-153045.md
  Transcript: .tmp/nabledge-test/eval-handlers-001-153045/with_skill/outputs/transcript.md

Aggregate report: .pr/xxxxx/nabledge-test/report-202602260800.md
```

## Dependencies

- skill-creator (evaluation procedures only - not invoked as skill)
- nabledge-6 or nabledge-5 (target skill)

## Notes

- nabledge-test follows skill-creator's eval-mode procedures
- Does NOT invoke skill-creator as a skill
- Manually executes executor and grader steps
- Workspace: `.tmp/nabledge-test/eval-<id>-HHMMSS/` (timestamp-based to avoid conflicts)
