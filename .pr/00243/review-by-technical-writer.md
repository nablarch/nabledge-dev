# Expert Review: Technical Writer

**Date**: 2026-03-26
**Reviewer**: AI Agent as Technical Writer
**Files Reviewed**: 5 files (3 articles + 2 guideline files)

## Overall Assessment

### Article 1: `01-get-ai-ready-on-nablarch.md`
**Rating: 4/5**
Well-structured introduction with a clear story arc and accessible technical explanations. Minor style concern in closing section.

### Article 2: `02-knowledge-creator.md`
**Rating: 4/5**
Strong narrative with good technical depth. Numbers are specific and properly distinguished between different runs. One style rule violation (bold bullet list in summary).

### Article 3: `03-build-with-expert.md`
**Rating: 4/5**
Excellent tone — personal, honest, and practical. "No Babysitting" framing is effective. A few minor issues: "だけ" framing risk, unexplained worktree term, TODO placeholder comments.

## Key Issues

### High Priority

#### H-1: 第1弾 — index.toon エントリ数（review-prompt の記述が stale）
- Description: `review-prompt-nabledge-series.md` に「296エントリ」と記載されているが、実際の `index.toon` ヘッダーは `files[295,]` で 295 エントリ。記事は既に 295 に修正済み。
- Decision: **Reject** — 記事の 295 は正確。review-prompt の 296 が誤り。review-prompt を 295 に修正する。
- Reasoning: `index.toon` の実データが `files[295,]` であることを直接確認済み。

#### H-2: 第1弾 — Mermaid 図に「回答生成」ノードが含まれる
- Description: 知識検索パイプラインの説明に「回答生成」ステップが含まれているが、パイプライン自体はポインタJSON返却で終わる。
- Decision: **Defer** — ユーザー視点の全フローとして「回答生成」まで示すことは理解しやすさのための合理的な簡略化。

### Medium Priority

#### M-1: 第2弾 — まとめセクションが太字リスト（文体ルール2違反）
- Description: 「AIの行動範囲は〜」「初回生成は1回〜」など4項目の太字リストがまとめに使われている。
- Decision: **Implement Now** — 段落形式に書き直す。
- Reasoning: ルール2違反。Deferすると全3弾で違反が残る。

#### M-2: 第3弾 — まとめセクションが箇条書きリスト（文体ルール2違反）
- Description: 「- **見える化** — 〜」形式の6項目リスト。
- Decision: **Implement Now** — 段落形式に書き直す。
- Reasoning: 同上。

#### M-3: 第3弾 — 「人間がやるのは〜だけ」が誤解を招く可能性
- Description: 「人間がやるのは「何を作るか決める」と「できたものを判断する」だけ」という太字表現が、人間のレビュー不要と読める。
- Decision: **Implement Now** — 「だけ」を削除または文脈を前提とした表現に修正。
- Reasoning: 内容ルール「品質担保は人間」に抵触する可能性がある。

#### M-4: 第3弾 — 「worktree」が説明なしで登場
- Description: 「Gitのworktreeでmainに加えてwork1〜work4の5面を開いて」が初見読者に分かりにくい。
- Decision: **Implement Now** — 短い補足を追加。
- Reasoning: 読者前提（Nabledgeを知らない）に対して未説明の用語。

#### M-5: 第1弾 — 「固有知識 × AI」セクションが本文の繰り返し
- Description: パイプラインセクションで説明済みの「スクリプト/AI分担」が再度登場。
- Decision: **Defer** — セクションを既に段落形式に書き直し、新しい視点（「どう格納するか」より「どう見つけるか」）を追加済み。繰り返しは軽微で読者への強調として機能する。

### Low Priority

#### L-1: 第2弾 — `kc-5-20260313` ブランチ名に「v5」が露出
- Decision: **Defer** — URLとして必要な情報。本文での言及は最小化済み。

#### L-2: 第3弾 — TODO コメント5箇所
- Decision: **Defer** — 公開前スクリーンショット追加の意図的なプレースホルダー。

#### L-3: 第2弾 — 421ソース→339知識ファイルの関係が未説明
- Decision: **Defer** — 読者に必須の情報ではない。

## Positive Aspects

- ストーリーアーク一貫性：全3記事が「困りごと→アプローチ→ノウハウ→正直な振り返り」を踏襲
- 個人的な冒頭一言：各記事に著者の近況エピソードあり（シリーズ規則準拠）
- 弱みの正直な記述：testing-frameworkの限界（第2弾）、突貫工事・CFR高止まり（第3弾）
- 数字の正確性：findingsデータ（540ファイル実行）とコストデータ（421ファイル実行）の混同なし、推定値の明記
- 内部バージョン番号：記事本文への「v5」「v6」露出なし（URL/ブランチ名除く）
- シリーズ間参照：各記事が前後の記事を正しく参照

## Files Reviewed

- `docs/articles/01-get-ai-ready-on-nablarch.md` (article)
- `docs/articles/02-knowledge-creator.md` (article)
- `docs/articles/03-build-with-expert.md` (article)
- `docs/articles/review-guidelines.md` (guidelines)
- `docs/articles/review-prompt-nabledge-series.md` (series facts)
