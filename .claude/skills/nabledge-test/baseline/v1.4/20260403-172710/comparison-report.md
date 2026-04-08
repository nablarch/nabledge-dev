# Comparison Report: v1.4 ca-002 Baseline

**Previous Baseline**: 20260331-160735  
**Current Baseline**: 20260403-172710  
**Reason**: Applied corrected grading logic that reads from output files (code-analysis-*.md) instead of response.md only

## Detection Rate Summary

| Baseline | Detected | Total | Rate | Change |
|----------|----------|-------|------|--------|
| Previous | 23 | 34 | 67.6% | - |
| Current | 27 | 34 | 79.4% | +11.8% ⬆️ |

**Δ Detection**: +4 items detected

## Changes

### Improvements

**+4 detection items now detected**:
- ✅ Nablarch Framework Usage includes 'FileBatchAction'
- ✅ Nablarch Framework Usage includes 'ValidatableFileDataReader'
- ✅ Nablarch Framework Usage includes 'BusinessDateUtil'
- ✅ Nablarch Framework Usage includes 'ParameterizedSqlPStatement'

### Root Cause Analysis

The improvement from 67.6% to 79.4% (+11.8pp) is due to corrected grading logic:

**Previous Logic (Incorrect)**:
- Checked only `response.md` file
- Did not examine actual structured output files (`code-analysis-*.md`)
- Missed many components that were written to output files by the agent

**Current Logic (Correct)**:
- Reads all `.md` files from output directory
- For section-based checks (Class Diagram, Nablarch Usage, etc.), extracts relevant sections
- Properly identifies heading-based components (### ComponentName)
- Detects components in diagrams and structured content

**Items Now Correctly Detected**:
- Class diagram classes and relationships (detected in mermaid classDiagram block)
- Nablarch Framework Usage sections with independent headings (### FileBatchAction, ### ValidatableFileDataReader, etc.)
- Components properly written to structured output files

## Detailed Detection Comparison

### Previously Undetected (Now Detected)

| Item | Section | Evidence |
|------|---------|----------|
| FileBatchAction | Class Diagram | Found in mermaid classDiagram |
| FileLayoutValidatorAction | Class Diagram | Found in mermaid classDiagram |
| UserInfoTempEntity | Class Diagram | Found in mermaid classDiagram |
| ValidatableFileDataReader | Class Diagram | Found in mermaid classDiagram |
| Relationship | Class Diagram | B11AC014Action --|> FileBatchAction found |
| FileBatchAction | Nablarch Framework Usage | Found as ### heading |
| ValidatableFileDataReader | Nablarch Framework Usage | Found as ### heading |
| BusinessDateUtil | Nablarch Framework Usage | Found as ### heading |
| ParameterizedSqlPStatement | Nablarch Framework Usage | Found as ### heading |

## Still Not Detected

- Overview: ValidatableFileDataReader, BusinessDateUtil, UserInfoTempEntity (not in overview section, only in Architecture/Components)
- Processing Flow: getValidatorAction (method not explicitly mentioned in flow steps)
- Sequence Diagram: UserInfoTempEntity (participant not in diagram), getValidatorAction (method call not shown)
- Nablarch Usage: TransactionAbnormalEnd (discussed but no independent heading)

## Conclusion

The corrected grading logic now accurately reflects what the skill generates. The 79.4% detection rate represents the actual capability of nabledge-1.4 code-analysis for this scenario, with proper section-based extraction from structured output files.

This correction enables:
1. **Accurate measurement**: Detection rates now match actual output quality
2. **Proper comparison**: Future improvements can be measured against correct baseline
3. **Bug validation**: Confirms the grading logic matches the SKILL.md specification
