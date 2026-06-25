# task-1 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| docker-compose.yml exists and `docker compose up` starts Qdrant | OK | `docker compose -f tools/rag/docker/docker-compose.yml up -d` succeeded; `curl http://localhost:6333/healthz` → `healthz check passed`; container `docker-qdrant-1` Up (qdrant/qdrant:v1.13.4) | | |
| index.py runs with --limit 10, stores points in Qdrant | NG | Chunking and metadata derivation work correctly (21 chunks from 10 files). Bedrock call to `cohere.embed-v4:0` fails with `AccessDeniedException`: "no service control policy allows the bedrock:InvokeModel action" for IAM user `PJ111-ito.kiyohito`. Model is ACTIVE in Bedrock but SCP blocks direct IAM user access. `cohere.embed-multilingual-v3` is accessible; `cohere.embed-v4:0` is not. Points were NOT stored. | | |
| Stored points have processing_type / category / page_id / section_id in metadata | NG | Not stored due to Bedrock SCP block on cohere.embed-v4:0. Metadata derivation is correct per unit tests (27/27 pass). | | |
| test_index.py tests all pass | OK | `python3 -m pytest tools/rag/tests/test_index.py -v` → 27 passed in 0.05s. All tests for chunking, metadata derivation, linked_pages extraction, classes.md parsing pass. | | |

## Notes on NG items

**Root cause**: IAM user `PJ111-ito.kiyohito` in account `686255957667` is blocked by SCP from calling `bedrock:InvokeModel` on `cohere.embed-v4:0`. The design doc (§2.1) confirmed the model is available in ap-northeast-1, but SCP restricts this specific IAM user.

**Accessible Cohere models**: `cohere.embed-multilingual-v3` (dim=1024), `cohere.embed-english-v3` (dim=1024) are accessible but differ from the design-specified `cohere.embed-v4:0`.

**Implementation correctness**: All code paths (chunking, metadata, Qdrant upsert) are correct and covered by unit tests. The `--no-verify-ssl` flag handles the corporate proxy SSL issue. The Bedrock SCP block is an environment/access issue, not an implementation bug.

**Resolution needed**: SCP update to allow `bedrock:InvokeModel` on `cohere.embed-v4:0` for this IAM user, OR use of a different IAM principal that has the required permission.

## QA Expert Review
(leave blank — coordinator fills this)

## Expert Reviews (code changes only)
(leave blank — coordinator fills this)

## Overall Verdict
- Self-check: NG (Bedrock SCP blocks cohere.embed-v4:0; unit tests 27/27 pass; docker-compose OK)
- QA: 
- Language expert: 
- Software-engineering expert: 
- Ready for user review: 
