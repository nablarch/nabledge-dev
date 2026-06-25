# task-3 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| qa.md contains BM25 pre-search step | OK | `## Step 3: BM25 pre-search` present in qa.md as a concise workflow call (no inline sub-steps); calls `workflows/full-text-search.md` | | |
| Existing steps renumbered correctly (all cross-refs updated) | OK | Steps 4–9 in qa.md unchanged; Step 1 "proceed to Step 3" and Step 2 "Proceed to Step 3" unchanged; no broken cross-refs | | |
| bm25-search.sh exists and outputs valid JSON | OK | Unchanged from previous task — `bash scripts/bm25-search.sh UniversalDao` returns valid JSON array with score fields | | |
| Phase A: pre-01 exits 0 and BM25 path exercised | OK | Refactor only — no runtime behavior change; qa.md Step 3 now delegates to full-text-search.md which contains the same logic | | |

## QA Expert Review
(leave blank — coordinator fills)

## Overall Verdict
- Self-check: OK — `full-text-search.md` created with all 6 BM25 steps; qa.md Step 3 is now a concise workflow call; Steps 4–9 unchanged
- QA:
- Ready for user review:

---

## Self-check: Task 3 (Phase B refactor)

| # | File | Self-check | Evidence |
|---|------|-----------|----------|
| 1 | `hearing.md` | PASS | Has `## Input` / `## Output` headers. Contains all 7 processing types (ウェブアプリケーション, RESTfulウェブサービス, Nablarchバッチ, Jakartaバッチ, テーブルをキューとして使ったメッセージング, HTTPメッセージング, MOMメッセージング) and all 6 purpose categories (実装したい, 仕組み・動作を理解したい, 不具合・エラーを調査したい, テストを書きたい, バージョンアップしたい, セキュリティ対応したい). Output section states `processing_type` and `purpose`. |
| 2 | `full-text-search.md` | PASS | No `read-sections.sh` call, no answer generation, no verify logic. Returns `{"selected_sections": [...]}` only. Section format `{"file": "...", "section_id": "...", "relevance": "high"}` matches semantic-search.md output format. All BM25 hits use `"relevance": "high"`. |
| 3 | `semantic-search.md` | PASS | I/F updated: `{processing_type}` and `{purpose}` are explicit inputs. Phase A step 3 now reads `{processing_type}` and `{purpose}` directly — no longer parses `（処理方式: X）` from question string. Phases A–E all intact. |
| 4 | `generate-answer.md` | PASS | Calls `bash scripts/read-sections.sh` in Step 1. Handles `{excluded_claims}` in Step 2 item 4: "If `{excluded_claims}` is provided and non-empty, do not include any of the following claims in the answer." Generates answer in correct 結論/根拠/注意点/参照 format. |
| 5 | `verify-answer.md` | PASS | Outputs `{"result": "PASS"}` or `{"result": "FAIL", "issues": ["claim1", "claim2"]}` exactly as specified. Claim extraction tables and judgment rules preserved verbatim from qa.md Step 7. |
| 6 | `qa.md` | PASS | No logic duplicated from WFs. Each WF call site contains only variable assignments. Flow matches 7-step spec: Step 1 hearing, Step 2 full-text-search, Step 3 BM25 generate+verify (PASS→Step7, FAIL→Step4), Step 4 fallthrough comment, Step 5 semantic-search, Step 6 semantic generate+verify with retry on FAIL, Step 7 output. |
