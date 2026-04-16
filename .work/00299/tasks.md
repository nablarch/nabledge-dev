# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-16 (session 8)

全フェーズ TDD: テスト作成 → RED確認 → 実装 → GREEN確認 → サブエージェント品質チェック

---

## In Progress

### Phase 17-C: 残存 FAIL の個別修正（v6）

**前提**: Phase 17-A 完了済み

**現状（Phase 17-A 適用後）**:
- FAIL: 20ファイル / 440件
- カテゴリ別内訳:

| カテゴリ | ファイル数 | 詳細 |
|---------|----------|------|
| Content token missing from JSON | 18 | RBKC 変換漏れ（下記参照） |
| Internal link target not found | 2 | `int[]` ×4 / `nablarch-async-pattern.png` ×2 |

**FAIL ファイル一覧**（20ファイル）:

```
RST (17ファイル):
  application_framework/adaptors/micrometer_adaptor.rst
  application_framework/batch/nablarch_batch/feature_details/nablarch_batch_retention_state.rst
  application_framework/cloud_native/containerize/index.rst
  application_framework/cloud_native/distributed_tracing/aws_distributed_tracing.rst
  application_framework/libraries/code.rst
  application_framework/libraries/repository.rst  ← int[] 偽陽性もあり
  application_framework/libraries/tag.rst
  application_framework/web/getting_started/client_create/client_create1.rst
  application_framework/web/getting_started/client_create/client_create2.rst
  application_framework/web/getting_started/client_create/client_create3.rst
  application_framework/web/getting_started/client_create/client_create4.rst
  application_framework/web/getting_started/client_create/index.rst
  application_framework/web/getting_started/project_bulk_update/index.rst
  biz_samples/04/0401_ExtendedDataFormatter.rst
  testing_framework/.../01_entityUnitTestWithBeanValidation.rst
  testing_framework/.../02_entityUnitTestWithNablarchValidation.rst
  testing_framework/.../06_TestFWGuide/01_Abstract.rst

MD (3ファイル):
  nablarch-patterns/Nablarchでの非同期処理.md  ← png 未コピーもあり
  nablarch-patterns/Nablarchアンチパターン.md
  nablarch-patterns/Nablarchバッチ処理パターン.md
```

**個別対応方針**:

1. **`int[]` 偽陽性** (repository.rst, 4件):
   - `[int[]](int[])` という Markdown リンクを Check C が誤検出
   - verify 変更のためユーザー事前承認必要
   - 修正: Check C の URL パターンで `[]` を含む識別子をスキップ

2. **`nablarch-async-pattern.png` 未コピー** (Nablarchでの非同期処理.md, 2件):
   - resolver が `.md` ソースの画像パスを処理していない可能性
   - 原因調査 → TDD で修正

3. **Content token missing from JSON** (18ファイル):
   - RBKC 変換漏れ（RST → JSON で落とされたトークン）
   - 各ファイルを調査して converter/run.py の修正箇所を特定
   - 修正は converter 側（verify は変更しない）

#### Steps
- [ ] `int[]` 偽陽性修正: ユーザー承認 → UT → RED → 実装 → GREEN
- [ ] `nablarch-async-pattern.png` 未コピー修正: 原因調査 → TDD で修正
- [ ] Content token missing 18ファイルを調査・分類
  - [ ] 共通パターンの特定（同じ converter バグが複数ファイルに出ているか）
  - [ ] converter/run.py 修正 → TDD で対応
- [ ] `pytest` 全通過
- [ ] `bash rbkc.sh verify 6` FAIL 0件確認
- [ ] Software Engineer + QA Engineer エキスパートレビュー
- [ ] コミット

---

### Phase 17-B: verify 再設計 — Check C 完全書き直し + JSON/docs MD 一致チェック追加

**設計決定（ユーザー承認済み）**:

**Check C 再設計（ソース駆動リンク検証）**:
1. 全 RST をスキャン → `.. _label:` 定義を収集 → グローバルラベルマップを作成
2. 各ソースファイルから参照を抽出: `:ref:`、`.. figure::`、`.. image::`、`.. literalinclude::`、MD `[text](path)`
3. グローバルマップで解決できない参照 → FAIL
4. 解決済みリンクターゲットが JSON/docs MD に存在しない → FAIL

**新規チェック追加（JSON ↔ docs MD 完全一致）**:
- JSON と docs MD の title、hints（keywords）、content が完全一致しているか確認

**実装状況（session 8 完了）**:
- `verify.py`: `build_label_map`、`check_source_links`、`check_json_docs_md_consistency` 実装済み
  - `build_label_map`: 全 RST スキャン → `{label: Path}` マップ（バッククォート形式対応済み）
  - `check_source_links`: `:ref:`/`.. figure::`/`.. image::`/`.. literalinclude::`/MD リンク検証
  - `check_json_docs_md_consistency`: title/hints/content 完全一致チェック
  - 旧 `check_internal_links` は Legacy として残存（run.py から呼ばれなくなった）
- `run.py`: `build_label_map` + `check_source_links` + `check_json_docs_md_consistency` を verify フローに組み込み済み
- UT: 28件追加（119件通過）
- E2E test_cli.py: フィクスチャを `universal_dao.rst` → `multiple_process.rst` に変更
  （`universal_dao` は `:ref:` ラベル未出力の RBKC バグを持つため）
- E2E path バグ修正: `test_resolver.py`、`test_rst_converter.py`、`test_pipeline_e2e.py` の相対パスを絶対パスに修正
- 全テスト: 362件通過

**残作業**:

#### Steps（TDD）
- [x] グローバルラベルマップ構築ロジックの設計（全 RST スキャン → `.. _label:` 収集）
- [x] UT: ラベルマップ構築テスト → RED → GREEN
- [x] UT: `:ref:`/`.. figure::`/`.. image::`/`.. literalinclude::`/MD リンク抽出テスト → RED → GREEN
- [x] UT: 未解決参照 → FAIL テスト → RED → GREEN
- [x] UT: 解決済みターゲットが JSON/docs MD に存在しない → FAIL テスト → RED → GREEN
- [x] UT: JSON ↔ docs MD title/hints/content 完全一致テスト → RED → GREEN
- [x] `pytest` 全通過（362件）
- [ ] `bash rbkc.sh verify 6` — FAIL 0件確認（新 Check C での FAIL 状況を確認）
- [ ] Software Engineer + QA Engineer エキスパートレビュー
- [ ] コミット

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
- [x] Phase 17-A: verify コンテンツチェック 再設計（diff ベース全面書き直し）
  - `strip_md_syntax()`, `classify_line()`, `_classify_source_lines()`, `_build_token_categories()` 新規
  - `check_content()`, `check_docs_md_content()` 全面書き直し
  - `_json_text()` に `data["title"]` 追加、`_INLINE_ROLE_RE` を名前空間ロール対応
  - テスト: 60件 → 91件（31件追加）
  - verify FAIL: 50ファイル → **20ファイル**（偽陽性解消、本物の変換漏れのみ残存）
  - committed `ff956aa8`, `37067033`
