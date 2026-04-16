# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-16 (session 6)

全フェーズ TDD: テスト作成 → RED確認 → 実装 → GREEN確認 → サブエージェント品質チェック

---

## In Progress

### Phase 17-A: verify コンテンツチェック 再設計（全バージョン対象）

**背景**:
現在の実装は「RST トークンの 70% が JSON に存在するか」を判定。
RST syntax 要素（`:maxdepth:`、toctree パス等）が混入して偽陽性が発生。
RBKC は変換ツール（要約不可）なのでコンテンツは 100% JSON に存在すべき。
→ 根本的にアプローチが違うため全面書き直し。

**新方式（diff ベース）**:
```
1. JSON（MD形式削除）のコンテンツトークン集合を作る
2. RST トークン − JSON コンテンツトークン = 残りトークン
3. 残りトークンの各トークンについて:
     RST 上の全出現行が RST syntax 行のみ → OK（expected: toctree, directive 等）
     コンテンツ行に出現 → FAIL（RBKC の変換漏れ）
```

**実装関数（新規）**:
- `strip_md_syntax(text)` — JSON の MD 形式（`##`, `|`, `-`, `**` 等）を削除
- `classify_line(line) → (category, effective_text)` — RST 行を分類
  - syntax 行: section_decoration / rst_label / directive_decl / directive_option / toctree_entry
  - content 行: それ以外（インラインロールは display text のみ保持）
- `check_content()` — 全面書き直し（既存実装は全廃）
- `_json_text()` — `data["title"]` を含めるよう修正

**strip_role_syntax の注意点**:
- `:ref:`display<target>`` → `display`（display text はコンテンツ）
- `:ref:`target`` （`<>` なし）→ `target` をそのまま保持（plain text はコンテンツ）
- `:role:`text`` → `text`（同上）

**全バージョン全量調査結果**（新方式仮適用、全 1,477 RST ファイル）:
| バージョン | RST files | 残りトークン（全量） | うち RBKC 変換漏れ |
|---|---|---|---|
| v6 | 333 | 14,973 | 調査済み（16 files に集中） |
| v5 | 430 | 52,250 | 調査済み（91 files） |
| v1.4 | 121 | 5,824 | 調査済み（15 files） |
| v1.3 | 300 | 26,304 | 調査済み（107 files） |
| v1.2 | 293 | 26,263 | 調査済み（109 files） |

注: RBKC 変換漏れは verify 修正後に別フェーズで修正する。

#### Steps（TDD）
- [ ] ユーザー承認（verify 変更のため必須）
- [ ] UT: `strip_md_syntax()` テスト → RED → 実装 → GREEN
- [ ] UT: `classify_line()` テスト → RED → 実装 → GREEN
- [ ] UT: `check_content()` diff ベース判定テスト → RED → 実装 → GREEN
- [ ] UT: `_json_text()` title 追加テスト → RED → 実装 → GREEN
- [ ] `pytest` 全通過
- [ ] 全バージョン verify 実行 — 現在の偽陽性 FAIL が解消、RBKC 変換漏れ FAIL は残ること確認
- [ ] Software Engineer + QA Engineer エキスパートレビュー
- [ ] コミット

---

### Phase 17-B: verify 再設計 — Phase 2 (リンク検証)

**背景**: 現在の Check C は JSON 内 Markdown リンクの物理存在確認のみ。
toctree が指すページ、外部 URL、アセット、内部参照（:ref:）の「正解データ」を作成し
漏れ・重複・間違いを検出できるようにする。

**前提**: Phase 17-A 完了後

#### 正解データ（RST から収集・解決して作成）

```
共通フィールド:
  type: page | url | asset | ref
  source_page_title: リンクのあるページタイトル
  source_section:    リンクのあるセクション（JSON照合に必要）
  label:             リンクラベルテキスト

① ページリンク（toctree エントリ）
  target_page_title: リンク先 RST の title
  target_section:    null（ページ全体）

② 外部 URL
  url:               https://...
  target_page_title: null（外部）

③ アセット（画像・ファイル）
  asset_path_rst:    RST 内の相対パス
  asset_path_out:    knowledge/assets/ 内の出力パス
  physical_path:     解決済み実ファイルパス

④ 内部参照（:ref: / ラベル参照）
  ref_name:          RST ラベル名
  target_page_title: ラベル定義のある RST title
  target_section:    ラベルが指すセクション title
```

#### 検証マトリクス（漏れ・重複・間違い）

| 種別 | 物理チェック | JSON チェック | MD チェック |
|------|------------|-------------|------------|
| ① ページ | rst ファイル存在 | target_page_title が JSON に存在 | MD に見出し存在 + リンク解決可 |
| ② 外部 URL | — | url が JSON に存在（漏れ） | url が MD に存在 |
| ③ アセット | physical_path 存在 | asset_path_out が JSON に存在 | MD リンクが物理解決可 + label 一致 |
| ④ 内部参照 | ラベル定義存在 | target_section が JSON に存在 | MD に該当セクション存在 |

#### Steps（TDD）
- [ ] RST リンク収集・解決ロジックの設計（ユーザー確認）
- [ ] UT: 各リンク種別の収集・解決テスト → RED → GREEN
- [ ] UT: JSON/MD 照合テスト（漏れ・間違い・物理チェック）→ RED → GREEN
- [ ] `pytest` 全通過
- [ ] `rbkc.sh verify 6` で残存 FAIL が解消していること確認
- [ ] サブエージェント品質チェック
- [ ] コミット

---

### Phase 17-C: 残存 FAIL の個別修正

**背景**: Phase 17-A/B 完了後も残る FAIL の個別対応。
現時点の残存 FAIL（50件）:

| カテゴリ | 件数 | 対応フェーズ |
|---------|------|------------|
| JSON: token coverage < 70% | 24 | Phase 17-A で解消見込み |
| docs MD: token coverage < 70% | 20 | Phase 17-A 完了後に再調査 |
| Internal link target not found | 6 | 下記 |

**Internal link 6件の詳細**:
- `repository.rst`: `int[]` 偽陽性 ×2 → Check C の正規表現改善（`[]` を含む識別子をスキップ）
- `Nablarchでの非同期処理.md`: `./nablarch-async-pattern.png` 未コピー ×4 → resolver でコピー対象に追加

#### Steps（TDD）
- [ ] `int[]` 偽陽性修正: UT → RED → 実装 → GREEN（verify 変更のためユーザー事前確認）
- [ ] `nablarch-async-pattern.png` 未コピー修正: 原因調査 → TDD で修正
- [ ] docs MD token coverage 20件の再調査（Phase 17-A 後）
- [ ] `pytest` 全通過
- [ ] `rbkc.sh verify 6` FAIL 0件確認
- [ ] コミット

---

### Phase 18: 統合検証 — v6 完了

**前提**: Phase 17-A/B/C 完了後（`rbkc.sh verify 6` FAIL 0件）

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
- [x] docs.py: assets/ リンクを docs MD の位置から相対解決できるよう書き換え — committed `008e8420`
  - → verify FAIL: 351件 → 50件（docs MD assets link 301件解消）
- [x] Rules整理: development.md追加、work-log/rbkc/pr.md更新 — committed `aa08f489`
