# RBKC Converter 設計 — AST node → MD 対応表

## 1. 目的

RST / Markdown ソースを公式パーサで AST 化したものを入力として、**正規化 Markdown** を生成する際の node → MD 対応表を定める。

本表は create / verify が共有する。両者とも `scripts/common/` 配下の共通モジュール経由で公式パーサを呼び、本表に従って Visitor で AST を走査する。

- **RST**: `scripts/common/rst_ast.py` 経由で `docutils.core.publish_doctree` を呼ぶ。対応表は §4
- **Markdown**: `scripts/common/md_ast.py` 経由で `markdown-it-py` を呼ぶ。対応表は §7
- **Excel**: AST ではなくセル単位の sequential-delete (`rbkc-verify-quality-design.md` §3-1 Excel 節参照)

各フォーマット共通の原則:

- **create**: AST → `RSTResult` (セクション分割済の構造体)。後段で JSON/docs MD に直列化。
- **verify**: AST → 正規化 MD 文字列（sequential-delete の対象となる「正規化ソース」）。

## 2. スコープと独立性

- `rbkc-verify-quality-design.md` §2-2 の独立性原則に従う
- 本対応表は create / verify の唯一の仕様。実装は本表を直接参照する
- 対応表未登録 node が出現したら **FAIL**（silent drop しない）。追加は設計書 §5 の変更プロセスを経る

## 3. 共通の原則

### 3-1. 再帰原則

`section` / `footnote` / `admonition` (10 種、§4-7) / `list_item` / `entry` / `block_quote` / `figure` / `topic` / `container` / `compound` / `field_body` などの**body を持つ node** は、**子 node 列を順に再帰 Visit** して MD を生成する。

これにより「footnote body 内の code-block」「admonition body 内の table」「table cell 内の list」「field_list value 内の reference / URL」のような RST ネスト構造がすべて一貫して扱われる。

### 3-1a. 情報保持原則 (no-drop principle)

知識価値のある文字列を**例外的に drop する規則は設けない**。以下の要素は従来「廃棄」だったが、実データ確認の結果すべて保持する:

- `image` / `figure` の `:alt:` — 日本語の知識文字列 10 件確認済
- `figure` の caption / legend
- `list-table` / `table` / `csv-table` directive の argument (表タイトル) — v6 で 176 件確認済
- `.. admonition:: <独自タイトル>` の独自タイトル
- `field_list` (standalone) の field_body (value) — directive option block のみ drop

drop するのは「RST 構文上意味のあるメタ情報だが人間可読コンテンツを含まない」場合のみ:

- `target` (ラベル定義本体; 解決後 id として section に付与される)
- `substitution_definition` (transform 後に参照側で raw/Text に展開される)
- `colspec` (MD table は列幅非対応)
- `comment` (RST コメント = 非表示)
- `system_message` (Visitor 警告として集計)
- directive option block (`:header-rows:` / `:widths:` / `:emphasize-lines:` 等の表示メタ)
- footnote/citation の `label` child (番号は body 再帰で footnote_reference として参照される)

この分類は設計書レビューにより閉集合として確定する。新規追加は `rbkc-verify-quality-design.md` §5 の変更プロセスを経る。

### 3-1b. 例外禁止原則 (zero-exception principle)

Visitor は次の状況で必ず FAIL を返す (silent fallback を設けない):

- 対応表未登録 node
- 未登録 role (Sphinx role shim のホワイトリストに無いもの)
- 未解決 reference / substitution (docutils transform + label_map 併用でも解決できなかったもの)
- docutils が parse error (level >= 3) を返したソース

### 3-2. create / verify の出力差

| 側 | 出力単位 | 備考 |
|---|---|---|
| create | `RSTResult` (top-level title / top-level content / `sections: list[Section]`、各 Section は `title` / `content` / `level: int`) | `section` node 単位で分割。nest depth を `Section.level` に記録 (h2=2, h3=3, h4=4, ...) |
| verify | 正規化 MD 文字列 (1 本) | section 境界は保持するが、全体を結合してフラットに |

両者とも以下の表の「MD 出力」列に従う。違いは「section で分割するか連結するか」のみ。

#### 3-2-1. Section level の記録

Phase 22-B-16 で `Section` dataclass に `level: int` フィールドを追加する。RST / MD 双方で使用:

- RST: `_walk_section` で nesting depth をインクリメントしながら記録 (`document` 直下の `section` = level 2、nested `section` = level 3、さらにネスト = level 4、...)
- MD: `heading_open` の `tag` (h2/h3/h4) から level を決定
- JSON schema: `sections[].level` として出力 (詳細は `rbkc-json-schema-design.md` §2-2)
- docs.py: level に応じて `##`/`###`/`####` を出力する (詳細は `rbkc-json-schema-design.md` §4)

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
| `container` | `directive_name == "toctree"` のとき: 子 `paragraph` の各テキスト行を toctree エントリとして取り出し、`doc_map` で解決する。解決成功なら `* [title](../../{type}/{category}/{file_id}.md)` 形式の bullet list 行を出力。解決失敗なら `` * `{path}` `` としてコードスパンで出力。複数 `paragraph` は結合して 1 つの bullet list とする。`directive_name != "toctree"` のとき: 子 node を再帰 Visit（属性は無視） | 同左（toctree か否かで同じ分岐を適用） | toctree は MD リンクリストに変換。`no_knowledge_content` 判定はリンク出力後の `content.strip()` 非空チェックで自動解決 |
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
| `reference` | `refuri` があれば `[<text>](<refuri>)`、`refid` があれば `[<target title>](../<target category>/<target file_id>.md#<github_slug(target section_title)>)` (`scripts/common/labels.py` の `build_label_map` で解決)。`refname` が残っている場合は**未解決** → FAIL (QC1 未解決参照) | label 解決は `scripts/common/labels.py` + docutils transform の併用。anchor slug は `scripts/common/github_slug.py` を経由 |
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
| `field_list` | **context-aware**: directive option block (directive head 直後) は全 drop、standalone (document 本文内・block body 内) は field_name を drop し field_body を再帰 Visit して保持 | v6 実データで field_body に `:ref:` / 外部リンク等の知識が入る事例を確認 |
| `field_name` | (standalone) 出力なし (field_body が value を出す)  | |
| `field_body` | (standalone) children を再帰 Visit | |
| `option_list` | `option_list_item` を順に Visit (コマンド CLI オプション表) | v6 の RST ではほぼ出現しない想定、念のため対応 |
| `option_list_item` | `option_group` + `description` の行 | |
| `option_group` / `option` / `option_string` / `option_argument` / `description` | children 連結 | |
| `line_block` | `line` の連結、各 line の先頭に空白なし (docutils が改行保持) | |
| `line` | inline 連結 + `\n` | |
| `attribution` | block_quote 末尾に `— <inline>` として出力 | `.. epigraph::` 等で出現 |

### 4-4. ブロック

| Node | 出力 | 備考 |
|---|---|---|
| `block_quote` | `attribution` を子に持つ場合のみ各行先頭に `> `、それ以外は `>` を付けず子 node の出力だけ返す | RST は空白インデントで自動的に block_quote を生成するため、AST 上では「作者が引用として書いた」ものと「レイアウト上字下げしただけ」のものが区別できない。明示的な引用の印である `attribution` が無い限り字下げ扱いとして `>` を付けない (Phase 22-A)。注意書きは `admonition` で扱う。 |
| `literal_block` | ` ```<language>\n<text>\n``` ` | `language` 属性があれば fence に付与。`.. literalinclude::` directive は `scripts/common/rst_ast.py` の shim で docutils `literal_block` に変換される (option `:language:` のみサポート、corpus 全量 43 件中 39 件が `:language:` 使用、他 option は 0 件の調査結果に基づく閉集合対応) |
| `doctest_block` | ` ```python\n<text>\n``` ` | Python doctest |

### 4-5. テーブル

| Node | 出力 | 備考 |
|---|---|---|
| `table` | `title` child があれば table の直前に paragraph として**必ず出力**、続けて MD table として `thead` / `tbody` を順に出力。`thead` が無い場合は `tbody` の 1 行目を header 行として合成する (MD は header なし table を表現できないため) | create/verify とも `fill_merged_cells` 共有ヘルパー (§3-6) を経由。`list-table` / `table` / `csv-table` directive の argument も docutils がこの `title` child に反映する |
| `tgroup` | 子 node を Visit (`colspec` / `thead` / `tbody`) | |
| `colspec` | 出力なし (MD は column width 非対応) | |
| `thead` | ヘッダ行 + セパレータ `\| --- \| --- \|` | |
| `tbody` | body 行 | |
| `row` | 各 `entry` の child を `\|` で区切った行 | |
| `entry` | 子 node を再帰 Visit し `escape_cell_text` (§3-6) を適用 | `morerows` / `morecols` は `fill_merged_cells` で top-left に内容を配置、他占有セルは空文字 |

### 4-6. 画像 / 図

| Node | 出力 | 備考 |
|---|---|---|
| `image` | `![<alt>](assets/<file_id>/<basename>)` を出力。`alt` / `uri` の少なくとも片方が空でなければ必ず出す | alt を drop しない (知識価値あり)。URI は source dir からの相対で resolve し、実ファイルを `knowledge/assets/<file_id>/<basename>` にコピーする |
| `figure` | child `image` を `![<caption or alt>](assets/<file_id>/<basename>)` で出し、`caption` / `legend` の children を再帰 Visit して後続 | caption / legend は必ず保持。`image` の alt/uri ルールに従う |
| `caption` | inline 連結 | |
| `legend` | 子 node を再帰 Visit | |

**Phase 22-B-16 の変更点**:
- URI は create 側の converter が AST 時点で解決する (source file directory からの相対 → `assets/<file_id>/<basename>` への正規化)
- 実 asset は `knowledge/assets/<file_id>/<basename>` にコピー済であることを converter が保証する
- JSON content に出る asset path は `assets/<file_id>/<basename>` の一形式のみ (絶対パス / RST 相対パス等は出力しない)
- docs.py は `assets/` 先頭の path のみを docs MD 位置からの相対 (`../../knowledge/assets/<file_id>/<basename>`) に rewrite する (既存ロジックの拡張)
- verify QL1 は JSON content / docs MD 双方で asset の実ファイル存在を検査する

`image` / `figure` の出力は create / verify で共通 (§3-2 の対称性原則)。

### 4-7. 注記 (admonition)

| Node | 出力 | 備考 |
|---|---|---|
| `note` / `tip` / `warning` / `important` / `attention` / `hint` / `caution` / `danger` / `error` | `> **<Label>:** <body>` body は子 node を再帰 Visit、各行先頭に `> ` | Label は `scripts/common/rst_admonition.py` の辞書から引く |
| `admonition` | child の `title` があればそれを Label に、無ければ `Note` を Label に。body は title を除いた children を再帰 Visit | custom title は**必ず保持** |

### 4-8. 参照 / 索引

| Node | 出力 | 備考 |
|---|---|---|
| `footnote` | 子 node を再帰 Visit (body を prose としてそのまま出力)、label child は drop (番号はソース側 `footnote_reference` の出力と重複) | 再帰原則によりネストした code-block / table / list も正しく処理される |
| `citation` | 同上 | |
| `label` | 出力なし | footnote/citation の label child |

### 4-9. その他

| Node | 出力 | 備考 |
|---|---|---|
| `raw` | `format="html"` の場合は children テキストを `normalise_raw_html` (§3-6) に通して出力、それ以外の format (latex/tex 等) は廃棄 | Y-1 probe で v6=708 / v5=977 / v1.x 50-60 件。処理対象 HTML entity / tag は §3-6 ヘルパーの仕様で管理 |
| `comment` | 出力なし | RST コメント |

## 5. 未登録 node / 未解決参照の扱い (zero-exception)

§3-1b の例外禁止原則に基づき、以下の状況は Visitor が必ず FAIL を返す:

- 対応表未登録 node 種別
- 未登録 role (Sphinx role shim ホワイトリスト外の `:xxx:\`...\`` 構文)
- 未解決 reference / substitution (docutils transform + label_map 併用でも解決できなかったもの)

create / verify とも**同じ扱い** (create だけ warning / skip に緩和することは禁止 — ドリフトの温床になる)。対応表追加 / ホワイトリスト拡張は `rbkc-verify-quality-design.md` §5 の変更プロセスを経る。

### 5-1. Sphinx role shim のリンク化 (Phase 22-B-16)

`inline` node (`classes` に `role-<name>` が付与された Sphinx role shim) のうち、**リンクとして意味を持つ role** は Phase 22-B-16 で CommonMark MD リンク形式に変換する:

| role | 入力 | 解決方法 | 出力 (JSON / docs MD 共通) |
|---|---|---|---|
| `ref` | `:ref:\`label\`` / `:ref:\`text <label>\`` | `labels.build_label_map` で `label -> (title, file_id, section_title)` に解決 | `[<display or title>](../<category>/<file_id>.md#<github_slug(section_title)>)` |
| `doc` | `:doc:\`path\`` / `:doc:\`text <path>\`` | `labels.build_doc_map` で `path -> (title, file_id)` に解決 | `[<display or title>](../<category>/<file_id>.md)` |
| `numref` | `:numref:\`label\`` | `ref` と同じ label_map を経由 | `ref` と同じ形式 |
| `download` | `:download:\`path\`` / `:download:\`text <path>\`` | URI を source dir からの相対で解決し、実ファイルを `knowledge/assets/<file_id>/<basename>` にコピー | `[<display or basename>](assets/<file_id>/<basename>)` |

上記以外の Sphinx role (`file` / `guilabel` / `menuselection` / `kbd` / `command` / `samp` / `envvar` / `abbr` / `term` / `java:extdoc` / `javadoc_url` / `strong` 等) は従来通り display text のみを出力する。

**display text の扱い**:
- `:ref:\`text <label>\`` / `:doc:\`text <path>\`` / `:download:\`text <path>\`` のように `text <target>` 形式で display text が明示されている場合は、MD リンクの `[text]` 部分に display text を使う
- display text が無い場合は解決した target title (ref/doc/numref) または basename (download) を使う

**解決失敗時** (Sphinx 追従、Phase 22-B-12 で確定、`rbkc-verify-quality-design.md` §3-2-2 の 5 象限分類と整合):
- `:ref:` / `:doc:` / `:numref:` で label が解決できない場合は、**Sphinx parity** に従い WARNING ログ + display text fallback を出力する (build は止めない、create の JSON には display text のみを残す)
- `:download:` で asset file が見つからない場合は、Sphinx は build failure にするため、RBKC も QL1 FAIL とする
- verify 側の 5 象限判定 (`rbkc-verify-quality-design.md` §3-2-2):
  - corpus に label 有 + mapping 採用 + JSON に link 出力 → PASS (象限 1)
  - corpus に label 有 + mapping 採用 + display text のみ → **FAIL** (象限 2、create の実バグ)
  - corpus に label 有 + mapping scope 外 + display text のみ → **PASS + WARNING** (象限 3、ユーザ scope 決定の尊重)
  - corpus に label 未定義 + display text のみ → **PASS + WARNING** (象限 4、Sphinx parity dangling)
  - display text も JSON に無い → **FAIL** (象限 5、データ損失)
- corpus に label がある場合、create 側で「mapping 採用」かどうかを判別できないため、create は Sphinx と同じく「解決できなければ display text を残す」動作をする。verify 側が corpus を独立 scan して 5 象限を判定する (`rbkc-verify-quality-design.md` §2-2 独立性原則)

**docs MD への path rewrite**:
- JSON content に出る path (`../<category>/<file_id>.md` / `assets/<file_id>/<basename>`) は JSON / docs MD の双方で**同一文字列**として出力される (QO2 完全一致を維持)
- docs.py はこのうち `assets/` 先頭のものだけを docs MD 位置からの相対 (`../../knowledge/assets/...`) に rewrite する
- `../<category>/<file_id>.md` 形式の MD リンクは JSON 側でも docs MD 側でも同じ文字列で、それぞれの位置から `../<category>/<file_id>.{json|md}` の形で解決可能 (AI 側は `.md` -> `.json` を読み替えるワークフローで対応)

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

## 7. Markdown AST 対応表

Markdown ソースは `markdown-it-py` の CommonMark パーサで token ストリームを取得し、block token → MD、inline token → MD の 2 段で正規化 MD を生成する。

### 7-1. 設定

`scripts/common/md_ast.py` 経由で以下を一元設定:

- Parser: `markdown-it-py` の `MarkdownIt("commonmark")` ベース (CommonMark 厳密モード)
- Inline expansion: 有効 (block token の `children` に inline token 列が入る)
- Table plugin: 有効 (GFM table; Nablarch 開発ガイドで使用)

### 7-2. Block token → MD

| Token | create | verify | 備考 |
|---|---|---|---|
| `heading_open` level=1 | document title に設定 | `<title>\n\n` | `_ATX_RE` の h1 と同等 |
| `heading_open` level>=2 | `Section(title, content)` 境界 | `<title>\n\n` 続けて body | RST `section` と対称 |
| `paragraph_open` / `paragraph_close` | 子 inline を連結、末尾 `\n\n` | 同左 | |
| `bullet_list_open` / `list_item_open` | `*` + インデント | 同左 | |
| `ordered_list_open` | `1.` `2.` | 同左 | |
| `code_block` / `fence` | ` ```<info>\n<content>\n``` ` | 同左 | |
| `blockquote_open` | 各行先頭に `> ` | 同左 | |
| `table_open` / `thead_open` / `tbody_open` / `tr_open` / `th_open` / `td_open` | GFM table として出力 | 同左 | |
| `hr` | `-----\n\n` | 同左 | |
| `html_block` | `normalise_raw_html` (§3-6 共有ヘルパー) で processed | 同左 | `<br>` `&nbsp;` `&lt;` 等 decode |

### 7-3. Inline token → MD

| Token | 出力 | 備考 |
|---|---|---|
| `text` | そのまま文字列化 | |
| `strong_open` / `strong_close` | `**<inner>**` | |
| `em_open` / `em_close` | `*<inner>*` | |
| `code_inline` | `` `<content>` `` | |
| `link_open` / `link_close` | `[<text>](<href>)` | href は token の `attrs` から取得。QL2 の URL 抽出はここから |
| `image` | `![<alt>](<src>)` | alt は drop しない (§3-1a) |
| `softbreak` / `hardbreak` | 空白 / `\n` | |
| `html_inline` | `normalise_raw_html` 共有ヘルパーで processed | |

### 7-4. 例外禁止 (MD)

§3-1b zero-exception を MD にも適用する:

- 対応表未登録 token 種別 → FAIL (QC1 未対応構文)
- `markdown-it-py` が parse error を返した場合 → FAIL (QC1 未対応ソース)

### 7-5. QL 抽出 (MD)

- **QL1 内部リンク**: `link_open` token のうち `href` が `http://` / `https://` で始まらないもの。抽出テキストは link_open 〜 link_close 間の inline children を連結。href は **source file 位置からの相対** として解釈し、converter が target MD ファイルを `doc_map` で file_id に resolve、JSON / docs MD の両方に `[text](../<category>/<file_id>.md)` または `[text](../<category>/<file_id>.md#<github_slug(anchor)>)` (`#anchor` 付きの場合) の形式で出力する (RST の `:ref:` / `:doc:` 扱いと対称)
- **QL2 外部リンク**: `link_open` token のうち `href` が `http://` / `https://` で始まるもの、および autolink (`<http://…>`) で生成された `link_open` の href
- **inline image**: `image` token の `src` を source dir からの相対で解決し、`knowledge/assets/<file_id>/<basename>` にコピー。JSON / docs MD の両方に `![alt](assets/<file_id>/<basename>)` を出力 (RST image と対称、`rbkc-verify-quality-design.md` §3-2-3 参照)

## 8. Excel 対応表

Excel (xlsx / xls) は AST 構造を持たないため、§4 / §7 とは別のセル処理方式で JSON / docs MD を生成する。対象ファイルはリリースノート (`*-releasenote.xlsx` / `*-releasenote-detail.xls`) と セキュリティ対応チェックリスト (`Nablarch機能のセキュリティ対応表.xlsx`) の 2 種で合計 76 ファイル / 212 シート (全バージョン合算)。

### 8-1. ファイル分割

- **1 xlsx/xls → 各シート 1 JSON + 1 docs MD**
- **シート数 = 1** の場合: ファイル ID は `{basename}` (sheet_slug を付加しない)
- **シート数 ≥ 2** の場合: ファイル ID は `{basename}-{sheet_name}` (シート名は日本語のまま)

### 8-2. シート分類 (P1 / P2)

各シートを次のルールで P1 / P2 に自動分類する:

- **P1 (データ表)**: 連続非空セル ≥ 3 のヘッダ行 + 同構造のデータ行 ≥ 2 が検出できるシート
- **P2 (段落主体)**: ヘッダ検出失敗、または **列数 ≤ 2** のシート (列数 ≤ 2 の場合は P2 扱い、例: `分類` の 71×2 対応表を 71 section に分けるのは過剰)

JSON に `sheet_type: "P1" | "P2"` メタ情報を出力する。自動判定ミス時の原因特定を容易にするため、初回生成後 `.work/00299/phase22/sheet-classification.md` に判定結果一覧を出力し、override が必要になったケースに限り mapping を追加する (最初は空)。

### 8-3. 複数行ヘッダ合成 (P1) — span-inherit アルゴリズム

Phase 22-B-12 で確定。corpus 全 95 P1 シートのうち真の多段ヘッダは 1 シートのみだが、アルゴリズムは一般化された span-inherit 方式を採用する。

**手順**:

1. ヘッダ行群を top-down に順序付ける (leaf = 最下段)
2. 各親行 (leaf 以外) について、各セルは「そのセル位置から右方向、次の非空セルが現れる列の直前まで」を span として inherit させる (Excel の merged-cell 慣習。実際に merge されていなくても飛び飛びに親名が書かれる corpus ケースに対応)
3. 各列 c について `parts = [inherited_parent_row_1[c], ..., inherited_parent_row_N[c], leaf[c]]` のうち非空のみを残し `SEP.join(parts)` で合成。連続する同一要素 (全行同値) は dedup する

**SEP**: `" / "` (space-slash-space)

- corpus 全量で既存ヘッダセル中に ` / ` を含むものは 0 件 (調査結果で確認済: `.work/00299/phase22/full-survey-summary.md`)
- SEP の選択は cosmetic であり、列名 unique 性の担保はアルゴリズム側にある
- SEP は本書で定義する constant (`SEP = " / "`) として参照され、create / verify 双方が同一 constant を使う (drift 防止)

**unique 性**: span-inherit 合成後の列名は、元 Excel 表が「1 親 N 子」構造で正しく書かれている限り unique になる。corpus 全量で 95/95 duplicate ゼロ。合成後に duplicate が検出された場合、converter は **エラーで停止** (P1 の JSON を出力しない) する。これにより verify 側で duplicate を FAIL として観測できる (§3-4 QP)。

**3 段以上**: corpus 全量で 0 件だが、アルゴリズムは `header_rows` 長に非依存で recurse する。unit test で 3 段合成を pin する。

### 8-3a. preamble の扱い (Phase 22-B-12)

P1 シートでタイトル行 (`■…` を含む行) とヘッダ行 (§8-2) の間にある非空セルは **preamble** として扱い、行優先・列順で収集したセル値を `\n` で join した文字列を JSON の **top-level `content` フィールド** に格納する。

- semantic: RST/MD converter が「title 直下の free-form preamble text」を `content` に入れるのと同一契約 (format 非依存の preamble semantic)
- corpus 実態: 95 P1 シート中 90 シート (95%) で preamble あり。1〜7 セル、最長 757 文字 (調査結果)
- 空の場合は `content: ""` (既存 RST/MD と同じ扱い)
- docs MD 側は既存の docs.py renderer が `content` を h1 直下の段落として出すロジックをそのまま流用する (Excel 専用 renderer 変更は不要)

### 8-4. JSON スキーマ

**P1**:
- `title`: row 1 の `■...` タイトル行 (なければシート名)
- `content`: preamble セル (§8-3a) を `\n` 区切りで join した文字列 (タイトル行とヘッダ行の間の非空セル値)。preamble が無ければ空文字
- `sections`: 1 データ行 = 1 section
- `section.title`: 「タイトル」列の値 (なければ先頭非 `No.` 列の値)
- `section.content`: 全列を `{列名}: {値}\n` の **縦列挙形式** で出力 (MD table 記法 `|---|` / `**` は使わない)。値の埋め込み改行・タブは単一スペースに正規化 (§8-4 の line-based format 制約)
- `sheet_type: "P1"`
- `columns`: 検出した P1 header 行の span-inherit 合成後列名リスト (§8-3 のアルゴリズム)。docs MD (§8-5) の table reconstruction で使用
- `data_rows`: データ行のセル値 2 次元配列 (行 × 列; 空セルは空文字)。docs MD (§8-5) の table reconstruction で使用

**P2**:
- `title`: row 1 の `■...` (なければシート名)
- `content`: シート全体のテキスト。**すべての P2 サブパターンで値の埋め込み改行は単一スペースに正規化** (AI キーワード検索の索引性を保つため。docs MD 側は §8-5 で異なる変換を行う)
- `sections`: 空 (`[]`)
- `sheet_type: "P2"`
- `p2_headings`: P2-1 シートのみ付与。Excel 列位置から生成される docs MD 見出し行を出現順に `[{"text": "...", "level": 2}, ...]` として列挙 (col-0→level 2, col-1→level 3, col-2→level 4)。P2-2/P2-3 は省略。verify QO1 逐次照合に使用 (§8-6 参照)
- `sheet_subtype`: P2-3 シートのみ `"P2-3"` を付与。P2-1/P2-2 は省略 (verify QO2 正規化に使用; §8-6 参照)
- `p2_raw_content`: P2-3 シートのみ付与。docs MD 生成用。各セル値の埋め込み改行を **保持** したまま `  ` / `\n` 結合した文字列 (`content` はフラット化済みで LF 情報が失われるため別フィールドとして保持)。verify はこのフィールドを使用しない

### 8-5. docs MD 出力

**P1**:
- 先頭に `# {title}`
- `content` が非空なら h1 直下に preamble 段落として出力 (既存 docs.py `_render_full` の挙動、Excel 専用分岐なし)
- 元 Excel を復元する MD table (全列網羅、列ヘッダ + 罫線 `|---|` + 全データ行)

**P2 (共通)**:
- 先頭に `# {title}`

**P2-1 (column-indent → MD headings)**:
- 対象シートは `xlsx-sheet-mapping.md` に明示的に列挙 (自動検出なし)
- docs MD では Excel 列位置を見出しレベルに対応させる (絶対列で判定):
  - **単一セル行**かつ col-0 が非空: `## {col-0 value}` (H2、シート H1 の直下)
  - **単一セル行**かつ col-0 が空かつ col-1 が非空: `### {col-1 value}`
  - **単一セル行**かつ col-0/col-1 が空かつ col-2 が非空: `#### {col-2 value}`
  - 上記以外 (col-3 以降に最初の非空セルがある、または複数セルが横並びの行): 残りの非空セル値を `  ` 区切りで結合した本文段落
  - 「複数セルが横並び」はシート内の対応表行 (「変更前 / 変更後」等) に相当し、min_cx ≤ 2 でも本文として扱う
- **JSON content との乖離**: docs MD は見出し構造を持つが、JSON の `content` はフラットテキスト (全セル値を `  ` / `\n` 結合)。見出しテキスト自体は JSON content にも含まれるため QO1 の title 照合は通過する。verify は `sections[]` の代わりに `p2_headings` 配列を用いた逐次照合で見出し欠落・余分・レベル誤り・順序違いを検出する (§8-6 参照)

**P2-2 (現状維持)**:
- 先頭に `# {title}` + シート全体のテキストをそのまま出力 (変更なし)

**P2-3 (embedded LF → MD hard line break)**:
- 対象シートは `xlsx-sheet-mapping.md` に明示的に列挙 (自動検出なし)
- docs MD では各セル内の `\n` を Markdown hard line break (`  \n`) に変換して出力
- **JSON content との乖離**: JSON の `content` は `_flatten_ws` でフラット化 (埋め込み `\n` → スペース)。docs MD は `  \n` を含む。verify QO2 での docs MD ⊂ JSON の逆チェックはないが、通常の QO2 (JSON content が docs MD に verbatim 含まれるか) は `  \n` の正規化が必要。verify 側で docs MD テキストの `  \n` を空白正規化してから比較する (§8-6 参照)

### 8-6. verify との整合

- QC1–QC4 (Excel): `rbkc-verify-quality-design.md` §3-1 Excel 節 (sequential-delete)
- QO2 Excel 例外: `rbkc-verify-quality-design.md` §3-3 の通り、JSON section.content の全セル値が docs MD に含まれる一方向 (JSON ⊂ MD) のみチェック。MD 側の列ヘッダ / 罫線 `|---|` は JSON に無くてよい
- QC5 (Excel): 対象外 (§3-1 マトリクス)

**P2-1 verify チェック (QO1 — p2_headings 逐次照合)**:
- `p2_headings` が存在する JSON に対して、verify は QO1 として以下の逐次照合を行う:
  1. docs MD から `##`/`###`/`####` を出現順に抽出し `md_headings = [{text, level}, ...]` を構築
  2. `len(p2_headings) == len(md_headings)` を確認 (件数不一致 → FAIL)
  3. インデックス i ごとに `p2_headings[i].text == md_headings[i].text` かつ `p2_headings[i].level == md_headings[i].level` を確認 (text 不一致・level 不一致 → FAIL)
- 検出対象: 見出し欠落・余分な見出し・レベル誤り・順序違い (4 類すべてを FAIL)
- `sections 空 → ## 見出しなし` チェックは P2-1 には不適用 (P2-1 は `sections: []` だが docs MD に `##` が出現するため)
- verify の変更種別: `p2_headings` フィールドを照合する新チェックの追加 (`.claude/rules/rbkc.md §Acceptable changes` — 「Add missing checks required by the specification」に該当)
- 実装: `check_json_docs_md_consistency` に `p2_headings` キー存在時の逐次照合ブランチを追加。既存 `sections 空 → ## なし` チェックは `not data.get("p2_headings")` 条件で除外

**P2-1 verify 例外 (QO2)**:
- P2-1 の JSON `content` は行ごと `\n` 区切りのフラットテキスト（各行 = 見出しまたは本文セル値）。docs MD は Markdown 見出し (`##`/`###`/`####`) と本文段落の形式で、verbatim containment は成立しない。
- P2-1 QO2 チェック: `content` を `\n` で split した各行（非空）が docs MD テキスト中に substring として含まれるかを一方向チェック (JSON 行 ⊂ MD)。P1 QO2 例外と同パターン (false positive fix)。
- verify の変更種別: `.claude/rules/rbkc.md §Acceptable changes` — 「Fix false positives」に該当
- 実装: `p2_headings` が存在する JSON の top-level content QO2 チェックを、verbatim 全体一致から「各行が MD に含まれる」一方向チェックに切り替える

**P2-3 verify 例外 (QO2)**:
- P2 シートの top-level content QO2 比較において、両辺を正規化してから verbatim 比較を行う
  - docs MD 側: `  \n`（Markdown hard line break）を単一スペースに正規化
  - JSON content 側: `\n`（行間セパレータ）を単一スペースに正規化
- これは false positive fix: JSON content の `\n` 区切り形式と docs MD の `  \n` 形式は意味的に等価だが文字列として異なる
- verify の変更種別: `.claude/rules/rbkc.md §Acceptable changes` — 「Fix false positives (verify incorrectly flags correct output)」に該当
- 実装: 比較前に docs MD 側 `re.sub(r'  \n', ' ', docs_region)` + JSON 側 `re.sub(r'\n', ' ', expected)` を適用
