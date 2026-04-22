# Stage 1: Facet Extraction

Map the user's question to discrete facet values on two axes that index the
Nablarch-6 knowledge base. Output ONLY the JSON defined by the schema — no
tools, no prose, no markdown.

## Context

The knowledge base has 295 files, each tagged on two axes: `type` and
`category`. You MUST select values only from the enumerated lists below.
Any value not in the list is invalid.

Processing patterns (batch, web, REST, messaging) are NOT a separate axis.
They are expressed as `type=processing-pattern` together with a
`category` that names the pattern (e.g., `web-application`,
`restful-web-service`). Cross-cutting mechanisms (handlers, libraries,
validation, transactions) are expressed as `type=component` with a
concrete `category`.

### Axis: type (pick 0–3)

- about               — concept, philosophy, release notes, migration
- check               — static security self-audit checklist (NOT runtime
                        authorization; authorization/認可/権限チェック uses
                        `component` with `handlers` or `libraries`)
- component           — concrete framework pieces: handlers, libraries, adapters
- development-tools   — testing framework, toolbox, static analysis
- guide               — business samples, tutorials
- processing-pattern  — end-to-end guide for a processing pattern
- releases            — release notes (Nablarch 6.x)
- setup               — blank project, configuration, setting-guide, cloud-native

### Axis: category (pick 0–4)

about-nablarch, adapters, biz-samples, blank-project, cloud-native,
configuration, db-messaging, handlers, http-messaging, jakarta-batch,
java-static-analysis, libraries, migration, mom-messaging, nablarch-batch,
nablarch-patterns, release-notes, releases, restful-web-service,
security-check, setting-guide, testing-framework, toolbox, web-application

Note: seven of these category values double as processing-pattern names —
`nablarch-batch`, `jakarta-batch`, `restful-web-service`, `http-messaging`,
`web-application`, `mom-messaging`, `db-messaging`. When a question is
pattern-specific, pair them with `type: ["processing-pattern"]` (and
typically also `"component"` so cross-cutting pieces are not excluded).

## Coverage

Set `coverage` to one of:

- `in_scope`     — a Nablarch question the knowledge base is likely to cover
- `uncertain`    — Nablarch-related but the feature may not be built in
- `out_of_scope` — not a Nablarch question (e.g., general Java, non-Nablarch
                   product, pure infrastructure question)

If coverage is `uncertain`, still emit plausible facets (do not leave
empty) so the downstream filter can surface the closest Nablarch pages.
If coverage is `out_of_scope`, leave both `type` and `category` as `[]` —
the downstream filter will short-circuit regardless, and empty arrays
keep the telemetry honest.

## Selection rules

- Under-specify over over-specify. If the user says "バリデーション" without
  naming a processing pattern, return a `component`-leaning `type` and do
  NOT add `web-application` speculatively.
- Prefer `component` + a concrete category (`libraries`, `handlers`,
  `adapters`) when the user names a concrete mechanism (e.g., ハンドラ,
  Bean Validation, UniversalDao, トランザクション).
- Include `processing-pattern` as a type (and the pattern's name in
  `category`) when any of the following holds:
  1. the question is "how do I build a ___" style (pattern entry-point);
  2. the question is clearly scoped to one pattern;
  3. the question names a UI / runtime surface even as a modifier —
     `画面` → `web-application`, `REST` / `API` → `restful-web-service`,
     `バッチ` → `nablarch-batch` or `jakarta-batch`, `メッセージ` / `MOM` →
     `mom-messaging` or `http-messaging`. Add the pattern axis even when
     the subject of the question is a cross-cutting mechanism.
- For cross-cutting concerns that apply to multiple patterns, include both
  `component` (for the mechanism's own file) and, optionally,
  `processing-pattern` (for the pattern's overview that references it) —
  but skip the pattern axis when the question is truly pattern-agnostic.
- Never invent axis values. If no value fits, leave that axis empty.
- The seven pattern-name categories (`nablarch-batch`, `jakarta-batch`,
  `restful-web-service`, `http-messaging`, `web-application`,
  `mom-messaging`, `db-messaging`) are used ONLY together with
  `type: ["processing-pattern"]` (optionally also `"component"`). Never
  emit them with a `type` that does not include `processing-pattern`.

## Output schema

```json
{
  "type": "object",
  "required": ["type", "category", "coverage"],
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
    "coverage": {"enum": ["in_scope","uncertain","out_of_scope"]}
  }
}
```

## Examples

Question: "ファイルの明細レコードを読み込んで DB テーブルに取り込む夜間バッチを作りたい。Nablarch での推奨構成を知りたい"
→ `{"type": ["processing-pattern","component"], "category": ["nablarch-batch","libraries"], "coverage": "in_scope"}`

Question: "ユーザーが入力する画面項目のチェックを Nablarch 流で書きたい"
→ `{"type": ["component","processing-pattern"], "category": ["libraries","web-application"], "coverage": "in_scope"}`

Question: "バッチで DB を更新しているんだけど、コミットのタイミングやトランザクションの境界は何で決まる？"
→ `{"type": ["component"], "category": ["handlers"], "coverage": "in_scope"}`

Question: "管理画面を特定のロールだけ開けるようにしたい。Nablarch にアクセス制御の仕組みはある？"
→ `{"type": ["processing-pattern","component"], "category": ["web-application","handlers","libraries"], "coverage": "in_scope"}`

Question: "REST API のレート制限は Nablarch にある？"
→ `{"type": ["component"], "category": ["handlers"], "coverage": "uncertain"}`

Question: "Spring Boot の設定ファイルはどこに置く？"
→ `{"type": [], "category": [], "coverage": "out_of_scope"}`

## Question

{{question}}
