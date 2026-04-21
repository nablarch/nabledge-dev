# Knowledge File Generation & Verification Prompt Improvement Task

## Background

Current knowledge file generation copies RST almost verbatim. JSON/RST size ratio is 0.84x–1.35x.
Manual conversion of 10 sections achieved 0.34x (~1/3) by extracting only decision-relevant content.

Root cause: Step 2d instruction "Keep all specifications and concepts" drives agents to copy RST wholesale.

RST analysis across all 11 categories confirms a single common approach works for all (see Appendix A).

---

## Tasks

### Task 1: Replace Step 2d in `workflows/knowledge.md`

**File**: `.claude/skills/nabledge-creator/workflows/knowledge.md`

**Steps**:
1. Find `### 2d. Convert to JSON` section inside the Step 2.2 Task agent prompt (4 lines)
2. Replace the entire section with the following

**Replacement content**:

````markdown
### 2d. Extract Knowledge from RST

Classify each paragraph/sentence in the RST into Layer A, B, or C. Write only A and B to JSON. Remove all C.

#### Step 1: Classify each sentence

**Layer A — Decision Criteria (→ KEEP ALL)**

Keep every sentence that an AI agent needs to make correct implementation decisions:
- Technology selection rules ("use Y instead of X", "X is deprecated")
- Constraints ("configure X before Y", "if X is not set, Z happens")
- Content inside `.. important::`, `.. warning::`, `.. tip::` directives
- Deprecation notices with alternatives ("this feature is deprecated; use X instead")
- Pitfalls/traps ("X appears to work but causes Y problem")
- Decision branches ("for case A use X; for case B use Y")

**Layer B — Implementation Specs (→ KEEP, minimize)**

Keep these with accuracy, write concisely:
- Class names / fully-qualified names
- Configuration property names, types, default values
- XML config examples (minimum working configuration only)
- Java/SQL code examples (minimum to show the pattern)
- Maven dependency info (groupId/artifactId)
- Method signatures, argument types, return types

**Layer C — Everything Else (→ REMOVE)**

If a sentence is neither Layer A nor Layer B, do not write it to JSON. This includes but is not limited to:
- Lead-in sentences: "The following shows...", "This section describes..."
- Referral sentences: "For details, see Javadoc", "See external site"
- Background explanations: "The reason X is dangerous is..."
- Gradual concept introductions: "First, you need to understand..."
- RST markup: `.. image::`, `.. contents::`, `:java:extdoc:` link syntax (extract class name only)
- Verbose preambles: "Refer to the following configuration file example given below" → keep only the XML
- getting_started tutorials
- Repetition of what was already written in overview

#### Step 2: Write retained content to JSON

Use category templates from knowledge-schema.md for JSON structure.
Write Layer A content in Japanese, concisely.
Compress Layer B from RST's verbose prose.

Do not add any information that is not in the RST. Do not infer, guess, or supplement.

**Example 1 — Compress handler description (Layer B)**:

RST (5 lines):
```
This handler, in addition to repeatedly executing the processing of the
subsequent handlers, performs transaction control, and commits the
transaction at a certain number of repetitions, while the data to be
processed is present in the data reader. By increasing the transaction
commit interval, it is possible to improve the throughput of batch processing.
```

→ JSON description (1 line):
```
"後続ハンドラの繰り返し実行＋トランザクション制御（一定件数ごとにコミット）。コミット間隔でスループット調整可能"
```

**Example 2 — Remove preamble, keep only XML (Layer C removal + Layer B retention)**:

RST:
```
Configure the handler by referring to the configuration file example given below.
.. code-block:: xml
  <component class="nablarch.fw.handler.LoopHandler">
    <property name="transactionFactory" ref="databaseTransactionFactory" />
    <property name="transactionName" value="name" />
  </component>
```

→ JSON xml_example (preamble removed, XML only):
```
"<component class=\"nablarch.fw.handler.LoopHandler\">\n  <property name=\"transactionFactory\" ref=\"databaseTransactionFactory\" />\n  <property name=\"transactionName\" value=\"name\" />\n</component>"
```

**Example 3 — Keep important/warning as-is (Layer A)**:

RST:
```
.. important::
  :ref:`transaction_management_handler` has to be configured to use this handler.
  Since the transaction control is not implemented if the transaction control handler
  is not configured, all subsequent changes to the database will be discarded.
```

→ JSON warnings:
```
["TransactionManagementHandlerが未設定の場合、トランザクション制御が行われずDB変更がすべて破棄される"]
```

**Example 4 — Deprecated library (Layer A: keep decision + reason; Layer C: remove tutorial)**:

RST:
```
.. important::
 This function is **deprecated** because of the following reasons:
 Uses :ref:`universal_dao` for exclusive control.

 * Exclusive control of :ref:`universal_dao` can be used more easily than this function.
 * If the primary key is defined as a non-string type, this function cannot be used
   depending on the database.
```

→ JSON notes:
```
["この機能は非推奨。代わりにUniversalDaoの排他制御を使うこと。理由: (1) UniversalDaoの方が簡易 (2) 主キーが文字列型以外の場合、DBによっては型不一致で実行時エラーが発生する"]
```

**Example 5 — Testing framework rules (Layer A/B only; Layer C tutorial removed)**:

RST:
```
The test class should be created in such a way that the following conditions are met.

* The test class package should be the same as the Action class to be tested.
* Create a test class with a class name of <Action class name>RequestTest.
* Inherits ``nablarch.test.core.batch.BatchRequestTestSupport``.

For example, if the Action class to be tested is ``nablarch.sample.ss21AA.RM21AA001Action``,
the test class would be as follows.

.. code-block:: java

  package nablarch.sample.ss21AA;
  // ~ Middle is omitted ~
  public class RM21AA001ActionRequestTest extends BatchRequestTestSupport {
```

→ JSON description:
```
"テストクラス作成ルール: (1) テスト対象Actionと同一パッケージ (2) クラス名は{Action名}RequestTest (3) BatchRequestTestSupportを継承"
```
(The "For example..." paragraph and code example are Layer C — they illustrate the rules but add no new decision-relevant information. The rules themselves are Layer A.)

#### Category-specific additional rules

Apply these in addition to the common rules above:

- **testing-framework**: Remove tutorial-style step-by-step instructions (Layer C). Keep only test class naming rules, Excel format rules, and NTF API specs.
- **guide/nablarch-patterns**: Most content is Layer A (decision criteria). Preserve over compress.
- **adapters**: Prioritize accuracy for XML config examples. Keep tested library version info.
- **libraries**: Keep deprecated features as Layer A in the form: "This feature is deprecated. Use X instead. Reason: ..."
````

---

### Task 2: Replace Step VK2.3 in `workflows/verify-knowledge.md`

**File**: `.claude/skills/nabledge-creator/workflows/verify-knowledge.md`

**Steps**:
1. Find `### 2.3 Verify Content Accuracy` section inside the Step VK2.2 Task agent prompt
2. Replace the entire section with the following

**Replacement content**:

````markdown
### 2.3 Verify Content Accuracy

For each RST section and its corresponding JSON section, verify two things: no omissions and no fabrications.

#### A. Omission Check (RST → JSON)

Read the RST section. Identify every piece of information that an AI agent would need to make correct implementation decisions. For each one, confirm it exists in the JSON.

What counts as decision-necessary information:
- Constraints and prerequisites (ordering, required configurations, preconditions)
- Warnings about incorrect behavior or failure modes
- Recommendations and best practices
- Deprecation notices and their alternatives
- Technology selection guidance (when to use X vs Y)
- Configuration properties, their types, defaults, and effects
- API specifications (class names, method signatures, argument types)
- Maven dependency info (groupId/artifactId)
- Code examples that demonstrate correct usage patterns

For each omission found, record:
"OMISSION: {RST heading or line description} — {what information is missing from JSON}"

#### B. Fabrication Check (JSON → RST)

Read the JSON section. For every statement, confirm it has a basis in the RST source.

Check each of these:
- Every sentence in description fields — does the RST say this?
- Every item in warnings/notes arrays — does the RST contain this warning or note?
- Every property in setup/configuration — does the RST define this property with this type and default?
- Every code example — does the RST contain this code, or is it a faithful minimal extraction of RST code?
- Every class name — does the RST reference this exact class name?

For each fabrication found, record:
"FABRICATION: section {section_id} — {the statement in JSON} — no basis found in RST"
````

---

### Task 3: Add checklist items to `scripts/generate-checklist.py`

**File**: `.claude/skills/nabledge-creator/scripts/generate-checklist.py`

**Steps**:
1. Open the checklist generation section
2. Append the following section to the existing checklist items

**Checklist items to add**:

```markdown
## Knowledge Extraction Quality

### Omission Check (RST → JSON)
- [ ] All `.. important::` content is reflected in JSON
- [ ] All `.. warning::` content is reflected in JSON
- [ ] All `.. tip::` recommendations are reflected in JSON
- [ ] All deprecation notices include alternatives in JSON
- [ ] All constraints/prerequisites are in JSON
- [ ] All configuration properties with types and defaults are in JSON
- [ ] All class names and API signatures are in JSON
- [ ] All Maven dependencies (groupId/artifactId) are in JSON

### Fabrication Check (JSON → RST)
- [ ] Every description statement has RST basis
- [ ] Every warning/note has RST basis
- [ ] Every configuration property matches RST definition
- [ ] Every code example is from RST (not generated)
- [ ] Every class name matches RST exactly
```

---

## Execution Order

1. Execute Task 1 → Replace Step 2d in knowledge.md
2. Pilot test → Generate knowledge files for these 6 RST files using the updated prompt:
   - handlers: `loop_handler.rst`
   - libraries: `bean_util.rst`
   - adapters: `doma_adaptor.rst`
   - processing-pattern: `architecture.rst` (nablarch-batch)
   - testing-framework: `batch.rst`
   - guide: `Nablarch_batch_processing_pattern.md`
3. Execute Task 2 → Replace verification prompt
4. Verify pilot files with updated verification prompt
5. Execute Task 3 → Update checklist
6. If pilot results are satisfactory, roll out to full file generation

---

## Appendix A: RST Analysis Summary by Category

| Category | Files | Content Nature | Common Approach | Notes |
|----------|-------|---------------|----------------|-------|
| handlers | ~56 | Highly structured specs | ✅ | Most uniform category |
| libraries | ~48 | Diverse (API + concepts) | ✅ | Keep deprecated as Layer A |
| adapters | ~14 | Setup procedures | ✅ | XML accuracy priority |
| nablarch-batch | ~19 | Architecture + patterns | ✅ | Decision criteria heavy |
| restful-web-service | ~9 | Spec tables + code | ✅ | — |
| web-application | ~13 | Similar to handlers/libs | ✅ | — |
| testing-framework | ~N | Test procedure guides | ✅ | Remove tutorials |
| blank-project | ~19 | Setup procedures | ✅ | — |
| nablarch-patterns | 3 (MD) | Decision criteria itself | ✅ | Preserve over compress |
| security-check | 1 (XLSX) | Checklist | Separate | Excel-specific handling |
| jakarta-batch | ~13 | — | — | Out of scope |
