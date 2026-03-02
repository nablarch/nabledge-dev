# nabledgeスキル 実装作業指示書

この文書は、nabledge-devリポジトリに対して行う全作業を定義する。この文書だけを見て作業を完了できることをゴールとする。

対象リポジトリ: `https://github.com/nablarch/nabledge-dev`

---

## 目次

1. [作業概要](#1-作業概要)
2. [完成状態の定義](#2-完成状態の定義)
3. [知識ファイル・データ構造の仕様](#3-知識ファイルデータ構造の仕様)
4. [nabledge-6の作業](#4-nabledge-6の作業)
5. [nabledge-5の作業](#5-nabledge-5の作業)
6. [SKILL.mdの内容](#6-skillmdの内容)
7. [ワークフローMDの内容](#7-ワークフローmdの内容)
8. [ヘルパースクリプトの内容](#8-ヘルパースクリプトの内容)
9. [code-analysis.mdの修正](#9-code-analysismdの修正)
10. [コマンドの作業](#10-コマンドの作業)
11. [GitHub Actions・CI/CDの作業](#11-github-actionscicdの作業)
12. [ドキュメントの作業](#12-ドキュメントの作業)
13. [テストシナリオの作業](#13-テストシナリオの作業)
14. [全体フロー図](#14-全体フロー図)
15. [完了チェックリスト](#15-完了チェックリスト)

---

## 1. 作業概要

nabledge-devリポジトリ内のnabledge-6スキルの検索系ワークフローを新設計に置き換え、nabledge-5スキルを新規追加する。

### やること

- nabledge-6の検索系ワークフロー・スクリプト・知識ファイルを削除し、新しいワークフロー・スクリプトを作成する
- nabledge-6のcode-analysis.mdは保持し、知識検索の呼び出し箇所のみ修正する
- nabledge-5を新規追加する（nabledge-6と同じワークフロー構成、知識ファイルは0件）
- GitHub Actions、セットアップスクリプト、ドキュメント、テストシナリオを更新する

### やらないこと

- 知識ファイル（JSON）の作成。別ツール（nabledge-creator）で生成する
- `.claude/skills/dy/`, `git/`, `pr/`, `skill-creator/` の変更
- `doc/mapping/` の変更

---

## 2. 完成状態の定義

### nabledge-6 の完成ディレクトリ構造

```
.claude/skills/nabledge-6/
  SKILL.md                                    # 新規作成
  workflows/
    qa.md                                     # 新規作成
    _knowledge-search.md                      # 新規作成
    _knowledge-search/
      full-text-search.md                     # 新規作成
      index-based-search.md                   # 新規作成
      file-search.md                          # 新規作成
      section-search.md                       # 新規作成
      section-judgement.md                     # 新規作成
    code-analysis.md                          # 既存を修正（§9）
  scripts/
    full-text-search.sh                       # 新規作成
    read-sections.sh                          # 新規作成
    generate-mermaid-skeleton.sh              # 既存のまま残す
    prefill-template.sh                       # 既存のまま残す
  assets/
    code-analysis-template.md                 # 既存のまま残す
    code-analysis-template-guide.md           # 既存のまま残す
    code-analysis-template-examples.md        # 既存のまま残す
  knowledge/
    index.toon                                # ヘッダーのみの状態にリセット
    （JSONファイルは0件。nabledge-creatorで後日生成）
  docs/
    README.md                                 # 既存のまま残す
    （その他のMDは削除。nabledge-creatorで後日生成）
  plugin/
    plugin.json                               # バージョン更新
    CHANGELOG.md                              # 変更追記
    README.md                                 # 内容更新
    GUIDE-CC.md                               # 既存のまま残す
    GUIDE-GHC.md                              # 既存のまま残す
```

### nabledge-5 の完成ディレクトリ構造

```
.claude/skills/nabledge-5/
  SKILL.md
  workflows/
    qa.md
    _knowledge-search.md
    _knowledge-search/
      full-text-search.md
      index-based-search.md
      file-search.md
      section-search.md
      section-judgement.md
    code-analysis.md
  scripts/
    full-text-search.sh
    read-sections.sh
    generate-mermaid-skeleton.sh
    prefill-template.sh
  assets/
    code-analysis-template.md
    code-analysis-template-guide.md
    code-analysis-template-examples.md
  knowledge/
    index.toon                                # ヘッダーのみ
  docs/
    README.md
  plugin/
    plugin.json
    CHANGELOG.md
    README.md
    GUIDE-CC.md
    GUIDE-GHC.md
```

### nabledge-6 で削除するファイル

```
workflows/keyword-search.md
workflows/knowledge-search.md
workflows/section-judgement.md
scripts/extract-section-hints.sh
scripts/parse-index.sh
scripts/sort-sections.sh
knowledge/checks/security.json
knowledge/features/adapters/slf4j-adapter.json
knowledge/features/handlers/batch/data-read-handler.json
knowledge/features/handlers/common/db-connection-management-handler.json
knowledge/features/handlers/common/transaction-management-handler.json
knowledge/features/libraries/business-date.json
knowledge/features/libraries/data-bind.json
knowledge/features/libraries/database-access.json
knowledge/features/libraries/file-path-management.json
knowledge/features/libraries/universal-dao.json
knowledge/features/processing/nablarch-batch.json
knowledge/features/tools/ntf-assertion.json
knowledge/features/tools/ntf-batch-request-test.json
knowledge/features/tools/ntf-overview.json
knowledge/features/tools/ntf-test-data.json
knowledge/overview.json
knowledge/releases/6u3.json
docs/ 配下のMD（README.md以外すべて）
```

削除後、空になったディレクトリも削除する。

---

## 3. 知識ファイル・データ構造の仕様

ワークフローMDとスクリプトが前提とするデータ構造を定義する。今回の作業では知識ファイルは作成しないが、ワークフローはこの構造を前提に動作する。

### 3.1 知識ファイル（JSON）スキーマ

```json
{
  "id": "db-connection-management-handler",
  "title": "データベース接続管理ハンドラ",
  "official_doc_urls": ["https://nablarch.github.io/docs/LATEST/doc/..."],
  "index": [
    {
      "id": "overview",
      "title": "概要",
      "hints": ["DbConnectionManagementHandler", "データベース接続管理", "DB接続"]
    }
  ],
  "sections": {
    "overview": "後続のハンドラ及びライブラリで使用するためのデータベース接続を..."
  }
}
```

- `sections` の値は **Markdown文字列（string型）**
- `index[].hints` はセクションレベルの検索ヒント
- `index[].id` と `sections` のキーは1:1対応

### 3.2 インデックス（index.toon）フォーマット

```toon
# Nabledge-6 Knowledge Index

files[93,]{title,type,category,processing_patterns,path}:
  データベース接続管理ハンドラ, component, handlers, , features/handlers/common/db-connection-management-handler.json
  Nablarchバッチ（都度起動型・常駐型）, processing-pattern, nablarch-batch, nablarch-batch, features/processing/nablarch-batch.json
  ユニバーサルDAO, component, libraries, nablarch-batch restful-web-service, features/libraries/universal-dao.json
```

フィールド:

| フィールド | 説明 |
|---|---|
| title | ドキュメントタイトル |
| type | ファイルパス分類のType |
| category | ファイルパス分類のCategory ID |
| processing_patterns | 処理パターン分類（スペース区切り、該当なしは空） |
| path | knowledgeディレクトリからの相対パス。未作成は `not yet created` |

### 3.3 ファイルパス分類

| Type | Category ID |
|------|-------------|
| processing-pattern | nablarch-batch, jakarta-batch, restful-web-service, http-messaging, web-application, mom-messaging, db-messaging |
| component | handlers, libraries, adapters |
| development-tools | testing-framework, toolbox, java-static-analysis |
| setup | blank-project, configuration, setting-guide, cloud-native |
| guide | nablarch-patterns, business-samples |
| check | security-check |
| about | about-nablarch, migration, release-notes |

### 3.4 処理パターン分類

有効値: nablarch-batch, jakarta-batch, restful-web-service, http-messaging, web-application, mom-messaging, db-messaging

---

## 4. nabledge-6の作業

以下の順番で作業する。

### Step 1: 削除

§2「完成状態の定義」の「nabledge-6 で削除するファイル」リストのファイルを削除する。空になったディレクトリも削除する。

```bash
cd .claude/skills/nabledge-6

# 旧ワークフロー・スクリプト
rm workflows/keyword-search.md
rm workflows/knowledge-search.md
rm workflows/section-judgement.md
rm scripts/extract-section-hints.sh
rm scripts/parse-index.sh
rm scripts/sort-sections.sh

# 知識ファイル（全JSON）
find knowledge -name "*.json" -delete

# 空ディレクトリ
find knowledge -mindepth 1 -type d -empty -delete

# 閲覧用Markdown（README.md以外）
find docs -name "*.md" ! -name "README.md" -delete
find docs -mindepth 1 -type d -empty -delete
```

完了条件:
- `ls workflows/` に `code-analysis.md` のみ存在
- `ls scripts/` に `generate-mermaid-skeleton.sh`, `prefill-template.sh` のみ存在
- `find knowledge -name "*.json" | wc -l` が 0

### Step 2: index.toon をリセット

```bash
cat > knowledge/index.toon << 'EOF'
# Nabledge-6 Knowledge Index

files[0,]{title,type,category,processing_patterns,path}:
EOF
```

### Step 3: 新ファイルの作成

以下のファイルを作成する。各ファイルの内容は後続のセクションで定義する。

| ファイル | 内容の定義 |
|---|---|
| `SKILL.md` | §6 |
| `workflows/qa.md` | §7.1 |
| `workflows/_knowledge-search.md` | §7.2 |
| `workflows/_knowledge-search/full-text-search.md` | §7.3 |
| `workflows/_knowledge-search/index-based-search.md` | §7.4 |
| `workflows/_knowledge-search/file-search.md` | §7.5 |
| `workflows/_knowledge-search/section-search.md` | §7.6 |
| `workflows/_knowledge-search/section-judgement.md` | §7.7 |
| `scripts/full-text-search.sh` | §8.1 |
| `scripts/read-sections.sh` | §8.2 |

スクリプトには実行権限を付与する:

```bash
chmod +x scripts/full-text-search.sh scripts/read-sections.sh
```

### Step 4: code-analysis.md を修正

§9の内容に従って修正する。

### Step 5: plugin/ 以下の更新

`plugin/plugin.json` のバージョンを更新し、`plugin/CHANGELOG.md` に変更内容を追記する（§12.4参照）。

---

## 5. nabledge-5の作業

nabledge-6のStep 3完了後に実施する。

### Step 1: ワークフロー・スクリプト・アセットをコピー

nabledge-6からコピーする。SKILL.md以外のワークフロー・スクリプト・アセットはバージョン番号をハードコードしていないため、そのまま使える（§8のパス解決方式による）。

```bash
SRC=".claude/skills/nabledge-6"
DST=".claude/skills/nabledge-5"

mkdir -p "$DST"

# ワークフロー（全コピー）
cp -r "$SRC/workflows" "$DST/"

# スクリプト（全コピー）
cp -r "$SRC/scripts" "$DST/"

# アセット（全コピー）
cp -r "$SRC/assets" "$DST/"
```

### Step 2: SKILL.md を作成

§6のnabledge-6用の内容で、以下を置換して作成する:
- `nabledge-6` → `nabledge-5`
- `Nablarch 6` → `Nablarch 5`

### Step 3: 知識ファイル初期構造を作成

```bash
mkdir -p "$DST/knowledge"
cat > "$DST/knowledge/index.toon" << 'EOF'
# Nabledge-5 Knowledge Index

files[0,]{title,type,category,processing_patterns,path}:
EOF
```

### Step 4: docs を作成

```bash
mkdir -p "$DST/docs"
cat > "$DST/docs/README.md" << 'EOF'
# Nabledge-5 Knowledge Docs

Human-readable version of knowledge files for Nablarch 5.
EOF
```

### Step 5: plugin/ を作成

```bash
mkdir -p "$DST/plugin"
```

`plugin/plugin.json`:
```json
{
  "name": "nabledge-5",
  "version": "0.1",
  "description": "Nablarch 5 skill for AI-assisted development",
  "author": { "name": "Nablarch" },
  "license": "Apache-2.0",
  "repository": "https://github.com/nablarch/nabledge",
  "keywords": ["nablarch"]
}
```

`plugin/CHANGELOG.md`, `plugin/README.md`, `plugin/GUIDE-CC.md`, `plugin/GUIDE-GHC.md` はnabledge-6のものをベースに、バージョン番号とNablarchバージョンの表記を5に置換して作成する。CHANGELOG.mdは `[0.1]` のみのクリーンな状態で作成する。

### Step 6: 検証

```bash
# nabledge-5 内に nabledge-6 へのハードコード参照がないことを確認
grep -r "nabledge-6" .claude/skills/nabledge-5/ --include="*.md" --include="*.sh"
# → ヒットしないこと
```

---

## 6. SKILL.mdの内容

nabledge-6用の内容を以下に示す。nabledge-5用は `6` → `5` を置換する。

```markdown
---
name: nabledge-6
description: Nablarch 6フレームワークの構造化知識ベース。バッチ処理、RESTful Webサービス、ハンドラ、ライブラリ等のNablarch機能について質問に回答する。コード分析も可能。
---

# Nabledge-6: Nablarch 6 Knowledge Base

## トリガー条件

以下のいずれかに該当する場合にこのスキルが呼び出される:

- Nablarch 6に関する質問
- Nablarchの機能、API、設定、パターンについての質問
- Nablarchを使ったバッチ処理、RESTful Webサービスの実装に関する質問
- Nablarchのハンドラ、ライブラリ、テストフレームワークに関する質問
- Nablarchを使った既存コードの分析

## ワークフロー振り分け

入力を解析し、以下のワークフローに振り分ける:

- 「質問」「知りたい」「教えて」「使い方」等 → workflows/qa.md
- 「コード分析」「構造を理解」等 → workflows/code-analysis.md
- 判定できない場合 → workflows/qa.md（デフォルト）

## 知識制約

**重要**: 回答は知識ファイル（knowledge/**/*.json）の情報のみに基づく。

- LLMの学習データ、外部Webサイト、一般知識の使用は禁止
- 知識ファイルにない情報は「この情報は知識ファイルに含まれていません」と明示する

## 知識ファイルのパス

- 知識ファイル: knowledge/{type}/{category-id}/*.json
- インデックス: knowledge/index.toon
- 閲覧用Markdown: docs/

## ワークフロー一覧

| ワークフロー | 役割 |
|---|---|
| workflows/qa.md | 質問応答 |
| workflows/code-analysis.md | コード分析・ドキュメント生成 |
| workflows/_knowledge-search.md | 知識検索（内部。qa.md, code-analysis.mdから呼び出される） |

## エラーハンドリング

- 知識が見つからない場合: 「この情報は知識ファイルに含まれていません」+ index.toonから関連エントリを提示
- LLM学習データでの補完は行わない
```

---

## 7. ワークフローMDの内容

### ワークフローMDの記述ルール

ワークフローMDはエージェントへの「指示書」である。以下のパターンで記述する:

```markdown
# [ワークフロー名]

[1行で何をするか]

## 入力
[具体的な入力データの形式]

## 出力
[具体的な出力データの形式]

## 手順

### Step N: [ステップ名]

**ツール**: [使うツール名、またはメモリ内]

**やること**: [命令形で具体的に記述]

**コマンド**:
[そのまま実行できるコマンド]

**判断基準**: [エージェントが判断する場合の基準]

**出力**: [このステップの出力]
```

以下の仕様を、このパターンに変換して各MDファイルを作成する。変換時のルール:
- 仕様の「処理」「ルール」を命令形（「〜せよ」「〜を実行する」）に書き換える
- 仕様のコマンド例はそのまま転記する
- 仕様の判断基準（判定表、閾値）はそのまま転記する
- 仕様にない情報を追加しない

### 7.1 workflows/qa.md

| 項目 | 内容 |
|---|---|
| 入力 | ユーザーの質問（日本語の自然文） |
| 出力 | 日本語の回答 |
| 使用ツール | Bash（jq）、Read |
| 想定ツールコール数 | 5〜12回 |

#### 処理フロー

```
Step 1: _knowledge-search.md を呼び出す
  IN:  ユーザーの質問
  OUT: ポインタJSON

Step 2: セクション内容を読み出す
  IN:  ポインタJSON
  OUT: セクション内容テキスト

Step 3: 回答を生成する
  IN:  ユーザーの質問 + セクション内容テキスト
  OUT: 日本語の回答
```

#### Step 1: 知識検索の呼び出し

`workflows/_knowledge-search.md` を呼び出す。入力はユーザーの質問そのまま。出力はポインタJSON。

ポインタJSONが空（`results: []`）の場合 → Step 3の「該当なしの応答」へ。

#### Step 2: セクション内容の読み出し

ポインタJSONの `results` を上から順に、セクション内容を取り出す:

```bash
# scripts/read-sections.sh を使用
bash scripts/read-sections.sh \
  "features/handlers/common/db-connection-management-handler.json:setup" \
  "features/libraries/universal-dao.json:paging"
```

出力形式:
```
=== features/handlers/common/db-connection-management-handler.json : setup ===
[セクション内容]
=== END ===
=== features/libraries/universal-dao.json : paging ===
[セクション内容]
=== END ===
```

読み出す順序: relevanceがhighのものから先。読み出す最大件数: **10件**。

#### Step 3: 回答の生成

**回答フォーマット**:

```
**結論**: [質問への直接的な回答]

**根拠**: [知識ファイルから得たコード例・設定例・仕様情報]

**注意点**: [制約、制限事項、よくある落とし穴]

参照: [知識ファイルID#セクションID]
```

**回答ルール**:
- 知識ファイルの情報**のみ**に基づいて回答する
- 知識ファイルに書いてない情報を推測で補完しない
- 参照元を明示する（例: `universal-dao.json#paging`）
- 目安の長さ: 500トークン以内（複雑な質問は800トークンまで許容）

**該当なしの応答**（ポインタJSONが空の場合）:

```
この情報は知識ファイルに含まれていません。

関連する知識ファイル:
- [index.toonから関連しそうなエントリのtitleとpathを列挙]
- [pathが "not yet created" のものはその旨を表示]
```

LLM学習データでの代替回答は**行わない**。

### 7.2 workflows/_knowledge-search.md

| 項目 | 内容 |
|---|---|
| 入力 | 検索クエリ（ユーザーの質問 or ワークフローからの検索要求） |
| 出力 | ポインタJSON |
| 役割 | 検索パイプライン全体の制御 |
| 想定ツールコール数 | 3〜8回 |

#### ポインタJSON スキーマ

```json
{
  "results": [
    {
      "file": "features/handlers/common/db-connection-management-handler.json",
      "section_id": "setup",
      "relevance": "high"
    },
    {
      "file": "features/libraries/universal-dao.json",
      "section_id": "configuration",
      "relevance": "partial"
    }
  ]
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| file | string | knowledgeディレクトリからの相対パス |
| section_id | string | セクション識別子 |
| relevance | "high" \| "partial" | high: 直接回答できる / partial: 部分的に関連 |

resultsはrelevance降順（high → partial）でソート。空配列は該当なし。

#### 処理フロー

```
Step 1: キーワード抽出
  IN:  検索クエリ
  OUT: キーワードリスト
  方法: エージェント判断（ツールコール不要）

Step 2: 全文検索（経路1）
  IN:  キーワードリスト
  OUT: ヒットしたセクションのリスト
  方法: _knowledge-search/full-text-search.md

Step 3: 分岐判定
  ヒットあり → Step 6へ
  ヒットなし（ゼロ件）→ Step 4へ
  方法: エージェント判断（ツールコール不要）

Step 4: ファイル選定（経路2）
  IN:  検索クエリ + index.toon
  OUT: 候補ファイルのリスト
  方法: _knowledge-search/file-search.md

Step 5: セクション選定（経路2）
  IN:  候補ファイルのリスト + キーワードリスト
  OUT: 候補セクションのリスト
  方法: _knowledge-search/section-search.md

Step 6: セクション判定（共通）
  IN:  候補セクションのリスト
  OUT: 関連セクション（High/Partial）
  方法: _knowledge-search/section-judgement.md

Step 7: ポインタJSON返却
  IN:  関連セクション
  OUT: ポインタJSON
  方法: エージェントがJSON組み立て（ツールコール不要）
```

#### Step 1: キーワード抽出

エージェントがメモリ内で実行（ツールコール不要）。

抽出観点:
- 日本語の機能名・概念名（例: ページング、トランザクション、バッチ処理）
- 英語の技術用語（例: UniversalDao、DbConnectionManagementHandler）
- クラス名、アノテーション名、プロパティ名
- 略語・別名（例: DAO、DB、NTF）

```
例: "ページングを実装したい"
→ ["ページング", "paging", "UniversalDao", "DAO", "per", "page"]
```

ルール:
- 日本語と英語の両方を含める
- 質問の意図から連想される技術用語も含める
- 3〜10個を目安

#### Step 3: 分岐判定

| ヒット件数 | 判定 | 次のステップ |
|---|---|---|
| 1件以上 | ヒットあり | Step 6（セクション判定） |
| 0件 | ヒットなし | Step 4（ファイル選定 → インデックス検索） |

#### Step 7: ポインタJSON返却

組み立てルール:
- relevance降順でソート（high → partial）
- 同一relevance内はファイルパスでソート（安定順序）
- 件数上限: なし（Step 6で絞り込み済み）

### 7.3 workflows/_knowledge-search/full-text-search.md

| 項目 | 内容 |
|---|---|
| 入力 | キーワードリスト |
| 出力 | ヒットしたセクションのリスト（file, section_id） |
| 使用ツール | Bash（`scripts/full-text-search.sh`） |
| 想定ツールコール数 | **1回** |

#### 処理

```bash
bash scripts/full-text-search.sh "ページング" "paging" "UniversalDao"
```

#### 検索ルール

| ルール | 設定 |
|---|---|
| 結合方式 | OR（いずれかのキーワードを含むセクションがヒット） |
| 大文字小文字 | 区別しない |
| マッチ方式 | 部分一致 |
| 検索対象 | 全知識ファイルの全セクション |
| ヒット上限 | なし（section-judgementで絞り込む） |

#### 出力形式

```
features/libraries/universal-dao.json|paging
features/libraries/universal-dao.json|overview
```

各行: `ファイル相対パス|セクションID`

#### エラーハンドリング

| 状態 | 対応 |
|---|---|
| ヒット0件 | 空の結果を返す（呼び出し元が経路2にフォールバック） |
| jqエラー | stderrにログ出力、該当ファイルをスキップして継続 |
| 知識ファイルが0件 | 空の結果を返す |

### 7.4 workflows/_knowledge-search/index-based-search.md

全文検索でヒットしなかった場合のフォールバック経路。file-search.md → section-search.md の順で呼び出す。

| 項目 | 内容 |
|---|---|
| 入力 | 検索クエリ + キーワードリスト |
| 出力 | 候補セクションのリスト |
| 想定ツールコール数 | 2〜4回 |

#### 手順

1. `_knowledge-search/file-search.md` を実行する
   - 検索クエリとindex.toonを渡す
   - 候補ファイルのリストを受け取る
2. 候補ファイルが0件の場合 → 空のリストを返して終了
3. `_knowledge-search/section-search.md` を実行する
   - 候補ファイルのリストとキーワードリストを渡す
   - 候補セクションのリストを受け取る
4. 候補セクションのリストを返す

### 7.5 workflows/_knowledge-search/file-search.md

| 項目 | 内容 |
|---|---|
| 入力 | 検索クエリ + index.toon |
| 出力 | 候補ファイルのリスト（パス、最大10件） |
| 使用ツール | Read（index.toon読み込み） |
| 想定ツールコール数 | **1回** |

#### 処理

エージェントがindex.toonを読み、検索クエリに基づいて候補ファイルを選定する。

**判断基準（3軸で評価、いずれかにマッチすれば候補とする）:**

**軸1: titleとの意味的マッチング**

検索クエリの意図とtitleが意味的に関連するかを判断する。
- 例: 「ページングを実装したい」→ 「ユニバーサルDAO」はページング機能を持つので候補
- 例: 「バッチの起動方法」→ 「Nablarchバッチ（都度起動型・常駐型）」が候補

**軸2: Type/Categoryによる絞り込み**

検索クエリの意図からType/Categoryを推定し、該当するファイルを候補とする。

| 意図パターン | 推定Type/Category |
|---|---|
| 「〜を実装したい」「〜の使い方」 | component/libraries |
| 「〜ハンドラの設定」「〜の制御」 | component/handlers |
| 「バッチの構成」「RESTの設計」 | processing-pattern |
| 「テストの方法」 | development-tools/testing-framework |
| 「プロジェクトの作り方」 | setup/blank-project |
| 「セキュリティチェック」 | check/security-check |

**軸3: processing_patternsによる絞り込み**

検索クエリに処理パターンの文脈が含まれる場合、該当するprocessing_patternsを持つファイルを候補とする。
- 例: 「バッチでのDB接続」→ `nablarch-batch` を含むファイル
- 例: 「RESTのバリデーション」→ `restful-web-service` を含むファイル

#### 選定ルール

- 最大ファイル数: **10件**
- `not yet created` のファイルは**除外**
- 3軸の合計で関連度が高い順に選定
- 明らかに無関係なファイルは含めない

#### 出力形式

```
features/libraries/universal-dao.json
features/libraries/database-access.json
features/handlers/common/db-connection-management-handler.json
```

#### エラーハンドリング

| 状態 | 対応 |
|---|---|
| index.toonが存在しない | エラーメッセージを返す |
| 候補が0件 | 空リストを返す |
| 全候補が `not yet created` | 空リストを返し、該当エントリのtitleを付記 |

### 7.6 workflows/_knowledge-search/section-search.md

| 項目 | 内容 |
|---|---|
| 入力 | 候補ファイルのリスト + キーワードリスト |
| 出力 | 候補セクションのリスト（file, section_id） |
| 使用ツール | Bash（jq） |
| 想定ツールコール数 | **1回** |

#### 処理

候補ファイルの `index[].hints` とキーワードをマッチングする。

**一括抽出コマンド**:

```bash
KNOWLEDGE_DIR="$(cd "$(dirname "$0")/.." && pwd)/knowledge"  # スクリプトから呼ぶ場合

for file in features/libraries/universal-dao.json \
            features/libraries/database-access.json; do
  jq -r --arg f "$file" \
    '.index[] | "\($f)|\(.id)|\(.hints | join(","))"' \
    "$KNOWLEDGE_DIR/$file" 2>/dev/null
done
```

出力例:
```
features/libraries/universal-dao.json|overview|UniversalDao,DAO,O/Rマッパー,CRUD
features/libraries/universal-dao.json|paging|ページング,paging,per,page,Pagination
```

**マッチングロジック**:

各セクションのhintsに対して、キーワードリストの各キーワードを部分一致で照合する。
- 部分一致（hintsの要素にキーワードが含まれる、またはキーワードにhints要素が含まれる）
- 大文字小文字区別なし
- マッチしたキーワード1つにつき +1点
- スコアが **1点以上** のセクションを候補とする

#### 選定ルール

- 最大セクション数: **20件**
- スコア降順で選定

#### 出力形式

```
features/libraries/universal-dao.json|paging
features/libraries/universal-dao.json|overview
```

全文検索の出力形式と同一。

#### エラーハンドリング

| 状態 | 対応 |
|---|---|
| 候補ファイルが0件 | 空リストを返す |
| hintsが空のセクション | スキップ |
| JSON読み込みエラー | 該当ファイルをスキップ |

### 7.7 workflows/_knowledge-search/section-judgement.md

| 項目 | 内容 |
|---|---|
| 入力 | 候補セクションのリスト（file, section_id） |
| 出力 | 関連セクションのリスト（file, section_id, relevance） |
| 使用ツール | Bash（`scripts/read-sections.sh`） |
| 想定ツールコール数 | 1〜3回 |

全文検索（経路1）とインデックス検索（経路2）の両方から呼び出される共通ワークフロー。

#### 処理フロー

```
Step A: 候補セクションの内容を一括読み出し
  IN:  候補セクションのリスト
  OUT: 各セクションの本文テキスト
  方法: scripts/read-sections.sh

Step B: 各セクションの関連度を判定
  IN:  検索クエリ + セクション本文テキスト
  OUT: 判定結果（High/Partial/None）
  方法: エージェント判断（メモリ内）

Step C: フィルタ・ソート
  IN:  判定結果
  OUT: High/Partialのみ、relevance降順
```

#### Step A: セクション内容の一括読み出し

```bash
bash scripts/read-sections.sh \
  "features/libraries/universal-dao.json:paging" \
  "features/libraries/universal-dao.json:overview" \
  "features/libraries/database-access.json:query"
```

1回のツールコールで全セクションの内容を取得する。候補が多い場合は2〜3回に分割（1回あたり最大10セクション程度）。

#### Step B: 関連度判定

エージェントがセクション内容を読んで判定（メモリ内、ツールコール不要）。

| 判定 | 条件 | 具体例 |
|---|---|---|
| **High** | 検索クエリに**直接回答できる情報**を含む。メソッド名、設定例、コード例、手順など実行可能な具体的情報がある | 「ページングの実装方法」に対して `per()`, `page()` メソッドの使い方とコード例があるセクション |
| **Partial** | **前提知識、関連機能、コンテキスト情報**を含む。直接の回答ではないが理解に必要 | 「ページングの実装方法」に対してUniversalDaoの基本的な使い方（前提知識）を説明するセクション |
| **None** | 検索クエリと**無関係** | 「ページングの実装方法」に対してログ出力の設定を説明するセクション |

判定手順:
1. このセクションは検索クエリに直接回答する情報を含んでいるか？ → YES: **High** / NO: 次へ
2. このセクションは検索クエリの理解に必要な前提知識・関連情報を含んでいるか？ → YES: **Partial** / NO: **None**

迷った場合: HighとPartialで迷ったら**Partial**を選ぶ（保守的に判定）。

#### Step C: フィルタ・ソート

- Noneを除外
- High → Partial の順でソート
- 同一relevance内はファイルパスでソート

#### 打ち切り条件

| 条件 | 動作 |
|---|---|
| 読み込みセクション数が **20件** に達した | 残りの候補は処理しない |
| Highが **5件** 見つかった | 残りの候補は処理しない |
| いずれかの条件に先に到達した方 | 処理を停止 |

#### 出力形式

呼び出し元（`_knowledge-search.md`）に以下の形式で返す:

```
file: features/libraries/universal-dao.json, section_id: paging, relevance: high
file: features/libraries/universal-dao.json, section_id: overview, relevance: partial
```

呼び出し元がポインタJSONに変換する。

#### エラーハンドリング

| 状態 | 対応 |
|---|---|
| 候補セクションが0件 | 空リストを返す |
| セクション内容が `SECTION_NOT_FOUND` | そのセクションをスキップ |
| 全セクションがNone判定 | 空リストを返す |

---

## 8. ヘルパースクリプトの内容

### パス解決パターン（両スクリプト共通）

スクリプトは自身の位置からknowledgeディレクトリを特定する。バージョン番号をハードコードしない:

```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KNOWLEDGE_DIR="$SKILL_DIR/knowledge"
```

この方式により:
- nabledge-6の場合: `KNOWLEDGE_DIR` = `.claude/skills/nabledge-6/knowledge`
- nabledge-5の場合: `KNOWLEDGE_DIR` = `.claude/skills/nabledge-5/knowledge`
- nabledge-6からnabledge-5にコピーしてもそのまま動作する

### 8.1 scripts/full-text-search.sh

```bash
#!/bin/bash
# 全知識ファイルの全セクションに対してキーワードOR検索を実行
#
# 引数: キーワード（1つ以上）
# 出力: ヒットしたファイルとセクションIDの一覧
# 出力形式: ファイル相対パス|セクションID

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KNOWLEDGE_DIR="$SKILL_DIR/knowledge"

if [ $# -eq 0 ]; then
  echo "Usage: $0 <keyword1> [keyword2] ..." >&2
  exit 1
fi

# 引数からjqのOR条件を組み立てる
conditions=""
for kw in "$@"; do
  if [ -n "$conditions" ]; then
    conditions="$conditions or "
  fi
  # jq正規表現のメタ文字をエスケープ
  escaped=$(echo "$kw" | sed 's/[.[\(*+?{|^$]/\\&/g')
  conditions="${conditions}test(\"$escaped\"; \"i\")"
done

# 全JSONファイルに対して検索
find "$KNOWLEDGE_DIR" -name "*.json" | sort | while read -r filepath; do
  relpath="${filepath#$KNOWLEDGE_DIR/}"
  jq -r --arg file "$relpath" \
    ".sections | to_entries[] | select(.value | ($conditions)) | \"\($file)|\(.key)\"" \
    "$filepath" 2>/dev/null
done
```

### 8.2 scripts/read-sections.sh

```bash
#!/bin/bash
# 複数セクションの内容を一括読み出し
#
# 引数: "ファイル相対パス:セクションID" のペアをスペース区切り
# 出力: 各セクションの内容を区切り付きで出力
#
# 出力形式:
#   === ファイル相対パス : セクションID ===
#   [セクション内容]
#   === END ===

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KNOWLEDGE_DIR="$SKILL_DIR/knowledge"

if [ $# -eq 0 ]; then
  echo "Usage: $0 <file:section> [file:section] ..." >&2
  exit 1
fi

for pair in "$@"; do
  file="${pair%%:*}"
  section="${pair##*:}"
  echo "=== $file : $section ==="
  jq -r --arg sec "$section" '.sections[$sec] // "SECTION_NOT_FOUND"' "$KNOWLEDGE_DIR/$file" 2>/dev/null || echo "FILE_NOT_FOUND"
  echo "=== END ==="
done
```

### 8.3 jqの可用性

jqが未インストールの環境ではPythonで代替する:

```python
import json, sys, re

def search_sections(filepath, keywords):
    with open(filepath) as f:
        data = json.load(f)
    for sid, content in data.get('sections', {}).items():
        for kw in keywords:
            if re.search(kw, content, re.IGNORECASE):
                print(f"{filepath}|{sid}")
                break
```

---

## 9. code-analysis.mdの修正

既存の `workflows/code-analysis.md` のStep 2内の知識検索呼び出し部分を修正する。

### 削除する箇所

Step 2内の以下のテキスト（L151〜L159付近）を削除する:

```
3. **Execute keyword-search workflow**:
   - Read `workflows/keyword-search.md`
   - Follow the workflow with combined keywords for all components
   - Expected output: 20-30 candidate sections covering all components

4. **Execute section-judgement workflow**:
   - Read `workflows/section-judgement.md`
   - Follow the workflow with candidate sections from step 3
   - Expected output: Filtered sections (High and Partial relevance only)
```

### 置換する内容

上記を以下に置き換える:

```
3. **Execute knowledge search workflow**:
   - Read `workflows/_knowledge-search.md`
   - Follow the workflow with the user's original request + detected components as search query
   - The workflow internally handles keyword extraction, full-text search, index-based fallback, and section judgement
   - Expected output: Pointer JSON with relevant sections (high/partial relevance)

4. **Read section content from Pointer JSON**:
   - For each result in Pointer JSON, extract section content:
     ```bash
     bash scripts/read-sections.sh \
       "file1:section1" "file2:section2" ...
     ```
   - Expected output: Section content text for documentation
```

### その他の修正箇所

- L50付近の `.keyword-search-results.json` への参照を削除する
- L112付近の `**Tools**: Read (index.toon), Bash with jq (keyword-search workflow)` を `**Tools**: Read, Bash with jq (knowledge-search workflow)` に修正する

### 完了条件

```bash
# keyword-searchとsection-judgementへの参照がないこと
grep -c "keyword-search\|section-judgement" .claude/skills/nabledge-6/workflows/code-analysis.md
# → 0

# _knowledge-searchへの参照があること
grep -c "_knowledge-search" .claude/skills/nabledge-6/workflows/code-analysis.md
# → 1以上
```

---

## 10. コマンドの作業

### n5コマンドの追加

`.claude/commands/n5.md` を新規作成:

```markdown
使い方: /n5 <質問またはコマンド>

例:
- /n5 Nablarch 5でのバッチ処理の実装方法
- /n5 トランザクション管理の設定方法
- /n5 code-analysis

以下のタスクをサブエージェントに委譲して、別コンテキストで実行してください。

サブエージェントへの指示:
.claude/skills/nabledge-5/SKILL.md を読み、その指示に従って以下を処理せよ。
$ARGUMENTS

知識検索の場合は回答のサマリーを、それ以外はワークフローの実行結果を返すこと。
```

### GitHub Copilot用プロンプトの追加

`.github/prompts/n5.prompt.md` を新規作成。`.github/prompts/n6.prompt.md` の `nabledge-6` を `nabledge-5` に置換した内容にする。

---

## 11. GitHub Actions・CI/CDの作業

### 11.1 transform-to-plugin.sh

`.github/scripts/transform-to-plugin.sh` の末尾（nabledge-6のコピー処理の後）に以下を追加する:

```bash
# nabledge-5 plugin (if exists)
if [ -d "$SOURCE_DIR/.claude/skills/nabledge-5" ]; then
  echo "Copying nabledge-5 plugin..."
  mkdir -p "$DEST_DIR/plugins/nabledge-5/.claude-plugin"
  mkdir -p "$DEST_DIR/plugins/nabledge-5/skills/nabledge-5"

  cp "$SOURCE_DIR/.claude/skills/nabledge-5/plugin/plugin.json" \
     "$DEST_DIR/plugins/nabledge-5/.claude-plugin/"

  cp "$SOURCE_DIR/.claude/skills/nabledge-5/SKILL.md" \
     "$DEST_DIR/plugins/nabledge-5/skills/nabledge-5/"
  cp -r "$SOURCE_DIR/.claude/skills/nabledge-5/workflows" \
        "$DEST_DIR/plugins/nabledge-5/skills/nabledge-5/"
  cp -r "$SOURCE_DIR/.claude/skills/nabledge-5/assets" \
        "$DEST_DIR/plugins/nabledge-5/skills/nabledge-5/"
  cp -r "$SOURCE_DIR/.claude/skills/nabledge-5/knowledge" \
        "$DEST_DIR/plugins/nabledge-5/skills/nabledge-5/"
  cp -r "$SOURCE_DIR/.claude/skills/nabledge-5/docs" \
        "$DEST_DIR/plugins/nabledge-5/skills/nabledge-5/"
  cp -r "$SOURCE_DIR/.claude/skills/nabledge-5/scripts" \
        "$DEST_DIR/plugins/nabledge-5/skills/nabledge-5/"

  cp "$SOURCE_DIR/.claude/skills/nabledge-5/plugin/README.md" \
     "$DEST_DIR/plugins/nabledge-5/"
  cp "$SOURCE_DIR/.claude/skills/nabledge-5/plugin/CHANGELOG.md" \
     "$DEST_DIR/plugins/nabledge-5/"
  cp "$SOURCE_DIR/.claude/skills/nabledge-5/plugin/GUIDE-CC.md" \
     "$DEST_DIR/plugins/nabledge-5/"
  cp "$SOURCE_DIR/.claude/skills/nabledge-5/plugin/GUIDE-GHC.md" \
     "$DEST_DIR/plugins/nabledge-5/"
fi
```

### 11.2 validate-marketplace.sh

`validate-marketplace.sh` のnabledge-6チェックの後に以下を追加する:

```bash
# nabledge-5 plugin validation (optional)
if [ -d "$MARKETPLACE_ROOT/plugins/nabledge-5" ]; then
  echo "Checking nabledge-5 plugin structure..."
  test -f "$MARKETPLACE_ROOT/plugins/nabledge-5/.claude-plugin/plugin.json" || { echo "Error: nabledge-5/plugin.json not found"; exit 1; }
  test -f "$MARKETPLACE_ROOT/plugins/nabledge-5/skills/nabledge-5/SKILL.md" || { echo "Error: nabledge-5/SKILL.md not found"; exit 1; }
  test -f "$MARKETPLACE_ROOT/plugins/nabledge-5/README.md" || { echo "Error: nabledge-5/README.md not found"; exit 1; }
  test -d "$MARKETPLACE_ROOT/plugins/nabledge-5/skills/nabledge-5/workflows" || { echo "Error: nabledge-5/workflows not found"; exit 1; }
  test -d "$MARKETPLACE_ROOT/plugins/nabledge-5/skills/nabledge-5/knowledge" || { echo "Error: nabledge-5/knowledge not found"; exit 1; }
  jq empty "$MARKETPLACE_ROOT/plugins/nabledge-5/.claude-plugin/plugin.json" || { echo "Error: Invalid nabledge-5/plugin.json"; exit 1; }
  echo "nabledge-5 validation passed"
else
  echo "nabledge-5 not found (optional), skipping"
fi
```

### 11.3 セットアップスクリプト

`scripts/setup-5-cc.sh` と `scripts/setup-5-ghc.sh` を新規作成する。それぞれ `scripts/setup-6-cc.sh`, `scripts/setup-6-ghc.sh` をベースに、以下を置換:
- `nabledge-6` → `nabledge-5`
- インストール先ディレクトリ名を `nabledge-5` に変更

---

## 12. ドキュメントの作業

### 12.1 CLAUDE.md

```markdown
- **nabledge-5**: Nablarch 5 (Java EE 7/8, Java 8+) - planned
```

上記の `- planned` を削除し、nabledge-6と同様の書き方にする。

### 12.2 marketplace.json

`.claude/marketplace/.claude-plugin/marketplace.json` を以下の内容に更新:

```json
{
  "name": "nabledge",
  "owner": { "name": "Nablarch" },
  "metadata": {
    "version": "0.4",
    "description": "Nablarch skills for AI-assisted development"
  },
  "plugins": [
    { "name": "nabledge-6", "source": "./plugins/nabledge-6" },
    { "name": "nabledge-5", "source": "./plugins/nabledge-5" }
  ]
}
```

### 12.3 marketplace README

`.claude/marketplace/README.md` のプラグイン表にnabledge-5行を追加:

```markdown
| [nabledge-5](plugins/nabledge-5/README.md) | Nablarch 5 | 提供中 |
```

### 12.4 nabledge-6 plugin/CHANGELOG.md

`[Unreleased]` セクションに以下を記載:

```markdown
### 変更
- **知識検索アーキテクチャの刷新**: 全文検索→インデックス検索のフォールバック構成に変更
- 知識ファイルのセクション形式をMarkdownテキストに統一（新形式での再生成により対応）
- index.toonを5フィールド構成に拡張

### 削除
- keyword-search.md、section-judgement.md（トップレベル）を新ワークフローに置換
- 旧検索パイプライン用スクリプト（extract-section-hints.sh、parse-index.sh、sort-sections.sh）を削除
- 既存の知識ファイル17件を削除（新形式での全量再生成を予定）
```

### 12.5 nabledge-6 plugin/README.md

「ワークフロー」セクションを以下に更新:

```markdown
### ワークフロー

Nablarchの知識を活用した開発支援ワークフローを提供します。

現在提供しているワークフロー:

- **知識検索**: Nablarchの知識ファイルから質問に回答する
- **コード分析**: Nablarchの観点からプロジェクトコードを分析し、構造や依存関係を可視化したドキュメントを生成する
```

### 12.6 その他

- `.claude/rules/changelog.md`: nabledge-5のCHANGELOGパスへの言及があれば追加
- `doc/development-status.md`: 現在の作業状況に合わせて更新

---

## 13. テストシナリオの作業

### nabledge-5 シナリオファイルの追加

`.claude/skills/nabledge-test/scenarios/nabledge-5/scenarios.json` を新規作成:

```json
{
  "metadata": {
    "version": "5.0.0",
    "description": "Test scenarios for nabledge-5",
    "total_scenarios": 0,
    "by_type": { "knowledge-search": 0, "code-analysis": 0 }
  },
  "scenarios": []
}
```

nabledge-6のシナリオファイル（`scenarios/nabledge-6/scenarios.json`）は変更しない。

---

## 14. 全体フロー図

```
ユーザーの質問
  │
  ▼
SKILL.md → qa.md
  │
  ▼
_knowledge-search.md
  │
  ├── Step 1: キーワード抽出（メモリ内）
  │
  ├── Step 2: 全文検索（経路1）
  │     └── full-text-search.sh [1 tool call]
  │
  ├── Step 3: 分岐判定（メモリ内）
  │     ├── ヒットあり → Step 6
  │     └── ヒットなし ↓
  │
  ├── Step 4: ファイル選定（経路2）
  │     └── index.toon読み込み [1 tool call]
  │
  ├── Step 5: セクション選定（経路2）
  │     └── jq一括処理 [1 tool call]
  │
  ├── Step 6: セクション判定（共通）
  │     └── read-sections.sh [1-3 tool calls]
  │
  └── Step 7: ポインタJSON返却（メモリ内）
  │
  ▼
qa.md に戻る
  │
  ├── セクション内容読み出し
  │     └── read-sections.sh [1-2 tool calls]
  │
  └── 回答生成（メモリ内）
  │
  ▼
回答（日本語）
```

ツールコール数:
- 経路1（全文検索ヒット）: 全体で5〜8回
- 経路2（インデックス検索）: 全体で7〜12回

---

## 15. 完了チェックリスト

### nabledge-6

- [ ] 旧ファイル6件が削除されている（keyword-search.md, knowledge-search.md, section-judgement.md, extract-section-hints.sh, parse-index.sh, sort-sections.sh）
- [ ] 知識ファイル（JSON）が0件（`find knowledge -name "*.json" | wc -l` → 0）
- [ ] index.toonがヘッダーのみ（3行）
- [ ] SKILL.md が§6の内容で作成されている
- [ ] 新ワークフロー7ファイルが作成されている（qa.md, _knowledge-search.md, full-text-search.md, index-based-search.md, file-search.md, section-search.md, section-judgement.md）
- [ ] 新スクリプト2ファイルが作成されている（full-text-search.sh, read-sections.sh）
- [ ] スクリプトに実行権限がある
- [ ] code-analysis.md 内に `keyword-search` `section-judgement` への参照がない
- [ ] code-analysis.md 内に `_knowledge-search` への参照がある
- [ ] plugin/plugin.json のバージョンが更新されている
- [ ] plugin/CHANGELOG.md に変更が記載されている

### nabledge-5

- [ ] §2のディレクトリ構造通りにファイルが配置されている
- [ ] SKILL.md に `nabledge-6` への参照がない
- [ ] `grep -r "nabledge-6" .claude/skills/nabledge-5/` がヒットしない
- [ ] index.toonがヘッダーのみ
- [ ] plugin/plugin.json の name が "nabledge-5"

### コマンド

- [ ] `.claude/commands/n5.md` が存在する
- [ ] `.github/prompts/n5.prompt.md` が存在する

### GitHub Actions

- [ ] transform-to-plugin.sh にnabledge-5のコピー処理がある
- [ ] validate-marketplace.sh にnabledge-5のバリデーションがある

### セットアップスクリプト

- [ ] `scripts/setup-5-cc.sh` が存在する
- [ ] `scripts/setup-5-ghc.sh` が存在する

### ドキュメント

- [ ] marketplace.json の plugins に nabledge-5 がある
- [ ] marketplace README に nabledge-5 行がある

### テストシナリオ

- [ ] `scenarios/nabledge-5/scenarios.json` が存在する
