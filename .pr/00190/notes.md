# Notes - PR #190

## 2026-03-13

### 現在の作業状況（再開ポイント）

**未コミットの変更ファイル** (`tools/knowledge-creator/` 配下):

| ファイル | 状態 | 内容 |
|---------|------|------|
| `mappings/v1.4.json` | modified | `document/` prefix を全パターンに追加、sample/portal パターン追加（ID dedup 修正）、レビュー指摘を反映 |
| `mappings/v1.3.json` | **new (未追跡)** | single-repo パターン（`1.3_maintain/` をストリップ後のパス） |
| `mappings/v1.2.json` | **new (未追跡)** | single-repo パターン（`1.2_maintain/` をストリップ後のパス） |
| `scripts/step2_classify.py` | modified | v1.4用条件分岐: `classify_rst`と`generate_id`でrepoマーカーをrel_pathに残す |
| `tests/e2e/generate_expected.py` | modified | 同上の修正（E2Eテスト期待値生成用） |

### 次のステップ

1. **E2Eテスト確認**:
   ```bash
   cd tools/knowledge-creator
   python -m pytest tests/e2e/test_e2e.py -k "1.4" -v
   ```
2. 通ったら **全バージョン** も確認:
   ```bash
   python -m pytest tests/e2e/test_e2e.py -v
   ```
3. テスト通過後、全5ファイルをコミット:
   ```bash
   git add tools/knowledge-creator/mappings/v1.4.json \
           tools/knowledge-creator/mappings/v1.3.json \
           tools/knowledge-creator/mappings/v1.2.json \
           tools/knowledge-creator/scripts/step2_classify.py \
           tools/knowledge-creator/tests/e2e/generate_expected.py
   git commit -m "feat: add v1.4/v1.3/v1.2 mapping files and fix multi-repo path handling"
   ```
4. Push して PR #190 のレビューコメントに返信

### 重要な設計判断（絶対に戻さないこと）

**v1.4 multi-repo パス処理**:
- `step2_classify.py`: v1.4 のみ `rel_path = marker + path[idx + len(marker):]`（`document/`, `workflow/` 等のprefixを保持）
- v5/v6 の後方互換を保つため `if self.ctx.version == "1.4":` で条件分岐
- `v1.4.json` のパターンはrepoプレフィックス付き（例: `document/FAQ/batch/`）
- `v1.2.json` / `v1.3.json` のパターンはプレフィックスなし（single-repo、マーカーストリップ後のパス）

### テストが失敗していた経緯

- 最初: v1.4.json のパターンが `FAQ/batch/`（prefixなし）→ 117ファイル未マッピング
- 修正1: step2_classify.py でマーカーを保持 + v1.4.json に `document/` prefix 追加
- 修正2: `sample/portal/src/source/faq/*` のIDデデュップ失敗 → 個別パターン追加
- 修正3: session-scoped fixture が v1.3.json を要求 → v1.3.json / v1.2.json 新規作成
- 現状: v1.3.json/v1.2.json 作成済み、テスト実行中（セッション終了のため結果未確認）
