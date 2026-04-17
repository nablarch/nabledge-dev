# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-17 (session 12)

全フェーズ TDD: テスト作成 → RED確認 → 実装 → GREEN確認 → サブエージェント品質チェック

---

## In Progress

### Phase V3: verify TDD 実装

**前提**: V0/V1/V2 完了済み（下記 Done 参照）

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

**サブフェーズ計画（V2 で確定済み）**:

| ID | 対象 | フォーマット | 依存 |
|----|------|------------|------|
| V2-1 | QO5（docs MD content 完全一致） | RST, MD, Excel | なし |
| V2-2 | QC5（形式純粋性） | RST, MD | なし |
| V2-3 | QC6（hints 完全性） | RST, MD, Excel | なし |
| V2-4 | QC1–QC3（Excel 集合比較） | Excel | なし |
| V2-5 | QC1–QC3（RST/MD 先頭からdelete） | RST, MD | なし |
| V2-6 | QC4 + QC1–QC3 マルチセクション | RST, MD | V2-5 |
| V2-7 | QO3（目次ページ除外） | RST | なし |
| V2-8 | QL2（外部URL一致） | RST, MD | なし |
| V2-9 | QL1（内部リンク正確性） | RST, MD | V2-8 |

**アルゴリズム確定事項（V2 議論済み）**:
- QC1–QC3/QC4 の delete algorithm: JSON テキストを先頭から順に検索・削除。先頭からなので重複文字列も問題なし。
- 削除後の残存 non-syntax テキスト → QC1（欠落）
- 削除できなかった JSON テキスト → QC2（捏造）/QC3（重複）
- QC4（配置正確性）は別途セクション境界追跡で実装

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

- [x] Phase V0: hints carry-over 実装 — committed `d155c92e`
  - `load_existing_hints(output_dir)` + `lookup_hints_with_fallback()` を run.py に追加
  - `create()` が rmtree する前に既存 RBKC 形式ファイルから hints を保存し新規生成時に引き継ぐ
  - `update()` も同様に carry-over 対応
  - テスト: 17件追加（TestLoadExistingHints）

- [x] Phase V1: 旧 verify 削除・スタブ化 — committed `2727facc`
  - `verify.py` を空スタブに置き換え（run.py の import は維持）
  - `test_verify.py` 削除
  - `test_cli.py` の verify テスト2件を skip マーク
  - pytest: 254 passed, 23 skipped

- [x] Phase V2: verify 実装計画確定
  - サブフェーズ V2-1〜V2-9 を設計（QA/SE エキスパートレビュー実施）
  - delete algorithm の方針確定: 先頭から順に削除するだけ→重複文字列問題なし
  - 計画は In Progress の Phase V3 に記載済み

- [x] Phase 17-R: verify 品質保証設計ドキュメント作成・レビュー完了（旧 Phase 17-B/17-C/17-A の verify コードは新設計で作り直し）
  - `tools/rbkc/docs/rbkc-verify-quality-design.md` を新規作成（旧 requirement-and-approach.md を全面リファクタリング）
  - QA エキスパートレビュー2回実施、指摘事項をすべて反映
  - 最終状態: QC1–QC6 / QL1–QL2 / QO1–QO5 の全観点定義済み
  - committed `d020efd2` 〜 `2464a55c`

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
