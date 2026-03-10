#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOL_DIR="$SCRIPT_DIR"
PYTHON="${PYTHON:-python}"

# Parse command and version
COMMAND="${1:-}"
VERSION="${2:-}"

if [ -z "$COMMAND" ] || [ -z "$VERSION" ]; then
    echo "Usage: ./kc.sh <gen|regen|fix> <version> [options]"
    echo ""
    echo "Commands:"
    echo "  gen     全件生成（clean後に全フェーズ実行）"
    echo "  regen   ソース変更への追随 / 特定ファイル再生成"
    echo "  fix     品質改善（再検証・修正）"
    echo ""
    echo "Options:"
    echo "  --resume          中断再開（genのみ、削除なし）"
    echo "  --target FILE_ID  対象ファイル指定（複数可）"
    echo "  --yes             確認プロンプトをスキップ"
    echo "  --dry-run         ドライラン"
    echo "  --max-rounds N    CDEループ回数（default: 1）"
    echo "  --concurrency N   並列数（default: 4）"
    echo "  --test FILE       テストファイル指定"
    echo "  --verbose         CC詳細ログ出力（stream-json + ツール呼び出し記録）"
    exit 1
fi

shift 2

# Parse remaining arguments
RESUME=false
TARGET_ARGS=""
YES_FLAG=""
PASSTHROUGH_ARGS=""

while [ $# -gt 0 ]; do
    case "$1" in
        --resume)
            RESUME=true
            shift
            ;;
        --target)
            TARGET_ARGS="$TARGET_ARGS --target $2"
            shift 2
            ;;
        --yes)
            YES_FLAG="--yes"
            shift
            ;;
        *)
            PASSTHROUGH_ARGS="$PASSTHROUGH_ARGS $1"
            shift
            ;;
    esac
done

case "$COMMAND" in
    gen)
        if [ "$RESUME" = true ]; then
            # UC2: Resume interrupted generation (no clean, new run_id)
            echo "🔄 中断再開モード"
            $PYTHON "$TOOL_DIR/scripts/run.py" --command gen --version "$VERSION" $PASSTHROUGH_ARGS
        else
            # UC1: Full generation (clean first)
            echo "🚀 全件生成モード"
            $PYTHON "$TOOL_DIR/scripts/clean.py" --version "$VERSION" ${YES_FLAG:---yes}
            $PYTHON "$TOOL_DIR/scripts/run.py" --command gen --version "$VERSION" $PASSTHROUGH_ARGS
        fi
        ;;
    regen)
        if [ -n "$TARGET_ARGS" ]; then
            # UC4: Regenerate specific files
            echo "🔄 特定ファイル再生成"
            $PYTHON "$TOOL_DIR/scripts/run.py" --command regen --version "$VERSION" \
                $TARGET_ARGS ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
        else
            # UC3: Detect source changes and regenerate
            echo "🔄 ソース変更検知 → 再生成"
            $PYTHON "$TOOL_DIR/scripts/run.py" --command regen --version "$VERSION" \
                ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
        fi
        ;;
    fix)
        # UC5, UC6: Quality improvement
        echo "🔧 品質改善モード"
        $PYTHON "$TOOL_DIR/scripts/run.py" --command fix --version "$VERSION" \
            $TARGET_ARGS ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
        ;;
    *)
        echo "Error: Unknown command '$COMMAND'"
        echo "Usage: ./kc.sh <gen|regen|fix> <version> [options]"
        exit 1
        ;;
esac
