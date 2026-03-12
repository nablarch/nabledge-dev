# Notes

## 2026-03-12

### Context: R2 Fabrication Findings Background

The large kc run (run_id: 20260309T232615, work1) ran ACDEM with max_rounds=2 on all 421 v6 knowledge files:
- Phase D R1: 48 fabrication findings among 289 "has_issues" files (total 419 files)
- Phase E R1: Fixed 289 files, deleted their findings files
- Phase D R2: 30 fabrication findings among 205 "has_issues" files
- Phase E R2: Fixed 205 files, deleted their findings files

### Problem: R2 Findings Are Gone

Phase E deletes findings files after fixing (`os.remove(findings_path)` in phase_e_fix.py:100).
Phase D R2's findings files for the 205 "has_issues" files were deleted by Phase E R2.

The findings directory (`20260309T232615/phase-d/findings/`) only contains:
- 212 clean files (findings were never deleted - only has_issues files get deleted by Phase E)
- 1 file with a single `section_issue` finding
- Total: 213 files = the clean ones from Phase D R2

The 30 fabrication findings from Phase D R2 are not recoverable from the findings directory.

### Approach: Re-run Phase D on Phase D R2 ISSUE Files

Identified the 205 Phase D R2 ISSUE files from the execution log (lines 889-1097).
Selected 20 diverse representative files from 6+ categories.
Launched subagent to run `python3 tools/knowledge-creator/scripts/run.py --version 6 --phase D`
on the sample in work2.

### Technical Notes

- work2/.lw → symlink to work1/.lw (RST sources)
- Phase D findings write to .logs/v6/{run_id}/phase-d/findings/ (gitignored)
- Knowledge files read from .cache/v6/knowledge/ (post-Phase E R2 state)
- clean_phase not needed for fresh run (new run_id = new findings dir)

### Results

- Batch 1 (run 20260312T102320): 2 fabrications, both real, in testing-framework-batch--csv
- Batch 2 (run 20260312T103251): 7 fabrications (6 real, 1 ambiguous) across 6 files
- Total: 9 findings across 40 sampled files, false positive rate = 0%
- All unambiguous findings are genuine fabrications
- Phase E R2 fixed many but not all fabrications
- 3 systematic patterns: grid-table header invention, empty-split generation, inference-as-fact

See report.md for full analysis including per-finding RST comparison.

## 2026-03-12（追加調査：RST vs JSON 直接比較）

### 全9件の捏造をRST原文と直接比較して確認

PR #172 マージ後、各 finding の RST ソース（Phase D in.txt）と JSON を直接比較。
全9件とも「RSTに書いていないことが書かれている」ことを確認した。

### 捏造の原因パターン（6種）

1. **フォーマット変換の副作用**（F1）
   RSTのグリッドテーブルはヘッダなしが合法だが、Markdownはヘッダ行が構文上必須。
   変換時にLLMが列名（区分/フィールド1/フィールド2/フィールド3）を架空生成した。

2. **例→ルール化（推論の事実化）**（F2, F6）
   例示データ（空セル、`//` 行）を見て暗示的なルールを「読み取り」、明文化して事実として記述。
   RSTは例を示しているだけでルールを明言していない。

3. **目的からの補完**（F3）
   テストが「何をすべきか」を理解して、RSTに書いていない検証の意図を追記。
   論理的には正しいが根拠がない。

4. **空コンテンツへの対処**（F4）
   splitが本文ゼロの場合、LLMが「何か書かなければ」と判断してプレースホルダーを生成。

5. **コードの「正規化」**（F5, F7）
   不完全・不整合に見えるコード（`<!-- 中略 -->`、`$`なし記法）を「正しく」修正。
   意図的な省略を「バグ」と誤解している。

6. **関連情報からの推論**（F8 ambiguous, F9）
   アーティファクト名（`nablarch-fw-standalone`）や他箇所の記述から用途を推論して記述。

### NTFに集中している理由

9件中7件がNablarch Testing Framework（NTF）のファイルから。
NTFドキュメントには捏造を誘発しやすい構造が集中している：
- ヘッダなしグリッドテーブルが多い
- テスト動作を例示スタイルで説明する（ルールを明言しない）
- 複数行にまたがる結合セルが多い
- 長いファイルのsplit境界で本文ゼロになりやすい

### 検知できる理由・修正が難しい理由

**検知が比較的できる理由**：
Phase DはRSTとJSONを両方持った状態で「この文字列がRSTに存在するか」という
文字列マッチング的なチェックができる。テーブル構造を完全に理解しなくても、
「区分」という文字列がRSTのどこにも存在しないことは確認できる。

**修正が難しい理由**：
RSTグリッドテーブルを正しくMarkdownに変換するには空間的な構造の理解が必要。
LLMはトークン列として処理するため、`+---+---+`の視覚的構造が潰れる。
「何が間違いか」はわかっても「どう直すか」の正解を出すのが難しい。

### 「HTML vs RST」の本質的なギャップ

NTFドキュメントはブラウザでレンダリングされたHTMLで読むことを前提に書かれており、
人間ですらHTMLで読んで初めて理解できる複雑なテーブルがある。
AIはその生のRSTテキストを処理しており、人間が参照しているHTMLとの乖離がある。

根本的な改善案：RSTではなくレンダリング済みHTMLまたはテキストを入力にする。
人間が理解する形と同じものをAIに見せることで精度向上が期待できる。

### 全体アーキテクチャへの示唆

Phase B（曖昧な理解で生成）→ Phase D（文字列照合的に検知）→ Phase E（構造理解が必要で修正が困難）
という非対称性があり、各フェーズで「できること」と「できないこと」が異なる。
R1→R2の2ラウンドでも解消しきれない残留捏造はこの構造的限界に起因する。

Phase Eの改善より「Phase Bが最初から作らない」ほうが根本的な解決策。
具体的にはPhase Bのプロンプトに「各記述がソースに根拠があるか自己確認せよ」を追加する方向。
