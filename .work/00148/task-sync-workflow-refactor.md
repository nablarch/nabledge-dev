# タスク: sync-to-nabledge ワークフローのリファクタリング

## 目的

nabledge-dev → nabledge リポジトリへの同期ワークフローを、マッピング定義ファイル駆動に再設計する。あわせて、ワークフローで使うスクリプトをワークフロー単位のディレクトリにグルーピングする。

## 結論

現在3つのスクリプト（`clean-repository.sh`, `transform-to-plugin.sh`, `validate-marketplace.sh`）とワークフロー内のインラインステップに分散していた配布ファイル定義を、1つのマッピング定義ファイル `sync-manifest.txt` に集約する。同期処理は `sync.sh` 1本に統合する。バリデーションはマッピング定義ファイルから自動導出するため、別スクリプト不要。

スクリプトは `.github/workflows/sync-to-nabledge/` にグルーピングし、ワークフローとスクリプトの対応関係を明確にする。

## あるべき姿

### 処理フロー

1. nabledge-repo を checkout
2. nabledge-repo 内の `.git` 以外を全削除（デリートインサート）
3. `sync-manifest.txt` を読み、各行に従ってコピー
4. コピー結果を `sync-manifest.txt` と突合してバリデーション
5. commit & push

### ファイル構成（変更後）

```
.github/
  workflows/
    sync-to-nabledge.yml                  # 簡素化
    sync-to-nabledge/                     # ワークフロー専用ディレクトリ
      sync.sh                             # NEW: 統合スクリプト（clean + transform + validate）
      sync-manifest.txt                   # NEW: マッピング定義
      capture-commit-message.sh           # 移動（元 .github/scripts/）
      build-commit-body.sh                # 移動（元 .github/scripts/）
      commit-and-push.sh                  # 移動（元 .github/scripts/）
  scripts/
    create-version-tag.sh                 # 変更なし（未使用、将来用）
    validate-version-updates.sh           # 変更なし（未使用、将来用）
```

## 作業手順

以下の順序で実行する。全6ステップ。各ステップ末尾の検証コマンドが全て成功してから次に進む。

---

### Step 1: ディレクトリを作成し、既存スクリプトを移動

```bash
mkdir -p .github/workflows/sync-to-nabledge

git mv .github/scripts/capture-commit-message.sh .github/workflows/sync-to-nabledge/
git mv .github/scripts/build-commit-body.sh .github/workflows/sync-to-nabledge/
git mv .github/scripts/commit-and-push.sh .github/workflows/sync-to-nabledge/
```

**検証:**
```bash
test -f .github/workflows/sync-to-nabledge/capture-commit-message.sh && echo "OK" || echo "FAIL"
test -f .github/workflows/sync-to-nabledge/build-commit-body.sh && echo "OK" || echo "FAIL"
test -f .github/workflows/sync-to-nabledge/commit-and-push.sh && echo "OK" || echo "FAIL"
test ! -f .github/scripts/capture-commit-message.sh && echo "OK" || echo "FAIL"
test ! -f .github/scripts/build-commit-body.sh && echo "OK" || echo "FAIL"
test ! -f .github/scripts/commit-and-push.sh && echo "OK" || echo "FAIL"
```

---

### Step 2: sync-manifest.txt を作成

**重要: タブ区切り（TSV）ファイル。カラム間はタブ文字1個。スペースではない。**

以下のコマンドで作成する（`printf` でタブ文字を確実に挿入する）:

```bash
cat > .github/workflows/sync-to-nabledge/sync-manifest.txt << 'MANIFEST_EOF'
# sync-manifest.txt
# nabledge-dev -> nabledge repository distribution file mapping
#
# Format: TYPE<TAB>SOURCE<TAB>DEST
# TYPE: file (single file copy), dir (recursive directory copy)
# SOURCE: relative path in nabledge-dev
# DEST: relative path in nabledge repo

MANIFEST_EOF

# Append entries with literal tab characters using printf
{
  printf '%s\t%s\t%s\n' '# --- Marketplace root ---' '' ''
  printf '%s\t%s\t%s\n' 'file' '.claude/marketplace/.claude-plugin/marketplace.json' '.claude-plugin/marketplace.json'
  printf '%s\t%s\t%s\n' 'file' '.claude/marketplace/README.md' 'README.md'
  printf '%s\t%s\t%s\n' 'file' '.claude/marketplace/CHANGELOG.md' 'CHANGELOG.md'
  printf '%s\t%s\t%s\n' 'file' '.claude/marketplace/LICENSE' 'LICENSE'
  echo ''
  printf '%s\t%s\t%s\n' '# --- nabledge-6 plugin metadata ---' '' ''
  printf '%s\t%s\t%s\n' 'file' '.claude/skills/nabledge-6/plugin/plugin.json' 'plugins/nabledge-6/.claude-plugin/plugin.json'
  printf '%s\t%s\t%s\n' 'file' '.claude/skills/nabledge-6/plugin/README.md' 'plugins/nabledge-6/README.md'
  printf '%s\t%s\t%s\n' 'file' '.claude/skills/nabledge-6/plugin/CHANGELOG.md' 'plugins/nabledge-6/CHANGELOG.md'
  printf '%s\t%s\t%s\n' 'file' '.claude/skills/nabledge-6/plugin/GUIDE-CC.md' 'plugins/nabledge-6/GUIDE-CC.md'
  printf '%s\t%s\t%s\n' 'file' '.claude/skills/nabledge-6/plugin/GUIDE-GHC.md' 'plugins/nabledge-6/GUIDE-GHC.md'
  echo ''
  printf '%s\t%s\t%s\n' '# --- nabledge-6 skill content ---' '' ''
  printf '%s\t%s\t%s\n' 'file' '.claude/skills/nabledge-6/SKILL.md' 'plugins/nabledge-6/skills/nabledge-6/SKILL.md'
  printf '%s\t%s\t%s\n' 'dir' '.claude/skills/nabledge-6/workflows' 'plugins/nabledge-6/skills/nabledge-6/workflows'
  printf '%s\t%s\t%s\n' 'dir' '.claude/skills/nabledge-6/assets' 'plugins/nabledge-6/skills/nabledge-6/assets'
  printf '%s\t%s\t%s\n' 'dir' '.claude/skills/nabledge-6/knowledge' 'plugins/nabledge-6/skills/nabledge-6/knowledge'
  printf '%s\t%s\t%s\n' 'dir' '.claude/skills/nabledge-6/docs' 'plugins/nabledge-6/skills/nabledge-6/docs'
  printf '%s\t%s\t%s\n' 'dir' '.claude/skills/nabledge-6/scripts' 'plugins/nabledge-6/skills/nabledge-6/scripts'
  echo ''
  printf '%s\t%s\t%s\n' '# --- CC command ---' '' ''
  printf '%s\t%s\t%s\n' 'file' '.claude/commands/n6.md' 'plugins/nabledge-6/commands/n6.md'
  echo ''
  printf '%s\t%s\t%s\n' '# --- GHC prompt ---' '' ''
  printf '%s\t%s\t%s\n' 'file' '.github/prompts/n6.prompt.md' 'plugins/nabledge-6/.github/prompts/n6.prompt.md'
  echo ''
  printf '%s\t%s\t%s\n' '# --- Setup scripts ---' '' ''
  printf '%s\t%s\t%s\n' 'file' 'tools/setup/setup-6-cc.sh' 'setup-6-cc.sh'
  printf '%s\t%s\t%s\n' 'file' 'tools/setup/setup-6-ghc.sh' 'setup-6-ghc.sh'
} >> .github/workflows/sync-to-nabledge/sync-manifest.txt
```

**検証:**
```bash
# フォーマットチェック: コメント/空行以外は全て3カラム（タブ区切り）
awk -F'\t' '!/^#/ && !/^$/ && NF != 3 { print "FAIL line " NR ": expected 3 columns, got " NF; exit 1 }' .github/workflows/sync-to-nabledge/sync-manifest.txt && echo "OK: format"

# TYPE が file または dir のみ
awk -F'\t' '!/^#/ && !/^$/ && $1 != "file" && $1 != "dir" { print "FAIL line " NR ": unknown type: " $1; exit 1 }' .github/workflows/sync-to-nabledge/sync-manifest.txt && echo "OK: types"

# エントリ数が 18 であること（file 13 + dir 5）
ENTRY_COUNT=$(awk -F'\t' '!/^#/ && !/^$/ { count++ } END { print count }' .github/workflows/sync-to-nabledge/sync-manifest.txt)
test "$ENTRY_COUNT" -eq 19 && echo "OK: entry count = $ENTRY_COUNT" || echo "FAIL: entry count = $ENTRY_COUNT (expected 19)"

# SOURCE が全て存在する
awk -F'\t' '!/^#/ && !/^$/ { print $1 "\t" $2 }' .github/workflows/sync-to-nabledge/sync-manifest.txt | while IFS=$(printf '\t') read -r type source; do
  if [ "$type" = "file" ] && [ ! -f "$source" ]; then
    echo "FAIL: source file not found: $source"; exit 1
  elif [ "$type" = "dir" ] && [ ! -d "$source" ]; then
    echo "FAIL: source dir not found: $source"; exit 1
  fi
done && echo "OK: all sources exist"
```

---

### Step 3: sync.sh を作成

以下の内容でファイルを作成する:

ファイル: `.github/workflows/sync-to-nabledge/sync.sh`

```bash
#!/bin/bash
set -euo pipefail

# Sync nabledge-dev files to nabledge repository using manifest
# Usage: sync.sh <source-dir> <dest-dir> <manifest-file>

SOURCE_DIR="${1:-}"
DEST_DIR="${2:-}"
MANIFEST="${3:-}"

if [ -z "$SOURCE_DIR" ] || [ -z "$DEST_DIR" ] || [ -z "$MANIFEST" ]; then
  echo "Error: All 3 arguments required"
  echo "Usage: $0 <source-dir> <dest-dir> <manifest-file>"
  exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Error: Source directory not found: $SOURCE_DIR"
  exit 1
fi

if [ ! -d "$DEST_DIR" ]; then
  echo "Error: Destination directory not found: $DEST_DIR"
  exit 1
fi

if [ ! -f "$MANIFEST" ]; then
  echo "Error: Manifest file not found: $MANIFEST"
  exit 1
fi

# Resolve to absolute paths to avoid issues with cd
SOURCE_DIR=$(cd "$SOURCE_DIR" && pwd)
DEST_DIR=$(cd "$DEST_DIR" && pwd)
MANIFEST=$(cd "$(dirname "$MANIFEST")" && echo "$(pwd)/$(basename "$MANIFEST")")

# --- Phase 1: Clean destination (.git 以外を全削除) ---
echo "Phase 1: Cleaning destination directory..."
find "$DEST_DIR" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
echo "  Done"

# --- Phase 2: Copy files according to manifest ---
echo "Phase 2: Copying files..."
LINE_NUM=0
while IFS= read -r line || [ -n "$line" ]; do
  LINE_NUM=$((LINE_NUM + 1))
  line=$(echo "$line" | tr -d '\r')

  # Skip comments and empty lines
  case "$line" in
    \#*|"") continue ;;
  esac

  # Parse TSV: TYPE SOURCE DEST
  TYPE=$(echo "$line" | cut -f1)
  SOURCE=$(echo "$line" | cut -f2)
  DEST=$(echo "$line" | cut -f3)

  # Validate column count
  COL_COUNT=$(echo "$line" | awk -F'\t' '{ print NF }')
  if [ "$COL_COUNT" -ne 3 ]; then
    echo "Error: Line $LINE_NUM: expected 3 columns, got $COL_COUNT"
    exit 1
  fi

  SRC_PATH="$SOURCE_DIR/$SOURCE"
  DST_PATH="$DEST_DIR/$DEST"

  case "$TYPE" in
    file)
      if [ ! -f "$SRC_PATH" ]; then
        echo "Error: Line $LINE_NUM: source file not found: $SRC_PATH"
        exit 1
      fi
      mkdir -p "$(dirname "$DST_PATH")"
      cp "$SRC_PATH" "$DST_PATH"
      echo "  file: $SOURCE -> $DEST"
      ;;
    dir)
      if [ ! -d "$SRC_PATH" ]; then
        echo "Error: Line $LINE_NUM: source dir not found: $SRC_PATH"
        exit 1
      fi
      mkdir -p "$DST_PATH"
      cp -r "$SRC_PATH/." "$DST_PATH/"
      echo "  dir:  $SOURCE -> $DEST"
      ;;
    *)
      echo "Error: Line $LINE_NUM: unknown type: $TYPE"
      exit 1
      ;;
  esac
done < "$MANIFEST"
echo "  Done"

# --- Phase 3: Validate copied files ---
echo "Phase 3: Validating..."
ERRORS=0
while IFS= read -r line || [ -n "$line" ]; do
  line=$(echo "$line" | tr -d '\r')

  case "$line" in
    \#*|"") continue ;;
  esac

  TYPE=$(echo "$line" | cut -f1)
  DEST=$(echo "$line" | cut -f3)
  DST_PATH="$DEST_DIR/$DEST"

  case "$TYPE" in
    file)
      if [ ! -f "$DST_PATH" ]; then
        echo "  FAIL: file not found: $DEST"
        ERRORS=$((ERRORS + 1))
      fi
      ;;
    dir)
      if [ ! -d "$DST_PATH" ]; then
        echo "  FAIL: dir not found: $DEST"
        ERRORS=$((ERRORS + 1))
      elif [ -z "$(find "$DST_PATH" -type f | head -1)" ]; then
        echo "  FAIL: dir is empty: $DEST"
        ERRORS=$((ERRORS + 1))
      fi
      ;;
  esac
done < "$MANIFEST"

# JSON syntax check
echo "  Checking JSON syntax..."
JSON_ERRORS=0
while IFS= read -r json_file; do
  if ! jq empty "$json_file" 2>/dev/null; then
    echo "  FAIL: invalid JSON: $json_file"
    JSON_ERRORS=$((JSON_ERRORS + 1))
  fi
done < <(find "$DEST_DIR" -name '*.json' -type f)

TOTAL_ERRORS=$((ERRORS + JSON_ERRORS))
if [ "$TOTAL_ERRORS" -ne 0 ]; then
  echo "Validation failed with $TOTAL_ERRORS error(s)"
  exit 1
fi

echo "  Done"
echo "Sync completed successfully"
```

作成後、実行権限を付与する:
```bash
chmod +x .github/workflows/sync-to-nabledge/sync.sh
```

**検証:**
```bash
test -x .github/workflows/sync-to-nabledge/sync.sh && echo "OK: exists and executable" || echo "FAIL"
head -1 .github/workflows/sync-to-nabledge/sync.sh | grep -q '#!/bin/bash' && echo "OK: shebang" || echo "FAIL"
grep -q 'set -euo pipefail' .github/workflows/sync-to-nabledge/sync.sh && echo "OK: strict mode" || echo "FAIL"
grep -q 'Phase 1' .github/workflows/sync-to-nabledge/sync.sh && echo "OK: Phase 1 present" || echo "FAIL"
grep -q 'Phase 2' .github/workflows/sync-to-nabledge/sync.sh && echo "OK: Phase 2 present" || echo "FAIL"
grep -q 'Phase 3' .github/workflows/sync-to-nabledge/sync.sh && echo "OK: Phase 3 present" || echo "FAIL"
```

---

### Step 4: sync-to-nabledge.yml を書き換え

以下のコマンドでファイル全体を置き換える:

```bash
cat > .github/workflows/sync-to-nabledge.yml << 'WORKFLOW_EOF'
name: Sync to nabledge repository

on:
  push:
    branches:
      - main

jobs:
  sync:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout nabledge-dev
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Checkout nabledge repository
        uses: actions/checkout@v4
        with:
          repository: nablarch/nabledge
          ref: develop
          token: ${{ secrets.NABLEDGE_SYNC_TOKEN }}
          path: nabledge-repo

      - name: Sync plugin files
        run: .github/workflows/sync-to-nabledge/sync.sh . nabledge-repo .github/workflows/sync-to-nabledge/sync-manifest.txt

      - name: Capture and transform commit message
        id: commit_message
        run: |
          .github/workflows/sync-to-nabledge/capture-commit-message.sh \
            "${{ github.sha }}" \
            "${{ github.event.head_commit.message }}"

      - name: Build commit body with trigger information
        run: |
          .github/workflows/sync-to-nabledge/build-commit-body.sh \
            "${{ github.repository }}" \
            "${{ github.sha }}" \
            "$COMMIT_BODY"

      - name: Display commit message for verification
        run: |
          echo "::notice::Syncing commit to nabledge repository"
          echo "Subject: $COMMIT_SUBJECT"
          echo "Body preview: ${FULL_COMMIT_BODY:0:200}..."

      - name: Commit and Push to nabledge
        working-directory: nabledge-repo
        run: |
          ../.github/workflows/sync-to-nabledge/commit-and-push.sh \
            "$COMMIT_SUBJECT" \
            "$FULL_COMMIT_BODY" \
            "develop"
WORKFLOW_EOF
```

**検証:**
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/sync-to-nabledge.yml')); print('OK: YAML valid')"
grep -q "workflows/sync-to-nabledge/sync.sh" .github/workflows/sync-to-nabledge.yml && echo "OK: sync.sh path" || echo "FAIL"
grep -q "workflows/sync-to-nabledge/capture-commit-message.sh" .github/workflows/sync-to-nabledge.yml && echo "OK: capture path" || echo "FAIL"
grep -q "workflows/sync-to-nabledge/build-commit-body.sh" .github/workflows/sync-to-nabledge.yml && echo "OK: build path" || echo "FAIL"
grep -q "workflows/sync-to-nabledge/commit-and-push.sh" .github/workflows/sync-to-nabledge.yml && echo "OK: commit path" || echo "FAIL"
! grep -q "\.github/scripts/" .github/workflows/sync-to-nabledge.yml && echo "OK: no old paths" || echo "FAIL"
! grep -q "clean-repository" .github/workflows/sync-to-nabledge.yml && echo "OK: no clean-repository" || echo "FAIL"
! grep -q "transform-to-plugin" .github/workflows/sync-to-nabledge.yml && echo "OK: no transform" || echo "FAIL"
! grep -q "validate-marketplace" .github/workflows/sync-to-nabledge.yml && echo "OK: no validate" || echo "FAIL"
```

---

### Step 5: 旧スクリプトを削除

```bash
git rm .github/scripts/clean-repository.sh
git rm .github/scripts/transform-to-plugin.sh
git rm .github/scripts/validate-marketplace.sh
```

**検証:**
```bash
test ! -f .github/scripts/clean-repository.sh && echo "OK" || echo "FAIL"
test ! -f .github/scripts/transform-to-plugin.sh && echo "OK" || echo "FAIL"
test ! -f .github/scripts/validate-marketplace.sh && echo "OK" || echo "FAIL"
# .github/scripts/ にはまだ2ファイル残っていること
test -f .github/scripts/create-version-tag.sh && echo "OK: create-version-tag.sh preserved" || echo "FAIL"
test -f .github/scripts/validate-version-updates.sh && echo "OK: validate-version-updates.sh preserved" || echo "FAIL"
```

---

### Step 6: 統合テスト

以下のスクリプトを実行する。全コマンドが exit code 0 で終了すれば作業完了。

```bash
#!/bin/bash
set -euo pipefail

SCRIPTS_DIR=".github/workflows/sync-to-nabledge"

echo "=== Test 1: sync.sh dry run ==="
TEST_DIR=$(mktemp -d)
mkdir -p "$TEST_DIR/.git"
echo "dummy" > "$TEST_DIR/old-file.txt"
mkdir -p "$TEST_DIR/stale-dir"
echo "stale" > "$TEST_DIR/stale-dir/stale.txt"

"$SCRIPTS_DIR/sync.sh" . "$TEST_DIR" "$SCRIPTS_DIR/sync-manifest.txt"
echo "PASS"

echo "=== Test 2: stale files are deleted ==="
test ! -f "$TEST_DIR/old-file.txt"
test ! -d "$TEST_DIR/stale-dir"
echo "PASS"

echo "=== Test 3: .git is preserved ==="
test -d "$TEST_DIR/.git"
echo "PASS"

echo "=== Test 4: all file entries exist in output ==="
awk -F'\t' '!/^#/ && !/^$/ && $1 == "file" { print $3 }' "$SCRIPTS_DIR/sync-manifest.txt" | while read -r dest; do
  test -f "$TEST_DIR/$dest" || { echo "FAIL: $dest"; exit 1; }
done
echo "PASS"

echo "=== Test 5: all dir entries exist and are non-empty ==="
awk -F'\t' '!/^#/ && !/^$/ && $1 == "dir" { print $3 }' "$SCRIPTS_DIR/sync-manifest.txt" | while read -r dest; do
  test -d "$TEST_DIR/$dest" || { echo "FAIL: dir not found: $dest"; exit 1; }
  test -n "$(find "$TEST_DIR/$dest" -type f | head -1)" || { echo "FAIL: dir empty: $dest"; exit 1; }
done
echo "PASS"

echo "=== Test 6: no unwanted .github dirs in output ==="
test ! -d "$TEST_DIR/plugins/nabledge-6/.github/workflows"
test ! -d "$TEST_DIR/plugins/nabledge-6/.github/scripts"
echo "PASS"

echo "=== Test 7: workflow YAML valid and references correct paths ==="
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/sync-to-nabledge.yml'))"
grep -q "workflows/sync-to-nabledge/sync.sh" .github/workflows/sync-to-nabledge.yml
grep -q "workflows/sync-to-nabledge/capture-commit-message.sh" .github/workflows/sync-to-nabledge.yml
grep -q "workflows/sync-to-nabledge/build-commit-body.sh" .github/workflows/sync-to-nabledge.yml
grep -q "workflows/sync-to-nabledge/commit-and-push.sh" .github/workflows/sync-to-nabledge.yml
! grep -q "\.github/scripts/" .github/workflows/sync-to-nabledge.yml
echo "PASS"

echo "=== Test 8: old scripts deleted, new scripts exist ==="
test ! -f .github/scripts/clean-repository.sh
test ! -f .github/scripts/transform-to-plugin.sh
test ! -f .github/scripts/validate-marketplace.sh
test ! -f .github/scripts/capture-commit-message.sh
test ! -f .github/scripts/build-commit-body.sh
test ! -f .github/scripts/commit-and-push.sh
test -x "$SCRIPTS_DIR/sync.sh"
test -x "$SCRIPTS_DIR/capture-commit-message.sh"
test -x "$SCRIPTS_DIR/build-commit-body.sh"
test -x "$SCRIPTS_DIR/commit-and-push.sh"
test -f "$SCRIPTS_DIR/sync-manifest.txt"
test -f .github/scripts/create-version-tag.sh
test -f .github/scripts/validate-version-updates.sh
echo "PASS"

rm -rf "$TEST_DIR"

echo ""
echo "All 8 tests passed."
```

すべてのテストが PASS になれば作業完了。
