# Tasks: docs: add knowledge article infrastructure and 3 initial articles

**PR**: #246
**Issue**: #243
**Updated**: 2026-03-26

## Not Started

### Apply self-check improvements

ユーザーとの合意が必要な項目と即対応可能な項目が混在。
セルフチェック結果の詳細は `notes.md` 参照。

**Steps:**

**🔴 即対応（ユーザー合意不要）:**
- [ ] 第1弾: `index.toon` のエントリ数を296→295に修正（本文2箇所）
- [ ] 第2弾: フェーズ数・AI使用数を実装と整合させる（本文とMermaid図）
- [ ] 第2弾: `pie title Nabledge v6（スキル）` の「v6」を削除

**🟡 ユーザー判断が必要:**
- [ ] 第1弾: 「固有知識 × AI」セクションの太字リスト → 著者に再構成の意向を確認
- [ ] 第1弾: AI擬人化2箇所の修正方針を確認
- [ ] 第3弾: 「最初のコミット」セクションの太字リスト → 著者に再構成の意向を確認
- [ ] 第3弾: 37%→38% の修正（計算誤り、即対応可能だが著者確認推奨）

**Context:**
- セルフチェック結果: `.pr/00243/notes.md`
- 第2弾の「private repo」指摘は誤り（nabledge-devはpublic）— 対応不要
- 記事ファイル: `docs/articles/01-get-ai-ready-on-nablarch.md` 〜 `03-build-with-expert.md`

### Expert review（Technical Writer）

**前提**: 上記の改善適用後に実施。

**Steps:**
- [ ] `docs/articles/` の変更ファイルを対象に Technical Writer ペルソナでレビュー
- [ ] `.pr/00243/review-by-technical-writer.md` に結果を保存
- [ ] Developer agent が改善提案を評価
- [ ] 承認された改善を適用

### PR review request

**Steps:**
- [ ] PR本文の Expert Review セクションにレビューファイルへのリンクを追加
- [ ] Success Criteria Check を更新（全項目 ✅ Met になること）
- [ ] ユーザーにレビュー依頼

## Done

- [x] `docs/articles/` ディレクトリ作成
- [x] 記事作成ワークフロー `.claude/rules/articles.md` 作成
- [x] レビューガイドライン `docs/articles/review-guidelines.md` 配置
- [x] シリーズ固有レビュープロンプト `docs/articles/review-prompt-nabledge-series.md` 配置
- [x] 初回3記事を `docs/articles/` に配置
- [x] 3記事のセルフチェック実施・改善案を `notes.md` に出力
- [x] `.claude/rules/pr.md` 作成
- [x] `.claude/rules/review-feedback.md` 作成
- [x] `.claude/rules/commit.md` 作成
- [x] `/re` コマンド作成
