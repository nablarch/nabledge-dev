# Notes

## 2026-03-25〜26

### nabledge-testシナリオ設計（合意済み）

v5/v6との対応とv1.4固有の差分を確認しながらシナリオを設計した。

**QAシナリオ（合意済み）**:

| id | 変更内容 |
|----|---------|
| qa-001 | `n:optionItems`/`listId`/`コードリスト` はRSTに存在しない → `n:codeSelect`, `codeId`, `n:select`, `コード値` に変更 |
| qa-002 | v1.4にUniversalDaoなし → 質問を「一覧検索でページングを実装するには？」に変更、`ListSearchInfo`, `search`, `DbAccessSupport`, `ページング` |
| qa-003 | v5/v6と同じ（BatchRequestTestSupportはv1.4も同じAPI） |
| qa-004 | `n:token` は v1.4 では使わない → `useToken` に変更 |
| qa-005 | `ValidateFor` を追加（v1.4回答にも現れることを確認） |

**CAシナリオ（未レビュー）**:
- ca-001: W11AC01Action — 期待値未合意のまま。明日レビュー要
- ca-002: W11AC02Action（benchmark）— 期待値未合意のまま。明日レビュー要

### 副次的発見: v5/v6 qa-001も間違い

`n:optionItems`/`listId`/`コードリスト` はv5/v6 RSTにも存在しない。
→ Issue #242 を作成済み。v5/v6のbaseline再取得も将来的に必要。

### クリーンアップ（完了 2026-03-26）

~~`.tmp/nabledge-test/run-20260325-234314/`~~ → 削除済み
~~`.nabledge/20260325/code-analysis-*.md`~~ → 削除済み

### 再開手順

1. CAシナリオ（ca-001/ca-002）の期待値をレビュー・合意
2. `nabledge-test 1.4 --baseline` を実行
