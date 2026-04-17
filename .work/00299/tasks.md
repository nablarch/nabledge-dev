# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-17 (session 11)

全フェーズ TDD: テスト作成 → RED確認 → 実装 → GREEN確認 → サブエージェント品質チェック

---

## In Progress

### Phase V0: RBKC hints — 既存ヒントをそのまま持ち越す

**背景**: 現在 hints.py は KC キャッシュから hints を生成しているが、既存の知識ファイルにはすでに質の高い hints が存在する。新 verify でも hints 完全性（QC6）をチェックするため、既存 hints を RBKC 出力に確実に引き継ぐ必要がある。

**方針**: `rbkc create` の各フォーマット変換パスで、既存知識ファイルが存在する場合はそのセクションの `hints` を出力 JSON にそのままコピーする。

**Steps:**
- [ ] 既存知識ファイルの hints 構造を調査（どのフォーマットで hints が存在するか確認）
- [ ] `run.py` または converters の hints 引き継ぎロジックを TDD で実装
  - [ ] テスト作成 → RED 確認
  - [ ] 実装 → GREEN 確認
  - [ ] 全テスト通過確認（`pytest`）
- [ ] Software Engineer + QA Engineer エキスパートレビュー
- [ ] コミット

---

### Phase V1: 既存 verify を削除してプッシュ

**背景**: 現在の `verify.py` と `tests/ut/test_verify.py` は旧設計（Check A/B/C/D/E/F/H）ベースで書かれており、新設計（QC1–QC6 / QL1–QL2 / QO1–QO5）と対応が取れていない。作り直しのためまず削除する。

**Steps:**
- [ ] `tools/rbkc/scripts/verify.py` の内容を削除（空ファイルまたはスタブに置き換え）
- [ ] `tools/rbkc/tests/ut/test_verify.py` を削除
- [ ] `verify.py` を参照している他モジュール（`run.py` 等）の import エラーがないことを確認
- [ ] `pytest` 実行 — verify テスト以外が全通過することを確認
- [ ] コミット → プッシュ

---

### Phase V2: verify 実装計画 → エキスパートレビュー → ユーザー確認

**背景**: `rbkc-verify-quality-design.md` の各観点（QC1–QC6 / QL1–QL2 / QO1–QO5）を TDD で実装するための詳細計画を立て、実施前にレビューを受ける。

**Steps:**
- [ ] `rbkc-verify-quality-design.md` を読み込み、実装サブフェーズ（V2-1, V2-2, ...）に分解して計画を作成
  - 各サブフェーズに: 対象観点、テストケース案、実装方針を記載
  - 依存関係と実装順序を明示する
- [ ] QA Engineer エキスパートレビュー（テストケース網羅性・設計妥当性）
- [ ] Software Engineer エキスパートレビュー（アーキテクチャ・実装可能性）

---

### Phase V3: verify TDD 実装

**前提**: Phase V2 でユーザー承認済みの計画に従って実施。

**実装観点（`rbkc-verify-quality-design.md` の ❌ 項目）**:

| ID | 観点 | RST | MD | Excel |
|----|------|:---:|:---:|:----:|
| QC1 | 完全性 | ❌ | ❌ | ❌ |
| QC2 | 正確性 | ❌ | ❌ | ❌ |
| QC3 | 非重複性 | ❌ | ❌ | ❌ |
| QC4 | 配置正確性 | ❌ | ❌ | — |
| QC5 | 形式純粋性 | ❌ | ❌ | — |
| QC6 | hints 完全性 | ❌ | ❌ | ❌ |
| QL1 | 内部リンクの正確性 | ❌ | ❌ | — |
| QL2 | 外部リンクの一致 | ❌ | ❌ | — |
| QO3 | 目次ページの除外 | ❌ | — | — |
| QO5 | docs MD 整合性（content 完全一致） | ❌ | ❌ | ❌ |

**Steps（各サブフェーズ共通）:**
- [ ] テスト作成 → RED 確認
- [ ] 実装 → GREEN 確認
- [ ] 全テスト通過確認（`pytest`）
- [ ] Software Engineer + QA Engineer エキスパートレビュー
- [ ] コミット

---

### Phase V4: v6 で生成 + 検証 → verify 動作確認

**前提**: Phase V3 完了

**Steps:**
- [ ] `bash rbkc.sh create 6` — v6 知識ファイルを生成
- [ ] `bash rbkc.sh verify 6` — FAIL 件数を確認・記録
- [ ] FAIL が出た場合: 原因分析 → RBKC 側（verify ではなく converter/run.py 等）を修正
  - 各 FAIL について修正を TDD で実施
  - 修正後 verify を再実行して FAIL 0件になるまで繰り返す
- [ ] FAIL 0件確認 → コミット

---

### Phase 18: 統合検証 — v6 完了

**前提**: Phase 17-C 完了（`rbkc.sh verify 6` FAIL 0件）+ Phase 17-B 判断済み

**Steps:**
- [ ] nabledge-test v6 実行 — ベースライン比で劣化なし確認
- [ ] 生成済み知識ファイル（knowledge/, docs/, assets/）をコミット

---

### Phase 19: 統合検証 — v5

**前提**: Phase 18 完了後

**Steps:**
- [ ] `bash rbkc.sh create 5` → `bash rbkc.sh verify 5` — FAIL 0件
  - FAIL が出た場合: 分析 → ユーザー報告 → 承認後修正 → 再 verify
- [ ] nabledge-test v5 — 劣化なし確認
- [ ] コミット

---

### Phase 20: 統合検証 — v1.4 / v1.3 / v1.2

**前提**: Phase 19 完了後

**Steps:**
- [ ] `bash rbkc.sh create 1.4` → `bash rbkc.sh verify 1.4` — FAIL 0件
- [ ] `bash rbkc.sh create 1.3` → `bash rbkc.sh verify 1.3` — FAIL 0件
- [ ] `bash rbkc.sh create 1.2` → `bash rbkc.sh verify 1.2` — FAIL 0件
  - 各バージョンで FAIL が出た場合: 分析 → 報告 → 承認 → 修正 → 再 verify
- [ ] nabledge-test v1.4 / v1.3 / v1.2 — 劣化なし確認
- [ ] コミット（全3バージョン）

---

## Done

- [x] Phase 17-R: verify 品質保証設計ドキュメント作成・レビュー完了
  - `tools/rbkc/docs/rbkc-verify-quality-design.md` を新規作成（旧 requirement-and-approach.md を全面リファクタリング）
  - QA エキスパートレビュー2回実施、指摘事項をすべて反映
  - 最終状態: QC1–QC6 / QL1–QL2 / QO1–QO5 の全観点定義済み、検証方法・マトリクス整合済み
  - committed `d020efd2` 〜 `2464a55c`（本セッション分）
  - **次のステップ**: 本ドキュメントを仕様として Phase 17-C / 17-B / 18 以降の実装を進める

- [x] Phase 1: KC cache → hints mapping (`scripts/hints.py`) — committed `f78304b4`
- [x] Phase 2: RST converter with full directive support — committed `5913ff6e`, `1b62c4c4`, `9cbbc729`
- [x] Phase 3: Hints extraction Stage 1 + Stage 2 merge — committed `ac294cdb`
- [x] Gap fill: Phase 2 test修正 + Phase 1/3 E2Eテスト追加 — committed `010d0c2f`
- [x] Phase 4: Cross-reference resolution + asset copying — committed `9336f900`, `87654126`
- [x] Phase 5: MD converter — committed `232df686`
- [x] Phase 6: Excel converters — committed `edce71eb`
- [x] Phase 7: Index + browsable docs generation — committed `dc019759`
- [x] Phase 8: CLI + create/update/delete/verify operations — committed `5baf7a6d`
- [x] Phase 9: v1.x固有ディレクティブ対応 — committed `bc632d0f`
- [x] Phase 10: コンバータ修正 (10-1〜10-6) — committed `54fe3ef8`, `d5a6961d`, `cd856500`, `d2303716`, `7eac70f6`, `10b239b1`
- [x] Phase 11: verify 完全チェック化 — committed `6c664a59` ※Phase 12で書き直し済み
- [x] Phase 12: verify 完全書き直し (B1/B2/B3修正) — committed `1eff2740`
- [x] Phase 13: create pipeline 完全修正 (B4修正) — committed `e85488cb`
- [x] Phase 14: classify 出力パス衝突修正 (B5修正) — committed `b6a4a630`
- [x] Phase 15: converter/verify URL バグ修正 (B6/B7修正) — committed `63ac0ec9`
- [x] Phase 16: toctree-only index.rst token coverage 修正 (B8修正) — committed `37d6e547`
- [x] docs.py: assets/ リンクを docs MD の位置から相対解決 — committed `008e8420`
  - → verify FAIL: 351件 → 50件（docs MD assets link 301件解消）
- [x] Rules整理: development.md追加、work-log/rbkc/pr.md更新 — committed `aa08f489`
- [x] Phase 17-R: verify 品質保証設計ドキュメント作成・レビュー完了（旧 Phase 17-B/17-C/17-A の verify コードは新設計で作り直し）
  - `tools/rbkc/docs/rbkc-verify-quality-design.md` を新規作成（旧 requirement-and-approach.md を全面リファクタリング）
  - QA エキスパートレビュー2回実施、指摘事項をすべて反映
  - 最終状態: QC1–QC6 / QL1–QL2 / QO1–QO5 の全観点定義済み
  - **既存 verify.py（Phase 11〜17-A で実装済み）は Phase V1 で削除・作り直しへ**
  - committed `d020efd2` 〜 `2464a55c`
