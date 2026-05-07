# Expert Review: Software Engineer

**Date**: 2026-05-07
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 2 files

## Summary

0 Findings

## Findings

None.

## Observations

- The `safe` parameter comment says `safe also includes "-_.()"` but the actual code is `safe="/-_()"`. The period `.` is absent from the string literal. However, this is not a bug: Python's `urllib.parse.quote()` treats `.` as an RFC 3986 unreserved character and never encodes it regardless of the `safe` parameter. The comment is slightly misleading (it implies `.` is in `safe` as a listed character), but the runtime behavior is correct. No fix required.

- `quote()` encodes non-ASCII characters (e.g., Japanese chars in filenames → percent sequences). This is intentional and correct: verify.py calls `unquote(href)` at line 1835 before resolving cross-document links, so the encoding round-trip is transparent. No action required.

- The fix is applied only to the `rel_md` path used in the README entry, not to the `docs_md_path` used for actual file I/O (`docs_md_path.write_text`). This is correct: the encoding only needs to appear in the Markdown link text, not the filesystem path.

- Separation of concerns is clean: `generate_docs()` handles encoding at the point where the path enters the Markdown link string, before it is handed to `_generate_readme()`. This is the right layer.

## Positive Aspects

- Minimal, surgical change: exactly 1 import and 1 assignment. No existing logic modified.
- `urllib.parse.quote` is the stdlib standard for percent-encoding — no third-party dependency introduced.
- The `safe` parameter correctly preserves `/` (directory separators), `-` (common in file IDs), `_`, `(`, `)` so that most knowledge file names are written verbatim and only the rare space is encoded.
- The comment explains the intent, the `safe` parameter rationale, and the example (`space → %20`) clearly.
- The fix is idempotent: paths without spaces pass through `quote()` unchanged, so existing README entries are not affected.

## Files Reviewed

- `tools/rbkc/scripts/create/docs.py` (source code)
- `tools/rbkc/tests/ut/test_docs.py` (test code)
