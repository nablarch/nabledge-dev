# Knowledge Creator

Nablarch公式ドキュメント（RST/MD/Excel）をAI-readyなナレッジファイル（JSON）に変換するツール。

## 概要

マルチフェーズパイプラインでナレッジファイルを生成：

- **Phase A**: 準備 - ソースファイル一覧取得、Type/Category分類
- **Phase B**: 生成 - claude -p でナレッジJSON生成（並列実行）
- **Phase C**: 構造検証 - S1-S15チェック（Python、AI不要）
- **Phase D**: 内容検証 - claude -p で内容チェック（並列実行）
- **Phase E**: 修正 - claude -p で問題修正（並列実行）
- **Phase G**: リンク解決 - RST cross-references を Markdown リンクに変換
- **Phase F**: 仕上げ - 処理パターン分類、index.toon生成、閲覧用MD生成

Phase C→D→E は `--max-rounds` 回ループ可能。

## 必要な環境

- Python 3.8+
- Claude CLI (`claude` コマンドが利用可能)
- 依存パッケージ: `openpyxl`, `pytest`

## セットアップ

```bash
cd tools/knowledge-creator

# 仮想環境作成（推奨）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate  # Windows

# 依存パッケージインストール
pip install -r requirements.txt
```

または、リポジトリルートの `setup.sh` を実行（knowledge-creator依存も含む）：

```bash
cd /path/to/nabledge-dev
./setup.sh
```

## 使い方

### テストモード（3ファイル）

最大ファイル3つ（分割後8ファイル）で動作確認：

```bash
cd tools/knowledge-creator
python run.py --version 6 --test-mode --repo /path/to/nabledge-dev
```

**重要**: `--repo` にはリポジトリルートの絶対パスを指定してください。

### テストモード（包括的・21ファイル）

全フォーマット・タイプ・カテゴリをカバー：

```bash
# test-files.json を切り替え
cp test-files-comprehensive.json test-files.json

# 実行
python run.py --version 6 --test-mode --repo /path/to/nabledge-dev
```

### 本番モード（全ファイル）

v6全252ソースファイル（分割後262ファイル）を生成：

```bash
python run.py --version 6 --repo /path/to/nabledge-dev
```

v5とv6を同時に生成：

```bash
python run.py --version all --repo /path/to/nabledge-dev
```

### 特定フェーズのみ実行

```bash
# Phase B（生成）のみ
python run.py --version 6 --phase B --repo /path/to/nabledge-dev

# Phase C,D,E（検証・修正）のみ
python run.py --version 6 --phase CDE --repo /path/to/nabledge-dev

# Phase G,F（リンク解決・仕上げ）のみ
python run.py --version 6 --phase GF --repo /path/to/nabledge-dev
```

### オプション

| オプション | 説明 | デフォルト |
|----------|------|----------|
| `--version` | バージョン（6, 5, all） | **必須** |
| `--phase` | 実行フェーズ（A, B, C, D, E, G, F の組み合わせ） | `ABCDEFG` |
| `--test-mode` | テストモード（test-files.json の対象ファイルのみ） | `False` |
| `--concurrency` | 並列実行数（Phase B, D, E） | `4` |
| `--max-rounds` | Phase C→D→E のループ回数上限 | `1` |
| `--dry-run` | ドライラン（ファイル書き込みなし） | `False` |
| `--repo` | リポジトリルートパス | `os.getcwd()` |

## 出力ファイル

### 最終成果物

```
.claude/skills/nabledge-6/
  knowledge/              # ナレッジJSONファイル
    {type}/{category}/{file-id}.json
    index.toon            # ナレッジファイルインデックス
  docs/                   # 閲覧用Markdown
    {type}/{category}/{file-id}.md
```

### 中間成果物

```
tools/knowledge-creator/logs/v6/
  sources.json                    # Phase A: ソースファイル一覧
  classified.json                 # Phase A: 分類済みファイル一覧
  structure-check.json            # Phase C: 構造検証結果
  generate/trace/{file-id}.txt    # Phase B: 生成トレース
  validate/findings/{file-id}.json # Phase D: 内容検証結果
  knowledge-resolved/{type}/{category}/{file-id}.json # Phase G: リンク解決済み
```

## クリーンアップ

生成ファイルを全削除してクリーンな状態に：

```bash
cd tools/knowledge-creator
./clean.sh /path/to/nabledge-dev
```

## テストファイル設定

`test-files.json` で `--test-mode` の対象ファイルを制御：

- **test-files-top3.json**: 3最大ファイル（SC検証用）
- **test-files-comprehensive.json**: 21ファイル（包括的テスト用）

切り替え方法：

```bash
cp test-files-top3.json test-files.json          # 3ファイル版
cp test-files-comprehensive.json test-files.json  # 21ファイル版
```

## トラブルシューティング

### `FileNotFoundError: .lw/nab-official/v6/`

→ `--repo` オプションでリポジトリルートの絶対パスを指定してください。

### 入れ子ディレクトリ `tools/knowledge-creator/tools/...` が作成される

→ `tools/knowledge-creator` ディレクトリから実行する場合は必ず `--repo` を指定してください。

### `claude: command not found`

→ Claude CLI をインストールしてください。`--dry-run` オプションでAI呼び出しなしのテストは可能です。

### テストが失敗する

```bash
# ユニットテスト実行
cd tools/knowledge-creator
python -m pytest tests/ -v
```

## 関連ドキュメント

- **設計書**: `doc/nabledge-creator-v2-task.md`
- **マッピングファイル**: `doc/mapping/` (302ファイル)
- **Issue**: #106
- **PR**: #107
