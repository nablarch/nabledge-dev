# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-20 (session 23)

全フェーズ TDD: テスト作成 → RED確認 → 実装 → GREEN確認 → サブエージェント品質チェック

## verify 実装ルール（絶対遵守）

- **設計書通りに実装する**: `tools/rbkc/docs/rbkc-verify-quality-design.md` が唯一の実装仕様。問題・疑問が生じたらユーザーに相談し、勝手に判断して実装を変更しない
- **設計書 → 実装の順序**: ユーザーと合意して verify の内容を見直す場合は、必ず設計書を更新してから実装を進める。設計書と実装の整合は常に維持する
- **マトリクスの ✅ 条件**: 実装が完了し、かつ実際の RBKC 出力に対して動作を確認した時点で初めて ✅ にする

---

## In Progress

以下 3 フェーズは独立して先行実施可能（V4 より前に全て完了させる）。

---

### Phase V-skip: verify のスキップ全量確認・修正

**目的**: verify が JSON/MD ファイル未存在を見逃さず、必ず FAIL を報告すること。

**判明している違反箇所（run.py）**:
- line 409: `json_path.exists() else {}` — JSON 未存在をサイレントに空 dict で続行
- line 430: `if docs_md_path.exists():` — docs MD 未存在を検証せずスキップ

**Steps:**
- [ ] `run.py` verify() の上記2箇所を FAIL 報告に修正
- [ ] `verify/verify.py` 内の `continue` / 空リスト返却パターンを全量確認し、正当でないものを FAIL 報告に修正
  - 正当なスキップ例: `no_knowledge_content=True` ファイルの特定チェック除外
  - 違反例: ファイル未存在・パース失敗の黙認
- [ ] pytest GREEN 確認
- [ ] コミット

---

### Phase V-hints: ヒント全量確認 → KC ファイル削除

**目的**: KC キャッシュからのヒント抽出が全ファイルをカバーしていることを確認してから、knowledge/ の KC 形式ファイルを削除する。

**背景**: knowledge/ には KC 形式（sections が dict）のファイルが残存。`rbkc create` 前に削除する必要があるが、ヒントの引き継ぎが確実でないと品質が下がる。

**Steps:**
- [ ] `build_hints_index` の出力ファイル一覧と KC キャッシュ（`.cache/v6/catalog.json`）の全 file_id を比較
  - カバー率を確認。100% でなければ原因調査・修正
- [ ] knowledge/ 内の KC 形式ファイル（sections が dict）をリストアップして削除
- [ ] docs/ 内の KC 由来 MD ファイルを削除（knowledge/ に対応するもの）
- [ ] コミット・push

---

### Phase V2-4-post: コンバーター修正（QC1・QL1 残件）

**目的**: `rbkc verify 6` が FAIL 0件になるよう、残りのコンバーターバグを修正する。

**完了済み（このフェーズ内）**:
- [x] ディレクトリ構造リファクタリング（scripts/common/, create/, verify/）— `139e18e4`
- [x] create 側テスト削除・スキップ禁止ルール追加 — `2f5993ae`
- [x] `xlsx_security.py` 固定ヘッダー除去（QC2 解消）— `514e81a8`
- [x] 旧 scripts/ パス削除 — `514e81a8`

**残件（QC1・QL1）**:
- [ ] 不要テスト削除（ルール変更に伴う整理）
  - `tests/ut/test_run.py` の create-side ロジックテスト（`TestLoadExistingHints` 等）を削除
  - `tests/e2e/test_cli.py` の `TestCreate` / `TestUpdate` / `TestDelete` クラスを削除
  - CLI 層テスト（verify が pass するかどうかを確認する `TestVerify` クラス）は残す
  - 1 failed テストが現在あるので先に修正してから削除
- [ ] `xlsx_releasenote.py` ヘッダー行修正（QC1 解消）
  - 根本原因: タイトル(`■`除去)・説明行・ヘッダー行・Col B/H/I/J/K/L/N・全シートが未収録
  - 修正: 全シートの全セル値を JSON に含める（セクション構造は現状維持）
- [ ] RST コンバーター `:ref:` 解決修正（QL1 解消）
  - `convert(text, file_id, label_map=None)` に引数追加
  - `:ref:\`label\`` → `label_map[label]` のセクションタイトルに解決
  - `run.py` の create パスで `build_label_map` を呼んで渡す
- [ ] SE + QA エキスパートレビュー
- [ ] コミット

---

### Phase V4: v6 create + verify FAIL 0件

**前提**: V-skip・V-hints・V2-4-post の全残件完了後

**Steps:**
- [ ] `bash rbkc.sh create 6` — RBKC 形式で v6 知識ファイルを全量生成
- [ ] `bash rbkc.sh verify 6` — FAIL 件数を確認・記録
- [ ] FAIL が出た場合: 原因分析 → RBKC 側（converter/run.py 等）を修正（TDD）→ 再 verify
- [ ] FAIL 0件確認 → コミット

---

### Phase 18: 統合検証 — v6 完了

**前提**: Phase V4 完了

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
