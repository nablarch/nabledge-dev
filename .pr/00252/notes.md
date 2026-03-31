# Notes

## 2026-03-31

### 検証: headless /n6 実行方式

#### CC (Claude Code)

スラッシュコマンド `/n6` は `-p` モードで動作する（`--disable-slash-commands` オプションが存在することから、デフォルト有効）。

**確定コマンド:**
```bash
claude -p '/n6 "質問"' --model haiku
```

- `--allowedTools` 等の追加フラグは不要
- 所要時間: 約52秒

#### GHC (GitHub Copilot CLI)

GHC のスラッシュコマンドは `.github/prompts/n6.prompt.md` を使用。
`n6.prompt.md` の `$ARGUMENTS` を質問に置換して `-p` に直接渡す方式を採用。

**確定コマンド:**
```bash
PROMPT="$(sed 's|$ARGUMENTS|質問|g' .github/prompts/n6.prompt.md)"
copilot -p "$PROMPT" --model claude-haiku-4.5 --allow-tool Bash --autopilot
```

**調査過程で判明した事項:**

- `n6.prompt.md` の `#runSubagent` は LLM へのヒントであり、内部的に `task` ツール (`mode: "background"`) を呼び出す
- `-p` 単体では1ターンで終了するため、サブエージェントの結果を受け取れない
- `--autopilot` を付けることで複数ターン継続し、`read_agent` でサブエージェント完了後の結果を取得できる
- `--allow-tool Bash` がないと grep/find が Permission denied になり、ファイルを1件ずつ読む迂回処理が発生して遅くなる（タイムアウト超過）
- `--allow-tool Bash` + `--autopilot` の組み合わせで60秒以内に完了

**GHC のトークン変数優先度:** `COPILOT_GITHUB_TOKEN` > `GH_TOKEN` > `GITHUB_TOKEN`
**`gh` コマンドとの分離:** `COPILOT_GITHUB_TOKEN` は GHC 専用（`gh` コマンドは無視）なので別々の PAT を指定可能

**モデル名:** GHC では `claude-haiku-4.5`（CC の `claude-haiku-4-5-20251001` とは異なる）
