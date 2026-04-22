# Prompt Engineer Design: Faceted Search Flow

**Date**: 2026-04-22
**Reviewer**: AI Agent as Prompt Engineer
**Target**: End-to-end redesign of nabledge-6 knowledge search (replaces BM25 keyword flow)
**Rating**: N/A (design, not a review of existing artifact)

---

## 0. Architecture at a glance

```
question
  │
  ▼
┌──────────────────────────────┐
│ AI-1  facet-extract          │   Claude (cheap), schema-constrained JSON
│   in:  question + axis values│   no tools, stdin prompt
│   out: {type[], category[],  │
│        processing_patterns[],│
│        coverage}             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ MECH  facet-filter.py        │   deterministic, unit-testable,
│   in:  facets + index.toon   │   no LLM, no network
│   out: candidate_paths[]     │
└──────────────┬───────────────┘
               │   (short-circuit if coverage=out_of_scope OR
               │    candidate_paths == [] after fallback)
               ▼
┌──────────────────────────────┐
│ AI-2  section-select         │   Claude (cheap), schema-constrained JSON
│   in:  question + rows       │
│        (title, hints only)   │
│   out: section_refs[]        │
└──────────────┬───────────────┘
               ▼
        read-sections.sh → answer prompt
```

No stage calls `keyword-search.sh`. BM25 remains only as a standalone public entry point
(renamed from `full-text-search.sh` per #307) for debugging and user-authored ad-hoc search.

---

## D1. AI-1 facet-extraction prompt + JSON schema

### D1.1 File location

`.claude/skills/nabledge-6/workflows/_knowledge-search/_facet-extract.md`

### D1.2 Full prompt text

```markdown
# Facet Extraction

Map the user's question to discrete facet values on three axes that index the
Nablarch-6 knowledge base. Output ONLY the JSON defined by the schema — no tools,
no prose, no markdown.

## Context

The knowledge base is indexed by three axes. You MUST select values only from the
enumerated lists below. Any value not in the list is invalid.

### Axis: type (pick 0-3)
- about                — concept, philosophy, release notes, migration
- check                — security checklist
- component            — concrete framework pieces: handlers, libraries, adapters
- development-tools    — testing framework, toolbox, static analysis
- guide                — business samples, tutorials
- processing-pattern   — end-to-end style guides per processing pattern
- releases             — release notes (Nablarch 6.x)
- setup                — blank project, configuration, setting-guide, cloud-native

### Axis: category (pick 0-4)
about-nablarch, adapters, biz-samples, blank-project, cloud-native, configuration,
db-messaging, handlers, http-messaging, jakarta-batch, java-static-analysis,
libraries, migration, mom-messaging, nablarch-batch, nablarch-patterns,
release-notes, releases, restful-web-service, security-check, setting-guide,
testing-framework, toolbox, web-application

### Axis: processing_patterns (pick 0-3)
nablarch-batch, jakarta-batch, restful-web-service, http-messaging,
web-application, mom-messaging, db-messaging

Leave this axis as [] if the question is not specific to a processing pattern
(e.g., cross-cutting concerns like validation, logging, transactions).
About 225 of 295 files have no processing_patterns; filtering on this axis
is OPT-IN, not default.

## Coverage

Set `coverage` to one of:

- `in_scope`       — a Nablarch question the knowledge base is likely to cover
- `uncertain`      — Nablarch-related but the feature may not be built in
- `out_of_scope`   — not a Nablarch question (e.g., general Java, non-Nablarch
                     product, pure infrastructure question)

If coverage is `out_of_scope`, still emit plausible facets (do not leave empty) so
downstream code can log why nothing matched — but the downstream filter will
short-circuit.

## Selection rules

- Under-specify over over-specify. If the user says "バリデーション" without naming
  a processing pattern, return `processing_patterns: []`, NOT every pattern.
- Prefer `component` + a concrete category over `processing-pattern` when the
  user names a concrete mechanism (e.g., ハンドラ, Bean Validation, UniversalDao).
- Include `processing-pattern` as a type only when the user asks "how do I build
  a ___" (a pattern entry-point question).
- Never invent axis values. If no value fits, leave that axis empty.

## Examples

Question: "ユーザーが入力する画面項目のチェックを Nablarch 流で書きたい"
→ { "type": ["component","processing-pattern"],
    "category": ["libraries","web-application"],
    "processing_patterns": ["web-application"],
    "coverage": "in_scope" }

Question: "REST API のレート制限は Nablarch にある？"
→ { "type": ["component","processing-pattern"],
    "category": ["handlers","restful-web-service"],
    "processing_patterns": ["restful-web-service"],
    "coverage": "uncertain" }

Question: "Spring Boot の設定ファイルはどこに置く？"
→ { "type": [], "category": [], "processing_patterns": [],
    "coverage": "out_of_scope" }

## Question

{{question}}
```

### D1.3 JSON schema

```json
{
  "type": "object",
  "required": ["type", "category", "processing_patterns", "coverage"],
  "additionalProperties": false,
  "properties": {
    "type": {
      "type": "array", "maxItems": 3, "uniqueItems": true,
      "items": {"enum": ["about","check","component","development-tools",
                         "guide","processing-pattern","releases","setup"]}
    },
    "category": {
      "type": "array", "maxItems": 4, "uniqueItems": true,
      "items": {"enum": ["about-nablarch","adapters","biz-samples","blank-project",
        "cloud-native","configuration","db-messaging","handlers","http-messaging",
        "jakarta-batch","java-static-analysis","libraries","migration",
        "mom-messaging","nablarch-batch","nablarch-patterns","release-notes",
        "releases","restful-web-service","security-check","setting-guide",
        "testing-framework","toolbox","web-application"]}
    },
    "processing_patterns": {
      "type": "array", "maxItems": 3, "uniqueItems": true,
      "items": {"enum": ["nablarch-batch","jakarta-batch","restful-web-service",
                         "http-messaging","web-application","mom-messaging",
                         "db-messaging"]}
    },
    "coverage": {"enum": ["in_scope","uncertain","out_of_scope"]}
  }
}
```

### D1.4 Field-bound rationale

- `type` max 3 of 8: a real question never spans more than ~3 types. Cap prevents
  the "all 8" degenerate answer.
- `category` max 4 of 24: cross-cutting questions (impact-01: transactions spans
  handlers + libraries; review-01: batch spans nablarch-batch + libraries +
  handlers + blank-project) need >2 but never all 24.
- `processing_patterns` max 3 of 7: same logic.
- All three arrays default to `[]` (valid). An empty axis = "no constraint" for
  the mechanical filter. This is how cross-cutting questions stay correct.

---

## D2. Mechanical filter

### D2.1 File and language choice

`.claude/skills/nabledge-6/scripts/facet-filter.py` — **Python, not bash**.

**Why Python over bash**:
- index.toon parsing (comma-separated but values may contain commas in titles; the
  generator already escapes title commas to 、 but we should not trust that forever)
- Set intersection / candidate counting with deterministic output ordering
- Unit-testable via pytest
- No new dependency — the repo already uses Python everywhere (tools/benchmark,
  tools/knowledge-creator)
- Bash + jq/awk would reimplement the same logic less safely

### D2.2 Interface

```
facet-filter.py \
  --type component processing-pattern \
  --category libraries web-application \
  --processing-patterns web-application \
  [--max-return 60] [--min-expand 3]

stdout: JSON { "candidate_paths": [...], "total": N, "fallback_applied": "none|type-only|all" }
exit 0 on success, 2 on invalid axis value
```

### D2.3 Logic

```
1. Load .claude/skills/nabledge-6/knowledge/index.toon once.
2. Parse files[N,]{title,type,category,processing_patterns,path} rows.
   Skip rows where path == "not yet created".
3. For each non-empty axis, filter rows where row.axis ∈ requested_values.
   - processing_patterns: row value is space-separated; pattern matches if the
     requested value appears as one of the tokens. EMPTY row value NEVER matches
     a requested pattern. If the axis is requested and the row has empty
     processing_patterns, the row is excluded.
4. Empty axis in the request = no filter on that axis (pass through).
5. Apply AND across axes.
6. Count candidates.
7. Fallback ladder:
   - If count == 0 and processing_patterns was non-empty:
       Retry without processing_patterns. fallback_applied="drop-pp".
   - If count == 0 and category was non-empty (pp already empty or dropped):
       Retry with type only. fallback_applied="type-only".
   - If count == 0 and type was non-empty:
       Return empty, fallback_applied="none-possible".
   - If count > max_return (default 60):
       Drop processing_patterns first, then category, until count ≤ max_return.
       If still over, keep top max_return by path lexical order and set
       fallback_applied="truncated".
   - If count < min_expand (default 3) and fallback_applied == "none":
       Keep result (small is valid; do not expand speculatively).
8. Output sorted by path (deterministic).
```

### D2.4 Justified thresholds

| Threshold | Value | Why |
|-----------|-------|-----|
| max_return | 60 | AI-2 context must include title+hints for each row. At ~25 tokens/row (title ~10, hints ~15 after joining) 60 rows ≈ 1.5k tokens — fits easily. 80+ rows shows AI-2 latency degrades per pilot math (D8). |
| min_expand | 3 | Below 3 candidates, we trust the filter. Expanding small results risks diluting precision (already saw this as the BM25 pathology). |
| Fallback order | pp → category → type | processing_patterns is the most prone to AI-1 over-specification (many files have empty pp). Dropping it first minimizes false-empty results. Category drops next because types are coarse enough that type-only is still a useful candidate set. |

### D2.5 Unit test scope (TDD required per `.claude/rules/development.md`)

- Single-axis AND with realistic index
- Empty request → return all rows (not zero)
- Empty-pp rows excluded when pp filter non-empty
- Fallback ladder: 0-result → drop-pp → type-only → none-possible
- max_return truncation deterministic ordering
- Malformed axis value → exit 2
- "not yet created" rows excluded

---

## D3. AI-2 section-selection prompt + JSON schema

### D3.1 File location

`.claude/skills/nabledge-6/workflows/_knowledge-search/_section-select.md`

### D3.2 Context passed to AI-2

Per-row object: `{path, title, sections: [{id, hints}]}`.

- `title`: from index.toon column 1
- `hints`: from knowledge file `sections[].hints` — loaded by a helper script
  `scripts/collect-hints.sh` that batches the `get-hints.sh` logic across all
  candidate paths. **Body content is not loaded.**
- Budget: at most `max_return = 60` rows, ~6 sections/row average → ~360 section
  lines × ~15 tokens = ~5k tokens of hints. Fits cheap model context comfortably.

### D3.3 Full prompt text

```markdown
# Section Selection

Given a user question and a pre-filtered candidate list (title + per-section hints),
pick the sections that will answer the question. Output ONLY the JSON defined by
the schema.

## Rules

- Select at most 6 sections total across all files. Fewer is better if they
  answer the question fully.
- Each section's `relevance` is "high" (section directly answers) or "partial"
  (section contributes background but is not the answer core).
- Do NOT invent paths or section ids. Only select from the candidates provided.
- If none of the candidates plausibly answer the question, return an empty
  `results` array. This is the correct output for out-of-scope questions.
- Hints are short keyword lists per section; they are indicative, not exhaustive.
  A section whose hints partially match is still a valid candidate.

## Question

{{question}}

## Candidates

{{candidates_json}}
```

### D3.4 JSON schema

```json
{
  "type": "object",
  "required": ["results"],
  "additionalProperties": false,
  "properties": {
    "results": {
      "type": "array", "maxItems": 6,
      "items": {
        "type": "object",
        "required": ["file", "section_id", "relevance"],
        "additionalProperties": false,
        "properties": {
          "file": {"type": "string"},
          "section_id": {"type": "string", "pattern": "^s[0-9]+$"},
          "relevance": {"enum": ["high", "partial"]}
        }
      }
    }
  }
}
```

### D3.5 Ceiling rationale

- `maxItems: 6` per existing benchmark `expected_sections` (all 5 sample
  scenarios have 0-3 expected sections). 6 leaves headroom without encouraging
  over-selection.
- Downstream `read-sections.sh` cost scales linearly with section count; 6
  sections × typical section size ≈ 3-8k tokens to read.

---

## D4. Edge cases

### D4.1 Out-of-scope question (req-09 style)

- AI-1 may return `coverage: "out_of_scope"` OR `coverage: "uncertain"`.
- Orchestrator behavior:
  - `out_of_scope` → skip filter and AI-2, return `{"results": []}`
  - `uncertain` → run filter + AI-2 normally; AI-2 is free to return `[]`
- Benchmark req-09 expected result `expected_sections: []` is satisfied either by
  short-circuit or by AI-2 returning empty. Both paths must produce the same
  final pointer JSON.

### D4.2 Cross-cutting question (impact-01 style)

Transactions span `handlers` (TransactionManagementHandler, DbConnectionManagementHandler)
and `libraries`. AI-1 returns:
```
type=[component], category=[handlers, libraries], processing_patterns=[]
```
Empty `processing_patterns` is correct — transactions are not pattern-specific.
Filter ANDs only `type ∈ {component}` AND `category ∈ {handlers, libraries}` →
gives all handler + library files, ~60-80 rows → may trigger max_return
truncation. That is acceptable because AI-2 sees hints and can pick.

### D4.3 Empty processing_patterns axis (~225/295 files)

Empty is NOT a value. The filter NEVER treats a row's empty processing_patterns
string as matching a requested value. This prevents the silent-dilution failure
mode where an "empty" bucket absorbs all unrelated files.

Corollary: a question that SHOULD match many files must leave the pp axis empty
in the request, not fill it hoping to catch empty rows.

### D4.4 AI-2 returns a path not in candidates

Strict post-validation in orchestrator: drop any result whose `file` is not in
the candidate_paths set, log as warning. Never pass hallucinated paths to
`read-sections.sh`. Surface as a benchmark metric (D9).

---

## D5. Integration into skill files

### D5.1 File-level changes

| File | Action | Notes |
|------|--------|-------|
| `workflows/_knowledge-search.md` | **Rewrite** | New 3-step flow below |
| `workflows/_knowledge-search/_facet-extract.md` | **New** | D1 prompt |
| `workflows/_knowledge-search/_section-select.md` | **New** | D3 prompt |
| `workflows/_knowledge-search/_full-text-search.md` | **Delete** | No longer on search path |
| `workflows/_knowledge-search/_file-search.md` | **Delete** | Replaced by facet filter |
| `workflows/_knowledge-search/_index-based-search.md` | **Delete** | Subsumed by facet filter |
| `workflows/_knowledge-search/_section-search.md` | **Delete** | Replaced by `_section-select.md` |
| `workflows/_knowledge-search/_section-judgement.md` | **Delete** | AI-2 now does select+judge in one call |
| `scripts/facet-filter.py` | **New** | D2 |
| `scripts/collect-hints.sh` | **New** | Batches `get-hints.sh` for all sections in a file set |
| `scripts/keyword-search.sh` | **Kept as public entry point** (rename from `full-text-search.sh` per #307) | NOT called from search flow |
| `scripts/read-file.sh`, `read-sections.sh`, `find-file.sh` | **Keep** | Unchanged |
| `workflows/qa.md`, `workflows/code-analysis.md` | **Update** | Replace references to Step 1-7 keyword flow with "invoke `_knowledge-search.md`" abstraction (they already do this, verify) |

### D5.2 New `_knowledge-search.md` (skeleton)

```markdown
# Knowledge Search Workflow

Three-stage faceted search. Output: pointer JSON (same schema as before).

## Steps

### Step 1: Facet extraction
Delegate to `_knowledge-search/_facet-extract.md` with the question.
Output: {type, category, processing_patterns, coverage}.
If coverage == "out_of_scope", return {"results": []} and exit.

### Step 2: Mechanical filter
Run `scripts/facet-filter.py` with Step 1 facets.
Output: candidate_paths[].
If candidate_paths == [] after fallback ladder, return {"results": []} and exit.

### Step 3: Section selection
Collect hints for candidate_paths via `scripts/collect-hints.sh`.
Delegate to `_knowledge-search/_section-select.md` with question + candidates.
Output: pointer JSON (file, section_id, relevance).
Validate every result's file is in candidate_paths; drop and log violations.

## Output
Sort by relevance (high → partial), then path. Return pointer JSON.
```

### D5.3 `keyword-search.sh` is NOT on the search path

Per #307: `full-text-search.sh` → `keyword-search.sh` is a rename for a public
ad-hoc entry point. No workflow in `_knowledge-search` invokes it. Left available
so users / debugging sessions can run BM25 directly.

---

## D6. processing_patterns back-propagation

### D6.1 Current state

- `phase_f_finalize.py::_build_index_toon` (line 307) reads
  `fi["processing_patterns"]` from `classified["files"]` (the catalog, an
  intermediate artifact from Phase A).
- `mappings/v6.json` currently specifies only `type` and `category`.
- Result: processing_patterns is assigned somewhere in Phase A/B, not
  mechanically traceable from a committed source-of-truth.

### D6.2 Target state

`mappings/v6.json` becomes the single source of truth for all three axes.

**Schema change**: each mapping entry gains an optional `processing_patterns`
field:

```json
{"pattern": "application_framework/application_framework/web/",
 "type": "processing-pattern", "category": "web-application",
 "processing_patterns": ["web-application"]}
```

Rules:
- `type: "processing-pattern"` entries: `processing_patterns` defaults to
  `[category]` if omitted (matches current behavior at line 303-304).
- `type: "component"`, `"development-tools"`, etc.: default to `[]` if omitted.
- Explicit `processing_patterns` in a mapping entry overrides the default.
  Example: a handler used exclusively for RESTful web service can be tagged
  `["restful-web-service"]`.

### D6.3 Build step

**No new script.** Modify `phase_f_finalize.py::_build_index_toon`:

```python
if fi["type"] == "processing-pattern":
    patterns = fi.get("processing_patterns") or [fi["category"]]
else:
    patterns = fi.get("processing_patterns") or []
patterns_str = " ".join(patterns)
```

`fi` is sourced from the classified catalog, which copies axes verbatim from
`mappings/v{version}.json`. So the pipeline is:

```
mappings/v6.json  --Phase A classification-->  classified.json
                  --Phase F _build_index_toon--> index.toon (column 4)
```

### D6.4 hints field — does it enter index.toon?

**No.** Hints stay where they are: inside each knowledge JSON file, at section
granularity. AI-2 pulls them on demand via `collect-hints.sh`.

**Why not add hints to index.toon**: ~295 files × ~6 sections × ~15 tokens =
~27k tokens. Loading the whole index for every AI-1 call is wasteful. Hints
should only be loaded for the ~60 filtered candidates (Stage 3).

### D6.5 Regeneration

```
cd tools/knowledge-creator
./run.py --version 6 --phase f   # rebuilds index.toon from mapping+catalog
```

No hand edits to index.toon. If a mapping needs updating, edit `mappings/v6.json`
and re-run Phase F.

---

## D7. Benchmark scenarios schema

### D7.1 New scenario schema

```json
{
  "id": "review-04",
  "expected_question": "...",
  "expected_facets": {
    "type": ["component","processing-pattern"],
    "category": ["libraries","web-application"],
    "processing_patterns": ["web-application"],
    "coverage": "in_scope"
  },
  "expected_candidate_paths": [
    "component/libraries/libraries-bean_validation.json",
    "component/libraries/libraries-validation.json",
    "processing-pattern/web-application/web-application-feature_details.json"
  ],
  "expected_sections": [
    "processing-pattern/web-application/web-application-feature_details.json|s2",
    "component/libraries/libraries-bean_validation.json|s13",
    "component/libraries/libraries-validation.json|s1"
  ]
}
```

- `expected_keywords` is **deleted**.
- `expected_candidate_paths` is a minimum-recall set: these paths MUST appear in
  the filter output. The filter may return more; it must not return fewer.
- `expected_sections` is unchanged semantically (minimum-recall set of sections).

### D7.2 Per-stage scoring

| Stage | Metric | Definition | Pass gate |
|-------|--------|------------|-----------|
| 1 (AI-1) | Jaccard per axis | `|pred ∩ exp| / |pred ∪ exp|`, avg across 3 axes | ≥ 0.6 mean, coverage enum exact match |
| 2 (filter) | Candidate recall | `|pred_paths ∩ expected_candidate_paths| / |expected_candidate_paths|` | **1.0** (see D9 open question) |
| 3 (AI-2) | Section recall / precision | recall = `|pred ∩ exp| / |exp|`; precision = `|pred ∩ exp| / |pred|`. For req-09 (exp=[]), precision=1.0 iff pred=[] else 0. | recall ≥ 0.9 mean, precision ≥ 0.6 mean |

### D7.3 Why Jaccard on facets

Facet axes are unordered sets. Jaccard punishes both over-broadening (diluted
union) and under-specification (missing intersection) symmetrically. Per-axis
then averaged so no single axis dominates.

---

## D8. Cost/latency projection

### D8.1 Baseline (current flow, review-04)

- 452 seconds, $0.39 per question
- Full skill run includes: Step 1 keywords (AI), Step 2 BM25 (mech),
  Step 6 section judgement (AI over all BM25 hits), read-sections, answer
- AI-judgement over BM25 hits is the dominant cost because BM25 recall is
  noisy (0.76 mean, 0.40 worst) and returns many candidates per call

### D8.2 Projection (faceted flow, Opus for AI-1+AI-2)

| Call | Input tokens | Output tokens | Est. latency | Est. cost (Opus) |
|------|-------------:|--------------:|-------------:|-----------------:|
| AI-1 (facet) | ~1.5k (prompt + axis enums) | ~100 | ~4s | $0.03 |
| facet-filter.py | — | — | <0.5s | $0 |
| collect-hints.sh | — | — | <1s | $0 |
| AI-2 (section) | ~6k (question + 60 rows × hints) | ~200 | ~8s | $0.10 |
| read-sections | — | — | ~1s | $0 |
| answer (existing) | ~8k (prompt + sections) | ~2k | ~60s | $0.20 |
| **Total** | | | **~75s** | **~$0.33** |

**Latency: ~75s vs 452s baseline (≈6× speedup).**
**Cost: ~$0.33 vs $0.39 (~15% reduction), dominated by the answer call which is
unchanged.** Cost win is modest because faceted search replaces the cheap BM25 +
mid-cost section-judgement, not the expensive answer generation. The big gain is
latency.

### D8.3 Projection with Sonnet for AI-1+AI-2

If AI-1 and AI-2 run on Sonnet (schema-constrained JSON is within Sonnet's
reliable range for short structured outputs):

- AI-1: ~$0.006, ~2s
- AI-2: ~$0.020, ~4s
- **Total ~68s, ~$0.22** (≈45% cost reduction overall).

This is the open question (D9). Must be answered by running the benchmark with
both models on the 5-scenario sample.

### D8.4 Caching

- AI-1 prompt is 100% static (axis enums). Prompt cache hit rate expected ≥95%
  across a benchmark run.
- AI-2 prompt varies per question (different candidates). Static header
  (instructions) is cacheable, ~60-70% cache hit on repeated shape.

---

## D9. Risks and benchmark detection hooks

| # | Risk | Failure mode | Benchmark metric that catches it |
|---|------|--------------|----------------------------------|
| R1 | AI-1 over-broadens (returns all 8 types) | Filter becomes no-op, AI-2 drowns | Stage 1 Jaccard drops on `type` axis; Stage 2 candidate count exceeds max_return and `fallback_applied=truncated` log warning |
| R2 | AI-1 under-specifies (returns [] everywhere) | Filter returns all 295 rows | Stage 1 Jaccard 0 on all axes; Stage 2 total == 295 |
| R3 | AI-1 picks wrong axis value (e.g., `mom-messaging` instead of `db-messaging`) | Filter excludes the correct files | Stage 2 candidate_recall < 1.0 on specific scenario |
| R4 | AI-2 hallucinates a path | Pointer JSON references a non-candidate path | Orchestrator logs "dropped hallucinated path: X"; bench assert count == 0 |
| R5 | AI-2 misses a section whose hints don't name the question's vocabulary | Stage 3 recall < 0.9 (same failure class as current BM25 recall 0.40 on review-01) | Per-scenario recall; investigate hints quality for that file |
| R6 | `mappings/v6.json` diverges from `classified.json` (drift) | processing_patterns column in index.toon doesn't match mapping | Add Phase F verify step: assert `fi["processing_patterns"]` round-trips from mapping |
| R7 | Hints missing or generic on a key section | AI-2 cannot distinguish it from neighbors | Per-file `get-hints.sh` audit: flag sections with 0 hints or hints length < 2 |
| R8 | `coverage: out_of_scope` false-positive (shutting down an in-scope question) | Pointer JSON empty on an in-scope question | Benchmark coverage-enum exact-match check at Stage 1 |
| R9 | `processing_patterns` empty-axis ambiguity: AI-1 fills it when it shouldn't | Cross-cutting questions get narrowed | Impact-01 Stage 2 recall < 1.0; compare `processing_patterns` len to expected |
| R10 | Index.toon format drift (new axis, renamed type) breaking facet-filter.py parse | Runtime parse error / silent miscount | CI: unit test `test_parse_current_index_toon` that reads real index.toon |

All ten risks are detected by at least one benchmark metric in D7.

---

## Open questions to flag

**OQ1. Model choice for AI-1 and AI-2 (Opus vs Sonnet)**
Schema-constrained JSON with short outputs is a reliable Sonnet workload, but
AI-1 must correctly map natural-language questions into a constrained vocabulary
and AI-2 must interpret per-section hints that are sometimes sparse. Recommend:
pilot benchmark both models on the 5-scenario sample; default to Sonnet unless
Stage 1 Jaccard or Stage 3 recall drops below gate. Opus is the fallback.

**OQ2. Cross-version rollout timing**
`.claude/rules/nabledge-skill.md` mandates structural identity across
nabledge-1.2/1.3/1.4/5/6. However, the faceted flow is a material behavior
change, and baseline detection rates differ widely (v1.2: 78%, v6: 97%).
Options:
- **v6 pilot first** (recommended): Land on v6, validate against the 30-scenario
  benchmark in `.work/00307/scenarios-all-30.json`, then lock-step replicate to
  v1.2–v5. Isolates risk; violates "single commit" rule in a controlled way.
- **Lock-step**: Replicate to all 5 skills at once. Faster consistency but
  magnifies a design bug by 5×.
Recommend v6 pilot, with the rollout PR blocked by a green re-baseline on v6.
User approval required per `.claude/rules/design-decisions.md`.

**OQ3. Stage 2 recall hard gate**
D7.2 proposes `candidate_recall = 1.0` for Stage 2. Rationale: every expected
section's file must appear for AI-2 to have a chance. But a hard 1.0 means a
single bad mapping entry fails the whole scenario. Softer gate: require 1.0 on
`expected_candidate_paths` but allow benchmark PR to proceed with ≥0.95 provided
a mapping-fix issue is filed. Recommend hard 1.0 to stay aligned with the
project quality standard ("if there is even a 1% risk, eliminate it").

**OQ4. Hints coverage audit**
The design assumes hints are dense enough for AI-2 to distinguish sections.
Facts do not yet confirm this. Pre-implementation audit: run
`collect-hints.sh` over all 295 files, report sections with 0 or 1 hint, and
decide if hints generation in Phase B needs strengthening before the faceted
flow can meet Stage 3 recall gate. This is a prerequisite, not a follow-up.

**OQ5. Fallback ladder behavior vs benchmark**
When `fallback_applied != "none"`, Stage 2 recall is measured against the
**final** candidate set after fallback. Should a scenario that only passes via
fallback be flagged? Recommend: yes, as a `fallback_used` column in the report,
not as a failure. Repeated fallbacks indicate AI-1 over-specification and
should drive prompt iteration.
