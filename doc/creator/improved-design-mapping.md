# nabledge-creator 設計書：mapping ワークフロー

この設計書はworkflows/mapping.mdとworkflows/verify-mapping.mdの内容を定義する。エージェントへの命令として記述する。

mappingワークフローは2つのセッションに分かれる。

| セッション | ワークフロー | 目的 |
|---|---|---|
| 生成セッション | workflows/mapping.md | マッピングファイルの生成（Step 1-5） |
| 検証セッション | workflows/verify-mapping.md | 分類結果の検証（別セッション） |

別セッションにする理由：generate-mapping.pyのパスルールで分類した結果を、同じコンテキストでチェックしてもパスルールの盲点は見つけられない。検証セッションでrstの中身を読んで分類の正しさを確認する。

関連する参照ファイル：
- references/classification.md
- references/target-path.md
- references/content-judgement.md

関連するスクリプト：
- scripts/generate-mapping.py
- scripts/validate-mapping.py
- scripts/export-excel.py
- scripts/generate-mapping-checklist.py（検証セッション用）

---

# workflows/mapping.md

公式ドキュメントを走査してマッピングファイルを生成するワークフロー。

## ワークフロー手順

### Step 1: マッピング生成

以下のコマンドを実行せよ。

```bash
python scripts/generate-mapping.py v6
```

出力：`references/mapping/mapping-v6.md`

終了コード1（review itemsあり）の場合、Step 4で解決する。終了コード2はスクリプトのバグなので修正して再実行せよ。

### Step 2: 検証

以下のコマンドを実行せよ。

```bash
python scripts/validate-mapping.py references/mapping/mapping-v6.md
```

全チェックがpassすれば次に進む。failした場合、エラー内容を読んでgenerate-mapping.pyのルールを修正し、Step 1から再実行せよ。

### Step 3: Excel出力

以下のコマンドを実行せよ。

```bash
python scripts/export-excel.py references/mapping/mapping-v6.md
```

### Step 4: レビュー項目の解決

Step 1でreview itemsが報告された場合のみ実行する。

1. 対象ファイルの周辺コンテキスト（同ディレクトリの他ファイル、参照元の`:ref:`や`toctree`）を読め
2. 判断できたら、`references/classification.md`のルールに追記してgenerate-mapping.pyに反映し、Step 1から再実行せよ
3. どうしても判断できない場合のみ、理由を添えて人間に報告せよ

### Step 5: チェックリスト生成

以下のコマンドを実行せよ。

```bash
python scripts/generate-mapping-checklist.py references/mapping/mapping-v6.md --source-dir .lw/nab-official/v6/ --output references/mapping/mapping-v6.checklist.md
```

生成セッションはここで完了。チェックリストを検証セッションに渡す。

---

# workflows/verify-mapping.md（検証セッション）

生成セッションとは**別のセッション**で実行する。

### 呼び出し

```
nabledge-creator verify-mapping-6
```

### Step VM1: チェックリストとマッピングを読む

以下のファイルを読め。

```
references/mapping/mapping-v6.checklist.md   # チェックリスト
references/mapping/mapping-v6.md             # マッピング
references/classification.md                 # 分類ルール
```

### Step VM2: 分類チェック（サンプリング）

チェックリストには、全マッピング行からサンプリングされた行が分類チェック対象として列挙されている。各行について以下を行え。

1. マッピングのSource Pathからrstファイルを読め（冒頭50行 + toctree + 参照先）
2. rstの内容が、マッピングのType / Category ID / Processing Patternと整合するか確認せよ
3. `references/classification.md`のどのルールでマッチしたかを特定せよ
4. 整合する → ✓ / 矛盾する → ✗（正しい分類を記録）

### Step VM3: Target Pathチェック（サンプリング）

チェックリストのTarget Path検証対象について以下を確認せよ。

1. Target Pathの先頭ディレクトリがTypeと一致するか
2. ファイル名がSource Pathのファイル名から正しく変換されているか（`_`→`-`、`.rst`→`.md`）
3. componentカテゴリのサブディレクトリが保持されているか

### Step VM4: 修正の適用

✗が1つでもあれば、classification.mdのルールを修正し、生成セッションのStep 1から再実行せよ。

### Step VM5: 検証結果の出力

チェックリストを更新して結果を記録せよ。全項目が✓になったら検証完了。

## 入出力

**入力（ソースディレクトリ）**：
```
.lw/nab-official/v6/nablarch-document/en/
.lw/nab-official/v6/nablarch-document/ja/
.lw/nab-official/v6/nablarch-system-development-guide/
```

**出力**：
```
references/mapping/mapping-v6.md       # Markdownテーブル
references/mapping/mapping-v6.xlsx     # Excelテーブル
```

**出力フォーマット例**：

```markdown
# Nablarch v6 Documentation Mapping

**Generated**: 2026-02-20
**Total Files**: 302

| Source Path | Title | Title (ja) | Official URL | Type | Category ID | Processing Pattern | Target Path |
|---|---|---|---|---|---|---|---|
| application_framework/.../data_read_handler.rst | Data Read Handler | データリードハンドラ | [🔗](https://nablarch.github.io/docs/6u3/doc/.../data_read_handler.html) | component | handlers | nablarch-batch | component/handlers/standalone/data-read-handler.md |
| application_framework/.../universal_dao.rst | Universal DAO | ユニバーサルDAO | [🔗](https://nablarch.github.io/docs/6u3/doc/.../universal_dao.html) | component | libraries |  | component/libraries/database/universal-dao.md |
```

## 参照ファイル

各ファイルはスクリプトが内部で参照する。レビュー項目の解決（Step 4）時にエージェントも直接読む。

| ファイル | 内容 | 読むタイミング |
|---|---|---|
| `references/classification.md` | パスパターン → Type/Category/PP の分類ルール | Step 4で分類を判断するとき |
| `references/target-path.md` | Source Path → Target Path の変換ルール | Step 4でTarget Pathを確認するとき |
| `references/content-judgement.md` | コンテンツを読んで分類を判断するルール | Step 4でreview itemを解決するとき |

---

# scripts/generate-mapping.py 仕様

## コマンドライン

```
python scripts/generate-mapping.py v6 [--output PATH]
```

## 処理パイプライン

```
enumerate() → classify() → verify() → enrich() → output()
```

### enumerate()

**nablarch-document**（ベース：`.lw/nab-official/v6/nablarch-document/en/`）：
- 対象：`**/*.rst`、`**/*.md`
- 除外：ルート`README.md`、`.textlint/`配下

**nablarch-system-development-guide**（ベース：`.lw/nab-official/v6/nablarch-system-development-guide/`）：
- 対象：
  - `en/Nablarch-system-development-guide/docs/nablarch-patterns/Asynchronous_operation_in_Nablarch.md`
  - `en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_anti-pattern.md`
  - `en/Nablarch-system-development-guide/docs/nablarch-patterns/Nablarch_batch_processing_pattern.md`
  - `Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx`

### classify()

`references/classification.md`のルールで各ファイルに分類仮説を立てる。

信頼度（confidence）：
- `confirmed`：パスルールで明確に決まる
- `needs_content`：パスルールだけでは不十分
- `unknown`：パスルールに該当なし

### verify()

`references/content-judgement.md`のルールで**全ファイル**のコンテンツを読んで仮説を検証する。

全ファイルを読む理由：パスベースの分類精度は約86%。残り約14%はどのファイルか事前にわからないため、全件検証が必要。

信頼度の遷移：
- `confirmed` + 矛盾なし → そのまま
- `confirmed` + 矛盾あり → `review`に降格
- `needs_content` + 判断可 → `confirmed`に昇格
- `needs_content` + 判断不可 → `review`
- `unknown` + 判断可 → `confirmed`に昇格
- `unknown` + 判断不可 → `review`

`review`項目は標準出力にJSON形式で報告する：

```json
{"review_items": [
  {"source_path": "path/to/file.rst", "hypothesis": "component/handlers", "issue": "PP undetermined"}
]}
```

### enrich()

confirmed項目にタイトルとURLを付与する。

**英語タイトル**：
- rst：先頭20行の`===`/`---`アンダーライン付きタイトル
- md：最初の`# `見出し
- xlsx：ファイル名

**日本語タイトル**：
- nablarch-document：`en/`→`ja/`に置換したパスから抽出
  - 例外：`duplicate_form_submission.rst` → ja版は`double_transmission.rst`
- system-development-guide：変換テーブル：

| 英語 | 日本語 |
|---|---|
| `Asynchronous_operation_in_Nablarch.md` | `Nablarchでの非同期処理.md` |
| `Nablarch_anti-pattern.md` | `Nablarchアンチパターン.md` |
| `Nablarch_batch_processing_pattern.md` | `Nablarchバッチ処理パターン.md` |

**Official URL**：

| ソース | パターン |
|---|---|
| nablarch-document | `https://nablarch.github.io/docs/6u3/doc/{path}.html` |
| system-development-guide | `https://github.com/Fintan-contents/nablarch-system-development-guide/blob/main/Nablarchシステム開発ガイド/docs/nablarch-patterns/{日本語ファイル名}` |
| Sample_Project | `https://github.com/Fintan-contents/nablarch-system-development-guide/blob/main/{ソースパス}` |

フォーマット：`[🔗](URL)`

### output()

mapping-v6.mdを出力。行はSource Pathのアルファベット順。

## 終了コード

- 0：完了（review itemsなし）
- 1：完了（review itemsあり）
- 2：エラー

---

# scripts/validate-mapping.py 仕様

## コマンドライン

```
python scripts/validate-mapping.py PATH [--source-dir DIR]
```

## 検証項目

| カテゴリ | チェック内容 |
|---|---|
| 構造 | 全行8カラム、必須カラム非空、PP空を許容 |
| タクソノミー | Type/Category IDが有効な組み合わせか |
| ソースファイル | 英語ファイル存在、日本語ファイル存在（警告） |
| Target Path | Type/Category一致、サブディレクトリ保持、重複なし |
| URL | `[🔗](https://...)`形式、バージョン番号正確 |
| 整合性 | PP=Category ID（processing-pattern時）、common→PP空 |

**タクソノミーの有効値**：

| Type | 有効なCategory ID |
|---|---|
| processing-pattern | nablarch-batch, jakarta-batch, restful-web-service, http-messaging, web-application, mom-messaging, db-messaging |
| component | handlers, libraries, adapters |
| development-tools | testing-framework, toolbox, java-static-analysis |
| setup | blank-project, configuration, setting-guide, cloud-native |
| guide | nablarch-patterns, business-samples |
| check | security-check |
| about | about-nablarch, migration, release-notes |

## 出力例

```
=== Validation Report ===
Total rows: 302

Structure:     PASS (302/302)
Taxonomy:      PASS (302/302)
Source files:  PASS (302/302 en, 300/302 ja)
Target paths:  PASS (302 unique, 0 duplicates)
URL format:    PASS (302/302)
Consistency:   PASS (302/302)

Result: ALL PASSED
```

## 終了コード

- 0：全pass
- 1：warningのみ
- 2：エラー

---

# scripts/export-excel.py 仕様

## コマンドライン

```
python scripts/export-excel.py PATH [--output PATH]
```

## 出力仕様

- シート名：`Mapping v6`
- カラム：mapping-v6.mdと同じ8カラム
- Official URL列：URLを抽出してハイパーリンク設定、表示テキスト`🔗`
- ヘッダ行：太字、フィルター有効、固定
- カラム幅：自動調整

## 終了コード

- 0：正常
- 1：エラー

---

# scripts/generate-mapping-checklist.py 仕様

マッピングファイルから検証セッション用のチェックリストを生成する。

## コマンドライン

```
python scripts/generate-mapping-checklist.py MAPPING_PATH --source-dir DIR [--output PATH] [--sample-rate N]
```

- `MAPPING_PATH`：マッピングファイル
- `--source-dir`：rstソースディレクトリ
- `--output`：チェックリスト出力先（デフォルト：`{MAPPING_PATH}.checklist.md`）
- `--sample-rate`：サンプリング率。N行に1行をチェック対象にする（デフォルト：3）

全行チェックは302行で非現実的なので、サンプリングする。ただし以下は必ず含める：
- confidence=`needs_content`だった行（パスルールだけで決まらなかった行）
- Processing Patternが空でない行のうち、PP≠Category IDの行
- handlers/standalone/配下（PP判断にコンテンツ確認が必要な行）

## 出力例

```markdown
# チェックリスト: mapping-v6

**マッピング行数**: 302
**チェック対象**: 45行（サンプリング + 必須チェック行）

---

## 分類チェック

| # | Source Path | Type | Category | PP | チェック理由 | 判定 |
|---|---|---|---|---|---|---|
| 1 | .../data_read_handler.rst | component | handlers | nablarch-batch | standalone配下 | |
| 2 | .../loop_handler.rst | processing-pattern | nablarch-batch | nablarch-batch | Typeオーバーライド | |
| 3 | .../universal_dao.rst | component | libraries | | サンプリング | |
| ... | | | | | | |

各行について：rstの冒頭50行を読み、分類が正しいか確認せよ。

---

## Target Pathチェック

| # | Source Path | Target Path | チェック内容 | 判定 |
|---|---|---|---|---|
| 1 | .../data_read_handler.rst | component/handlers/standalone/data-read-handler.md | ファイル名変換、サブディレクトリ | |
| 2 | .../batch/nablarch_batch/index.rst | processing-pattern/nablarch-batch/... | index.rst命名ルール | |
| ... | | | | |
```

## 終了コード

- 0：正常
- 1：エラー

---

# references/classification.md

（内容は前回版と同じ。パスパターンルール、Processing Patternルール。）

---

# references/target-path.md

（内容は前回版と同じ。ファイル名変換、サブディレクトリ、index.rst命名。）

---

# references/content-judgement.md

（内容は前回版と同じ。index.rst採用/除外、PP判断、Typeオーバーライド。）
