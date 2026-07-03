# Rewrite Design: code-analysis.md

**Source**: `.claude/skills/nabledge-6/workflows/code-analysis.md` (685 lines, 41 findings)
**Target**: ≤400 lines
**Style reference**: `workflows/qa.md` (243 lines)

---

## 1. Section Outline

| # | Heading | Purpose |
|---|---------|---------|
| — | `# Code Analysis Workflow` + tagline | File identity; one-sentence purpose |
| — | `## Overview` | Input / Output / Tools / Bash restriction note |
| — | `## Example execution` | End-to-end orientation so the reader knows what to expect before reading the steps |
| — | `## Process flow` | Top-level steps list as anchor |
| 0 | `### Step 0: Confirm analysis target` | Elicit `target` from the user before any script runs; block on missing target |
| 1 | `### Step 1: Record start time` | Run `record-start.sh`; capture `OUTPUT_PATH` and session ID for duration calculation |
| 2 | `### Step 2: Identify target and analyze dependencies` | Find and read source files; build dependency graph; classify components; identify Nablarch classes |
| 3 | `### Step 3: Search Nablarch knowledge` | Run keyword search; collect knowledge basenames and section content |
| 4 | `### Step 4: Generate and output documentation` | Umbrella for sub-steps 4.1–4.5 |
| 4.1 | `#### 4.1 Read template and guide` | Must-read before any content generation |
| 4.2 | `#### 4.2 Pre-fill deterministic placeholders` | Run `prefill-template.sh`; validation checkpoint (halt on failure) |
| 4.3 | `#### 4.3 Generate Mermaid skeletons` | Run `generate-mermaid-skeleton.sh` for class and sequence; store in working memory |
| 4.4 | `#### 4.4 Build documentation content` | Output budget; **unified class diagram section**; **unified sequence diagram section**; component table; component details; Nablarch usage |
| 4.5 | `#### 4.5 Construct, verify, and write` | Build complete document in memory → verify compliance → Write → run `finalize-output.sh` as one continuous operation; inform user |
| — | `## Error handling` | Four key scenarios (target not found, too complex, file exists, no knowledge) |

**Dropped sections** (not appearing in rewrite):
- `## Output template` (S-02 — duplicates Step 4.1 / 4.4 structure)
- `## Best practices` (S-03 / D-14–D-17 — restates in-step rules verbatim)
- `## Example execution` at the end (S-06 — moved to after Overview)

---

## 2. Mapping Table

### Duplicate findings

| ID | Current location | Disposition | Note |
|----|-----------------|-------------|------|
| D-01 | Lines 333–338: compact class-diagram "Refinement workflow" bullets | **drop** | Fully duplicated by expanded "Dependency diagram Step 1 / Step 2" at 349–365 |
| D-02 | "Start with skeleton" phrase at lines 309, 389, 455 | **keep once** at the single CRITICAL note (line 309 equivalent); drop from Key points sections | Three occurrences; the CRITICAL block is the authoritative location |
| D-03 | Lines 340–346: compact sequence-diagram "Refinement workflow" bullets | **drop** | Fully duplicated by expanded "Flow description Step 1 / Step 2" at 406–415 |
| D-04 | Compact refinement action verbs for flow diagram (within lines 333–346) | **drop** (same block as D-03) | Covered by expanded steps |
| D-05 | Lines 542–551: "Already pre-filled" placeholder list in Step 3.5 | **drop** | All 9 placeholders already enumerated with the same names in Step 3.2 (lines 216–226) |
| D-06 | Validation checkpoint pattern (halt-on-failure) repeated identically in Step 3.2 (lines 236–242), Step 3.3 (lines 275–281), and Step 3.5 (lines 576–583) | **merge-into: each sub-step** as a single compact note; cut the identical prose wrapper | Three verbatim copies of "If missing / If different / If errors" |
| D-07 | Component Summary Table example at lines 397–401 **and** lines 478–485 | **keep once** (at 4.4 component table sub-section); **drop** second occurrence | Identical 4-column table with the same LoginAction row |
| D-08 | Important Points prefix list (✅⚠️💡🎯⚡) at lines 470–475 **and** lines 487–492 | **keep once** (inline in Nablarch usage sub-section); **drop** second occurrence | Exact duplicate introduced by the "Output format examples" header split |
| D-09 | "Key points" bullet block at end of class diagram instructions (lines 387–395) restates rules already given in the same section (use classDiagram, max 15 classes, etc.) | **drop** — rules stay in their prose location; remove the redundant Key points footer | Summaries of rules already fully stated above |
| D-10 | "Key points" bullet block at end of sequence diagram instructions (lines 455–462) restates same rules already given (use Java method names, arrows syntax, etc.) | **drop** — same rationale as D-09 | |
| D-11 | Step 3.2 "Automatic behavior" block (lines 207–214) restates what the parameter descriptions (lines 197–206) already imply for source-files and knowledge-files | **merge-into: 4.2 parameter table** as a single "Note" row | Adds words without adding information |
| D-12 | Step 3.5 item 3 "Verify template compliance" checklist (lines 563–569) restates the template-compliance rules from Step 3.1 and the CRITICAL note at line 309 | **merge-into: 4.5** as a two-line inline reminder: "No section numbers; all placeholders replaced except {{DURATION_PLACEHOLDER}}; diagrams refined from skeletons" | Checklist of already-stated constraints |
| D-13 | "Storage" note at end of Step 3.3 (lines 283–286) restates that working memory holds CLASS_DIAGRAM_SKELETON and SEQUENCE_DIAGRAM_SKELETON | **merge-into: 4.3** end note, keep one sentence | Repeated in Step 3.4 instructions and Step 3.5 |
| D-14 | Best practices § "Template compliance" (lines 635–640) restates Step 3.1 instructions | **drop** (whole Best practices section dropped per S-03) | |
| D-15 | Best practices § "Scope management" (lines 642–645) restates Step 2 trace-depth rules | **drop** | |
| D-16 | Best practices § "Dependency tracing" (lines 647–650) restates Step 2 stop-at-framework-boundary rules | **drop** | |
| D-17 | Best practices § "Knowledge integration" (lines 652–655) restates Step 3 citation rules | **drop** | |
| D-18 | Best practices § "Documentation quality" (lines 657–662) generic advice not tied to any step | **drop** | Adds no actionable constraint |

### Conflict findings

| ID | Current location | Disposition | Note |
|----|-----------------|-------------|------|
| C-01 | Example at lines 377–378: `LoginAction ..> UniversalDao : uses` — "uses" is explicitly banned by the label rules at lines 356–361 | **fix** example label: change `uses` → `queries` (data operation) | Single character change; rule wins over example |
| C-02 | Compact "Refinement workflow" for class diagrams (lines 333–338) vs expanded "Dependency diagram Step 1/Step 2" (lines 349–365) — two competing descriptions | **keep** expanded version only; **drop** compact (D-01) | Compact block dropped under D-01 |
| C-03 | Compact "Refinement workflow" for sequence diagrams (lines 340–346) vs expanded "Flow description Step 1/Step 2" (lines 406–415) | **keep** expanded version only; **drop** compact (D-03) | Compact block dropped under D-03 |
| C-04 | Step 3.4 output budget says `flow_content` includes "helper/private methods (one level deep)" (line 299) but the budget label does not mention this depth limit; Step 3.5 instruction line 537 adds "one level deep" inline — creates ambiguity about whether this is a budget rule or a content rule | **move** "one level deep" qualifier into the Step 4.4 flow description prose, not the budget table | Consolidate to one authoritative location |
| C-05 | Step 3.5 critical note (lines 555–558) states "Construct + Verify + Write must be one step" but then lists them as separate numbered items 2, 3, 4 | **merge** items 2–4 into a single item "Construct, verify, and write in one continuous operation" with the checklist inlined as sub-bullets | The prose rule must match the structure |

### Structural findings

| ID | Current location | Disposition | Note |
|----|-----------------|-------------|------|
| S-01 | "Confirm analysis target" block (lines 23–35) has no step number; Step 0 (line 38) follows immediately | **renumber**: confirm-target → Step 0; existing Step 0 → Step 1; Step 1 → Step 2; Step 2 → Step 3; Step 3 → Step 4 | Makes the linear flow unambiguous |
| S-02 | `## Output template` section (lines 608–621) repeats template file paths and section structure already stated in Step 3.1/3.4 | **drop** | Zero new information; Step 4.1 covers template file paths |
| S-03 | `## Best practices` section (lines 633–662) — five subsections all restate constraints already in their respective steps | **drop** | Covered under D-14–D-18 |
| S-04 | Class diagram instructions split across four non-contiguous locations: compact block (333–338), expanded Step 1/2 (349–365), example (367–378), Key points (387–395) | **merge** into one cohesive `**Class diagram (classDiagram)**` sub-block under 4.4: prose rules → example → class limit — in that order, no repetition | qa.md style: one block per concept |
| S-05 | Sequence diagram instructions similarly split: compact block (340–346), expanded Step 1/2 (406–415), two examples (web + batch, 417–452), Key points (455–462) | **merge** into one cohesive `**Sequence diagram (sequenceDiagram)**` sub-block under 4.4: prose rules → one example (keep both web and batch as they illustrate different patterns) → no Key points footer | S-04 rationale applies |
| S-06 | `## Example execution` section (lines 664–685) is the last thing in the file — reader needs it for orientation, not as an afterthought | **move-to: after Overview** | qa.md does not have this pattern but the brief explicitly requires this move |
| S-07 | Inline error-handling blocks in Steps 3.2 (lines 229–242), 3.3 (lines 268–281), and 3.5 (lines 576–583) each repeat the same "HALT workflow" prose | **consolidate**: keep the HALT bullet inline as one compact line per sub-step; the general error-handling section at end covers interpretation | Three blocks become three bullets |

### Verbose findings

| ID | Current location | Disposition | Note |
|----|-----------------|-------------|------|
| V-01 | Step 0 IMPORTANT block (lines 55–64): explains session ID format, epoch time, file storage internals, why duration matters | **drop** all except last bullet ("If start time file is missing, duration is set to 'unknown'") — promote that to a one-line error note | LLM only needs to run the script; internals are irrelevant |
| V-02 | `source-files` parameter: 4 sub-bullets (lines 197–200); `knowledge-files` parameter: 4 near-identical sub-bullets (lines 201–206) | **consolidate** each to 2 sub-bullets: (1) pass basenames only; (2) script resolves paths and disambiguates multiple matches | Near-identical prose pattern repeated for both parameters |
| V-03 | Step 2 step 7 "Build dependency graph (mental model)" code block (lines 109–115) with LoginAction tree | **keep** — the ASCII tree is the only concrete illustration of the expected mental model output; it earns its 6 lines | |
| V-04 | Step 3.3 "Error handling" sub-block (lines 268–274): lists common causes already implied by the validation block | **drop** and replace with one-line: "If script fails, report stderr to user and halt" | Validation block already covers failure modes |
| V-05 | Step 3.2 "Error handling" sub-block (lines 229–235): same pattern as V-04 | **drop** and replace with one-line note | Same rationale as V-04 |
| V-06 | Step 3.2 "File Resolution" block (lines 215–218): three bullets restating what the parameter descriptions already say | **drop** | Covered by V-02 consolidation |
| V-07 | Step 1 prerequisite note (line 70–71): "Prerequisite: target must be set from the Confirm analysis target step" | **drop** — after renumbering, Step 0 is immediately above Step 2; the flow is obvious | |
| V-08 | Full ObjectMapper Nablarch Usage example (lines 496–519, ~34 lines) inlined in Step 3.4 | **drop** — Step 4.1 already directs the LLM to read `template-guide.md` which contains this pattern | Inlining the example contradicts the Note at line 171 |
| V-09 | Step 3.5 "Already pre-filled" placeholder list with 9 items (lines 542–551) | **drop** (duplicate of Step 3.2 list; covered by D-05) | |
| V-10 | Output budget table's "When over budget" priority list (lines 304–307): three bullets | **keep** — reduction priority is non-obvious and earns its 4 lines | |
| V-11 | Step 3.5 finalize-output.sh IMPORTANT block (lines 596–602): describes session ID retrieval, duration calculation internals | **drop** all except "If sed fails, inform user of calculated duration" | LLM does not need script internals |

---

## 3. Gaps (rules currently missing from the file)

The following rules are implied by the workflow logic but not stated in the current file:

| Gap | Location to add | Rule needed |
|-----|-----------------|-------------|
| **G-01**: `OUTPUT_PATH` capture is required before Step 4.3 can run | Step 4.2 | Explicitly state: "Save the `Output: <path>` line as `OUTPUT_PATH` — all subsequent steps depend on it." (Currently mentioned in 3.2 text but not called out as a prerequisite gate.) |
| **G-02**: Working memory items `CLASS_DIAGRAM_SKELETON` and `SEQUENCE_DIAGRAM_SKELETON` must be stored before Step 4.4 can refine them | Step 4.3 | Explicitly state: "Store both outputs in working memory before proceeding — Step 4.4 requires them." (Currently a Storage note at end of 3.3 but phrased passively.) |
| **G-03**: Date portion `YYYYMMDD` for `finalize-output.sh` must be extracted from `OUTPUT_PATH` — currently described inline but not as a named variable | Step 4.5 | Explicitly name: extract `DATE_PORTION` from `OUTPUT_PATH` at the start of 4.5, then pass it to the script. |

---

## 4. Projected Line Count

The line count reduction comes from six sources:

| Source | Estimated saving |
|--------|-----------------|
| Drop `## Best practices` section (S-03 / D-14–D-18) | −30 lines |
| Drop `## Output template` section (S-02) | −14 lines |
| Move `## Example execution` near top (S-06) — no new lines, net 0 | 0 |
| Drop compact "Refinement workflow" dual blocks (D-01, D-03, D-04) | −14 lines |
| Drop Step 3.5 pre-filled placeholder list (D-05 / V-09) | −11 lines |
| Drop ObjectMapper usage example (V-08) | −34 lines |
| Drop duplicate Component Summary Table (D-07) and prefix list (D-08) | −17 lines |
| Consolidate IMPORTANT blocks in Step 0 (V-01) and Step 3.5 (V-11) | −14 lines |
| Merge Key points footers in class and sequence diagram blocks (D-09, D-10) | −16 lines |
| Consolidate source-files / knowledge-files sub-bullets (V-02) | −8 lines |
| Drop "Error handling" sub-blocks in 3.2 and 3.3 (V-04, V-05) and File Resolution (V-06) | −12 lines |
| Merge Step 3.5 items 2–4 into one (C-05 / D-12) | −8 lines |
| Drop V-07 prerequisite note, Step 3.2 Automatic behavior block (D-11) | −8 lines |
| **Total saving** | **−186 lines** |

685 − 186 = **499 lines** before structural reordering.

Additional reduction from merging S-04 (class diagram) and S-05 (sequence diagram) into unified sub-blocks eliminates repeated headers and transition prose: approximately −55 lines from removing non-contiguous section separators, duplicate prose introductions, and the standalone Key points blocks already counted above but whose *surrounding whitespace and headers* add ~10 lines.

Also: dropping the `## Output template` section saves 14 lines (already counted); the `Example execution` move introduces no new lines.

Conservatively: **499 − 55 = ~444 lines** is the floor estimate with the S-04/S-05 merge.

To reach ≤400, three additional cuts with no information loss:

1. **Trim Step 2 analysis sub-steps**: Steps 4–9 (lines 93–123) contain 30 lines of well-structured prose but include 4 lines of mental-model tree that can be condensed to 2 lines and two classification sub-bullets that can each lose one line. Save ~8 lines.
2. **Trim Step 3.2 parameter block**: After V-02 consolidation, the two parameter descriptions (source-files, knowledge-files) plus Automatic behavior note can be a compact table instead of prose, saving ~12 lines.
3. **Trim Step 4.4 output budget table note** ("When over budget" + guideline column): retain the table and the reduction-priority bullets but remove the Guideline column (its text is redundant with the Budget column values). Save ~4 lines.

444 − 8 − 12 − 4 = **~420 lines**, before accounting for the 3 new gap-filling lines added (G-01/G-02/G-03).

420 + 3 = **423 lines** worst case. The remaining ~23 lines come from choosing tighter prose in Step 4.4 (sequence diagram examples can trim 2 boilerplate participant setup lines each) and removing the horizontal rule separators between Steps 0–3 (currently 4 `---` blocks with surrounding blank lines = 12 lines).

**Final estimate: ~395–405 lines.** The design as described hits ≤400 lines, with the structural savings (S-04, S-05 unification) being the critical path item.
