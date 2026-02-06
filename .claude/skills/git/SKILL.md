---
name: git
description: Git操作を実行する。使い方：/git（対話選択）、/git commit（コミット）、/git branch-create（ブランチ作成）、/git branch-delete（ブランチ削除）、/git worktree-create（ワークツリー作成）、/git worktree-delete（ワークツリー削除）
argument-hint: [commit|branch-create|branch-delete|worktree-create|worktree-delete]
allowed-tools: Bash, Task, AskUserQuestion, Read
---

# Git操作スキル

このスキルは、Git操作を統合的に実行するオーケストレーターです。
各操作は専用のワークフローを別コンテキストで実行します。

## 実行手順

以下の手順に従って、このスキルを実行してください。

### ステップ1: 引数解析とモード決定

$ARGUMENTSを確認し、モードを決定します。

**$ARGUMENTSの形式**:
- 引数なし（空文字列）: `/git` のみが実行された
- 引数あり: `/git commit` や `/git branch-delete feature-branch` のように引数が渡される
  - 最初の単語がサブコマンド
  - 2番目以降の単語が追加パラメータ

**引数解析の手順**:

1. $ARGUMENTSが空または空白のみの場合、AskUserQuestionツールで操作を選択:

```
AskUserQuestion
  questions:
    - question: "どのGit操作を実行しますか？"
      header: "Git操作"
      multiSelect: false
      options:
        - label: "コミット＆プッシュ (commit)"
          description: "変更をコミットしてリモートにプッシュ"
        - label: "ブランチ作成 (branch-create)"
          description: "mainから作業ブランチを作成"
        - label: "ブランチ削除 (branch-delete)"
          description: "マージ済みブランチを削除"
        - label: "ワークツリー操作 (worktree)"
          description: "ワークツリーの作成または削除"
```

ユーザーの回答から、カッコ内の単語（commit、branch-create等）を抽出してモードとします。
「ワークツリー操作」が選択された場合、さらにAskUserQuestionでサブモードを選択:

```
AskUserQuestion
  questions:
    - question: "ワークツリー操作を選択してください"
      header: "操作種別"
      multiSelect: false
      options:
        - label: "作成 (worktree-create)"
          description: "新しいワークツリーを作成"
        - label: "削除 (worktree-delete)"
          description: "ワークツリーを削除"
```

2. $ARGUMENTSに文字列がある場合、スペースで分割して解析:
   - 最初の単語がサブコマンド（モード）
   - `commit` → mode="commit"
   - `branch-create` → mode="branch-create"
   - `branch-delete` → mode="branch-delete"
   - `worktree-create` → mode="worktree-create"
   - `worktree-delete` → mode="worktree-delete"
   - `worktree` → AskUserQuestionでサブモード選択（上記と同じ）
   - その他 → 無効なサブコマンドとしてAskUserQuestionでモード選択

   - 2番目以降の単語がある場合:
     - `branch-delete`の場合: target_branchとして保存
     - `worktree-delete`の場合: target_pathとして保存

### ステップ2: 現在のGit状態を確認

Bashツールで以下のコマンドを実行し、現在の状態を取得します:

```bash
git branch --show-current && pwd
```

**結果の解析**:
- 1行目: カレントブランチ名を保存 (例: "main" または "feature/new-feature")
- 2行目: カレントディレクトリパスを保存 (例: "/home/user/project")

これらの情報は変数として保持し、ステップ3-2でTaskツールのpromptに含めます。

**gitリポジトリチェック**:
もしgit branch --show-currentが失敗した場合（終了コード0でない）、カレントディレクトリはgitリポジトリではありません。以下のメッセージを表示して終了:

```
エラー: カレントディレクトリはgitリポジトリではありません。
gitリポジトリのディレクトリで実行してください。
```

### ステップ3: ワークフローの読み込みと実行

決定したモードに応じて、対応するワークフローファイルを読み込み、Taskツールで実行します。

#### 3-1. ワークフローファイルの読み込み

Readツールで対応するワークフローファイルを読み込みます:

- `commit` → `.claude/skills/git/workflows/commit.md`
- `branch-create` → `.claude/skills/git/workflows/branch-create.md`
- `branch-delete` → `.claude/skills/git/workflows/branch-delete.md`
- `worktree-create` → `.claude/skills/git/workflows/worktree-create.md`
- `worktree-delete` → `.claude/skills/git/workflows/worktree-delete.md`

#### 3-2. Taskツールでワークフロー実行

3-1で読み込んだワークフローの内容を、Taskツールのpromptパラメータに含めて実行します。

**重要**: promptには以下の構造で文字列を構築してください:
```
以下のワークフローに従って、{操作内容}してください。

{Readツールで読み込んだワークフローファイルの全内容（1行目から最後の行まで全て）}

## 追加の入力情報
- {ステップ2で取得した情報}
```

**各モードの実装**:

**commit モード**:
```
Task
  subagent_type: "general-purpose"
  description: "コミット実行"
  prompt: 文字列を以下のように構築:
    - 1行目: "以下のワークフローに従って、変更をコミットしてプッシュしてください。"
    - 2行目: 空行
    - 3行目以降: Readツールで取得した.claude/skills/git/workflows/commit.mdの全内容
    - 最後に追加: "## 追加の入力情報\n- カレントブランチ: {ステップ2で取得したブランチ名}"
```

**branch-create モード**:
```
Task
  subagent_type: "general-purpose"
  description: "ブランチ作成"
  prompt: 文字列を以下のように構築:
    - 1行目: "以下のワークフローに従って、作業ブランチを作成してください。"
    - 2行目: 空行
    - 3行目以降: Readツールで取得した.claude/skills/git/workflows/branch-create.mdの全内容
    - 最後に追加: "## 追加の入力情報\n- カレントブランチ: {ステップ2で取得したブランチ名}"
```

**branch-delete モード**:
```
Task
  subagent_type: "general-purpose"
  description: "ブランチ削除"
  prompt: 文字列を以下のように構築:
    - 1行目: "以下のワークフローに従って、ブランチを削除してください。"
    - 2行目: 空行
    - 3行目以降: Readツールで取得した.claude/skills/git/workflows/branch-delete.mdの全内容
    - 最後に追加: "## 追加の入力情報\n- カレントブランチ: {ステップ2で取得したブランチ名}\n- 削除対象ブランチ: {ステップ1で取得したtarget_branch（ある場合、なければ「指定なし」）}"
```

**worktree-create モード**:
```
Task
  subagent_type: "general-purpose"
  description: "ワークツリー作成"
  prompt: 文字列を以下のように構築:
    - 1行目: "以下のワークフローに従って、ワークツリーを作成してください。"
    - 2行目: 空行
    - 3行目以降: Readツールで取得した.claude/skills/git/workflows/worktree-create.mdの全内容
    - 最後に追加: "## 追加の入力情報\n- カレントディレクトリ: {ステップ2で取得したディレクトリ}"
```

**worktree-delete モード**:
```
Task
  subagent_type: "general-purpose"
  description: "ワークツリー削除"
  prompt: 文字列を以下のように構築:
    - 1行目: "以下のワークフローに従って、ワークツリーを削除してください。"
    - 2行目: 空行
    - 3行目以降: Readツールで取得した.claude/skills/git/workflows/worktree-delete.mdの全内容
    - 最後に追加: "## 追加の入力情報\n- 削除対象パス: {ステップ1で取得したtarget_path（ある場合、なければ「指定なし」）}"
```

### ステップ4: 結果の確認と報告

Taskツールが完了したら、その結果をユーザーに報告します。

**報告の方針**:
- ワークフロー内で詳細な結果（ブランチ名、ファイル数等）が既に表示されています
- オーケストレーター側では、Taskツールの結果を見て、成功したか失敗したかを簡潔に報告するだけで十分です

**成功時の報告例**:
- "コミット処理が完了しました。"
- "ブランチ作成が完了しました。"
- "ブランチ削除が完了しました。"
- "ワークツリー作成が完了しました。"
- "ワークツリー削除が完了しました。"

**失敗時の対応**:
- Taskツールからエラーメッセージが返された場合、そのエラーメッセージをユーザーに伝えます
- ワークフロー内に対処方法が記載されているため、追加の説明は不要です

## 重要な注意事項

### 1. ワークフローの全内容を必ず渡す

**最重要**: Readツールで読み込んだワークフローファイルの内容は、1文字も省略せず、要約もせず、そのまま全てTaskツールのpromptに含めてください。

- ✅ 正しい: ワークフローファイルの内容を全て（1行目から最後の行まで）promptに含める
- ❌ 間違い: ワークフローを要約したり、一部だけを含めたりする
- ❌ 間違い: 「workflows/commit.mdを参照してください」とだけ書く（Taskツールは別コンテキストなので参照できない）

### 2. 別コンテキストでの実行

Taskツールは完全に別のコンテキストで実行されます。そのため:
- このスキル（オーケストレーター）側では、ステップ2の状態確認以外のBashコマンドは実行不要
- ワークフロー内の全てのBashコマンドは、Taskツール側で実行される
- Taskツールは、promptに含まれる情報のみを使用する（このスキル側の変数や状態にアクセスできない）

### 3. 引数解析の柔軟性

ユーザーが引数を指定しなくても、AskUserQuestionで対話的にモードを選択できるようにします。これにより、コマンドに不慣れなユーザーでも使いやすくなります。

### 4. エラーハンドリングの分担

- **オーケストレーター側**: gitリポジトリチェックのみ
- **ワークフロー側**: 各操作固有のエラーハンドリング（各ワークフローファイルに記載済み）

## トラブルシューティング

### gitリポジトリではない
カレントディレクトリがgitリポジトリでない場合:
```
エラー: カレントディレクトリはgitリポジトリではありません。
gitリポジトリのディレクトリで実行してください。
```

### 無効なサブコマンド
$ARGUMENTSに無効なサブコマンドが指定された場合、AskUserQuestionでモードを選択します。

## 参考情報

詳細な使用例は `assets/examples.md`、技術リファレンスは `assets/reference.md` を参照してください。
