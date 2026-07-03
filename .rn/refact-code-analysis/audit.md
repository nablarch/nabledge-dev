# Audit — code-analysis.md (685 lines)

**File**: `.claude/skills/nabledge-6/workflows/code-analysis.md`  
**Date**: 2026-07-03  
**Total findings**: 41

## Category counts

| Category | Count |
|----------|-------|
| Duplicate | 18 |
| Conflict | 5 |
| Structural | 7 |
| Verbose | 11 |

---

## Duplicate (D) — same instruction stated ≥2 times

**D-01** Lines 312–329 vs 333–346  
Refinement "Permitted actions" / "Prohibited actions" and the compact "For class diagrams / For sequence diagrams" bullets cover exactly the same refinement policy. Same content stated twice in adjacent blocks.

**D-02** Lines 310, 389, 405  
"Start with skeleton (reduces generation time)" / "Retrieve skeleton from working memory" stated 3× across Step 3.4 sub-sections (compact refinement block, class diagram key-points, sequence diagram key-points).

**D-03** Lines 333–337 vs 349–366  
Compact "For class diagrams" workflow (5 bullets) and expanded "Dependency diagram Step 1/Step 2" block describe identical class diagram refinement actions. Fully redundant.

**D-04** Lines 340–346 vs 404–414  
Compact "For sequence diagrams" workflow and expanded "Flow description Step 1/Step 2" describe identical sequence diagram refinement actions. Fully redundant.

**D-05** Lines 535–551 vs 215–226  
Step 3.5 lists all 9 pre-filled placeholders in a "Already pre-filled (keep as-is)" block; Step 3.2 already enumerates the same 9 with descriptions. The Step 3.5 list adds nothing.

**D-06** Lines 367–378 vs 480–485  
Class diagram example (LoginAction/LoginForm/UniversalDao) appears in "Dependency diagram" sub-section and again in "Output format examples / Component Summary Table" area. Same mermaid block shown twice.

**D-07** Lines 396–401 vs 478–484  
Component Summary Table format shown with example in Step 3.4 main area (lines 396–401) and repeated in "Output format examples" block (lines 478–484). Identical content.

**D-08** Lines 469–474 vs 486–493  
"Nablarch usage" bullet list (Class name, Code example, Important points, etc.) and "Important Points prefixes" block both enumerate the ✅⚠️💡🎯⚡ prefixes. Stated twice in the same section.

**D-09** Lines 320, 343, 411  
"Add error handling branches using `alt`/`else` blocks" instruction appears in Permitted actions, compact sequence workflow, and expanded sequence workflow.

**D-10** Lines 321, 344, 412  
"Add loops for repetitive operations using `loop` blocks" appears in Permitted actions, compact sequence workflow, and expanded sequence workflow.

**D-11** Lines 322, 345, 413  
"Add explanatory notes using `Note over` syntax" appears in Permitted actions, compact sequence workflow, and expanded sequence workflow.

**D-12** Lines 455–462 vs 312–329  
"Key points" block for sequence diagrams re-lists skeleton retrieval + method name guidance that already appears in the expanded refinement block above it.

**D-13** Lines 380–394 vs 355–366  
"Key points" block for class diagram re-lists `classDiagram` syntax, `<<Nablarch>>` marking, and class limit — all already covered in the Step 2 refinement block above.

**D-14** Lines 633–640 vs 160–178 (Step 3.1)  
"Best practices / Template compliance" section restates: read template first, no section numbers, no extra sections, verify compliance. All are already stated in-step (Step 3.1 and Step 3.5 verify list).

**D-15** Lines 641–644 vs 103–106 (Step 1.6)  
"Best practices / Scope management" restates stop-at-framework-boundaries and ask-user-before-expanding, already stated in Step 1.

**D-16** Lines 645–649 vs 103–106 (Step 1.5–1.6)  
"Best practices / Dependency tracing" restates stop at framework boundaries and Entity classes, already in Step 1.

**D-17** Lines 650–654 vs 143–153 (Step 2.3)  
"Best practices / Knowledge integration" restates knowledge-files-only and cite-sources rules, already in Step 2.

**D-18** Lines 229–233 vs 235–242  
Step 3.2 "Error handling" block and "Validation" block both address the case where the script fails / produces wrong output. Partial overlap of error scenarios.

---

## Conflict (C) — two instructions contradict each other

**C-01** Lines 357–362 vs 370 (example)  
Rules say avoid generic labels "uses", "calls", "has". The example at line 370 uses `LoginAction ..> UniversalDao : uses`. Rule and example contradict.

**C-02** Lines 333–337 vs 349–366  
Compact "For class diagrams" bullets and expanded "Dependency diagram Step 1/Step 2" are both presented as the authoritative class diagram refinement procedure. Reader cannot know which governs.

**C-03** Lines 340–346 vs 404–414  
Same conflict for sequence diagrams: compact and expanded workflows both claim to be authoritative.

**C-04** Lines 309 vs 323  
Line 309: "CRITICAL: All diagram work REFINES skeletons from Step 3.3." Line 323 prohibited action: "Delete skeleton and create new diagram from scratch." But lines 329: "Exception: If skeleton is malformed, report error and request manual intervention." Conflict: what to do if skeleton is bad is unclear (request manual intervention ≠ any stated action path).

**C-05** Lines 556–558 vs 560–569  
Step 3.5 item 2 says "Construct, Verify, Write must be a single step — DO NOT split Build and Write". Item 3 is "Verify template compliance before writing" as a separate, listed item. This contradicts the single-step mandate by presenting verification as a separable step.

---

## Structural (S) — misplaced rules, no clear entry point, obscured structure

**S-01** Lines 22–35 (before Step 0)  
"Confirm analysis target" is an unnumbered step positioned before Step 0. It is effectively Step -1 but has no step number. A reader scanning step numbers misses it. Should be Step 0 or Step 1 with Step 0 renumbered.

**S-02** Lines 608–621 ("Output template" section)  
This section summarizes the template structure (7 bullet points). Step 3.1 already says "Read template file" and Step 3.4 inlines the examples. The section adds a 7-item list that duplicates Step 3.4's structure summary. Orphaned after the main process flow.

**S-03** Lines 633–661 ("Best practices" section)  
All 4 sub-sections restate rules already embedded in steps (see D-14 through D-17). The section provides no information not already in the steps; it exists only as a summary, but summaries at the end of workflow files invite the AI to skip the steps and read only the summary.

**S-04** Lines 309–474 (Step 3.4 diagram instructions)  
Class diagram instructions are split across: (a) compact refinement workflow, (b) permitted/prohibited actions, (c) "Dependency diagram Step 1/Step 2" expanded block, (d) "Key points" block. A reader trying to understand class diagram rules must synthesize 4 non-contiguous sub-blocks.

**S-05** Lines 525–606 (Step 3.5)  
The step has 5 numbered items but items 2–4 are described as a single operation ("Build and Write must be single step"). The numbering implies separability that the instructions then contradict.

**S-06** Lines 663–685 ("Example execution" section)  
The example re-narrates the steps at a high level. Useful as orientation but currently placed after "Best practices", making it the last thing in the file. As a reader orientation aid it belongs near the top (e.g., after the Overview).

**S-07** Lines 88–91 (Step 1 Output line)  
Step 1's Output sentence ("Target files list, dependency graph...") is listed as the last item under Step 1 but uses the same bullet style as the numbered sub-steps, making it visually indistinguishable from a sub-step.

---

## Verbose (V) — reducible without loss

**V-01** Lines 55–63 (Step 0 IMPORTANT block)  
Explains internal file-naming conventions (`.nabledge-code-analysis-id`, `UNIQUE_ID format`, epoch time) that are script internals. The LLM only needs to run the script; internal file naming is irrelevant to workflow execution.

**V-02** Lines 193–205 (Step 3.2 parameter bullets)  
`source-files` and `knowledge-files` each have 4 nearly identical sub-bullets ("Pass basenames only", "Script searches", "If multiple found", "Script handles"). The sub-bullets are a policy note that applies to both; stating it once at the parameter block level would suffice.

**V-03** Lines 207–214 (Step 3.2 "Automatic behavior")  
Describes what the script does automatically (output path, official docs). These are useful one-liners but are expanded into a block with headers and sub-bullets that adds length without adding clarity.

**V-04** Lines 215–226 (Step 3.2 "Pre-filled placeholders 9/17")  
Enumerating all 9 placeholder descriptions here is redundant with the template-guide which already defines them, and with the Step 3.5 list.

**V-05** Lines 259–273 (Step 3.3 Error handling + Validation)  
Script-level error-handling instructions (check stderr, common causes, verify parse errors) repeat the same pattern as Step 3.2's error-handling block. A single shared error-handling policy statement would be shorter.

**V-06** Lines 283–286 (Step 3.3 Storage)  
"Store class diagram output as CLASS_DIAGRAM_SKELETON in working memory... You will retrieve these skeletons in the following steps." The last sentence is obvious given that the next sections reference these variables.

**V-07** Lines 292–307 (Step 3.4 output budget table)  
Budget guideline table is useful, but the "When over budget" bullet block below it restates the same priority logic verbally. Either the table or the prose is sufficient.

**V-08** Lines 486–519 (Output format examples)  
The full Nablarch Usage structure example (ObjectMapper) occupies 34 lines. The template-guide already contains this example. Inlining the full example here duplicates the template-guide.

**V-09** Lines 541–551 (Step 3.5 "Already pre-filled" block)  
Lists 9 already-filled placeholders with descriptions. The reader just ran Step 3.2 which filled them; this list is a reminder that adds 11 lines without adding information.

**V-10** Lines 576–583 (Step 3.5 Validation checkpoint)  
File-size heuristic ("<5 KB likely missing content, >100 KB possible duplicate") is not actionable — the LLM cannot measure file size before writing. Remove or replace with a meaningful post-write check.

**V-11** Lines 596–601 (Step 3.5 Step 5 IMPORTANT block)  
Explains that finalize-output.sh "handles: session ID retrieval, duration calculation, and file update" — script internals not needed for correct invocation. The error-handling sub-point is worth keeping; the internal description is not.

---

## Estimated line savings

| Action | Savings (approx.) |
|--------|------------------|
| Remove compact refinement workflow (D-01, D-02, D-03, D-04) | ~35 lines |
| Remove "Output template" section (S-02) | ~14 lines |
| Remove "Best practices" section (D-14–D-17, S-03) | ~30 lines |
| Compress Step 3.5 placeholder block (D-05, V-09) | ~20 lines |
| Remove Step 3.2 sub-bullet redundancy (V-02, V-04) | ~18 lines |
| Remove Nablarch Usage inline example (V-08) | ~30 lines |
| Remove script-internal IMPORTANT blocks (V-01, V-11) | ~12 lines |
| Merge error-handling blocks (V-05) | ~10 lines |
| Remove "Example execution" or move to Overview (S-06) | ~23 lines |
| Fix conflicts (C-01 example fix, C-05 step renumber) | ~5 lines |
| Other verbose reductions (V-03, V-06, V-07, V-10) | ~15 lines |
| **Total** | **~212 lines** |

**Projected result**: 685 − 212 ≈ **473 lines** (before prose tightening)  
With prose tightening across remaining sections: **~390–410 lines** — within ≤400 target.
