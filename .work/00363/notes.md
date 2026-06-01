# Notes: PR #365 タスク設計の根拠（レビュー用 / CC 非対象）

このファイルは **ユーザーと expert review が読む**ためのもの。CC のタスク実行には不要なので tasks.md からは分離した。

**確認範囲**（2026-06-02、PR #365 ブランチ実物）: `tools/rbkc/scripts/run.py`（`_convert_and_write` 全呼び出し）、`scripts/create/docs.py`・`index.py`、`scripts/verify/verify.py`、`tools/rbkc/docs/rbkc-converter-design.md` §5-2、`rbkc.sh`、`tools/rbkc/lib/`。

---

## 実装環境の確定事実（実物確認済）

- **scripts ルート**: `tools/rbkc/scripts/`。`create/` に converters/docs.py/index.py 等、`common/` に linkfmt.py/rst_ast_visitor.py 等、`verify/verify.py`、`run.py` は `scripts/` 直下。
- **`rbkc.sh`**: `tools/rbkc/rbkc.sh`。CLI は `create <version>` / `verify <version>`。
- **`_convert_and_write()`**（run.py 75行）: 現行 `(fi, output_dir, label_map=None, doc_map=None, sheet_subtype_map=None)`。呼び出しは **create() 254行 と update() 302行 の2箇所**。
- **RST のみ `:java:extdoc:` を持つ**。`_convert_and_write` 内で RST 分岐（95-102行）だけが label_map/doc_map を渡す。MD（103-109行）・xlsx（110-120行）は javadoc_map 不要。
- **docs MD 生成責務**: `docs/javadoc/{file_id}.md` は設計書 §5-2 手順6 で **`javadoc_generate()` 自身**が書き込む。`generate_docs()`（docs.py 290行）は `knowledge_dir.rglob("*.json")` で全 JSON 走査、除外は `assets` のみ（16-20行）。
- **`generate_index_md` / `generate_docs` は create()・update() 双方から呼ばれる**（create 259-260行 / update 308-309行）。
- **QO4 除外パターン**: verify.py 464行 `if "assets" in rel_path.parts: continue`。javadoc も同型で追加（設計書 §3-3 スキャン除外に既記）。
- **jar の現状**: `ff6108c9` で追加 → revert（`f2dd8fc2`/`94200ab6`）で削除済。現ブランチに存在しない。
- **linkfmt.py に `emit_javadoc_link` なし**（revert 済。2-A で新規）。

---

## 設計判断: update() も配線する

`:java:extdoc:` 解決は javadoc_map に依存。`update()` も `_convert_and_write` を呼ぶため、update 経由の再生成で javadoc_map を渡さないと extdoc が未解決のまま JSON 出力され QL1 FAIL する。
→ 本PRでは create()・update() の**両方**に配線し、update 冒頭でも `javadoc_generate()` を呼ぶ。どの経路で再生成しても extdoc が解決される状態を恒常的に保証する。

---

## 前回版から塞いだ穴

| # | 穴 | 実物根拠 | 対応タスク |
| --- | --- | --- | --- |
| 1 | update() 経路に javadoc_map が渡らず QL1 FAIL | `_convert_and_write` は create 254行・update 302行の2箇所 | 2-F で両方配線 + update 冒頭でも javadoc_generate |
| 2 | generate_docs が javadoc JSON を二重 docs MD 化し QO3 衝突 | docs.py 290行 rglob 全走査、除外 assets のみ。docs MD は §5-2 手順6 で javadoc_generate 側が生成 | 2-I を docs.py + index.py 両除外に拡張 |
| 3 | `_convert_and_write` 引数追加が未記載で CC が独自判断 | 現行シグネチャ確認済 | 2-F に After シグネチャ + RST 限定を明記 |
| 4 | 「意図的 RED」を6コミット放置し本物 FAIL を見落とす | — | 2-C 単体のみ + 2-C2 全件ベースライン + 2-J 集合照合 |
| 5 | jar 配置がローカル絶対パス依存で再現不可 | jar は revert で消失済 | 2-D を `git checkout ff6108c9 --` 復元に変更 |

---

## tasks.md と notes.md の分離方針

- **tasks.md（CC 用）**: 指示・前提・完了条件・検知ゲートのみ。「なぜ」は載せない。行番号は「該当箇所の目安」とし CC は grep で再確認する前提。
- **notes.md（本ファイル）**: 根拠・出典・設計判断。コード変更で陳腐化し得る事実主張はこちらに隔離し、tasks.md の指示が古い根拠で汚染されないようにする。
