# Issue #133: knowledge file output path bug の修正

## 目的

knowledge-creator実行時に、リポジトリルートに迷子ディレクトリ（`component/`, `processing-pattern/` 等）が出力される問題を解消する。

## 原因

`claude -p` はエージェントとして動作し、プロンプト内のパス情報と出力指示を解釈してWriteツール等でファイルを書き込む可能性がある。

`--json-schema` はSDK/CLI側のconstrained decodingでエージェントの最終出力をスキーマに沿わせるもの。エージェント自身は `--json-schema` の存在を知らず、プロンプトの指示に従って行動する。tool use（ファイル書き込み等）は制限されない（公式: "Grammar scope: Grammars apply only to Claude's direct output, not to tool use calls"）。

現在のプロンプト（generate.md）には以下が含まれている:

- `- Output Path: \`component/handlers/xxx.json\``（相対パス）
- `Output the JSON matching the schema above.`（出力指示）

エージェントがこれを「このパスにJSONをファイルとして出力しろ」と解釈し、CWD（リポジトリルート）に相対パスでファイルを書き込んだ結果、`component/` 等のディレクトリがリポジトリルートに生成された。

## 修正箇所

修正対象は `generate.md` と `phase_b_generate.py` のパス情報、および全4プロンプトの出力指示の表現。`content_check.md` の `{SOURCE_PATH}`（line 10）は検証に必要な情報のため今回は変更しない。

### 修正1: `prompts/generate.md` — 不要なパス情報の削除

`Output Path` と `Assets Directory` はWork Step 1〜7で参照されておらず不要。エージェントのファイル書き込みを誘発する原因。

**Before**:
```
- Output Path: `{OUTPUT_PATH}`
- Assets Directory: `{ASSETS_DIR}`
- Official Doc Base URL: `{OFFICIAL_DOC_BASE_URL}`
```

**After**:
```
- Official Doc Base URL: `{OFFICIAL_DOC_BASE_URL}`
```

### 修正2: `steps/phase_b_generate.py` — 対応する置換コードの削除

修正1でプロンプトから `{OUTPUT_PATH}` と `{ASSETS_DIR}` を削除するため、置換コードも削除する。`{SOURCE_PATH}` の置換（line 96）はgenerate.md内にプレースホルダが存在しないため空振りしているが、今回は合わせて削除する。

**Before**:
```python
        prompt = prompt.replace("{OUTPUT_PATH}", file_info["output_path"])
        prompt = prompt.replace("{SOURCE_PATH}", file_info["source_path"])
        prompt = prompt.replace("{ASSETS_DIR}", file_info["assets_dir"])
```

**After**:
```
（3行とも削除）
```

### 修正3: 全プロンプトの出力指示の表現変更

「Output」がエージェントのファイル書き込みを誘発しうるため、「Respond with」に変更する。

#### prompts/generate.md

**Before**:
```
Output the JSON matching the schema above. No explanation, no markdown fences, no other text.
```

**After**:
```
Respond with the JSON matching the schema above. No explanation, no markdown fences, no other text.
```

#### prompts/content_check.md

**Before**:
```
Report all findings as JSON matching the provided schema.
```

**After**:
```
Respond with the findings as JSON matching the provided schema.
```

#### prompts/fix.md

**Before**:
```
Output the entire corrected knowledge file JSON matching the schema defined in generate.md (knowledge file structure with index[], sections{}, source{}, assets{} fields).
```

**After**:
```
Respond with the entire corrected knowledge file as JSON matching the schema defined in generate.md (knowledge file structure with index[], sections{}, source{}, assets{} fields).
```

#### prompts/classify_patterns.md

**Before**:
```
Output the result as JSON matching the provided schema.
```

**After**:
```
Respond with the result as JSON matching the provided schema.
```

## 検証手順

### 1. 既存テスト

```bash
cd tools/knowledge-creator
python -m pytest tests/ -v
```

全テストがパスすることを確認する（現状108 passed, 7 skipped）。テストは `run_claude` をmockしているため、プロンプト変更とPythonコード変更のどちらもテスト結果に影響しない。

### 2. 迷子ファイルの非発生確認

テストモードでPhase Bを実行し、リポジトリルートに新規ディレクトリが増えないことを確認する:

```bash
ls -d */ > /tmp/dirs_before.txt
./tools/knowledge-creator/nc.sh gen 6 --test test-files-top3.json --yes
ls -d */ > /tmp/dirs_after.txt
diff /tmp/dirs_before.txt /tmp/dirs_after.txt
```

diff出力が空であれば成功。
