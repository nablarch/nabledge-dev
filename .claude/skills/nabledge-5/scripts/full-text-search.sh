#!/bin/bash
# 全知識ファイルの全セクションに対してキーワードOR検索を実行
#
# 引数: キーワード（1つ以上）
# 出力: ヒットしたファイルとセクションIDの一覧
# 出力形式: ファイル相対パス|セクションID

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KNOWLEDGE_DIR="$SKILL_DIR/knowledge"

if [ $# -eq 0 ]; then
  echo "Usage: $0 <keyword1> [keyword2] ..." >&2
  exit 1
fi

# 引数からjqのOR条件を組み立てる
conditions=""
for kw in "$@"; do
  if [ -n "$conditions" ]; then
    conditions="$conditions or "
  fi
  # jq正規表現のメタ文字をエスケープ
  escaped=$(echo "$kw" | sed 's/[.[\(*+?{|^$]/\\&/g')
  conditions="${conditions}test(\"$escaped\"; \"i\")"
done

# 全JSONファイルに対して検索
find "$KNOWLEDGE_DIR" -name "*.json" | sort | while read -r filepath; do
  relpath="${filepath#$KNOWLEDGE_DIR/}"
  jq -r --arg file "$relpath" \
    ".sections | to_entries[] | select(.value | ($conditions)) | \"\($file)|\(.key)\"" \
    "$filepath" 2>/dev/null
done
