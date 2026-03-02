# knowledge-creator 詳細設計書

## 目的

Nablarchの公式情報（RST/MD/Excel）をAI Readyな知識ファイル（JSON）に変換するツール。この設計書だけを見てエージェントが実装を完了できることを目標とする。

---

## ファイル構成

```
tools/knowledge-creator/
  README.md                 # ユーザー向けドキュメント（処理フロー、使い方）
  run.py                    # メインスクリプト（エントリポイント）
  steps/
    1_list_sources.py       # ソースファイル一覧の取得
    2_classify.py           # Type/Category分類
    3_generate.py           # 知識ファイル生成（claude -p使用）
    4_build_index.py        # index.toon生成（claude -p使用）
    5_generate_docs.py      # 閲覧用MD生成
    6_validate.py           # 検証（claude -p使用）
  prompts/                  # claude -pに渡すプロンプトテンプレート
    generate.md             # Step 3用プロンプト
    classify_patterns.md    # Step 4用プロンプト（処理パターン判定）
    validate.md             # Step 6用プロンプト（内容検証）
  logs/                     # 作業ログ（バージョン別、ファイル単位）
    v{version}/
      sources.json          # Step 1出力
      classified.json       # Step 2出力
      generate/             # Step 3: ファイル単位の生成ログ
      classify-patterns/    # Step 4: ファイル単位の分類ログ
      validate/             # Step 6: ファイル単位の検証ログ
        structure/
        content/
      summary.json          # 全体サマリー
```

---

## 前提条件

- Python3、uv、venvはsetup.shでセットアップ済み
- 並行処理は `concurrent.futures`（標準ライブラリ）で `claude -p` を並行起動
- モデル: Sonnet 4.5（全ステップ共通）
- リポジトリルートを `$REPO` とする

### claude -p の呼び出し規約

プロンプトは長文（数千文字〜）になるため、コマンドライン引数ではなくstdin経由で渡す。

```python
import subprocess

def run_claude(prompt: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """claude -p をstdin経由で実行する"""
    return subprocess.run(
        ["claude", "-p", "--model", "claude-sonnet-4-5-20250929"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
```

- `claude -p` はstdinからプロンプトを読み取り、stdoutに応答を出力する
- `--model` でモデルを明示指定する
- `--output-format` オプションは使用しない（claude -pの標準出力をそのままパースする）
- タイムアウトはデフォルト300秒（Step 3）、Step 4・6は120秒

---

## run.py 設計

### コマンドラインインターフェース

```bash
# 全ステップ実行（デフォルト）
python run.py --version 6

# 特定ステップのみ実行
python run.py --version 6 --step 3

# 並行数指定（デフォルト: 4）
python run.py --version 6 --concurrency 8

# 全ステップ一括（v6 + v5）
python run.py --version all
```

| 引数 | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `--version` | str | ○ | — | `6`, `5`, `all` |
| `--step` | int | × | なし（全実行） | 1〜6 の特定ステップのみ実行 |
| `--concurrency` | int | × | 4 | claude -p の並行起動数 |
| `--repo` | str | × | カレントディレクトリ | リポジトリルートパス |
| `--dry-run` | flag | × | false | 実際のファイル出力をせず、処理対象のみ表示 |

### 全体フロー制御

差分処理セクション（後述）に統合した `main()` を参照。ここでは簡易版を示す:

```python
def main(version, step, concurrency, repo):
    versions = ["6", "5"] if version == "all" else [version]
    for v in versions:
        ctx = Context(version=v, repo=repo, concurrency=concurrency)
        # 詳細は「差分処理 > run.pyにおける初回/2回目以降の統合」を参照
        run_pipeline(ctx, step)
```

### Context オブジェクト

各ステップ間で共有するデータ。ファイルで永続化する。

```python
@dataclass
class Context:
    version: str          # "6" or "5"
    repo: str             # リポジトリルートパス
    concurrency: int      # 並行数
    
    @property
    def source_list_path(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/logs/v{self.version}/sources.json"
    
    @property
    def classified_list_path(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/logs/v{self.version}/classified.json"
    
    @property
    def knowledge_dir(self) -> str:
        return f"{self.repo}/.claude/skills/nabledge-{self.version}/knowledge"
    
    @property
    def docs_dir(self) -> str:
        return f"{self.repo}/.claude/skills/nabledge-{self.version}/docs"
    
    @property
    def index_path(self) -> str:
        return f"{self.knowledge_dir}/index.toon"
```

---

## Step 1: ソースファイル一覧の取得

### 概要

| 項目 | 内容 |
|---|---|
| 処理方式 | Pythonスクリプト（機械的） |
| 入力 | ソースディレクトリ |
| 出力 | `logs/v{version}/sources.json` |

### 入力パス

| ソース | 形式 | パス |
|---|---|---|
| 公式解説書 | RST | `$REPO/.lw/nab-official/v{version}/nablarch-document/ja/` |
| パターン集 | MD | `$REPO/.lw/nab-official/v6/nablarch-system-development-guide/Nablarchシステム開発ガイド/docs/nablarch-patterns/*.md` |
| セキュリティ対応表 | Excel | `$REPO/.lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx` |

補足:
- パターン集・セキュリティ対応表は最新版のみ存在（v6配下）。v5の知識ファイル生成時もv6のものを参照する
- パターン集の対象ファイル（3件）: `Nablarchバッチ処理パターン.md`、`Nablarchでの非同期処理.md`、`Nablarchアンチパターン.md`

### 除外ルール

| 除外対象 | 理由 |
|---|---|
| `index.rst` | 目次ファイル（内容なし） |
| `README.md` | パターン集ディレクトリの説明ファイル |
| `_` で始まるディレクトリ | RST設定ディレクトリ（`_static`, `_templates` 等） |
| 英語ディレクトリ（`en/`） | 日本語がオリジナル、英語は翻訳のため参照不要 |

### 出力スキーマ

```json
{
  "version": "6",
  "generated_at": "2025-01-01T00:00:00Z",
  "sources": [
    {
      "path": ".lw/nab-official/v6/nablarch-document/ja/application_framework/...",
      "format": "rst",
      "filename": "db_connection_management_handler.rst"
    },
    {
      "path": ".lw/nab-official/v6/nablarch-system-development-guide/...",
      "format": "md",
      "filename": "Nablarchバッチ処理パターン.md"
    },
    {
      "path": ".lw/nab-official/v6/nablarch-system-development-guide/...",
      "format": "xlsx",
      "filename": "Nablarch機能のセキュリティ対応表.xlsx"
    }
  ]
}
```

### 処理ロジック

```python
def list_sources(ctx: Context) -> list[dict]:
    sources = []
    
    # 1. 公式解説書（RST）
    rst_base = f"{ctx.repo}/.lw/nab-official/v{ctx.version}/nablarch-document/ja/"
    for root, dirs, files in os.walk(rst_base):
        # _で始まるディレクトリを除外
        dirs[:] = [d for d in dirs if not d.startswith("_")]
        for f in files:
            if f.endswith(".rst") and f != "index.rst":
                sources.append({
                    "path": os.path.relpath(os.path.join(root, f), ctx.repo),
                    "format": "rst",
                    "filename": f
                })
    
    # 2. パターン集（MD）— 常にv6配下を参照
    pattern_dir = f"{ctx.repo}/.lw/nab-official/v6/nablarch-system-development-guide/Nablarchシステム開発ガイド/docs/nablarch-patterns/"
    target_files = [
        "Nablarchバッチ処理パターン.md",
        "Nablarchでの非同期処理.md",
        "Nablarchアンチパターン.md"
    ]
    for f in target_files:
        filepath = os.path.join(pattern_dir, f)
        if os.path.exists(filepath):
            sources.append({
                "path": os.path.relpath(filepath, ctx.repo),
                "format": "md",
                "filename": f
            })
    
    # 3. セキュリティ対応表（Excel）— 常にv6配下を参照
    xlsx_path = f"{ctx.repo}/.lw/nab-official/v6/nablarch-system-development-guide/Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx"
    if os.path.exists(xlsx_path):
        sources.append({
            "path": os.path.relpath(xlsx_path, ctx.repo),
            "format": "xlsx",
            "filename": "Nablarch機能のセキュリティ対応表.xlsx"
        })
    
    return sources
```

---

## Step 2: Type/Category 分類

### 概要

| 項目 | 内容 |
|---|---|
| 処理方式 | Pythonスクリプト（機械的） |
| 入力 | `logs/v{version}/sources.json` |
| 出力 | `logs/v{version}/classified.json` |

### マッピングテーブル

ソースファイルの相対パス（`nablarch-document/ja/` 以降）からType/Categoryを機械的に決定する。

#### RST: パス → Type/Category マッピング

パスのディレクトリ構造に基づくマッピング。上から順にマッチングし、最初にマッチした行を適用する。

```python
RST_MAPPING = [
    # processing-pattern
    ("application_framework/application_framework/batch/nablarch_batch", "processing-pattern", "nablarch-batch"),
    ("application_framework/application_framework/batch/jsr352", "processing-pattern", "jakarta-batch"),
    ("application_framework/application_framework/web_service/rest", "processing-pattern", "restful-web-service"),
    ("application_framework/application_framework/web_service/http_messaging", "processing-pattern", "http-messaging"),
    ("application_framework/application_framework/web/", "processing-pattern", "web-application"),
    ("application_framework/application_framework/messaging/mom_messaging", "processing-pattern", "mom-messaging"),
    ("application_framework/application_framework/messaging/db_messaging", "processing-pattern", "db-messaging"),
    
    # component - handlers
    ("application_framework/application_framework/handlers/", "component", "handlers"),
    ("application_framework/application_framework/batch/jBatchHandler", "component", "handlers"),
    
    # component - libraries
    ("application_framework/application_framework/libraries/", "component", "libraries"),
    
    # component - adapters
    ("application_framework/adaptors/", "component", "adapters"),
    
    # development-tools
    ("development_tools/testing_framework/", "development-tools", "testing-framework"),
    ("development_tools/toolbox/", "development-tools", "toolbox"),
    ("development_tools/java_static_analysis/", "development-tools", "java-static-analysis"),
    
    # setup
    ("application_framework/application_framework/blank_project/", "setup", "blank-project"),
    ("application_framework/application_framework/configuration/", "setup", "configuration"),
    ("application_framework/setting_guide/", "setup", "setting-guide"),
    ("application_framework/application_framework/cloud_native/", "setup", "cloud-native"),
    
    # about
    ("about_nablarch/", "about", "about-nablarch"),
    ("application_framework/application_framework/nablarch_architecture/", "about", "about-nablarch"),
    ("migration/", "about", "migration"),
    ("release_notes/", "about", "release-notes"),
]
```

#### MD（パターン集）→ Type/Category マッピング

```python
MD_MAPPING = {
    "Nablarchバッチ処理パターン.md": ("guide", "nablarch-patterns"),
    "Nablarchでの非同期処理.md": ("guide", "nablarch-patterns"),
    "Nablarchアンチパターン.md": ("guide", "nablarch-patterns"),
}
```

#### Excel（セキュリティ対応表）→ Type/Category マッピング

```python
XLSX_MAPPING = {
    "Nablarch機能のセキュリティ対応表.xlsx": ("check", "security-check"),
}
```

### 知識ファイルIDの生成ルール

ソースファイル名から生成する。

```python
def generate_id(filename: str, format: str) -> str:
    """
    RST: 拡張子を除去し、そのまま使う（すでにケバブケース）
    MD:  日本語ファイル名をそのままIDとして使う（拡張子除去）
    Excel: 固定ID 'security-check'
    """
    if format == "rst":
        return filename.replace(".rst", "")
    elif format == "md":
        return filename.replace(".md", "")
    elif format == "xlsx":
        return "security-check"
```

### 出力パスの計算

```python
def output_path(knowledge_dir: str, type: str, category: str, file_id: str) -> str:
    return f"{knowledge_dir}/{type}/{category}/{file_id}.json"
```

### 出力スキーマ

```json
{
  "version": "6",
  "generated_at": "2025-01-01T00:00:00Z",
  "files": [
    {
      "source_path": ".lw/nab-official/v6/nablarch-document/ja/application_framework/...",
      "format": "rst",
      "filename": "db_connection_management_handler.rst",
      "type": "component",
      "category": "handlers",
      "id": "db_connection_management_handler",
      "output_path": "component/handlers/db_connection_management_handler.json",
      "assets_dir": "component/handlers/assets/db_connection_management_handler/"
    }
  ]
}
```

### エラーハンドリング

- マッピングにマッチしないパスが見つかった場合: エラーログに記録し、処理を続行。最後にマッチしなかったファイル一覧を出力する。
- 対応策: マッピングテーブルを更新して再実行する。

---

## Step 3: 知識ファイル生成

### 概要

| 項目 | 内容 |
|---|---|
| 処理方式 | スクリプト（assets事前抽出）+ claude -p（知識ファイル生成） |
| 並行単位 | 1ソースファイル = 1 claude -pセッション |
| 入力 | 1つのソースファイル + 分類情報 |
| 出力 | 1つの知識ファイルJSON + assets（画像等） |
| 出力先 | `$REPO/.claude/skills/nabledge-{version}/knowledge/{type}/{category}/` |

### assets取り込みの責任分界

画像・添付ファイルの取り込みはスクリプト側が担当する。claude -pはファイルシステム操作を行わない。

```
スクリプト側の責任:
1. ソースファイルと同階層の画像ファイル（.png, .jpg, .gif, .svg）を検出
2. RSTの image/figure ディレクティブから参照パスを抽出
3. 対象ファイルを assets/{知識ファイルID}/ にコピー
4. コピー済み画像の一覧（ファイル名 → assetsパス）をプロンプトに含める

claude -p側の責任:
1. スクリプトから渡された画像一覧を元に、MD内で適切にパス参照する
2. テキスト代替が可能な画像はテキスト代替を優先する
3. テキスト代替が困難な画像のみ ![説明](assets/...) で参照する
```

#### 画像抽出スクリプト

```python
def extract_assets(source_path: str, source_content: str, source_format: str,
                   assets_dir: str) -> list[dict]:
    """ソースから参照される画像・添付ファイルを抽出しassetsにコピーする"""
    assets = []
    source_dir = os.path.dirname(source_path)
    
    if source_format == "rst":
        # image/figureディレクティブから参照パスを抽出
        image_refs = re.findall(
            r'\.\.\s+(?:image|figure)::\s+(.+)', source_content
        )
        for ref in image_refs:
            ref = ref.strip()
            src = os.path.join(source_dir, ref)
            if os.path.exists(src):
                os.makedirs(assets_dir, exist_ok=True)
                dst = os.path.join(assets_dir, os.path.basename(ref))
                shutil.copy2(src, dst)
                assets.append({
                    "original": ref,
                    "assets_path": f"assets/{os.path.basename(assets_dir)}/{os.path.basename(ref)}"
                })
    
    # Office等の添付ファイル（テンプレートExcel等）
    if source_format == "rst":
        download_refs = re.findall(r':download:`[^<]*<([^>]+)>`', source_content)
        for ref in download_refs:
            ref = ref.strip()
            src = os.path.join(source_dir, ref)
            if os.path.exists(src):
                os.makedirs(assets_dir, exist_ok=True)
                dst = os.path.join(assets_dir, os.path.basename(ref))
                shutil.copy2(src, dst)
                assets.append({
                    "original": ref,
                    "assets_path": f"assets/{os.path.basename(assets_dir)}/{os.path.basename(ref)}"
                })
    
    return assets
```

claude -pに渡すプロンプトには、抽出結果を以下の形式で追加する:

```
## 画像・添付ファイル一覧

このソースファイルから以下の画像・添付ファイルが抽出済みです。
テキスト代替が困難な場合のみ、assets_pathを使って参照してください。

| ソース内パス | assetsパス |
|---|---|
| _images/flow.png | assets/db-connection-management-handler/flow.png |
```

抽出された画像がない場合はこのセクションを省略する。

### 処理フロー

```python
def run(ctx: Context):
    classified = load_json(ctx.classified_list_path)
    
    with ThreadPoolExecutor(max_workers=ctx.concurrency) as executor:
        futures = []
        for file_info in classified["files"]:
            output_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
            # 中断再開: 生成済みファイルはスキップ
            if os.path.exists(output_path):
                log_skip(file_info["id"])
                continue
            futures.append(executor.submit(generate_one, ctx, file_info))
        
        for future in as_completed(futures):
            result = future.result()
            if result["status"] == "error":
                log_error(result)
```

### 単一ファイルの生成処理

```python
def generate_one(ctx: Context, file_info: dict) -> dict:
    source_content = read_file(f"{ctx.repo}/{file_info['source_path']}")
    prompt = build_prompt(file_info, source_content)
    output_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
    log_path = f"{ctx.repo}/tools/knowledge-creator/logs/v{ctx.version}/generate/{file_info['id']}.json"
    
    # ディレクトリ作成
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    started_at = datetime.utcnow().isoformat() + "Z"
    
    # claude -p 実行（stdin経由）
    try:
        result = run_claude(prompt, timeout=300)
    except subprocess.TimeoutExpired:
        log_entry = {
            "file_id": file_info["id"], "status": "error",
            "started_at": started_at,
            "finished_at": datetime.utcnow().isoformat() + "Z",
            "error": "timeout", "raw_output": ""
        }
        write_json(log_path, log_entry)
        return {"status": "error", "id": file_info["id"], "error": "timeout"}
    
    if result.returncode != 0:
        log_entry = {
            "file_id": file_info["id"], "status": "error",
            "started_at": started_at,
            "finished_at": datetime.utcnow().isoformat() + "Z",
            "error": result.stderr, "raw_output": result.stdout
        }
        write_json(log_path, log_entry)
        return {"status": "error", "id": file_info["id"], "error": result.stderr}
    
    # 出力JSONの抽出・保存
    try:
        knowledge_json = extract_json(result.stdout)
    except (json.JSONDecodeError, ValueError) as e:
        log_entry = {
            "file_id": file_info["id"], "status": "error",
            "started_at": started_at,
            "finished_at": datetime.utcnow().isoformat() + "Z",
            "error": f"JSON extraction failed: {e}", "raw_output": result.stdout
        }
        write_json(log_path, log_entry)
        return {"status": "error", "id": file_info["id"], "error": str(e)}
    
    write_json(output_path, knowledge_json)
    
    finished_at = datetime.utcnow().isoformat() + "Z"
    log_entry = {
        "file_id": file_info["id"], "status": "ok",
        "started_at": started_at, "finished_at": finished_at,
        "duration_sec": (datetime.fromisoformat(finished_at.rstrip("Z"))
                        - datetime.fromisoformat(started_at.rstrip("Z"))).seconds
    }
    write_json(log_path, log_entry)
    
    return {"status": "ok", "id": file_info["id"]}
```

### claude -p プロンプト（`prompts/generate.md`）

以下がclaude -pに渡すプロンプト全文のテンプレート。`{PLACEHOLDERS}` は実行時に置換する。

````markdown
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
- **例外**: h2配下のテキスト量がおおよそ2000文字を超える場合、h3を分割単位に引き上げる

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

## パターン別セクション構成ガイド

ソースの記載パターンに応じて、以下の推奨構成に従ってセクションを構成してください。あくまで推奨であり、ソースの内容に応じて柔軟に調整できます。

### パターンA: 共通ハンドラ（handlers — 主要部分）

推奨セクション: overview, processing, setup, (機能別)*, constraints

- overview: 冒頭説明、クラス名、モジュール依存
- processing: 処理の流れ（番号付きリスト）
- setup: プロパティ一覧（表）、XML設定例
- constraints: 配置制約、制限事項

### パターンB: インターセプタ（handlers/web_interceptor）

推奨セクション: overview, usage, (応用)*

パターンAとの差異: processing/constraintsがない。usageでアノテーション設定のコード例が中心。

### パターンC: 機能概要 + 使用方法型（libraries — 標準型）

推奨セクション: overview, modules, (設定), (使用方法)*, (機能詳細)*, anti-patterns?, tips?, limitations?, errors?

- overview: 「〜ができる」形式の機能一覧を含む
- anti-patterns, tips, limitations, errors: 箇条書きテキスト

### パターンD: 一覧 + 詳細参照型（libraries — 大きなライブラリ）

パターンCの拡張。セクション数が多い（15〜20）。サブページの内容もセクションとして統合する。

### パターンE, J: 機能比較型

推奨セクション: overview, comparison

- comparison: 機能比較表 + 脚注

### パターンF: アーキテクチャ概要（batch, web_service, messaging）

推奨セクション: overview, (types), architecture, request-path, process-flow, handler-queue

- handler-queue: 最小ハンドラ構成表（ハンドラ × 処理フェーズのマトリクス）

### パターンG: アプリケーション設計

推奨セクション: responsibility, implementation

パターンFと同一ファイルに統合されることが多い。

### パターンH: 機能詳細（batch固有機能等）

セクション構成は機能に応じて自由。パターンF, Gと同一ファイルに統合。

### パターンI: 機能詳細 目次型（web）

推奨セクション: overview, (カテゴリ別)*

各カテゴリセクション: 説明 + 推奨パターン + 参照先リスト。

### パターンK: アダプタ（adaptors）

推奨セクション: overview, setup, configuration, usage, notes?, limitations?

- overview: 統合対象の外部ライブラリ名を含む
- setup: 依存関係の段階的設定手順

### パターンL: テストガイド（testing_framework）

推奨セクション: overview, (構成要素), (手順・設定)*

- overview: 関連ファイルへの参照を含む
- RSTグリッドテーブルはMDテーブルに変換

### パターンM: 手順ガイド（blank_project）

推奨セクション: overview, (ステップ)*

各ステップにコマンド例（bashコードブロック）とファイル変更例を含む。

### パターンN: コンセプト・概念説明（about_nablarch）

セクション構成は自由。散文形式、コード例なし。

### パターンO: カスタマイズ手順（setting_guide）

推奨セクション: overview, (変更方法)*

パターンMに近い。変更対象ファイルパスとプロパティ書式を含む。

### パターンP: クラウド設定手順（cloud_native）

推奨セクション: overview, dependencies, (設定カテゴリ)*

- overview: 方式選択の説明と採用理由を含む

### パターンQ: パターン集（MD形式）

推奨セクション: overview, (分類軸)*, (詳細)*

MD形式がソース。MDテーブルとURL参照を含む。

---

## 出力形式の指示

以下のJSON形式で出力してください。JSON以外のテキスト（説明文等）は一切含めないでください。

```json
{出力JSONをここに}
```
````

### プロンプトのプレースホルダ

| プレースホルダ | 値の取得元 |
|---|---|
| `{FILE_ID}` | `file_info["id"]` |
| `{FORMAT}` | `file_info["format"]` |
| `{TYPE}` | `file_info["type"]` |
| `{CATEGORY}` | `file_info["category"]` |
| `{OUTPUT_PATH}` | `file_info["output_path"]` |
| `{ASSETS_DIR}` | `file_info["assets_dir"]` |
| `{OFFICIAL_DOC_BASE_URL}` | 下記の計算ロジックで生成 |
| `{SOURCE_CONTENT}` | ソースファイルの全文 |

#### OFFICIAL_DOC_BASE_URL の計算ロジック

```python
def compute_official_url(file_info: dict) -> str:
    """ソースファイル情報から公式ドキュメントURLを生成する"""
    if file_info["format"] == "rst":
        # nablarch-document/ja/ 以降のパスを取得し .rst → .html に変換
        path = file_info["source_path"]
        marker = "nablarch-document/ja/"
        idx = path.find(marker)
        if idx >= 0:
            relative = path[idx + len(marker):]
            relative = relative.replace(".rst", ".html")
            return f"https://nablarch.github.io/docs/LATEST/doc/{relative}"
    elif file_info["format"] in ("md", "xlsx"):
        return "https://fintan.jp/page/252/"
    return ""
```

### エラーハンドリング

| エラー | 対応 |
|---|---|
| claude -p タイムアウト（300秒） | エラーログに記録、リトライしない（手動で再実行） |
| claude -p の出力からJSONが抽出できない | エラーログに記録、出力を `logs/v{version}/generate/{file_id}.json` に保存 |
| JSON Schemaに適合しない出力 | エラーログに記録、出力を `logs/v{version}/generate/{file_id}.json` に保存 |

リトライはrun.py再実行で対応する（生成済みファイルはスキップされるため）。

### JSON抽出ロジック

```python
def extract_json(output: str) -> dict:
    """claude -p の出力からJSONを抽出する"""
    # コードブロック内のJSONを抽出
    match = re.search(r'```json?\s*\n(.*?)\n```', output, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # コードブロックがない場合、出力全体をJSONとしてパース
    return json.loads(output.strip())
```

---

## Step 4: index.toon 生成

### 概要

| 項目 | 内容 |
|---|---|
| 処理方式 | スクリプト + claude -p（processing_patterns判定のみ） |
| 入力 | 生成済み知識ファイル一覧 + 分類済みファイル一覧 |
| 出力 | `$REPO/.claude/skills/nabledge-{version}/knowledge/index.toon` |

### 処理フロー

```
1. 分類済みファイル一覧から全エントリを取得（スクリプト）
2. 各知識ファイルJSONからtitleを取得（スクリプト）
3. processing_patternsの判定（claude -p、並行処理）
4. 結果をマージしてindex.toonを生成（スクリプト）
```

### 処理パターン分類ルール

| 条件 | processing_patterns の値 |
|---|---|
| Typeが `processing-pattern` | Category ID と同じ値（1つ） |
| それ以外 | エージェントが内容を読んで判定。複数はスペース区切り。該当なしは空 |

有効な処理パターン値: `nablarch-batch`, `jakarta-batch`, `restful-web-service`, `http-messaging`, `web-application`, `mom-messaging`, `db-messaging`

### claude -p プロンプト（`prompts/classify_patterns.md`）

processing_patterns判定用のプロンプト。Typeが `processing-pattern` 以外のファイルに対してのみ使用する。

````markdown
あなたはNablarchの処理パターン分類エキスパートです。

## タスク

以下の知識ファイルの内容を読み、関連する処理パターンを判定してください。

## 有効な処理パターン

nablarch-batch, jakarta-batch, restful-web-service, http-messaging, web-application, mom-messaging, db-messaging

## 判定基準

- ファイルの内容が特定の処理パターンに関連する記述を含む場合、そのパターンを割り当てる
- 複数の処理パターンに関連する場合は全て列挙する
- どの処理パターンにも関連しない場合は空（何も返さない）
- 汎用的に使われるライブラリ（例: ユニバーサルDAO）は、実際に言及されている処理パターン全てを割り当てる
- ソースに書かれていない処理パターンを推測で追加しない

## 知識ファイル情報

- ID: `{FILE_ID}`
- Title: `{TITLE}`
- Type: `{TYPE}`
- Category: `{CATEGORY}`

## 知識ファイル内容

```json
{KNOWLEDGE_JSON}
```

## 出力形式

スペース区切りの処理パターン値のみを出力してください。該当なしの場合は空行を出力してください。
テキストの説明は一切不要です。

例:
```
nablarch-batch restful-web-service
```
````

### index.toon フォーマット

```toon
# Nabledge-{VERSION} Knowledge Index

files[{COUNT},]{title,type,category,processing_patterns,path}:
  データベース接続管理ハンドラ, component, handlers, , component/handlers/db-connection-management-handler.json
  Nablarchバッチ（都度起動型・常駐型）, processing-pattern, nablarch-batch, nablarch-batch, processing-pattern/nablarch-batch/nablarch-batch.json
  ユニバーサルDAO, component, libraries, nablarch-batch restful-web-service web-application, component/libraries/universal-dao.json
```

フィールドの区切り: `, `（カンマ+スペース）
各行のインデント: 2スペース

### 生成スクリプトロジック

```python
def build_index(ctx: Context):
    classified = load_json(ctx.classified_list_path)
    entries = []
    
    for file_info in classified["files"]:
        json_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
        
        if not os.path.exists(json_path):
            # 未生成の場合
            entries.append({
                "title": file_info["id"],
                "type": file_info["type"],
                "category": file_info["category"],
                "processing_patterns": "",
                "path": "not yet created"
            })
            continue
        
        knowledge = load_json(json_path)
        title = knowledge["title"]
        
        # processing_patternsの判定
        if file_info["type"] == "processing-pattern":
            patterns = file_info["category"]
        else:
            patterns = classify_patterns_with_claude(ctx, file_info, knowledge)
        
        entries.append({
            "title": title,
            "type": file_info["type"],
            "category": file_info["category"],
            "processing_patterns": patterns,
            "path": file_info["output_path"]
        })
    
    # TOON形式で出力
    write_toon(ctx.index_path, entries, ctx.version)


def write_toon(index_path: str, entries: list[dict], version: str):
    """index.toonをTOON形式で出力する。
    
    エスケープルール:
    - フィールド区切りは `, `（カンマ+スペース）
    - titleにカンマが含まれる場合: 全角カンマ `、` に置換する
      （TOON形式にはクォート機構がないため。titleは日本語が主で、
       半角カンマが含まれるケースは稀だが、含まれる場合は全角に置換して区切りとの衝突を回避する）
    - title以外のフィールド（type, category, processing_patterns, path）には
      カンマが含まれることはない（値が制約されているため）
    """
    lines = [f"# Nabledge-{version} Knowledge Index", ""]
    lines.append(f"files[{len(entries)},]{{title,type,category,processing_patterns,path}}:")
    
    for entry in entries:
        title = entry["title"].replace(",", "、")  # 半角カンマを全角に置換
        fields = [
            title,
            entry["type"],
            entry["category"],
            entry["processing_patterns"],
            entry["path"],
        ]
        lines.append(f"  {', '.join(fields)}")
    
    lines.append("")  # 末尾改行
    write_file(index_path, '\n'.join(lines))
```

---

## Step 5: 閲覧用MD生成

### 概要

| 項目 | 内容 |
|---|---|
| 処理方式 | Pythonスクリプト（機械的変換） |
| 入力 | 知識ファイルJSON |
| 出力 | `$REPO/.claude/skills/nabledge-{version}/docs/{type}/{category}/{id}.md` |

### 変換ルール

```
# {title}

## {index[0].title}

{sections[index[0].id]}

## {index[1].title}

{sections[index[1].id]}

...
```

### 処理ロジック

```python
def generate_docs(ctx: Context):
    classified = load_json(ctx.classified_list_path)
    
    for file_info in classified["files"]:
        json_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
        if not os.path.exists(json_path):
            continue
        
        knowledge = load_json(json_path)
        md_content = convert_to_md(knowledge)
        
        md_path = f"{ctx.docs_dir}/{file_info['type']}/{file_info['category']}/{file_info['id']}.md"
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        write_file(md_path, md_content)


def convert_to_md(knowledge: dict) -> str:
    lines = [f"# {knowledge['title']}", ""]
    
    for entry in knowledge["index"]:
        section_id = entry["id"]
        section_title = entry["title"]
        section_content = knowledge["sections"].get(section_id, "")
        
        lines.append(f"## {section_title}")
        lines.append("")
        lines.append(section_content)
        lines.append("")
    
    return "\n".join(lines)
```

---

## Step 6: 検証

### 概要

| 項目 | 内容 |
|---|---|
| 処理方式 | スクリプト（構造チェック）+ claude -p（内容検証、別セッション） |
| 並行単位 | 1知識ファイル = 1 claude -pセッション |
| 入力 | 知識ファイルJSON + 元のソースファイル |
| 出力 | `logs/v{version}/validate/structure/`, `logs/v{version}/validate/content/`, `logs/v{version}/summary.json` |

### 検証フロー

```
1. 構造チェック（スクリプト、全ファイル対象）
   → passしたファイルのみ次へ
2. 内容検証（claude -p、並行処理）
   → 生成バイアス排除のため別セッションで実行
3. 結果集約・レポート出力
```

### 構造チェック（スクリプト）

全項目 pass / fail の2値判定。1つでもfailがあればそのファイルはNG。NGはOKになるまで修正、または修正方針をユーザーに相談する。

#### チェック項目一覧

| # | チェック項目 | 判定基準 |
|---|---|---|
| S1 | JSONとしてパースできる | パース失敗 → fail |
| S2 | 必須フィールドが存在する（id, title, official_doc_urls, index, sections） | 1つでも欠落 → fail |
| S3 | index[].id が全て sections のキーに存在する | 不一致あり → fail |
| S4 | sections のキーが全て index[].id に存在する | 不一致あり → fail |
| S5 | index[].id がケバブケース（`^[a-z0-9]+(-[a-z0-9]+)*$`） | 不適合あり → fail |
| S6 | index[].hints が空配列でない | 空配列あり → fail |
| S7 | sections の値が空文字列でない | 空あり → fail |
| S8 | id フィールドがファイル名（拡張子なし）と一致する | 不一致 → fail |
| S9 | セクション数がソースの見出し数と整合する | 下記ルール参照 |
| S10 | h3分割の妥当性（RST のみ） | 下記ルール参照 |
| S11 | official_doc_urls が有効である | 下記ルール参照 |
| S12 | hintsにセクション本文中の技術用語が含まれている | 下記ルール参照 |
| S13 | セクション本文が極端に短くない | 50文字未満 → fail |
| S14 | クロスリファレンスの参照先が存在する | 下記ルール参照 |
| S15 | assetsパス参照のファイルが存在する | 下記ルール参照 |
| S16 | index.toonの行数と知識ファイル数が一致する | 不一致 → fail |
| S17 | index.toonのprocessing_patterns値が有効値のみで構成されている | 無効値あり → fail |

#### S9: セクション数チェック

ソースの見出し数と知識ファイルのセクション数を突き合わせる。

| 形式 | ソース側のカウント方法 |
|---|---|
| RST | h2（`-----` 下線）の数をカウント |
| MD | `##` で始まる行（`###` 以上は除外）の数をカウント |
| Excel | 固定で1 |

判定:
- セクション数 < ソースのh2数 → **fail**（セクションが欠落している）
- MD形式でセクション数 ≠ ソースの##数 → **fail**（MDにはh3分割ルールがないため厳密一致）
- RST形式でセクション数 > ソースのh2数 → S10（h3分割）で妥当性を判定

#### S10: h3分割の妥当性（RSTのみ）

セクション数がソースのh2数を超えている場合、h3分割が正当に行われたかを検証する。

ソースのRSTを解析し、各h2配下のテキスト量を算出する:
- h2配下のテキスト量 ≥ 2000文字 かつ h3分割されている → **pass**
- h2配下のテキスト量 < 2000文字 かつ h3分割されている → **fail**（不要な分割）
- h2配下のテキスト量 ≥ 2000文字 かつ h3分割されていない → **fail**（分割漏れ）

テキスト量の算出: h2の直後からh3見出し行・コードブロック・ディレクティブを除いたプレーンテキストの文字数。

#### S11: official_doc_urls の検証

各URLに対してHTTPリクエスト（GET）を実行し、以下を全て確認する:
- HTTPステータスコードが200である
- レスポンスHTMLの`<title>`タグの内容が知識ファイルの`title`と一致する（部分一致可。HTMLタイトルに`title`の文字列が含まれていればpass）
- レスポンスHTMLに日本語テキストが含まれている（`[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]` にマッチするテキストが存在する）

タイムアウト: 10秒。タイムアウトした場合はfail。

#### S12: hints技術用語チェック

セクション本文中のバッククォート内テキストから技術用語を抽出し、hints配列に完全一致で含まれているかを検証する。

抽出対象（バッククォート内テキストのうち以下に該当するもの）:
- パッケージ付きクラス名: `nablarch.common.handler.DbConnectionManagementHandler` のようにドット区切りで最後がPascalCase
- 単独クラス名/インターフェース名: PascalCase（`[A-Z][a-zA-Z0-9]+`、2語以上の結合）
- アノテーション: `@` で始まるもの（`@InjectForm` 等）
- 例外クラス名: `Exception` で終わるもの

抽出対象外（コード断片であり技術用語ではないもの）:
- コードブロック（` ``` ` 〜 ` ``` `）内のバッククォート
- XML/HTMLタグ（`<` で始まるもの）
- ファイルパス（`/` を含むもの）
- 全て小文字のもの（`true`, `false`, `null` 等のリテラル）
- camelCase単独のもの（プロパティ名は別途ルール。下記参照）

プロパティ名の扱い: プロパティ一覧の表（`| プロパティ名 |` ヘッダを持つMDテーブル）内の第1列の値を抽出対象とする。

判定: 抽出された技術用語がhintsに1つも含まれていないセクションがあれば → **fail**

#### S13: セクション本文の最小長

セクション本文が50文字未満のセクションは情報の漏れの兆候。 → **fail**

#### S14: クロスリファレンスの参照先存在確認

セクション本文中の「〜を参照」パターン（`知識ファイルID を参照` / `セクションID を参照`）から参照先を抽出し、対応する知識ファイルまたはセクションが実際に存在するかを検証する。

- `{知識ファイルID} を参照` → `knowledge/**/{知識ファイルID}.json` が存在するか
- `{セクションID} を参照`（同一ファイル内）→ 当該JSONのsectionsにキーが存在するか
- 存在しない参照先がある → **fail**

#### S15: assetsパス参照の実在確認

セクション本文中の `![...](assets/...)` および `[...](assets/...)` パターンからファイルパスを抽出し、実際にファイルが存在するかを検証する。

- パスは知識ファイルのあるディレクトリからの相対パスとして解決
- ファイルが存在しない → **fail**

#### S16: index.toon行数チェック

index.toonのヘッダー行 `files[N,]` の `N` と、実際のデータ行数、および `knowledge/` 配下のJSONファイル数が全て一致するかを検証する。

- いずれかが不一致 → **fail**

#### S17: index.toon processing_patterns値チェック

index.toonの各行の `processing_patterns` フィールドが以下の有効値のみで構成されているかを検証する。

有効値: `nablarch-batch`, `jakarta-batch`, `restful-web-service`, `http-messaging`, `web-application`, `mom-messaging`, `db-messaging`

- 空（該当なし）は許容
- 複数値はスペース区切り
- 有効値以外が含まれている → **fail**

#### 構造チェック実装

```python
import re
import json
import os
import requests

KEBAB_CASE_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
JAPANESE_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')
VALID_PROCESSING_PATTERNS = {
    "nablarch-batch", "jakarta-batch", "restful-web-service",
    "http-messaging", "web-application", "mom-messaging", "db-messaging"
}

# S12: 技術用語抽出パターン
PASCAL_CASE = re.compile(r'^[A-Z][a-zA-Z0-9]*[a-z][a-zA-Z0-9]*$')  # 2語以上のPascalCase
PACKAGE_CLASS = re.compile(r'^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*\.[A-Z][a-zA-Z0-9]+$')  # パッケージ付き
ANNOTATION = re.compile(r'^@[A-Z][a-zA-Z0-9]+$')  # アノテーション
EXCEPTION_CLASS = re.compile(r'^[A-Z][a-zA-Z0-9]*Exception$')  # 例外クラス


def validate_structure(json_path: str, source_path: str, source_format: str,
                       knowledge_dir: str) -> list[str]:
    """構造チェック。エラーメッセージのリストを返す。空ならpass。"""
    errors = []

    # --- S1: JSONパース ---
    try:
        knowledge = load_json(json_path)
    except json.JSONDecodeError as e:
        return [f"S1: JSON parse error: {e}"]

    # --- S2: 必須フィールド ---
    for field in ["id", "title", "official_doc_urls", "index", "sections"]:
        if field not in knowledge:
            errors.append(f"S2: Missing required field: {field}")
    if errors:
        return errors

    index_ids = [entry["id"] for entry in knowledge["index"]]
    index_id_set = set(index_ids)
    section_keys = set(knowledge["sections"].keys())

    # --- S3, S4: index ↔ sections 整合性 ---
    for iid in index_id_set - section_keys:
        errors.append(f"S3: index[].id '{iid}' has no corresponding section")
    for sk in section_keys - index_id_set:
        errors.append(f"S4: sections key '{sk}' has no corresponding index entry")

    # --- S5: ケバブケース ---
    for entry in knowledge["index"]:
        if not KEBAB_CASE_PATTERN.match(entry["id"]):
            errors.append(f"S5: Section ID '{entry['id']}' is not kebab-case")

    # --- S6: hints非空 ---
    for entry in knowledge["index"]:
        if not entry.get("hints"):
            errors.append(f"S6: Section '{entry['id']}' has empty hints")

    # --- S7: sections非空 ---
    for sid, content in knowledge["sections"].items():
        if not content.strip():
            errors.append(f"S7: Section '{sid}' has empty content")

    # --- S8: ファイル名との一致 ---
    expected_id = os.path.basename(json_path).replace(".json", "")
    if knowledge["id"] != expected_id:
        errors.append(f"S8: id '{knowledge['id']}' does not match filename '{expected_id}'")

    # --- S9, S10: セクション数・h3分割妥当性 ---
    source_content = read_file(source_path)
    expected_sections = count_source_headings(source_content, source_format)
    actual_sections = len(knowledge["sections"])

    if actual_sections < expected_sections:
        errors.append(
            f"S9: Section count {actual_sections} < source heading count {expected_sections}"
        )
    elif source_format == "md" and actual_sections != expected_sections:
        # MDはh3分割ルールがないため、セクション数は厳密一致
        errors.append(
            f"S9: MD section count {actual_sections} != source ## count {expected_sections}"
        )
    elif actual_sections > expected_sections and source_format == "rst":
        errors.extend(validate_h3_splits(source_content, knowledge))

    # --- S11: official_doc_urls ---
    errors.extend(validate_urls(knowledge))

    # --- S12: hints技術用語 ---
    errors.extend(validate_hints_terms(knowledge))

    # --- S13: セクション最小長 ---
    for sid, content in knowledge["sections"].items():
        if len(content.strip()) < 50:
            errors.append(f"S13: Section '{sid}' is too short ({len(content.strip())} chars)")

    # --- S14: クロスリファレンス ---
    errors.extend(validate_cross_references(knowledge, knowledge_dir))

    # --- S15: assetsパス参照 ---
    errors.extend(validate_asset_paths(knowledge, os.path.dirname(json_path)))

    return errors


def count_source_headings(content: str, fmt: str) -> int:
    """ソースの分割単位見出しの数をカウント"""
    if fmt == "rst":
        # h2: テキスト行の直後に ----- が続くパターン
        return len(re.findall(r'\n[^\n]+\n-{3,}\n', content))
    elif fmt == "md":
        # ## で始まるが ### 以上ではない行
        return len(re.findall(r'^## (?!#)', content, re.MULTILINE))
    elif fmt == "xlsx":
        return 1
    return 0


def validate_h3_splits(rst_content: str, knowledge: dict) -> list[str]:
    """S10: h2配下のテキスト量に基づくh3分割の妥当性チェック"""
    errors = []
    h2_sections = parse_rst_h2_sections(rst_content)

    for h2_title, h2_text, has_h3s in h2_sections:
        plain_len = len(strip_rst_markup(h2_text))
        if plain_len >= 2000 and not has_h3s:
            errors.append(
                f"S10: h2 '{h2_title}' has {plain_len} chars but no h3 split"
            )
        if plain_len < 2000 and has_h3s:
            # h3が知識ファイル上でセクションとして独立しているか確認
            h3_titles = extract_h3_titles(h2_text)
            for h3 in h3_titles:
                h3_id = to_kebab(h3)
                if h3_id in knowledge["sections"]:
                    errors.append(
                        f"S10: h2 '{h2_title}' has only {plain_len} chars "
                        f"but h3 '{h3}' is split as separate section"
                    )
    return errors


def parse_rst_h2_sections(rst_content: str) -> list[tuple[str, str, bool]]:
    """RSTをh2セクション単位に分割する。
    
    RSTの見出し記法:
    - 見出しレベルはファイル内の出現順で決まる（RST仕様）
    - ただしNablarchドキュメントでは以下の規約で統一されている:
      - h1: === (overline + underline) または === (underline only, ファイル先頭)
      - h2: --- (underline)
      - h3: ~~~ (underline)
      - h4: ^^^ (underline)
    - 見出し行: テキスト行の直後に同じ長さ以上の記号行が続く
    
    戻り値: [(h2タイトル, h2配下テキスト全文, h3を含むか), ...]
    """
    lines = rst_content.split('\n')
    h2_sections = []
    current_h2_title = None
    current_h2_lines = []
    has_h3 = False
    
    i = 0
    while i < len(lines):
        # 見出し検出: テキスト行 + 記号行
        if (i + 1 < len(lines) and
            lines[i].strip() and
            not lines[i].startswith(' ') and
            len(lines[i + 1]) >= 3):
            
            underline = lines[i + 1].strip()
            
            if underline and all(c == '-' for c in underline):
                # h2検出
                if current_h2_title is not None:
                    h2_sections.append((
                        current_h2_title,
                        '\n'.join(current_h2_lines),
                        has_h3
                    ))
                current_h2_title = lines[i].strip()
                current_h2_lines = []
                has_h3 = False
                i += 2
                continue
            
            elif underline and all(c == '~' for c in underline):
                # h3検出
                has_h3 = True
                current_h2_lines.append(lines[i])
                current_h2_lines.append(lines[i + 1])
                i += 2
                continue
        
        if current_h2_title is not None:
            current_h2_lines.append(lines[i])
        i += 1
    
    # 最後のh2セクション
    if current_h2_title is not None:
        h2_sections.append((
            current_h2_title,
            '\n'.join(current_h2_lines),
            has_h3
        ))
    
    return h2_sections


def strip_rst_markup(text: str) -> str:
    """RSTマークアップを除去してプレーンテキストの文字数を算出するための前処理。
    
    除去対象:
    - 見出し記号行（---, ~~~, ^^^, === のみの行）
    - ディレクティブ行（.. xxx:: で始まる行）
    - コードブロック（.. code-block:: 〜 次の非インデント行まで）
    - インデントされたディレクティブ本文
    - 空行
    
    残す対象:
    - 通常のテキスト行（RSTインラインマークアップ :ref:, :doc: 等はそのまま残す。
      正確な文字数は不要で、おおよそ2000文字の閾値判定に使うため）
    """
    result_lines = []
    in_code_block = False
    in_directive = False
    
    for line in text.split('\n'):
        stripped = line.strip()
        
        # 空行
        if not stripped:
            in_directive = False
            continue
        
        # 見出し記号行
        if all(c in '-~^=' for c in stripped) and len(stripped) >= 3:
            continue
        
        # コードブロック開始
        if stripped.startswith('.. code-block::') or stripped.startswith('.. literalinclude::'):
            in_code_block = True
            continue
        
        # ディレクティブ開始
        if re.match(r'\.\.\s+\w+', stripped):
            in_directive = True
            continue
        
        # インデントされた行（コードブロック/ディレクティブ本文）
        if line.startswith('   '):
            if in_code_block or in_directive:
                continue
        else:
            in_code_block = False
        
        result_lines.append(stripped)
    
    return '\n'.join(result_lines)


def extract_h3_titles(h2_text: str) -> list[str]:
    """h2セクションのテキスト内からh3タイトルを抽出する。
    
    h3: テキスト行の直後に ~~~ が続くパターン
    """
    titles = []
    lines = h2_text.split('\n')
    for i in range(len(lines) - 1):
        if (lines[i].strip() and
            not lines[i].startswith(' ') and
            lines[i + 1].strip() and
            all(c == '~' for c in lines[i + 1].strip()) and
            len(lines[i + 1].strip()) >= 3):
            titles.append(lines[i].strip())
    return titles


def to_kebab(text: str) -> str:
    """日本語/英語テキストをケバブケースに変換する。
    
    - 英語: スペース・アンダースコアをハイフンに変換し小文字化
    - 日本語: そのまま返す（日本語タイトルのh3がセクションIDになることはない。
      セクションIDは英語ベースのケバブケースのみ）
    
    例:
    - "Database Connection" → "database-connection"
    - "error_handling" → "error-handling"
    """
    text = text.strip().lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def validate_urls(knowledge: dict) -> list[str]:
    """S11: official_doc_urlsの検証"""
    errors = []
    for url in knowledge.get("official_doc_urls", []):
        if not url.startswith("https://"):
            errors.append(f"S11: URL does not start with https://: {url}")
            continue
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                errors.append(f"S11: URL returned {resp.status_code}: {url}")
                continue
            html = resp.text
            # タイトル一致（部分一致）
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            if title_match:
                html_title = title_match.group(1).strip()
                if knowledge["title"] not in html_title:
                    errors.append(
                        f"S11: Title mismatch: knowledge='{knowledge['title']}' "
                        f"not found in html_title='{html_title}': {url}"
                    )
            else:
                errors.append(f"S11: No <title> tag found: {url}")
            # 日本語チェック
            if not JAPANESE_PATTERN.search(html):
                errors.append(f"S11: No Japanese text found: {url}")
        except requests.Timeout:
            errors.append(f"S11: Timeout (10s): {url}")
        except requests.RequestException as e:
            errors.append(f"S11: Request failed: {url}: {e}")
    return errors


def extract_tech_terms(section_content: str) -> set[str]:
    """S12: セクション本文からバッククォート内の技術用語を抽出"""
    terms = set()

    # コードブロック除去
    cleaned = re.sub(r'```[\s\S]*?```', '', section_content)

    # プロパティ一覧テーブルからプロパティ名を抽出
    # テーブル構造: ヘッダ行 → 区切り行(---|---) → データ行 → 空行で終了
    lines = cleaned.split('\n')
    in_prop_table = False
    for line in lines:
        stripped = line.strip()
        # 空行またはテーブル行でない行でテーブル終了
        if in_prop_table and (not stripped or not stripped.startswith('|')):
            in_prop_table = False
            continue
        if '| プロパティ名 |' in stripped:
            in_prop_table = True
            continue
        if in_prop_table and stripped.startswith('|'):
            # 区切り行はスキップ
            if re.match(r'^\|[\s\-|]+\|$', stripped):
                continue
            # 第1列を抽出
            cells = [c.strip() for c in stripped.split('|')]
            # split('|')の先頭・末尾は空文字になる
            if len(cells) >= 2 and cells[1]:
                terms.add(cells[1])

    # バッククォート内テキスト
    backtick_terms = re.findall(r'`([^`]+)`', cleaned)
    for t in backtick_terms:
        t = t.strip()
        if t.startswith("<") or "/" in t:
            continue
        if t.lower() == t and not t.startswith("@"):
            continue
        if PACKAGE_CLASS.match(t) or PASCAL_CASE.match(t) or \
           ANNOTATION.match(t) or EXCEPTION_CLASS.match(t):
            terms.add(t)

    return terms


def validate_hints_terms(knowledge: dict) -> list[str]:
    """S12: 各セクションのhintsに技術用語が含まれているか検証"""
    errors = []
    hints_by_section = {
        entry["id"]: set(entry.get("hints", []))
        for entry in knowledge["index"]
    }

    for entry in knowledge["index"]:
        sid = entry["id"]
        content = knowledge["sections"].get(sid, "")
        terms = extract_tech_terms(content)
        if not terms:
            continue  # 技術用語がないセクション（概念説明等）はスキップ
        hints = hints_by_section.get(sid, set())
        missing = terms - hints
        if missing == terms:
            errors.append(
                f"S12: Section '{sid}' hints contain none of the tech terms: "
                f"{sorted(missing)}"
            )
    return errors


def validate_cross_references(knowledge: dict, knowledge_dir: str) -> list[str]:
    """S14: クロスリファレンスの参照先存在確認"""
    errors = []
    # 「XXX を参照」パターン
    ref_pattern = re.compile(r'(\S+)\s*を参照')
    section_ids = set(knowledge["sections"].keys())

    for sid, content in knowledge["sections"].items():
        for match in ref_pattern.finditer(content):
            ref_id = match.group(1)
            # 同一ファイル内セクション参照
            if ref_id in section_ids:
                continue
            # 別ファイル参照
            from glob import glob
            found = glob(f"{knowledge_dir}/**/{ref_id}.json", recursive=True)
            if not found:
                errors.append(
                    f"S14: Section '{sid}' references '{ref_id}' but no matching "
                    f"knowledge file or section found"
                )
    return errors


def validate_asset_paths(knowledge: dict, json_dir: str) -> list[str]:
    """S15: assetsパス参照の実在確認"""
    errors = []
    asset_pattern = re.compile(r'[!\[]\[?[^\]]*\]\(assets/([^)]+)\)')

    for sid, content in knowledge["sections"].items():
        for match in asset_pattern.finditer(content):
            asset_rel = f"assets/{match.group(1)}"
            asset_abs = os.path.join(json_dir, asset_rel)
            if not os.path.exists(asset_abs):
                errors.append(
                    f"S15: Section '{sid}' references '{asset_rel}' but file not found"
                )
    return errors


def validate_index_toon(index_path: str, knowledge_dir: str) -> list[str]:
    """S16, S17: index.toonの検証"""
    errors = []
    content = read_file(index_path)

    # ヘッダー行からN取得
    header_match = re.search(r'files\[(\d+),\]', content)
    if not header_match:
        return ["S16: Cannot parse index.toon header"]
    declared_count = int(header_match.group(1))

    # データ行カウント
    data_lines = [
        line for line in content.split('\n')
        if line.startswith('  ') and line.strip() and not line.strip().startswith('#')
    ]
    data_count = len(data_lines)

    # 知識ファイル数カウント
    from glob import glob
    json_files = glob(f"{knowledge_dir}/**/*.json", recursive=True)
    json_count = len(json_files)

    if not (declared_count == data_count == json_count):
        errors.append(
            f"S16: Count mismatch: header={declared_count}, "
            f"data_lines={data_count}, json_files={json_count}"
        )

    # S17: processing_patterns値チェック
    for i, line in enumerate(data_lines, 1):
        fields = [f.strip() for f in line.strip().split(', ')]
        if len(fields) >= 4:
            patterns_str = fields[3]  # 4番目のフィールド
            if patterns_str:
                for p in patterns_str.split():
                    if p not in VALID_PROCESSING_PATTERNS:
                        errors.append(
                            f"S17: Invalid processing_pattern '{p}' at line {i}"
                        )

    return errors
```

### 内容検証（claude -p）

生成バイアスを排除するため、生成時とは別セッションのclaude -pで実行する。
構造チェック（S1〜S17）をpassしたファイルのみが対象。

### claude -p プロンプト（`prompts/validate.md`）

````markdown
あなたはNablarchの知識ファイルの品質検証エキスパートです。
生成された知識ファイルとソースファイルを突き合わせ、品質を検証してください。

## ソースファイル

```
{SOURCE_CONTENT}
```

## 知識ファイル

```json
{KNOWLEDGE_JSON}
```

## 検証観点

以下の観点で検証し、問題を全て報告してください。全項目 pass / fail の2値判定です。

### 1. 情報の漏れ（最も重要）

ソースに書かれている以下の情報が知識ファイルに含まれているか確認:
- 仕様（設定項目、デフォルト値、型、制約、動作仕様）
- 注意点・警告（important, warning, tip, note ディレクティブの内容）
- 設計思想、推奨パターン
- コード例、設定例
- クラス名、インターフェース名、アノテーション名

漏れがある場合は、具体的に何が漏れているかを記載すること。

### 2. 情報の捏造

知識ファイルにソースに書かれていない情報が含まれていないか確認:
- 推測で追加されたデフォルト値、制約、動作仕様
- ソースにない説明の追加
- ソースにないコード例の追加

### 3. セクション分割の妥当性

- RSTの場合: h2で分割されているか。h2配下が2000文字を超える場合にh3で分割されているか
- MDの場合: ##で分割されているか
- h3以下が親セクションに含まれているか

### 4. 検索ヒントの品質

- 各セクションのhints にクラス名、プロパティ名、機能キーワードが含まれているか
- 不足しているhintがないか

## 出力形式

以下のJSON形式で出力してください。JSON以外のテキストは含めないでください。

```json
{
  "verdict": "pass" または "fail",
  "issues": [
    {
      "type": "missing_info" または "fabricated_info" または "bad_section_split" または "poor_hints",
      "section_id": "対象セクションID（該当する場合）",
      "description": "問題の具体的な説明"
    }
  ]
}
```

判定基準:
- issueが1つでもあれば `"verdict": "fail"`
- issueなしのみ `"verdict": "pass"`
- 全タイプのissueが同等にfailの原因となる（warningレベルは存在しない）
````

### 検証結果の集約

検証結果は個別ファイルに出力され、全並行処理の完了後にサマリーを生成する。詳細は「ログ管理」セクションを参照。

個別ファイルの出力先:
- 構造チェック: `logs/v{version}/validate/structure/{file_id}.json`
- 内容検証: `logs/v{version}/validate/content/{file_id}.json`
- サマリー: `logs/v{version}/summary.json`
```

### fail時の対応

全てのfailは、OKになるまで修正するか、修正方針をユーザーに相談する。

| 判定 | 対応 |
|---|---|
| 構造チェック fail（S1〜S8） | Step 3を該当ファイルのみ再実行 |
| 構造チェック fail（S9, S10） | セクション分割に問題あり。Step 3を該当ファイルのみ再実行 |
| 構造チェック fail（S11） | URLの修正が必要。公式URLが移動している場合はユーザーに相談 |
| 構造チェック fail（S12） | hints不足。Step 3を該当ファイルのみ再実行 |
| 構造チェック fail（S13） | セクション内容が薄い（情報漏れの兆候）。Step 3を該当ファイルのみ再実行 |
| 構造チェック fail（S14） | 参照先が存在しない。参照先の生成漏れか参照IDの誤り。原因に応じて修正 |
| 構造チェック fail（S15） | assetsファイルが存在しない。画像の取り込み漏れ。Step 3を再実行 |
| 構造チェック fail（S16, S17） | index.toonの不整合。Step 4を再実行 |
| 内容検証 fail | Step 3を該当ファイルのみ再実行 |

再実行手順:
```bash
# 該当ファイルを削除
rm $REPO/.claude/skills/nabledge-6/knowledge/component/handlers/some-handler.json

# Step 3のみ再実行（スキップ機構により該当ファイルのみ生成される）
python run.py --version 6 --step 3
```

---

## 差分処理

### run.pyにおける初回/2回目以降の統合

run.pyは初回実行と2回目以降を自動判別する。分岐のロジックは以下:

```python
def main(version, step, concurrency, repo):
    versions = ["6", "5"] if version == "all" else [version]
    for v in versions:
        ctx = Context(version=v, repo=repo, concurrency=concurrency)
        
        # Step 1, 2 は常に実行（毎回上書き生成）
        if step is None or step <= 2:
            Step1ListSources(ctx).run()
            Step2Classify(ctx).run()
        
        # 差分検知（Step 3以降の前に実行）
        changes = detect_changes(ctx)
        
        if changes["deleted"]:
            # 削除されたファイルのクリーンアップ
            for file_id in changes["deleted"]:
                delete_knowledge(ctx, file_id)
        
        if changes["updated"]:
            # 更新されたファイルの知識ファイルを削除（Step 3で再生成される）
            for file_id in changes["updated"]:
                delete_knowledge_json(ctx, file_id)
        
        # Step 3: 生成（存在チェックでスキップされるため、
        #   追加分 + 更新で削除された分のみ実際に生成される）
        if step is None or step == 3:
            Step3Generate(ctx).run()
        
        # Step 4: index は常に全量再生成
        if step is None or step == 4:
            Step4BuildIndex(ctx).run()
        
        # Step 5: docs は常に全量再生成
        if step is None or step == 5:
            Step5GenerateDocs(ctx).run()
        
        # Step 6: 検証
        if step is None or step == 6:
            Step6Validate(ctx).run()
```

つまり:
- **初回**: 全ファイルの知識ファイルがないので、Step 3で全量生成
- **2回目以降**: detect_changesで追加・削除・更新を検知し、削除/更新分をクリーンアップ後、Step 3のスキップ機構で差分のみ生成
- **--step指定時**: 指定ステップのみ実行。ただしStep 3以降を指定した場合、Step 1, 2は実行されない（前回のclassified JSONを使用する）

### 2回目以降の実行フロー

```
1. Step 1: ソースファイル一覧を再取得
2. Step 2: 分類
3. 差分検知: 既存の知識ファイルと比較
   - 追加: 分類リストにあり知識ファイルがない
   - 削除: 知識ファイルがあり分類リストにない
   - 更新: パスは同じだがソースファイルの更新日時が知識ファイルより新しい
4. 削除分のクリーンアップ、更新分の知識ファイル削除
5. Step 3〜6を実行（スキップ機構で差分のみ処理される）
```

### 差分検知ロジック

```python
def detect_changes(ctx: Context) -> dict:
    current = load_json(ctx.classified_list_path)
    current_ids = {f["id"] for f in current["files"]}
    
    # 既存の知識ファイルをスキャン
    existing_ids = set()
    for json_file in glob(f"{ctx.knowledge_dir}/**/*.json", recursive=True):
        if "index.toon" not in json_file:
            existing_ids.add(os.path.basename(json_file).replace(".json", ""))
    
    added = current_ids - existing_ids
    deleted = existing_ids - current_ids
    
    # 更新検知（ソースの更新日時 > 知識ファイルの更新日時）
    updated = set()
    for f in current["files"]:
        if f["id"] not in added:
            source_mtime = os.path.getmtime(f"{ctx.repo}/{f['source_path']}")
            json_path = f"{ctx.knowledge_dir}/{f['output_path']}"
            if os.path.exists(json_path):
                json_mtime = os.path.getmtime(json_path)
                if source_mtime > json_mtime:
                    updated.add(f["id"])
    
    return {"added": added, "deleted": deleted, "updated": updated}
```

### 差分に応じた処理

| 差分種別 | 処理 |
|---|---|
| 追加 | Step 3（生成）→ Step 4（index更新）→ Step 5（docs生成）→ Step 6（検証） |
| 削除 | 知識ファイルJSON + 閲覧用MD + assetsを削除 → Step 4（index更新） |
| 更新 | 知識ファイルJSONを削除 → 追加と同じフローで再生成 |

削除処理:
```python
def delete_knowledge(ctx: Context, file_id: str, file_info: dict):
    json_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
    md_path = f"{ctx.docs_dir}/{file_info['type']}/{file_info['category']}/{file_id}.md"
    assets_path = f"{ctx.knowledge_dir}/{file_info['type']}/{file_info['category']}/assets/{file_id}/"
    
    for path in [json_path, md_path]:
        if os.path.exists(path):
            os.remove(path)
    if os.path.exists(assets_path):
        shutil.rmtree(assets_path)
```

### 中断再開

各ステップは冪等性を持つ:
- Step 1, 2: 毎回上書き生成（軽量処理）
- Step 3: 生成済みファイルの存在チェックでスキップ
- Step 4: 毎回全量再生成（index.toonは1ファイルのため差分不要）
- Step 5: 毎回全量再生成（軽量処理）
- Step 6: 検証レポートがない/不完全なファイルのみ対象

---

## ログ管理

### 設計方針

エージェントの並行処理を前提に、全てのログをファイル単位の独立ファイルとして出力する。共有ファイルへの並行書き込みは行わない。

- 各ステップの作業結果は `logs/v{version}/{step名}/{file_id}.json` に1ファイルずつ出力
- ステップ完了後にマージスクリプトが個別ファイルを集約してサマリーを生成
- 中断再開時は個別ファイルの存在でスキップ判定

### ログファイル構成

```
tools/knowledge-creator/logs/
  v{version}/
    sources.json                          # Step 1出力（全量）
    classified.json                       # Step 2出力（全量）
    generate/                             # Step 3: 生成ログ（ファイル単位）
      {file_id}.json                      # 成功: {"status":"ok","duration_sec":30}
                                          # エラー: {"status":"error","error":"timeout","raw_output":"..."}
    classify-patterns/                    # Step 4: パターン分類ログ（ファイル単位）
      {file_id}.json                      # {"patterns":"nablarch-batch restful-web-service"}
    validate/                             # Step 6: 検証ログ（ファイル単位）
      structure/
        {file_id}.json                    # {"result":"pass","errors":[]}
      content/
        {file_id}.json                    # {"verdict":"pass","issues":[]}
    summary.json                          # マージ後のサマリー（ステップ完了時に生成）
```

### 個別ログのスキーマ

#### Step 3: generate/{file_id}.json

```json
{
  "file_id": "db-connection-management-handler",
  "status": "ok",
  "started_at": "2025-01-01T00:00:00Z",
  "finished_at": "2025-01-01T00:00:30Z",
  "duration_sec": 30
}
```

エラー時:

```json
{
  "file_id": "some-handler",
  "status": "error",
  "started_at": "2025-01-01T00:00:00Z",
  "finished_at": "2025-01-01T00:05:00Z",
  "error": "timeout",
  "raw_output": "claude -pの生出力（パース失敗時等）"
}
```

#### Step 6: validate/structure/{file_id}.json

```json
{
  "file_id": "db-connection-management-handler",
  "result": "pass",
  "errors": []
}
```

#### Step 6: validate/content/{file_id}.json

```json
{
  "file_id": "db-connection-management-handler",
  "verdict": "pass",
  "issues": []
}
```

### サマリー生成（マージ処理）

各ステップの完了後に、個別ログを走査してサマリーを生成する。

```python
def generate_summary(ctx: Context):
    """全ステップの個別ログを集約してsummary.jsonを生成する"""
    log_dir = f"{ctx.repo}/tools/knowledge-creator/logs/v{ctx.version}"

    # Step 3 生成結果
    generate_dir = f"{log_dir}/generate"
    generate_results = []
    if os.path.exists(generate_dir):
        for f in sorted(os.listdir(generate_dir)):
            if f.endswith(".json"):
                generate_results.append(load_json(os.path.join(generate_dir, f)))

    # Step 6 検証結果
    structure_dir = f"{log_dir}/validate/structure"
    content_dir = f"{log_dir}/validate/content"
    validate_results = []
    if os.path.exists(structure_dir):
        for f in sorted(os.listdir(structure_dir)):
            if f.endswith(".json"):
                file_id = f.replace(".json", "")
                s = load_json(os.path.join(structure_dir, f))
                c_path = os.path.join(content_dir, f)
                c = load_json(c_path) if os.path.exists(c_path) else None
                validate_results.append({
                    "id": file_id,
                    "structure": s["result"],
                    "structure_errors": s["errors"],
                    "content": c["verdict"] if c else "skipped",
                    "content_issues": c["issues"] if c else [],
                })

    summary = {
        "version": ctx.version,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "generate": {
            "total": len(generate_results),
            "ok": sum(1 for r in generate_results if r["status"] == "ok"),
            "error": sum(1 for r in generate_results if r["status"] == "error"),
        },
        "validate": {
            "total": len(validate_results),
            "all_pass": sum(1 for r in validate_results
                          if r["structure"] == "pass" and r["content"] == "pass"),
            "structure_fail": sum(1 for r in validate_results if r["structure"] == "fail"),
            "content_fail": sum(1 for r in validate_results if r["content"] == "fail"),
        },
        "validate_results": validate_results,
    }

    write_json(f"{log_dir}/summary.json", summary)
```

### スキップ判定

各ステップで個別ログの存在をスキップ判定に使用する。

| ステップ | スキップ条件 |
|---|---|
| Step 3 | 知識ファイルJSON が存在する（従来どおり） |
| Step 4 | スキップなし（毎回全量再生成） |
| Step 6 構造チェック | `validate/structure/{file_id}.json` が存在し `result` が `pass` |
| Step 6 内容検証 | `validate/content/{file_id}.json` が存在し `verdict` が `pass` |

### 並行安全性

この設計では共有ファイルへの並行書き込みが発生しない。

- Step 3: 各ワーカーは `generate/{file_id}.json` に独立して書き込む
- Step 4: processing_patterns判定は `classify-patterns/{file_id}.json` に独立して書き込み、最後にシングルスレッドでindex.toonを生成
- Step 6: 各ワーカーは `validate/structure/{file_id}.json` と `validate/content/{file_id}.json` に独立して書き込む
- サマリー生成: 全並行処理が完了した後にシングルスレッドで実行

