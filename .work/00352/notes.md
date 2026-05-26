# Notes

## 2026-05-26

### Task 1: コミット分析結果

前回リリース: marketplace 0.8 (2026-03-30, commit `18f0f58ed`)
基準: `sync-manifest.txt` 記載のデプロイ対象パスに触れるコミット

#### ユーザー影響あり（10件）

| # | Hash | コミット | 影響プラグイン | 分類 |
|---|------|---------|--------------|------|
| 1 | `4f50306ed` | feat: allow nabledge scripts to run without permission prompts (#178) (#305) | v6/v5/v1.4/v1.3/v1.2 | スクリプト自動実行 (scripts/, GUIDE-CC.md, GUIDE-GHC.md, qa.md) |
| 2 | `8f37ab917` | feat: implement RBKC — rule-based knowledge creator (#299) (#304) | v6/v5/v1.4/v1.3/v1.2 | 知識ファイル全再生成 (docs/README.md, knowledge/index.toon, plugin CHANGELOG.md) |
| 3 | `087c2c8ef` | fix: per-section fix + severity lock + retry limit (#274) (#295) | v1.4/v1.3/v1.2/v5 | 知識ファイル品質修正 (docs/README.md, index.toon) |
| 4 | `393107610` | feat: improve nabledge-1.2 CA accuracy with prompt/template fixes (#277) (#288) | v1.2 | コード分析精度改善 (plugin/CHANGELOG.md, assets/, scripts/) |
| 5 | `c430898c9` | fix: convert handler docs raw HTML to Markdown tables for v1.x (#312) (#315) | v1.4/v1.3/v1.2 | 知識ファイル品質修正 (index.toon) |
| 6 | `7c6a2de2b` | fix: convert toctree entries to MD links in docs MD (#317) (#324) | v1.4/v1.3/v1.2 | 閲覧用MD品質修正 (docs/README.md, index.toon) |
| 7 | `931120c66` | fix: fix setting_guide mapping pattern in v6.json and v5.json (#318) (#328) | v6/v5 | 知識ファイル品質修正 (docs/README.md, index.toon) |
| 8 | `4945dfd94` | fix: broken link in v6 docs README for Nablarch 6u2 (#326) (#331) | v6 | リンク修正 (docs/README.md) |
| 9 | `2ecaddd68` | chore: regenerate v1.x knowledge and docs after .lw refresh (#336) (#337) | v1.4/v1.3/v1.2 | 知識ファイル再生成 (docs/README.md, index.toon) |
| 10 | `44f206e29` | feat: improve search quality with new semantic+keyword search (#343) (#346) | v6/v5/v1.4/v1.3/v1.2 | 検索品質改善 (SKILL.md, knowledge/index.md, workflows/qa.md, CC command, GHC prompt, scripts/) |
| 11 | `0b4fa8cdc` | fix: create .vscode/ dir before writing settings.json in setup-ghc.sh (#350) (#351) | 全バージョン共通 | セットアップスクリプト修正 (tools/setup/setup-ghc.sh) |

**合計: 11件**

#### ユーザー影響なし（主要なもの）

- `dacec0c72` verify設計書品質修正 → `.claude/rules/` のみ（デプロイ非対象）
- `f2310be42` verify品質エスケープハッチ除去 → `scripts/verify/` のみ（デプロイ非対象）
- `c16c053f9` scripts/common/ リファクタリング → `scripts/` のみ（verifyスクリプト、デプロイ非対象）
- `f2c54dcbf` QL1アンカーバリデーション → `docs/README.md`, `knowledge/index.toon` (閲覧用MDのみ変更、知識JSONは変更なし) ※デプロイ対象だがユーザー影響は閲覧用MD品質改善

**注**: f2c54dcbfは `docs/README.md` と `knowledge/index.toon` のみ変更。`index.toon` はデプロイ対象ディレクトリ内だが、これは閲覧用MDファイル（ユーザーが直接参照するわけではなくnabledgeスキルが参照する知識ファイルの索引）。ユーザー影響: あり（知識ファイルのリンク精度向上）。

#### [Unreleased] 内容との対応確認

各プラグインの `[Unreleased]` 内容と上記コミット分析との対応:

**nabledge-6**:
- 「スクリプト自動実行」← `4f50306ed` ✅
- 「知識ファイルルールベース変換」← `8f37ab917` ✅
- 未記載: `44f206e29`（検索品質改善）、`4945dfd94`（リンク修正）、`931120c66`（setting_guideマッピング修正）、`8f37ab917`に含まれる知識ファイル品質修正 → CHANGELOGに追加が必要か検討（Task 2で対処）

**nabledge-5**:
- 「知識ファイルルールベース変換」← `8f37ab917` ✅
- 未記載: `44f206e29`（検索品質改善）、`8f37ab917`関連品質修正 → Task 2で対処

**nabledge-1.4**:
- 「知識ファイルルールベース変換」← `8f37ab917` ✅
- 未記載: `44f206e29`（検索品質改善）、`087c2c8ef`、`c430898c9`、`7c6a2de2b`、`2ecaddd68` → Task 2で対処

**nabledge-1.3**:
- 「知識ファイルルールベース変換」← `8f37ab917` ✅
- 未記載: 上記と同様 → Task 2で対処

**nabledge-1.2**:
- 「知識ファイルルールベース変換」← `8f37ab917` ✅
- 「コード分析シーケンス図修正」「処理フロー修正」「出力ファイルパス追加」← `393107610` ✅
- 未記載: `44f206e29`（検索品質改善）、その他品質修正 → Task 2で対処
