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
| **QC1** | 完全性 | ソースのコンテンツが JSON に欠落している | 削除手順 → 手順3 | ❌ | ❌ | ❌ |
| **QC2** | 正確性 | ソースにないコンテンツが JSON に混入している | 削除手順 → 手順4 | ❌ | ❌ | ❌ |
| **QC3** | 非重複性 | 同一コンテンツが JSON に重複して含まれている | 削除手順 → 手順4 | ❌ | ❌ | ❌ |
| **QC4** | 配置正確性 | ソースのセクション A のコンテンツが JSON の異なるセクションに配置されている | 削除手順 → 手順2 | ❌ | ❌ | — |
| **QC5** | 形式純粋性 | フォーマット固有の構文記法が JSON に残留している（RST: `:role:`・`.. directive::` 等、MD: raw HTML・エスケープ文字等） | 独立チェック | ❌ | ❌ | — |

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
- **未知 node → FAIL 原則**: node → MD 対応表に未登録の node が出現した場合は FAIL として報告し、対応表追加は 5 章の変更プロセスを経る。

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

`.. include::` / `.. literalinclude::` は docutils に `file_insertion_enabled=True` を設定することで doctree 構築時に展開される。循環検出・深さ制限は `scripts/common/rst_include.py` に実装し、create / verify の両方から利用する。

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

3. **残存チェック（QC1）**: 削除後の正規化ソースの残存テキストをチェックする。フォーマット固有の**許容構文要素リスト**（3-1 末尾）に含まれないトークンが残っていれば **FAIL（QC1: 欠落）**

4. **未削除チェック（QC2, QC3）**: 手順2で正規化ソースから削除できなかった JSON テキストをチェックする。
   - 正規化ソース中に当該テキストが一度も出現しなかった → **FAIL（QC2: 誤追加）**
   - 既に削除済みの領域と重複していた（ソース中に複数回出現し、先行セクションで消費済み） → **FAIL（QC3: 重複）**

**判定分岐のまとめ**:

| 状況 | 判定 |
| --- | --- |
| Visitor が対応表未登録の node を検出 | QC1（未対応 node） |
| docutils が parse error を返した | QC1（未対応ソース） |
| 正規化ソース残存に許容構文要素以外あり | QC1（欠落） |
| JSON テキストが正規化ソースに全く存在せず | QC2 |
| JSON テキストが正規化ソースに存在するが先行削除済み | QC3 |
| 削除位置が JSON 順より前に逆行 | QC4 |

#### 許容構文要素リスト（QC1 残存判定の基準）

手順 0（docutils AST → MD Visitor）による正規化後、ソース固有の構文記号はすべて MD 等価形式に変換済みである（あるいは完全に落としている）。したがって「正規化ソース残存」に現れる許容要素は、Visitor が意図的に body を落とした構文の**名残として残る空行・ホワイトスペース類のみ**である。

- **RST 正規化ソースの許容残存**:
  - 空行、タブ、連続スペース
  - MD コードフェンス（` ``` ` 単独行、` ```lang ` 開始行）— `.. code-block::` 変換由来
  - MD table セパレータ行（`\| --- \| --- \|` 等）— `.. list-table::` / `.. table::` / simple-table / grid-table 変換由来
  - MD blockquote 記号（`> ` 行頭） — admonition 変換由来
  - MD 強調記号（`**Note:** ` 等） — admonition 変換由来
  - MD 画像参照の残骸（`![alt](path)`） — `.. image::` / `.. figure::` 変換由来
  - MD リンク記法の残骸（`[text](url)`） — ext-link / `:ref:` label 解決由来

- **MD 正規化ソースの許容残存**:
  - フロントマター（`---` で囲まれた YAML ブロック）
  - コードフェンス記号（` ``` ` 単独行）
  - HTML コメント（`<!-- -->`）
  - 空行

重要: 上記はすべて「tokenizer が Markdown に変換した結果として生まれた記号」であり、JSON content 側にも同じ記号が現れる。したがって実運用上は手順 2 の substring 削除の過程でほとんどが消費される。残存するのは**JSON 側で空白正規化されて記号が欠落した部分**のみである。

RBKC が変換で落とすべき構文要素が上記に追加された場合のみ、リスト拡張が妥当となる。リスト拡張によって「変換漏れコンテンツが許容構文とみなされる」状態を作ってはならない。

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

**ソーストークンの構築**: 全シートの非空セル値（前後空白除去後、空文字を除く）を行優先・列順に取り出したリストをソーストークンとする。`.xlsx` と `.xls` の両形式に対応する。

**JSON テキストの構築**: top-level title + top-level content + 全セクションの title + 全セクションの content を空白で結合した単一テキスト。section title はセル値であるため JSON テキストに含める。

**削除手順**:

1. **削除**: 各ソーストークンを JSON テキストから先頭から順に検索・削除する。削除位置を記録する。
2. **QC1（欠落）**: JSON テキストから見つからなかったソーストークン → FAIL
3. **QC2（捏造）**: 全ソーストークン削除後に JSON テキストに残ったテキスト（空白・空行を除く）→ FAIL
4. **QC3（重複）**: ソーストークンが見つかったが、その位置が既消費領域と重複していた → FAIL

**許容構文要素リスト（QC2 残存判定）**: Excel ソースにはマークアップ構文が存在しないが、RBKC は JSON content を Markdown 形式で生成する（テーブル記号 `|`・`---`、強調記号 `**` 等）。これらは JSON テキストに残存しても QC2 の対象外とする。

### 3-2. リンク検証（QL1–QL2）

**品質観点と検証状況**:

| ID | 観点 | 定義 | RST | MD | Excel |
| --- | --- | --- | --- | --- | --- |
| **QL1** | 内部リンクの正確性 | ソース内の内部リンク（`:ref:`、figure/image/literalinclude、`[text](path)` 等）が、意図したページ・セクションに正しく機能するよう JSON および docs MD に反映されていない | ❌ | ❌ | — |
| **QL2** | 外部リンクの一致 | 外部 URL が JSON および docs MD にソースと完全同一で含まれていない | ❌ | ❌ | — |

**前提**: JSON はリンク構造を保持せずプレーンテキストのみを保持する。したがって JSON 側の QL1 判定は「リンク先のキーワード（セクションタイトル、キャプション、コード内容）が content に含まれるか」という**間接検証**となる。URL やラベル自体の存在を JSON に期待してはならない（それは QC5 違反となる）。

**検証方法**:

QL1（内部リンク）: ソースの内部リンクを抽出し、JSON と docs MD の両方でリンク先のページ・セクションまで正しく機能するかを確認する。リンク種別ごとの期待形式:

| リンク種別 | JSON での期待形式（間接検証） | docs MD での期待形式（直接検証） |
| --- | --- | --- |
| `:ref:\`label\`` | ラベルが指すセクションのタイトルが JSON に含まれているか | セクションへのアンカーリンクが正しく解決されているか |
| `.. figure::`、`.. image::` | キャプションまたはファイル名が JSON に含まれているか | 画像パスまたはキャプションが正しく含まれているか |
| `.. literalinclude::` | 参照先コードの内容が JSON に含まれているか（`:lines:`・`:start-after:`・`:end-before:` 等のオプションがある場合はその範囲のみを対象とする） | コードブロックとして正しく含まれているか |
| `[text](path)`（Markdown） | リンクテキストが JSON に含まれているか | href がリンク先ページ・セクションと一致しているか |

QL2（外部リンク）: URL の文字列がソースと完全一致しているかを確認する。

### 3-3. 出力検証（QO1–QO4）

**品質観点と検証状況**:

| ID | 観点 | 定義 | RST | MD | Excel |
| --- | --- | --- | --- | --- | --- |
| **QO1** | docs MD 構造整合性 | docs MD の構造要素（タイトル・セクションタイトル・セクション順序）が JSON と一致していない | ✅ | ✅ | ✅ |
| **QO2** | docs MD 本文整合性 | JSON 各セクションの content が docs MD に完全一致で含まれていない | ❌ | ❌ | ❌ |
| **QO3** | docs MD 存在確認 | JSON に対応する docs MD が存在しない | ✅ | ✅ | ✅ |
| **QO4** | index.toon 網羅性 | 変換済み JSON が index.toon（知識ファイルの検索インデックス）に未登録 | ✅ | ✅ | ✅ |

> **旧 QO3（目次ページの除外）は QC1/QC2 のスコープで扱う**: 目次ページが実コンテンツを持たないまま JSON 化された場合、QC1 のソース残存チェックで RBKC のバグとして検出される。独立した品質観点を設けない。

**検証方法（docs MD）**: docs MD は JSON の人間可読レンダリングであるため、両者は完全に一致しなければならない。JSON が FAIL の場合は docs MD も自動的に FAIL とする。

- **QO1 構造整合性**:
  - タイトル: JSON top-level `title` == docs MD の `#` 見出し
  - セクションタイトル: JSON 各セクションのタイトルが docs MD の `##`/`###` に存在し、かつ JSON と同じ順序で並んでいる
  - sections が空で top-level content のみの場合: docs MD に `##` 見出しが出現しない
- **QO2 本文整合性**:
  - JSON top-level `content` が docs MD の `#` 見出し直下に完全一致で含まれている
  - JSON 各セクションの `content` が docs MD に完全一致で含まれている

**検証方法（index.toon）**: 変換済みの全 JSON ファイルが index.toon に登録されているかを確認する。登録漏れがあると nabledge の検索から除外される。index.toon に存在する全エントリと出力ディレクトリの JSON ファイル一覧を突き合わせ、未登録ファイルを検出する。

---

## 4. 品質保証マトリクス

セクション 3 の各チェックの検証状況を一覧で確認できる。

凡例: ✅ 検証済み / ❌ 未実装 / — 対象外

> **マトリクスの ❌ は verify の穴を意味する**: 2-1 の「ゼロトレランス」「100% コンテンツカバレッジ」は、全項目が ✅ になった時点で初めて保証される。現状で verify PASS になっても、❌ の項目については品質未検証である。

### コンテンツ

| 品質観点 | RST | MD | Excel |
| --- | --- | --- | --- |
| **QC1** 完全性 | ❌ | ❌ | ❌ |
| **QC2** 正確性 | ❌ | ❌ | ❌ |
| **QC3** 非重複性 | ❌ | ❌ | ❌ |
| **QC4** 配置正確性 | ❌ | ❌ | — |
| **QC5** 形式純粋性 | ❌ | ❌ | — |

### リンク

| 品質観点 | RST | MD | Excel |
| --- | --- | --- | --- |
| **QL1** 内部リンクの正確性 | ❌ | ❌ | — |
| **QL2** 外部リンクの一致 | ❌ | ❌ | — |

### 出力

| 品質観点 | RST | MD | Excel |
| --- | --- | --- | --- |
| **QO1** docs MD 構造整合性 | ✅ | ✅ | ✅ |
| **QO2** docs MD 本文整合性 | ❌ | ❌ | ❌ |
| **QO3** docs MD 存在確認 | ✅ | ✅ | ✅ |
| **QO4** index.toon 網羅性 | ✅ | ✅ | ✅ |

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
- 許容構文要素リスト（3-1）への項目追加（ただし「変換漏れコンテンツを構文要素とみなす」拡張は禁止）

### 許容されない変更

- RBKC の現在の出力に合わせて verify 基準を緩める
- チェックを無効化・スキップする
- RBKC 実装の詳細に合わせた回避策を追加する
- 独立性原則（2-2）の例外を出力間整合以外に追加する