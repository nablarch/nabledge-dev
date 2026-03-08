# Knowledge Creator

Nablarch公式ドキュメント（RST/MD/Excel）をAI用ナレッジファイル（JSON）に変換するマルチフェーズパイプライン。

```mermaid
flowchart TD
    Start([Start]) --> A[Phase A: Preparation]
    A --> |catalog.json 永続保存<br/>split 状態| B[Phase B: Generation]
    B --> |knowledge_cache_dir<br/>split JSON 生成| C[Phase C: Structure Check]
    C --> |S1-S16 Validation| PassC{Structure<br/>Errors?}
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
    M --> |1. delete-insert knowledge_dir<br/>2. Merge Split Files<br/>3. Resolve RST Links<br/>4. Generate Docs<br/>5. Restore split catalog| Complete([Complete])

    style Start fill:#e1f5e1
    style Complete fill:#e1f5e1
    style RerunB fill:#fff3cd
    style RerunCDE fill:#fff3cd
    style StructWarn fill:#fff3cd
    style M fill:#e1e5ff
```

### フェーズ詳細

| フェーズ | 処理内容 | 種別 | 並列 |
|----------|----------|------|------|
| **A: Preparation** | ソースファイルの一覧・分類・分割 | Python | No |
| **B: Generation** | Claude APIによるナレッジJSON生成 | AI | Yes |
| **C: Structure Check** | JSON構造バリデーション（S1-S16） | Python | No |
| **D: Content Check** | Claude APIによるコンテンツ検証 | AI | Yes |
| **E: Fix** | Phase Dで検出した問題の自動修正 | AI | Yes |
| **M: Finalization** | 分割ファイル統合 → RSTリンク解決 → インデックス・ドキュメント生成 | Hybrid | No |

Phase C→D→Eは `--max-rounds` 回（デフォルト: 2、最大: 10）まで繰り返す。

## セットアップ

```bash
cd /path/to/nabledge-dev
./setup.sh
source ~/.bashrc
```

## 運用コマンド

### kc.sh

| 用途 | コマンド |
|------|---------|
| 全件生成 | `./kc.sh gen 6` |
| 中断再開 | `./kc.sh gen 6 --resume` |
| ソース変更追随 | `./kc.sh regen 6` |
| 特定ファイル再生成 | `./kc.sh regen 6 --target FILE_ID` |
| 品質改善 | `./kc.sh fix 6` |
| 特定ファイル修正 | `./kc.sh fix 6 --target FILE_ID` |

FILE_ID はナレッジファイルの拡張子なしファイル名（例: `handlers-data_read_handler`）。`.claude/skills/nabledge-6/knowledge/` 配下で確認できる。分割ファイルの場合は元ファイルのベースID（例: `testing-framework-http_send_sync`）を指定すると、全分割パートが対象になる。

### オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--version` | バージョン（6, 5, all） | **必須** |
| `--resume` | 中断再開（genのみ） | - |
| `--target FILE_ID` | 対象ファイル指定（複数可） | 全件 |
| `--yes` | 確認プロンプトスキップ | `False` |
| `--dry-run` | ドライラン | `False` |
| `--max-rounds N` | CDEループ回数 | `2` |
| `--concurrency N` | 並列数 | `4` |
| `--test FILE` | テストファイル指定 | `None` |
| `--verbose` | CC詳細ログ出力（stream-json + ツール呼び出し記録） | `False` |

### テストモードファイル

`tests/mode/` 配下。`--test` オプションにファイル名を指定する。

| ファイル | 内容 |
|---------|------|
| `largest3.json` | 最大3ファイル（分割後22エントリー）— 高速検証向け |
| `smallest3.json` | 最小3ファイル — 最速検証向け |
| `batch.json` | main branch準拠の37ファイル（分割後51エントリー） |

## ディレクトリ構造

```
tools/knowledge-creator/
├── .cache/v6/
│   ├── catalog.json          # Phase A が生成・永続保存（常に split 状態）
│   ├── knowledge/            # Phase B/C/D/E の作業ディレクトリ（split 状態）
│   │   ├── component/
│   │   ├── development-tools/
│   │   └── ...
│   └── traces/               # Phase B 生成トレース
└── .logs/v6/                 # 実行ログ（gitignore）
    └── {timestamp}/
        ├── phase-a/
        ├── phase-b/
        └── ...

.claude/skills/nabledge-6/
└── knowledge/                # Phase M の出力（merge 済み、delete-insert で更新）
    ├── component/
    ├── development-tools/
    └── ...
```

**knowledge_cache_dir** と **knowledge_dir** の役割分担:

| ディレクトリ | 書き込みフェーズ | 状態 | 用途 |
|-------------|----------------|------|------|
| `.cache/v6/knowledge/` | Phase B/C/D/E | split（分割あり） | 生成・検証・修正の作業領域 |
| `.claude/skills/nabledge-6/knowledge/` | Phase M のみ | merged（統合済み） | スキルが参照する最終成果物 |

Phase M は `knowledge_dir` を delete-insert で更新する:
1. `knowledge_dir` を全削除
2. キャッシュから split ファイルを統合し `knowledge_dir` に書き込み
3. RSTリンク解決・インデックス生成
4. `catalog.json` を split 状態に復元

## 開発ガイド

### テスト種類

- **Unit Tests**: Phase C構造バリデーション、分割ロジック等
- **Integration Tests**: Phase C/D/E/M統合、マージ、パイプラインフロー
- **E2E Tests**: 分割ファイル・修正サイクルを含むフルパイプライン

### テスト実行

```bash
cd tools/knowledge-creator

# 全テスト
pytest tests/ -v

# テストモード実行
python scripts/run.py --version 6 --test smallest3.json
```
