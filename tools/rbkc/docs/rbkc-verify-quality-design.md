# RBKC verify 品質保証設計

## 1. 目的とスコープ

### 1-1. 目的

RBKC（RST/Markdown/Excel → JSON 知識ファイル変換）の出力品質を自動検証し、nabledge が正確な Nablarch 知識を提供することを保証する。

### 1-2. 検証対象

| ソースフォーマット | 公式ドキュメント | 出力形式 |
| --- | --- | --- |
| RST | Nablarch 解説書 | 知識ファイル（JSON）、閲覧用知識（docs MD） |
| Markdown | Nablarch システム開発ガイド | 知識ファイル（JSON）、閲覧用知識（docs MD） |
| Excel | セキュリティ対応表、リリースノート | 知識ファイル（JSON）、閲覧用知識（docs MD） |

### 1-3. スコープ外

RBKC の内部実装（converters、resolver 等）の正しさ。verify はソースと出力だけを見る。独立性の詳細は 2-2 参照。

hints（キーワード索引）は RBKC のスコープ外である。RBKC は content（タイトル + 本文）のみを生成し、hints は別 Issue の AI 駆動フローで扱う。したがって verify も hints を検証しない。

---

## 2. 品質基準

### 2-1. 品質水準

Nablarch は大規模金融システム等の重要インフラで使用されるミッションクリティカルなエンタープライズフレームワークである。nabledge はその知識を提供するため、同等の品質基準が求められる。

- **ゼロトレランス**: 1% のリスクも許容しない
- **品質は二値**: 正しいか正しくないか。「十分に良い」は存在しない
- **verify は品質ゲート**: verify が FAIL を報告したら修正は RBKC 側で行う。verify を弱めて出力をパスさせてはならない
- **100% コンテンツカバレッジ必達**: ソースに存在するコンテンツトークン（テスト用語の coverage ではなく、ソース側テキストの取込率を指す）が JSON に欠落していれば RBKC のバグ

> **注意**: 上記の品質水準は verify が全チェック項目を実装し終えた状態を前提とする。4 章のマトリクスで ❌ が残る限り、verify PASS はゼロトレランス達成を意味しない。現状の verify PASS を品質保証と誤認しないこと。

### 2-2. verify の独立性原則

verify は RBKC の create 側実装から独立していなければならない。独立性は**向き**で定義する:

- verify → create 実装 の依存は禁止（`scripts/create/` 配下の converters / resolver / run 等をインポートしない）
- create → verify の依存も禁止（相互依存を避ける）

ただし、**ソースフォーマット仕様由来の共通ロジック**は create と verify の両方から利用してよい。これは独立性原則に抵触しない:

- `scripts/common/` 配下のモジュール（RST 仕様由来の純粋ロジック層）
- 外部の公式 RST パーサー（`docutils`）および `scripts/common/rst_ast.py` を経由した AST ユーティリティ

共通モジュール経由で create と verify が**別々に**AST を consume し、それぞれ独立に正しく動くことで品質ゲートが担保される。共通モジュールが create と verify の間のデータを受け渡すことは禁止する。

この共有により、「RST 仕様の解釈」がコード 2 箇所で分岐する危険（tokenizer と converter が仕様からドリフトする問題）を構造的に排除する。

独立性原則の例外は次の 1 種類に限る。これ以外の例外追加は 5 章の変更プロセスを要する。

| 例外 | 対象チェック | 根拠 |
| --- | --- | --- |
| 出力間整合の参照 | QO1, QO2, QO4 | docs MD と index.toon は JSON の派生物。JSON を期待値として照合する |

### 2-3. RBKC の契約前提

verify は次の RBKC 契約を前提とする。契約違反は RBKC 側のバグであり、verify の責務ではない。

- **セクション順序保存**: JSON の `sections` 配列は、ソース上のセクション登場順と一致する
- **content の連続性**: JSON 各セクションの `content` はソースの連続部分文字列から導出される（空白・改行は正規化されうる）

この契約により、QC4 の「期待位置」が定義される（3-1 参照）。

---

## 3. 品質チェック

品質観点 ID は QC（コンテンツ）、QL（リンク）、QO（出力）+ 連番。各サブセクションは「品質観点と検証状況」→「検証方法」の順で記述する。

### 3-1. コンテンツ検証（QC1–QC5）

**品質観点と検証状況**:

| ID | 観点 | 定義 | 判定手順 | RST | MD | Excel |
| --- | --- | --- | --- | --- | --- | --- |
| **QC1** | 完全性 | ソースのコンテンツが JSON に欠落している | 削除手順 → 手順3 | ⚠️ | ⚠️ | ⚠️ |
| **QC2** | 正確性 | ソースにないコンテンツが JSON に混入している | 削除手順 → 手順4 | ⚠️ | ⚠️ | ⚠️ |
| **QC3** | 非重複性 | 同一コンテンツが JSON に重複して含まれている | 削除手順 → 手順4 | ⚠️ | ⚠️ | ⚠️ |
| **QC4** | 配置正確性 | ソースのセクション A のコンテンツが JSON の異なるセクションに配置されている | 削除手順 → 手順2 | ⚠️ | ⚠️ | — |
| **QC5** | 形式純粋性 | フォーマット固有の構文記法が JSON に残留している（RST: `:role:`・`.. directive::` 等、MD: raw HTML・エスケープ文字等） | 独立チェック | ⚠️ | ⚠️ | — |

#### 削除手順（QC1–QC4 共通、RST/MD 対象）

RST/Markdown コンバーターは原文を逐語的に保持せず、inline 記法（`:ref:`、`` ``code`` ``、`` `text <url>`_ `` など）・ブロック記法（admonition、table、substitution 等）を Markdown 等価形式に変換する。したがって「JSON テキストをオリジナルのソースから substring 削除する」手法は機械的に成立しない（ソース原文に対応する部分文字列が存在しない）。

これを解決するため、**検証の対象を「原文ソース」ではなく、**tokenizer で正規化した「正規化ソース」**に切り替える。正規化ソースは MD 等価のプレーンテキストに揃えられており、JSON content（同じく MD）と substring 削除可能な共通形式を持つ。

```
[原文ソース]
    │
    ├─ 手順0: tokenizer で字句解析し、各 token を MD 等価表現に変換
    │
    ▼
[正規化ソース]                                    [JSON content/title]
    │                                                     │
    │       ← 順次削除（JSON 順 = ソース登場順を前提） ──┘
    │
    ├─ 削除できなかった JSON テキスト → 誤追加/重複 → FAIL（QC2, QC3）
    ├─ 前セクションの削除位置より前にしか見つからない → FAIL（QC4）
    │
    └─ 削除後の正規化ソース残存テキスト → 構文要素のみか？ → PASS / FAIL（QC1）
```

#### 手順 0: ソース前処理（docutils AST による正規化）

RST の公式パーサー（`docutils.core.publish_doctree`）を `scripts/common/rst_ast.py` 経由で呼び出し、原文ソースを doctree（AST）に変換する。その doctree を node → MD 対応表に従って Visitor で走査し、正規化 MD を生成する。

- **仕様準拠の保証**: 構文解釈は docutils 公式実装に委ねる。自前で regex による parse を行わない。これにより「tokenizer と converter が RST 仕様の解釈で分岐する」構造的バグを排除する。
- **order 非依存**: AST は入力ソースを一度で構造化済みであり、Visitor は node ごとに独立した純粋関数で MD を生成する。
- **create と共通**: `common/rst_ast.py` および node → MD 対応表は create / verify の両方が consume する（2-2 独立性原則参照）。create は doctree → JSON/MD、verify は doctree → 正規化 MD として使い分けるが、**AST 取得と node → MD 対応表は 1 箇所**で管理する。
- **例外禁止原則 (zero-exception principle)**:
  - 未登録 node → **FAIL (QC1)**、silent な children 再帰 fallback は禁止
  - 未登録 role → **FAIL (QC1)**、silent に raw テキスト表示する fallback は禁止
  - 未解決 reference / substitution → **FAIL (QC1)**、silent に text を返す fallback は禁止
  - 情報を「廃棄 (drop)」する対応表エントリは、実データで**対象文字列が 1 件も知識として価値がない**ことを確認した上でのみ許容する（alt / figure caption / table title 等はすべて保持する）
  - 対応表追加 / 変更は 5 章の変更プロセスを経る

##### node → MD 対応表の範囲と所在

docutils が出力する全 node 種別に対して MD 出力規則を定める。対応表は別ドキュメント `tools/rbkc/docs/rbkc-converter-design.md` で一覧管理し、本書は対応表が満たすべき**原則**のみを規定する。

対応表が網羅すべき node 種別（docutils 公式）:

- 構造: `document` / `section` / `title` / `paragraph` / `transition`
- インライン: `Text` / `strong` / `emphasis` / `literal` / `title_reference` / `inline` / `reference` / `target` / `substitution_reference` / `substitution_definition` / `footnote_reference` / `citation_reference` / `problematic` / `system_message`
- リスト: `bullet_list` / `enumerated_list` / `list_item` / `definition_list` / `definition_list_item` / `term` / `definition` / `field_list` / `field` / `field_name` / `field_body` / `line_block` / `line`
- ブロック: `block_quote` / `literal_block` / `doctest_block`
- テーブル: `table` / `tgroup` / `colspec` / `thead` / `tbody` / `row` / `entry`
- 画像/図/注記: `image` / `figure` / `caption` / `legend`
- 注: `note` / `tip` / `warning` / `important` / `attention` / `hint` / `admonition` / `caution` / `danger` / `error`
- 参照/索引: `footnote` / `citation` / `label`
- その他: `topic` / `sidebar` / `rubric` / `container` / `compound` / `raw` / `comment`

##### 対応表が満たすべき原則

1. **閉集合**: 対応表は上記の docutils node 種別を閉集合として列挙し、各 node に出力規則（MD 生成 / 廃棄 / 子 node への再帰）を割り当てる。
2. **再帰原則**: body を持つ node（`section` / `footnote` / `note` / `admonition` / `figure` / `list_item` / `entry` 等）は、子 node 列を再帰的に Visit して MD を生成する。これにより「footnote body に code-block がネストされる」等の構造が自動的に正しく処理される。
3. **未登録 node → FAIL**: 対応表に未登録の node が出現した場合、verify は FAIL（QC1: 未対応 node）を報告する。対応表追加は 5 章の変更プロセスを経る（silent drop しない）。
4. **parse warning の扱い**: docutils が `system_message` を埋め込んだ場合（ソース側の RST 仕様違反）、`system_message` 自体は出力しないが、周辺の `problematic` node は原文テキストとして保持する。parse error（halt 相当）は FAIL として報告する。
5. **create / verify 対称**: create は doctree から JSON/MD を生成し、verify は doctree から正規化 MD を生成する。両者が参照する対応表は 1 本に統一する。

##### 外部ファイル参照（include / literalinclude）

`.. include::` / `.. literalinclude::` は `scripts/common/rst_ast.py` の `parse()` が docutils に `file_insertion_enabled=True` を渡すことで doctree 構築時に展開される。循環検出・深さ制限は docutils 本体が実装しているため、プロジェクト側で独自に管理しない。

##### Label / substitution の解決

`:ref:`label`` / `|name|` 等の参照は、docutils の transform によって doctree 上で解決される（`reference` node の `refid` / `refuri` 属性、`raw` / text への置換）。create は解決後ラベルのタイトル文字列を使い、verify は doctree 上のテキスト表現を正規化 MD として使う。

##### line-continuation の扱い

行末バックスラッシュ `\` は docutils が paragraph 組み立て時に空白へ正規化する。Visitor 側の追加処理は不要。

#### 手順 1–4（正規化ソースに対する削除）

1. **抽出**: JSON の top-level `title` / top-level `content` / 各セクション `title` / 各セクション `content` を JSON 順のテキストリストとして抽出する。削除の単位は各フィールドの文字列全体（1フィールド = 1単位）。抽出順序は「top-level title → top-level content → sections[0].title → sections[0].content → sections[1].title → ...」とする。

   **正規化**: 各テキストに対して、空白・改行正規化（連続する空白→単一スペース、行末空白除去）のみを適用する。Markdown 構文は**除去しない**。手順 0 で正規化ソースが既に MD 等価形式に揃っているため、JSON 側の MD 構文記号はそのまま比較される。

2. **削除と配置チェック（QC4）**: **手順 0 で生成した正規化ソース**を対象に、手順1のリストを JSON 順に削除する。各要素の削除位置（正規化ソース上のオフセット）を記録する。
   - JSON 順 i 番目要素の削除位置が、i-1 番目の削除位置よりも前であれば **FAIL（QC4: 配置ミス）**
   - 削除位置が前に無く、後ろにも無い（そもそも見つからない）場合は手順4 の対象に回す

3. **残存チェック（QC1）**: 削除後の正規化ソースの残存テキストをチェックする。**空白文字 / 改行 / タブ以外のテキスト**が残っていれば **FAIL（QC1: 欠落）**。例外リスト・許容構文要素リストは設けない (詳細は「残存判定の基準」参照)

4. **未削除チェック（QC2, QC3）**: 手順2で正規化ソースから削除できなかった JSON テキストをチェックする。
   - 正規化ソース中に当該テキストが一度も出現しなかった → **FAIL（QC2: 誤追加）**
   - 既に削除済みの領域と重複していた（ソース中に複数回出現し、先行セクションで消費済み） → **FAIL（QC3: 重複）**

**判定分岐のまとめ**:

| 状況 | 判定 |
| --- | --- |
| Visitor が対応表未登録の node / role を検出 | QC1（未対応構文） |
| Visitor が未解決 reference / substitution を検出 | QC1（未解決参照） |
| docutils が parse error を返した | QC1（未対応ソース） |
| 正規化ソース残存に**空白・改行以外**のテキストが残った | QC1（欠落） |
| JSON テキストが正規化ソースに全く存在せず | QC2 |
| JSON テキストが正規化ソースに存在するが先行削除済み | QC3 |
| 削除位置が JSON 順より前に逆行 | QC4 |

#### 残存判定の基準（no-tolerance）

手順 0 の Visitor が出力する正規化ソースと、JSON 側の MD は**完全に同じ記法で揃っている**前提で sequential-delete を行う。したがって手順 3 の残存チェックでは:

- **空白文字 / 改行 / タブ以外のテキストが残ったら QC1 FAIL**
- 許容構文要素リスト・許容残存パターンといった例外リストは**設けない**
- 過去に必要とされた「許容残存」は、Visitor と JSON 側の MD 記法が揃っていない (ドリフトしている) ことの徴候だった。Visitor / JSON 双方の MD 生成ロジックを共通化することで、例外リストは不要となる

JSON content の MD 記法も create 側が `scripts/common/rst_ast_visitor.py` 経由で出力し、verify 側の正規化ソースと同じヘルパー (`scripts/common/rst_ast.py` の `escape_cell_text` / `normalise_raw_html` / `fill_merged_cells`) を使う。両側の記法揃えが create/verify 共通モジュールで構造的に保証される。

#### QC5 形式純粋性（独立チェック）

JSON の top-level `title` / top-level `content` / 全セクション `title` / 全セクション `content` を対象に、フォーマット固有の構文パターンが残留していないかを正規表現で検査する。

- **RST**: `:role:\`text\`` パターン、`.. directive::` パターン、`.. _label:` ラベル定義
- **RST（title フィールドのみ）**: 見出しアンダーライン（`====`、`----` 等）。content フィールドではコードブロック内の `===` や `---` が正当に出現しうるため検査しない
- **MD**: `<[a-zA-Z]` で始まる raw HTML タグ（`<details>`、`<summary>`、`<br>` 等）、`\*`・`\_` 等のバックスラッシュエスケープ

いずれかのパターンが検出された場合 → **FAIL（QC5）**

#### Excel 検証（sequential-delete）

**verify の独立性原則（Excel）**: verify は Excel コンバーターの実装を参照しない。verify が正しい検証ロジックを定義し、コンバーターはそれを通るように実装される。verify をコンバーターの現在の出力に合わせて変更してはならない。

**方向性**: Excel は RST/MD と削除方向が逆になる。RST/MD では「JSON テキストをソースから削除」するが、Excel では「ソースセル値を JSON テキストから削除」する。

理由：Excel のソースはセルが原子単位であり構造化テキストではない。各セル値が JSON に取り込まれているかは、セル値を JSON テキストから順に削除して残存（余分なテキスト）を見ることで検証する。

**ファイル粒度** (Phase 22-B): 1 xlsx/xls ファイルは各シートごとに 1 JSON + 1 docs MD に分割される。ファイル ID はシート数 1 の場合 `{basename}`、シート数 ≥ 2 の場合 `{basename}-{sheet_slug}` を使う。verify は 1 JSON 対 1 シートで検証する。

**ソーストークンの構築**: 当該 JSON に対応する 1 シートの非空セル値（前後空白除去後、空文字を除く）を行優先・列順に取り出したリストをソーストークンとする。`.xlsx` と `.xls` の両形式に対応する。

**P1 シートにおけるヘッダ行の展開** (Phase 22-B): P1 シート（`rbkc-converter-design.md` §8-2 で定義される表形式シート）は、列名が各データ行の section に `{列名}: {値}` 形式で再出現する（§8-4 JSON スキーマ）。Excel ソースではヘッダ行のセル値は 1 回しか出現しないため、そのままでは sequential-delete の残存チェック (QC2) が列名ごとに「データ行数 - 1」回の偽陽性を生む。

したがって P1 シート（JSON の `sheet_type == "P1"`）に限り、ヘッダ行のセル値（= 列名）のトークンをデータ行数ぶん複製してから sequential-delete に渡す。

- **対象**: `sheet_type == "P1"` のシートのみ
- **対象セル**: verify が `rbkc-converter-design.md` §8-2 の header 検出規則（ヘッダ開始行検出、マージセル展開、副ヘッダ結合）に**のみ**依拠して特定するヘッダ行（+副ヘッダ行）のセル値。verify は converter 実装を参照してはならない
- **複数行ヘッダ**: マージ後の `メイン/副` 形式で複製する（§8-3 の合成規則）
- **複製数 (データ行数)**: 当該シートの「ヘッダ行以降の非空行数」（§8-4 P1 規約）から verify が独立に算出する。JSON の section 数を参照してはならない（参照すると QC2 がトートロジーになる）
- **§8-2 が曖昧な入力**: header 検出に失敗したシートは P2 として扱う（§8-2 のルール）。converter と判定が食い違った場合 (converter 側 P1 / verify 側 P2 またはその逆) は QC2 / QC1 の残存または欠落として自然に FAIL する
- **P2 シート**: 展開なしで従来通り 1:1 照合する

**JSON テキストの構築**: top-level title + top-level content + 全セクションの title + 全セクションの content を空白で結合した単一テキスト。section title はセル値であるため JSON テキストに含める。

**削除手順**:

1. **削除**: 各ソーストークン（P1 の header 展開後）を JSON テキストから先頭から順に検索・削除する。削除位置を記録する。
2. **QC1（欠落）**: JSON テキストから見つからなかったソーストークン → FAIL
3. **QC2（捏造）**: 全ソーストークン削除後に JSON テキストに残ったテキスト（空白・空行を除く）→ FAIL
4. **QC3（重複）**: ソーストークンが見つかったが、その位置が既消費領域と重複していた → FAIL

### 3-2. リンク検証（QL1–QL2）

**品質観点と検証状況**:

| ID | 観点 | 定義 | RST | MD | Excel |
| --- | --- | --- | --- | --- | --- |
| **QL1** | 内部リンクの正確性 | ソース内の内部リンク（`:ref:` / `:doc:` / `:numref:` / `:download:` / `.. image::` / `.. figure::` / `.. literalinclude::` / Markdown 相対リンク / Markdown inline image）が、**意図したページ・セクション・アセットを指す CommonMark MD リンクとして** JSON および docs MD に反映されていない | ⚠️ | ⚠️ | — |
| **QL2** | 外部リンクの一致 | 外部 URL が JSON および docs MD にソースと完全同一で含まれていない | ⚠️ | ⚠️ | — |

**前提の変更** (Phase 22-B-16): 従来「JSON はリンク構造を保持せずプレーンテキストのみ保持」としていたが、これを**変更**する。AI がキーワード検索を経ずに cross-document 参照を直接辿れるようにするため、RBKC は以下を出力する:

- JSON content と docs MD の両方に、RST の各内部リンクを **CommonMark `[text](path)` / `![alt](src)` 記法の MD リンク**として出力する
- JSON / docs MD で **同一文字列**を出力する (QO2 完全一致を維持するため)
- path 形式は docs MD の位置を前提とする (`.md` 拡張子、`docs/{type}/{category}/` からの相対)。AI 側は `.md` を対応 `.json` に読み替えるワークフローを持つ

これにより QC5 形式純粋性は崩れない (CommonMark `[text](path)` は QC5 の検出パターン `<[a-zA-Z]` raw HTML や `\*` エスケープに該当しない)。

**Sphinx 追従原則 (Phase 22-B-16b で確定)**: リンク解決・anchor 生成・display text の扱いで設計の判断に迷った場合、**RST の公式挙動 (Sphinx の HTML 出力) に合わせる**ことを既定とする。RBKC はルールベース知識変換であり、ソースとして RST を使う以上、RST の意味論 (Sphinx が採用しているもの) が正典であり、verify が独自に厳しくして RBKC が RST 上流より多く FAIL することは避ける。

- 参考実装は Sphinx (`sphinx-build`) の出力挙動。判断に迷ったら `/tmp` で小さな RST を書き Sphinx を走らせて HTML を観測し、それに合わせる
- ただし「Sphinx が黙って落としている」ケースは verify 側で可視化してよい (silent skip 禁止は維持)。Sphinx が WARNING を出す場合は RBKC も同等の WARNING を出し、ビルドは止めない
- 対象: `:ref:` / `:doc:` / `:numref:` / `:download:` / `.. image::` / `.. figure::` / `.. literalinclude::` の解決挙動 および anchor slug 生成

**AST 経由原則**: QL1 / QL2 の抽出は、ソースフォーマットの公式パーサーで取得した AST から読み取る。ソースを行単位の regex で直接走査してはならない (`_URL_RE` / `_RST_FIGURE_RE` / `_RST_REF_*` / `_MD_INTERNAL_LINK_RE` 等の独自 regex による抽出は禁止)。

- **RST**: `scripts/common/rst_ast.py` 経由で `docutils` AST を取得
- **Markdown**: `scripts/common/md_ast.py` 経由で `markdown-it-py` AST を取得
- **Excel**: QL 対象外

公式パーサーが CJK 境界やフォーマット固有の inline 構文を正しく解釈するため、regex 由来の false positive (URL が `」` まで伸びる、caption が inline 構文のみでも文字列比較される等) が構造的に排除される。

#### 3-2-1. 共通モジュール: `labels.py` / `github_slug.py`

QL1 強化に伴い、以下を `scripts/common/` に置く (§2-2 独立性原則: source-format 仕様由来の純粋ロジックは create / verify の両方から利用してよい):

- **`scripts/common/labels.py`**: `build_label_map(source_dir) -> dict[label, LabelTarget]` を返す。`LabelTarget = (title, file_id, section_title)`。従来 `label -> title` のみだった契約を拡張する。
  - `title`: target section (or document) の title 文字列
  - `file_id`: target が属する JSON / docs MD のファイル ID (scan.py の file_id 算出と同じ)
  - `section_title`: target section の title (top-level なら空文字)。docs MD アンカーの slug 計算に使う
- **`scripts/common/labels.py` (追加)**: `build_doc_map(source_dir) -> dict[rst_relpath, (title, file_id)]` を返す。`:doc:\`xxx/yyy\`` 解決用
- **`scripts/common/github_slug.py` (新規)**: GitHub Web の heading auto-anchor 生成規則に従う純粋関数 `github_slug(text: str) -> str` を提供する。仕様根拠は GitHub docs: 小文字化、空白を `-` に置換、ASCII 記号除去 (一部許容)、CJK/非ASCII はそのまま保持、重複時は `-1`/`-2` サフィックス (重複処理は同一 MD ドキュメント内でのみ発生)
  - 単体テストは GitHub 公式仕様由来の fixture (例: `"コード値の選択" -> "コード値の選択"`, `"Foo Bar" -> "foo-bar"`, 重複 `"Foo" "Foo"` -> `"foo"`/`"foo-1"`) で pin
  - create / verify とも本モジュールを経由する。circular test を避けるため、verify 側は anchor を独立に slug 再計算した上で、docs MD の実 heading slug と一致するかを検証する

**独立性 (§2-2)**: 上記 3 モジュールはすべて source-format 仕様由来の純粋関数であり、create / verify の間でデータを受け渡さず、各側が独立に consume する。

#### 3-2-2. dangling reference の扱い (Sphinx 追従)

「dangling link」= ソース AST に reference は存在するが、解決先のファイル / label が見つからないケース。**Sphinx 追従原則 (§3-2)** により、Sphinx の挙動に合わせて扱う:

- 未解決 `:ref:` label (label_map に無い) → **WARNING ログ + display text fallback** (Sphinx の挙動: `<span class="xref">text</span>` としてリンクなしで display text を残す、build は WARNING のみ)
- 未解決 `:doc:` path (doc_map に無い) → **WARNING ログ + display text fallback** (同上)
- docutils parse exception を握りつぶして QL1 抽出を無言 return → パース段階の失敗自体は **QC1 FAIL** (Sphinx も parse error は build failure)
- verify は QL1 WARNING としてログに列挙する (silent skip 禁止は維持)。FAIL 昇格は ソース側修正の判断材料として保留

**labels.py の label 解決規則 (Phase 22-B-16b step 2 で確定、Sphinx 挙動に準拠)**:

Sphinx は `.. _label:` の直後要素 (heading であれ definition-list であれ paragraph であれ) を anchor 点にし、**label 名そのもの** を slug として HTML `id` に埋め込む。RBKC もこれに追従する:

1. **anchor slug**: `github_slug(label_name)` — label 名を slug 化したものがそのまま anchor になる (target の heading text を slug 化するのではない)
2. **display text (bare `:ref:\`label\``)**: label 直下の要素から推定した短い title 文字列 (heading の場合は heading text、definition-list の場合は最初の term、他は直近の enclosing section title)
3. **display text (`:ref:\`text <label>\``)**: `text` をそのまま使う
4. **ファイル内に heading が一切無い位置の label のみ** `UNRESOLVED` → それでも dangling として WARNING 扱い (§3-2-2 の真性 dangling と同じ)

この規則により、v6 の `big_picture.rst:20` `.. _runtime_platform:` (block_quote 内) は `anchor=runtime_platform` / `display=実行制御基盤` (直下 definition-list の term または enclosing section title) で正しく解決される。

#### 3-2-3. QL1 抽出と検証

ソース AST から内部リンク候補を収集し、JSON / docs MD の両側で下表の整合を検証する。

| AST node | 抽出するもの | JSON content / docs MD 双方の期待形式 | verify 検証 (JSON side) | verify 検証 (docs MD side) |
| --- | --- | --- | --- | --- |
| `reference` (`refid` / `refname`、refuri なし) | label 解決後の (title, file_id, section_title) | `[title](../../{type}/{category}/{file_id}.md#{github_slug(section_title)})` | target `.json` がディスクに存在 + target JSON の `sections[]` に section_title が実在 | target `.md` がディスクに存在 + target docs MD の heading slug と anchor が一致 |
| `inline` role=`ref` | 同上 (`label` 側から解決) | 同上 | 同上 | 同上 |
| `inline` role=`doc` | `:doc:\`path\`` or `:doc:\`text <path>\`` を doc_map で解決 | `[title](../../{type}/{category}/{file_id}.md)` | target `.json` がディスクに存在 | target `.md` がディスクに存在 |
| `inline` role=`numref` | ref と同様 (label_map で解決) | 同上 (ref と同じ形式) | 同上 | 同上 |
| `inline` role=`download` | `:download:\`text <path>\`` の path 解決 | `[text](assets/{file_id}/{basename})` | `knowledge/assets/{file_id}/{basename}` の実ファイル存在 | `docs/../../knowledge/assets/{file_id}/{basename}` の実ファイル存在 (同一 asset を docs.py が相対 rewrite) |
| `image` | `:alt:` 属性 + `:uri:` を source dir からの相対で resolve | `![alt](assets/{file_id}/{basename})` | `knowledge/assets/{file_id}/{basename}` の実ファイル存在 | 同上 (docs.py rewrite 後の相対) |
| `figure` | child `caption` (alt 扱い、fallback は画像 basename) + child `image` の uri | `![caption](assets/{file_id}/{basename})` | 同上 + caption 文字列が JSON content に出現 | 同上 |
| `literal_block` (`.. literalinclude::` 由来) | docutils が展開済コード + source file 名 | fenced code block (既存) | code body が JSON content に含まれる (既存 QC1 経由) | 同左 (QO2 完全一致経由) |
| Markdown `link_open` (`href` が相対パス) | link text + href | `[text](href)` (相対を docs MD 位置基準に解決) | target `.md` 存在 | 同左 |
| Markdown `image` (インライン画像) | `alt` / `title` / `src` | `![alt](src)` (相対を docs MD 位置基準に解決) | target 画像ファイル存在 | 同左 |

**caption / alt が空または RST inline のみの場合**: ファイル名 fallback (例: `foo.png` を alt として採用)。

**dangling reference の扱い**: 上表の各「存在」チェックで不在が検出された場合、**QL1 FAIL (dangling link)** を報告する。QC1 ではなく QL1 に分類する理由は、ソース AST には参照が**あった**ため「欠落」ではなく「解決先が無効」だからである。

**anchor 一致の circular 回避**: verify は docs MD の heading を読み取り、各 heading の text を `github_slug.py` で slug 化してから anchor と比較する。create 側 (converter + docs.py) とは別パスで slug を再計算することで、「docs.py が間違った slug を埋め込んでも verify が同じ slug で通してしまう」を防ぐ。`github_slug.py` の仕様は GitHub docs 由来の独立 fixture で pin するため、函数自身の正しさは create 実装とは独立に保証される。

QL2（外部リンク）: ソース AST から `http://` / `https://` で始まる URL を AST ノード属性として列挙し、URL 文字列が JSON content 内に完全一致で含まれているかを確認する。

- **RST**: `reference` node の `refuri` 属性
- **Markdown**: `link_open` トークンの `href` 属性、および CommonMark autolink (`<http://…>`) の `refuri`
- 正規表現でソース全体から URL を抽出することは禁止 (CJK 括弧 / フォーマット内部記法で境界を誤認しやすいため)
- RST の `.. |sub| raw:: html` substitution body 内 URL も `raw` node として AST に現れるため、対象から除外する場合は AST ノードの属性で判定する

### 3-3. 出力検証（QO1–QO4）

**品質観点と検証状況**:

| ID | 観点 | 定義 | RST | MD | Excel |
| --- | --- | --- | --- | --- | --- |
| **QO1** | docs MD 構造整合性 | docs MD の構造要素（タイトル・セクションタイトル・セクション順序）が JSON と一致していない | ⚠️ | ⚠️ | ⚠️ |
| **QO2** | docs MD 本文整合性 | JSON 各セクションの content が docs MD に完全一致で含まれていない | ⚠️ | ⚠️ | ⚠️ |
| **QO3** | docs MD 存在確認 | JSON に対応する docs MD が存在しない | ⚠️ | ⚠️ | ⚠️ |
| **QO4** | index.toon 網羅性 | 変換済み JSON が index.toon（知識ファイルの検索インデックス）に未登録 | ⚠️ | ⚠️ | ⚠️ |

> **旧 QO3（目次ページの除外）は QC1/QC2 のスコープで扱う**: 目次ページが実コンテンツを持たないまま JSON 化された場合、QC1 のソース残存チェックで RBKC のバグとして検出される。独立した品質観点を設けない。

**QO3 の下位チェック (README.md)**: `docs_dir/README.md` には全 MD ページの目次とページ数宣言が含まれる。QO3 の一部として以下を検証する:

- README.md 自体が存在すること
- README.md に `N ページ\n` 形式の行が存在すること (宣言が無い場合は FAIL)
- 宣言されたページ数と実際の .md ファイル数 (README 自身を除く) が一致すること

**検証方法（docs MD）**: docs MD は JSON の人間可読レンダリングであるため、両者は完全に一致しなければならない。JSON が FAIL の場合は docs MD も自動的に FAIL とする。

- **QO1 構造整合性**:
  - タイトル: JSON top-level `title` == docs MD の `#` 見出し
  - セクションタイトル: JSON 各セクションのタイトルが docs MD の `##`/`###`/`####` に存在し、かつ JSON と同じ順序で並んでいる
  - **Section level 一致** (Phase 22-B-16): JSON `sections[].level` (2/3/4...) と docs MD の対応 heading の `#` 数が一致する。RST h2 → `level: 2` → docs MD `##`、h3 → `level: 3` → `###`、h4 → `level: 4` → `####`。RBKC 既定では `sections[].level >= 2` (h2 以降のみが section として切り出される)
  - sections が空で top-level content のみの場合: docs MD に `##` 見出しが出現しない
  - **Excel P1 例外** (Phase 22-B): P1 シートの docs MD は MD table で再構成される (§8-5)。行単位の section は `##` 見出しではなくテーブル行として表現されるため、section-title `##` チェックは P1 では実施しない。section 構造の整合性は §3-4 QP (列-値ペアリング + section/データ行数一致) で閉じる。`#` タイトル一致チェックは P1 にも従来通り適用する。P1 sections には level を出力しない (段落主体の P2 も同様)
- **QO2 本文整合性**:
  - JSON top-level `content` が docs MD の `#` 見出し直下に完全一致で含まれている
  - JSON 各セクションの `content` が docs MD に完全一致で含まれている
  - **Excel 例外** (Phase 22-B): Excel 由来の docs MD は人間閲覧のため元の表を MD table として再構成する (1 行 = 1 データレコード)。一方 JSON の検索索引性を保つため、JSON section.content は `{列名}: {値}\n` の縦列挙形式で持つ。したがって両者の形は異なり完全一致は成立しない。Excel ファイルに対しては **「JSON section.content に含まれる全てのセル値テキストが docs MD 内にも現れる」の一方向 (JSON ⊂ MD) のみをチェック** する。MD 側に追加される行 (列ヘッダ、罫線 `|---|`) は JSON に無くて良い。

**検証方法（index.toon）**: 変換済みの全 JSON ファイルが index.toon に登録されているかを確認する。登録漏れがあると nabledge の検索から除外される。具体的な判定:

1. **index.toon 不在**: `no_knowledge_content: true` でない JSON が 1 件でもあれば、**全 JSON を QO4 FAIL として列挙**する (検索インデックスが完全に欠落している状態)
2. **未登録 JSON**: `no_knowledge_content: true` でない JSON の相対パスが index.toon に列挙されていなければ FAIL
3. **dangling entry**: index.toon に列挙されている相対パスに対応する JSON が存在しなければ FAIL (検索でヒットした後にファイルが見つからず 404 になる状態を防ぐ)
4. **JSON parse 失敗**: `knowledge_dir` 配下の JSON が parse 失敗した場合は **QO4 FAIL** とする (silent skip 禁止。ゼロトレランスに基づき、壊れたファイルは検出対象とする)

いずれも「index.toon の内容と JSON ファイル群が完全に一致する」ことを双方向で確認する。

### 3-4. P1 シート 列-値ペアリング検証（QP、Excel 専用）

**品質観点と検証状況**:

| ID | 観点 | 定義 | RST | MD | Excel |
| --- | --- | --- | --- | --- | --- |
| **QP** | P1 列-値ペアリング | P1 シートにおいて、JSON 各 section の `{列名}: {値}` が Excel ソースの同一行・同一列のセル値と一致していない | — | — | ⚠️ |

**背景**: §3-1 Excel 節の sequential-delete (QC1–QC4) は bag 照合であり、セル値の欠落・捏造・重複は検出するが「列名に続く値が同一行の当該セル値ではない」タイプのずれは検出できない（例: row-N の `タイトル` 値が row-M の section に混入）。converter のインデックス計算バグや複数行ヘッダのマージミスで発生しうるため、ゼロトレランスの観点からこのギャップを独立検査 QP で閉じる。

**対象**: JSON の `sheet_type == "P1"` のシート。P2 シートは対象外（段落主体であり行対応が存在しない）。

**独立性**: verify は `rbkc-converter-design.md` §8-2 の header 検出規則と §8-4 の P1 規約に**のみ**依拠する。converter 実装を参照してはならない。

**検証手順**:

1. **ソース側**: verify 独自に Excel ソースから header 行（+副ヘッダ行のマージ）とデータ行を取り出し、「`{マージ後列名}: {セル値}`」のペアリスト (= 期待ペア) を 1 データ行ごとに構築する。空セルは空文字として扱う。
2. **JSON 側**: JSON の各 section.content を改行で行分割し、`:` の最初の出現で `{列名}` と `{値}` に分割する（値側に `:` が含まれてよい、spec §8-4 と verify の既存 QO2 P1 処理と整合）。
3. **section → 行の対応**: JSON section は spec §8-4 で「1 データ行 = 1 section」かつ「ヘッダ行以降のデータ行を順に section 化」と定義されているため、JSON section N と Excel データ行 N を対応付ける。
4. **照合**:
   - section 数 ≠ データ行数 → **QP FAIL (section_count_mismatch)**
   - section N の `{列名}: {値}` ペアが、データ行 N の期待ペア集合に含まれない → **QP FAIL (pair_mismatch)**
   - 期待ペアのうち、section N にペアとして含まれないもの → **QP FAIL (pair_missing)**（空セルは期待ペアに含めないため、空セル列を section に書かないのは許容）

**空セルの扱い**: データ行の空セル列は converter が section.content に書かない運用（§8-4 の縦列挙は「非空セルを列挙」と解釈）。期待ペア構築時も空セルは除外する。

**FAIL メッセージ**: ファイル ID、シート名、section インデックス (1-origin)、検出した不一致（期待 vs 実際）を含める。

---

## 4. 品質保証マトリクス

セクション 3 の各チェックの検証状況を一覧で確認できる。

凡例: ✅ 検証済み / ❌ 未実装 / — 対象外

> **マトリクスの ❌ は verify の穴を意味する**: 2-1 の「ゼロトレランス」「100% コンテンツカバレッジ」は、全項目が ✅ になった時点で初めて保証される。現状で verify PASS になっても、❌ の項目については品質未検証である。
>
> **✅ 付与のルール (bias-avoidance)**: マトリクスの ✅ は、**独立コンテキストの QA エキスパートレビュー (bias-avoidance 明示)** で当該 ID が通過した時点でのみ付与する。実装者自身が ✅ を付けない。不通過項目が 1 件でも残る間、マトリクス全体に ✅ を付与しない。

### 対応テスト (Z-2 整備)

各品質観点と対応するテストケースの所在は以下。新規チェック追加時にもこの表を更新し、設計書 ↔ テストの MECE を維持する。

| ID | テストクラス (`tests/ut/test_verify.py`) |
| --- | --- |
| QC1–QC4 (RST) | `TestCheckContentCompleteness` (RST ケース群) |
| QC1–QC4 (MD) | `TestCheckContentCompleteness` (MD ケース群) |
| QC1–QC4 (Excel) | `TestVerifyFileExcel` + `tests/e2e/test_cli.py` |
| QC5 | `TestVerifyFileQC5` (RST / MD 両対応) |
| QL1 JSON side (link resolution + target existence) | `TestCheckSourceLinks_JsonSide` (RST / MD) |
| QL1 docs MD side (dangling link + anchor slug) | `TestCheckSourceLinks_DocsMdSide` (RST / MD) |
| QL2 | `TestVerifyFileQL2` (RST / MD) |
| QO1 title / section title | `TestCheckJsonDocsMdConsistency_QO1` |
| QO1 section level (Phase 22-B-16) | `TestCheckJsonDocsMdConsistency_QO1_Level` |
| QO2 | `TestCheckJsonDocsMdConsistency_QO2` |
| QO3 | `TestCheckDocsCoverage` (JSON↔MD 1:1 存在確認 + README ページ数) |
| QO4 | `TestCheckIndexCoverage` |
| QP (P1 列-値ペアリング) | `TestCheckXlsxP1Pairing` |
| `github_slug.py` 独立仕様 (GitHub auto-anchor 再現) | `TestGithubSlug` (新規、tests/ut/test_github_slug.py) |
| `labels.py` LabelTarget / doc_map 構築 | `TestLabelMap` / `TestDocMap` (拡張) |

**✅ の成立条件**: 以下を**全て満たした上で**独立コンテキストの QA エキスパートレビュー (bias-avoidance 明示) で通過すること。

1. verify に実装が存在する (設計書 §3 準拠、silent fallback や不認可の skip なし)
2. 主要 FAIL ケースとエッジケースが unit test で RED→GREEN 固定されている (circular test 不可)
3. v6 実データに対して verify FAIL 0 件である
4. **QA エキスパートレビュー (bias-avoidance) を通過している**

### コンテンツ

| 品質観点 | RST | MD | Excel |
| --- | --- | --- | --- |
| **QC1** 完全性 | ✅ | ✅ | ✅ |
| **QC2** 正確性 | ✅ | ✅ | ✅ |
| **QC3** 非重複性 | ✅ | ✅ | ✅ |
| **QC4** 配置正確性 | ✅ | ✅ | — |
| **QC5** 形式純粋性 | ✅ | ✅ | — |

### リンク

| 品質観点 | RST | MD | Excel |
| --- | --- | --- | --- |
| **QL1** 内部リンクの正確性 (JSON side: link resolution + target existence) | ⚠️ | ⚠️ | — |
| **QL1** 内部リンクの正確性 (docs MD side: dangling link + anchor slug) | ⚠️ | ⚠️ | — |
| **QL2** 外部リンクの一致 | ✅ | ✅ | — |

### 出力

| 品質観点 | RST | MD | Excel |
| --- | --- | --- | --- |
| **QO1** docs MD 構造整合性 (title + section title + 順序) | ✅ | ✅ | ✅ |
| **QO1** docs MD section level 一致 (Phase 22-B-16) | ⚠️ | ⚠️ | — |
| **QO2** docs MD 本文整合性 | ✅ | ✅ | ✅ |
| **QO3** docs MD 存在確認 | ✅ | ✅ | ✅ |
| **QO4** index.toon 網羅性 | ✅ | ✅ | ✅ |

### 構造検証 (Excel P1 専用)

| 品質観点 | RST | MD | Excel |
| --- | --- | --- | --- |
| **QP** P1 列-値ペアリング | — | — | ⚠️ |

**現状**: Phase 21-Z Z-1 完了。r2〜r9 の bias-avoidance QA 反復レビューで critical は全て解消、spec §3 の各チェックに対して実装 + pass/fail 両方向の test pinning 済。v6 実変換に対して verify FAIL 0。r2 以降の各ラウンドのレビュー結果と対応履歴は `.work/00299/review-z1-r{N}/` に記録。

---

## 5. verify の変更ルール

verify は品質ゲートであり、その変更は厳密に管理する。

### 変更プロセス

1. 変更内容と理由をユーザーに説明する
2. ユーザーの明示的な承認を取得する
3. TDD で実装する（RED → GREEN）

### 許容される変更

- verify 自体のロジックバグの修正（例: 正規表現の誤り、範囲の間違い）
- 仕様上必要なチェックの追加
- 誤検知（false positive）の修正

### 許容されない変更

- RBKC の現在の出力に合わせて verify 基準を緩める
- チェックを無効化・スキップする
- RBKC 実装の詳細に合わせた回避策を追加する
- 独立性原則（2-2）の例外を出力間整合以外に追加する