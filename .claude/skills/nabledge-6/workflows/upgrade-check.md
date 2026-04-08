# Upgrade Check Workflow

Analyze the impact of upgrading Nablarch from one version to another. Runs a rule-based script to detect affected items and uses LLM evaluation for undecidable cases, then generates a structured Markdown report.

## Input

- Target project root path
- Upgrade source version (e.g., `6`)
- Upgrade target version (e.g., `6u3`)

## Output

Markdown impact assessment report presented to the user

## Steps

### Step 0: Detect Nablarch version from pom.xml

**Tool**: Bash

**Action**:
1. Locate `pom.xml` in the target project (recursive search):
   ```bash
   find <project-path> -name "pom.xml" | head -5
   ```
2. Extract the current Nablarch version from `<parent>` or `<dependency>` elements:
   ```bash
   grep -E "(nablarch|5u|6u)" <project-path>/pom.xml | grep -E "version|artifactId" | head -20
   ```
3. If the version cannot be detected automatically, prompt the user to specify `--from-version` explicitly.

**Output**: Confirmed Nablarch version range (from/to versions to use in Step 1)

**Branch**:
- If `pom.xml` is not found → inform user, ask for project root path, HALT workflow
- If version is not detected → ask user to specify the source version manually, then continue

---

### Step 1: Run rule-based filter (upgrade-checker.sh)

**Tool**: Bash

**Action**:
1. Determine the release notes JSON directory:
   - Default path (Nablarch 6): `knowledge/releases/releases/` (within nabledge-6 skill directory)
   - To resolve the absolute path, use `$SKILL_DIR/knowledge/releases/releases/` where `SKILL_DIR` is the nabledge-6 skill root
2. Run the upgrade checker script:
   ```bash
   bash .claude/skills/nabledge-6/scripts/upgrade-checker.sh \
     --release-notes-dir .claude/skills/nabledge-6/knowledge/releases/releases \
     --project-dir <project-path> \
     --from <from-version> \
     --to <to-version>
   ```
3. Capture stdout (JSON format with hit/no-hit/undecidable classification per item)

**Output**: JSON result listing affected items, no-hit items, and undecidable items

**Branch**:
- If script exits with non-zero status → display the error message, ask user to verify paths, HALT workflow
- If 0 affected items and 0 undecidable items → inform user that no impact was found, skip to Step 3

**Error handling**:
- JSON directory not found: show expected path (`knowledge/releases/releases/`), advise user to verify the nabledge-6 skill is properly installed
- grep errors in script stderr: display stderr output and continue (non-fatal)
- Script not found: verify `.claude/skills/nabledge-6/scripts/upgrade-checker.sh` exists

---

### Step 2: LLM-assisted evaluation for undecidable items

**Tool**: In-memory (LLM evaluation)

**Action**:
1. For each item marked as `"undecidable"` in Step 1 output:
   a. Read the corresponding section content from the release note JSON:
      ```bash
      bash .claude/skills/nabledge-6/scripts/read-sections.sh \
        "<release-note-json-path>:<section-id>"
      ```
   b. Evaluate whether the change affects the target project based on the section text
   c. Classify the item as one of:
      - `affected` — change clearly applies to this project
      - `not_affected` — change does not apply to this project
      - `requires_manual_review` — cannot determine automatically; human review needed

2. For items marked `"affected"` by the rule-based filter:
   a. Read the corresponding section content
   b. Extract the recommended action or workaround from the section text

**Output**: Enriched result with LLM classification and recommended actions for each item

**Branch**:
- If all undecidable items are classified as `not_affected` and the rule-based `affected` list is also empty → inform user that no impact was found, skip to Step 3 (report still generated)

---

### Step 3: Generate impact assessment report

**Tool**: In-memory (LLM generation)

**Action**:
1. Compose a Markdown report using the following structure:

```markdown
# Nablarch Upgrade Impact Assessment
## Target: {from} → {to}
## Summary
- Affected items: N
- Requires manual review: M
- No impact confirmed: K

## Affected Items
| # | Title | Detection | Match Location | Action |
|---|-------|-----------|----------------|--------|
| 1 | ... | Rule R5 (FQCN match) | src/main/java/Foo.java:42 | ... |

## Items Requiring Manual Review
| # | Title | Reason |
|---|-------|--------|
| 1 | ... | Conditional impact — verify manually |

## No Impact Confirmed
The following items were evaluated and confirmed to have no impact on this project:
- ...
```

2. Present the report to the user

**Output**: Markdown impact assessment report

---

## Error handling

| Scenario | Action |
|----------|--------|
| `pom.xml` not found | Ask user to specify the project root path |
| JSON cache directory not found | Show expected path; advise user to verify nabledge-6 skill installation |
| `upgrade-checker.sh` not found | Verify the scripts directory exists; report path to user |
| `grep` errors in script output | Display stderr and continue (non-fatal) |
| Version range produces no JSON files | Confirm the version range is correct; list available JSON files in the releases directory |
