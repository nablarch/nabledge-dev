# Gitスキル - 詳細リファレンス

このドキュメントは、gitスキルの詳細な技術仕様とワークフローを記載します。

## 目次

1. [Git用語説明](#git用語説明)
2. [ブランチ命名規則](#ブランチ命名規則)
3. [Conventional Commits形式](#conventional-commits形式)
4. [機密ファイルの検出ロジック](#機密ファイルの検出ロジック)
5. [ワークツリーの仕組み](#ワークツリーの仕組み)
6. [エラーハンドリング詳細](#エラーハンドリング詳細)
7. [トラブルシューティング](#トラブルシューティング)
8. [ベストプラクティス](#ベストプラクティス)

## Git用語説明

### ブランチ関連
- **作業ブランチ**: 機能開発やバグ修正のために作成するブランチ
- **mainブランチ**: メインの開発ブランチ（masterとも呼ばれる）
- **マージ済みブランチ**: mainブランチにマージされたブランチ
- **未マージブランチ**: mainブランチにマージされていないブランチ

### コミット関連
- **ステージング**: コミット対象のファイルを選択する操作
- **コミット**: 変更をローカルリポジトリに記録する操作
- **プッシュ**: ローカルの変更をリモートリポジトリに送信する操作
- **HEREDOC**: シェルスクリプトで複数行の文字列を扱う記法

### ワークツリー関連
- **メインワークツリー**: 元のリポジトリディレクトリ
- **ワークツリー**: 同じリポジトリの別ディレクトリ（並行作業用）
- **ワークツリーパス**: ワークツリーが作成されるディレクトリのパス

## ブランチ命名規則

### プレフィックス

| プレフィックス | 用途 | 例 |
|--------------|------|-----|
| `add-` | 新機能の追加 | `add-user-auth` |
| `fix-` | バグ修正 | `fix-login-page` |
| `refactor-` | リファクタリング | `refactor-api-layer` |
| `update-` | 既存機能の更新・改善 | `update-user-settings` |
| `docs-` | ドキュメント更新 | `docs-setup-guide` |
| `test-` | テストの追加・修正 | `test-auth-logic` |
| `chore-` | ビルド、設定等の変更 | `chore-update-deps` |

### 命名ルール

1. **小文字のみ**: すべて小文字で記述
2. **英数字とハイフン**: 使用可能な文字は`a-z`, `0-9`, `-`のみ
3. **プレフィックス必須**: 作業内容を表すプレフィックスを付ける
4. **簡潔に**: 3-5単語程度、最大50文字以内
5. **説明的**: ブランチの目的が分かる名前にする

### 良い例・悪い例

**良い例**:
- `add-user-profile` - 明確で簡潔
- `fix-login-timeout` - バグの内容が分かる
- `refactor-database-layer` - リファクタリング対象が明確

**悪い例**:
- `feature` - 内容が不明
- `Add-User-Profile` - 大文字を使用している
- `add_user_profile` - アンダースコアを使用している
- `add-a-new-feature-for-user-profile-management` - 長すぎる

## Conventional Commits形式

### コミットタイプ

| タイプ | 説明 | 例 |
|--------|------|-----|
| `feat` | 新機能の追加 | `feat: ユーザー認証機能を追加` |
| `fix` | バグ修正 | `fix: ログイン時のセッションタイムアウトを修正` |
| `refactor` | リファクタリング | `refactor: API層のエラーハンドリングを改善` |
| `update` | 既存機能の更新・改善 | `update: ユーザー設定画面のUIを改善` |
| `docs` | ドキュメント更新 | `docs: READMEにセットアップ手順を追加` |
| `test` | テストの追加・修正 | `test: ユーザー認証のテストを追加` |
| `chore` | ビルド、設定等の変更 | `chore: 依存パッケージを最新化` |

### メッセージ形式

```
{type}: {目的・意図を表す簡潔な説明}

Co-Authored-By: Claude (jp.anthropic.claude-sonnet-4-5-20250929-v1:0) <noreply@anthropic.com>
```

### メッセージ生成ルール

1. **1行目（タイトル）**:
   - 50文字以内を目標（最大70文字）
   - 日本語で記述
   - 目的または意図が伝わる内容にする
   - 「〜を追加」「〜を修正」など、動作を明確に

2. **Co-Authored-By**:
   - 2行目は空行
   - 3行目にClaude署名を追加

### 生成例

**変更内容**: ユーザー認証機能の実装
```
feat: ユーザー認証機能を追加

Co-Authored-By: Claude (jp.anthropic.claude-sonnet-4-5-20250929-v1:0) <noreply@anthropic.com>
```

**変更内容**: ログインバグ修正
```
fix: ログイン時のセッションタイムアウトを修正

Co-Authored-By: Claude (jp.anthropic.claude-sonnet-4-5-20250929-v1:0) <noreply@anthropic.com>
```

**変更内容**: API層のリファクタリング
```
refactor: API層のエラーハンドリングを改善

Co-Authored-By: Claude (jp.anthropic.claude-sonnet-4-5-20250929-v1:0) <noreply@anthropic.com>
```

## 機密ファイルの検出ロジック

### 検出パターン

gitスキルは以下のパターンに一致するファイルを自動的に機密ファイルとして検出します:

#### 環境変数ファイル
```
.env
.env.*
.env.local
.env.production
.env.development
```

#### 認証情報ファイル
```
*credentials*
*secret*
*password*
config/credentials.yml.enc
config/secrets.yml
```

#### 鍵ファイル
```
*.key
*.pem
*.p12
*.pfx
id_rsa
id_rsa.pub
```

#### データベース設定
```
config/database.yml
database.yml
```

#### その他
```
.npmrc (認証トークンを含む場合)
.pypirc
.dockercfg
.docker/config.json
```

### 検出時の動作

1. **警告表示**: 機密ファイルが検出されたことをユーザーに通知
2. **自動除外**: コミット対象から自動的に除外
3. **処理継続**: 他のファイルは通常通りコミット

### 例外処理

機密ファイルを意図的にコミットしたい場合は、手動でコミットしてください:

```bash
git add .env.example  # サンプルファイルは問題ない
git commit -m "chore: 環境変数のサンプルを追加"
```

## ワークツリーの仕組み

### ワークツリーとは

ワークツリーは、同じGitリポジトリの異なるブランチを別のディレクトリで操作できる機能です。

### メリット

1. **並行作業**: 複数の機能を同時に開発できる
2. **緊急対応**: 作業中のブランチを保持したまま、別ブランチで緊急バグ修正
3. **レビュー対応**: メインの作業を中断せずに、レビュー対応を行える

### ディレクトリ構造

```
/home/user/work/
├── nab-agents/              # メインワークツリー (mainブランチ)
├── nab-agents-add-feature/  # ワークツリー1 (add-featureブランチ)
└── nab-agents-fix-bug/      # ワークツリー2 (fix-bugブランチ)
```

### パス命名規則

```bash
{親ディレクトリ}/{リポジトリ名}-{ブランチ名}
```

例:
- メインリポジトリ: `/home/user/work/nab-agents`
- ワークツリー: `/home/user/work/nab-agents-add-user-auth`

### ワークツリーのライフサイクル

1. **作成**: `/git worktree-create`
   - mainブランチから新しいブランチを作成
   - 指定パスにワークツリーを作成

2. **作業**: 通常のGit操作が可能
   - `/git commit` でコミット
   - `/mr create` でMR作成

3. **削除**: `/git worktree-delete`
   - ワークツリーディレクトリを削除
   - 必要に応じてブランチも削除

### ワークツリーの制限

1. **同じブランチを複数のワークツリーで使用不可**
2. **ディスク容量**: ワークツリーごとにファイルが複製される
3. **.gitディレクトリ**: メインリポジトリと共有される

## エラーハンドリング詳細

### ブランチ作成時のエラー

#### main以外のブランチから実行

```bash
# エラー
/git branch-create
# 現在: feature-branch

# 対応
git checkout main
/git branch-create
```

#### 未コミット変更がある

```bash
# エラー
/git branch-create
# 変更あり

# 対応方法1: コミット
/git commit

# 対応方法2: stash
git stash
/git branch-create
git stash pop
```

#### ブランチ名が既に存在

```bash
# エラー
/git branch-create
# ブランチ名「add-feature」選択 → 既に存在

# 対応方法1: 別の名前を使用
/git branch-create
# → "Other"で別の名前を入力

# 対応方法2: 既存ブランチを削除
git branch -d add-feature
/git branch-create
```

### コミット時のエラー

#### 変更がない

```bash
# エラー
/git commit
# 変更なし

# 対応
# ファイルを編集してから実行
```

#### プッシュ失敗（rejected）

```bash
# エラー
/git commit
# プッシュ失敗: リモートに新しいコミットがある

# 自動対応
# → rebaseして再プッシュ
```

#### プッシュ失敗（コンフリクト）

```bash
# エラー
/git commit
# rebase失敗: コンフリクト

# 対応
git status  # コンフリクトファイルを確認
# コンフリクトを手動で解決
git add {resolved_files}
git rebase --continue
git push
```

### ブランチ削除時のエラー

#### 未マージブランチの削除試行

```bash
# エラー
/git branch-delete unmerged-branch

# 対応方法1: マージしてから削除
git checkout main
git merge unmerged-branch
/git branch-delete unmerged-branch

# 対応方法2: 強制削除（注意）
git branch -D unmerged-branch
```

#### mainブランチの削除試行

```bash
# エラー
/git branch-delete main

# 対応
# mainブランチは削除できません
```

### ワークツリー削除時のエラー

#### 未コミット変更がある

```bash
# 警告
/git worktree-delete /path/to/worktree
# 未コミット変更あり

# 対応方法1: キャンセルしてコミット
cd /path/to/worktree
/git commit
/git worktree-delete /path/to/worktree

# 対応方法2: 変更を破棄して削除
# → AskUserQuestionで「はい、削除する」を選択
```

#### ワークツリーが見つからない

```bash
# エラー
/git worktree-delete /invalid/path

# 対応
git worktree list  # 一覧を確認
/git worktree-delete  # 引数なしで選択
```

## トラブルシューティング

### スキルが起動しない

1. **gitリポジトリか確認**:
   ```bash
   git status
   # Not a git repository → gitリポジトリではない
   ```

2. **サブコマンドの確認**:
   ```bash
   /git branch-create  # 正しい
   /git create         # 間違い（無効なサブコマンド）
   ```

### ブランチが作成できない

1. **カレントブランチを確認**:
   ```bash
   git branch --show-current
   # main以外 → mainに切り替える
   ```

2. **作業ツリーの状態を確認**:
   ```bash
   git status
   # 変更あり → コミットまたはstash
   ```

3. **リモートの状態を確認**:
   ```bash
   git fetch origin main
   git status
   # behind → pullが必要
   ```

### コミットができない

1. **変更があるか確認**:
   ```bash
   git status
   # nothing to commit → 変更なし
   ```

2. **機密ファイルが含まれている**:
   - 自動的に除外される
   - 意図的にコミットしたい場合は手動で実行

3. **プッシュが失敗する**:
   ```bash
   git pull --rebase origin {branch}
   # コンフリクトを解決
   git push
   ```

### ブランチが削除できない

1. **マージ済みか確認**:
   ```bash
   git branch --merged main
   # リストに含まれない → 未マージ
   ```

2. **mainブランチではないか確認**:
   ```bash
   # mainブランチは削除不可
   ```

3. **リモートブランチが削除できない**:
   ```bash
   # 権限を確認
   # リポジトリへの書き込み権限が必要
   ```

### ワークツリーが作成できない

1. **パスが既に存在する**:
   ```bash
   ls /home/user/work/nab-agents-add-feature
   # 既に存在 → 別の名前を使用
   ```

2. **ブランチ名が既に存在する**:
   ```bash
   git branch --list add-feature
   # 既に存在 → 別の名前を使用
   ```

3. **ディスク容量不足**:
   ```bash
   df -h
   # ディスク容量を確認
   ```

### ワークツリーが削除できない

1. **メインワークツリーではないか確認**:
   ```bash
   git worktree list
   # 最初の行はメインワークツリー（削除不可）
   ```

2. **削除に失敗する**:
   ```bash
   git worktree remove --force {path}
   # それでも失敗する場合
   rm -rf {path}
   git worktree prune
   ```

## ベストプラクティス

### ブランチ管理

1. **命名規則を統一**: チーム全体で統一したプレフィックスを使用
2. **定期的なクリーンアップ**: マージ済みブランチは定期的に削除
3. **mainから分岐**: 作業ブランチは常にmainから分岐
4. **小さなブランチ**: 1つのブランチで1つの目的を達成

### コミット管理

1. **目的単位でコミット**: 複数の目的を1つのコミットにしない
2. **頻繁にコミット**: 作業の節目ごとにコミット
3. **プッシュを忘れずに**: コミット後は忘れずにプッシュ
4. **機密情報の除外**: .envファイル等は.gitignoreに追加

### ワークツリー管理

1. **用途を明確に**: 緊急バグ修正、並行開発など、目的を明確に
2. **作業完了後は削除**: 不要なワークツリーは残さない
3. **ディスク容量を考慮**: 大規模プロジェクトでは容量に注意
4. **ブランチの整理**: ワークツリー削除時にブランチも整理

### チーム開発

1. **ブランチ戦略の共有**: チームで統一した運用ルールを決める
2. **コミットメッセージの品質**: 他のメンバーが理解できる内容に
3. **レビュー前のセルフチェック**: `/git commit`後、diffを確認
4. **定期的なmainへのマージ**: 長期間放置しない

### 安全性

1. **強制操作は慎重に**: `-D`, `--force`等は使用しない（スキルも使わない）
2. **バックアップの取得**: 重要な変更前はバックアップブランチを作成
3. **テストの実行**: コミット前に関連テストを実行
4. **段階的な変更**: 大きな変更は複数のコミットに分割

### パフォーマンス

1. **不要なファイルを除外**: .gitignoreを適切に設定
2. **大きなファイルを避ける**: バイナリファイルはGit LFSを使用
3. **ワークツリーの数を制限**: 同時に使用するワークツリーは3-4個まで
4. **定期的なgc**: `git gc`でリポジトリを最適化

## 高度な使用例

### フック活用

プロジェクトのニーズに応じて、gitフックを活用できます:

```bash
# .git/hooks/pre-commit
# コミット前にテストを実行
npm test || exit 1
```

### エイリアス設定

よく使うコマンドをエイリアスに設定:

```bash
# ~/.bashrc または ~/.zshrc
alias gbc='/git branch-create'
alias gc='/git commit'
alias gbd='/git branch-delete'
alias gwc='/git worktree-create'
alias gwd='/git worktree-delete'
```

### CI/CD連携

GitLab CI/CDと連携して、自動テスト・デプロイを実現:

```yaml
# .gitlab-ci.yml
test:
  script:
    - npm test

deploy:
  script:
    - npm run deploy
  only:
    - main
```
