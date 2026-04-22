# Notes

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

現在の verify.py は `_verify_normalise_backup.py` として保全済 (session 42)。Phase 21-X Step X-4 で tokenizer ベースに書き直す。

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
