# QC5 形式純粋性 — QA Review

**Target**: RBKC verify QC5 (Format purity) — detect RST/MD syntax remnants in JSON output.
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1
**Scope**: RST / MD (xlsx excluded)

---

## 1. 実装の有無

### RST — ✅ 実装あり

`tools/rbkc/scripts/verify/verify.py:214-232`

Patterns:
- `_RST_ROLE_RE` (L214): `:[a-zA-Z][a-zA-Z0-9_.-]*:\``  → `:role:\`text\``
- `_RST_DIRECTIVE_RE` (L215): `\.\.\s+\S+.*::`  → `.. directive::`
- `_RST_LABEL_RE` (L217): `\.\.\s+_[a-zA-Z0-9_-]+:`  → `.. _label:`
- `_RST_HEADING_UNDERLINE_RE` (L216): `^[=\-~^"'\`#*+<>]{4,}\s*$` (MULTILINE) — checked only when `is_title=True` (L230)

`_rst_syntax_issues()` L222-232 emits `[QC5]` messages. `_check_format_purity()` L244-271 applies to title + content + per-section title/content (L253-261). Underline check is correctly gated by `is_title` — matches spec ("heading underline (title only)").

### MD — ✅ 実装あり

`tools/rbkc/scripts/verify/verify.py:218-219, 235-241`

Patterns:
- `_MD_RAW_HTML_RE` (L218): `(?<![a-zA-Z])<[a-zA-Z][a-zA-Z0-9]*[\s>]` — detects `<details>`, `<summary>`, `<br>`, `<a ...>` etc. with negative lookbehind to avoid mid-word matches.
- `_MD_BACKSLASH_ESCAPE_RE` (L219): `\\[*_\`\[\](){}#+\-.!|]` — detects `\*`, `\_`, `\[`, etc.

Applied to title/content/sections at L262-270.

### Integration — ✅

xlsx short-circuits at L245 (`if fmt == "xlsx" or _no_knowledge(data): return []`), matching spec ("Excel 対象外").

---

## 2. ユニットテストのカバレッジ

File: `tools/rbkc/tests/ut/test_verify.py:255-336` (`TestVerifyFileQC5`, 9 tests)

| Spec item | Test | Verdict |
|---|---|---|
| RST `:ref:\`x\`` / `:class:\`y\`` | `test_fail_rst_role_in_content` (L275) — uses `:ref:\`something\`` | ✅ |
| RST `.. note::` directive | `test_fail_rst_directive_in_content` (L282) | ✅ |
| RST `.. _label:` | `test_fail_rst_label_in_content` (L289) | ✅ |
| RST heading underline in title | `test_fail_rst_heading_underline_in_title` (L296) — title=`====` | ✅ |
| RST heading underline in content (should be allowed, not title) | **⚠️ missing** — no explicit negative test that `====` inside content does NOT raise QC5 | ⚠️ |
| RST clean content passes | `test_pass_rst_clean_content` (L301) | ✅ |
| MD `<details>`, `<summary>`, `<br>`, `<a>` | `test_fail_md_raw_html_in_content` (L308) — only `<details>` tested; `<summary>`, `<br>`, `<a>` not explicitly covered | ⚠️ partial |
| MD `\*`, `\_`, `\[` | `test_fail_md_backslash_escape_in_content` (L315) — only `\*` tested; `\_`, `\[` not explicitly exercised | ⚠️ partial |
| MD clean content passes (incl. inline `\`code\``) | `test_pass_md_clean_content` (L322) | ✅ |
| xlsx skipped | `test_pass_xlsx_no_qc5` (L328) | ✅ |
| `no_knowledge_content` skipped | `test_pass_no_knowledge_content_skipped` (L334) | ✅ |
| **Edge: Japanese punctuation false positive** | ❌ missing | ❌ |
| **Edge: code fence containing directive (should NOT FAIL)** | ❌ missing — and since `_check_format_purity` runs on raw JSON content strings without stripping code fences, a code block containing `.. note::` in MD source would indeed pass JSON (converter strips it) but this invariant is not asserted by a test | ❌ |
| **Edge: inline code containing role syntax** | ❌ missing | ❌ |

### カバレッジ判定: ⚠️ 基本ケースはカバー、エッジケース不足

Spec-listed core patterns each have at least one RED-path test. However, three edge cases the QA brief specifically names are untested:
- Japanese punctuation false positive (e.g. does `：`/`・` ever mistakenly match?)
- Code-fence-containing-directive (invariant: converter drops it — but no regression test locks this down)
- Inline code with role syntax (e.g. `` `:ref:\`x\`` `` inside code span — should ideally not FAIL but currently **would** FAIL since regex scans raw string)

Also, the positive variants for `:class:`, `<summary>`, `<br>`, `<a>`, `\_`, `\[` are not individually asserted (same code path, so low risk, but weak against regex regressions).

---

## 3. v6 verify + ユニットテスト実行結果

### v6 verify

```
$ cd tools/rbkc && bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0
$ bash rbkc.sh verify 6 2>&1 | tail -3
All files verified OK
```

✅ **FAIL = 0**

### Unit tests

```
$ python3 -m pytest tests/ 2>&1 | tail -3
tests/ut/test_xlsx_converters.py ......                                  [100%]
============================= 138 passed in 3.10s ==============================
```

✅ **138 passed, 0 failed**

---

## 4. 総合判定

**⚠️ Acceptable but test coverage has gaps**

- 実装: ✅ spec §3-1 の全パターンを正しく実装。xlsx 除外、underline の title-only ゲートも正しい。
- テスト: ⚠️ 基本 RED/GREEN は揃うが、QA ブリーフ明示のエッジケース 3 件が未テスト。潜在的に深刻なのは **inline code / code fence 内の構文を誤検出する可能性** で、現行実装は生文字列を regex スキャンするため、将来 JSON に inline code が含まれる仕様変更があると false positive を起こす余地がある。
- 実行: ✅ v6 FAIL 0, 138 tests pass.

Zero-tolerance 基準で見ると、「1% のリスクも排除」の観点から **エッジケースの不在 = 未検知のリグレッション余地** に該当する。現状 v6 で FAIL が出ていないのは運が良いだけでなく、JSON 生成側が role/directive を剥がしている結果。そのガードレールを verify 側のテストで明示的に固めるべき。

---

## 5. 改善案（実装は変更しない、テスト追加のみ）

**[High] エッジケーステスト追加** — `TestVerifyFileQC5` に以下を追加:

1. `test_pass_rst_heading_underline_in_content` — `content="====\n見出し\n===="` (section content) で QC5 が発火しないことを確認。仕様の "title only" ゲートを固定。
2. `test_fail_md_raw_html_summary_br_a` — `<summary>`, `<br>`, `<br/>`, `<a href="...">` それぞれで発火することを確認（parametrize 推奨）。
3. `test_fail_md_backslash_escape_all_chars` — `\_`, `\[`, `\`` などを parametrize で網羅。
4. `test_pass_md_inline_code_with_role_syntax` — JSON content に `` `:ref:\`x\`` `` のような inline code が混入した場合の期待動作を明文化（現実装では **FAIL する** — 仕様上 MD には RST role は存在しないので影響なしだが、挙動をテストで固定しておく）。
5. `test_pass_japanese_punctuation_no_false_positive` — `：`, `・`, `※`, `「」` を含む通常日本語コンテンツで QC5 が発火しないことを確認。

**[Medium] 仕様クロスチェック**:
- `rbkc-verify-quality-design.md` §3-1 に列挙された全パターン ↔ `_RST_*_RE` / `_MD_*_RE` の 1:1 マッピング表を docstring に追加（verify.py L211-219 付近）。テストではなくコメントで「なぜこの regex なのか」を固定化。

**[Low] 負の回帰テスト**:
- `:class:`, `:func:`, `:doc:` 各 role 別のテスト（parametrize 1 本で足りる）。

いずれも実装変更は不要、テスト追加のみ。
