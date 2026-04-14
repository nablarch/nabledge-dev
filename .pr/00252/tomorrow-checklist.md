# 明日の実施チェックリスト

**PR #252**: v1.x のプロジェクトベース統一

## 完了済み（本日）

- [x] `tools/tests/test-setup.sh` 修正
  - setup_env, verify_env, verify_dynamic の v1.x パス更新
  - 不要変数・コメント削除
  - Syntax OK、tutorial 参照ゼロ確認
- [x] 作業ノート作成 (`.pr/00252/notes.md`)
- [x] PR本文ドラフト作成 (`.pr/00252/pr-body-draft.md`)

## 明日の実施順序

### Step 1: 検証実行
```bash
cd /home/tie303177/work/nabledge/work3
source .env
bash tools/tests/test-setup.sh
```

**期待される結果**:
- 全20行の動的チェック（CC/GHC × v6/v5/v1.4/v1.3/v1.2 各2回）
- 各行: [OK] または detection rate 50%以上
- エラーなし

### Step 2: PR作成
```bash
# 本文ドラフトを確認してから、以下で作成
gh pr create --title "fix: unify v1.x test environment base project to v6's nablarch-example-batch (#252)" \
  --body "$(cat .pr/00252/pr-body-draft.md)"
```

### Step 3: Expert Review
- **Expert**: Software Engineer
- **Focus**: 
  - 設定の一貫性（環境変数、パス）
  - エラーハンドリング（プロジェクト見つからない場合など）
  - テスト構造の完全性
- **Output**: `.pr/00252/review-by-software-engineer.md`

### Step 4: PR本文最終化
- Expert Review の結果を PR 本文に反映
- 必要に応じてコード修正（High/Medium priority issue）

## 懸念点・確認事項

### 1. v1.x でも v6 ベース使用の妥当性

✅ **確認済み**: 動的チェックはナレッジ検索のみ（読み取り専用）
- v1.4/v1.3/v1.2 の特定シナリオ(qa-001など)で v6 ベースで十分
- 問題なければ検証実行で detection rate 50%以上を確認予定

### 2. 不要変数の削除について

✅ **判断**: 削除を実施した
- `V14_PROJECT_SRC`, `V13_PROJECT_SRC`, `V12_PROJECT_SRC`
- `HINT_V14`, `HINT_V13`, `HINT_V12`
- コード内で参照されていないため削除しても問題なし

### 3. Baseline 削除はこのPR?

❓ **未定**: PR本文には含めない
- 別途のbaseline cleanup PR として実施する可能性あり
- このPRはツール設定（test-setup.sh）のみフォーカス

## ファイル参照

- 修正内容: `tools/tests/test-setup.sh`
- 作業ノート: `.pr/00252/notes.md`
- PR本文案: `.pr/00252/pr-body-draft.md`
- ルール: `.claude/rules/expert-review.md`

## 関連PR・Issue

- Issue #252: verify_dynamic の改善
- Issue #277: nabledge-test re-baseline
- 前提: setup.sh で v6/v5 のみダウンロード（v1.x は tutorial チェックアウト不要に）
