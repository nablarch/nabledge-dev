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
