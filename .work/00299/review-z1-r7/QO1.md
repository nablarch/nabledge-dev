# QO1 Review — Z-1 r7

Target: `tools/rbkc/scripts/verify/verify.py` `check_json_docs_md_consistency` (QO1 portion), regexes `_H1_RE`, `_H2_RE`, and their interaction with spec §3-3.

Spec references quoted from `tools/rbkc/docs/rbkc-verify-quality-design.md`:

- §3-3 QO1: 「タイトル: JSON top-level `title` == docs MD の `#` 見出し」
- §3-3 QO1: 「セクションタイトル: JSON 各セクションのタイトルが docs MD の `##`/`###` に存在し、かつ JSON と同じ順序で並んでいる」
- §3-3 QO1: 「sections が空で top-level content のみの場合: docs MD に `##` 見出しが出現しない」

## Findings

### F1. `_H2_RE` treats `###` as a section-title heading, but `###` inside section content is legal Markdown and will be misclassified as an extra/out-of-order section

`_H2_RE = re.compile(r'^#{2,3}\s+(.+)$', re.MULTILINE)` collects every `##` and every `###` line in docs MD. Per spec §3-3 "セクションタイトルが docs MD の `##`/`###` に存在し", treating both levels as candidates is spec-faithful.

However, the code then compares that flat list (`docs_h2_titles`) directly against `json_sec_titles` for equality and order. `sections[*].title` in JSON is a single flat list — subsection structure is encoded by the section author writing `###` lines inside `sections[*].content`. docs.py renders `content` verbatim, so any `### 小見出し` the converter emitted inside a section body will be picked up by `_H2_RE` and reported as:

```
[QO1] …: docs MD has extra section title not in JSON: '小見出し'
```

This is a false positive produced by verify itself against valid output. ゼロトレランス (§2-1) forbids accepting this risk: even a single source file that contains a `###` inline heading in its converted content will FAIL QO1 spuriously, and the "fix" would have to happen in verify (not in RBKC), because the output is correct.

Quoted spec clause that the current code contradicts in practice:
- §3-3 QO1: "セクションタイトル: JSON 各セクションのタイトルが docs MD の `##`/`###` に存在し、かつ JSON と同じ順序で並んでいる"

The spec requires JSON section titles to **exist at** `##`/`###`; it does **not** say every `##`/`###` in docs MD must be a JSON section title. The implementation inverts the direction in the "extra" check.

Proposed fix: limit the "extra" direction to the level docs.py actually emits for sections (`##` only — see docs.py lines 98). Keep `###` acceptable on the "presence" direction only, if future converters promote a section to `###`. Simplest correct form:
- Collect docs headings at `##` only for the extra-check list.
- For the missing-check, also accept a JSON title matched at `###`.

### F2. Extra-H2 detection for `sections == []` is restricted to any `##/###`, same false-positive class

Line 138: `if not sections and docs_h2_titles:` uses the same `docs_h2_titles` list. A file with `sections=[]` but whose top-level `content` legitimately contains a `### ` inline heading would FAIL QO1 with "docs MD has section headings but JSON has no sections". Same root cause as F1.

Quoted spec clause: §3-3 QO1 "sections が空で top-level content のみの場合: docs MD に `##` 見出しが出現しない" — the spec names `##` only, not `###`.

### F3. `_H1_RE` does not reject a line that starts with `#` but is actually a Setext / ATX closing pattern edge case — in practice safe, documented as observation

`_H1_RE = re.compile(r'^#\s+(.+)$', re.MULTILINE)` correctly rejects `##`/`###` because the char after the first `#` is another `#`, not whitespace, so `\s+` fails and the regex does not match the line. Tested via `test_multiple_h1_in_docs_md_first_wins` and by the structural guarantee that `## X` has no whitespace at offset 1.

No finding on H1 rejection of `##`.

### F4. `_H1_RE` captures the trailing ATX close `#` characters if present (`# Title #`)

CommonMark allows an optional closing sequence: `# Title #` is a valid H1 with title "Title". `_H1_RE`'s `(.+)$` greedily captures `Title #`, and the `.strip()` on line 130 only trims whitespace, not trailing `#`. If docs.py ever emits an ATX-closed form (or a future converter does), `docs_title` becomes `"Title #"` and fails the equality check against JSON `"Title"`.

docs.py currently never emits the closed form (lines 75, 87, 98, 116, 125, 130), so this is latent. Under ゼロトレランス, a latent regex that silently misreads a spec-valid form is a bug: spec §3-3 says "docs MD の `#` 見出し" without restricting ATX form. Same class applies to `_H2_RE`.

Quoted clause: §3-3 QO1 "タイトル: JSON top-level `title` == docs MD の `#` 見出し".

Proposed fix: strip an optional trailing ` #+` from the captured title group, per CommonMark §4.2 ATX headings.

### F5. `_H1_RE.search` picks the first `#` line; if the first `#` sits inside a non-fenced indented code block (4-space indent), the regex will still match it because `^` is line-start, not block-start

CommonMark treats a 4-space-indented line as an indented code block, and text inside is not a heading. `_H1_RE`'s MULTILINE `^` matches any line start regardless of indentation, and `^#\s+` requires `#` at column 0, so an indented `    # not heading` would NOT match (good). But a leading tab or <=3 spaces of indent followed by `#` (which CommonMark still treats as a heading) — `^#\s+` requires column 0 `#` literally, so `   # heading` (3 spaces) would be missed.

This is a precision gap against CommonMark. In practice docs.py always writes `# ` at column 0, so latent. Observation only.

### F6. Equality-based order check misses duplicate-title ordering subtleties when JSON has duplicated section titles

`docs_h2_titles != json_sec_titles` catches list-level mismatch including duplicates because list equality is ordered + counted. This is correct. No finding.

## Observations

- O1. Test `test_fail_duplicate_h2_order_violation` (line 105) exercises a real ordering case: JSON `[B, A]` vs docs `[A, B]`. The list-equality compare plus the "no missing / no extra → order differs" branch (lines 152-156) correctly flags it. Good.

- O2. `test_pass_tilde_fenced_code_block_with_heading_inside` and the backtick counterpart guard against the most important false-positive source (fences). These are solid.

- O3. `_FENCE_BLOCK_RE = re.compile(r'^(```|~~~).*?^\1', re.MULTILINE | re.DOTALL)` requires the closing fence to also be at line start (`^\1`). CommonMark requires the closing fence on its own line, indented 0-3 spaces — column-0 is the common case. A closing fence preceded by up to 3 spaces would not match; headings after such an unterminated (from the regex's view) fence would be treated as inside the fence and silently dropped. Observation: under-masking is a false-negative risk for QO1 (heading inside a fence gets reported) but the current regex fails *open* the other way (over-masking when fence isn't closed at column 0, false negatives). Under ゼロトレランス this is a real concern; docs.py does not emit indented closing fences, but user-authored RST/MD content passed through as JSON body could.

## Tests — coverage gaps

The test class does not exercise:

1. A section whose `content` contains a `### subheading` line — would demonstrate F1 / F2 directly. Missing.
2. An ATX-closed heading `# Title #` — would demonstrate F4. Missing.
3. A `sections=[]` file whose top-level `content` contains a `### foo` line — would demonstrate F2. Missing.
4. Indented closing fence with `## fake` heading after it — would demonstrate O3. Missing.

Every one of these is a spec-valid CommonMark / spec-valid content case that the current code silently mishandles, and ゼロトレランス requires them to be tests, not assumptions.

## Summary of required changes

1. (F1/F2) Use `##`-only for the "extra H2" direction; allow `##`/`###` only on the "JSON title found in docs" direction. Add tests for inline `###` inside content.
2. (F4) Strip optional trailing ATX close sequence from captured H1/H2 titles. Add test for `# Title #`.
3. (O3) Either tighten fence regex to CommonMark (allow 0-3 leading spaces on open/close), or document the restriction with a spec-clause citation. Add test for indented closing fence.
4. (F5) Observation — no change required unless CommonMark indent tolerance becomes relevant.
