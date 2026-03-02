# Add nabledge-creator tool for knowledge file management

Resolves #99

## 背景・目的

Nablarchの公式ドキュメント（RST/MD/Excel）をAIエージェントが検索・参照できる知識ファイル（JSON）に変換するツールを実装します。

**現状の課題：**
- 手動での知識ファイル作成は時間がかかり、ミスが発生しやすい
- 品質や一貫性を保つための標準化されたツールが存在しない
- v6では302ファイル、v5でも同規模のソースファイルを処理する必要がある

**ツールの特徴：**
- ルールベースの制約でAIの判断余地を最小化
- 生成と検証を分離（別セッション）してバイアスを排除
- 機械的チェック（17項目）とAIチェック（4観点）の組み合わせ
- 差分更新対応で2回目以降の更新を効率化

## アプローチ

### 6ステップの処理フロー

1. **ソースファイル一覧取得** - スクリプトで公式ドキュメントを走査
2. **Type/Category分類** - ディレクトリパスから機械的に分類
3. **知識ファイル生成** - claude -pで「漏れなく、盛らず」の原則で抽出
4. **インデックス生成** - 全知識ファイルのメタ情報を集約
5. **閲覧用Markdown生成** - JSONから人間向けMarkdownを変換
6. **検証** - 構造チェック（17項目）+ 内容検証（4観点）

### 技術選択

- **言語**: Python 3（既存環境と統一）
- **並行処理**: `concurrent.futures`（標準ライブラリ）
- **AIモデル**: Sonnet 4.5（全ステップ共通）
- **出力形式**: JSON Schema定義による構造化出力

### 品質担保

- **17項目の構造チェック**: JSON構造、必須フィールド、URL有効性、hints網羅性など
- **4観点の内容検証**: 情報の漏れ・捏造・セクション分割・検索ヒント品質
- **fail時は修正必須**: すべての項目でpassになるまで繰り返し

## タスクリスト

### Phase 1: プロジェクト構造とコア機能

- [ ] ディレクトリ構造作成（tools/knowledge-creator/）
- [ ] run.py実装（メインエントリポイント、引数解析）
- [ ] Step 1実装（1_list_sources.py: ソースファイル走査）
- [ ] Step 2実装（2_classify.py: Type/Category分類）

### Phase 2: AI生成機能

- [ ] claude -p呼び出しユーティリティ実装
- [ ] Step 3プロンプトテンプレート作成（prompts/generate.md）
- [ ] Step 3実装（3_generate.py: 知識ファイル生成、並行処理対応）
- [ ] Step 4プロンプトテンプレート作成（prompts/classify_patterns.md）
- [ ] Step 4実装（4_build_index.py: index.toon生成）

### Phase 3: ドキュメント生成と検証

- [ ] Step 5実装（5_generate_docs.py: 閲覧用MD生成）
- [ ] Step 6プロンプトテンプレート作成（prompts/validate.md）
- [ ] Step 6実装（6_validate.py: 構造チェック17項目）
- [ ] Step 6実装（6_validate.py: 内容検証4観点、claude -p使用）

### Phase 4: 動作確認とドキュメント

- [ ] 小規模テスト（1-2ファイルで全ステップ実行）
- [ ] エラーハンドリングと再開処理の確認
- [ ] ログ出力の動作確認
- [ ] README.md作成（使い方、オプション、トラブルシューティング）

### Phase 5: Success Criteria検証

- [ ] SC1: 既存知識ファイルの削除確認（完了済み）
- [ ] SC2: nabledge-creatorツールの機能確認
- [ ] SC3: 設計書に基づく実装の確認
- [ ] SC4: nabledge-6とnabledge-5対応の確認
- [ ] SC5: エラーメッセージとバリデーションの確認
- [ ] SC6: ドキュメント（README.md）の確認
- [ ] SC7: 全知識ファイル再生成の実行と確認

## Expert Review

*Expert review will be conducted before PR creation*

## Success Criteria検証

### ✅ SC1: Delete all existing knowledge files before starting implementation

**Status**: Completed
- Deleted 17 JSON knowledge files from `.claude/skills/nabledge-6/knowledge/`
- Deleted 18 Markdown files from `.claude/skills/nabledge-6/docs/`
- Deleted `index.toon`

### ⬜ SC2: nabledge-creator tool is created and functional

**Verification**:
- [ ] `python tools/knowledge-creator/run.py --version 6 --dry-run` executes without errors
- [ ] All 6 steps can be executed individually with `--step` option
- [ ] Tool handles errors gracefully and provides clear error messages

### ⬜ SC3: Implementation follows design document provided by user at work start

**Verification**:
- [ ] File structure matches `doc/99-nabledge-creator-tool/knowledge-creator-design.md`
- [ ] All 6 steps implemented according to specifications
- [ ] Prompt templates follow design patterns
- [ ] Validation checks include all 17 structure items and 4 content aspects

### ⬜ SC4: Tool supports nabledge-6 and nabledge-5 knowledge file creation

**Verification**:
- [ ] `--version 6` processes v6 source files correctly
- [ ] `--version 5` processes v5 source files correctly
- [ ] `--version all` processes both versions
- [ ] Output paths follow pattern: `.claude/skills/nabledge-{6,5}/knowledge/`

### ⬜ SC5: Tool provides clear error messages and validation

**Verification**:
- [ ] 17 structure checks report clear pass/fail status
- [ ] 4 content validation aspects provide actionable feedback
- [ ] Logs saved to `tools/knowledge-creator/logs/v{version}/` with file-level detail
- [ ] `summary.json` provides overall status

### ⬜ SC6: Documentation includes usage examples and workflow guide

**Verification**:
- [ ] `tools/knowledge-creator/README.md` exists and covers:
  - Processing flow (6 steps)
  - Basic usage examples
  - Options documentation (`--version`, `--step`, `--concurrency`, `--dry-run`)
  - Resume and differential update behavior
  - Troubleshooting guide for validation failures
  - Log structure explanation

### ⬜ SC7: All knowledge files are recreated from scratch using the tool

**Verification**:
- [ ] Run `python tools/knowledge-creator/run.py --version 6` completes successfully
- [ ] Knowledge files generated in `.claude/skills/nabledge-6/knowledge/`
- [ ] `index.toon` generated with correct structure
- [ ] Docs generated in `.claude/skills/nabledge-6/docs/`
- [ ] All validation checks pass (17 structure + 4 content)
- [ ] Compare file count with mapping (302 files for v6)

## 実装方針

1. **段階的実装**: Phase 1→2→3→4の順で実装し、各フェーズで動作確認
2. **小規模テスト優先**: 1-2ファイルで全ステップを確認してから本番実行
3. **不明点は質問**: 設計書の解釈が不明確な場合は推測せず確認
4. **既存参照禁止**: 削除した既存知識ファイルは参考にしない

## 補足

### ソースファイル規模

- **v6**: 約302ファイル（公式解説書RST、パターン集MD、セキュリティ対応表Excel）
- **v5**: 同規模を想定

### 処理時間の見積もり

- Step 3（生成）: 1ファイル約30秒（claude -p起動含む）
- 並行数4の場合: 302ファイル ÷ 4 × 30秒 = 約38分
- 全ステップ合計: 約45-60分（初回実行時）
