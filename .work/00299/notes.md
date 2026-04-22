# Notes

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
