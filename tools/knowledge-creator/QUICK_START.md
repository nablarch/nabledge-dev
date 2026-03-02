# nabledge-creator Quick Start

## ⚠️ Important: Nested Session Limitation

The tool uses `claude -p` which **cannot run from within Claude Code**. You must run it from a normal terminal.

## Usage

### 1. Exit Claude Code

First, exit the current Claude Code session.

### 2. Run from Terminal

```bash
cd /home/tie303177/work/nabledge/work3

# Test with small batch first (optional)
# Edit logs/v6/classified.json to include only first 10 files for testing

# Run all steps
python tools/knowledge-creator/run.py --version 6

# Or run specific steps
python tools/knowledge-creator/run.py --version 6 --step 1    # List sources
python tools/knowledge-creator/run.py --version 6 --step 2    # Classify
python tools/knowledge-creator/run.py --version 6 --step 3    # Generate knowledge files
python tools/knowledge-creator/run.py --version 6 --step 4    # Build index.toon
python tools/knowledge-creator/run.py --version 6 --step 5    # Generate docs
python tools/knowledge-creator/run.py --version 6 --step 6    # Validate (not yet implemented)
```

### 3. Options

```bash
# Dry-run (show what would be done)
python tools/knowledge-creator/run.py --version 6 --dry-run

# Adjust concurrency (default: 4)
python tools/knowledge-creator/run.py --version 6 --concurrency 8

# Process both v5 and v6
python tools/knowledge-creator/run.py --version all
```

## Current Status

| Step | Status | Description |
|------|--------|-------------|
| 1 | ✅ Complete | List 252 source files |
| 2 | ✅ Complete | Classify all files (100% match) |
| 3 | ✅ Code complete | Generate knowledge files (needs external testing) |
| 4 | ✅ Code complete | Build index.toon (needs Step 3 output) |
| 5 | ✅ Code complete | Generate browsable docs (needs Step 3 output) |
| 6 | ⚠️ Design only | Validation (17 checks + 4 AI aspects) not implemented |

## Output Locations

```
.claude/skills/nabledge-6/knowledge/
  ├── processing-pattern/
  │   ├── nablarch-batch/*.json
  │   ├── web-application/*.json
  │   └── ...
  ├── component/
  │   ├── handlers/*.json
  │   ├── libraries/*.json
  │   └── adapters/*.json
  └── index.toon

.claude/skills/nabledge-6/docs/
  ├── processing-pattern/
  ├── component/
  └── ...

tools/knowledge-creator/logs/v6/
  ├── sources.json (252 files)
  ├── classified.json (252 files)
  ├── generate/ (per-file logs)
  ├── classify-patterns/ (pattern classification logs)
  └── validate/ (validation results)
```

## Troubleshooting

### "Cannot launch Claude Code inside another session"

**Solution**: Exit Claude Code and run from normal terminal.

### Step 3 takes too long

**Solution**:
1. Reduce concurrency: `--concurrency 1`
2. Test with small batch first (edit classified.json)
3. Monitor progress in `logs/v6/generate/`

### Knowledge files not generated

**Check**:
1. Did Step 3 complete without errors?
2. Check logs in `logs/v6/generate/`
3. Verify claude CLI is available: `which claude`

## Next Steps

1. **Test Step 3**: Run with small batch (10 files)
2. **Verify output**: Check generated knowledge files
3. **Test Step 4-5**: Build index and docs
4. **Implement Step 6**: Validation checks (see design document)
5. **Full run**: Process all 252 files

## Documentation

- Full README: `tools/knowledge-creator/README.md`
- Implementation Status: `tools/knowledge-creator/IMPLEMENTATION_STATUS.md`
- Design Spec: `doc/99-nabledge-creator-tool/knowledge-creator-design.md`
