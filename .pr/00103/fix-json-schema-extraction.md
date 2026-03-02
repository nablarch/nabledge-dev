# Fix: JSON Schema Extraction Error

**Issue**: #103
**Date**: 2026-03-02
**Error**: `Expecting value: line 1 column 1 (char 0)`

## Root Cause

The `--json-schema` option was passed to `claude -p` but not used correctly:

1. **Missing `--output-format json`**: Required when using `--json-schema`
2. **No structured_output extraction**: Response includes metadata with actual data in `structured_output` field
3. **No subtype checking**: Need to check `subtype` field to detect success/failure

### Error Logs

```json
{
  "file_id": "setting-guide-CustomizeMessageIDAndMessage",
  "error": "JSON extraction failed: Expecting value: line 1 column 1 (char 0)",
  "raw_output": "Knowledge file generated successfully for `setting-guide-CustomizeMessageIDAndMessage`.\n"
}
```

The AI returned a text message instead of JSON because the output format wasn't properly configured.

## Official Documentation (via claude-code-guide agent)

According to Claude Code documentation:

**Correct usage**:
```bash
claude -p --output-format json --json-schema '<schema>' "query"
```

**Response structure**:
```json
{
  "type": "result",
  "subtype": "success",
  "result": "...",
  "structured_output": { /* validated JSON matching schema */ }
}
```

**Error response**:
```json
{
  "type": "result",
  "subtype": "error_max_structured_output_retries",
  "result": "error message",
  "structured_output": null
}
```

## Changes Made

### 1. Fixed `run_claude()` in `common.py`

**Before**:
```python
cmd = ["claude", "-p"]
if json_schema:
    cmd.extend(["--json-schema", json.dumps(json_schema)])

return subprocess.run(cmd, ...)
```

**After**:
```python
cmd = ["claude", "-p"]
if json_schema:
    cmd.extend(["--output-format", "json"])  # Added
    cmd.extend(["--json-schema", json.dumps(json_schema)])

result = subprocess.run(cmd, ...)

# Extract structured_output from response
if json_schema and result.returncode == 0:
    response = json.loads(result.stdout)
    subtype = response.get("subtype", "")

    if subtype == "success":
        structured_output = response.get("structured_output")
        # Return structured_output as stdout
        result = subprocess.CompletedProcess(
            args=result.args,
            returncode=0,
            stdout=json.dumps(structured_output, ensure_ascii=False),
            stderr=""
        )
    elif subtype == "error_max_structured_output_retries":
        # Handle validation failure
        result = subprocess.CompletedProcess(
            args=result.args,
            returncode=1,
            stdout="",
            stderr=f"Structured output error: {response.get('result')}"
        )

return result
```

### 2. Simplified `extract_json()` in `step3_generate.py`

**Before**:
```python
def extract_json(self, output: str) -> dict:
    # Try to extract from code block
    match = re.search(r'```json?\s*\n(.*?)\n```', output, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    # Try parsing entire output
    return json.loads(output.strip())
```

**After**:
```python
def extract_json(self, output: str) -> dict:
    """When using --json-schema, output is already the structured_output JSON."""
    return json.loads(output.strip())
```

## Testing (Must Run Outside Claude Code)

**IMPORTANT**: Cannot test inside Claude Code session (nested `claude -p` not allowed).

### Test Command

```bash
# Exit Claude Code first
cd /home/tie303177/work/nabledge/work3

# Run test mode (generates 31 test files)
python tools/knowledge-creator/run.py --version 6 --test-mode
```

### Expected Result

**Before fix**:
```
ERROR: setting-guide-CustomizeMessageIDAndMessage: Expecting value: line 1 column 1 (char 0)
ERROR: cloud-native-azure_distributed_tracing: Expecting value: line 1 column 1 (char 0)
```

**After fix**:
```
[GEN] setting-guide-CustomizeMessageIDAndMessage
[GEN] cloud-native-azure_distributed_tracing
...
Generation complete:
  OK: 31
  Error: 0
```

### Verification

```bash
# Check generated files exist
ls -lh .claude/skills/nabledge-6/knowledge/setup/setting-guide/

# Check JSON is valid
cat .claude/skills/nabledge-6/knowledge/setup/setting-guide/setting-guide-CustomizeMessageIDAndMessage.json | jq .

# Check no errors in logs
grep '"status": "error"' tools/knowledge-creator/logs/v6/generate/*.json
```

## Why This Happened

The `--json-schema` option was added in commit 821c994 but implemented incorrectly:
- Passed `--json-schema` flag ✅
- Missing `--output-format json` ❌
- Missing structured_output extraction ❌
- Missing subtype error handling ❌

This caused `claude -p` to return metadata JSON instead of the actual structured output, leading to parsing errors.

## Related Files

- `tools/knowledge-creator/steps/common.py` - Fixed run_claude()
- `tools/knowledge-creator/steps/step3_generate.py` - Simplified extract_json()
- `tools/knowledge-creator/prompts/generate.md` - Prompt template (unchanged)
