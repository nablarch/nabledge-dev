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

## 2026-04-10 セッション

### 状況

実装・Expert Review・PR作成はすべて完了済み (PR #296)。

残り1つ: **`bash tools/tests/test-setup.sh` を実行して全体を実証確認してからマージ**。

### 問題: test-setup.sh が GitHub ネットワーク問題でハング

`git sparse-checkout set` のblob fetch（1009 objects、setup-cc.sh内の2回目のgit操作）が途中（17%や92%等）でハングする。

- `git ls-remote` での疎通確認: OK
- こちら環境（同WSL）での再現: 発生しない（3秒で完了）
- → GitHubのCDNノードまたはIPレートリミットの可能性

**対処**: 時間をおいて再実行、またはMTU低下で改善する場合あり:
```bash
sudo ip link set dev eth0 mtu 1200
```

### 次ステップ（再開時）

1. `bash tools/tests/test-setup.sh` を実行 — 全12環境の静的チェック＋動的チェックが全 [OK] を確認
2. 問題なければ `/bb` でマージ

### メモ: 旧 notes の「未実施項目」について

2026-04-08 時点で記載していた以下はいずれも issue #252 のスコープ外:
- ベースライン削除（別issue）
- nabledge-test SKILL.md 更新（別issue）
- workflow コード分析テンプレート削除（別issue）
- prefill-template.sh 修正（別issue）

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
