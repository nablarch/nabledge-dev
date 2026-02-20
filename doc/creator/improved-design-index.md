# nabledge-creator 設計書：index ワークフロー

この設計書はworkflows/index.mdとworkflows/verify-index.mdの内容を定義する。エージェントへの命令として記述する。

indexワークフローは2つのセッションに分かれる。

| セッション | ワークフロー | 目的 |
|---|---|---|
| 生成セッション | workflows/index.md | index.toonの生成（Step 1-3） |
| 検証セッション | workflows/verify-index.md | ヒントの妥当性検証（別セッション） |

別セッションにする理由：generate-index.pyが集約したヒントが各知識ファイルの内容を正しく代表しているか、未作成エントリのヒント推定が妥当かを、別のコンテキストで確認する。

関連するスクリプト：
- scripts/generate-index.py
- scripts/generate-index-checklist.py（検証セッション用）

---

# workflows/index.md

知識ファイル群からindex.toonを生成するワークフロー。

## なぜindex.toonが必要か

nabledge-6のkeyword-searchは、最初にindex.toonを読んで候補ファイルを絞り込む。index.toonがないと全JSONを走査する必要があり、コンテキストを大量に消費する。index.toonは約5-7Kトークンで93エントリの検索を可能にする。

未作成の知識ファイルもエントリに含めることで、keyword-searchがマッチしたとき「この情報は知識ファイルに含まれていません」と正確に回答できる。

## ワークフロー手順

### Step 1: 生成

以下のコマンドを実行せよ。

```bash
python scripts/generate-index.py v6
```

### Step 2: 確認

生成されたindex.toonを開き、以下を確認せよ：
- エントリ数が`knowledge-file-plan.md`の総数と一致するか
- 作成済みファイルのパスが正しいか（`not yet created`でないか）
- ヒントが空のエントリがないか

### Step 3: チェックリスト生成

以下のコマンドを実行せよ。

```bash
python scripts/generate-index-checklist.py .claude/skills/nabledge-6/knowledge/index.toon --knowledge-dir .claude/skills/nabledge-6/knowledge/ --output .claude/skills/nabledge-6/knowledge/index.checklist.md
```

生成セッションはここで完了。

---

# workflows/verify-index.md（検証セッション）

生成セッションとは**別のセッション**で実行する。

### 呼び出し

```
nabledge-creator verify-index-6
```

### Step VI1: チェックリストとindex.toonを読む

以下のファイルを読め。

```
.claude/skills/nabledge-6/knowledge/index.checklist.md   # チェックリスト
.claude/skills/nabledge-6/knowledge/index.toon            # 生成されたindex
```

### Step VI2: 作成済みエントリのヒントチェック

チェックリストの「作成済みエントリ」セクションの各行について以下を行え。

1. 該当するJSONファイルを読め（index配列のhintsを確認）
2. index.toonのヒントが、JSONの全セクションヒントから適切に集約されているか確認せよ
3. JSONのセクションヒントに含まれる重要なL1/L2キーワードがindex.toonのヒントに含まれているか確認せよ
4. 適切 → ✓ / 重要なキーワードが欠落 → ✗

### Step VI3: 未作成エントリのヒントチェック

チェックリストの「未作成エントリ」セクションの各行について以下を行え。

1. knowledge-file-plan.mdの該当エントリを読め
2. 推定されたヒントがtitleとtagsから妥当に導出されているか確認せよ
3. 妥当 → ✓ / 不十分 → ✗（追加すべきヒントを記録）

### Step VI4: 検索シミュレーション

チェックリストの「想定質問」について、index.toonのヒントとの照合をシミュレーションせよ。正しいファイルが選定されるか確認する。

### Step VI5: 修正の適用

✗が1つでもあれば修正を行い、generate-index.pyを再実行せよ。

## 入出力

**入力**：
```
.claude/skills/nabledge-6/knowledge/**/*.json       # 既存知識ファイル
references/knowledge-file-plan.md                    # 全知識ファイル計画
```

**出力**：
```
.claude/skills/nabledge-6/knowledge/index.toon
```

## 出力例

```toon
# Nabledge-6 Knowledge Index

files[93,]{title,hints,path}:
  Nablarchバッチ（都度起動型・常駐型）, バッチ 都度起動 常駐 大量データ処理 アーキテクチャ ハンドラ DataReader, features/processing/nablarch-batch.json
  ユニバーサルDAO, データベース DAO O/Rマッパー CRUD JPA 検索 ページング 排他制御, features/libraries/universal-dao.json
  データリードハンドラ, ハンドラ バッチ データ読み込み ファイル データベース, features/handlers/batch/data-read-handler.json
  JSR352準拠バッチ（Jakarta Batch）, バッチ JSR352 Jakarta Batch Batchlet Chunk 標準仕様, not yet created
```

TOON形式。ヒントはスペース区切り。エントリはtitle順ソート。

---

# scripts/generate-index.py 仕様

## コマンドライン

```
python scripts/generate-index.py v6 [--knowledge-dir DIR] [--plan PATH] [--output PATH]
```

- `--knowledge-dir`：デフォルト `.claude/skills/nabledge-6/knowledge/`
- `--plan`：デフォルト `references/knowledge-file-plan.md`
- `--output`：デフォルト `{knowledge-dir}/index.toon`

## 処理パイプライン

```
scan_knowledge() → load_plan() → merge() → output_toon()
```

### scan_knowledge()

`knowledge/**/*.json`を走査（index.toonは除外）。各ファイルから：
- `title`を取得
- `index[].hints`を全セクションから集約してファイルレベルヒントを生成
- 相対パスを記録

ファイルレベルヒントの集約方法：全セクションのhintsからL1+L2相当のキーワードを抽出し、重複を排除する。

### load_plan()

knowledge-file-plan.mdの各エントリからtitle、tagsを取得。

### merge()

planの各エントリについて：
- scan_knowledge()に該当JSONがある → JSONから取得したtitle, hints, pathを使用
- 該当JSONがない → planのtitleを使用、tagsからヒントを推定、path=`not yet created`

未作成エントリのヒント推定：titleから主要な名詞を抽出し、tagsからL1相当のキーワード（batch→バッチ、rest→REST等）を追加する。

### output_toon()

title順ソート。TOON形式で出力。

```
# Nabledge-{N} Knowledge Index

files[{count},]{title,hints,path}:
  {title}, {hints}, {path}
```

## 終了コード

- 0：正常
- 1：警告（ヒント推定が不十分なエントリあり）
- 2：エラー

---

# scripts/generate-index-checklist.py 仕様

index.toonとJSONから検証セッション用のチェックリストを生成する。

## コマンドライン

```
python scripts/generate-index-checklist.py INDEX_PATH --knowledge-dir DIR [--output PATH]
```

## 処理の流れ

1. index.toonをパースして全エントリを取得
2. 作成済みエントリ：対応するJSONのindex[].hintsを全取得し、index.toonのhintsと照合
3. 未作成エントリ：knowledge-file-plan.mdのtitle/tagsと照合
4. 想定質問を自動生成（各エントリのtitleから）

## 出力例

```markdown
# チェックリスト: index.toon

**エントリ数**: 93（作成済み: 17, 未作成: 76）

---

## 作成済みエントリ

| # | title | index.toonヒント | JSONヒント総数 | 自動照合 | 判定 |
|---|---|---|---|---|---|
| 1 | ユニバーサルDAO | データベース DAO O/Rマッパー CRUD ... | 42 | 8/42含む | |
| 2 | データリードハンドラ | ハンドラ バッチ データ読み込み ... | 15 | 5/15含む | |

「自動照合」はJSONの全セクションヒントのうちindex.toonに含まれる数。比率が低い場合は重要なヒントが欠落している可能性あり。

---

## 未作成エントリ

| # | title | 推定ヒント | tags | 判定 |
|---|---|---|---|---|
| 1 | JSR352準拠バッチ | バッチ JSR352 Jakarta Batch | batch | |
| 2 | メール送信アダプタ | アダプタ メール送信 | adapters | |

推定ヒントがtitleとtagsの内容を適切に反映しているか確認せよ。

---

## 想定質問

1. 「バッチ処理のアーキテクチャを知りたい」
2. 「UniversalDaoの使い方を知りたい」
3. 「メール送信機能の設定方法は？」

各質問でindex.toonのヒントとの照合をシミュレーションし、正しいエントリが選定されるか確認せよ。
```

## 終了コード

- 0：正常
- 1：エラー
