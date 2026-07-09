# task-2 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| pre-01 実行時 `answer.md` の `参照:` ブロックがページタイトル・plain docs パス・インデントしたセクションタイトルの形式で出力される（bare `file.json:sN` が残っていない） | OK | `tools/benchmark/results/20260708-113336/pre-01/answer.md` の `参照:` ブロック: `- アーキテクチャ概要\n  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md\n  Nablarchバッチアプリケーションの構成\n  リクエストパスによるアクションとリクエストIDの指定\n  Nablarchバッチアプリケーションの処理の流れ` — bare `file.json:sN` なし | | |
| `参照:` ブロックに `#anchor` が含まれない | OK | pre-01 answer.md の `参照:` ブロック内に `#` によるアンカーフラグメントなし | | |
| `nabledge-6/workflows/qa.md` の変更が `参照:` 指示ブロック以外に及んでいない | OK | git diff 確認: 変更箇所は `参照:` 指示ブロック（Path derivation, Example）のみ | | |

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Verification approach meaningful to the objective (checks the right thing, not just "passed") | OK | All three criteria checked against actual pre-01 output: page title present, plain docs path with correct prefix, indented section titles, no bare file.json:sN, no #anchor, no out-of-scope changes |

## Expert Reviews

### Craft Expert (writing)

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Medium-specific best practice | OK (after fix) | Fix 1: replaced `{json-path-with-.md-extension}` curly-brace placeholder with `<derived path with .md extension>` angle-bracket style — unambiguously signals substitution rather than literal output |
| Consistency with existing style | OK | `参照:` restructuring matches existing answer-format block style; terminology consistent |

### Verification Expert (fact-check)

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Artifact actually checked (claims verified against source) | OK | All paths and section titles verified against actual docs files on disk |
| Coverage (edge cases / claims / steps) | OK | Both example entries confirmed: libraries-database.md page title, section titles in libraries-universal-dao.md |

## Overall Verdict

- Self-check: OK
- QA: OK
- Design expert: N/A
- Craft expert: OK (after fix in commit 1e1425c6)
- Verification expert: OK
- Ready to check off: Yes

---

## Fix round 1 (2026-07-08)

Two defects found and fixed in the path derivation rules:

**Defect 1 (qa.md + code-analysis.md): Wrong path derivation rule**
- Old rule said "replace `knowledge/` with `docs/`" — dead operation because JSON paths from `read-sections.sh` are relative paths like `component/libraries/libraries-database.json` (no `knowledge/` prefix).
- Fixed: now says "prepend `.claude/skills/nabledge-6/docs/`" (qa.md) and "prepend `../../.claude/skills/nabledge-6/docs/`" (code-analysis.md), with concrete examples.

**Defect 2 (qa.md only): `Path: ` label inconsistency**
- Template description had `Path: .claude/...` label but the example omitted it.
- Fixed: removed `Path: ` label from the template description to match the example (the example is the authority).

**Additional improvement (qa.md): multi-section example and restructured instruction**
- Added a second entry to the example showing two sections from the same file (`条件を指定して検索する` under ユニバーサルDAO).
- Restructured the instruction block: "One entry per cited file, in this format:" followed by the format, then "Path derivation:" as a separate labeled rule.
