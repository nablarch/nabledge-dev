あなたはNablarchの公式ドキュメントをAI Readyな知識ファイルに変換するエキスパートです。

## タスク

以下のソースファイルを知識ファイル（JSON）に変換してください。

## ソースファイル情報

- ファイルID: `{FILE_ID}`
- 形式: `{FORMAT}` (rst/md/xlsx)
- Type: `{TYPE}`
- Category: `{CATEGORY}`
- 出力パス: `{OUTPUT_PATH}`
- Assetsディレクトリ: `{ASSETS_DIR}`
- 公式ドキュメントベースURL: `{OFFICIAL_DOC_BASE_URL}`

## ソースファイル内容

```
{SOURCE_CONTENT}
```

{ASSETS_SECTION}

---

## official_doc_urls の生成ルール

`official_doc_urls` にはソースファイルに対応する公式ドキュメントのURLを設定する。

### RST（公式解説書）

ソースファイルのパスから以下のルールでURLを生成する:

```
ベースURL: https://nablarch.github.io/docs/LATEST/doc/
変換ルール: nablarch-document/ja/ 以降のパスから .rst を除去し、ベースURLに結合

例:
  ソースパス: .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/handlers/common/db_connection_management_handler.rst
  URL: https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/handlers/common/db_connection_management_handler.html
```

スクリプト側で `{OFFICIAL_DOC_BASE_URL}` にこのURLを計算して渡す。`official_doc_urls` にはこのURLを1つ設定する。

加えて、ソース内の `:java:extdoc:` 参照からJavadoc URLを抽出し、`official_doc_urls` に追加する:

```
:java:extdoc:` の参照先パッケージ → https://nablarch.github.io/docs/LATEST/javadoc/ 配下のURL
例: nablarch.common.handler.DbConnectionManagementHandler
  → https://nablarch.github.io/docs/LATEST/javadoc/nablarch/common/handler/DbConnectionManagementHandler.html
```

### MD（パターン集）

パターン集の公式掲載先URLを設定する:

```
https://fintan.jp/page/252/
```

全パターン集ファイルで同一のURL。

### Excel（セキュリティ対応表）

パターン集と同様:

```
https://fintan.jp/page/252/
```

## 抽出ルール（最重要）

### 優先順位

| 優先度 | ルール | 判定 |
|:---:|---|:---:|
| 1 | ソースに書いてあることが漏れる | **NG（最悪）** |
| 2 | ソースに書いてないことを推測で入れる | **NG** |
| 3 | ソースに書いてあることが冗長に入る | **OK（許容）** |

- 迷ったら含める側に倒す
- 「たぶんこうだろう」「一般的にはこうなる」で補完しない
- 書いてあることであれば余分に入ってもよい、ないよりまし

### 残す情報

- **仕様は全部残す**: 設定項目、デフォルト値、型、制約、動作仕様、理由・背景、注意点、警告
- **考え方も全部残す**: 設計思想、推奨パターン、注意事項
- **表現は最適化する**: 読み物としての冗長な説明を省く。ただし情報は削らない
- **判断基準**: 「この情報がないとAIが誤った判断をする可能性があるか？」→ YESなら残す

---

## セクション分割ルール

### RSTの場合

- h1（`=====` で下線）→ ファイルタイトル（`title`フィールド）
- h2（`-----` で下線）→ セクション1つに対応（分割単位）
- h3以下 → 親セクション内に含める（分割しない）
- **例外**: h2配下のテキスト量が2000文字以上の場合、h3を分割単位に引き上げる

### MDの場合

- `#` → ファイルタイトル
- `##` → セクション分割単位
- `###` 以下 → 親セクション内に含める

### Excelの場合

- ファイル全体で1セクション

---

## 出力JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "title", "official_doc_urls", "index", "sections"],
  "properties": {
    "id": {
      "type": "string",
      "description": "知識ファイル識別子（ファイル名から拡張子を除いたもの）"
    },
    "title": {
      "type": "string",
      "description": "ドキュメントタイトル（RST: h1見出し、MD: #見出し、Excel: ファイル名）"
    },
    "official_doc_urls": {
      "type": "array",
      "description": "公式ドキュメントのURL",
      "items": { "type": "string" }
    },
    "index": {
      "type": "array",
      "description": "セクションの目次。検索時にhintsでセクションを絞り込む",
      "items": {
        "type": "object",
        "required": ["id", "title", "hints"],
        "properties": {
          "id": {
            "type": "string",
            "description": "セクション識別子（sectionsのキーと対応。ケバブケース）"
          },
          "title": {
            "type": "string",
            "description": "セクションの日本語タイトル（閲覧用MDの見出しに使用）"
          },
          "hints": {
            "type": "array",
            "description": "検索ヒント",
            "items": { "type": "string" }
          }
        }
      }
    },
    "sections": {
      "type": "object",
      "description": "セクション本体。キーはセクション識別子。値はMDテキスト",
      "additionalProperties": {
        "type": "string",
        "description": "セクション内容（Markdown形式のテキスト）"
      }
    }
  }
}
```

### 出力サンプル

```json
{
  "id": "db-connection-management-handler",
  "title": "データベース接続管理ハンドラ",
  "official_doc_urls": [
    "https://nablarch.github.io/docs/LATEST/doc/..."
  ],
  "index": [
    {
      "id": "overview",
      "title": "概要",
      "hints": ["DbConnectionManagementHandler", "データベース接続管理", "DB接続"]
    },
    {
      "id": "setup",
      "title": "設定",
      "hints": ["設定", "connectionFactory", "connectionName", "XML"]
    }
  ],
  "sections": {
    "overview": "後続のハンドラ及びライブラリで使用するためのデータベース接続を、スレッド上で管理するハンドラ\n\n**クラス名**: `nablarch.common.handler.DbConnectionManagementHandler`\n\n**モジュール**:\n```xml\n<dependency>\n  <groupId>com.nablarch.framework</groupId>\n  <artifactId>nablarch-core-jdbc</artifactId>\n</dependency>\n```",
    "setup": "| プロパティ名 | 型 | 必須 | デフォルト値 | 説明 |\n|---|---|---|---|---|\n| connectionFactory | ConnectionFactory | ○ | | ファクトリクラス |\n\n```xml\n<component class=\"nablarch.common.handler.DbConnectionManagementHandler\">\n  <property name=\"connectionFactory\" ref=\"connectionFactory\" />\n</component>\n```"
  }
}
```

---

## セクションIDの命名規約

全パターンで**ケバブケース**（小文字、ハイフン区切り）を適用する。

例: `overview`, `setup`, `handler-queue`, `anti-patterns`, `error-handling`

---

## 検索ヒント生成ルール（index[].hints）

日本語中心、技術用語は英語表記をそのまま含める。以下の観点で該当するものを**全て含める**（個数は固定しない）。

含める観点:
- 機能キーワード（そのセクションで何ができるか、日本語）
- クラス名・インターフェース名（英語表記）
- 設定プロパティ名（英語表記）
- アノテーション名（英語表記）
- 例外クラス名（英語表記）

---

## セクション内MD記述ルール

### クラス・インターフェース情報

```markdown
**クラス名**: `nablarch.common.handler.DbConnectionManagementHandler`
```

複数クラス: `**クラス**: \`Class1\`, \`Class2\``
アノテーション: `**アノテーション**: \`@InjectForm\`, \`@OnError\``

### モジュール依存

````markdown
**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-jdbc</artifactId>
</dependency>
```
````

### プロパティ一覧

```markdown
| プロパティ名 | 型 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|---|
| connectionFactory | ConnectionFactory | ○ | | ファクトリクラス |
```

必須列: ○ = 必須、空 = 任意。デフォルト値がない場合は空。

### コード例

java, xml 等のコードブロックを使用。

### 注意喚起ディレクティブ

| RSTディレクティブ | MD表現 |
|---|---|
| `.. important::` | `> **重要**: テキスト` |
| `.. tip::` | `> **補足**: テキスト` |
| `.. warning::` | `> **警告**: テキスト` |
| `.. note::` | `> **注意**: テキスト` |

### 処理の流れ

```markdown
1. 共通起動ランチャ(Main)がハンドラキューを実行する
2. DataReaderが入力データを読み込む
3. アクションクラスが業務ロジックを実行する
```

### ハンドラ構成表

```markdown
| No. | ハンドラ | 往路処理 | 復路処理 | 例外処理 |
|---|---|---|---|---|
| 1 | ステータスコード変換ハンドラ | — | ステータスコード変換 | — |
```

### 機能比較表

```markdown
| 機能 | Jakarta Batch | Nablarchバッチ |
|---|---|---|
| 起動パラメータ設定 | ◎ | ○ |
```

凡例: ◎ = 仕様で定義、○ = 提供あり、△ = 一部提供、× = 提供なし、— = 対象外

脚注がある場合は表の直後に記載:

```markdown
[1] ResumeDataReaderを使用することで再実行が可能。ただしファイル入力時のみ。
```

### クロスリファレンスの変換

| ソース記載 | 変換先 |
|---|---|
| `:ref:` / `:doc:`（同一ファイル内） | `セクションID を参照` |
| `:ref:` / `:doc:`（別ファイル） | `知識ファイルID を参照` |
| `:java:extdoc:` | `official_doc_urls` に含める |

### 画像・添付ファイルの扱い

テキスト代替を優先し、代替できない場合はassetsディレクトリに取り込んでパス参照する。

| 画像種別 | 対応方法 |
|---|---|
| フロー図 | テキスト代替（番号付きリスト） |
| アーキテクチャ/構成図 | テキスト代替（定義リスト形式） |
| 画面キャプチャ | テキスト代替（手順の説明） |
| 上記でテキスト代替が困難な図 | `assets/{知識ファイルID}/` に配置し、MD内で `![説明](assets/{知識ファイルID}/filename.png)` で参照 |

Office等の添付ファイル（テンプレートExcel等）は `assets/{知識ファイルID}/` に配置し、MD内でパス参照する。

---

## エラーハンドリング

ソースファイルの内容に問題がある場合は、以下のガイドラインに従ってください:

- **破損したRST/MD構文**: 可能な範囲で解釈し、読み取れる情報を抽出。完全に解釈不能な場合はエラーメッセージを出力せず、読み取れた部分のみで知識ファイルを生成
- **画像が見つからない**: テキスト代替に注力。画像ファイルがないことは無視
- **不完全な表**: 読み取れる行・列のみを抽出
- **文字化け**: 文脈から推測せず、読み取れる部分のみ抽出

## 出力形式の指示

以下のJSON形式で出力してください。JSON以外のテキスト（説明文等）は一切含めないでください。

```json
{出力JSONをここに}
```
