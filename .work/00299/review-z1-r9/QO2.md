# Z-1 r9 Bias-Avoidance QA Review — QO2

**Scope**: `check_json_docs_md_consistency` (QO2 branches only), `_apply_asset_link_rewrite`, `TestCheckJsonDocsMdConsistency_QO2`.
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3.

Format: Findings quote the violated spec clause verbatim. Observations flag matters on which the spec is silent.

---

## Findings

### F1. `knowledge_dir is None` silent no-op path in `_apply_asset_link_rewrite` is untested and can mask QO2 violations

Spec §3-3 QO2 clause: *"JSON 各セクションの content が docs MD に完全一致で含まれていない"* (FAIL condition, unconditional — no skip carve-out).

`verify.py:101-102`:
```
if docs_md_path is None or knowledge_dir is None:
    return text
```

When the caller omits the paths, the rewrite becomes a no-op and the comparison runs on the raw JSON text. The docstring describes this as "legacy callers / unit tests without real paths", but spec §3-3 does not sanction such a carve-out — it says the JSON content must appear verbatim in docs MD. If a caller under-passes paths, a `![x](assets/y.png)` in JSON will be compared literally against a docs MD containing `![x](../../../knowledge/assets/y.png)` and FAIL, which is the correct direction; but equally, a caller that passes paths selectively (e.g. `docs_md_path` set, `knowledge_dir=None`) silently turns the rewrite off.

Spec §2-1 ゼロトレランス disallows a skip path that is not derivable from the spec itself. No unit test exercises the `None` branch; `TestCheckJsonDocsMdConsistency_QO2` does not cover it.

### F2. QO2 "section content verbatim" test suite is silent on the `assets/` no-asset-FAIL symmetry case when only `docs_md_path` or only `knowledge_dir` is passed

Spec §3-3 QO2 clause: *"JSON 各セクションの content が docs MD に完全一致で含まれていない"*.

`_apply_asset_link_rewrite` returns early when **either** path is `None` (`verify.py:101`). The current tests cover only two of the four partial-pass combinations:

| `docs_md_path` | `knowledge_dir` | test coverage |
|---|---|---|
| set | set | `test_pass_assets_link_rewrite_symmetric`, `test_fail_assets_link_rewrite_missing_from_docs` |
| None | None | `test_pass_top_content_in_docs` and siblings (no assets/) |
| set | None | **absent** |
| None | set | **absent** |

If the production call-site ever regresses to half-passing paths (e.g. forgetting one argument in a refactor), QO2 will silently accept rewritten-docs-vs-raw-JSON as "no diff" because the rewrite is skipped. The spec does not sanction that.

### F3. Closing `)` in an MD link URL is not handled by `_MD_LINK_RE` — both in verify and in `docs._rewrite_asset_links`

Spec §3-3 QO2 clause: *"JSON 各セクションの content が docs MD に完全一致で含まれていない"*.

`verify.py:86` and `docs.py:36`:
```
_MD_LINK_RE = re.compile(r'(!?\[[^\]]*\])\(([^)]+)\)')
```

`[^)]+` rejects any `)` inside the URL. CommonMark §6.3 allows `)` inside the URL when balanced, and allows a `"title"` component after the URL. A JSON section content of `[x](assets/a(1).png)` therefore has no `assets/...` match in either implementation, and the rewrite is skipped on **both** sides — which by chance makes the "verify equals docs" containment pass, but the skip is not spec-sanctioned. Spec §3-3 says verbatim containment; it does not carve out link-with-paren URLs.

The r7-added symmetric drift test (`test_verify_and_docs_rewrite_agree_on_matrix`) uses only simple URLs — `assets/a(1).png`, `assets/a "t".png`, percent-encoded forms, and the CommonMark pointy-bracket form `<assets/x.png>` are absent from the matrix. The drift test therefore cannot catch the case where both copies skip an asset link in lock-step.

### F4. Fenced-code masking does not match the CommonMark fence definition the spec presumes

Spec §3-3 QO2 evaluates docs MD against "完全一致". Docs MD is CommonMark, so the fence-detection the verifier uses must match CommonMark's fence rule. The spec cites no alternative.

`verify.py:69`:
```
_FENCE_BLOCK_RE = re.compile(r'^(```|~~~).*?^\1', re.MULTILINE | re.DOTALL)
```

CommonMark §4.5 allows:
- Fences indented by up to 3 spaces (regex requires column 0).
- Opening fence of N backticks closed by N-or-more (regex requires exact-length close via backref).
- Opening fence followed by an info string that may itself contain a `~` or backtick variant (regex `.*?` is fine but sees the first such char on the same line).

A 4-backtick fence `\`\`\`\`markdown ... \`\`\`\`` closes on 4+ backticks. The current regex captures only the first 3 and may stop at a 3-backtick line inside the block, cutting the mask short. Any `##` that falls between the "short close" and the real close is then read as a section boundary, so the top-content region-bounding in QO2 (`verify.py:215`) will truncate early and a legitimate top content will appear to be missing.

No QO2 test exercises a 4-backtick fence, indented fence, or the tilde form (`~~~`) with a variant-length close.

### F5. Top-content region end uses `_H2_ONLY_RE` on the masked text but the containment check runs on the unmasked `docs_md_text`

Spec §3-3 QO2 clause: *"JSON top-level `content` が docs MD の `#` 見出し直下に完全一致で含まれている"*.

`verify.py:208-218`:
```
masked = _FENCE_BLOCK_RE.sub(_mask, docs_md_text)
h1_match = _H1_RE.search(masked)
h2_match = _H2_ONLY_RE.search(masked)
start = h1_match.end() if h1_match else 0
end = h2_match.start() if h2_match else len(docs_md_text)
top_region = docs_md_text[start:end] if start <= end else ""
if expected not in top_region:
```

The offsets `start`/`end` are computed on `masked` but indexed into `docs_md_text`. The masking replaces non-newline bytes with spaces (preserving length), so positions are byte-equivalent — this is correct. However, `h1_match.end()` on the masked string points past `# T\n` including the heading content, but `_H1_RE` is `^#\s+(.+)$` — the `end()` is the position after the last char of the title, not after the trailing newline. If the JSON top `content` begins with `\n` (i.e. JSON content = `"\n本文"`), the substring check needs that leading newline. docs.py at `docs.py:91` emits `lines.append(_rewrite_asset_links(top_content, ...))` with `"\n\n".join(...)` around it, so the physical docs MD has `# T\n\n本文` — one `\n` is consumed by `end()`, the other remains in the region. Any JSON content with a leading `\n` therefore passes; without a leading `\n` also passes. **This is correct** but fragile: no test demonstrates the boundary (`test_pass_top_content_in_docs` uses a content that neither starts with nor is sensitive to the boundary).

This is a test-coverage finding, not an implementation finding: the top-region boundary arithmetic is an undocumented invariant that no test pins down.

### F6. `test_fail_whitespace_only_diff` name does not match what it tests

Spec §3-3 QO2 requires verbatim containment. The test at `test_verify.py:366` names itself "whitespace-only diff" and asserts FAIL, but the inputs are `"本文\n\n続き"` (JSON) vs `"本文 続き"` (docs) — this is a substring-absence case, not a whitespace-normalization case. The test passes for the right reason (verbatim `in` check), but the name and docstring imply the verifier performs whitespace-sensitive comparison as a deliberate policy. No test asserts the inverse — that two strings differing *only* by a trailing newline (e.g. JSON `"A"` vs docs containing `"A\n"`) **pass**, which is the actual whitespace-sensitivity claim the spec's "verbatim" wording leaves open to interpretation.

The finding is circular-test-adjacent: the test name claims to test whitespace policy but actually tests substring absence.

---

## Observations (spec-silent)

### O1. `os.path.relpath` platform behaviour

`verify.py:104` and `docs.py:59` both use `os.path.relpath`. On Windows this returns backslash-separated paths; on POSIX, forward slashes. Spec §3-3 is silent on path separator. Because both sides use the same call, the strings stay symmetric, and QO2 containment holds on either platform. Not a finding — but the symmetric-drift test `test_verify_and_docs_rewrite_agree_on_matrix` runs only on the host platform, so cross-platform symmetry is asserted only where tests run.

### O2. `_apply_asset_link_rewrite` only matches `assets/` at URL start

Spec §3-3 is silent on how docs MD should resolve other URL shapes (`./assets/…`, URL-encoded, pointy-bracket autolinks). Both verify and docs apply the same filter, so symmetry holds. The r7 matrix `test_verify_and_docs_rewrite_agree_on_matrix` could be extended to include these forms to guard against future asymmetric changes.

### O3. `no_knowledge_content` short-circuit is QO2-wide

`verify.py:130-131` returns `[]` when `no_knowledge_content` is set. Spec §3-3 covers QO1/QO2/QO3/QO4 but does not explicitly state that QO2 is waived for `no_knowledge_content` files. The waiver is inferable from §3-3's overall framing (docs MD is derived from JSON; no content → nothing to check) but not literally stated. Not a finding — the inference is reasonable — but the code comment does not cite any spec clause.

### O4. `_MD_LINK_RE` treats `![alt](...)` and `[text](...)` identically

Both are valid MD; docs.py rewrites both, verify rewrites both. Spec does not distinguish. Noted for completeness.

---

## Summary

Five findings (F1–F5 implementation / test gaps that can suppress a spec-violating case) plus one test-naming finding (F6). Four observations on spec-silent behaviour that are symmetric today but would benefit from matrix coverage.
