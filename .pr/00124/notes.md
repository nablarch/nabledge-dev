# Notes

## 2026-03-26

### Environment Check

Before starting kc gen, verified:
- AWS credentials: set in environment (Bedrock access)
- Claude CLI: v2.1.84 available
- v1.2 RST sources: 293 files in `.lw/nab-official/v1.2/document/` (already checked out)
- v1.2 catalog: empty template - Phase A will populate it
- v1.2 mappings: 44 RST patterns in `tools/knowledge-creator/mappings/v1.2.json`
- SVN credentials: NOT needed for initial `gen` (only needed for `regen` to detect source changes)

### Decision: Start with full gen

v1.2 has no knowledge files yet. Running full `gen` to go through all phases ABCDEM.
Reference: v1.4 full gen took ~10249 seconds (2.8 hours) for 553 files with concurrency=4.
v1.2 has 293 RST source files; actual catalog size after splitting may be higher.
