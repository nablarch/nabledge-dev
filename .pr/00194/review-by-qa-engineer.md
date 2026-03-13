# Expert Review: QA Engineer

**Date**: 2026-03-13
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 1 file (+ 2 source files for verification)

## Overall Assessment

**Rating**: 4/5
**Summary**: The nabledge-5 scenarios.json is well-structured and correctly adapts v5-specific source paths and nablarch_usage entries against the actual v5 source code. The main weakness is that all 5 QA scenarios are identical to nabledge-6, missing the opportunity to validate nabledge-5-specific knowledge, and there is one inherited inconsistency in nablarch_usage classification across CA scenarios.

## Key Issues

### High Priority

None

### Medium Priority

1. **QA scenarios are 100% identical to nabledge-6 — no nabledge-5-specific coverage**
   - Description: All 5 QA scenarios (qa-001 through qa-005) have the same question and expectations as nabledge-6. Nablarch 5 has meaningful differences from Nablarch 6 (Java EE 7 vs Jakarta EE 10, CDI differences, legacy web framework patterns, distinct annotation sets). None of these are tested.
   - Suggestion: Replace at least 1-2 QA scenarios with nabledge-5-specific topics in a future PR.
   - Decision: Defer to Future
   - Reasoning: Changing scenarios.json would invalidate the just-saved baseline data (detection counts would shift, making benchmark comparison invalid). Address in a future baseline re-run PR.

2. **Inconsistent `BeanUtil` in `nablarch_usage` across CA scenarios (ca-004 lacks it, ca-005 has it)**
   - Description: `ca-005` lists `BeanUtil` in `nablarch_usage`, but `ca-004` does not — despite both actions using `BeanUtil` equivalently in their Java source code. Inherited from nabledge-6.
   - Suggestion: Normalize by either adding BeanUtil to ca-004's nablarch_usage or removing from ca-005.
   - Decision: Defer to Future
   - Reasoning: Same baseline-invalidation constraint as above.

3. **No CA scenario covers nabledge-5 batch-specific classes**
   - Description: All 5 CA scenarios target web actions or the same batch action as nabledge-6 (`ExportProjectsInPeriodAction`). No CA scenario exercises nabledge-5-specific batch knowledge.
   - Suggestion: Add a CA scenario for a batch action unique to Nablarch 5 in a future PR.
   - Decision: Defer to Future
   - Reasoning: Adding scenarios requires scenarios.json changes; same baseline-invalidation risk.

### Low Priority

1. **`ca-003` sequence_diagram messages missing `listProject`**
   - Description: v6's ca-003 includes `findAllBySqlFile` in messages; v5's correctly drops it (v5 delegates through `ProjectService.listProject()`) but doesn't add `listProject` as a replacement message.
   - Suggestion: Add `listProject` to ca-003 sequence_diagram messages.
   - Decision: Defer to Future (baseline-breaking change)

2. **`per` and `page` as standalone expectations in qa-002 are fragile**
   - Description: Very short strings that could match incidentally in any response.
   - Decision: Defer to Future (inherited from v6, acceptable known limitation)

3. **ca-004 overview method name inconsistency vs ca-005**
   - Description: ca-005 overview includes method names (`confirmUpdate`, `update`); ca-004 does not. Minor style inconsistency inherited from v6.
   - Decision: Reject (inherited intentional design difference)

## Positive Aspects

- `target_file` paths are correctly adapted from `v6/` to `v5/` across all CA scenarios.
- `nablarch_usage` for ca-004 correctly omits `UniversalDao` (present in nabledge-6 but absent in the actual v5 `ProjectCreateAction.java`).
- `nablarch_usage` for ca-005 correctly substitutes `InjectForm` for `UniversalDao` compared to nabledge-6, reflecting the actual v5 source.
- Benchmark scenario selection is well-reasoned: qa-001 (55% mean) as weakness probe, qa-003 (95.7%) as stability probe, ca-004/ca-005 as CRUD operation benchmarks.
- `ca-003` sequence_diagram accurately drops `findAllBySqlFile` from messages, correctly reflecting that v5's `ProjectSearchAction` delegates through `ProjectService` rather than calling DAO directly.
- Metadata block is complete and accurate (`total_scenarios: 10`, correct `by_type` counts).
- JSON structure is valid and consistent with the nabledge-6 schema throughout.

## Recommendations

1. Introduce nabledge-5-specific QA scenarios in a future PR (e.g., Nablarch 5 form validation annotations, JSP tag library usage).
2. Normalize `BeanUtil` in `nablarch_usage` across ca-004 and ca-005 in the same future PR (when baseline will be re-run anyway).
3. Document intentional differences from nabledge-6 (UniversalDao omissions, findAllBySqlFile removal) in a companion notes file.

## Files Reviewed

- `.claude/skills/nabledge-test/scenarios/nabledge-5/scenarios.json` (test definitions)
- `.claude/skills/nabledge-test/scenarios/nabledge-6/scenarios.json` (reference for consistency check)
- `.lw/nab-official/v5/.../ProjectCreateAction.java` (source truth for ca-004)
- `.lw/nab-official/v5/.../ProjectUpdateAction.java` (source truth for ca-005)
- `.lw/nab-official/v5/.../ProjectSearchAction.java` (source truth for ca-003)
