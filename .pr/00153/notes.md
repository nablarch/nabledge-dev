# Notes

## 2026-03-12

### Context: R2 Fabrication Findings Background

The large kc run (run_id: 20260309T232615, work1) ran ACDEM with max_rounds=2 on all 421 v6 knowledge files:
- Phase D R1: 48 fabrication findings among 289 "has_issues" files (total 419 files)
- Phase E R1: Fixed 289 files, deleted their findings files
- Phase D R2: 30 fabrication findings among 205 "has_issues" files
- Phase E R2: Fixed 205 files, deleted their findings files

### Problem: R2 Findings Are Gone

Phase E deletes findings files after fixing (`os.remove(findings_path)` in phase_e_fix.py:100).
Phase D R2's findings files for the 205 "has_issues" files were deleted by Phase E R2.

The findings directory (`20260309T232615/phase-d/findings/`) only contains:
- 212 clean files (findings were never deleted - only has_issues files get deleted by Phase E)
- 1 file with a single `section_issue` finding
- Total: 213 files = the clean ones from Phase D R2

The 30 fabrication findings from Phase D R2 are not recoverable from the findings directory.

### Approach: Re-run Phase D on Phase D R2 ISSUE Files

Identified the 205 Phase D R2 ISSUE files from the execution log (lines 889-1097).
Selected 20 diverse representative files from 6+ categories.
Launched subagent to run `python3 tools/knowledge-creator/scripts/run.py --version 6 --phase D`
on the sample in work2.

### Technical Notes

- work2/.lw → symlink to work1/.lw (RST sources)
- Phase D findings write to .logs/v6/{run_id}/phase-d/findings/ (gitignored)
- Knowledge files read from .cache/v6/knowledge/ (post-Phase E R2 state)
- clean_phase not needed for fresh run (new run_id = new findings dir)

### Results

- Batch 1 (run 20260312T102320): 2 fabrications, both real, in testing-framework-batch--csv
- Batch 2 (run 20260312T103251): 7 fabrications (6 real, 1 ambiguous) across 6 files
- Total: 9 findings across 40 sampled files, false positive rate = 0%
- All unambiguous findings are genuine fabrications
- Phase E R2 fixed many but not all fabrications
- 3 systematic patterns: grid-table header invention, empty-split generation, inference-as-fact

See report.md for full analysis including per-finding RST comparison.
