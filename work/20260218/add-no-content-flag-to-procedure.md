# Add _no_content Flag to Mapping Procedure

**Date**: 2026-02-18

## Summary

Updated mapping creation procedure to handle navigation-only files (index.rst with only toctree directives).

## Problem

During Phase 6 target file assignment, many entries were assigned `index.json` as target, which consolidates multiple source files. Upon inspection, many of these source files are pure navigation files (toctree only) with no technical content to extract.

Example:
- `nab-official/v6/nablarch-document/en/application_framework/index.rst` - Only contains toctree
- `nab-official/v6/nablarch-document/en/development_tools/index.rst` - Only contains toctree

## Solution

Introduced `_no_content` flag to explicitly mark entries without extractable technical content.

### Schema Addition

Added two optional fields to mapping entry schema:
- `_no_content` (boolean): Flag indicating file has no technical content
- `_no_content_reason` (string): Brief explanation why target_files is empty

Example:
```json
{
  "id": "v6-0150",
  "source_file": "nab-official/v6/nablarch-document/en/application_framework/index.rst",
  "title": "Application Framework",
  "categories": ["about"],
  "target_files": [],
  "_no_content": true,
  "_no_content_reason": "Navigation only (toctree without technical content)"
}
```

### Decision Rules Added

**Navigation-only file criteria**:
1. File is named `index.rst` or `index.md`
2. Content consists primarily of:
   - `.. toctree::` directive(s)
   - Brief section title
   - No substantial technical explanations, examples, or guidance
3. Any meaningful content (> 3 sentences of explanation) means it's NOT navigation-only

**When NOT navigation-only**:
- index.rst with substantial overview (e.g., "What is Nablarch?" with explanations)
- index.rst with technical guidance or examples

## Files Modified

### 1. mapping-creation-procedure.md

**Section: Mapping Entry Schema**
- Added example with _no_content flag
- Added field descriptions for _no_content and _no_content_reason

**Section: Empty target_files Array**
- Added navigation-only files as valid use case
- Added identification criteria (3-step process)
- Added requirement to set both _no_content flags
- Clarified when NOT to use (index files with substantial content)

**Section: Phase 6 Agent Prompt**
- Updated "Empty Target Files" section with:
  - Navigation-only identification rules
  - Required _no_content field usage
  - 3-sentence threshold guideline

### 2. 06-validate-targets.sh

**Function: check_completeness**
- Added validation for _no_content flag on empty target_files entries
- Reports error if empty target_files without _no_content flag
- Accepts empty entries if < 5% and properly flagged

## Next Steps

1. Review existing mapping-v6.json entries targeting index.json
2. Identify navigation-only source files
3. Update entries:
   - Set `target_files: []`
   - Set `_no_content: true`
   - Set `_no_content_reason: "Navigation only (toctree without technical content)"`
4. For entries with substantial content, use more specific target filenames instead of index.json

## Impact

- Improved clarity: Explicitly marks which files have no content
- Better validation: Script checks for proper flagging
- Cleaner knowledge files: Avoids creating empty or meaningless knowledge files
- Traceability: Reason documented for each no-content decision
