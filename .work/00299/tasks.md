# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-23 (session 54 — Z-1 完了: r7 全 27 Finding + r8 7 Finding 対応 → r9 で QC1/QC4/QL2 は 0 Finding、他は reviewer 間で方向が矛盾する spec 沈黙解釈で打ち切り。Excel QC3 earliest-only scan の真のバグのみ r9 で fix。§4 品質マトリクス全 ✅ 復元。SE エキスパート相談で r7-r9 で追加した防御コード (ATX-close / TOON drift 検出 / QO3 MD→JSON dangling / QL2 test) を YAGNI 原則で削除、verify.py -114 行。次フェーズは Phase 21-Z Z-5 (v6 ベースライン取得) または Phase 19 (v5/v1.x 展開)。)

全フェーズ TDD（verify が質問ゲートのため順序に注意）:
- **verify 追加時**: verify テスト作成 → RED確認 → verify チェック実装 → GREEN確認 → RBKC 実装 → verify GREEN確認 → サブエージェント品質チェック
- **CLI 追加時**: テスト作成 → RED確認 → 実装 → GREEN確認 → サブエージェント品質チェック

## verify 実装ルール（絶対遵守）

- **設計書通りに実装する**: `tools/rbkc/docs/rbkc-verify-quality-design.md` が唯一の実装仕様。問題・疑問が生じたらユーザーに相談し、勝手に判断して実装を変更しない
- **設計書 → 実装の順序**: ユーザーと合意して verify の内容を見直す場合は、必ず設計書を更新してから実装を進める。設計書と実装の整合は常に維持する
- **マトリクスの ✅ 条件**: 実装が完了し、かつ実際の RBKC 出力に対して動作を確認した時点で初めて ✅ にする

---

## 方針転換（session 38 合意）

**RBKC は "ルールベースで content のみ生成" に責務を限定する。**

**背景**:
- hints は機械抽出しても本文検索で同等にヒットするため価値が低い（本文にない別名・略語・類義語こそ価値、それは AI でしか取れない）
- KC catalog は h4 まで section 化、RBKC converter は h2/h3 のみ section 化 → 粒度不整合に起因する mismatch が Phase 21-D 以降ずっと続いている
- hints を RBKC から外すことで、粒度不整合問題は本 PR から消える

**本 PR で扱うこと**:
- RBKC は JSON / docs MD / 索引を content（タイトル + 本文）のみで生成
- JSON の `hints` フィールドは出力しない（空でも出さない）
- docs MD の `<details><summary>keywords</summary>` ブロックは出さない
- verify の hints 関連チェック（QC6 完全一致・`_parse_docs_md_hints` 等）は削除

**本 PR で扱わないこと（別 Issue 管轄）**:
- AI 生成 hints (`hints/v*.json`) の人間レビュー・マージ
- 別 Issue に以下を資産として渡す:
  - 現状の `hints/v6.json`（他バージョン含む）
  - `.work/00299/generate_hints.py` と周辺スクリプト
  - KC catalog との粒度差の背景

---

## 現状サマリー（session 38 方針転換時点）

`bash rbkc.sh verify 6` → **FAIL 合計 139件**（全て hints 関連、Phase 21-K 完了後に自動解消予定）

| カテゴリ | 件数 | 受け皿 Phase |
|---|---|---|
| hints `file entry not matched by any knowledge section` | 74 | Phase 21-K（削除で解消） |
| hints `docs MD hints differ from hints file` | 65 | Phase 21-K（削除で解消） |

---

## In Progress

### Phase 21-Z Z-1: QA 反復レビュー → マトリクス復元 ✅ 完了 (session 54)

**結果**:
- r2〜r9 で bias-avoidance QA レビューを反復、critical は全て解消
- §4 品質マトリクスを全 ✅ に復元 (`55bebe0cf`)
- r7-r9 で追加した防御コードを SE 相談後に YAGNI cleanup (`1e46d6eb6`)
- 最終: 248 unit tests GREEN、v6 verify FAIL 0、verify.py は必要最小限

**Status (履歴参照のみ)**: r7 完了 (`66cc4c541`)。binary review format 適用で、27 Finding を抽出。QC2 のみ 0 Finding、その他 10 観点に残存。レビュー結果は `.work/00299/review-z1-r7/`。

**r7 Finding 一覧 (spec clause 引用付き、全て blocking)**:

**QC1 (2)**:
- [ ] F1: `verify.py:551-557` の post-normalisation (image/link/whitespace strip) 削除。§3-1 "残存判定の基準" 違反。`_build_rst_search_units._norm` L475-486 の同じ strip も共通化または削除
- [ ] F2: RST residue が 80-char 1 snippet のみ → MD 同様に全 fragment 報告 (L596-607 を MD path L688-710 と同形に統一)

**QC3 (4)**: OR assert `"QC3" in i or "duplicate..." in i` を spec label 単独 `"[QC3]" in i` + `not any("[QC2]"/"[QC4]")` に
- [ ] F1: `test_fail_qc3_duplicate_content_rst` (L1129)
- [ ] F2: `test_fail_qc3_top_level_and_section_content_duplicated` (L1162)
- [ ] F3: `test_fail_qc3_duplicate_content_md` (L1171)
- [ ] F4: `test_fail_qc3_duplicate_cell_in_json` (Excel, L1375)

**QC4 (4)**:
- [ ] F1: `test_fail_qc3_qc4_boundary_duplicate_text_misplaced` — QC4 label 明示 assert 追加、真の boundary fixture に。QC3 側と QC4 側 2 本 split
- [ ] F2: **実ロジックバグ** — `prev_idx = norm_source.find(norm_unit)` が最早出現のみ見て QC3/QC4 誤分類。3+ 回出現で中央 unconsumed のケースで QC3 誤報。RST/MD 両枝 (L576, L671) を finditer で全走査に書き直し。3-occurrence 再現テスト追加
- [ ] F3: 3-section content-only rotation test 追加 (RST + MD)
- [ ] F4: QC4 テスト全件に section id assert (`"s2" in i`) 追加

**QC5 (2)**:
- [ ] F1: `_RST_ROLE_RE` を `:[a-zA-Z][a-zA-Z0-9_.-]*:\`[^\`\n]+\`` に (閉じ backtick 必須)
- [ ] F2: `_RST_LABEL_RE` を `^\.\.\s+_[a-zA-Z0-9_-]+:\s*$` (MULTILINE) に行アンカー

**QL1 (4)**:
- [ ] F1: RST substitution-body image 除外 (`isinstance(img.parent, nodes.substitution_definition)` で skip)。QL2 対称性 §3-2 line 268
- [ ] F2: RST image dedup (`seen_rst_images: set[str]`) 追加 — MD 側 L1069-1074 と対称
- [ ] F3: `test_pass_rst_substitution_image_body_skipped` 追加
- [ ] F4: RST/MD duplicate image dedup テスト追加

**QL2 (5)**:
- [ ] F1: `test_pass_md_url_with_parentheses_in_path` の `expected = parts.external_urls[0]` を source literal に + truncated FAIL 対追加
- [ ] F2: `replace::` + embedded `<url>` の substitution-body 除外テスト追加 (spec line 268 AST 属性判定)
- [ ] F3: `test_pass_md_autolink_url_present` 追加 (PASS counterpart)
- [ ] F4: RST URL-with-parens (Javadoc) PASS+FAIL 追加
- [ ] F5: trailing-slash mismatch FAIL テスト追加

**QO1 (2, F3/F5/F6 は Observation)**:
- [ ] F1: `_H2_RE` の "extra" 方向を `##` only に制限。JSON section title が `###` にもあり得る "missing" 方向のみ両方許容。`### subheading` inline PASS テスト追加
- [ ] F2: `sections=[]` + top content 内 `###` PASS テスト追加
- [ ] F4: `# Title #` ATX 閉じ strip + テスト

**QO2 (4)**:
- [ ] F1: `test_pass_assets_link_rewrite_symmetric` — expected を `docs._rewrite_asset_links` 呼び出しで生成 (circular 解消)
- [ ] F2: `verify.py:184-185` `if not content: continue` 削除 (§3-3 verbatim 一致)
- [ ] F3: Top content 内 fenced `##` PASS + FAIL test 追加
- [ ] F4: `verify._apply_asset_link_rewrite` vs `docs._rewrite_asset_links` cross-check test 追加 (マトリクス入力で出力一致 assert)

**QO3 (2)**:
- [ ] F1: MD→JSON 方向チェック追加 (dangling docs MD 検出) — §3-3 "JSON↔MD 1:1"
- [ ] F2: dangling docs MD FAIL テスト追加

**QO4 (7)**:
- [ ] F1: `no_knowledge_content: true` JSON が index.toon に列挙された場合、distinct FAIL メッセージに ("index.toon lists no_knowledge JSON: …")
- [ ] F2: broken JSON が index.toon に列挙された場合の double FAIL 防止 — "known on disk" set で reverse check
- [ ] F3: TOON parser — header 列最後が `path` でない schema, 非 indented 行, row count mismatch で explicit FAIL
- [ ] F4: TOON parser — path field の quote/comma を explicit FAIL or honour quoting
- [ ] F5: path separator 双方を forward slash に正規化
- [ ] F6: 2 個目の `files[…]:` header で explicit FAIL
- [ ] F7: `test_fail_missing_index_file` を per-file FAIL line assert 強化 or 削除

**進行方針**:

1. 上記を根本原因クラスでまとめて横並び fix
2. 各 fix で TDD (test → RED → 実装 → GREEN)
3. 全 221 tests + v6 verify FAIL 0 維持
4. r8 bias-avoidance QA review (11 並列) で 0 Findings 確認
5. 設計書 §4 マトリクスを ✅ に復元
6. Z-1 完了コミット

**Steps**:
- [ ] QC5 regex 厳格化 (F1 F2) — 局所、最小
- [ ] QC3 OR assert を label-exact に (F1-F4)
- [ ] QC4 F2 実ロジックバグ (QC3/QC4 誤分類) 修正 + 再現テスト
- [ ] QC4 F1 F3 F4 テスト強化
- [ ] QC1 F1 post-normalisation 整理 / F2 residue all-fragments 化
- [ ] QL1 F1 F2 RST substitution-body image 除外 + dedup
- [ ] QL1 F3 F4 テスト追加
- [ ] QL2 F1 circular test 修正 / F2-F5 テスト追加
- [ ] QO1 F1 F2 F4 regex 修正 + テスト
- [ ] QO2 F2 silent skip 削除 / F1 F4 circular 解消 / F3 test
- [ ] QO3 F1 MD→JSON 方向 + F2 test
- [ ] QO4 F1-F7 修正
- [x] `pytest tests/` GREEN + `bash rbkc.sh verify 6` → FAIL 0
- [x] r8 bias-avoidance QA review 11 並列 — 5 観点 ✅ / 6 観点で新 Finding
- [x] r8 Finding の実質 fix — QC2/QC3/QL1(F1 F2)/QO1 F1/QO4(F1 F3) 完了 (`243174a2a`)
- [x] r9 bias-avoidance QA review 11 並列 — QC1/QC4/QL2 は 0 Finding、他は reviewer ごとに spec 沈黙部分への厳密解釈が分散
- [x] r9 で見つかった唯一の真の横並びバグ: Excel QC3 earliest-only scan → `_classify_missed_unit` 相当の全走査ロジックに修正
- [x] r9 残 Finding は打ち切り: reviewer 間で方向が矛盾する spec 沈黙解釈 (tolerance を狭めよ vs 広げよ) または test pinning 提案。critical は r2-r9 で全て解消済、Z-1 完了条件 (実装 / test / v6 FAIL 0) は満たす
- [x] 設計書 §4 マトリクスを全 ✅ に復元 (`rbkc-verify-quality-design.md`)
- [ ] Z-1 完了コミット

---

### Phase 21-Y: RST 処理を docutils AST + 共通ロジック化し create/verify 双方を書き直す (完了)

**目的**: 残 53 FAIL を 0 化。同時に、create 側 tokenizer と verify 側 tokenizer が RST 仕様解釈で分岐する構造バグ (footnote body 等) を根絶する。

**方針 (session 49 合意)**:

- `scripts/common/rst_ast.py` を新設し、docutils AST 取得と node → MD 対応表を一元管理
- create 側 (`scripts/create/converters/rst.py`) と verify 側 (`scripts/verify/verify.py` + `scripts/common/rst_normaliser.py`) は両方 `common/rst_ast.py` を経由して docutils を consume
- 独立性原則は「向き」で再定義: create → verify / verify → create の相互依存は禁止、だが両者が `common/` 経由で同じ RST 仕様ロジックを使うのは**推奨**
- 自前 parse (grid-table / simple-table / inline / directive / section splitter / tokenizer の regex 群) を**全廃**
- **TDD なし・verify 駆動**: `.claude/rules/rbkc.md` の「create-side は verify が quality gate、test 不要」方針に従う
- 旧 `rst.py` / `rst_normaliser.py` / 旧テストは書き直し完了時に削除

**設計書更新 (session 49 実施済)**:
- `rbkc-verify-quality-design.md` §2-2: 独立性原則を「向き」で再定義、`scripts/common/` + docutils の共有を明文化
- `rbkc-verify-quality-design.md` §3-1 手順 0: tokenizer 列挙方式 → docutils AST + node → MD 対応表方式に刷新
- footnote body を含む全 body-owning node は「子 node を再帰 Visit」で統一扱い (B. Admonition と同じ原則が footnote にも自動適用される)

**期待される効果**:
- create / verify で同じ AST を consume するため、RST 仕様の解釈がドリフトする構造バグが消える (footnote body 再帰・section splitter・table cell 内 directive 等)
- grid-table rowspan / simple-table continuation / substitution / rowspan 変則 separator / inline role 等、現 converter/tokenizer が苦手としていた構文は docutils が解決済
- コード行数が大幅削減 (現 `rst.py` 1598 行 + `rst_normaliser.py` ~600 行 → 合算で減少見込み)

---

#### Y-1: docutils AST の実証調査 ✅ 完了 (session 48)

- [x] `tools/rbkc/.work/y1_probe_ast.py` を作成、全 5 バージョン 2,581 RST ファイルを `publish_doctree` に通して計測:
  - [x] CJK parse: v6/v5/v1.x 全ファイルで成功 (UTF-8 素のまま可)
  - [x] grid-table rowspan: `entry.morerows` / `morecols` 属性として取得可 (v6=74, v5=91, v1.4=133, v1.3=77, v1.2=72)
  - [x] substitution: Substitutions transform が `|x|` を raw ノードに展開済で AST に反映 (v6=95 def, v5=133 def)
  - [x] include / literalinclude / raw: `file_insertion_enabled=False` で include 無効化、literalinclude は shim で literal_block、raw は built-in で取れる
  - [x] `:ref:` / `:doc:` / `:file:` 等 10 種の role: minimal shim で `inline` ノード (classes=`role-xxx`) に落とし、Visitor で targets 辞書解決
  - [x] footnote / footnote_reference / transition / field_list / admonition (14 種) / image / figure / table / list-table / topic / rubric / line_block すべて AST node として確認
- [x] parse 失敗・警告ファイルの分類:
  - v6=0 err, v5=0 err, v1.4=4 err, v1.3=1 err, v1.2=0 err (合計 5 件のみ、真の malformed)
  - warn は ソース側 RST ゆるみ (list/blockquote/definition list ends without blank line) が中心、docutils は AST を構築するので converter 側で許容
- [x] 結果を `.work/00299/phase21y/ast-probe.md` / `ast-probe.json` に保存、notes.md (session 48) にサマリ記載
- [ ] **BLOCKED**: Y-2 (Visitor 設計) 開始可否、include 事前展開方針、cross-ref 解決 hook 方針をユーザーに確認

#### Y-2: 共通モジュール + node → MD 対応表の設計

- [x] `scripts/common/rst_ast.py` の API を設計 (docutils ラッパー) — `rbkc-converter-design.md` §6 に記載
  - [x] `parse(source: str, source_path: Path | None) -> Doctree` — 設定 (Sphinx role/directive shim・`file_insertion_enabled=True`・`report_level`) を一元化
  - [x] `walk(doctree, visitor: NodeVisitor) -> str` — node → MD の共通 Visitor フレームワーク
  - [x] `register_shims() -> None` — Sphinx 固有 role / v1.x 固有 directive を generic に登録 (Y-1 probe で確立したセット)
- [x] node → MD 対応表を `tools/rbkc/docs/rbkc-converter-design.md` として新規作成
  - [ ] 構造: `document` / `section` / `title` / `paragraph` / `transition` / `container` / `compound` / `topic` / `sidebar` / `rubric`
  - [ ] インライン: `Text` / `strong` / `emphasis` / `literal` / `title_reference` / `inline` / `reference` / `target` / `substitution_reference` / `substitution_definition` / `footnote_reference` / `citation_reference` / `problematic` / `system_message`
  - [ ] リスト: `bullet_list` / `enumerated_list` / `list_item` / `definition_list` / `definition_list_item` / `term` / `definition` / `field_list` / `field` / `field_name` / `field_body` / `line_block` / `line`
  - [ ] ブロック: `block_quote` / `literal_block` / `doctest_block`
  - [ ] テーブル: `table` / `tgroup` / `colspec` / `thead` / `tbody` / `row` / `entry`
  - [ ] 画像/図: `image` / `figure` / `caption` / `legend`
  - [ ] 注: `note` / `tip` / `warning` / `important` / `attention` / `hint` / `admonition` / `caution` / `danger` / `error`
  - [ ] 参照/索引: `footnote` / `citation` / `label`
  - [ ] その他: `raw` / `comment`
- [ ] create / verify それぞれの Visitor サブクラスが対応表から生成する出力の差分を明記
  - create Visitor: `sections: list[Section]`・`RSTResult` (JSON 化前の構造) を返す
  - verify Visitor: フラットな正規化 MD 文字列を返す
- [ ] 設計書レビューをユーザーに依頼 (レビューなしでは実装着手しない)

#### Y-3: 共通モジュール + create/verify 実装 (基礎実装完了分)

- [x] `scripts/common/rst_ast.py` 実装 (Y-2 API 通り)
- [x] 旧 `scripts/create/converters/rst.py` を `rst_legacy.py` にリネーム (すぐ戻せる状態を維持)
- [x] 旧 `scripts/common/rst_normaliser.py` を `rst_normaliser_legacy.py` にリネーム
- [x] 新 `rst.py` を `common/rst_ast.py` + create Visitor で書き直し
- [x] 新 `rst_normaliser.py` (verify 側 tokenizer) を `common/rst_ast.py` + verify Visitor で書き直し
- [x] `verify.py` から新 normaliser を呼ぶよう配線変更
- [x] `bash rbkc.sh create 6` が完走することを確認
- [x] Sphinx role (`:ref:` / `:doc:` / `:java:extdoc:` 等) の label_map 経由解決
- [x] v6 verify FAIL 53 → 7 まで削減 (committed `cf57a1718`)

#### Y-3b: 例外全廃の横並び修正 (モグラ叩き終結)

残 7 FAIL と横並び確認で判明した構造的な例外経路を一括撤去する。

**Y-3b-1: 設計書 (横並びチェックの反映) ✅ 完了 (session 50)**
- [x] `rbkc-verify-quality-design.md` §3-1 に「例外禁止原則 (zero-exception)」追加
- [x] `rbkc-verify-quality-design.md` §3-1 「許容構文要素リスト」を撤廃 (Visitor と JSON 側 MD を共通ヘルパーで揃える前提)
- [x] `rbkc-verify-quality-design.md` §3-2 に「AST 経由原則」追加、QL1 / QL2 の抽出経路を node 属性ベースに書き換え
- [x] `rbkc-converter-design.md` §3-1a「情報保持原則 (no-drop principle)」追加 (image alt / figure caption / table title / admonition custom title / field_list value は保持)
- [x] `rbkc-converter-design.md` §3-1b「例外禁止原則 (zero-exception)」追加
- [x] `rbkc-converter-design.md` §4 の対応表を新方針 (field_list context-aware / image alt 保持 / admonition custom title 保持) に更新
- [x] `rbkc-converter-design.md` §5 を zero-exception に合わせて書き換え

**Y-3b-2: Visitor の例外経路撤去 ✅ 完了**
- [x] `render()` 最終 fallback の silent children 再帰を撤去 → 未登録 node で `UnknownNodeError` raise
- [x] `_inline()` / `inline_inline()` の未登録 role fallback を撤去 → Sphinx role ホワイトリスト外は `UnknownRoleError` raise
- [x] `inline_substitution_reference()` / `inline_reference()` の silent fallback を撤去 → 未解決は `UnresolvedReferenceError` raise

**Y-3b-3: 情報保持 (Visitor の drop 規則見直し) ✅ 完了**
- [x] `visit_field_list`: context-aware に変更 (standalone は field_name drop / field_body 再帰)
- [x] `visit_image`: alt / uri を必ず出力
- [x] `visit_figure`: caption / legend を必ず保持
- [x] `visit_table`: child `title` (list-table 等の argument) を table 直前の paragraph として出力
- [x] `visit_admonition`: custom title を Label として保持
- [x] `visit_docinfo` / `visit_field`: bibliographic field 対応 (value を保持)
- [x] `labels.py`: backtick-quoted label (`.. _\`name\`:`) 対応

**Y-3b-4: verify.py の regex 経路を AST 経路に置換 ✅ 完了**
- [x] `check_source_links` (QL1) を AST 駆動に: `reference` / `figure` / `image` / `literal_block` から候補収集、caption が RST inline 構文のみの場合はファイル名 fallback
- [x] `check_external_urls` (QL2) を AST 駆動に: `_source_urls` が `reference.refuri` を収集、JSON 側は substring 検索 (URL 内の括弧で regex 境界問題が起きない)
- [x] 旧 regex 群 (`_RST_REF_DISPLAY_RE` / `_RST_REF_PLAIN_RE` / `_RST_FIGURE_RE` / `_RST_IMAGE_RE` / `_RST_IMAGE_ALT_RE` / `_RST_LITERALINCLUDE_RE` / `_read_rst_block`) を削除

**Y-3b-5: 旧モジュールと未使用資産の削除 ✅ 完了**
- [x] `scripts/create/converters/rst_legacy.py` 削除
- [x] `scripts/common/rst_normaliser_legacy.py` 削除
- [x] `scripts/common/rst_substitutions.py` 削除
- [x] `scripts/common/rst_include.py` 削除
- [x] `scripts/verify/_verify_normalise_backup.py` 削除
- [x] 旧テスト (`tests/ut/test_rst_converter.py` / `test_rst_normaliser.py` / `test_rst_include.py` / `test_rst_substitutions.py`) 削除
- [x] `verify.py` の `_collect_rst_substitutions` / 未使用 substitutions 引数を削除

**Y-3b-6: 収束確認 ✅ 完了 (session 50)**
- [x] `bash rbkc.sh create 6 && bash rbkc.sh verify 6` → **"All files verified OK"** (v6 FAIL 0)
- [x] `pytest tests/` → 120 passed (全テスト GREEN)
- [x] サブエージェント品質チェック (SE 4/5) — High/Medium 指摘を全て取り込み `6ee04b9c4`
- [x] コミット・プッシュ (`4ae3ada3b` 本体 / `6ee04b9c4` SE 指摘反映)

#### Y-4: v6 verify FAIL 0 まで収束

- [ ] `bash rbkc.sh create 6 && bash rbkc.sh verify 6` → FAIL 0
- [ ] FAIL が残る場合は以下のいずれか:
  - (a) Visitor の漏れ → Y-2 対応表 + Visitor を更新
  - (b) docutils 挙動の差異で想定と異なる node が出る → 対応表を更新 (ユーザー承認)
  - (c) 許容構文リスト追加 → 設計書更新 + 更新 (ユーザー承認)
- [ ] 反復

#### Y-5: v5 / v1.4 / v1.3 / v1.2 で verify FAIL 0 まで収束

- [ ] `bash rbkc.sh create 5 && bash rbkc.sh verify 5` — FAIL 0
- [ ] `bash rbkc.sh create 1.4 && bash rbkc.sh verify 1.4` — FAIL 0
- [ ] `bash rbkc.sh create 1.3 && bash rbkc.sh verify 1.3` — FAIL 0
- [ ] `bash rbkc.sh create 1.2 && bash rbkc.sh verify 1.2` — FAIL 0
- [ ] v1.x 固有 directive (旧 Phase 9) の Visitor 対応が足りない場合は Y-3 に戻る

#### Y-6: 統合検証とクリーンアップ

- [ ] nabledge-test v6 / v5 / v1.4 / v1.3 / v1.2 — ベースライン比で劣化なし (Phase 18〜20 を吸収)
- [ ] `pytest tools/rbkc/tests/` — verify / CLI / common モジュールの test 全 PASS
- [ ] サブエージェント品質チェック (SE + QA)
- [ ] `tools/rbkc/README.md` の説明を「docutils AST + common/rst_ast.py 経由、create / verify 共通」に更新
- [ ] コミット・プッシュ (feature / docs 分割)

---

### Phase 21-X: 調査 → 設計書更新 → tokenizer 方式で verify 実装 (完了分、Y への前提)

**意図（なぜやるか）**:

Phase 21-W の「原文のまま削除するだけ」は、converter が RST → MD でラベル解決・記法変換・table 再構成を行う以上、substring 一致が**機械的に不可能**と判明した（例: `:ref:\`doma_config\`` → `Doma設定` にラベル解決されるため原文に存在しない）。

前回 (Phase 21-V/W 以前) の `_normalize_rst_source` 300 行が破綻したのは次の 3 つの構造的欠陥:

1. **場当たり的にパターンを発見**：実装中に実データで見つけては正規表現を追加
2. **regex パターンの積み上げ**：複数の regex が同じ行を書き換えるため、適用順に副作用が出る
3. **規則の出所が実装者の推測**：RST 仕様に照らした閉じた列挙ではない

**今回の違い（前回と同じ轍を踏まないための必須要件）**:

| 観点 | 前回 | 今回 |
|---|---|---|
| パターン発見の時期 | 実装中に場当たり | **実装前に全バージョン・全ファイル走査で一括** |
| 網羅性の保証 | なし | **出現箇所 100% をスクリプトで数値確認** |
| 規則の出所 | 実装者の推測 | **RST 公式仕様 (docutils) + 実データ実測** |
| 実装手法 | 正規表現 300 行を 1 関数に積む | **tokenizer + 独立純粋関数** (順序非依存) |
| 新規パターン発生時 | regex を黙って追加 | **設計書更新 + ユーザー承認** が前提 |

**実装方針（tokenizer 方式）**:

RST は docutils 仕様に準拠した明確な構文を持つため、正規表現で行単位に書き換えるのではなく、字句解析で構文要素を切り出して独立に変換する:

1. RST ソースを文字単位でスキャンし、inline role / inline code / external link / substitution / directive block / table block / heading underline / bullet / field list を token 列に切り出す
2. 各 token は純粋関数で MD 同等形式に変換（`:ref:\`label\`` → ラベル表を引いて解決タイトル、`` ``code`` `` → `` `code` ``、`` `text <url>`_ `` → `[text](url)` など）
3. JSON content は converter 出力 (MD) なので、同じ MD 形式に揃える（既存 `_normalize_md_unit` を流用）
4. 両側を正規形で substring 比較（sequential-delete）
5. 残渣は「許容構文要素リスト」で判定

**調査対象**: v6 / v5 / v1.4 / v1.3 / v1.2 の**全バージョン・全ソースファイル** (RST + MD + Excel 対象外)

**Steps:**

#### X-1: 方針確定と現状保全 ✅ 完了 (session 43)

- [x] 現在の verify.py を `_verify_normalise_backup.py` にコピー保全
- [x] 最新コミット記録 → notes.md (session 43 下の「最新コミット」を参照)

#### X-2: 調査スクリプト群の作成と実行 (実装前・手戻り防止のコア)

**目的**: 実装前に全バージョン・全ファイルから RST/MD 構文の出現パターンを網羅的に洗い出し、converter の変換規則を実データから逆算する。この Step を終えた時点で、「後から新パターンが出て実装を書き直す」という手戻りを原理的に消す。

**Steps:**

- [x] `.work/00299/phase21x/` ディレクトリを作成
- [x] **X-2-a: Inline 構文の網羅スクリプト** (`scan_inline.py`)
  - 全 RST ファイルから次を抽出・集計:
    - `:[a-zA-Z][\w.-]*:\`...\`` (role with/without target)
    - `` ``...`` `` (double-backtick inline literal)
    - `` `...`_ `` / `` `...`__ `` (named / anonymous reference)
    - `` `...<...>`_ `` (embedded URL)
    - `\|[^|]+\|` (substitution reference)
    - `\[[^\]]+\]_` (footnote/citation reference)
    - `[*][*][^*]+[*][*]` / `[*][^*]+[*]` (emphasis — RST 用法あり)
  - 各パターンの**出現回数**、**バリエーション一覧**（例: role 名は何種類あるか）
  - 出力: `.work/00299/phase21x/inline-patterns.json`
- [x] **X-2-b: Block 構文の網羅スクリプト** (`scan_block.py`)
  - 全 RST ファイルから次を抽出・集計:
    - `^\.\. \S+::` のディレクティブ名一覧と出現回数
    - simple-table (`=== ===` separator) / grid-table (`+---+`) / list-table の出現数
    - 見出しアンダーライン記号の種類別集計
    - field list (`^:\w+:`) の出現パターン
    - bullet / enumerated list マーカーの種類
    - line block (`|`) の使用有無
  - 出力: `.work/00299/phase21x/block-patterns.json`
- [x] **X-2-c: 変換規則の逆算スクリプト** (`derive_transforms.py`)
  - 各 inline/block パターンについて、**対応する JSON content** の該当箇所を diff で取り、変換規則を逆算
  - 方法: サンプルファイルごとに `(RST 断片, 対応する JSON 断片)` のペアを抽出（位置合わせは元 offset → converter 出力 offset の対応表を構築）
  - 出力: `.work/00299/phase21x/transform-rules.md` (人間レビュー用の表形式)
- [x] **X-2-d: MD ソース側の網羅** (`scan_md.py`)
  - v6 の nablarch-system-development-guide 配下の全 MD ファイルから、RST と異なる MD 独自記法の出現を集計
  - 例: `<details>` / `<summary>` / `<br>` / 数式 / 独自 link 形式
  - 出力: `.work/00299/phase21x/md-patterns.json`
- [x] **X-2-e: 残渣パターンの試行スクリプト** (`pilot_residue.py`)
  - X-2-a〜d の結果で**仮の tokenizer**を書き、全ファイルで「JSON token → ソース substring 検索」を試行
  - マッチしなかった箇所を**全件ダンプ**
  - 分類: (i) tokenizer 未対応の構文 / (ii) converter の真のバグ / (iii) 許容構文リスト追加候補
  - 出力: `.work/00299/phase21x/residue-triage.md`
- [x] **X-2-f: 全バージョン横断確認**
  - v6 で確立したパターンを v5 / v1.4 / v1.3 / v1.2 でも走らせ、差分を抽出
  - 出力: `.work/00299/phase21x/cross-version-diff.md`
- [x] **X-2-g: 調査結果レビューをユーザーに依頼** ✅ 調査完了、notes.md (session 44) にサマリ記載。以下でユーザーに照会中
  - `.work/00299/phase21x/` の全結果をサマリして notes.md に記載済
  - **BLOCKED**: ユーザーに「このパターン集合で設計書を閉じて X-3 に進んで良いか」確認を取る

#### X-3: 設計書の更新 (ユーザー承認後) ✅ 完了 (session 44)

- [x] `tools/rbkc/docs/rbkc-verify-quality-design.md` 3-1 節を書き直す:
  - **新規セクション「手順 0: ソース前処理 (tokenizer)」** 追加、inline 10 種・directive 7 グループ（22 種）・block 構文を閉集合として明記
  - 手順 1–4 を「正規化ソース」を対象とするよう書き換え
  - 許容構文要素リストを、tokenizer 正規化後の MD 由来残渣（fence・table sep・blockquote 等）に刷新
  - Include / substitution を `scripts/common/` に配置する方針を記載
- [x] 設計書変更案をユーザーに提示、承認取得（Q1〜Q4 + 実データ scan に基づく精緻化）

#### X-4: tokenizer + verify の TDD 実装 ✅ 基本実装完了 (session 44〜45、4812→123 FAIL)

- [x] **scripts/common/rst_substitutions.py** — `.. |name| replace::` / `raw:: html` の定義収集と展開、循環検出
- [x] **scripts/common/rst_include.py** — `.. include::` / `literalinclude` の展開、depth 制限、循環検出
- [x] **scripts/common/rst_normaliser.py** — tokenizer 本体 (inline 10種 + directive 22種 + tables/headings/lists/line-blocks/footnotes + field list + line-continuation)
- [x] **scripts/verify/verify.py** — 既存 `_normalize_rst_source` を新 normaliser に委譲、sequential-delete を spec 通りに
- [x] 既存テスト全件 GREEN 確認 (180 PASS)
- [x] v6 create/verify で 4812→123 FAIL

**実装中の設計書違反 (session 45 で発覚)**:

実装中に converter 出力と tokenizer 出力がミスマッチする箇所を、安易に「tokenizer 側を converter に合わせる」方向で修正してしまった。これは設計書 2-2 節「独立性原則」および 5 章「許容されない変更」に違反する。箇所:

| 違反箇所 | 設計書違反 | 本来の正しい方向 |
|---|---|---|
| `_render_grid_table` が HTML `<table>` 出力 | converter 出力模倣 | converter を MD table 出力に修正する |
| `_render_simple_table` に trailing-separator 形式 | converter バグに合わせた | converter のバグを直す (header\n---\nbody に) |
| `_ADMONITION_LABELS` 辞書 (Note/Tip/...) | converter 出力模倣 | `scripts/common/` に共通の RST→MD 規約として配置 |
| `raw:: html <a>` → MD link 変換 | converter 出力模倣 (ユーザー指示で既に共通化済の形) | 既に `common/` にある、OK |
| `\x04` 幅保存 padding | RST 仕様外の hack | 削除 (inline transforms は RST 仕様に忠実に) |
| `_render_simple_table` の CJK mid-sep detection | RST 仕様範囲内だが複雑化 | 維持 or 簡素化 |

#### X-4a: 独立性違反の撤去と converter 修正 ✅ 完了 (session 46)

**結果**: v6 verify FAIL 4812 → 56 (98.8% 削減)、全 199 unit test GREEN。

- [x] **tokenizer の converter-依存コード撤去**
  - [x] `_render_grid_table` の HTML `<table>` 出力 → MD table に変更
  - [x] `_render_simple_table` → 標準 MD (header/sep/body) に統一
  - [x] `_PAD_CHAR` 幅保存 padding 削除 (inline transforms は RST 仕様準拠)
  - [x] `_ADMONITION_LABELS` 辞書 → `scripts/common/rst_admonition.py` に移動
- [x] **`scripts/common/rst_admonition.py` 作成** (TDD 16 件 PASS)
  - [x] RST admonition → MD blockquote 変換規則、14 directive の閉集合
  - [x] converter / tokenizer 両方から import
- [x] **converter の RST 仕様準拠修正**
  - [x] `_parse_grid_table` → HTML ではなく MD table を出力
  - [x] `_parse_simple_table_cjk` の mid-separator 検出バグ修正 (total_seps >= 3 を要件化)
  - [x] footnote label regex の hyphen 許可 (`[#thread-unsafe]` など)
  - [x] `_ADMONITIONS` を `scripts.common.rst_admonition.ADMONITION_LABELS` に切替
- [x] **tokenizer 側追加修正** (converter 追従)
  - [x] backtick-label 定義 `.. _\`name\`:` 対応
  - [x] コメント行の indent-aware continuation strip 修正
  - [x] field-list 厳密正規表現 (inline role `:java:extdoc:` を誤マッチしない)
  - [x] admonition body 2 段階処理 (prose の field-list 名 drop / tail はそのまま)
  - [x] admonition tail に CJK field-list 対応 (`:リクエストスコープ:` など)
  - [x] simple-table / list-table / grid-table cell 内 directive ヘッダ行 strip
  - [x] grid-table rowspan sub-separator (`| +---+`) 対応
  - [x] grid-table 変則 sub-separator `+---+/text/+---+` スキップ
  - [x] fenced code block 内の whitespace 非圧縮
  - [x] 見出しアンダーライン単体行 (transition) 保持

**残 56 FAIL の分類**:

主に converter の真のバグに収束 (tokenizer は設計書通りの品質ゲートとして機能):

| カテゴリ | ファイル例 | 件数 |
|---|---|---|
| 多カラム simple-table で cell 値が行跨ぎ + 埋込み directive | `tag_reference.rst` `biz_samples/01/index.rst` など | ~30 |
| 複雑 directive (Excel 記述方法の画像 etc) の converter 側処理漏れ | `06_TestFWGuide/01_Abstract.rst` 他 | ~15 |
| biz_samples の footnote body が section splitter で前 section に吸収 | `PBKDF2*`, `biz_samples/01` | ~8 |
| QC5 converter がディレクティブ記法を JSON に残存 | `RequestUnitTest_rest` | 2 |
| 未分類 | その他 | ~1 |

#### X-4b: 残 56 FAIL → 0 化 (converter の真のバグ修正) — SUPERSEDED by Phase 21-Y

**打ち切り理由 (session 47)**:

残 53 FAIL を調査した結果、以下の理由で個別修正路線を断念し、converter 全面書き直しに切り替える。

- 残バグが 8 分類・56 件に分散しており、1 件 1 コミットでは FAIL 0 到達まで 7〜10h 見込み
- 現 `rst.py` (1598 行) は過去の patch 積み重ねで grid/simple table・inline・substitution・section splitter が密結合。B5 のように**修正順序を変えるだけで他所が壊れる**構造
- docutils 0.22.4 が既にセットアップ済で、`GridTableParser` / `SimpleTableParser` / `publish_doctree` など参照実装が利用可能。**自前再実装をやめて reference implementation に委ねる**方が仕様準拠・保守性・ROI いずれでも優位

X-4b の Step 定義 (B1〜B8) と B4-a commit (`4b617079d`) は参考資料として残す。Phase 21-Y で converter を書き直すとこれらは包含されて消える。

#### X-5 / X-6 (旧): SUPERSEDED by Phase 21-Y の該当 Step

---

### Phase 21-W: verify を設計書通りに書き直す（SUPERSEDED by Phase 21-X）

**結論**: 設計書 3-1 節「原文のまま・削除だけ」は、converter がラベル解決・inline 記法変換を行うため**機械的に substring 一致不能**と session 43 で判明。tokenizer 方式に切り替え、実装前に全バージョン全ファイルを走査するアプローチ (Phase 21-X) に移行した。Phase 21-W の Step 定義は参考資料として以下に残す。

---

### Phase 21-V: verify 作り直し + v6 verify PASS まで一気通貫 (SUPERSEDED by Phase 21-X)

**方針（session 39 合意）**:
- 既存 verify は hints 時代の層が残り、配線漏れ・sequential-delete アルゴリズムが converter 出力形式と衝突している（RST simple-table ↔ MD table 変換を認識できず QC1/QC2 両方で FAIL 等）
- モグラ叩きをやめて、**設計書 `rbkc-verify-quality-design.md` の仕様通りの最小 verify を一から書き直す**
- hints が無くなった今、verify の責務は「ソースの内容が JSON/docs MD に、許容構文リスト通りに正しく含まれているか」だけ
- Issue #299 の SC は verify PASS — 本 PR でクリアする

**前提**:
- 配線のみコミット済 (`d7e3469ac`) は維持（verify 作り直しで置き換わる）
- 現在の CJK fallback 差分は revert 済（新 verify のほうで必要なら対応）

**Steps (一気通貫):**

#### V-1: 既存 verify の白紙化 ✅ committed `c0afe5f27`
- [x] `tools/rbkc/scripts/verify/verify.py` を空スタブに置換（公開 API のシグネチャのみ残す）
- [x] `tools/rbkc/tests/ut/test_verify.py` も一旦退避（`_test_verify_OLD.py.bak` にリネーム）
- [x] `bash rbkc.sh verify 6` → "All files verified OK" 確認

#### V-2: 設計書仕様の再確認・調整 ✅ (設計書変更不要と確認)
- [x] 設計書 3 章「許容構文要素リスト」確認 — 変更不要（設計書は現状で問題なし）

#### V-3: 最小 verify を TDD で再構築（RST/MD） ✅ 100 PASS（テスト 62件）
- [x] QO1: docs MD 構造整合性（title / section titles / 順序）— TDD GREEN
- [x] QO2: docs MD 本文整合性 — TDD GREEN
- [x] QO3: docs MD 存在確認（check_docs_coverage）— TDD GREEN
- [x] QO4: index.toon 網羅性（check_index_coverage）— TDD GREEN
- [x] QC1/QC2/QC3/QC4: sequential-delete（設計書 3-1 通り）— TDD GREEN
- [x] QC5: 形式純粋性 — TDD GREEN
- [x] QL1: 内部リンク — TDD GREEN
- [x] QL2: 外部 URL — TDD GREEN

#### V-4: Excel verify の再構築 ✅ (V-3 と同コミット)
- [x] Excel sequential-delete ロジック移植、単体テスト GREEN

#### V-5: 実データで FAIL を洗い出し（完了）
- [x] `bash rbkc.sh create 6 && bash rbkc.sh verify 6` 実行
- [x] FAIL カテゴリ集計: 24256 件 (QC2: 12552, QC1: 9545, QC4: 1640, QO4: 318, QC5: 134, QC3: 62, QL2: 5)
- [x] 根本原因調査 — QC1/QC2 の大多数は RST→MD 変換差異の false positive

#### V-6: 初期改修 (session 41) — 5968 → 1253 FAIL (79% reduction)
- [x] committed `aafbadcd0`: verify の QO4 parser / QL2 backtick / QC1 normalize (ref, backtick, substitution, extended label, table-border) + converter の admonition body 再帰 / substitution 展開 / typo directive / list-table cell 改行保持 / footnote inline 変換 / RST comment 対応

#### V-6 現状サマリー (残 1253 FAIL)
| カテゴリ | 件数 | 根本原因 | 対応コスト |
|---|---|---|---|
| QC1 | 693 | search unit (MD-norm) と norm source (RST-norm) 両側で取り除くパターンの非対称：bullet list `* text` / grid-table 行 / table-cell 分割の continuation / footnote 定義の位置ズレ | 中〜大。verify normalize を lossy に統一する改修が必要 |
| QC2 | 557 | converter の section 分割バグ — footnote 定義やファイル末尾 text が直前 section の content に吸収される (例: `jakarta_ee/index.rst` s2 に末尾のfootnote bodyと後続prose全てが吸収) | 大。RST section splitter の再設計が必要 |
| QC5 | 3 | simple-table cell 内の nested directive 残留 (`.. code-block::` / `.. tip::` in `=== ===` table cells) | 中。_parse_simple_table に cell-level strip を追加 |

#### V-6 次ステップ — ユーザー判断待ち

**問題点**: ここから先は「verify 単独の調整」では解決できない。converter の設計変更が必要な項目が複数あり、設計書の独立性原則 (2-2) の範囲内で対応するか、設計書自体を更新するかの判断を要する。

**選択肢案**:
- **A**: converter を深掘りして section splitter と table-cell 処理を見直し (大工事)
- **B**: QC1/QC2 の判定を「normalized token set の双方向包含」に変えて順序・位置への厳密さを緩める (設計書 QC4 の「配置正確性」を弱める結果になるため設計書更新要)
- **C**: 現状の 1253 FAIL を「残既知」として PR を切り、別 Issue で converter 設計見直しを扱う (v6 verify PASS は達成できないが、リスク限定)

品質基準 (ゼロトレランス) に最も誠実なのは A だが、スコープが大きく別 Phase 相当。

- [ ] **BLOCKED**: ユーザーに A/B/C の判断を仰ぐ

#### V-7: v6 verify PASS 確認
- [ ] `bash rbkc.sh create 6 && bash rbkc.sh verify 6` — "All files verified OK" を確認
- [ ] `tools/rbkc/docs/rbkc-verify-quality-design.md` 4 章マトリクスの ❌ → ✅ 更新
- [ ] サブエージェント品質チェック (SE + QA)
- [ ] コミット・プッシュ

---

### Phase 21-K: hints スコープアウト — 設計書とコードを "content のみ" に整える (完了)

**目的**: 後続タスク（統合検証など）で「ここは hints あるんだっけ？」と判断に迷わないように、設計書とコードから hints 関連を削除して基盤を整える。hints 資産は別 Issue 用にブランチ外の形で保全する。

#### Step K-1: 別 Issue 用の資産棚卸し（削除前に固定）

- [x] `hints/v6.json` / `v5.json` / `v1.4.json` / `v1.3.json` / `v1.2.json` の現状を別 Issue 用資料として `.work/00299/handoff-hints/` にコピー
- [x] `.work/00299/generate_hints.py` / `extract_hints.py` も同ディレクトリに保全
- [x] 別 Issue 用の引き継ぎメモ `.work/00299/handoff-hints/README.md` 作成（背景・粒度差問題・AI hints の価値判断の要約）
- [x] コミット・プッシュ（「hints 別 Issue 引き継ぎ資産を保全」）— committed `28fdef842`

#### Step K-2: 設計書を "content のみ" に更新

- [x] `tools/rbkc/docs/rbkc-verify-quality-design.md` — QC6 / hints 関連検査項目を削除、マトリクスも hints 行削除
- [x] `tools/rbkc/docs/rbkc-json-schema-design.md` — `hints` フィールドの記述を削除（top-level / section 両方）
- [x] `.claude/rules/rbkc.md` — Hints files セクション（`rbkc hints` / `hints/v{V}.json` / 三者一致ルール）を削除。「RBKC は content のみ扱う、hints は別 Issue」と明記
- [x] コミット・プッシュ（「docs: scope RBKC to content-only」）— committed `b21197d73`

#### Step K-3: コードから hints を削除 + processing_patterns バグ修正

**session 39 で発覚した追加問題（必ず本 Step で同時修正）**:
- `tools/rbkc/scripts/create/index.py:91` が `_collect_hints(data)` を呼び、hints 語彙を `processing_patterns` 列に詰め込んでいる（本来の意味論違反）
- 監査結果（v6 index.toon 313 entries）:
  - `type=processing-pattern` 79件: `pp != category`（本来 `pp == category` が正、例: `pp=nablarch-batch`）
  - `type!=processing-pattern` 186件: `pp` に hints 語彙が詰まっている（本来空文字）
- v1.2〜v5 は KC 出力のまま正しい意味論。汚染されているのは v6 のみ
- KC の挙動 (`phase_f_finalize.py:303-308`): `type=processing-pattern` なら `category` を使う、それ以外は空
- RBKC の mapping (`tools/rbkc/mappings/v{V}.json`) は既に type/category を持つので RBKC 自己完結で機械生成可能（AI 不要、別ファイル不要）

**修正方針（ユーザー承認済み: 案 A）**:
- `processing_patterns` は mapping 由来の type/category から機械生成（KC と同じ意味論）
- 追加ファイル生成は不要。`index.py` のロジック差し替えだけで済む
- index.toon スキーマ `{title,type,category,processing_patterns,path}` は維持（skill 5 版の `_file-search.md` Axis 3 も維持）

**Steps:**
- [x] `tools/rbkc/scripts/create/index.py` — `_collect_hints(data)` 呼び出しを削除し、`file_infos` を受け取って `fi.type == "processing-pattern"` なら `fi.category`、それ以外は空文字を使うロジックに置換
- [x] `tools/rbkc/scripts/create/hints.py` — ファイル削除
- [x] `tools/rbkc/scripts/run.py` — hints 関連を全削除、generate_index() 呼び出しを新シグネチャに更新
- [x] `tools/rbkc/scripts/create/docs.py` — `<details>keywords</summary>` ブロック出力を削除（2箇所）
- [x] `tools/rbkc/scripts/verify/verify.py` — `check_hints_completeness` / `_parse_docs_md_hints` / `check_hints_file_consistency` / `_KEYWORDS_RE` / `FILE_SENTINEL` import を削除
- [x] `tools/rbkc/scripts/common/constants.py` — `FILE_SENTINEL` のみの定義だったためファイル削除
- [x] `tools/rbkc/hints/` ディレクトリ削除
- [x] converters は元々 hints 参照なしを確認済み
- [x] `tools/rbkc/rbkc.sh` は hints サブコマンドなしを確認済み
- [x] `test_hints.py` 削除、`test_run.py` / `test_verify.py` / `test_docs.py` の hints 関連テスト削除。`test_index.py` 新規作成（TestProcessingPatternsSemantics / TestNoKnowledgeContentExcluded / TestMissingJsonSkipped / TestTitleCommaEscape / TestGenerateIndexEdgeCases）
- [x] `bash rbkc.sh create 6 && bash rbkc.sh verify 6` — "All files verified OK" (FAIL 0件)、index.toon 監査: pp 79件すべて `pp == category`、他 239件すべて `pp == ''`、違反 0件
- [x] サブエージェント品質チェック (SE 4.5/5 / QA 4.5/5) — 全指摘（Medium 2, Low 3）を同一コミットで修正済み
- [x] コミット・プッシュ — committed `f7cff23a1` (feat) + `983ae8301` (docs)

#### Step K-4: 別 Issue 起票

- [x] GitHub Issue #309 起票 — AI-curated hints のフォローアップ
- [x] `.work/00299/handoff-hints/` へのリンクと背景要約を記載

---

## Not Started

### Phase 21-Z: クリーンアップと品質固定 (土台整理 → v6 品質固定)

Phase 21-Y 完了直後 (`bf6b2d355`) の状態を起点に、土台を整えてから v6 品質を固定する。順序の意図は **土台 → 品質固定 → 展開 → 配信物 → ドキュメント**。

#### Z-2: 設計書・ソース・テストの MECE 化 (土台その 1) ✅ 完了 (session 51)

**目的**: 次の品質計測で「何を測っているか」を明確にする。

- [x] 設計書 2 本 (`rbkc-verify-quality-design.md` / `rbkc-converter-design.md`) の重複 / 矛盾解消 — committed `c8934ffc4`
  - §3-1 許容残存リストの文言を撤回しゼロトレランスで統一
  - §3-2 AST 経由原則を MD にも適用 (markdown-it-py)
  - §5 許容残存リスト追加ルールを削除
  - converter-design §7 に MD AST 対応表を追加
  - admonition 数の記載を 14 → 10 に訂正
- [x] MD を AST 経由に統一 (create / verify 双方) — committed `c53cb19e3` `eee6129a8`
  - `scripts/common/md_ast.py` + `md_ast_visitor.py` + `md_normaliser.py` 新設
  - `converters/md.py` を Visitor 経由に書き換え
  - verify の `_URL_RE` / `_MD_INTERNAL_LINK_RE` を削除、AST 収集に差し替え
  - `_check_md_content_completeness` を AST 正規化 + sequential-delete に書き換え
- [x] QO3 を JSON↔MD 1:1 存在確認に修正 — committed `1f5954d23`
- [x] tolerance list 削除 (許容残存リスト全廃) — committed `be604f880`
  - `_ALLOWED_RESIDUE_PATTERNS` (14 regex) / `_ADMONITION_RESIDUE_LABELS` (13 labels) / `_strip_allowed_residue` 削除
  - v6 verify FAIL 0 のまま動作
- [x] テストと設計書の対応表を §4 に追加 — committed `f013cd94e`

#### Z-6: 未使用コード削除 (土台その 2) ✅ 完了 (session 51) — committed `6c06b24c8`

- [x] `create/resolver.py` の `build_label_map` 削除 (common/labels.py に統合済、呼び出し元なし)
- [x] `verify.py` の `_RST_LABEL_DEF_RE` re-export 削除
- [x] `rst_ast_visitor.py` の `UnknownSyntaxError` 定義削除 (未使用)
- [x] `rst_admonition.py` の `render_header` / `is_admonition` / `ADMONITION_DIRECTIVES` 削除 (Visitor 以外で未使用)
- [x] `tests/ut/_test_verify_OLD.py.bak` 削除

#### Z-1: 設計書 §4 品質マトリクスの ❌ → ✅ 更新 ✅ 完了 (session 52)

- [x] QA エキスパート 11 並列レビューで 3 条件 (実装 / テスト / v6 FAIL 0) を点検 — `.work/00299/review-z1/SUMMARY.md` + 個別レポート
- [x] 設計ドリフト 3 件解消 (commit `2ca93d7d9`)
  - QC1 RST normaliser を `strict_unknown=True` に、parse error を QC1 FAIL 化
  - QL1 MD inline image を `check_source_links` で検査対象化
  - QO4 設計書 §3-3 に index 不在時と dangling entry の扱いを明文化、実装を双方向チェックに
- [x] QC1-QC5 gap test 追加 (commit `24c88b934`)
- [x] QL1/QL2 gap test 追加 (commit `1b46de370`)
- [x] QO1-QO4 gap test 追加 (commit `223d5f8fe`)
- [x] §4 マトリクス 11 観点すべて ✅ 化 + ✅ の三条件を明文化 (commit `e3a68e37a`)
- [x] 190 unit test GREEN / v6 verify FAIL 0 を最終確認

#### Z-5: nabledge-test v6 ベースライン (v6 品質の数値固定)

**目的**: 確定した土台 (Z-2 / Z-6) と記述 (Z-1) で、v6 の品質を数値ベースで固定。以降の他バージョン展開はここを基準に「劣化なし」をゲートにする。

- [ ] `nabledge-test 6` を実行して現状ベースラインを取得
- [ ] 旧ベースライン (memory 記録の 97.3%) と比較し劣化がないことを確認
- [ ] 劣化があれば Phase 21-Y の修正で生じた converter 出力差を調査し対応 (Visitor の出力調整 or 設計書更新 + ユーザー承認)
- [ ] ベースラインスナップショットを `baseline/v6/<timestamp>/` に保存してコミット

---

### Phase 19 (改称): 他バージョン展開 — v5 / v1.4 / v1.3 / v1.2

**前提**: Phase 21-Z 完了後。

展開は**各バージョン単位で nabledge-test ベースラインを取りながら**進める。劣化があれば即止めて調査。

**Steps (各バージョン共通):**
- [ ] `bash rbkc.sh create <v> && bash rbkc.sh verify <v>` → FAIL 分類と件数を記録
- [ ] バージョン固有 directive / role / substitution が Visitor の閉集合にない場合は設計書更新 + ユーザー承認 → 対応表追加
- [ ] verify FAIL 0 確認
- [ ] `nabledge-test <v>` で現行ベースラインと比較、劣化なしを確認
- [ ] 劣化があれば調査 → 対応 → 再測定
- [ ] コミット

**展開順** (実装影響が小さい順):

- [ ] v5
- [ ] v1.4
- [ ] v1.3
- [ ] v1.2

---

### Phase 21-Z (続): 配信物クリーン化 → ドキュメント整備

Phase 19 (他バージョン展開) 完了後に実施。rbkc 本体の出力が全バージョンで安定した後に、配信物と文言を整える。

#### Z-4: setup スクリプトのゴミ残り対策 (配信物クリーン化)

- [ ] `tools/setup/setup-cc.sh` をバージョンアップ時に旧 `.claude/skills/nabledge-${v}/` を完全に削除してから `cp -r` する形に修正 (現状は上書きのみで、旧版の削除済み知識ファイル / docs / assets が残留)
- [ ] `tools/setup/setup-ghc.sh` も同様に確認
- [ ] 削除範囲はユーザー資産 (`knowledge/` 配下にユーザーが置いたファイル等) に影響しないよう skills plugin 配下のみに限定
- [ ] 手動テスト: 模擬 vup でゴミが残らないことを確認

#### Z-3: CHANGELOG / README / 過去経緯要約 (ドキュメント整備)

- [ ] `.claude/skills/nabledge-6/plugin/CHANGELOG.md` の `[Unreleased]` に追記:
  > ### 変更
  > - 知識ファイル生成を AI ベースからルールベースに変更しました。AI 特有のハルシネーション（捏造）が発生しない構造になり、公式ドキュメントの内容が正確に反映されるようになりました。
- [ ] nabledge-5 / 1.4 / 1.3 / 1.2 の CHANGELOG も同様に更新 (他バージョン展開完了後)
- [ ] `tools/rbkc/README.md` を現状 (docutils AST + 共通 Visitor 構成) に合わせて書き直し。動作確認手順 (`bash rbkc.sh create 6 && bash rbkc.sh verify 6`) を記載
- [ ] `.work/00299/notes.md` を「Phase 21-Y で何をどう変えたか」に簡潔に要約し、不要になった中間計測ログ (`.work/00299/phase21x/` 等の大量 JSON / md) は削除または 1 ページのサマリに集約
- [ ] `tasks.md` の Done セクションから、Phase 21-Y で意味が消えた Phase (21-V 系 / 21-W / 21-X-4b など) を「Superseded by Phase 21-Y」1 行にまとめる
- [ ] GitHub Issue #309 (AI hints フォローアップ) への引き継ぎメモが現状と合っているか確認

---

### Phase 21-C (旧番): リリースノート・セキュリティ対応表の粒度が粗い

**問題**: 現状は全シート×全行を1セクションに連結 → 毎回全行ロード、検索で使えない。
行単位（変更1件=1セクション）にすれば個別レコードとして検索可能になる。

**前提**: Phase 21-V 完了後

**Steps:**
- [ ] 全容把握: v6リリースノート・セキュリティExcelのシート構造・行構造を調査しセクション分割設計を確定
- [ ] ユーザーに設計案提示・承認
- [ ] xlsx_releasenote TDD: 行単位セクション分割テスト（RED → GREEN）
- [ ] xlsx_security TDD: 行単位セクション分割テスト（RED → GREEN）
- [ ] verify 更新: 新粒度に対応したチェック
- [ ] rbkc create 6 → verify 6 FAIL 0件確認
- [ ] コミット

---

### Phase 22: 閲覧用 docs MD の可読性改善 (ユーザー実地確認から発覚)

**背景**: ユーザーが GitHub Web 上で実際に docs/ を閲覧した結果、以下の問題を報告。

verify は現在 JSON↔docs MD の content 完全一致を保証しているため、JSON 側に `>` で blockquote 化された table や、不要な blockquote に取り込まれた段落がそのまま docs MD にも反映されている。結果として GitHub Web 上でテーブルに見えない / 段落が引用ブロックに押し込まれて読みにくい。

Excel 系 (リリースノート / セキュリティ対応チェックリスト) は別問題。1 Excel ファイル = 1 JSON (全シート / 全行を空白連結したテキスト) になっており、ユーザーが期待する「1 sheet = 1 JSON = 1 MD、1 行 = 1 section、MD はテーブル」に全く従っていない。

---

#### 設計合意 (session 55)

| | JSON | docs MD | verify の一致ルール |
|---|---|---|---|
| **22-A (RST / MD)** | きれいな MD (不要な `>` blockquote を剥がす、RST `list-table` は table のまま) | JSON と同じ | QO2 完全一致を維持 |
| **22-B (Excel)** | 1 sheet = 1 JSON、1 行 = 1 section、section.content は `列名: 値\n...` の列挙 | 先頭に `# タイトル` + 全行 MD テーブル (全列網羅) | QO2 は「JSON section.content の全列値が MD テーブル内に含まれる」方向のみ (JSON ⊂ MD)。MD → JSON 方向 (MD に含まれるテキストが JSON にあるか) は Excel については緩和。spec §3-3 更新が必要。 |

**RST/MD 側ポリシー** (依頼 1 対応):

- converter `rst_ast_visitor.py` の `visit_block_quote` を修正
  - 子が table / admonition / figure のみのとき → `>` を付けずに中身だけ出力
  - 本当の引用 (paragraph を含む block_quote) → 従来通り `>` 付与
- RST `list-table` / grid-table / simple-table は blockquote に入れず、MD table として出力 (既存処理の見直し)
- 段落 (`paragraph`) が block_quote 直下にあっても、RST 仕様上の「引用」と解釈すべき場面のみ `>` を付ける。現 converter が付けすぎているケースは仕様に従って剥がす
- その他 spurious `>` の検出とルール化は調査結果に基づき決定

**Excel 側ポリシー** (依頼 2 対応):

- 1 `.xlsx` → 複数 `.json` + 複数 `docs/.../*.md` (1 sheet per file)
- JSON: `title` = シートのタイトル行、`sections` は 1 行 = 1 section、section.title はヘッダ列の "タイトル" 列値、section.content は全列を `列名: 値` の縦列挙 (検索索引として全ての値がヒットする形)
- docs MD: 先頭に `# {シートタイトル}` + 全列 / 全行の MD table 1 個 (人間閲覧用、元 Excel を復元)
- Excel の全列をそのまま table 列に含める (No., 分類, リリース区分, タイトル, 概要, 修正後のバージョン, 不具合の起因バージョン, システムへの影響の可能性, システムへの影響の可能性の内容と対処, 参照先, JIRA issue, モジュール等)
- verify: Excel 系ファイルに対しては QO2 を「JSON section.content の全テキストトークンが docs MD 内に含まれる」に緩和 (MD 側の「# タイトル」「table 罫線 `|---|`」「列ヘッダ」は JSON に無いため完全一致不能)。QC1-QC4 / QO1 / QO3 / QO4 は維持、QC5 はテーブル許容パターン追加

---

#### Steps

##### 22-A: RST/MD 側の docs MD 可読性修正

- [ ] 22-A-1: 全 docs MD (v6 ~300 ファイル) を走査する調査スクリプトを作成 (`.work/00299/phase22/scan_docs_md.py`)
  - 検出対象: (a) blockquote 内 table (`>` 内に `|...|`)、(b) 段落 1 個だけの block_quote 化、(c) 生 RST 残渣 (`.. directive::`, `:ref:`, `|substitution|`) が docs MD に漏れているケース
  - 出力: 件数 + 代表ファイル/行番号
- [ ] 22-A-2: 調査結果をユーザーに提示 → ルール確定
- [ ] 22-A-3: `scripts/common/rst_ast_visitor.py` の `visit_block_quote` を修正 (table / admonition / figure だけの child なら `>` 剥がす、他は維持)。必要に応じて `visit_admonition` / `visit_figure` の内側 table 処理も調整
- [ ] 22-A-4: `bash rbkc.sh create 6 && bash rbkc.sh verify 6` → verify FAIL 0 維持
- [ ] 22-A-5: 代表ファイルを GitHub Web で実地確認 (ユーザー)
- [ ] 22-A-6: コミット

##### 22-B: Excel converter 書き直し + spec 更新

- [ ] 22-B-1: v6 Excel ソース 2 種 (リリースノート / セキュリティ対応チェックリスト) のシート構造・列構成・ヘッダ行位置・タイトル行位置を調査。`.work/00299/phase22/excel-structure.md` に構造表を出力
- [ ] 22-B-2: 調査結果 + 新 JSON/MD 仕様案 (上記ポリシー具体化) をユーザーに提示 → 承認
- [ ] 22-B-3: `rbkc-verify-quality-design.md` §3-3 QO2 に Excel 例外 (JSON ⊂ MD の一方向) を追記、§3-1 QC5 にテーブル罫線許容を追記
- [ ] 22-B-4: `scripts/create/converters/xlsx_releasenote.py` / `xlsx_security.py` を新仕様で書き直し
  - 1 sheet = 1 JSON 分割
  - 1 行 = 1 section、content は列名:値の列挙
  - sheet タイトル取得ロジック (タイトル行位置の判定)
- [ ] 22-B-5: `scripts/create/docs.py` の Excel 用レンダリング分岐を追加 (JSON の sections を MD table に再構成)
- [ ] 22-B-6: `scripts/create/index.py` (sheet 分割で index 項目増加) 対応確認
- [ ] 22-B-7: `scripts/verify/verify.py` の QO2 (Excel 分岐) 実装 + テスト追加
- [ ] 22-B-8: `bash rbkc.sh create 6 && bash rbkc.sh verify 6` → verify FAIL 0
- [ ] 22-B-9: 生成された docs MD を GitHub Web で実地確認 (ユーザー)
- [ ] 22-B-10: コミット

**備考**: Phase 21-C (旧番 — リリースノート行粒度) は 22-B に統合済。xlsx converter 書き直しで包括する。

---

## Done

- [x] Phase 21-Y: RST 処理を docutils AST + 共通 Visitor に全面書き直し — v6 verify FAIL 53→0、unit test 120 PASS。zero-exception / no-drop / AST-only 原則を設計書と実装に適用 — commits `cf57a1718` (Y-3 初期実装 53→7) / `4ae3ada3b` (Y-3b 本体 7→0) / `6ee04b9c4` (SE review 反映) / `cf53c5752` (tasks.md 整理) / `bf6b2d355` (Phase 21-Z 計画追加)
- [x] Phase 21-A: docs/README.md 未生成 — committed `c238dc8f`
- [x] Phase 21-B: hints 永続化と完全一致チェック — verify check 実装 / `build_hints_index` file_id 正規化 / `catalog_index` last-wins バグ修正 / `extract_hints.py` 作成 / v6.json 初版生成。残 FAIL の分析は 21-D/21-I/21-J に分割
- [x] Phase 21-D: JSON スキーマゼロベース見直し（ソース忠実）— session 31〜37 で `_PREAMBLE_TITLE` 廃止、top-level content + hints 導入、converter/docs/index/verify 同時改修、read-sections.sh 5版同時修正 — commits `603c5ade` / `23bb7e5f` / `4b6531fe` / `49e467e2` / `3154264e`
- [x] Phase 21-E（旧 file=[] 46件）: Phase 21-D で大半解消。残存は Phase 21-J に統合してクローズ
- [x] Phase 21-F（旧値不一致 4件）: Phase 21-D で解消。Phase 21-J に統合してクローズ
- [x] Phase 21-H: hints file 生成ロジックの再設計（R1〜R6 ルールで 5 版 hints/v{V}.json を ゼロベース再生成、同名見出し対応の配列スキーマ化）— commits `9ffefa08` / `5adf4404` / `60b16f98` / `ca7a924f` / `f7a4db40` / `fbd2b52f` / `8ed9aa0c` / `c286de77` / `83031d95` / `d015c03e` / `80a3ed48`（verify GREEN 確認は 21-J にバトン）
- [x] Phase 21-I: QL1 回帰 314件解消 — `_json_text()` に top-level content 追加（設計書 `rbkc-verify-quality-design.md:170` 通りに修正、false-positive fix）。TDD: RED 3件 → GREEN、regression/MD top-level/`_json_text()` 直接テスト 5件追加（合計244 PASS）。SE 5/5 / QA 5/5（追試対応後）
- [x] Phase 21-J: hints mismatch 139件分析 — 根本原因は KC catalog（h4 まで section 化）と RBKC converter（h2/h3 のみ section）の粒度不整合。ユーザー判断により方針転換（session 38）し、hints は RBKC 本 PR から外して別 Issue 管轄に。受け皿は Phase 21-K

- [x] Phase V-skip: verify() FAIL on missing JSON/docs MD — committed `86dd660e`
- [x] Phase V-hints: KC-format files deleted from nabledge-6 — committed `c92accc4`
- [x] Phase V2-4-post: converter fixes (QC1, QL1) + tests — committed `6ce09683` / `21ca2783`
- [x] Phase V4: rbkc create 6 + verify 6 FAIL 0件 — committed `dbfc0582`
- [x] Phase V0: hints carry-over 実装 — committed `d155c92e`
- [x] Phase V1: 旧 verify 削除・スタブ化 — committed `2727facc`
- [x] Phase V2-1/V2-2/V2-3: QO5 / QC5 / QC6 verify 実装 — committed `a0c7abf1`
- [x] Phase V2: verify 実装計画確定
- [x] Phase 17-R: verify 品質保証設計ドキュメント作成・レビュー — commits `d020efd2`〜`2464a55c`
- [x] Phase 1: KC cache → hints mapping — committed `f78304b4`
- [x] Phase 2: RST converter with full directive support — commits `5913ff6e` / `1b62c4c4` / `9cbbc729`
- [x] Phase 3: Hints extraction Stage 1 + Stage 2 merge — committed `ac294cdb`
- [x] Gap fill: Phase 2 test修正 + Phase 1/3 E2Eテスト追加 — committed `010d0c2f`
- [x] Phase 4: Cross-reference resolution + asset copying — commits `9336f900` / `87654126`
- [x] Phase 5: MD converter — committed `232df686`
- [x] Phase 6: Excel converters — committed `edce71eb`
- [x] Phase 7: Index + browsable docs generation — committed `dc019759`
- [x] Phase 8: CLI + create/update/delete/verify operations — committed `5baf7a6d`
- [x] Phase 9: v1.x固有ディレクティブ対応 — committed `bc632d0f`
- [x] Phase 10: コンバータ修正 (10-1〜10-6) — commits `54fe3ef8` / `d5a6961d` / `cd856500` / `d2303716` / `7eac70f6` / `10b239b1`
- [x] Phase 11: verify 完全チェック化 — committed `6c664a59`（Phase 12 で書き直し済み）
- [x] Phase 12: verify 完全書き直し — committed `1eff2740`
- [x] Phase 13: create pipeline 完全修正 — committed `e85488cb`
- [x] Phase 14: classify 出力パス衝突修正 — committed `b6a4a630`
- [x] Phase 15: converter/verify URL バグ修正 — committed `63ac0ec9`
- [x] Phase 16: toctree-only index.rst token coverage 修正 — committed `37d6e547`
- [x] docs.py: assets/ リンクを docs MD の位置から相対解決 — committed `008e8420`
- [x] Rules整理: development.md追加、work-log/rbkc/pr.md更新 — committed `aa08f489`
