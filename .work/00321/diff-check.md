# Diff Check: Issue #321

## Task 3: 設計書に §0「この文書を読む前に」追加

**Date**: 2026-05-14

**対象ファイル**:
- `tools/rbkc/docs/rbkc-json-schema-design.md`
- `tools/rbkc/docs/rbkc-converter-design.md`
- `tools/rbkc/docs/rbkc-verify-quality-design.md`

**変更箇所**:

| ファイル | 変更内容 |
|----------|----------|
| rbkc-json-schema-design.md | §0 追加: 全体像（フロー図）/ 用語（KC 形式・nabledge スキル・jq クエリ・h1〜hN）/ `sections[].level` の「なぜ」 / 2000 文字閾値の根拠 / `read-sections.sh` バグの文脈説明 |
| rbkc-converter-design.md | §0 追加: 全体像（フロー図）/ 用語（AST・Visitor・正規化 MD・RSTResult・sequential-delete・create/verify）/ ディレクトリ構成 / `field_list` の context-aware 説明補足 / `Y-1 probe` の定義 / `.work/` 参照の補足 |
| rbkc-verify-quality-design.md | §0 追加: 全体像（フロー図）/ 出力ファイルの役割 / 品質 ID の読み方 / 用語（RBKC mapping・corpus・Phase・tokenizer/正規化ソース）/ `scripts/common/` の列挙補完 / `LabelTarget` のファイルシステムレイアウト前提説明 |

**確認**:
- 既存の仕様内容の変更: なし（追記のみ）
- 想定外変更: なし

---

## Task 1: シンボル統一（⚠️ 廃止）

**Date**: 2026-05-14

**対象ファイル**: `tools/rbkc/docs/rbkc-verify-quality-design.md`

**変更箇所**:

| 位置 | 変更前 | 変更後 |
|------|--------|--------|
| §4 凡例 | `❌ 未実装` | `❌ 未実装・未検証` |
| §3-1 QC テーブル (5行) | ⚠️ → 各セル | §4 と一致する ✅/— |
| §3-2 QL テーブル (2行) | ⚠️ → 各セル | §4 と一致する ✅/— |
| §3-3 QO テーブル (4行) | ⚠️ → 各セル | §4 と一致する ✅/— |
| §3-4 QP テーブル (1行) | ⚠️ | ❌ |
| §4 出力マトリクス QO1 section level | ⚠️ | ❌ |
| §4 構造検証マトリクス QP | ⚠️ | ❌ |

**確認**:
- `grep -n "⚠️"` の結果: 0件（全廃止確認済み）
- §3 と §4 の各シンボルの一致: 目視確認済み
- 想定外変更: なし
