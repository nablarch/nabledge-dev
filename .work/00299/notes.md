# Notes

## 2026-04-22 (session 44) — Phase 21-X Step X-2 完了

### X-2 調査結果サマリー (全 5 バージョン・1477 RST ファイル)

**inline patterns** (`.work/00299/phase21x/inline-patterns.json`):

| Pattern | 総数 | ユニーク |
|---|---:|---:|
| role_target (`:r:\`t <tgt>\``) | 6,921 | 5 |
| role_simple (`:r:\`t\``) | 8,515 | 4 |
| double_backtick (``` ``x`` ```) | 5,362 | — |
| ext_link_named (`` `t <url>`_ ``) | 766 | — |
| ref_named (`` `t`_ ``) | 819 | — |
| substitution (`\|name\|`) | 1,140 | 22 |
| footnote_ref (`[x]_`) | 716 | — |
| strong / emphasis | 6,355 / 549 | — |
| interpreted (バック1個) | 888 | — |

- **Role 名は 4 種のみ**: `ref`, `doc`, `java:extdoc`, `download`, `javadoc_url`。
- **Substitution 名は 22 種のみ**（`br` が圧倒的多数）。

**block patterns** (`.work/00299/phase21x/block-patterns.json`):

- **Directive は 22 種**: `code-block` (5,744), `image` (1,281), `tip` (942), `note` (808), `important`, `toctree`, `list-table`, `contents`, `raw`, `warning`, `admonition`, `table`, `include`, `figure`, `function`, `literalinclude`, `attention`, `class`, `hint`, `java:method`, `csv-table`, `rubric`
- **セクション見出しアンダーライン**: `= - ^ ~ * + \` < > : . _` の 12 種
- **テーブル**: simple-table 6,348 sep / grid-table 2,254 sep + 413 head / list-table 397
- **field list**: 64 種 (`scale`, `maxdepth`, `header-rows`, `class`, `widths`, `depth`, `file`, `align`, `width`, `language`, `return`, ...)
- **bullet markers**: `*` (12,817), `-` (4,656), `+` (347)
- **line-block** (leading `|`): 8,278 行（v1.3/1.2 で特に多い）

**変換規則** (`.work/00299/phase21x/transform-rules.md`) — v6 snapshot 比較:

| Pattern | verbatim | transformed/dropped |
|---|---:|---:|
| role_target | 0 | 2,902 |
| role_simple | 0 | 5,039 |
| double_backtick | 6 | 2,442 |
| ext_link_named | 0 | 282 |
| ref_named | 0 | 103 |
| substitution | 14 | 373 |
| footnote_ref | 198 | 0 |
| strong | 285 | 0 |
| emphasis | 105 | 1 |
| interpreted | 327 | 198 |

⇒ Role/backtick/ext-link はほぼ 100% 変換される。Strong/emphasis/footnote_ref はほぼ verbatim。

**pilot residue** (`.work/00299/phase21x/residue-triage.md`) — プロトタイプ reducer の coverage:

- match (exact): 12,807
- match (space-normalised): 58
- miss: 3,152
- **coverage: 80.3%**

主な miss の原因（実例分析から分類）:
- `:ref:\`label\`` のラベル解決（ラベル → 参照先タイトル置換）が reducer 側未対応
- line-continuation `\` 末尾で RST ソースが改行された行が、MD 側では 1 行に統合される
- field list の value（例 `:widths: 20 80`）が JSON content に含まれるが reducer の削除ルールで落ちる
- 先頭文字が ASCII 以外の `|name|` （substitution 扱いだが実データはラベル）と、grid-table の `|` 始まりセル
- `java:extdoc:\`Klass<FQN>\`` のラベル部分が MD 側ではリンク化される

**cross-version** (`.work/00299/phase21x/cross-version-diff.md`):

- Role 名セット（`ref`/`doc`/`java:extdoc`/`download`/`javadoc_url`）は全バージョン共通。
- `java:extdoc` は v6/v5 のみ、v1.x には存在しない（v1.x は Javadoc を別記法）。
- Directive の全バージョン共通セット: `code-block`, `image`, `list-table`, `note`, `warning`, `tip`, `figure`, `include`, `contents`, `table`, `raw`, `admonition`, `function`, `attention`。
- v1.x 固有: `admonition`, `function`, `literalinclude` の使用比が高い。
- Section underline chars も全バージョン共通（`= - ^ ~` が主体）。

### 結論

- tokenizer が扱うべき inline 構文は **8 種** (role_target, role_simple, double_backtick, ext_link_named, ref_named, substitution, footnote_ref, interpreted) + strong/emphasis の 10 種で閉じている。
- Directive は 22 種で閉じている。うち admonition 系 (note/tip/warning/important/attention/hint/admonition) は body text を保持、残り (code-block/image/toctree/raw/...) は完全に落とす、という二分類で設計できる。
- Label resolution（`:ref:` の target → 参照先タイトル）は converter 側で `label_map` を使って実装済み。tokenizer もこの map を受け取り同じ変換をかける。
- Substitution は 22 種の閉集合なので substitution definition を読み取る関数で十分。
- Line-continuation `\` は逆方向で、RST → MD 変換で行が結合される。tokenizer 側で `\\\n` → ` ` に正規化する必要がある。
- **80% の coverage を粗い pilot で達成**しており、残 20% は上記で分類できている。

X-3 以降で設計書を更新し、tokenizer を TDD で実装する。

---

## 2026-04-22 (session 43)

### Decision: tokenizer 方式に切替 (Phase 21-X)

**背景**:

session 43 の対話で、設計書 3-1 節「ソース原文のまま・削除だけ」が以下の converter 変換により**機械的に substring 一致不能**と確認:

- `:ref:\`label\`` → ラベル解決により別文字列（参照先タイトル）に置換
- `` ``code`` `` → `` `code` `` (backtick 数変化)
- `` `text <url>`_ `` → `[text](url)` (括弧の構造自体が別形式)
- `\|name\|` (substitution 参照) → 定義先展開後のテキスト
- `.. note::` + 本文 → `> **Note:** ` + 本文 (admonition)
- RST simple/grid/list-table → MD table `| --- |` 形式に再構成

**前回 (`_normalize_rst_source` 300行) が失敗した構造的原因**:

1. 場当たり: 実装中にパターンを見つけて regex を追加
2. 積み上げ: 複数 regex が同じ行を書き換え、適用順に副作用
3. 推測ベース: RST 公式仕様でなく実装者の推測

**今回の違い**:

- **実装前**に全バージョン・全ファイルを走査してパターンを網羅 (Phase 21-X Step X-2)
- **tokenizer 方式**: 字句解析で token 列に切り、各 token を独立純粋関数で変換 (順序非依存)
- **規則は RST 公式仕様 (docutils) + 実データ実測** から導出
- **設計書更新** が必須 (3-1 手順に「手順0: ソース前処理 (tokenizer)」を追加)

### 関連コミット (session 42 — 参考資料として保全)

Phase 21-W 方針で session 42 に行った修正は参考資料として維持。Phase 21-X の tokenizer 設計時に「どの構文をどう変換すべきか」の実データ例として活用する:

- `9abea1c57` fix(rbkc): reduce v6 verify FAIL 310→240 via verify/converter fixes
- `31de50369` fix(rbkc): preserve nested-directive body in simple-table cells
- `56988a2bf` fix(rbkc): batch verify/converter fixes reduce FAIL 162→135
- `64253ec5b` fix(rbkc): grid-table sub-separators + simple-table substitutions

現在の verify.py は `_verify_normalise_backup.py` として保全済 (session 43 で git add)。Phase 21-X Step X-4 で tokenizer ベースに書き直す。

### 最新コミット (Phase 21-X 開始時点)

```
5dee028c0 docs: update tasks.md — Phase 21-X tokenizer approach (supersedes 21-W)
600a243bc docs: add Phase 21-W — rewrite verify per design (abandon normalisation)
64253ec5b fix(rbkc): grid-table sub-separators + simple-table substitutions
56988a2bf fix(rbkc): batch verify/converter fixes reduce FAIL 162→135
31de50369 fix(rbkc): preserve nested-directive body in simple-table cells
```

---

## 2026-04-22 (session 42)

### Decision: verify の正規化パイプラインを廃止し、設計書通りに書き直す (Phase 21-W)

**背景**:

session 41 〜 session 42 で FAIL を 310→120 まで削減したが、潰したパターンの多くは `_normalize_rst_source` に正規表現を追加するものだった。結果として verify は:

- ソース（RST）側を MD-ish な中間形式に寄せる正規化（300行超）
- JSON（MD）側を同じ中間形式に寄せる正規化
- 両側を中間形式で substring 比較

という、設計書から逸脱した二重正規化パイプラインになっていた。

**設計書が求めているもの**（`rbkc-verify-quality-design.md` 3-1 節）:

```
[JSON content] → MD構文を除去 → token列
[ソースファイル] から token を順次「削除」
  削除できなかった token → FAIL (QC2/QC3/QC4)
  削除後の残渣に「許容構文要素」以外が残っていれば → FAIL (QC1)
```

- ソース側は**原文のまま、削除するだけ**
- 残渣は「許容構文要素リスト」（設計書 3-1 末尾）で判定

**間違っていた理由**:

- 「JSON の MD 構文除去」と「ソース原文保持」という非対称な扱いを理解していなかった
- モグラ叩きで正規表現を追加していく過程で、ソース側も正規化する方針に無自覚に移行
- 各修正の副作用で別のテストが壊れ、パッチのパッチが積み重なった

**今後の方針** (Phase 21-W):

1. `_normalize_rst_source` を全廃
2. `_normalize_md_unit` は維持（設計書通り）
3. sequential-delete を**生ソースに対して**実行
4. QC1 残渣判定は**許容構文リスト**との純粋な構文照合
5. 許容構文リストに追加が必要なら**設計書を先に更新**しユーザー承認を得る

**期待される効果**:

- verify のコード行数が大幅削減
- 新規 false positive の原因が「構文かコンテンツか」の単純判定に帰着
- RBKC 側の真のバグと verify 側の許容リスト漏れが明確に分離される

### 関連コミット（session 42 でやったモグラ叩き系）

以下は方針転換前の修正。削除せず維持するが、Phase 21-W で verify を書き直す際は参考資料として読み、必要な構文パターンを許容構文リストに整理する:

- `9abea1c57` fix(rbkc): reduce v6 verify FAIL 310→240 via verify/converter fixes
- `31de50369` fix(rbkc): preserve nested-directive body in simple-table cells
- `56988a2bf` fix(rbkc): batch verify/converter fixes reduce FAIL 162→135
- `64253ec5b` fix(rbkc): grid-table sub-separators + simple-table substitutions
- 未コミット: `<url>`_ greedy text match (120件時点)

## 2026-04-23 (session 48) — Phase 21-Y / Y-1 docutils AST probe 完了

### 実施内容

`tools/rbkc/.work/y1_probe_ast.py` を作成し、v6 / v5 / v1.4 / v1.3 / v1.2 の全 2,581 RST ファイルを `docutils.core.publish_doctree` に通して AST を取得・計測。

Sphinx 固有 role (`ref`/`doc`/`java:extdoc`/`download`/`javadoc_url` ほか) と v1.x 固有 directive (`function`/`class`) は minimal shim を登録し、docutils 組み込み directive (admonition 14 種・image/figure/table/list-table/rubric/contents/topic など) は**シムせずに実 node として取得**するようにした。

### 判明したこと (`.work/00299/phase21y/ast-probe.md` / `ast-probe.json`)

**1. パース成功率は実用水準**

| Version | Total | OK | Warn | Error |
|---|---:|---:|---:|---:|
| v6 | 667 | 667 | 0 | 0 |
| v5 | 772 | 771 | 1 | 0 |
| v1.4 | 464 | 389 | 71 | 4 |
| v1.3 | 380 | 317 | 62 | 1 |
| v1.2 | 298 | 239 | 59 | 0 |

v6/v5 は完全にクリーン。v1.x は「bullet list/block quote/definition list ends without a blank line」等の**ソース側 RST 仕様ゆるみ**が大半で、docutils は警告扱い (WARNING) しつつも AST を構築する。パース失敗 (4+1+0=5 件) は真の malformed table / skipped title level 等。Visitor 側で警告ノードをスキップすれば実用上問題なし。

**2. `morerows` / `morecols` は AST に乗る**

| Version | tables | entries | morerows | morecols |
|---|---:|---:|---:|---:|
| v6 | 632 | 9,766 | 74 | 52 |
| v5 | 810 | 14,626 | 91 | 77 |
| v1.4 | 1,138 | 18,809 | 133 | 90 |
| v1.3 | 879 | 14,251 | 77 | 72 |
| v1.2 | 737 | 11,015 | 72 | 55 |

grid-table の rowspan/colspan が `entry.morerows` / `entry.morecols` 属性として読める。現 converter の自前 grid-table 実装で苦しんでいた領域が reference 実装で解決済。

**3. Substitution は transform 後に `raw` / text へ展開済**

`substitution_definition` ノードは保持されるが `substitution_reference` は Substitutions transform で raw ノードに置換されて消える (v6=95 def / v5=133 def / v1.4=1 / v1.3=0 / v1.2=0)。Visitor は `raw` ノードを最終 MD として扱えばよく、substitution を別扱いする必要なし。

**4. 組み込み directive が素で取れる node 種別**

- admonition 系: `note` / `tip` / `important` / `warning` / `attention` / `hint` / `admonition` / `caution` / `danger` / `error`
- figure/image、footnote / footnote_reference、transition、field_list、topic、rubric、line_block
- `reference` には `refuri` (外部 URL) / `refname` (named internal) / `refid` (resolved internal) / `anonymous` 属性が揃う

各バージョンの count (抜粋): v6 tip=872, important=570, image=602, footnote=307, transition=34。v1.x は admonition=94, note=474 (v1.4), line_block=2,433。

**5. Include 系は `file_insertion_enabled=False` で無効化**

`.. include::` / `literalinclude` は converter 側で `scripts/common/rst_include.py` を使った pre-processing に委ねる (Y-2 対応表で明示)。

**6. Cross-ref 解決は AST 後の hook で対応**

`:ref:` / `:doc:` などの shim はいま `inline` ノードに置換している。Visitor では `inline.classes` から `role-ref` 等を検出し、`targets` 辞書でラベル解決する。

### Y-1 結論

docutils AST は全バージョンの実データで **converter の入力として十分に成立する**:

- 自前 parse (grid-table / simple-table / inline / substitution / directive) を全廃できる
- rowspan / colspan / substitution / footnote / transition / admonition 14 種 / table 3 種がすべて AST node として取れる
- Sphinx 固有構文は minimal shim (inline role 10 種・container directive 4 種・literal directive 3 種) で全量吸収できる
- パース失敗 5 件は真の malformed であり、converter 側でも扱えない (現 converter 出力も破損)

→ Y-2 (Visitor 設計) に進む。

### 次の判断点

1. **Y-2 開始可否**: この probe 結果で AST 方式の実現可能性確認が取れたと判断してよいか
2. **Include の扱い**: Y-2 対応表に「converter が include を事前展開して doctree に渡す」と明記する方針で OK か
3. **Cross-ref の扱い**: `targets` 辞書経由の解決を Visitor の post-processing として実装する方針で OK か
