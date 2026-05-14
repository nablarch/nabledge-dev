# Notes: Issue #321

## 2026-05-14

### Task 3: 設計書の通読結果

3 つの設計書を通読し、実装を知らない読者にとって理解困難な箇所を特定した。

#### rbkc-verify-quality-design.md

1. **L7, 13-15**: 「知識ファイル（JSON）」「閲覧用知識（docs MD）」「index.toon」の説明なし。なぜ 2 種の出力が必要か未説明。
2. **L19, 43, 47**: `scripts/create/`, `scripts/common/`, `converters/resolver/run` が説明なしに参照される。独立性原則の説明が構造知識前提。
3. **L87-107**: 「tokenizer」「正規化ソース」の定義なし。docutils AST Visitor との関係が不明。
4. **L93-107**: ASCII フロー図の表記（`→` / `├─` / `└─` 等）に凡例なし。「削除できなかった」の操作的意味が不明。
5. **L215, 219, 223**: 「Phase 22-B」等のフェーズ参照が説明なし（開発イテレーション？仕様バージョン？）。
6. **L295-305**: `LabelTarget` フィールドの説明が、ファイルシステムレイアウト知識を前提とする。
7. **L313-325**: 「RBKC mapping 採用」という用語が未定義。

#### rbkc-converter-design.md

1. **L15-17**: `RSTResult`, `Section` 型が定義なしに登場。JSON スキーマ設計書への参照なし。
2. **L63-68**: create は `RSTResult`、verify は flat MD string を出力する違いの「なぜ」が未説明。
3. **L120-122**: `doc_map`, `no_knowledge_content`, `type`/`category` ディレクトリ分類が未説明。
4. **L159-161**: `field_list` の「directive option block vs standalone」の区別が RST 内部知識前提。
5. **L280-283**: 「Y-1 probe」が未定義の内部アーティファクト参照。
6. **L340, 369-370**: `.work/00299/...` の内部作業ファイルが設計根拠として引用されている。

#### rbkc-json-schema-design.md

1. **L10-11**: 「KC 形式」「nabledge スキル」「jq クエリ」が説明なし。
2. **L51-54**: `sections[].level` を JSON に持つ理由（なぜ docs.py が再計算できないのか）が未説明。
3. **L89-94**: 2000 文字閾値の根拠が未文書化。
4. **L166-170**: `read-sections.sh` のバグ言及が文脈なし。
5. **L57-58**: `index.toon` の形式・場所・生成方法が 3 文書いずれにも説明なし。

→ 詳細: investigate agent の出力による
