# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-23 (session 58 — 22-B-5b 完了 (v6 verify PASS, 353 files)。22-B-11 実地確認 FB で 3 件発覚: ①NULL混入 修正済 (`f67969f8a`)、②RST h3→## 潰れ、③内部リンク/画像が docs MD と JSON に適切反映されない + verify QL1 が docs MD 側未検証。②③は 22-B-16 に統合して本 PR で対応 (anchor 生成の前提として階層を先に正す必要があるためセットで完結)。)

---

## 現状サマリー

- v6 verify: **FAIL 0 (Phase 21-Z 完了時点で達成)**。255 unit tests GREEN
- 現在着手中: **Phase 22-B-5** — Excel converter を sheet-level 分割 + P1/P2 分類に書き直し
- verify 層 (QO2 P1 一方向 containment / `_xlsx_source_tokens` sheet_name 拡張) は TDD で実装済 (`bd678e4aa`)
- 残: xlsx converter 書き直し / docs.py P1-P2 分岐 / create→verify FAIL 0 / nabledge-test baseline 再取得 / 他バージョン展開
- 次の土台タスク: Phase 21-Z Z-5 (nabledge-test v6 baseline)、Phase 19 (他バージョン展開)

---

## 方針転換（session 38 合意）— 保持

**RBKC は "ルールベースで content のみ生成" に責務を限定する。**

- RBKC は JSON / docs MD / 索引を content（タイトル + 本文）のみで生成
- JSON の `hints` フィールドは出力しない、docs MD の `<details><summary>keywords</summary>` ブロックも出さない
- AI 生成 hints は別 Issue #309 管轄 (資産は `.work/00299/handoff-hints/`)

---

## verify 実装ルール（絶対遵守）

- **設計書通りに実装する**: `tools/rbkc/docs/rbkc-verify-quality-design.md` が唯一の実装仕様。問題・疑問が生じたらユーザーに相談し、勝手に判断して実装を変更しない
- **設計書 → 実装の順序**: ユーザーと合意して verify の内容を見直す場合は、必ず設計書を更新してから実装を進める。設計書と実装の整合は常に維持する
- **マトリクスの ✅ 条件**: 実装が完了し、かつ実際の RBKC 出力に対して動作を確認した時点で初めて ✅ にする
- **verify 変更は事前ユーザー承認**: `.claude/rules/rbkc.md` 参照。設計書に既に記載済の変更はこの限りでない
- **TDD 厳守**: verify テスト作成 → RED → verify 実装 → GREEN → RBKC 実装 → verify GREEN → SE + QA expert review

---

## In Progress

### Phase 22-B-5: Excel converter 書き直し (sheet-level 分割 + P1/P2)

**背景** (session 55 合意、保持): Excel 系 (リリースノート / セキュリティ対応チェックリスト) は現状 1 ファイル = 1 JSON (全シート / 全行を空白連結) で、ユーザーが期待する「1 sheet = 1 JSON = 1 MD、1 行 = 1 section、MD はテーブル」に従っていない。

#### 設計合意 (session 55) — 保持

| | JSON | docs MD | verify の一致ルール |
|---|---|---|---|
| **22-A (RST / MD)** ✅ | きれいな MD (不要な `>` blockquote を剥がす、RST `list-table` は table のまま) | JSON と同じ | QO2 完全一致を維持 |
| **22-B (Excel)** 着手中 | 1 sheet = 1 JSON、1 行 = 1 section、section.content は `列名: 値\n...` の列挙 | 先頭に `# タイトル` + 全行 MD テーブル (全列網羅) | QO2 は JSON ⊂ MD の一方向のみ。spec §3-3 更新済 |

**Excel 対象**: `*-releasenote.xlsx` (57)、`*-releasenote-detail.xls` (17、v1.2/v1.3)、`Nablarch機能のセキュリティ対応表.xlsx` (v5/v6 各 1)、合計 **76 ファイル / 212 シート**。

**ファイル分割**:
- 1 `.xlsx` → 各シートごとに 1 `.json` + 1 `.md`
- シート数 = 1: ファイル基底名のまま (sheet_slug 付加せず)
- シート数 ≥ 2: `{基底名}-{シート名}.json` (シート名は日本語そのまま)

**シート分類 (P1 / P2)**:
- P1 (データ表): ヘッダ行 (連続非空セル ≥ 3) + 同構造データ行 ≥ 2。ただし列数 ≤ 2 のシートは P2
- P2 (段落主体): ヘッダ検出失敗、または列数 ≤ 2

**判定メタ情報**:
- 各 JSON に `sheet_type: "P1" | "P2"` を出力
- 初回生成後に `.work/00299/phase22/sheet-classification.md` を出力、ユーザーが override 必要性判断

**複数行ヘッダ**:
- 2 段以上のヘッダは副列がある列のみ `メイン/副` 合成、副列なし列はメインのみ
- 例: `不具合の起因バージョン/モジュール/Nablarch` / `修正後のバージョン`

**JSON スキーマ**:
- P1: `title` = row 1 の `■...` (なければシート名)、`content` = 空 or タイトル直下前書き、`sections` = 1 データ行 = 1 section、`section.title` = 「タイトル」列の値 (なければ先頭非 No. 列)、`section.content` = 全列を `{列名}: {値}\n` で列挙
- P2: `title` = row 1 の `■...` (なければシート名)、`content` = シート全体テキスト、`sections` = 空

**docs MD**:
- P1: `# {title}` + 全列 MD table (元 Excel を復元)
- P2: `# {title}` + シート全体テキストをそのまま

**Baseline 再取得**:
- Excel ファイル分割で file ID が変わる → 旧 v6 baseline 97.3% と直接比較不能
- Phase 22-B 完了後に再取得、旧 baseline は履歴として保持

#### Steps

- [x] 22-B-1: 全バージョン Excel 調査 (76 ファイル / 212 シート)、構造表を `.work/00299/phase22/excel-structure.md` に出力
- [x] 22-B-2: 設計案ユーザー承認 (session 55)
- [x] 22-B-3: `rbkc-verify-quality-design.md` §3-3 QO2 Excel 例外 + §3-1 sheet-level 分割 を仕様化 (`f5aa6a0e3`)
- [x] 22-B-4: `rbkc-converter-design.md` §8 Excel 対応表新設 (`5a7cacf03`)
- [x] 22-B-5a: **verify 層 TDD** (`bd678e4aa`) — `_xlsx_source_tokens(sheet_name=...)` / `sheet_type == "P1"` 一方向 containment / P2 strict verbatim fallthrough。edge cases (URL 内 `:` / blank 値 / no-sheet_type regression guard) 含む 7 + 3 tests。SE + QA expert review 済 (QA 2 Findings を同コミットで修正)
- [x] 22-B-5a-r2: **設計書更新** (session 58) — §3-1 Excel 節に P1 header 展開仕様、§3-4 QP 新設、§4 マトリクス更新 (`03974a0ea`)
- [x] 22-B-5a-r3: **verify TDD** — RED (`a491488bb`) → GREEN (`eb0c47a77`) → QA 7 Findings 対応 (`45fd37de1` `04bdf74fa`)。274 tests GREEN
- [x] 22-B-5b: **xlsx converter 書き直し** — `xlsx_common.py` 新規、`xlsx_releasenote.py` / `xlsx_security.py` / `classify.py` / `run.py` / `docs.py` 更新 (`dabc57274`)。スキーマ sheet-level split + sheet_type + P1 table / P2 text。spec §3-3 QO1 P1 例外追加 (`023d53248`)
- [x] 22-B-5c: scan/classify/run sheet-level 対応 (22-B-5b に統合済)
- [x] 22-B-6: docs.py Excel P1/P2 分岐 (22-B-5b に統合済)
- [x] 22-B-7: index.py sheet 分割増加に対応 (353 files で動作確認)
- [x] 22-B-10: `bash rbkc.sh create 6 && bash rbkc.sh verify 6` → 353 files, All files verified OK
- [x] 22-B-5b-review: SE + QA expert review for commits `dabc57274` + `023d53248` 実施済 — SE 1 Finding (`columns`/`data_rows` JSON 未記載) + QA 3 Findings (P1 #title check / flatten edge cases / sheet_name_fallback 陽性ケース) 全件対応 (`d1e4a314a`)。282 tests GREEN
- [x] 22-B-9: 判定結果一覧 `.work/00299/phase22/sheet-classification.md` 出力 (`ca3bf744f`)。現状維持で確定、見た目改善は Issue #311 に切り出し
- [ ] 22-B-11: 生成された docs MD を GitHub Web で実地確認 (ユーザー) — FB ①NULL混入 (修正済 `f67969f8a`)、②RST h3→## 潰れ、③内部リンク/画像リンクがdocs MDに反映されない → 22-B-16 で対応
- [ ] 22-B-16: **RST section 階層 + 内部リンク / 画像 / literalinclude を docs MD と JSON に適切反映**
  - **統合理由**: 階層修正 (##/###/####) とリンク anchor 生成はセットで完結させる。§22-B-15 は 22-B-16 に統合。アンカーは section heading の slug なので、同一ファイル内で h3 が `##` に潰れると GitHub が `slug-1` と自動採番して converter が予測できなくなる。階層を正す = anchor を一意かつ安定にする前提。
  - **現状の問題**:
    - RST 階層: `_walk_section` が h2/h3/h4 を flat `parts.sections` に再帰 append → docs.py が全部 `##` で出力 → 重複 section title + 階層消失
    - `:ref:` / `reference[refid/refname]` → docs MD がプレーンテキスト (リンク消失)
    - `.. image::` / `.. figure::` → docs MD が `![](images/xxx.png)` の RST 相対パスのまま → **リンク切れ** (実アセットは `knowledge/assets/{file_id}/` にコピー済)
    - `:ref:` cross-document → ラベルからターゲット file_id への解決が無い
    - verify QL1 は JSON 側の文字列含有しか見ない → docs MD 側のリンク形式チェック欠落 (spec §3-2 に「docs MD にアンカーリンクとして出現」と記載済、実装が未対応)
  - **あるべき姿**:
    - 階層: `Section` に `level: int`、docs MD は `##`/`###`/`####` を level に応じ出力
    - JSON (AI 向け):
      - `:ref:` → target title + ターゲット file_id ヒント埋め込み (AI が file_id で cross-document 検索できる)
      - `image` / `figure` → `![](assets/{file_id}/fname.ext)` で content に埋め込み
    - docs MD (人間閲覧向け):
      - `:ref:` → `[target title](../../{type}/{category}/{target_file_id}.md#anchor)` (GitHub Web でクリック可能)
      - `image` / `figure` → `![alt](../../knowledge/assets/{file_id}/fname.ext)` (ブラウザで表示可能)
    - verify QL1 強化: **JSON と docs MD **両側**でチェック**
      - JSON: target title + asset path が content に存在
      - docs MD: 対応するアンカーリンク / 画像リンクが実在する MD / 画像ファイルを指している
      - QO1: section.level と docs MD heading level の一致
  - **対象一覧**: verify の既存 `check_source_links` が AST から抽出済 (追加調査不要)
  - **手順**:
    1. 設計書更新
       - `rbkc-converter-design.md`: Section に `level`, sections[].level を §4 / §7 に明記、:ref: / image の MD リンク形式
       - `rbkc-verify-quality-design.md` §3-2 QL1 の JSON/docs MD 両側仕様、§3-3 QO1 の level 一致要件、§4 マトリクスに QL1 (docs MD 側) を追加
    2. `label_map` を label → (title, file_id) に拡張 (cross-document リンク解決)
    3. verify TDD:
       - QO1 level 一致
       - QL1 docs MD アンカーリンク存在チェック
       - QL1 docs MD 画像リンク存在チェック (実ファイル解決)
    4. converter 修正:
       - `rst_ast_visitor._walk_section` が level を記録 / `md_ast_visitor` 同
       - `Section` dataclass / JSON schema に `level` 追加
       - `inline_reference` / `inline_inline(role=ref)` / `image` / `figure` を MD リンク/画像形式で出力
    5. `docs.py._render_full`: level 別 heading 出力
    6. `docs.py._rewrite_asset_links`: `assets/{file_id}/...` 相対パスを docs MD からの相対に rewrite (既存 `assets/` 先頭の rewrite を拡張)
    7. v6 再生成 → verify FAIL 0 + 実地確認
    8. SE + QA expert review → Findings 全件対応
- [ ] 22-B-12: 他バージョン (v5 / v1.4 / v1.3 / v1.2) で create → verify FAIL 0 を確認 (22-B-16 完了後)
- [ ] 22-B-13: nabledge-test v6 baseline 再取得 (旧 baseline 97.3% は履歴として保持) (22-B-16 完了後)

**備考**:
- Phase 21-C (旧番 — リリースノート行粒度) は 22-B に統合済。xlsx converter 書き直しで包括する
- 22-B-8 (verify 例外分岐) は 22-B-5a にリネームして先行実施済 — TDD 順序が verify → create となるため

---

## Not Started

### Phase 21-Z Z-5: nabledge-test v6 baseline (Phase 22-B-5 完了後)

**目的**: 確定した土台 (Z-2 / Z-6) と記述 (Z-1) + Phase 22 での Excel 分割変更を反映した baseline で、v6 の品質を数値ベースで固定。以降の他バージョン展開はここを基準に「劣化なし」ゲート。

- [ ] `nabledge-test 6` を実行してベースラインを取得
- [ ] 旧 baseline (memory 記録の 97.3%) と比較し、Excel 分割由来の file ID 変化を踏まえた評価
- [ ] ベースラインスナップショットを `baseline/v6/<timestamp>/` に保存してコミット

### Phase 19 (改称): 他バージョン展開 — v5 / v1.4 / v1.3 / v1.2

**前提**: Phase 22-B + Z-5 完了後。各バージョン単位で nabledge-test ベースラインを取りながら進める。

**展開順** (実装影響が小さい順): v5 → v1.4 → v1.3 → v1.2

各バージョン共通 Steps:
- [ ] `bash rbkc.sh create <v> && bash rbkc.sh verify <v>` → FAIL 分類と件数を記録
- [ ] バージョン固有 directive / role / substitution が Visitor の閉集合にない場合は設計書更新 + ユーザー承認 → 対応表追加
- [ ] verify FAIL 0 確認
- [ ] `nabledge-test <v>` で現行ベースラインと比較、劣化なしを確認
- [ ] コミット

### Phase 21-Z (続): 配信物クリーン化 → ドキュメント整備

Phase 19 完了後に実施。

**Z-4: setup スクリプトのゴミ残り対策**
- [ ] `tools/setup/setup-cc.sh` を vup 時に旧 `.claude/skills/nabledge-${v}/` を完全削除してから `cp -r` する形に修正 (現状は上書きのみで残留あり)
- [ ] `tools/setup/setup-ghc.sh` も同様
- [ ] 削除範囲はユーザー資産に影響しないよう skills plugin 配下のみに限定
- [ ] 手動テスト: 模擬 vup でゴミが残らないことを確認

**Z-3: CHANGELOG / README / 過去経緯要約**
- [ ] `.claude/skills/nabledge-6/plugin/CHANGELOG.md` の `[Unreleased]` に追記: 「知識ファイル生成を AI ベースからルールベースに変更しました。ハルシネーションが発生しない構造になり、公式ドキュメントの内容が正確に反映されるようになりました」
- [ ] nabledge-5 / 1.4 / 1.3 / 1.2 の CHANGELOG も同様
- [ ] `tools/rbkc/README.md` を現状構成に合わせて書き直し。動作確認手順記載
- [ ] `.work/00299/notes.md` を「Phase 21-Y〜22 で何をどう変えたか」に簡潔要約、不要中間ログは削除または集約
- [ ] GitHub Issue #309 への引き継ぎメモが現状と合っているか確認

---

## Done

- [x] **Phase 22-A**: RST/MD 側 docs MD 可読性改善 — attribution なし `block_quote` の `>` 剥がし。v6 bq_table 270 → 4 (残 4 は admonition 内正当)。commit `a203853ee`
- [x] **Phase 22-B-5a** (22-B-8 から先行): verify 層 TDD — `_xlsx_source_tokens(sheet_name=...)` / QO2 P1 一方向 containment / P2 strict verbatim fallthrough。7 + 3 tests GREEN。SE + QA review 済。commit `bd678e4aa`
- [x] **Phase 21-Z Z-1**: 設計書 §4 品質マトリクス ✅ 復元 — r2〜r9 bias-avoidance QA 反復レビューで critical 全解消。248 unit tests GREEN、v6 verify FAIL 0。commits `55bebe0cf` `1e46d6eb6` ほか
- [x] **Phase 21-Z Z-2**: 設計書・ソース・テストの MECE 化 — 設計書 2 本の重複/矛盾解消、MD を AST 経由に統一、QO3 双方向化、tolerance list 全廃、テスト/設計書対応表追加。commits `c8934ffc4` `c53cb19e3` `eee6129a8` `1f5954d23` `be604f880` `f013cd94e`
- [x] **Phase 21-Z Z-6**: 未使用コード削除 — commit `6c06b24c8`
- [x] **Phase 21-Y**: RST 処理を docutils AST + 共通 Visitor に全面書き直し — v6 verify FAIL 53→0、unit test 120 PASS。zero-exception / no-drop / AST-only 原則を設計書と実装に適用。commits `cf57a1718` `4ae3ada3b` `6ee04b9c4` ほか
- [x] **Phase 21-X** (SUPERSEDED by 21-Y): 調査 → 設計書更新 → tokenizer 方式で verify 実装。v6 FAIL 4812→56 まで削減した段階で、自前 tokenizer/converter が密結合のため docutils AST に全面切替 (Y)。調査成果 (`.work/00299/phase21x/`) は AST 方式に寄与
- [x] **Phase 21-W / 21-V** (SUPERSEDED by 21-X): 「原文のまま削除」方式 → converter のラベル解決/記法変換により substring 一致不能と判明、tokenizer 方式 (X) に移行
- [x] **Phase 21-K**: hints スコープアウト — 設計書とコードを "content のみ" に整備。Issue #309 を別 Issue として起票、資産 `.work/00299/handoff-hints/` に保全。commits `28fdef842` `b21197d73` `f7cff23a1` `983ae8301`
- [x] **Phase 21-A**: docs/README.md 生成 — `c238dc8f`
- [x] **Phase 21-B / 21-D / 21-E / 21-F / 21-H / 21-I / 21-J** (hints 時代の一連): Phase 21-K で hints を別 Issue に分離したため実質クローズ
- [x] **Phase V 系 (V-skip / V-hints / V2-* / V4 / V0 / V1 / V2-1〜3 / 17-R)**: verify の初期実装・再構築。`86dd660e` 他
- [x] **Phase 1〜16**: RST/MD/Excel converter 初期実装、CLI、v1.x 対応、各種バグ修正 — commits `f78304b4`〜`008e8420`

---

## 参考履歴: 前 session (session 56) の失敗

Phase 22-B-5 着手時に以下を破ったため全 revert された:
- TDD 順: verify テスト → RED → verify 実装 → GREEN → RBKC 実装 の順序を守らなかった
- verify 変更の事前承認を取らなかった (本来は設計書既定ならスキップ可だが、当時は逸脱)
- expert review の逐次実行を怠った

session 57 では上記を遵守して 22-B-5a (verify 層) を TDD + SE/QA review 付きで完了 (`bd678e4aa`)。以降も同じ順序で進める。
