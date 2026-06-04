# Tasks: Add Javadoc knowledge to nabledge skills

**PR**: #365
**Issue**: #363
**Updated**: 2026-06-04 (session 24 saved)

## Rules（全タスク共通）

- 1コミット = 1タスク
- 推測せず事実ベースで作業・判断する（実物・全件を確認し、確認範囲を明示する）
- RBKC の create/verify を変更する場合は実装前に設計書を更新してユーザーに確認する
- 各タスクは TDD 順（RED → GREEN）。1タスク=1コミット
- 1タスク完了後に必ず `python -m pytest tests/ut/ -q`（`tools/rbkc/` で実行）を行い全 GREEN を確認してからコミットする
- 統合 verify を変化させるタスクは、完了時に検知ゲートで FAIL 集合の差分を確認する

## 検知設計

QL1（2-C）有効化後、パイプライン（2-E〜2-I）完成まで `rbkc.sh verify` は意図的に FAIL する。本物の FAIL を見落とさないため:
1. 2-C2 で extdoc FAIL を FQCN 全件 + 他カテゴリ0件で `.work/00363/verify-baseline.md` に固定
2. 2-J で FAIL 集合を取得し、照合A（ベースラインの extdoc 全件消滅）+ 照合B（ベースライン外0件）で判定

設計書: `tools/rbkc/docs/rbkc-converter-design.md` §5-1 / §5-2、`rbkc-verify-quality-design.md` §3-2-3 / §3-3

---

## In Progress

### Task 6: 差分チェック + PR レビュー依頼
- **前提**: Task 5 完了
- **完了条件**: 全変更差分が想定どおりと記録、Expert review 通過、PR 更新
- [ ] `git diff main...HEAD --stat` で変更ファイルを全件確認
- [ ] 想定外変更がないかをチェックし `.work/00363/diff-check.md` に記録
- [ ] ユーザーに確認依頼
- [ ] Expert review（Software Engineer + QA Engineer）
- [ ] PR を更新

---

## Done

- [x] `.work/00363/tasks.md` と `notes.md` 作成 — `521ac200d`
- [x] PR #365 作成
- [x] jar ツール動作確認・設計方針合意
- [x] Task 1: 設計書更新 → ユーザー承認 — `12053d029` / `f771ecbfa` / `fb631766c`
- [x] 実装コミット（session 3-5）を revert — `f2dd8fc2a`
- [x] Task 2-A: emit_javadoc_link / JAVADOC_LINK_RE — `d019f2f4d`
- [x] Task 2-B: QO4 javadoc 除外 — `ae830a3b1`
- [x] Task 2-C: QL1 extdoc チェック — `c053dab00` / `6fe6646dc`
- [x] Task 2-C2: QL1 ベースライン記録 (813 FQCNs) — `5eeb73d89`
- [x] Task 2-D: jar 復元 — `c9d6a66a0`
- [x] Task 2-E: javadoc.py 実装 — `7f37cdb36`
- [x] Task 2-G: rst_ast_visitor extdoc 内部リンク化 — `426046d34`
- [x] Task 2-H: rst_ast_visitor javadoc_url 外部リンク化 — `da4ce9b21`
- [x] Task 2-F: run.py javadoc_generate 配線 — `0886687ba`
- [x] Task 2-I: docs.py + index.py javadoc/ 除外 — `5742f62e2`
- [x] Task 2-J-pre: verify QC1/QC2 対称化（_build_javadoc_map） — `4ee4e4571`
- [x] Task 2-J: 統合 verify 確認（QC1/QC2=0、照合B OK） — `1eeb96e89` / `1fb952523` / `cb56a0602`
- [x] Task 2-J-follow: QL1 254件対処 — 設計書追記 `b0c4f3b11` / 共通モジュール実装 `d1fa3c75d` / v6 knowledge 再生成 `a9fd984bf`
- [x] リンク拡張子規約是正 設計書更新 — verify/converter 設計書改訂（承認済）`77761ce5b`
- [x] Task 3-A: test_linkfmt.py に .json 出力テスト追加（RED） — `061507687`
- [x] Task 3-B: linkfmt.py を .json 出力に変更（GREEN）+ 波及テスト修正 — `524f90a22` / `a4cf9383d`
- [x] Task 3-C: test_docs.py に .json→.md 変換テスト追加（RED） — `bbc34b7d0`
- [x] Task 3-D: docs.py に .json→.md 変換追加（GREEN） — `2bcab2f1d`
- [x] Task 3-E: QO2 正規化テスト RED+GREEN、QO1 section title 修正 — `1249cc588` / `5dffd297d` / `4e43c66c7`
- [x] Task 3-E（続き）: v6 docs 再生成 + 新規 knowledge コミット、全バージョン verify 新規FAIL=0 確認 — `0b2508a2e` / `140b6459f`
- [x] Task 3: semantic-search に Step 3b 追加（v6/v5）— `6bd3dea23`
- [x] Task 4: ベンチマークシナリオ追加（qa-16/17/18）— `e9f4adbff`
- [x] Task 5: v6 ベンチマーク 3 run + report.md 作成 — `e527ee219` / Issue #368 作成
