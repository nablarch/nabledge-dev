# nabledge-creator 設計書：knowledge ワークフロー

この設計書はworkflows/knowledge.mdとその参照ファイルの内容を定義する。エージェントへの命令として記述する。

knowledgeワークフロー（生成）の後に、verifyワークフロー（検証）を別セッションで実行する。verify設計書は別ファイル。

関連する参照ファイル：
- references/knowledge-file-plan.md
- references/knowledge-schema.md

関連するスクリプト：
- scripts/validate-knowledge.py（構造チェック）
- scripts/convert-knowledge-md.py（JSON→MD変換）
- scripts/generate-checklist.py（検証セッション用チェックリスト生成）

---

# workflows/knowledge.md

マッピングファイルと公式ドキュメントから知識ファイル（JSON + Markdown）を生成するワークフロー。

## なぜこのワークフローが重要か

知識ファイルはnabledge-6スキルの検索パイプラインのデータソースになる。検索は3段階で動作する：

1. **index.toon**のヒントでファイルを選定する（L1/L2キーワード、閾値≥2点）
2. **JSON内index配列**のヒントでセクションを選定する（L2/L3キーワード、閾値≥2点）
3. **sectionsの中身**を読んでHigh/Partial/Noneの関連度を判定する

つまり、ヒントが不十分だと検索でヒットせず、セクションの粒度が粗いとHigh判定を得られない。このワークフローの品質が検索精度に直結する。

## ワークフロー手順

### Step 1: 対象の特定

`references/knowledge-file-plan.md`を読み、フィルタに該当する知識ファイルのリストを取得せよ。各エントリにはsources（読むべきrstファイル群）が記されている。

### Step 2: 知識ファイル生成

対象の知識ファイルを1つずつ生成せよ。各ファイルについて以下を行え。

**2a. ソースを読む**

sourcesに記されたrstファイル群を全部読め。日本語版（`en/`→`ja/`）も用語確認のため参照せよ。

**2b. セクションIDを決定する**

`references/knowledge-schema.md`の「セクション分割ルール」に従ってセクションIDを決定せよ。rstの見出し構造から導出する。

**2c. ヒントを抽出する**

`references/knowledge-schema.md`の「ヒント抽出ルール」に従ってヒントを抽出せよ。抽出元はrstの構造要素で決まっている。

**2d. JSONに変換する**

`references/knowledge-schema.md`のカテゴリ別テンプレートに従いJSONに変換せよ。

変換の判断基準：
- 仕様は全部残す（設定項目、デフォルト値、型、制約、動作仕様、理由・背景、注意点、警告）
- 考え方も全部残す（設計思想、推奨パターン、注意事項）
- 表現は最適化する（導入文や冗長な説明は削除、箇条書き化）
- 迷ったら：「この情報がないとAIが誤った判断をする可能性があるか？」→ YESなら残す

**2e. JSONを出力する**

`.claude/skills/nabledge-6/knowledge/{path}.json`に書き出せ。

### Step 3: Markdown変換

以下のコマンドを実行せよ。

```bash
python scripts/convert-knowledge-md.py .claude/skills/nabledge-6/knowledge/ --output-dir .claude/skills/nabledge-6/docs/
```

### Step 4: 検証

以下のコマンドを実行せよ。

```bash
python scripts/validate-knowledge.py .claude/skills/nabledge-6/knowledge/
```

failした場合、エラー内容を読んでJSONを修正し、Step 3から再実行せよ。

### Step 5: チェックリスト生成

以下のコマンドを実行せよ。

```bash
python scripts/generate-checklist.py .claude/skills/nabledge-6/knowledge/{file}.json --source .lw/nab-official/v6/nablarch-document/en/{source-path} --output .claude/skills/nabledge-6/knowledge/{file}.checklist.md
```

スクリプトはrstとJSONの両方を解析し、検証セッション用のチェックリストを生成する。生成セッションはここで完了。検証はverifyワークフロー（別セッション）で行う。

---

# references/knowledge-file-plan.md について

知識ファイルの一覧と、対応するマッピング行を定義する。以下のフォーマットで記述する。

```markdown
## features/processing/nablarch-batch.json

tags: batch
title: Nablarchバッチ（都度起動型・常駐型）
sources:
  - PP=nablarch-batch かつ Type=processing-pattern の全行
```

**統合パターン**：

| 知識ファイルの種類 | マッピング行との関係 |
|---|---|
| 処理方式 | N:1（同じCategory IDのprocessing-pattern行を統合） |
| ハンドラ | 1:1 |
| ライブラリ | 1:1 基本。サブ機能別ファイルならN:1 |
| ツール | N:1 |
| アダプタ | 1:1 |
| チェック | 1:1 |
| リリースノート | 特殊 |
| 概要 | 特殊 |

**Type/Category → 知識ファイルパスの変換**：

| Type | Category | パス |
|---|---|---|
| processing-pattern | nablarch-batch | features/processing/nablarch-batch.json |
| processing-pattern | restful-web-service | features/processing/restful-web-service.json |
| component | handlers | features/handlers/{sub}/{name}.json |
| component | libraries | features/libraries/{name}.json |
| component | adapters | features/adapters/{name}.json |
| development-tools | testing-framework | features/tools/{name}.json |
| development-tools | toolbox | features/tools/{name}.json |
| check | security-check | checks/security.json |
| about | about-nablarch | overview.json |
| about | release-notes | releases/{version}.json |

---

# references/knowledge-schema.md について

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

**必須ルール**：
- `id` = ファイル名（拡張子なし）
- `title`は日本語
- `official_doc_urls` ≥ 1
- `index`と`sections`のキーは1:1対応
- `sections`には`overview`を含める

---

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

---

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

---

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

### 共通プロパティ辞書

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

---

## 生成のInput→Output例

**入力**：`application_framework/.../handlers/standalone/data_read_handler.rst`

**出力**：`features/handlers/batch/data-read-handler.json`（ハンドラテンプレート適用）

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

**セクション分割の根拠**：rstのh2が「Overview」「Processing Flow」「Setup」「Constraints」の4つ → 4セクション。

**ヒント抽出の根拠**：
- overview: クラス名「DataReadHandler」（優先度2）、日本語タイトル「データリード」「データリーダ」（優先度5）、目的の主要語「入力データ読み込み」（優先度2に準ずる）
- processing: 見出し「処理フロー」（優先度1）、インターフェース「DataReader」（優先度2）、本文キーワード「順次読み込み」「1件ずつ」（優先度2）、マーカー「NoMoreRecord」（優先度2）
- setup: 見出し「設定」（優先度1）、プロパティ名「maxCount」（優先度3）、日本語「最大処理件数」（優先度5）、形式「XML」（優先度3に準ずる）
- constraints: 見出し「制約」（優先度1）、クラス名「DataReader」「ExecutionContext」（優先度2）、日本語「前提条件」（優先度5）

---

# scripts/convert-knowledge-md.py 仕様

JSON知識ファイルから人間向けの閲覧用Markdownを生成する。

## コマンドライン

```
python scripts/convert-knowledge-md.py INPUT_DIR [--output-dir DIR]
```

- `INPUT_DIR`：知識ファイルディレクトリ
- `--output-dir`：出力先（デフォルト：INPUT_DIRと同階層の`docs/`）

index.toonは除外する。ディレクトリ構造はknowledge/と同じにする。

## 変換ルール

### 全体構造

```markdown
# {title}

{sections.overview.description}

**目的**: {sections.overview.purpose}

（overviewのその他のプロパティ）

**公式ドキュメント**:
- [{url}]({url})

---

## {section-id}

（セクション内容）
```

### 型別の変換

| JSONの型 | Markdown表現 |
|---|---|
| 文字列 | 段落テキスト |
| 配列（文字列） | 箇条書き `- item` |
| 配列（キー揃いオブジェクト） | テーブル |
| 配列（キー不揃いオブジェクト） | ネスト箇条書き |
| フラットオブジェクト | `**key**: value` |
| ネストオブジェクト | `### key` で展開 |
| `*_example` キー | コードブロック（言語はキー名から推定） |
| `properties`/`settings`/`setup` | プロパティテーブル |

### 変換例

**配列（文字列）**：
```json
{"responsibilities": ["データの読み込み", "IDの採番"]}
```
→ `**責務**:` + 箇条書き

**配列（キー揃いオブジェクト）**：
```json
{"modules": [{"groupId": "com.nablarch", "artifactId": "nablarch-fw"}]}
```
→ Markdownテーブル

**コード例**：
`xml_example` → ` ```xml ` コードブロック

**プロパティ設定**：
```json
[{"name": "maxCount", "type": "int", "required": false, "description": "最大処理件数"}]
```
→ `| プロパティ | 型 | 必須 | 説明 |` テーブル

## 終了コード

- 0：正常
- 1：エラー

---

# scripts/validate-knowledge.py 仕様

構造的な正しさを検証する。生成セッションのStep 4で使用。

## コマンドライン

```
python scripts/validate-knowledge.py DIR [--source-dir DIR]
```

## 検証項目

| カテゴリ | チェック |
|---|---|
| スキーマ | 必須キー存在、id=ファイル名、index↔sections 1:1対応、overview存在 |
| テンプレート準拠 | overviewに必須プロパティがあるか（カテゴリ別） |
| セクション数 | ソースrstのh2数とJSONセクション数の差が±30%以内 |
| セクションサイズ | 各セクションが100-1500トークンの範囲内 |
| ヒント品質 | セクションごとhints≥3、ファイル全体hints≥10 |
| URL | official_doc_urls≥1、形式正確 |
| docs一致 | JSONに対応する.mdが存在するか |

## 終了コード

- 0：全pass
- 1：warningのみ
- 2：エラー

---

# scripts/generate-checklist.py 仕様

rstとJSONから検証セッション用のチェックリストを生成する。生成セッションのStep 5で使用。

## コマンドライン

```
python scripts/generate-checklist.py JSON_PATH --source RST_PATH [--output PATH]
```

- `JSON_PATH`：知識ファイル
- `--source`：ソースrst（複数指定可。処理方式などN:1統合の場合）
- `--output`：チェックリスト出力先（デフォルト：`{JSON_PATH}.checklist.md`）

## 処理の流れ

```
1. extract_from_rst()    → rstから構造化要素を抽出
2. extract_from_json()   → JSONからhints, sections内容を抽出
3. generate_hints_checklist()     → ヒント候補の消し込みリスト
4. generate_spec_checklist()      → 仕様項目の消し込みリスト
5. generate_questions()           → 想定質問（タイトルとヒントから自動生成）
6. output()              → チェックリストMarkdownを出力
```

### 1. extract_from_rst()

rstから以下を抽出する。

| 抽出対象 | パターン | 例 |
|---|---|---|
| クラス名 | `` `ClassName` ``（大文字始まり） | `DataReadHandler` |
| プロパティ名 | `name="propName"` | `maxCount` |
| アノテーション名 | `@AnnotationName` | `@GeneratedValue` |
| ディレクティブ | `.. important::`等（行番号 + 内容の先頭80文字） | `L42 .. important:: DataReaderが...` |
| 例外クラス名 | `Exception`で終わるクラス名 | `NoDataException` |
| h2見出し | `---`アンダーライン付き見出し | `Processing Flow` |

### 2. extract_from_json()

JSONから以下を抽出する。

- `index[].hints`の全ヒント（セクションID付き）
- `sections.*.setup[].name`の全プロパティ名
- `sections.*.errors.list[].exception`の全例外クラス名
- `sections`の全キー（セクションID一覧）

### 3-5. チェックリスト生成

抽出結果を照合し、消し込みリストを生成する。

## 出力例

```markdown
# チェックリスト: data-read-handler.json

**ソース**: application_framework/.../data_read_handler.rst
**生成日**: 2026-02-20

---

## ヒント候補

rstから抽出されたヒント候補。JSONのhintsに含まれているか確認せよ。

| # | 候補 | 種別 | rst出現セクション | JSON hints内 | 判定 |
|---|---|---|---|---|---|
| 1 | `DataReadHandler` | クラス名 | overview | overview:✓ | |
| 2 | `DataReader` | クラス名 | processing | processing:✓ | |
| 3 | `ExecutionContext` | クラス名 | constraints | constraints:✓ | |
| 4 | `NoMoreRecord` | クラス名 | processing | processing:✓ | |
| 5 | `NoDataHandler` | クラス名 | processing | なし | |
| 6 | `maxCount` | プロパティ | setup | setup:✓ | |
| 7 | `@Published` | アノテーション | overview | なし | |

「JSON hints内」が「なし」の項目を重点的に確認せよ。

---

## 仕様項目

### プロパティ

| # | プロパティ名 | rst行番号 | JSON setup内 | 判定 |
|---|---|---|---|---|
| 1 | `maxCount` | L35 | ✓ | |

### ディレクティブ

| # | 種別 | rst行番号 | 内容（先頭80文字） | 判定 |
|---|---|---|---|---|
| 1 | important | L42 | DataReaderが設定されていない場合は処理対象データ無しとしてNoMoreRecor... | |
| 2 | warning | L58 | マルチスレッド実行時はスレッドセーフなDataReaderを使用すること... | |

各ディレクティブについて：rstの該当行を読み、JSONのいずれかのセクションに内容が反映されているか確認せよ。

### 例外クラス

| # | 例外クラス名 | rst行番号 | JSON errors内 | 判定 |
|---|---|---|---|---|
| 1 | `NoDataException` | L72 | なし | |

---

## 想定質問

以下の質問で検索シミュレーションを行え。

1. 「バッチでデータ読み込みの最大件数を制限したい」
2. 「DataReaderが見つからないエラーが出た」
3. 「データリードハンドラの設定方法を知りたい」
```

## 終了コード

- 0：正常
- 1：エラー
