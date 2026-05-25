# 検索設計書

v6の検索実装（`workflows/`, `scripts/`）の設計。

---

## 概要

4つのワークフローを提供する:

| ワークフロー | 用途 |
|---|---|
| `workflows/qa.md` | Nablarchの使い方を質問すると、日本語で回答する |
| `workflows/semantic-search.md` | 質問の内容に関連するナレッジセクションを探す |
| `workflows/keyword-search.md` | クラス名・メソッド名などのキーワードで、言及しているナレッジセクションを探す |
| `workflows/code-analysis.md` | 既存コードを指定すると、依存関係を追跡しNablarch観点でドキュメントを生成する |

---

## ディレクトリ構成

```
.claude/skills/nabledge-6/
├── SKILL.md           — スキルのエントリーポイント定義・使い方
├── knowledge/         — RBKC が生成するナレッジJSONとインデックス（353ファイル）
│   ├── index.md       — 意味検索が読むページ一覧（カテゴリ/ページ/セクション構造）
│   └── {category}/    — カテゴリ別のナレッジJSON
├── workflows/         — ワークフロー定義（qa.md, semantic-search.md 等）
│   └── code-analysis/ — コード分析ワークフローのサブテンプレート
├── scripts/           — ワークフローが呼び出すBashスクリプト
├── docs/              — ユーザー向けドキュメント（GUIDE等）
├── assets/            — 回答テンプレート等
└── plugin/            — マーケットプレイス配布用メタデータ・CHANGELOG
```

---

## ナレッジファイルの生成（RBKC）

`knowledge/` 以下のファイルはすべて RBKC（Rule-Based Knowledge Creator）が自動生成する。手動編集は禁止。

```
Nablarch公式ドキュメント（RST/Markdown/Excel）
  ↓ tools/rbkc/rbkc.sh create 6
知識JSON（353ファイル）+ knowledge/index.md
```

`index.md` は `tools/benchmark/scripts/generate_index.py` が生成する。カテゴリ（H2）→ページ（H3）→セクション（L2/L3）の階層構造で、意味検索の Step 1 でページ選定の手がかりとして使われる。

---

## 実行環境（CC / GHC）

ユーザーからの入口は2つある:

| 環境 | 入口 | 実行方式 |
|---|---|---|
| Claude Code（CC） | `/n6 <質問またはコマンド>` | メインエージェントで SKILL.md を読んで実行 |
| GitHub Copilot（GHC） | `@n6 <質問またはコマンド>` | メインエージェントで SKILL.md を読んで実行 |

メインエージェントで実行するため、`qa.md` のヒアリング（Step 2）や `code-analysis.md` のターゲット確認など、ユーザーとの対話が機能する。

どちらも SKILL.md のルーティング定義に従い、引数によって実行するワークフローを切り替える:

| 引数 | 実行するワークフロー |
|---|---|
| なし | ユーザーに QA / コード分析 を選ばせる |
| `<質問>` | `workflows/qa.md` |
| `code-analysis` | `workflows/code-analysis.md` |
| `keyword-search "<terms>"` | `workflows/keyword-search.md` |
| `semantic-search "<question>"` | `workflows/semantic-search.md` |

---

## QAワークフロー（`workflows/qa.md`）

### 全体フロー

```
入力（質問テキスト）
  ↓
Step 1: 質問を分類（processing_type / purpose）
  ↓ （未確定の軸がある場合）
Step 2: ユーザーへ確認
  ↓
Step 3: 意味検索 → selected_sections（最大30件）
  ↓
Step 4: セクション内容を読む（最大10件）
  ↓ （sections_content が空）→ 「知識ファイルに含まれていません」で終了
Step 5: 回答生成
  ↓
Step 6: ハルシネーション検証
  ↓
Step 7: FAIL時 → Step 5 を再実行（問題のclaimを除外）
  ↓
Step 8: 最終回答を出力
```

### Step 1: 質問分類

2つの軸を独立して判定する。

| 軸 | 確定条件 | 値 |
|---|---|---|
| `processing_type` | 質問が明確に1種類の処理方式に属する | その処理方式名 |
| `processing_type` | 横断的（テストフレームワーク、i18n、ロギング等） | `null` |
| `processing_type` | 判断できない | `UNCLEAR` |
| `purpose` | 質問から明確に判定できる | カテゴリ名 |
| `purpose` | 判断できない | `UNCLEAR` |

**処理方式の選択肢**: ウェブアプリケーション / RESTfulウェブサービス / Nablarchバッチ / Jakartaバッチ / テーブルをキューとして使ったメッセージング / HTTPメッセージング / MOMメッセージング

**目的の選択肢**: 実装したい / 仕組み・動作を理解したい / 不具合・エラーを調査したい / テストを書きたい / バージョンアップしたい / セキュリティ対応したい

両軸が確定済み → Step 3 へスキップ。どちらかが `UNCLEAR` → Step 2 へ。

なお、トランザクション・バリデーション・DBアクセス・SQLなど、処理方式によって設定や実装が異なる概念は「横断的」には分類しない。

### Step 2: ユーザーへの確認

`UNCLEAR` な軸についてのみ質問する。両軸が `UNCLEAR` なら1メッセージにまとめる。  
ユーザーが「その他」または8を選択した場合: `processing_type = null` / `purpose = 実装したい` とする。  
回答を受け取ったら Step 3 へ進む。

### Step 3: 意味検索

`workflows/semantic-search.md` を実行する。

質問テキストの構築:
- `processing_type` が null でない場合: `"{質問}（処理方式: {processing_type}）（目的: {purpose}）"`
- `processing_type` が null の場合: `"{質問}（目的: {purpose}）"`

返値の `selected_sections` を保存する。

### Step 4: セクション内容の読み取り

`selected_sections` から読み取り対象を選ぶ:
1. `high` セクションを優先
2. 空きスロットに `partial` セクションを追加
3. 合計最大10件

```bash
bash scripts/read-sections.sh "file1.json:s1" "file2.json:s3" ...
```

出力を `sections_content` として保存。`selected_sections` が空なら `sections_content = ""`。

### Step 5: 回答生成

`sections_content` が空なら「この情報は知識ファイルに含まれていません。」を出力して終了。

そうでなければ以下の形式で日本語回答を生成する（500トークン以内、複雑な質問は最大800トークン）:

```
**結論**: 質問への直接回答（1〜2文）
  - 具体的なメソッド名・クラス名・方式を含む
  - 質問の言い換えにしない

**根拠**: 結論を裏付けるコード例・設定例・仕様情報
  - コード/設定例はコードブロックで表示
  - 優先順位: 実装例 > 設定例 > API仕様 > 概念説明
  - セクションのコード例は verbatim（変更不可）

**注意点**: 制約・リソース管理・よくある誤り（該当なければ省略）

参照: 回答で実際に引用したセクション（file.json:sN形式、カテゴリパス省略）
```

`processing_type` が null でない場合はその処理方式に合致する情報を優先する。  
セクションにない情報のギャップは「この情報は知識ファイルの対象範囲外です」と記述（推測しない）。

一般的なJava/プログラミング知識（try-catch、Bean、getter/setter等）はナレッジセクションと併用可。

結果を `answer_text` として保存。

### Step 6: ハルシネーション検証

`answer_text` 中のNablarch固有クレームを抽出し、各クレームが `sections_content` で裏付けられているか検証する。

**抽出対象（Nablarch固有クレーム）**:

| カテゴリ | 例 |
|---|---|
| API名 | `UniversalDao.deferメソッド`、`@InjectFormアノテーション` |
| クラス名 | `DatabaseRecordReader`、`BatchAction` |
| 設定方法 | `web-component-configuration.xmlに設定`、`コンポーネント定義ファイルに記述` |
| 動作仕様 | `遅延ロードはDB接続をストリーミングする`、`バリデーションエラー時にステータスコード400を返す` |
| 制約 | `closeしないとリソースリーク`、`Formのプロパティは全てString型` |
| パラメータ | `-requestPathで指定`、`SQLID` |

**抽出しない（一般知識）**:

| カテゴリ | 例 |
|---|---|
| 一般Java | `Beanクラスを作成する`、`try-with-resourcesを使う` |
| 一般プログラミング | `バリデーションを実行する`、`エラーメッセージを表示する` |
| フロー記述 | `まず〜して、次に〜する` |
| 一般Webの概念 | `HTTPリクエスト`、`JSONレスポンス` |

各クレームの判定順序:
1. セクション内容に直接記述がある → 裏付けあり
2. セクション内容の言い換え（paraphrase/省略/同義語）→ 裏付けあり
3. 明示されていない属性・動作・制約 → 裏付けなし（技術的に妥当でも）

いずれかのクレームが裏付けなしなら `verify_result = FAIL`（`issues` に未裏付けクレーム一覧を記録）。すべて裏付けあれば `verify_result = PASS`。

### Step 7: 検証結果の処理

- **PASS**: `final_answer = answer_text`
- **FAIL**: `issues` に含まれるクレームを含めずに Step 5 を再実行し、結果を `final_answer` とする

### Step 8: 出力

`final_answer` をユーザーに出力する。

---

## 意味検索（`workflows/semantic-search.md`）

### 入力

`{question}`: ユーザーの質問テキスト（処理方式・目的の補足文を含む）

### 出力

ポインタJSON（`selected_sections` 配列）

### ステップ

**Step 1: インデックス読み取り**

`knowledge/index.md` を読む。内容を `index_content` として保存。

**Step 2: ページ選定**

1. 質問の要約（1文）を書く
2. `（処理方式: X）` / `（目的: X）` の制約を抽出する
3. インデックス内の各ページに対して以下の決定手順を適用する:
   - 質問が尋ねている機能・コンポーネント・トピックをカバーするページ → **候補**
   - 質問の技術的問題を直接解決する機能をカバーするページ → **候補**
   - 質問で指定された処理方式をカバーするページ → **候補**（*異なる*処理方式をカバーするページ → **スキップ**）
   - それ以外 → **スキップ**
4. 目的が特定された場合、以下の優先カテゴリ順で候補をソートする:

| 目的 | 優先カテゴリ |
|---|---|
| 実装したい | `processing-pattern/*`, `component/libraries`, `component/adapters` |
| 仕組み・動作を理解したい | `component/handlers`, `component/libraries`, `about/about-nablarch` |
| 不具合・エラーを調査したい | `component/handlers`, `component/libraries`, `processing-pattern/*` |
| テストを書きたい | `development-tools/testing-framework`, `component/libraries` |
| バージョンアップしたい | `about/migration`, `releases/releases`, `about/release-notes` |
| セキュリティ対応したい | `check/security-check`, `component/handlers`, `processing-pattern/*` |

5. 候補がゼロなら `{"selected_sections": []}` を即時返す。そうでなければ上位10件を選ぶ（3件未満でもパディングしない）
6. 選択したページパス（`knowledge/` からの相対パス）を `selected_pages` として保存する

**Step 3: セクション選定**

`selected_pages` 内の各パスについて（最大10件）:
1. `knowledge/{path}` を読む
2. 各セクションに以下の決定手順を適用する:
   - 「このセクションなしに質問への完全な回答は不可能か？」→ **high**
   - 「このセクションは high セクションを使う際に必要な背景や設定を提供しており、high セクションだけからは推測できないか？」→ **partial**
   - それ以外 → **skip**

   常にスキップ:
   - 具体的な情報のない一般概要のみのセクション
   - モジュール一覧・改訂履歴・その他定型文
   - 選択済みの high セクションと同じ情報を再述するセクション
   - 実装の詳細を持たない概念定義のみのセクション
   - high セクションと同じ情報を別の角度から説明するセクション

high セクションを優先して収集する。合計30件になるまで partial セクションを追加する（high が30件ある場合は partial を追加しない）。

返値: relevance 降順（high → partial）でソートしたポインタJSON

---

## キーワード検索（`workflows/keyword-search.md`）

### 入力

`{keywords}`: 検索キーワードのリスト（例: `UniversalDao`, `batchUpdate`, `ページング`）

### 出力

ポインタJSON（`results` 配列）

### ステップ

**Step 1: キーワード検索スクリプトの実行**

```bash
bash scripts/keyword-search.sh <keyword1> [keyword2] ...
```

`{keywords}` が空なら `{"results": []}` を即時返す。

スクリプトの出力はカテゴリ > ページ > セクションの階層JSON。`section_id` フィールドは `"ファイルパス:セクションID"` の完全形式。

出力が空配列 `[]` なら `{"results": []}` を即時返す。

**Step 2: ポインタJSONへの変換**

各セクションエントリを変換する:
- `section_id` を**最後の `:`** で分割 → `file` と `sid`
- エントリを作成: `{"file": file, "section_id": sid, "relevance": "partial"}`
- `(file, section_id)` で重複除去

---

## キーワード検索スクリプト（`scripts/keyword-search.sh`）

### 動作仕様

全知識JSONファイルを全文スキャンして、キーワードにマッチするセクションを返す。

| 仕様項目 | 詳細 |
|---|---|
| 大文字小文字 | 区別しない（lowercase変換して比較） |
| マッチ方式 | 部分一致（substring） |
| マッチ対象フィールド | セクションの `title` と `content` |
| 複数キーワード時のページ条件 | AND（全キーワードがそのファイルのいずれかのセクションにヒットすること） |
| 複数キーワード時のセクション条件 | OR（いずれかのキーワードにヒットするセクションを返す） |
| 最小キーワード長 | 2文字（2文字未満は無視） |
| 結果上限 | なし |
| スキップ条件 | `no_knowledge_content: true` のファイル |

### 出力形式

カテゴリ > ページ > セクションの階層JSON。`section_id` は `"相対ファイルパス:sN"` の完全形式。

---

## セクション読み取りスクリプト（`scripts/read-sections.sh`）

### 動作仕様

`"ファイルパス:セクションID"` ペアを引数として受け取り、各セクションの内容を返す。

入力バリデーション: 絶対パス（`/`始まり）と `../` を含むパスは拒否する。

### 出力形式

```
=== relative-file-path : section-id ===
# {ページタイトル} > {セクションタイトル}
[セクション内容]
=== END ===
```

ファイルが存在しない場合は `FILE_NOT_FOUND`、セクションが存在しない場合は `SECTION_NOT_FOUND` を出力する。

セクションを持たないページ（単一コンテンツのページ）の場合は、`# {ページタイトル}` に続いてページ全体の内容を返す。
