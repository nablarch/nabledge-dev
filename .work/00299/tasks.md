# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-20 (session 19)

全フェーズ TDD: テスト作成 → RED確認 → 実装 → GREEN確認 → サブエージェント品質チェック

## verify 実装ルール（絶対遵守）

- **設計書通りに実装する**: `tools/rbkc/docs/rbkc-verify-quality-design.md` が唯一の実装仕様。問題・疑問が生じたらユーザーに相談し、勝手に判断して実装を変更しない
- **設計書 → 実装の順序**: ユーザーと合意して verify の内容を見直す場合は、必ず設計書を更新してから実装を進める。設計書と実装の整合は常に維持する
- **マトリクスの ✅ 条件**: 実装が完了し、かつ実際の RBKC 出力に対して動作を確認した時点で初めて ✅ にする

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

**完了済みサブフェーズ**:
- [x] V2-1 QO5（docs MD content 完全一致）— committed `a0c7abf1`
- [x] V2-2 QC5（形式純粋性）— committed `a0c7abf1`
- [x] V2-3 QC6（hints 完全性）— committed `a0c7abf1`（SE + QA エキスパートレビュー実施・修正適用済み）
- [x] E2E テストスキップ修正 — committed `91796838`（322 passed, 2 skipped）
- [x] V2-5 QC1–QC3（RST/MD delete アルゴリズム）— committed `13d3b6bb`
- [x] V2-5b テスト補完＋バグ修正 — committed `d35e55f7`（336 passed, 2 skipped）
  - SE + QA エキスパートレビュー実施・全指摘修正済み

**完了済みサブフェーズ（続き）**:
- [x] V2-6 QC4（配置正確性）— committed `131bce43`（SE + QA エキスパートレビュー実施・全指摘修正適用済み）
- [x] V2-7 QO3（目次ページ除外）— **実装不要**（設計書の注記: QC1/QC2のスコープで扱う、独立した品質観点を設けない）
- [x] V2-8 QL2（外部URL一致）— committed `43fb4d3f`（SE + QA エキスパートレビュー実施・全指摘修正適用済み）
- [x] V2-9 QL1（内部リンク正確性）— committed `2b421497`（SE + QA エキスパートレビュー実施・全指摘修正適用済み）

**次に着手するサブフェーズ:**

| ID | 対象 | フォーマット | 依存 |
|----|------|------------|------|
| V2-4-pre | Excel mapping 追加 + scan 拡張 | 設定・scan.py | なし |
| V2-4 | QC1–QC3（Excel sequential-delete） | Excel | V2-4-pre |

**設計書更新状況（session 19）**:
- `rbkc-verify-quality-design.md` の Excel 検証セクションを集合比較 → sequential-delete に更新済み（未コミット）
- xls（`.xlsx` と `.xls` 両対応）の記述追加済み（未コミット）
- 旧テスト `TestVerifyFileExcelQC` のクラス見出しコメントを更新済み（旧実装はまだ残存、TDD作り直し未着手）

**V2-4-pre タスク詳細（V2-4 の前提）:**

スコープ確定（2026-04-20 調査済み）:

| バージョン | ファイル | ディレクトリ | 備考 |
|-----------|---------|------------|------|
| v6 | `Nablarch機能のセキュリティ対応表.xlsx` | `nablarch-system-development-guide/` | mapping済み |
| v6 | `*-releasenote.xlsx` | `nablarch-document/ja/releases/` | mapping済み |
| v5 | `Nablarch機能のセキュリティ対応表.xlsx` | `nablarch-system-development-guide/` | mapping済み |
| v5 | `*-releasenote.xlsx` (u6–u26) | `nablarch-document/ja/releases/` | mapping済み |
| v5 | `nablarch5-releasenote.xlsx`, `nablarch5u1–u5-releasenote.xlsx` | `all-releasenote/nablarch-5-all-releasenote/` | scan対象外→要追加 |
| v1.4 | `nablarch-1.4.*-releasenote.xlsx` (14件) | `all-releasenote/nablarch-1.4-all-releasenote/` | mapping空+scan対象外→要追加 |
| v1.3 | `nablarch-1.3.2–1.3.7-releasenote.xlsx` (6件) | `all-releasenote/nablarch-1.3-all-releasenote/` | mapping空+scan対象外→要追加 |
| v1.3 | `*-releasenote-detail.xls` (1.3.0, 1.3.1) | `all-releasenote/nablarch-1.3-all-releasenote/1.3.0/, 1.3.1/` | xls、mapping空+scan対象外→要追加 |
| v1.2 | `nablarch-1.2.3–1.2.8-releasenote.xlsx` (6件) | `all-releasenote/nablarch-1.2-all-releasenote/` | mapping空+scan対象外→要追加 |
| v1.2 | `*-releasenote-detail.xls` (1.2.0, 1.2.1, 1.2.2) | `all-releasenote/nablarch-1.2-all-releasenote/1.2.0/, 1.2.1/, 1.2.2/` | xls、mapping空+scan対象外→要追加 |

作業内容:
- [ ] `scan.py` の `_source_roots` に `all-releasenote/nablarch-{version}-all-releasenote/` を各バージョンのルートとして追加
- [ ] `scan.py` の xlsx スキャンに `.xls` 拡張子も追加（xls対応）
- [ ] `tools/rbkc/mappings/v1.4.json` に xlsx_patterns 追加（`-releasenote.xlsx` endswith）
- [ ] `tools/rbkc/mappings/v1.3.json` に xlsx_patterns 追加（`-releasenote.xlsx`, `-releasenote-detail.xls` 対応）
- [ ] `tools/rbkc/mappings/v1.2.json` に xlsx_patterns 追加（`-releasenote.xlsx`, `-releasenote-detail.xls` 対応）
- [ ] `tools/rbkc/mappings/v5.json` に all-releasenote スキャン対応（`-releasenote.xlsx` pattern は既存、ディレクトリ追加のみ）
- [ ] xls コンバータ実装（`xlsx_releasenote.py` の xls 対応、または専用コンバータ）
- [ ] TDD: テスト → RED → 実装 → GREEN → 全テスト通過 → エキスパートレビュー

**開発ルール追記（完了済み）:**
- [x] `.claude/rules/development.md` にテスト作成観点（バグ露呈ケース・エッジケース必須）を追記

**Steps（各サブフェーズ共通）:**
- [ ] テスト作成 → RED 確認
- [ ] 実装 → GREEN 確認
- [ ] 全テスト通過確認（`pytest`）
- [ ] Software Engineer + QA Engineer エキスパートレビュー
- [ ] コミット

---

### Phase V2-4-post: Excel コンバーター修正（verify 通過のため）

**前提**: V2-4（Excel QC1–QC3 verify 実装）完了後に着手

**背景**: V2-4 の verify 実装で「Excel のあるべき変換ルール」が確定する。verify が通るように生成側（Excel コンバーター）を修正する。

**確認観点（V2-4 完了時に判明する）:**

- [ ] `xlsx_releasenote.py`: section title がソースセル値から構成されているか（`No.{no} {title_text}` 形式でセル値を使用しているか）
- [ ] `xlsx_releasenote.py`: section content に含まれる Markdown 構文（`**リリース区分**:` 等）が QC2 に引っかからないか
- [ ] `xlsx_security.py`: section title がソースセル値から構成されているか（`{no}. {name}` 形式でセル値を使用しているか）
- [ ] `xlsx_security.py`: section content に含まれる Markdown テーブル記号・強調記号が QC2 に引っかからないか
- [ ] xls 対応コンバーター: 同様の確認

**Steps:**
- [ ] `bash rbkc.sh verify 6` を実行して Excel 由来ファイルの FAIL を確認
- [ ] 各 FAIL について原因を分析（コンバーターのバグか、設計書の許容構文要素リスト漏れか）
- [ ] コンバーター修正が必要な場合: TDD で修正（テスト → RED → 実装 → GREEN）
- [ ] 設計書の許容構文要素リスト追加が必要な場合: ユーザー確認 → 設計書更新 → 実装
- [ ] 全 FAIL 解消確認

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

- [x] Phase V2-1/V2-2/V2-3: QO5 / QC5 / QC6 verify 実装 — committed `a0c7abf1`
  - QO5: docs MD content 完全一致（assets/ リンク含むセクションはスキップ）
  - QC5: RST/MD 形式純粋性（Java ジェネリクス false positive 排除済み）
  - QC6: hints 完全性（前回生成 hints の欠落検出）
  - テスト 34 本追加（計 288 passed, 23 skipped）

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
