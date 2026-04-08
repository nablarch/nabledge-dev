# Notes - Issue #252: v1.x のプロジェクトベース統一

**Date**: 2026-04-08
**Branch**: 252-fix-verify-dynamic

## 完了した作業

### 2026-04-08 セッション2

#### Task: v1.x の setup_env と verify_dynamic を v6 ベースに変更

v1.x テスト環境が SVN 由来の tutorial ディレクトリを使用していたため、`.git` がない状態で CC/GHC CLI がプロジェクトルート判定に失敗していた。これを修正。

**実装内容**:

1. **setup_env 呼び出し** (行167-172)
   - v1.4, v1.3, v1.2: `$V14_PROJECT_SRC/"tutorial"` → `$V6_PROJECT_SRC/"nablarch-example-batch"`
   - すべて `$HINT_V6` を使用

2. **verify_env 呼び出し** (行385-390)
   - プロジェクトパス: `v1.x/test-{cc,ghc}/tutorial` → `v1.x/test-{cc,ghc}/nablarch-example-batch`

3. **verify_dynamic 呼び出し** (行401-406)
   - プロジェクトパス: 同上

4. **Summary セクション** (行439-444)
   - 出力パス表示: `tutorial` → `nablarch-example-batch` に更新
   - 左揃えをそろえて見やすく調整

5. **クリーンアップ**
   - 不要な `V14_PROJECT_SRC`, `V13_PROJECT_SRC`, `V12_PROJECT_SRC` 変数削除
   - 不要な `HINT_V14`, `HINT_V13`, `HINT_V12` 削除
   - 関連コメント更新（SVN 参照削除）

**ゲート**:
- ✅ `bash -n` syntax OK
- ✅ `grep -c 'tutorial'` = 0（すべての obsolete 参照削除確認）

**コミット**:
```
93d12e86 fix: unify v1.x test environment base project to v6's nablarch-example-batch (#252)
```

## 残りの作業（明日再開）

### 未実施項目（PR本体にまだ含まれていないもの）

- ベースライン削除（v1.2, v1.3, v1.4, v5 の古い実行結果）
- nabledge-test SKILL.md の更新
- workflow コード分析テンプレート削除
- スクリプト側の prefill-template.sh 修正

### 推定される次ステップ

1. **検証実行**: `bash tools/tests/test-setup.sh` で全20行の動的チェック実行
   - 各バージョン CC/GHC のペアが [OK] または detection rate 50%以上を確認
   
2. **PR本文作成**:
   ```
   ## Summary
   - v1.x テスト環境を tutorial (SVN) から v6 の nablarch-example-batch に統一
   - CC/GHC プロジェクトルート判定の問題を解決
   - 動的チェックはナレッジ検索のみ（読み取り専用）なので v6 ベース使用で十分
   
   ## Tasks
   - [x] tools/tests/test-setup.sh v1.x パス統一
   - [ ] 検証実行（setup.sh → test-setup.sh）
   - [ ] PR本文作成＆expert review
   ```

3. **Expert Review**: Software Engineer として品質確認
   - 設定の一貫性
   - エラーハンドリング
   - テスト環境の完全性

## 技術背景

**問題**:
- v1.4/v1.3/v1.2 の tutorial は SVN チェックアウト（`.git` なし）
- CC/GHC は `.git` で git リポジトリを検出
- 見つからないと親ディレクトリを遡って nabledge-dev ルートをプロジェクト認識
- `GIT_CEILING_DIRECTORIES` で回避していたが、プロジェクトルート判定が不安定

**ソリューション**:
- 動的チェック = ナレッジ検索のみ（読み取り専用操作）
- v1.x でも v6 の nablarch-example-batch を使用可
- プロジェクトルート判定が安定（`.git` あり）

**利点**:
- テスト環境構成が単純化
- 不要な SVN 参照削除
- v1.4/v1.3/v1.2 用のダウンロード時間削除（setup.sh で SVN チェックアウト不要）

## 関連issue/PR

- Issue #252: verify_dynamic の改善
- PR #277: re-baseline nabledge-test
- nabledge-dev/nabledge-6, v5, v1.x スキル全対応
