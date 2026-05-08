# Tasks: fix: broken link in v6 docs README for Nablarch 6u2 release note

**PR**: #331
**Issue**: #326
**Updated**: 2026-05-08 (rebase onto origin/main 完了)

## In Progress

### 再現検証: docs.py変更がv1.x差分の原因か確認

**目的**: origin/main の状態で create/verify して差分ゼロを確認 → ブランチの修正を入れて create/verify → 想定外差分が出れば修正影響確定

**Steps:**
- [x] PRを origin/main と差分ゼロの状態にした（7ファイルをリバート、PR本文もクリア）
- [x] .lw を最新化した（古い .lw が原因で前回の create に差分が出ていた）
- [x] origin/main 状態で create + verify 全5バージョン (6, 5, 1.4, 1.3, 1.2) 実行 — 全 OK
- [x] `git diff origin/main --stat` で差分確認 → **67ファイル差分あり**（v1.2/1.3/1.4 のみ、v5/v6 は差分なし）
- [x] 差分原因調査結果を記録（.lw更新起因、PR修正とは無関係）
- [DECISION: この差分の扱いを決定してから次のステップへ] v1.x再生成をこのPRに含めるか、Issue #326修正のみにするか
- [ ] ブランチの修正（README.md, docs.py, test_docs.py）を再適用
- [ ] create + verify 全5バージョン 再実行
- [ ] `git diff origin/main --stat` で差分確認 → 想定外差分があれば報告

**調査結果（このセッションで判明）:**

差分の根本原因: `.lw/nab-official/v1.x` に origin/main 作成時点にはなかった RST ファイルが追加されている。

具体的には:
- `fw/architectural_pattern/concept.rst`（新規）が `TOP/top/about_nablarch/concept.rst` と同じ file_id `about-nablarch-concept` に衝突
- disambiguation が発動 → `about-nablarch-about-nablarch-concept.json`（prefix 付き）に変わり、元の `about-nablarch-concept.json` が削除扱いになる
- 同様のパターンが `libraries-validation`、`nablarch-batch-batch` など複数ファイルで発生
- v1.2/1.3/1.4 の `docs/README.md` と `knowledge/index.toon` にも連鎖的に差分

**この差分は `.lw` の更新（外部 repo の内容変化）によるものであり、Issue #326 のブランチ修正（docs.py）とは無関係と考えられる。**

ユーザーへの確認事項:
1. この差分（v1.x 知識ファイルの再生成）をこの PR に含めてよいか？
2. それとも今は無視して Issue #326 の修正のみをこの PR でリリースするか？

## Done

- [x] PRを origin/main と差分ゼロの状態にした（7ファイルをリバート）
- [x] .lw を最新化した
- [x] origin/main へのリベース完了（20コミット適用）
