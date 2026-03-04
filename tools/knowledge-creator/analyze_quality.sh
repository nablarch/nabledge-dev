#!/bin/bash
# Quality Analysis Script - 品質集計スクリプト

LOG_DIR="tools/knowledge-creator/.logs/v6"

echo "=== nabledge-creator 品質レポート ==="
echo ""

# Phase B: 生成
echo "## Phase B: 生成"
PHASE_B_COUNT=$(ls -1 "$LOG_DIR/phase-b/executions/"*.json 2>/dev/null | wc -l)
echo "生成セクション数: $PHASE_B_COUNT"
echo ""

# Phase C: 構造チェック
echo "## Phase C: 構造チェック"
if [ -f "$LOG_DIR/phase-c/results.json" ]; then
  jq -r '.summary | "総数: \(.total)\n合格: \(.pass) (\(.pass * 100 / .total | floor)%)\n不合格: \(.fail) (\(.fail * 100 / .total | floor)%)"' "$LOG_DIR/phase-c/results.json"
else
  echo "未実行"
fi
echo ""

# Phase D: 内容チェック
echo "## Phase D: 内容チェック"
PHASE_D_DIR="$LOG_DIR/phase-d/findings"
if [ -d "$PHASE_D_DIR" ]; then
  TOTAL_CHECKED=$(ls -1 "$PHASE_D_DIR"/*.json 2>/dev/null | wc -l)
  CLEAN=$(jq -s 'map(select(.findings | length == 0)) | length' "$PHASE_D_DIR"/*.json 2>/dev/null)
  HAS_ISSUES=$(jq -s 'map(select(.findings | length > 0)) | length' "$PHASE_D_DIR"/*.json 2>/dev/null)
  TOTAL_FINDINGS=$(jq -s 'map(.findings | length) | add' "$PHASE_D_DIR"/*.json 2>/dev/null)
  CRITICAL=$(jq -s 'map(.findings[]?) | map(select(.severity=="critical")) | length' "$PHASE_D_DIR"/*.json 2>/dev/null)
  MINOR=$(jq -s 'map(.findings[]?) | map(select(.severity=="minor")) | length' "$PHASE_D_DIR"/*.json 2>/dev/null)

  echo "チェック済み: $TOTAL_CHECKED セクション"
  echo "クリーン: $CLEAN ($(echo "scale=0; $CLEAN * 100 / $TOTAL_CHECKED" | bc)%)"
  echo "問題あり: $HAS_ISSUES ($(echo "scale=0; $HAS_ISSUES * 100 / $TOTAL_CHECKED" | bc)%)"
  echo ""
  echo "Total findings: $TOTAL_FINDINGS 件"
  echo "  Critical: $CRITICAL 件"
  echo "  Minor: $MINOR 件"
  echo ""

  echo "### Findings カテゴリ別"
  jq -s 'map(.findings[]?) | group_by(.category) | map({category: .[0].category, total: length, critical: (map(select(.severity=="critical")) | length)}) | sort_by(-.total) | .[] | "  \(.category): \(.total)件 (critical: \(.critical)件)"' "$PHASE_D_DIR"/*.json 2>/dev/null
else
  echo "未実行"
fi
echo ""

# Phase E: 修正
echo "## Phase E: 修正"
PHASE_E_DIR="$LOG_DIR/phase-e/executions"
if [ -d "$PHASE_E_DIR" ] && [ "$(ls -A $PHASE_E_DIR 2>/dev/null)" ]; then
  FIXED_COUNT=$(ls -1 "$PHASE_E_DIR"/*.json 2>/dev/null | wc -l)
  echo "修正実行: $FIXED_COUNT セクション"

  # 修正前後の比較は generate/ ディレクトリの比較が必要
else
  echo "未実行 または 修正不要"
fi
echo ""

# Phase F: パターン分類
echo "## Phase F: パターン分類"
PHASE_F_DIR="$LOG_DIR/phase-f/patterns"
if [ -d "$PHASE_F_DIR" ] && [ "$(ls -A $PHASE_F_DIR 2>/dev/null)" ]; then
  PATTERN_COUNT=$(ls -1 "$PHASE_F_DIR"/*.json 2>/dev/null | wc -l)
  echo "分類済み: $PATTERN_COUNT セクション"
else
  echo "未実行"
fi
echo ""

# Phase G: リンク解決
echo "## Phase G: リンク解決"
PHASE_G_DIR="$LOG_DIR/phase-g/resolved"
if [ -d "$PHASE_G_DIR" ]; then
  RESOLVED_COUNT=$(find "$PHASE_G_DIR" -name "*.json" 2>/dev/null | wc -l)
  echo "解決済み: $RESOLVED_COUNT セクション"
else
  echo "未実行"
fi
echo ""

# 最終出力ファイル
echo "## 最終出力"
SKILL_DIR=".claude/skills/nabledge-6/knowledge"
if [ -d "$SKILL_DIR" ]; then
  FINAL_COUNT=$(find "$SKILL_DIR" -name "*.json" 2>/dev/null | wc -l)
  echo "最終ナレッジファイル: $FINAL_COUNT 個"
else
  echo "出力ディレクトリなし"
fi
echo ""

# ファイル別サマリー
echo "## ファイル別品質"
echo ""
echo "| ファイル | セクション数 | クリーン | 問題あり | Critical | Minor |"
echo "|---------|-------------|---------|---------|----------|-------|"

for prefix in "adapters-micrometer_adaptor" "libraries-tag--" "libraries-tag_reference"; do
  FILE_NAME=$(echo "$prefix" | sed 's/--$//')
  SECTIONS=$(ls -1 "$LOG_DIR/phase-b/executions/${prefix}"*.json 2>/dev/null | wc -l)

  if [ $SECTIONS -gt 0 ]; then
    CLEAN_F=$(ls -1 "$PHASE_D_DIR/${prefix}"*.json 2>/dev/null | xargs jq -s 'map(select(.findings | length == 0)) | length' 2>/dev/null)
    ISSUES_F=$(ls -1 "$PHASE_D_DIR/${prefix}"*.json 2>/dev/null | xargs jq -s 'map(select(.findings | length > 0)) | length' 2>/dev/null)
    CRITICAL_F=$(ls -1 "$PHASE_D_DIR/${prefix}"*.json 2>/dev/null | xargs jq -s 'map(.findings[]?) | map(select(.severity=="critical")) | length' 2>/dev/null)
    MINOR_F=$(ls -1 "$PHASE_D_DIR/${prefix}"*.json 2>/dev/null | xargs jq -s 'map(.findings[]?) | map(select(.severity=="minor")) | length' 2>/dev/null)

    echo "| $FILE_NAME | $SECTIONS | $CLEAN_F | $ISSUES_F | $CRITICAL_F | $MINOR_F |"
  fi
done

echo ""
echo "=== 品質レポート完了 ==="
