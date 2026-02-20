# knowledge-schema.md

JSON構造とカテゴリ別テンプレートの定義。

## JSON構造（共通）

```json
{
  "id": "string（ファイル名 拡張子なし、kebab-case）",
  "title": "string（日本語タイトル）",
  "official_doc_urls": ["string（1つ以上）"],
  "index": [
    {"id": "string（sectionsのキーと1:1対応）", "hints": ["string（3-8個、日英混在）"]}
  ],
  "sections": {
    "overview": { "...カテゴリ別テンプレート参照..." },
    "{section-id}": { "..." }
  }
}
```

**必須ルール**:

- `id` = ファイル名（拡張子なし）
- `title`は日本語
- `official_doc_urls` ≥ 1
- `index`と`sections`のキーは1:1対応
- `sections`には`overview`を含める

## セクション分割ルール

rstの見出し構造に基づいてセクションIDを導出する。Nablarch解説書は人が読む文書なので、見出し単位が自然なセクション境界になる。

### 基本ルール

rstの見出しレベル2（`---`アンダーライン）をセクション境界にする。

```rst
Universal DAO
=============        ← h1：ファイルタイトル（= titleに使用）

Overview              ← h2 → セクション "overview"
---------
...

Paging               ← h2 → セクション "paging"
------
...

Search Condition     ← h2 → セクション "search-condition"
----------------
...
```

h2見出しテキストをkebab-caseに変換してセクションIDにする。

### 調整ルール

| 条件 | 対応 |
|---|---|
| h2の内容が短い（100トークン未満） | 次のh2と統合してよい |
| h2の内容が長い（1500トークン以上） | h3で分割してよい。IDは`{h2-id}-{h3-id}` |
| `getting_started`系のh2 | スキップ（チュートリアルは対象外） |

### 必ず追加するセクション

rstの見出しに関係なく、以下のセクションは必ず作る：

| セクションID | 内容 | ソース |
|---|---|---|
| `overview` | 全体の位置づけ・目的 | rstの冒頭段落 |
| `errors` | エラー対処（該当する場合） | rst内の例外・エラー関連記述を集約 |

### 処理方式（N:1統合）の場合

複数rstを1つのJSONに統合する場合、rstファイル名をそのままセクションIDにするのではなく、内容の論理的なまとまりでセクションIDを設計せよ。ここはエージェントの判断が必要。ただしrstのh2を出発点にすること。

### validate-knowledge.pyによるチェック

- overviewセクションが存在するか
- ソースrstのh2見出し数とJSONのセクション数の差が±30%以内か
- 各セクションのトークン数が100-1500の範囲内か

## ヒント抽出ルール

rstの構造要素から抽出する。カテゴリごとに何を含めるか決まっている。

### セクションレベルヒント（JSON内index配列。3-8個）

以下の抽出元から、上から順に該当するものを含める。8個を超えたら下から削る。3個未満ならセクション内の主要な技術用語を追加する。

| 優先度 | 抽出元 | 例 |
|:---:|---|---|
| 1 | そのセクションのh2見出しテキスト（日英両方） | 「ページング」「Paging」 |
| 2 | セクション内のクラス名・インターフェース名 | 「UniversalDao」「DataReader」 |
| 3 | セクション内の設定プロパティ名 | 「maxCount」「per」「page」 |
| 4 | セクション内のアノテーション名 | 「@GeneratedValue」「@Version」 |
| 5 | 日本語版rstの対応見出しテキスト | 「ページング」 |

### ファイルレベルヒント（index.toonに記載。5-10個）

| 優先度 | 抽出元 | 例 |
|:---:|---|---|
| 1 | L1技術領域（下表から導出） | 「ハンドラ」「データベース」 |
| 2 | rstのファイルタイトル（h1、日英両方） | 「Universal DAO」「ユニバーサルDAO」 |
| 3 | rst冒頭段落の主要クラス名 | 「UniversalDao」 |
| 4 | 全セクションヒントの中で出現頻度が高いもの | 「CRUD」「検索」 |

### L1技術領域の導出テーブル

| Category | L1ヒント |
|---|---|
| handlers | ハンドラ |
| libraries | rstの内容から判断（DB系→データベース、ファイル系→ファイル、等） |
| adapters | アダプタ |
| processing / nablarch-batch | バッチ |
| processing / restful-web-service | REST Web |
| testing-framework | テスト NTF |
| toolbox | ツール |
| security-check | セキュリティ |

librariesのL1はrstの内容から判断が必要。ここがエージェント判断になる。

## カテゴリ別JSONテンプレート

### ハンドラ（handlers）

```json
{
  "sections": {
    "overview": {
      "class_name": "完全修飾クラス名",
      "description": "100-200文字の要約",
      "purpose": "目的（1文）",
      "responsibilities": ["責務1", "責務2"],
      "modules": [{"groupId": "...", "artifactId": "..."}]
    },
    "{機能セクション}": {
      "description": "説明"
    },
    "setup": [
      {"name": "プロパティ名", "type": "型", "required": true/false, "description": "説明", "default": "デフォルト値"}
    ],
    "errors": {
      "list": [{"exception": "例外クラス名", "cause": "原因", "resolution": "対処法"}]
    }
  }
}
```

### ライブラリ（libraries）

```json
{
  "sections": {
    "overview": {
      "classes": ["主要クラス名"],
      "annotations": ["アノテーション"],
      "description": "100-200文字の要約",
      "purpose": "目的",
      "modules": [{"groupId": "...", "artifactId": "..."}],
      "prerequisites": ["前提条件"],
      "limitations": ["制限事項"]
    },
    "{機能セクション}": {
      "description": "説明"
    },
    "configuration": {},
    "anti-patterns": {
      "list": [{"pattern": "名前", "description": "説明", "solution": "対策"}]
    },
    "errors": {
      "list": [{"exception": "例外", "cause": "原因", "resolution": "対処"}]
    }
  }
}
```

### 処理方式（processing）

```json
{
  "sections": {
    "overview": {
      "description": "100-200文字の要約",
      "use_cases": ["ユースケース"],
      "features": ["特徴"]
    },
    "architecture": {
      "description": "アーキテクチャ説明",
      "components": ["構成要素"],
      "process_flow": "処理フロー"
    },
    "handler-queue-{type}": {
      "description": "ハンドラキュー構成",
      "handlers": ["ハンドラ名"],
      "notes": ["注意点"]
    },
    "patterns-{name}": {
      "name": "パターン名",
      "description": "説明",
      "use_cases": ["ユースケース"],
      "flow": "処理フロー",
      "implementation_points": ["実装ポイント"]
    },
    "configuration": {},
    "anti-patterns": {
      "list": [{"pattern": "名前", "description": "説明"}]
    },
    "errors": {
      "list": [{"exception": "例外", "cause": "原因", "resolution": "対処"}]
    }
  }
}
```

### アダプタ（adapters）

```json
{
  "sections": {
    "overview": {
      "class_name": "完全修飾クラス名",
      "description": "要約",
      "purpose": "目的",
      "modules": [{"groupId": "...", "artifactId": "..."}],
      "adapted_library": "アダプト先ライブラリ名"
    },
    "setup": [
      {"name": "プロパティ名", "type": "型", "required": true/false, "description": "説明"}
    ],
    "{機能セクション}": {
      "description": "説明"
    }
  }
}
```

### ツール（tools）

ツールはNTFのように構造が多様なため、overviewのみテンプレート化する。機能セクションの内部構造は自由。

```json
{
  "sections": {
    "overview": {
      "description": "要約",
      "purpose": "目的",
      "modules": [{"groupId": "...", "artifactId": "..."}]
    },
    "{機能セクション}": {}
  }
}
```

### チェック（checks）

```json
{
  "sections": {
    "overview": {
      "description": "要約",
      "purpose": "目的"
    },
    "{チェック項目グループ}": {
      "items": [{"id": "項目ID", "description": "説明", "check_point": "確認ポイント", "severity": "重要度"}]
    }
  }
}
```

## 共通プロパティ辞書

機能セクション内で使用できる共通プロパティ。該当するものだけ使え。

| プロパティ | 型 | 使用場面 |
|---|---|---|
| `description` | string | 常に。セクションの説明 |
| `xml_example` | string | XML設定例 |
| `java_example` | string | Javaコード例 |
| `sql_example` | string | SQL例 |
| `properties` | array | コンポーネントの設定プロパティ |
| `notes` | array(string) | 注意事項（`.. tip::`由来） |
| `warnings` | array(string) | 警告（`.. warning::`由来） |
| `reference` | string | 関連ドキュメントへの参照 |

## 生成のInput→Output例

**入力**: `application_framework/.../handlers/standalone/data_read_handler.rst`

**出力**: `features/handlers/batch/data-read-handler.json`（ハンドラテンプレート適用）

```json
{
  "id": "data-read-handler",
  "title": "データリードハンドラ",
  "official_doc_urls": ["https://nablarch.github.io/docs/6u3/doc/.../data_read_handler.html"],
  "index": [
    {"id": "overview", "hints": ["DataReadHandler", "データリード", "データリーダ", "入力データ読み込み"]},
    {"id": "processing", "hints": ["処理フロー", "DataReader", "順次読み込み", "1件ずつ", "NoMoreRecord"]},
    {"id": "setup", "hints": ["設定", "maxCount", "最大処理件数", "XML"]},
    {"id": "constraints", "hints": ["制約", "DataReader", "ExecutionContext", "前提条件"]}
  ],
  "sections": {
    "overview": {
      "class_name": "nablarch.fw.handler.DataReadHandler",
      "description": "データリーダを使用して入力データの順次読み込みを行うハンドラ",
      "purpose": "バッチ処理における入力データの順次読み込みを制御し、データ終端の判定を行う",
      "responsibilities": ["データリーダを使用して入力データの読み込み", "実行時IDの採番", "データ終端の判定"],
      "modules": [{"groupId": "com.nablarch.framework", "artifactId": "nablarch-fw-standalone"}]
    },
    "processing": {
      "description": "データリーダから入力データを1件読み込み後続ハンドラに委譲する。終端でNoMoreRecordを返却",
      "data_reader": {"interface": "nablarch.fw.DataReader", "source": "ExecutionContextに設定", "end_marker": "NoMoreRecord"}
    },
    "setup": [
      {"name": "maxCount", "type": "int", "required": false, "description": "最大の処理件数", "default": "制限なし"}
    ],
    "constraints": {
      "prerequisites": ["ExecutionContextにDataReaderが設定されていること"],
      "notes": ["DataReaderが未設定の場合はNoMoreRecordを返却する"]
    }
  }
}
```

**セクション分割の根拠**: rstのh2が「Overview」「Processing Flow」「Setup」「Constraints」の4つ → 4セクション。

**ヒント抽出の根拠**:

- overview: クラス名「DataReadHandler」（優先度2）、日本語タイトル「データリード」「データリーダ」（優先度5）、目的の主要語「入力データ読み込み」（優先度2に準ずる）
- processing: 見出し「処理フロー」（優先度1）、インターフェース「DataReader」（優先度2）、本文キーワード「順次読み込み」「1件ずつ」（優先度2）、マーカー「NoMoreRecord」（優先度2）
- setup: 見出し「設定」（優先度1）、プロパティ名「maxCount」（優先度3）、日本語「最大処理件数」（優先度5）、形式「XML」（優先度3に準ずる）
- constraints: 見出し「制約」（優先度1）、クラス名「DataReader」「ExecutionContext」（優先度2）、日本語「前提条件」（優先度5）
