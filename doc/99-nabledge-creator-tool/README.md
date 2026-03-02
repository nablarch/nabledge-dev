# knowledge-creator

Nablarchの公式ドキュメント（RST / MD / Excel）を、AIエージェントが検索・参照できる知識ファイル（JSON）に変換するツールです。

## 処理フロー

| Step | 処理 | 方式 | 説明 |
|---|---|---|---|
| 1 | ソースファイル一覧の取得 | スクリプト | 公式解説書（RST）、パターン集（MD）、セキュリティ対応表（Excel）を走査し、処理対象を一覧化。目次ファイルや英語翻訳は自動除外 |
| 2 | Type / Category 分類 | スクリプト | ソースのディレクトリパスからType・Categoryを機械的に決定し、出力先パスを確定 |
| 3 | 知識ファイル生成 | claude -p | ソース1ファイルにつき1セッションで知識ファイル（JSON）を生成。「漏れなく、盛らず」の抽出ルールに従い、ソースの仕様・設定・注意点を漏らさず抽出。並行処理対応 |
| 4 | インデックス生成 | スクリプト + claude -p | 全知識ファイルのメタ情報を集約しindex.toonを生成。処理パターン分類のみclaude -pが判定 |
| 5 | 閲覧用Markdown生成 | スクリプト | 知識ファイル（JSON）から人間向けMarkdownを機械的に変換 |
| 6 | 検証 | スクリプト + claude -p | 構造チェック（17項目）+ 内容検証（4観点）で品質を確認。全項目pass/failの2値判定、failはOKまで修正 |

### Step 6: 検証の詳細

構造チェック（スクリプト）と内容検証（claude -p）の2段階で検証します。failが1つでもあればNGです。NGはOKになるまで修正するか、修正方針をユーザーに相談します。

**構造チェック（スクリプト、17項目）**

| # | チェック内容 |
|---|---|
| S1 | JSONとしてパースできる |
| S2 | 必須フィールドが存在する（id, title, official_doc_urls, index, sections） |
| S3 | index[].id が全て sections のキーに存在する |
| S4 | sections のキーが全て index[].id に存在する |
| S5 | index[].id がケバブケースに適合する |
| S6 | index[].hints が空配列でない |
| S7 | sections の値が空文字列でない |
| S8 | id フィールドがファイル名と一致する |
| S9 | セクション数がソースの見出し数と整合する |
| S10 | h3分割が2000文字ルールに基づいて妥当である（RSTのみ） |
| S11 | 公式URLが有効である（HTTP 200、タイトル一致、日本語ページ確認） |
| S12 | セクション本文中の技術用語（クラス名、アノテーション等）がhintsに含まれている |
| S13 | セクション本文が50文字以上ある |
| S14 | クロスリファレンス（「〜を参照」）の参照先が実在する |
| S15 | assets参照（画像等）のファイルが実在する |
| S16 | index.toonの行数と知識ファイル数が一致する |
| S17 | index.toonのprocessing_patterns値が有効値のみで構成されている |

**内容検証（claude -p、4観点）**

生成時のバイアスを排除するため、生成とは別のclaude -pセッションで実行します。

| 観点 | 内容 |
|---|---|
| 情報の漏れ | 仕様、注意点、コード例などがソースにあるのに知識ファイルにない |
| 情報の捏造 | ソースにない情報が知識ファイルに含まれている |
| セクション分割の妥当性 | 見出しレベルに基づく分割ルールの逸脱 |
| 検索ヒントの品質 | クラス名やプロパティ名の不足 |

## 品質担保の仕組み

このツールは3つの仕組みで品質を担保しています。

**ルールベースの制約**: Step 3のプロンプトに抽出ルール・セクション分割ルール・MD記述ルール・パターン別構成ガイドを全量埋め込み、AIの判断余地を最小化しています。出力はJSON Schemaで構造が定義されており、自由形式のテキストではありません。

**生成と検証の分離**: Step 3で知識ファイルを生成するAIと、Step 6で内容を検証するAIは別セッションです。同一セッションでは自分の出力に対するバイアスが生じるため、検証は必ず独立したセッションで行います。

**機械的チェック（17項目）とAIチェックの組み合わせ**: セクション数・URL有効性・hints網羅性・参照先の実在確認など、スクリプトで確実に検出できるものは全て機械的にチェックします。情報の漏れ・捏造のような意味的な判断が必要なものはAIが担当します。全項目failなしになるまで修正を繰り返します。

## 使い方

### 前提

- Python 3、uv、venvがセットアップ済みであること（`setup.sh` で構築）
- claude CLIが使用可能であること

### 基本的な実行

```bash
# Nablarch 6の知識ファイルを全ステップで生成
python tools/knowledge-creator/run.py --version 6

# Nablarch 5の知識ファイルを生成
python tools/knowledge-creator/run.py --version 5

# v6とv5を一括生成
python tools/knowledge-creator/run.py --version all
```

### オプション

```bash
# 並行数を変更（デフォルト: 4）
python tools/knowledge-creator/run.py --version 6 --concurrency 8

# 特定のステップだけ実行
python tools/knowledge-creator/run.py --version 6 --step 3

# 処理対象の確認のみ（ファイル出力なし）
python tools/knowledge-creator/run.py --version 6 --dry-run

# リポジトリルートを明示的に指定
python tools/knowledge-creator/run.py --version 6 --repo /path/to/repo
```

| 引数 | 必須 | デフォルト | 説明 |
|---|---|---|---|
| `--version` | ○ | — | 対象バージョン。`6`, `5`, `all` |
| `--step` | × | 全実行 | 特定ステップのみ実行（1〜6） |
| `--concurrency` | × | 4 | claude -pの並行起動数 |
| `--repo` | × | カレントディレクトリ | リポジトリルートパス |
| `--dry-run` | × | false | 処理対象の確認のみ |

### 中断と再開

処理が途中で中断しても、同じコマンドで再実行すれば中断箇所から再開します。Step 3は生成済みの知識ファイルをスキップするため、完了分の再処理は発生しません。

### 差分更新（2回目以降）

ソースファイルの追加・更新・削除を自動で検知します。

- **追加**: 新しいソースファイルに対応する知識ファイルを生成
- **更新**: ソースの更新日時が知識ファイルより新しい場合、再生成
- **削除**: ソースが消えたファイルの知識ファイル・MD・assetsを削除

### 検証失敗時の対処

Step 6でfailとなったファイルは、該当の知識ファイルを削除してからStep 3を再実行します。

```bash
# 例: some-handler.json がfailした場合
rm .claude/skills/nabledge-6/knowledge/component/handlers/some-handler.json

# Step 3のみ再実行（削除したファイルだけが再生成される）
python tools/knowledge-creator/run.py --version 6 --step 3
```

### ログの確認

ログはバージョンごとのサブディレクトリに、ファイル単位で出力されます。

```
tools/knowledge-creator/logs/v{version}/
  sources.json                      # ソースファイル一覧
  classified.json                   # 分類結果
  generate/                         # Step 3: 生成ログ（ファイル単位）
    {file_id}.json                  # 成功/エラーの詳細
  classify-patterns/                # Step 4: パターン分類ログ
    {file_id}.json
  validate/                         # Step 6: 検証ログ（ファイル単位）
    structure/{file_id}.json        # 構造チェック結果
    content/{file_id}.json          # 内容検証結果
  summary.json                      # 全体サマリー
```

特定のファイルの結果を確認したい場合は、該当する `{file_id}.json` を直接参照できます。全体の状況は `summary.json` で確認できます。

## 出力先

| 出力物 | パス |
|---|---|
| 知識ファイル（JSON） | `.claude/skills/nabledge-{6,5}/knowledge/{type}/{category}/` |
| 添付ファイル | `.claude/skills/nabledge-{6,5}/knowledge/{type}/{category}/assets/{id}/` |
| インデックス | `.claude/skills/nabledge-{6,5}/knowledge/index.toon` |
| 閲覧用Markdown | `.claude/skills/nabledge-{6,5}/docs/{type}/{category}/` |
