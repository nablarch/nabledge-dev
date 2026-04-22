# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-23 (session 48 — Phase 21-Y / Y-1 完了。docutils AST probe を全 5 バージョン 2,581 RST に実施、v6/v5 は parse error 0 件、v1.x は WARNING 中心で真の parse 失敗 5 件のみ。grid-table rowspan (`morerows`) / substitution / admonition 14 種 / table 3 種 / footnote / transition はすべて AST node として取得可能。Sphinx 固有 role/directive は minimal shim で吸収できることを実証。結果を `.work/00299/phase21y/ast-probe.md` / `ast-probe.json` に保存、notes.md (session 48) にサマリ。**Y-2 (Visitor 設計) に進む判断をユーザーに要請中**。)

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

### Phase 21-Y: converter を docutils AST ベースで全面書き直し (最優先)

**目的**: 残 53 FAIL を 0 化。同時に、過去の patch 堆積による密結合と再発リスクを解消する。

**方針 (session 47 合意)**:

- `tools/rbkc/scripts/create/converters/rst.py` (1598 行) をゼロから書き直す
- 自前 parse (grid-table / simple-table / inline / directive / section splitter) を**全廃**し、`docutils.core.publish_doctree(source)` で得られる AST (doctree) を入力とする Visitor に変える
- プロジェクト固有の変換ロジックは「doctree node → MD」の Visitor のみ
- **TDD なし・verify 駆動**: `.claude/rules/rbkc.md` の「create-side は verify が quality gate、test 不要」方針に従う
- 旧 `rst.py` と `tests/ut/test_rst_converter.py` は書き直し完了時に削除

**docutils 利用可否の確認 (session 47)**:
- `docutils==0.22.4` が setup.sh で install 済、`GridTableParser` / `SimpleTableParser` / `publish_doctree` / `statemachine` 利用可能
- 現 `rst.py` も一部で `SimpleTableParser` / `StringList` を使っているが、CJK fallback や grid-table 自前実装と混在 → Phase 21-Y で AST 経由に一本化

**期待される効果**:
- grid-table rowspan / simple-table continuation / substitution 順序 / rowspan 変則 separator 等、現 converter が苦手としていた構文は docutils が解決済
- CJK の display-width 問題は tableparser 固有。AST 経由なら回避可能 (`publish_doctree` は CJK でも動く想定、X-Y-1 で実測)
- inline (role/ref/literal/substitution) が doctree ノードとして構造化済 → 自前 regex 不要
- 設計書の独立性原則 (`rbkc.md` / `rbkc-verify-quality-design.md` §2-2) と整合

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

#### Y-2: Visitor 設計の確定

- [ ] X-2 の成果物 (`.work/00299/phase21x/inline-patterns.json` / `block-patterns.json` / `transform-rules.md`) を参照しつつ、doctree node → MD の対応表を作る
- [ ] node → MD 対応表を `tools/rbkc/docs/rbkc-converter-design.md` として新規作成
  - section / title / paragraph / literal / emphasis / strong
  - reference (`:ref:` / external / named / anonymous)
  - substitution_reference / target / footnote / footnote_reference
  - bullet_list / enumerated_list / definition_list / field_list
  - table (grid / simple / list-table)
  - admonition (14 種、`scripts/common/rst_admonition.py` に委譲)
  - literal_block / code (言語アノテーション付き)
  - image / figure / raw
  - comment / transition / line_block
- [ ] 設計書レビューをユーザーに依頼 (レビューなしでは実装着手しない)

#### Y-3: 新 converter 実装 (feature branch 内で clean cut)

- [ ] 旧 `rst.py` を `rst_legacy.py` にリネーム (switch は使わず、すぐ戻せる状態だけ維持)
- [ ] `rst.py` を `publish_doctree` + Visitor で書き直し
  - [ ] `RSTConverter.convert(source, file_id, targets, source_dir, substitutions) -> RSTResult`
  - [ ] Visitor 実装 (Y-2 対応表通り)
  - [ ] `scripts/common/rst_admonition.py` / `rst_substitutions.py` / `rst_include.py` の共通モジュールは流用
  - [ ] cross-ref 解決 hook (targets 辞書経由) は doctree transform で対応
- [ ] `bash rbkc.sh create 6` が完走することを確認
- [ ] 旧 `rst_legacy.py` 削除
- [ ] `tests/ut/test_rst_converter.py` 削除 (rbkc.md 方針通り)

#### Y-4: v6 verify FAIL 0 まで収束

- [ ] `bash rbkc.sh create 6 && bash rbkc.sh verify 6` → FAIL 0
- [ ] FAIL が残る場合は以下のいずれか:
  - (a) Visitor の漏れ → Y-2 対応表 + Visitor を更新
  - (b) tokenizer 側の抜け → 設計書更新 + tokenizer 更新 (ユーザー承認)
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
- [ ] `tools/rbkc/README.md` の converter 説明を「docutils AST ベース Visitor」に更新
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

### Phase 18: 統合検証 — v6 完了

**前提**: Phase 21-V 完了後

**Steps:**
- [ ] nabledge-test v6 実行 — ベースライン比で劣化なし確認
- [ ] 問題があればユーザー報告

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

### Phase 21-C: リリースノート・セキュリティ対応表の粒度が粗い

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
