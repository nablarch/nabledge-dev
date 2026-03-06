# Knowledge Creator

Nablarch 公式ドキュメント（RST/MD/Excel）を AI 対応ナレッジファイル（JSON）に変換するマルチフェーズパイプライン。

## セットアップ

### 必要なもの

- Python 3.8+
- Claude CLI（`claude` コマンドが使える状態）
- `jq`
- Python パッケージ: `openpyxl`, `pytest`

### セットアップ手順

リポジトリルートから `setup.sh` を実行する。システムツール・Python 依存パッケージ（knowledge-creator を含む）のインストールと、Nablarch 公式リポジトリのクローンを行う:

```bash
cd /path/to/nabledge-dev
./setup.sh
```

セットアップ完了後、シェルを再起動するか以下を実行:

```bash
source ~/.bashrc
```

**Note**: `setup.sh` はクローン対象リポジトリの情報を `plugin/knowledge-creator.json` から読み取る。

## 運用ガイド

**Important**: コマンドはリポジトリルートディレクトリから実行すること。

### UC 一覧

| UC | コマンド | 用途 | 何が起きるか |
|---|---|---|---|
| UC1 | `nc.sh gen 6` | 初回の全件生成 | 全クリーン → Phase A〜M を順次実行 |
| UC2 | `nc.sh gen 6 --resume` | 中断からの再開 | 生成済みファイルをスキップして続行 |
| UC3 | `nc.sh regen 6` | 公式ドキュメント更新への追随 | git pull → コミット比較 → 変更ファイルのみ再生成 |
| UC4 | `nc.sh regen 6 --target FILE_ID` | 特定ファイルの再生成 | 指定ファイルをクリーン → 再生成 |
| UC5 | `nc.sh fix 6` | 品質改善（全件） | Phase C→D→E→M で再検証・修正 |
| UC6 | `nc.sh fix 6 --target FILE_ID` | 品質改善（指定ファイル） | 指定ファイルのみ再検証・修正 |

### ソース変更追随の仕組み

#### knowledge-creator.json の役割

`plugin/knowledge-creator.json` はナレッジファイル生成に使用したソースリポジトリのコミット情報を記録する。フォーマット例:

```json
{
  "generated_at": "2026-03-01T12:00:00Z",
  "sources": [
    {
      "repo": "nablarch/nablarch-document",
      "branch": "develop",
      "commit": "abc1234..."
    }
  ]
}
```

`setup.sh` もこのファイルを読み取り、クローン対象リポジトリと対象ブランチを決定する。

#### UC3 の処理フロー

`nc.sh regen 6` を実行すると以下のステップが順次実行される:

```
nc.sh regen 6
  1. 公式リポを git pull（最新化）
  2. knowledge-creator.json の記録済みコミット vs HEAD を比較
  3. コミット同一 → 「更新なし」で終了
  4. コミット異なる → git diff --name-only <old> HEAD で変更ファイル一覧取得
  5. classified.json の source_path と突き合わせて対象 file_id を特定
  6. 対象の Phase B/D 成果物をクリーン
  7. Phase BCDEM を対象 file_id に対して実行
  8. Phase M 完了後、knowledge-creator.json に HEAD コミットを書き戻し
```

### Phase 詳細

```mermaid
flowchart TD
    Start([Start]) --> A[Phase A: Preparation]
    A --> |List & Classify Sources<br/>Split large files| B[Phase B: Generation]
    B --> |Generate Knowledge JSON| C[Phase C: Structure Check]
    C --> |S1-S15 Validation| PassC{Structure<br/>Errors?}
    PassC --> |Yes| StructWarn[Skip files with errors<br/>Continue with valid files]
    PassC --> |No| D[Phase D: Content Check]
    StructWarn --> D
    D --> |AI Validation<br/>Valid files only| PassD{Content<br/>Issues?}
    PassD --> |No| CheckStruct{Structure<br/>Errors<br/>Remain?}
    CheckStruct --> |Yes| RerunB([Re-run Phase B])
    CheckStruct --> |No| M[Phase M: Finalization]
    PassD --> |Yes| Round{Rounds<br/>Left?}
    Round --> |Yes| E[Phase E: Fix]
    Round --> |No| RerunCDE([Re-run Phase CDE<br/>with more rounds])
    E --> |AI Fix<br/>Content issues only| C
    M --> |1. Merge Split Files<br/>2. Resolve RST Links<br/>3. Generate Docs| Complete([Complete])

    style Start fill:#e1f5e1
    style Complete fill:#e1f5e1
    style RerunB fill:#fff3cd
    style RerunCDE fill:#fff3cd
    style StructWarn fill:#fff3cd
    style M fill:#e1e5ff
```

| Phase | Description | Type | Parallelized |
|-------|-------------|------|--------------|
| **A** | Preparation | List source files, classify by type/category, split large files | Python | No |
| **B** | Generation | Generate knowledge JSON from sources using Claude API | AI | Yes |
| **C** | Structure Check | Validate JSON structure with S1-S15 checks | Python | No |
| **D** | Content Check | Validate content accuracy against sources using Claude API | AI | Yes |
| **E** | Fix | Automatically fix issues found in Phase D using Claude API | AI | Yes |
| **M** | Finalization | Merge split files → Resolve RST links → Generate index & browsable docs | Hybrid | No |

**Loop Behavior**: Phase C→D→E can repeat up to `--max-rounds` times (default: 1, max: 10) until all files pass Phase D or maximum rounds reached.

**Split File Handling**: RST files with multiple h2 sections (≥2) are automatically split into per-section parts during Phase A, processed independently through Phases B-E, then merged in Phase M to prevent context overflow.

### オプション一覧

#### nc.sh オプション

| オプション | 説明 |
|---|---|
| `--resume` | クリーンをスキップ（gen コマンドのみ） |
| `--target FILE_ID` | 特定ファイルのみ処理（複数指定可） |
| `--yes` | 確認プロンプトをスキップ |
| `--dry-run` | ファイル書き込みなしのドライラン |
| `--max-rounds N` | Phase C→D→E の最大繰り返し回数（デフォルト: 1） |
| `--concurrency N` | 並列実行数（デフォルト: 4） |
| `--test FILE` | テスト設定ファイルを使用 |

**nc.sh と run.py の使い分け**:
- **nc.sh**: 一般的なワークフロー向け（推奨）
- **run.py**: フェーズや詳細オプションを細かく制御したい場合

#### run.py オプション

| Option | Description | Default |
|--------|-------------|---------|
| `--version` | Version (6, 5, all) | **Required** |
| `--phase` | Phases to run (combination of A, B, C, D, E, M) | `ABCDEM` |
| `--test` | Test mode: specify test file (e.g., `test-files-top3.json`) | `None` |
| `--concurrency` | Parallel execution count (Phase B, D, E) | `4` |
| `--max-rounds` | Max Phase C→D→E loop iterations (1-10) | `1` |
| `--clean-phase` | Clean artifacts for specified phases before run (e.g., 'D', 'BD') | `None` |
| `--target` | Target file ID(s) to process (repeatable) | `None` |
| `--yes` | Skip confirmation prompts | `False` |
| `--regen` | Detect source changes and regenerate affected files | `False` |
| `--dry-run` | Dry run (no file writes) | `False` |
| `--repo` | Repository root path (advanced) | `os.getcwd()` |

**Note**: Phases G and F are still available individually for backward compatibility, but Phase M (which combines merge, link resolution, and finalization) is now the default in the standard flow.

### テストモード

テスト設定ファイルで処理対象ソースファイルを指定する:

- **test-files-top3.json**: 最大 3 ファイル（セクション分割あり）— 成功基準検証向け
- **test-files-comprehensive.json**: main ブランチのナレッジファイルに対応する 17 ファイル

```bash
# 3 ファイルでテスト
python tools/knowledge-creator/run.py --version 6 --test test-files-top3.json

# 17 ファイルで総合テスト
python tools/knowledge-creator/run.py --version 6 --test test-files-comprehensive.json
```

### 特定フェーズのみ実行

```bash
# Phase B（生成）のみ
python tools/knowledge-creator/run.py --version 6 --phase B

# Phase C,D,E（検証・修正ループ）のみ
python tools/knowledge-creator/run.py --version 6 --phase CDE

# Phase M（最終化）のみ
python tools/knowledge-creator/run.py --version 6 --phase M

# 後方互換: Phase G,F（旧最終化）
python tools/knowledge-creator/run.py --version 6 --phase GF
```

### クリーンアップ

生成済みファイルを削除する:

```bash
# v6 をクリーン（確認プロンプトあり）
python tools/knowledge-creator/clean.py --version 6

# v6 をクリーン（確認スキップ）
python tools/knowledge-creator/clean.py --version 6 --yes

# v5 のみクリーン
python tools/knowledge-creator/clean.py --version 5

# 両バージョンをクリーン
python tools/knowledge-creator/clean.py --version all
```

## 開発ガイド

### テスト実行

```bash
# リポジトリルートから全テストを実行
python -m pytest tools/knowledge-creator/tests/ -v

# tools/knowledge-creator ディレクトリから実行
cd tools/knowledge-creator
pytest tests/ -v

# 特定テストファイルのみ実行
pytest tests/test_phase_c.py -v

# カバレッジ付きで実行
pytest tests/ --cov=steps --cov-report=html
```

### テストの種類

- **Unit Tests**: Phase C structure validation, split criteria logic, source change detection
- **Integration Tests**: Phase C/D/E/M integration, merge logic, pipeline flow
- **E2E Tests**: Full pipeline scenarios with split files, fix cycles

主なテストファイル:
- `tests/test_phase_c.py`: Phase C 構造チェック検証
- `tests/test_knowledge_meta.py`: ソース変更検知（git commit ベース）
- その他 Phase D/E/M のインテグレーション・E2E テスト

### ディレクトリ構成

```
tools/knowledge-creator/
  nc.sh                        # ユーザー向けラッパースクリプト
  run.py                       # メインエントリーポイント
  clean.py                     # 生成物クリーンアップユーティリティ
  steps/
    common.py                  # 共通ユーティリティ（JSON I/O、Claude API ラッパー）
    cleaner.py                 # フェーズ別成果物クリーンアップ
    knowledge_meta.py          # ソース変更検知（git commit ベース）
    step1_list_sources.py      # ソースファイル検索
    step2_classify.py          # ファイル分類・分割ロジック
    phase_b_generate.py        # Claude API によるナレッジ生成
    phase_c_structure_check.py # 構造検証（S1-S15）
    phase_d_content_check.py   # Claude API によるコンテンツ検証
    phase_e_fix.py             # Claude API による自動修正
    phase_m_finalize.py        # マージ → リンク解決 → 生成（オーケストレーター）
    merge.py                   # 分割ファイルマージロジック
    phase_g_resolve_links.py   # RST→Markdown リンク変換
    phase_f_finalize.py        # パターン分類、インデックス、ドキュメント生成
  tests/
    test_phase_c.py
    test_knowledge_meta.py
    ...

.claude/skills/nabledge-6/
  knowledge/                   # 最終成果物: ナレッジ JSON ファイル
    {type}/{category}/{file-id}.json
    index.toon                 # ナレッジファイルインデックス
  docs/                        # 閲覧可能な Markdown ファイル
    {type}/{category}/{file-id}.md
  plugin/
    knowledge-creator.json     # 生成時ソースリポジトリのコミット情報

tools/knowledge-creator/.logs/v6/  # 中間成果物（gitignore）
  sources.json                 # Phase A: ソースファイル一覧
  classified.json              # Phase A: 分類済みファイル一覧（分割情報含む）
  structure-check.json         # Phase C: 構造検証結果
  execution.log                # タイムスタンプ付き実行ログ
  phase-b/
    traces/{file-id}.json
    executions/{file-id}_{timestamp}.json
  phase-c/
    results.json
  phase-d/
    findings/{file-id}.json
    executions/{file-id}_{timestamp}.json
  phase-e/
    executions/{file-id}_{timestamp}.json
  phase-g/
    resolved/{type}/{category}/{file-id}.json
  summary.json
```

**Execution Metrics**: 各 `executions/` ディレクトリには AI コールの詳細メトリクスが含まれる:
- `num_turns`: エージェントターン数
- `duration_ms`: 実行時間
- `total_cost_usd`: API コスト
- `structured_output`: 生成コンテンツ

### アーキテクチャ方針

1. **Separation of Concerns**: 各フェーズは単一責任
2. **Split-Aware Processing**: 大きなファイルを早期に分割し、後で統合してコンテキストオーバーフローを防止
3. **Defensive Programming**: 出力サイズガード、不完全パート検出
4. **Observability**: 全 AI 操作の詳細メトリクスとトレース
5. **Idempotency**: フェーズの再実行が副作用なく安全に行える

## トラブルシューティング

### `nc.sh: permission denied`

→ スクリプトに実行権限を付与: `chmod +x tools/knowledge-creator/nc.sh`

### `FileNotFoundError: .lw/nab-official/v6/`

→ リポジトリルートディレクトリからコマンドを実行すること（`tools/knowledge-creator/` からではない）。

### `claude: command not found`

→ Claude CLI をインストールすること。AI コールなしでテストするには `--dry-run` オプションを使用。

### Phase E output too small warning

→ これは安全ガード。Phase E の出力が入力の 50% 未満に縮小した場合、データ消失防止のため修正を却下する。`.logs/v6/phase-e/executions/` でメトリクスを確認し、必要に応じて `--max-rounds` を調整。

### Max rounds reached without all files passing

→ `.logs/v6/phase-d/findings/` で継続的な問題を確認すること。一部の問題はソースドキュメントの手動修正またはプロンプト調整が必要な場合がある。

## 関連ドキュメント

- **Task Specification**: `doc/nabledge-creator-v2-task.md`
- **Split-Aware Pipeline**: `.pr/00107/split-aware-pipeline-tasks.md`
- **Mapping Files**: `doc/mapping/` (302 files)
- **Issue**: #106
- **PR**: #107

## Version History

- **v2.1** (PR #107): Added nc.sh wrapper, source change tracking, target filtering
- **v2.0** (PR #107): Split-aware pipeline with Phase M, context overflow prevention
- **v1.0** (PR #106): Initial implementation with Phases A-G
