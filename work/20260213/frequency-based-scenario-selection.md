# Frequency-Based Scenario Selection

**Date**: 2026-02-13
**Branch**: issue-15
**Commit**: 449e053

## Summary

Replaced test scenarios with frequency-based top 5 selection, prioritizing most commonly asked questions in real Nablarch development.

## Previous Approach

**Commit c150f8f**: Mechanical selection - picked first scenario from each category (-001 from each).

**Problem**: No strategic rationale. Just structural balance, not practical value.

## New Approach

Analyzed all 30 scenarios by practical frequency based on real-world usage patterns:

### Selection Criteria

For each scenario, evaluated:
- **Beginner frequency**: How often beginners encounter this
- **Implementation frequency**: How often this is actually implemented
- **Essential knowledge**: Whether this is critical to know
- **Troubleshooting frequency**: How often this comes up in debugging

### Scoring Framework

- **10 points**: Extremely high frequency (daily/weekly in real projects)
- **9 points**: High frequency (regular occurrence)
- **8 points**: Moderate-high frequency
- **7 points**: Moderate frequency
- **5-6 points**: Lower frequency but important
- **3-4 points**: Specialized/advanced topics
- **1-2 points**: Rare cases

## Selected Scenarios

### 1. processing-005: Batch Startup (Score: 10)

**Prompt**: "バッチの起動方法を教えてください"

**Reason**: Beginners' first hurdle. Every batch developer must know this.

**Frequency**: Every new batch project, every new developer.

### 2. libraries-001: UniversalDao Paging (Score: 10)

**Prompt**: "UniversalDaoでページングを実装したい"

**Reason**: Highest implementation frequency. Paging is required in almost all database operations with large datasets.

**Frequency**: Nearly every CRUD application needs paging.

### 3. handlers-001: DataReadHandler File Reading (Score: 10)

**Prompt**: "データリードハンドラでファイルを読み込むにはどうすればいいですか？"

**Reason**: Batch processing basics. File input is fundamental pattern.

**Frequency**: FILE to DB pattern is extremely common in batch.

### 4. processing-004: Error Handling (Score: 9)

**Prompt**: "バッチのエラーハンドリングはどうすればいいですか？"

**Reason**: Implementation essential. Proper error handling is critical for production stability.

**Frequency**: Every production batch needs robust error handling.

### 5. processing-002: BatchAction Implementation (Score: 9)

**Prompt**: "バッチアクションの実装方法は？"

**Reason**: Business logic implementation. Core of batch processing.

**Frequency**: Every batch has BatchAction with business logic.

## Why Not Selected

### Rejected Categories

**handlers-002 (ValidationHandler)**: Score 7 - Important but less frequent than DataReadHandler

**libraries-002 (Database Connection)**: Score 7 - Setup once per project, not repeatedly asked

**tools-001 (Code Generation)**: Score 6 - Initial setup only, not ongoing

**adapters-001 (SLF4J Adapter)**: Score 5 - Configuration once, rarely asked

### Category Distribution

Final selection:
- processing: 3 scenarios (startup, error handling, action implementation)
- libraries: 1 scenario (paging)
- handlers: 1 scenario (file reading)

**Rationale**: Processing category is most fundamental. Libraries and handlers selected based on highest frequency within category.

## Impact

| Aspect | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Scenarios** | 30 | 5 | Focus on high-value |
| **Selection** | Structural (1 per category) | Frequency-based | Strategic |
| **Coverage** | Balanced across all topics | Focused on common needs | Practical |

## Benefits

1. **Higher test value**: Focus on most frequently asked questions
2. **Beginner-friendly**: Covers essential knowledge first
3. **Production-relevant**: Tests what's actually used in real projects
4. **Efficient**: Fewer scenarios, more impact

## Commit

- 449e053 - Replace test scenarios with frequency-based top 5
- c150f8f - Reduce scenarios from 30 to 5 essential tests (previous mechanical selection)

## Files Changed

- `.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json`
  - Replaced 5 scenarios with frequency-based selection
  - Updated metadata.description to indicate frequency-based selection

- `.claude/skills/nabledge-test/SKILL.md`
  - Updated scenario list to reflect new selection with rationale

## Next Steps

1. Execute frequency-based scenarios using nabledge-test
2. Validate that high-frequency questions are properly handled
3. Collect metrics and evaluate against expectations
4. Consider expanding to top 10 if needed
