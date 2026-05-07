# Notes

## 2026-05-07

### Decision: toctree container rendering approach

toctreeコンテナの子paragraphはdocutilsの`nested_parse`でRSTとして再帰パースされるが、
toctreeエントリは純粋なパス文字列（例: `handlers/index`）であり、RST markup ではないため、
結果は `paragraph` ノード内のplain textとなる。

このため `visit_container` で `directive_name == "toctree"` を特別処理し、
`_render_toctree` メソッドを追加して doc_map 経由でMDリンクリストに変換した。

- 解決成功: `* [title](../../{type}/{category}/{file_id}.md)` 形式のbullet list
- 解決失敗: `` * `{path}` `` のコードスパン fallback

`no_knowledge_content` 判定は変更不要 — toctreeリンクが `content` に出力されれば
`content.strip()` が非空になり、自動的に `no_knowledge_content: false` が維持される。

### verify FAIL件数の変化（Task 6）

| バージョン | 変更前 FAIL | 変更後 FAIL |
|-----------|-----------|-----------|
| v6        | 2237      | 0          |
| v5        | 2339      | 0          |
| v1.4      | 1649      | 0          |
| v1.3      | 1071      | 0          |
| v1.2      | 1036      | 0          |

変更前のFAIL件数が多い理由：旧JSON（plain text content）に対して、
新しいvisitor（MDリンク出力）でverifyするとsequential-deleteが失敗するため。
createで再生成後は双方がMDリンク形式で一致し、0件に収束。

横断確認: 全5バージョンで同じ `visit_container` / `_render_toctree` コードパスを共有するため、
すべてのバージョンで同じ修正が適用された。
