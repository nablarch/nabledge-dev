#!/bin/bash
# Search impact evaluation: Convert real RST files with RBKC and compare with KC
#
# Prerequisites: ./setup.sh must be run first (.lw/nab-official/v6/ must exist)
#
# Usage: cd tools/rbkc/docs/search-impact-evaluation && bash run_evaluation.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"
LW_V6="$REPO_ROOT/.lw/nab-official/v6"
KC_KNOWLEDGE="$REPO_ROOT/.claude/skills/nabledge-6/knowledge"
SEARCH_SCRIPT="$REPO_ROOT/.claude/skills/nabledge-6/scripts/full-text-search.sh"
CONVERT_SCRIPT="$EVAL_DIR/convert_rst.py"
PYTHON="${PYTHON:-python3}"

# Output directory for RBKC-converted files (temporary)
RBKC_OUT="$EVAL_DIR/.output"

echo "=== Search Impact Evaluation ==="
echo ""

# Check prerequisites
if [ ! -d "$LW_V6" ]; then
    echo "ERROR: .lw/nab-official/v6/ not found. Run ./setup.sh first."
    exit 1
fi

if [ ! -f "$SEARCH_SCRIPT" ]; then
    echo "ERROR: full-text-search.sh not found."
    exit 1
fi

# Clean previous output
rm -rf "$RBKC_OUT"
mkdir -p "$RBKC_OUT"

echo "--- Step 1: Convert target RST files with RBKC ---"
echo ""

# Target files for evaluation (representative samples)
# Format: source_path|output_subpath|file_id
TARGETS=(
    "nablarch-document/ja/application_framework/application_framework/libraries/validation/bean_validation.rst|component/libraries/libraries-bean_validation.json|libraries-bean_validation"
    "nablarch-document/ja/application_framework/application_framework/libraries/database/universal_dao.rst|component/libraries/libraries-universal_dao.json|libraries-universal_dao"
    "nablarch-document/ja/application_framework/application_framework/libraries/tag.rst|component/libraries/libraries-tag.json|libraries-tag"
    "nablarch-document/ja/application_framework/application_framework/handlers/web/http_response_handler.rst|component/handlers/handlers-http_response_handler.json|handlers-http_response_handler"
    "nablarch-document/ja/application_framework/application_framework/handlers/standalone/data_read_handler.rst|component/handlers/handlers-data_read_handler.json|handlers-data_read_handler"
    "nablarch-document/ja/application_framework/adaptors/doma_adaptor.rst|component/adapters/adapters-doma_adaptor.json|adapters-doma_adaptor"
)

for target in "${TARGETS[@]}"; do
    IFS='|' read -r src_rel out_rel file_id <<< "$target"
    src_path="$LW_V6/$src_rel"
    out_path="$RBKC_OUT/$out_rel"

    if [ ! -f "$src_path" ]; then
        echo "  SKIP: $src_rel (file not found)"
        continue
    fi

    $PYTHON "$CONVERT_SCRIPT" "$src_path" "$out_path" --id "$file_id"
done

echo ""
echo "--- Step 2: Compare content sizes ---"
echo ""

$PYTHON - "$KC_KNOWLEDGE" "$RBKC_OUT" << 'PYEOF'
import json, sys, os, glob

kc_dir = sys.argv[1]
rbkc_dir = sys.argv[2]

print(f"{'File':50s} {'KC lines':>10s} {'RBKC lines':>11s} {'Ratio':>7s}")
print("-" * 82)

total_kc = 0
total_rbkc = 0

for rbkc_fp in sorted(glob.glob(f"{rbkc_dir}/**/*.json", recursive=True)):
    rel = os.path.relpath(rbkc_fp, rbkc_dir)
    kc_fp = os.path.join(kc_dir, rel)

    with open(rbkc_fp, encoding="utf-8") as f:
        rbkc_data = json.load(f)
    rbkc_lines = sum(len(v.splitlines()) for v in rbkc_data.get("sections", {}).values())

    if os.path.exists(kc_fp):
        with open(kc_fp, encoding="utf-8") as f:
            kc_data = json.load(f)
        kc_lines = sum(len(v.splitlines()) for v in kc_data.get("sections", {}).values())
    else:
        kc_lines = 0

    ratio = f"{rbkc_lines/kc_lines:.1f}x" if kc_lines > 0 else "N/A"
    basename = os.path.basename(rbkc_fp).replace(".json", "")
    print(f"{basename:50s} {kc_lines:10d} {rbkc_lines:11d} {ratio:>7s}")
    total_kc += kc_lines
    total_rbkc += rbkc_lines

print("-" * 82)
ratio = f"{total_rbkc/total_kc:.1f}x" if total_kc > 0 else "N/A"
print(f"{'TOTAL':50s} {total_kc:10d} {total_rbkc:11d} {ratio:>7s}")
PYEOF

echo ""
echo "--- Step 3: Search speed comparison ---"
echo ""

# Create a search script that works on the RBKC output
# Copy all KC knowledge files, then overlay RBKC converted files
RBKC_FULL="$EVAL_DIR/.output_full"
rm -rf "$RBKC_FULL"
cp -r "$KC_KNOWLEDGE" "$RBKC_FULL"
# Overlay RBKC files
cp -r "$RBKC_OUT"/* "$RBKC_FULL"/ 2>/dev/null || true

SEARCH_QUERIES=(
    "バリデーション Bean Validation"
    "データベース DAO UniversalDao"
    "JSP カスタムタグ tag"
    "ハンドラ handler HttpResponse"
)

# Create RBKC search script by copying original and patching KNOWLEDGE_DIR
RBKC_SEARCH="$EVAL_DIR/.rbkc_search.sh"
cp "$SEARCH_SCRIPT" "$RBKC_SEARCH"
# Replace the 3 lines that compute KNOWLEDGE_DIR with a hardcoded path
sed -i "s|^SCRIPT_DIR=.*|# patched for evaluation|; s|^SKILL_DIR=.*|# patched for evaluation|; s|^KNOWLEDGE_DIR=.*|KNOWLEDGE_DIR=\"$RBKC_FULL\"|" "$RBKC_SEARCH"
chmod +x "$RBKC_SEARCH"

for query in "${SEARCH_QUERIES[@]}"; do
    echo "Query: $query"

    # KC search
    kc_start=$(date +%s%N)
    kc_results=$(bash "$SEARCH_SCRIPT" $query 2>/dev/null)
    kc_end=$(date +%s%N)
    kc_ms=$(( (kc_end - kc_start) / 1000000 ))

    # RBKC search
    rbkc_start=$(date +%s%N)
    rbkc_results=$(bash "$RBKC_SEARCH" $query 2>/dev/null)
    rbkc_end=$(date +%s%N)
    rbkc_ms=$(( (rbkc_end - rbkc_start) / 1000000 ))

    echo "  KC:   ${kc_ms}ms"
    echo "  RBKC: ${rbkc_ms}ms"

    # Compare top 5 results
    kc_top5=$(echo "$kc_results" | head -5)
    rbkc_top5=$(echo "$rbkc_results" | head -5)
    if [ "$kc_top5" = "$rbkc_top5" ]; then
        echo "  Results: Top 5 identical"
    else
        echo "  Results: DIFFERENT"
        echo "    KC top 5:"
        echo "$kc_top5" | sed 's/^/      /'
        echo "    RBKC top 5:"
        echo "$rbkc_top5" | sed 's/^/      /'
    fi
    echo ""
done

echo "--- Step 4: Section size comparison ---"
echo ""

$PYTHON - "$KC_KNOWLEDGE" "$RBKC_OUT" << 'PYEOF'
import json, sys, os, glob

kc_dir = sys.argv[1]
rbkc_dir = sys.argv[2]

print(f"{'File':40s} {'Section':>10s} {'KC':>6s} {'RBKC':>6s} {'Ratio':>7s}")
print("-" * 73)

for rbkc_fp in sorted(glob.glob(f"{rbkc_dir}/**/*.json", recursive=True)):
    rel = os.path.relpath(rbkc_fp, rbkc_dir)
    kc_fp = os.path.join(kc_dir, rel)

    with open(rbkc_fp, encoding="utf-8") as f:
        rbkc_data = json.load(f)

    if not os.path.exists(kc_fp):
        continue
    with open(kc_fp, encoding="utf-8") as f:
        kc_data = json.load(f)

    basename = os.path.basename(rbkc_fp).replace(".json", "")

    # Build section title → content mapping for both
    kc_sections = {}
    for entry in kc_data.get("index", []):
        content = kc_data.get("sections", {}).get(entry["id"], "")
        kc_sections[entry["title"]] = len(content.splitlines())

    for entry in rbkc_data.get("index", []):
        title = entry["title"]
        rbkc_lines = len(rbkc_data.get("sections", {}).get(entry["id"], "").splitlines())
        kc_lines = kc_sections.get(title, 0)
        ratio = f"{rbkc_lines/kc_lines:.1f}x" if kc_lines > 0 else "new"
        print(f"{basename:40s} {title[:10]:>10s} {kc_lines:6d} {rbkc_lines:6d} {ratio:>7s}")
PYEOF

# Cleanup
rm -rf "$RBKC_FULL" "$RBKC_SEARCH"

echo ""
echo "--- Done ---"
echo "RBKC output preserved at: $RBKC_OUT"
