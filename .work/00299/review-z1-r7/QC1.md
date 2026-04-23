# QC1 — r7

## Summary

2 Findings — not shippable.

Bias-avoidance re-derivation from `rbkc-verify-quality-design.md` §3-1 and the
project quality standard surfaces two violations. The zero-exception paths (unknown
node/role/unresolved ref/parse error → QC1 FAIL), the sequential-delete ordering, the
no-tolerance residue rule for the MD and Excel paths, and the 1-char Excel residue
test are all spec-conformant and independently pinned by tests — those parts are
correct. The RST path, however, still post-processes the Visitor output in
`verify.py` with image/link/whitespace normalisation that the spec does not
authorise, and still reports RST residue as a single truncated snippet while MD
reports all fragments. Both are explicitly ruled by the standard (§2-2 shared
normaliser; `.claude/rules/rbkc.md` "RST one-snippet vs MD all-fragments → All
fragments").

## Findings

1. **RST verify-side post-normalisation after the shared Visitor (verify.py:551–557)**
   - Violated clause: `rbkc-verify-quality-design.md` §3-1 "残存判定の基準" —
     > "手順 0 の Visitor が出力する正規化ソースと、JSON 側の MD は**完全に同じ記法で揃っている**前提で sequential-delete を行う"
     > "許容構文要素リスト・許容残存パターンといった例外リストは**設けない**"
     > "JSON content の MD 記法も create 側が `scripts/common/rst_ast_visitor.py` 経由で出力し、verify 側の正規化ソースと同じヘルパー (`scripts/common/rst_ast.py` の `escape_cell_text` / `normalise_raw_html` / `fill_merged_cells`) を使う。両側の記法揃えが create/verify 共通モジュールで構造的に保証される。"
     And §2-2 independence principle — "共通モジュール経由で create と verify が別々に AST を consume し、それぞれ独立に正しく動くことで品質ゲートが担保される", with the listed exception table covering only QO1/QO2/QO4.
   - Description: `_check_rst_content_completeness` calls
     `_normalize_rst_source(...)` (the shared Visitor path) and then, at
     `verify.py:551–557`, runs an additional loop that strips MD image syntax
     (`![..](..)`), collapses `[text](url)` to `text`, and squashes whitespace
     — re-applying the same custom post-processing that `_build_rst_search_units._norm`
     (`verify.py:475–486`) does on the JSON side. This is a second, verify-only
     normalisation layer on top of the shared Visitor. It is not present in the
     MD path (`normalise_md` + `_squash` only). The spec mandates that record-keeping
     for residue agreement lives in the shared `scripts/common/` helpers, not in
     verify.py. If the extra stripping is needed to keep JSON and source in sync,
     it must be in the shared helper so create-side generation uses the same code;
     if it is not needed, it hides genuine residues (e.g. a bare `![alt](url)` the
     JSON failed to capture would be silently erased from the residue set).
   - Fix: Remove `verify.py:551–557` and `_build_rst_search_units._norm`'s image/link
     stripping. If `![..](..)` / `[text](url)` truly must be normalised away for the
     sequential-delete algorithm, move that rule into `scripts/common/rst_ast_visitor`
     (or the create-side MD emitter it shares with the converter) so both sides go
     through the same code. Add a unit test that fails if a verify-only strip is
     re-introduced (e.g. feed an RST with an image whose JSON counterpart omits the
     alt text — must FAIL as residue, not pass silently).

2. **RST residue reporting collapses to a single 80-char snippet, masking additional gaps (verify.py:605–607)**
   - Violated clauses:
     - `CLAUDE.md` §Quality Standard — "If there is even a 1% risk, eliminate it — do not accept it" / "100% content coverage is the target across all source formats".
     - `.claude/rules/rbkc.md` "Decide from the spec and quality standard" examples —
       > "`QC1` residue reporting — RST one-snippet vs MD all-fragments — which is correct? → All fragments. The one-snippet form hides gaps, which ゼロトレランス forbids."
     - `rbkc-verify-quality-design.md` §3-1 判定分岐のまとめ row 4 — "正規化ソース残存に**空白・改行以外**のテキストが残った | QC1（欠落）" (plural residue; not "first 80 chars").
   - Description: The MD path at `verify.py:706–710` iterates every non-whitespace
     fragment in the residue and emits one `[QC1]` per fragment. The RST path at
     `verify.py:605–607` emits exactly one `[QC1]` whose payload is the first
     80 characters of `residue.strip()`. An RST JSON file with several distinct
     missing fragments reports a single snippet; the later gaps are structurally
     invisible to the operator and to any downstream FAIL-counting tool. This is
     the exact asymmetry `.claude/rules/rbkc.md` names as a ゼロトレランス violation.
   - Fix: Replace the snippet block with the MD path's per-fragment emission —
     iterate `residue.split()` (after merging consumed spans as the MD path does
     at L688-704) and emit one `[QC1] RST source content not captured: <frag[:50]>`
     per non-empty fragment. Add a unit test with three disjoint residues in the
     source: assert exactly three `[QC1]` entries. Also align the residue
     computation with MD's consumed-span merge (current RST code at L596-603 uses
     `residue.find(..)` from 0 and mutates a single string, which can collapse
     adjacent residues into a single fragment and loses position fidelity).

## Observations

- The RST sequential-delete residue loop at `verify.py:596–603` finds each unit
  from position 0 in a mutating string, rather than from the recorded consumed
  position as the MD path does via merged consumed spans. After fixing Finding 2
  by aligning with the MD merge-consumed approach, this observation is
  structurally resolved — it is not itself a spec violation today because any
  missed unit was already reported by the preceding QC2/QC3/QC4 loop, but the
  duplicated logic makes future drift likely.
- Zero-exception paths (unknown node/role/unresolved reference/parse error →
  `[QC1]`) are correctly wired in both `rst_normaliser.normalise_rst`
  (`strict_unknown=True` re-raises `UnknownSyntaxError`, plus the
  `(ERROR/3)`/`(SEVERE/4)` warning stream scan at L58–61) and `md_normaliser.normalise_md`.
- Excel direction reversal is correct per §3-1 Excel 節: source-cells-deleted-from-JSON
  with per-token `[QC1]` on absent and `[QC3]` on consumed-overlap.
  `test_fail_qc2_one_char_fabrication_detected` (test_verify.py L1297) explicitly pins
  the no-length-tolerance rule from §3-1 Excel 節 手順 3.
- Tests are not circular: hand-written RST/MD/xlsx sources + hand-written `data`
  dicts are used, and `test_fail_qc1_md_unknown_token_surfaces` injects a synthetic
  markdown-it Token that the converter cannot produce, isolating the verify-side
  strict path.
- `_no_knowledge_content: true` early return is covered for all three paths (RST/MD
  at test_verify.py L935, Excel at L1272).

## Positive Aspects

- Zero-exception principle is enforced at the normaliser boundary; no silent
  children-recursion fallback was found in the RST or MD QC1 path.
- No allowed-residue tolerance list — consistent with §3-1 残存判定の基準 and the
  removal recorded in commit `be604f880` (refactor: remove allowed-residue tolerance list).
- 1-char Excel fabrication is asserted to FAIL, matching the spec's no-length
  tolerance wording.
- Tests reference spec wording (docstrings cite "§3-1 手順", "zero-exception") and
  assert on the semantic `[QC1]` prefix rather than on private message strings.
- MD residue reporting is spec-conformant (all fragments reported) and is the
  reference implementation the RST path should converge on.
