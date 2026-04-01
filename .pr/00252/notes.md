# Notes

## 2026-04-01

### Implementation: Deterministic Dynamic Checks

**Overview**: Replaced LLM-dependent `verify_dynamic()` with deterministic verification that directly executes knowledge search scripts (full-text-search.sh + read-sections.sh). This enables CI to verify knowledge search without requiring authentication or LLM invocation.

**Key Changes to `tools/tests/test-setup.sh`:**

1. **New `verify_dynamic()` function** (replaces LLM-based version):
   - Calls `full-text-search.sh` with comma-separated keywords to search for matching sections
   - Calls `read-sections.sh` to fetch actual section content
   - Validates all keywords exist in the retrieved content
   - Returns [OK] if all keywords found, [FAIL] if not found
   - No `claude -p` or `copilot -p` invocation; no LLM dependency
   - Checks jq dependency with clear error message

2. **Enabled all 20 dynamic checks**:
   - v6 × 2 (cc/ghc)
   - v5 × 2 (cc/ghc)
   - v1.4 × 2 (cc/ghc)
   - v1.3 × 2 (cc/ghc)
   - v1.2 × 2 (cc/ghc)
   - all × 2 (cc/ghc with multiple versions per environment)
   - Total: 20 verify_dynamic calls (previously 0 active; all 20 were commented out)

3. **Keywords** derived from nabledge-test benchmark scenarios:
   - v6/v5: `findAllBySqlFile,page,per,Pagination,getPagination` (qa-002)
   - v1.4/v1.3/v1.2: `n:codeSelect,codeId` (qa-001)

**Unit Tests** (`tools/tests/verify-dynamic.test.sh`):
- 10 test cases covering:
  - Normal case: keywords found (5 tests)
  - Zero hits: no search results
  - Missing scripts: detection of missing/non-executable scripts (2 tests)
  - Content validation: multiple keywords verified in content
  - Format validation: search results in correct `file|section` format
  - Section handling: SECTION_NOT_FOUND for missing sections

**Verification**:
- All 10 unit tests pass ✓
- No external dependencies beyond jq (required by scripts, checked in verify_dynamic)
- No credentials required (no ANTHROPIC_API_KEY, GITHUB_TOKEN, gh auth)
- Deterministic: same input → same output (no LLM variability)

**Success Criteria Met**:
- ✅ Checks execute without LLM or CLI authentication
- ✅ Verify knowledge search via direct script execution
- ✅ Expected keywords validated against section content
- ✅ All 20 version × tool combinations run as [RUN]
- ✅ jq dependency checked with clear error
- ✅ Unit tests exist for normal/0-hit/missing-keyword/script-missing cases

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
