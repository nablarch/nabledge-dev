# RBKC Converter 設計 — docutils AST node → MD 対応表

## 1. 目的

RST ソースを `docutils.core.publish_doctree` で AST 化したものを入力として、**正規化 Markdown** を生成する際の node → MD 対応表を定める。

本表は create / verify が共有する。両者とも `scripts/common/rst_ast.py` 経由で docutils を呼び、本表に従って Visitor で AST を走査する。

- **create**: AST → `RSTResult` (セクション分割済の構造体)。後段で JSON/docs MD に直列化。
- **verify**: AST → 正規化 MD 文字列（sequential-delete の対象となる「正規化ソース」）。

## 2. スコープと独立性

- `rbkc-verify-quality-design.md` §2-2 の独立性原則に従う
- 本対応表は create / verify の唯一の仕様。実装は本表を直接参照する
- 対応表未登録 node が出現したら **FAIL**（silent drop しない）。追加は設計書 §5 の変更プロセスを経る

## 3. 共通の原則

### 3-1. 再帰原則

`section` / `footnote` / `admonition` (14 種) / `list_item` / `entry` / `block_quote` / `figure` / `topic` / `container` / `compound` などの**body を持つ node** は、**子 node 列を順に再帰 Visit** して MD を生成する。

これにより「footnote body 内の code-block」「admonition body 内の table」「table cell 内の list」のような RST ネスト構造がすべて一貫して扱われる。

### 3-2. create / verify の出力差

| 側 | 出力単位 | 備考 |
|---|---|---|
| create | `RSTResult` (top-level title / top-level content / `sections: list[Section]`) | `section` node 単位で分割 |
| verify | 正規化 MD 文字列 (1 本) | section 境界は保持するが、全体を結合してフラットに |

両者とも以下の表の「MD 出力」列に従う。違いは「section で分割するか連結するか」のみ。

### 3-3. inline の扱い

paragraph・title 等のテキスト属性を持つ node の children として出現する inline node (`Text` / `strong` / `emphasis` / `literal` / `reference` / `substitution_reference` 等) は、文字列として連結し 1 行の MD テキストを生成する。

### 3-4. label / substitution の解決

docutils の transform が以下を解決済で AST に反映する:

- `:ref:`label`` → `reference` node (`refid` / `refname` 属性)
- `|name|` → `substitution_reference` → Substitutions transform 後は `raw` / `Text` ノードに置換
- `.. _label:` → `target` node (children の直後 section に id として付与)

Visitor 側は**解決後の AST をそのまま walk する**だけで、自前のラベル表は不要。

### 3-5. 未解決 substitution / 未解決 reference の扱い

docutils transform が解決できなかった `substitution_reference` / `reference` (`refname` のまま残存) は、create / verify とも **FAIL (QC1: 未解決参照)** を報告する。silent drop / fallback は禁止 (検証抜け穴になるため)。

### 3-6. 共通エスケープ・正規化ヘルパー

テーブルセル内の `|` / 改行エスケープ、`raw html` の entity decode 等、create / verify が一致して適用する必要のある文字列変換は、必ず `scripts/common/rst_ast.py` に共有ヘルパーとして実装し、両側がそれを呼び出す。個別実装禁止 (符号化の drift が sequential-delete の破綻原因になる)。

共有すべきヘルパー:

- `escape_cell_text(s: str) -> str` — `|` と改行を escape
- `normalise_raw_html(html: str) -> str` — `<br>`/`<br/>` → `\n`、`&nbsp;` → 空白、`&lt;` `&gt;` `&amp;` を decode。対象 entity / tag は Y-1 probe で確認したものに限定
- `fill_merged_cells(table_rows, morerows, morecols) -> list[list[str]]` — rowspan/colspan を空 cell 補完で展開。**マージ元セルの内容は top-left に配置し、他の占有セルは空文字**とする。create / verify は同じ結果を得る

## 4. node → MD 対応表

### 4-1. 構造

| Node | create | verify | 備考 |
|---|---|---|---|
| `document` | root。top-level title は最初の `title` child、top-level content は次の `section` 出現までの child 列の再帰 Visit 結果 | root。全 child の再帰 Visit 結果を連結 | |
| `section` | `Section(title, content)` として追加。title は最初の child `title`、content は残りの children の再帰 Visit 結果 | title を 1 行、body を再帰 Visit、末尾に空行 | |
| `title` | 最初の Text child を文字列化 | `<title>\n\n` | `section` 直下の場合 |
| `subtitle` | `title` と同様に文字列化 (document 直下 = document title の補足) | 同左 | v5/v6 に 2-7 件、v1.x に 4-7 件出現 |
| `docinfo` | 子 node (`field`) を再帰 Visit | 同左 | v1.4 に 1 件のみ |
| `paragraph` | 子 inline を連結、末尾 `\n\n` | 同左 | |
| `transition` | `-----\n\n` を出力 | `-----\n\n` | create/verify で同一形式 (sequential-delete で marker として一致) |
| `container` | 子 node を再帰 Visit（属性は無視） | 同左 | generic grouping |
| `compound` | 子 node を再帰 Visit | 同左 | |
| `topic` | 子 node を再帰 Visit（topic title は title child） | 同左 | |
| `sidebar` | 子 node を再帰 Visit | 同左 | |
| `rubric` | children を連結した単行テキストを paragraph として出力 | 同左 | |

### 4-2. インライン

| Node | 出力 | 備考 |
|---|---|---|
| `Text` | そのまま文字列化 | |
| `strong` | `**<child>**` | children を再帰して内側テキスト生成 |
| `emphasis` | `*<child>*` | |
| `literal` | `` `<child>` `` | inline code |
| `title_reference` | children を連結（強調なし） | docutils デフォルト role |
| `inline` | children を連結（class 属性は無視） | generic span |
| `reference` | `refuri` があれば `[<text>](<refuri>)`、`refid` があれば `<text>` (解決後タイトル)。`refname` が残っている場合は**未解決** → FAIL (QC1 未解決参照) | label 解決は docutils に委譲 |
| `target` | 出力なし (label 登録済) | |
| `substitution_reference` | transform で置換済なので通常到達しない。到達したら**未解決** → FAIL (QC1 未解決参照) | |
| `substitution_definition` | 出力なし | |
| `footnote_reference` | `[<label>]` | MD に索引不要、残置 |
| `citation_reference` | `[<label>]` | 同上 |
| `problematic` | children を連結（inline 失敗箇所の原文を保持） | v1.x で最大 181 件。system_message 側で警告として記録するが本文は出す |
| `system_message` | 出力なし (Visitor が警告として集計するのみ) | parse error (level >= 3) の場合は create は警告ログ、verify は QC1 未対応ソースとして FAIL |

### 4-3. リスト

| Node | 出力 | 備考 |
|---|---|---|
| `bullet_list` | `list_item` を順に Visit、各項目の先頭に `*` とインデント | |
| `enumerated_list` | `list_item` を順に Visit、先頭に `1.` `2.` ... | docutils が番号を付与 |
| `list_item` | 子 node を再帰 Visit、1 段インデント | |
| `definition_list` | `definition_list_item` を順に Visit | |
| `definition_list_item` | `term` 行 + `classifier` (存在時) + `definition` 行 | |
| `term` | inline 連結 | |
| `classifier` | `: <inline>` (term 末尾に連結) | |
| `definition` | 子 node を再帰 Visit | |
| `field_list` | **出力なし** (directive option も standalone も廃棄) | v6 実データ 238 件で JSON 非出現を確認済。bibliographic field も同じ扱い |
| `field` / `field_name` / `field_body` | 出力なし (`field_list` 内で処理) | |
| `option_list` | `option_list_item` を順に Visit (コマンド CLI オプション表) | v6 の RST ではほぼ出現しない想定、念のため対応 |
| `option_list_item` | `option_group` + `description` の行 | |
| `option_group` / `option` / `option_string` / `option_argument` / `description` | children 連結 | |
| `line_block` | `line` の連結、各 line の先頭に空白なし (docutils が改行保持) | |
| `line` | inline 連結 + `\n` | |
| `attribution` | block_quote 末尾に `— <inline>` として出力 | `.. epigraph::` 等で出現 |

### 4-4. ブロック

| Node | 出力 | 備考 |
|---|---|---|
| `block_quote` | 子 node を再帰 Visit、各行先頭に `> ` | |
| `literal_block` | ` ```<language>\n<text>\n``` ` | `language` 属性があれば fence に付与 |
| `doctest_block` | ` ```python\n<text>\n``` ` | Python doctest |

### 4-5. テーブル

| Node | 出力 | 備考 |
|---|---|---|
| `table` | MD table として `thead` / `tbody` を順に出力。`title` children があれば table の直前に paragraph として | create/verify とも `fill_merged_cells` 共有ヘルパー (§3-6) を経由してから行出力する |
| `tgroup` | 子 node を Visit (`colspec` / `thead` / `tbody`) | |
| `colspec` | 出力なし (MD は column width 非対応) | |
| `thead` | ヘッダ行 + セパレータ `\| --- \| --- \|` | |
| `tbody` | body 行 | |
| `row` | 各 `entry` の child を `\|` で区切った行 | |
| `entry` | 子 node を再帰 Visit し `escape_cell_text` (§3-6) を適用 | `morerows` / `morecols` は `fill_merged_cells` で top-left に内容を配置、他占有セルは空文字 |

### 4-6. 画像 / 図

| Node | 出力 | 備考 |
|---|---|---|
| `image` | 単独出現時は出力なし | `:alt:` 等は drop（設計書 E グループ） |
| `figure` | child `image` はパス抽出、`caption` / `legend` の children を再帰 Visit して後続 | |
| `caption` | inline 連結 | |
| `legend` | 子 node を再帰 Visit | |

**create 側**のみ、`image` / `figure` 出現時に `![caption](relative_path)` を emit（docs MD に画像を残す）。verify 側は空文字。

### 4-7. 注記 (admonition)

| Node | 出力 | 備考 |
|---|---|---|
| `note` / `tip` / `warning` / `important` / `attention` / `hint` / `caution` / `danger` / `error` / `admonition` | `> **<Label>:** <body>` body は子 node を再帰 Visit、各行先頭に `> ` | Label は `scripts/common/rst_admonition.py` の辞書を継続利用 |

### 4-8. 参照 / 索引

| Node | 出力 | 備考 |
|---|---|---|
| `footnote` | 子 node を再帰 Visit (body を prose としてそのまま出力)、label は廃棄 | 再帰原則によりネストした code-block / table / list も正しく処理される |
| `citation` | 同上 | |
| `label` | 出力なし | footnote/citation の label child |

### 4-9. その他

| Node | 出力 | 備考 |
|---|---|---|
| `raw` | `format="html"` の場合は children テキストを `normalise_raw_html` (§3-6) に通して出力、それ以外の format (latex/tex 等) は廃棄 | Y-1 probe で v6=708 / v5=977 / v1.x 50-60 件。処理対象 HTML entity / tag は §3-6 ヘルパーの仕様で管理 |
| `comment` | 出力なし | RST コメント |

## 5. 未登録 node の扱い

Visitor は上記の全 node 種別を直接ハンドルする。**それ以外の node 種別**が出現した場合:

- verify は **FAIL (QC1: 未対応 node)** を報告
- create は警告をログに出し、node をスキップ (JSON 品質は verify で担保するため create 単独では停止しない)
- 対応表追加は `rbkc-verify-quality-design.md` §5 の変更プロセスを経る

## 6. 参考: docutils 設定

`scripts/common/rst_ast.py` 経由で以下を一元設定:

- `report_level=2` (WARNING 以上を system_message として AST に埋め込む)
- `halt_level=5` (いかなるエラーでも halt しない)
- `file_insertion_enabled=True` (`.. include::` / `.. literalinclude::` を docutils に展開させる)
- `raw_enabled=True` (`.. raw:: html` を raw node として保持)
- Sphinx 固有 role / directive の shim 登録 (Y-1 probe で確立したセット):
  - inline role: `ref` / `doc` / `download` / `java:extdoc` / `javadoc_url` / `file` / `guilabel` / `menuselection` / `kbd` / `command` / `samp` / `envvar` / `abbr` / `term` / `numref` / `strong` (generic に登録)
  - literal directive: `code-block` / `literalinclude` / `csv-table` (body は literal_block として保持)
  - container directive: `toctree` / `function` / `class` / `java:method` / `java:type` / `java:field` (child は nested_parse で RST として再帰)
