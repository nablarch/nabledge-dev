#!/bin/bash

set -uo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local status="$1"
    local message="$2"
    case "$status" in
        ok)      echo -e "${GREEN}[OK]${NC} $message" ;;
        error)   echo -e "${RED}[ERROR]${NC} $message" ;;
        warning) echo -e "${YELLOW}[WARN]${NC} $message" ;;
        info)    echo -e "${BLUE}[INFO]${NC} $message" ;;
    esac
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

# ============================================================
# Configuration
#
# Set SVN_BASE_URL to your organization's SVN repository root.
# Example: https://svn.example.com/svn/repo
#
# Each module is checked out from:
#   ${SVN_BASE_URL}/${MODULE_PATH}
# into .lw/nab-official/v1.x/<module-name>/
# ============================================================

SVN_BASE_URL="${SVN_BASE_URL:-}"
SVN_USERNAME="${SVN_USERNAME:-}"
SVN_PASSWORD="${SVN_PASSWORD:-}"

if [ -z "$SVN_BASE_URL" ]; then
    echo "Usage: SVN_BASE_URL=https://your-svn-server/svn/repo SVN_USERNAME=user SVN_PASSWORD=pass ./setup-svn.sh"
    echo ""
    echo "  SVN_BASE_URL  SVN repository root URL (required)"
    echo "  SVN_USERNAME  SVN username (optional)"
    echo "  SVN_PASSWORD  SVN password (optional)"
    echo ""
    echo "Example:"
    echo "  SVN_BASE_URL=https://svn.example.com/svn/repo SVN_USERNAME=user SVN_PASSWORD=pass ./setup-svn.sh"
    exit 1
fi

# Build SVN auth options
SVN_AUTH_OPTS=()
if [ -n "$SVN_USERNAME" ]; then
    SVN_AUTH_OPTS+=(--username "$SVN_USERNAME")
fi
if [ -n "$SVN_PASSWORD" ]; then
    SVN_AUTH_OPTS+=(--password "$SVN_PASSWORD" --no-auth-cache)
fi

# Check svn command
if ! command -v svn &> /dev/null; then
    print_status info "svn command not found. Installing subversion..."
    sudo apt-get install -y subversion
    if ! command -v svn &> /dev/null; then
        print_status error "Failed to install subversion"
        exit 1
    fi
    print_status ok "subversion installed"
fi

# Checkout or update a single SVN working copy
# Usage: svn_checkout <svn_url> <target_dir>
# Returns 0 on success, 1 on error (non-fatal)
svn_checkout() {
    local svn_url="$1"
    local target_dir="$2"
    local name
    name=$(basename "$target_dir")

    if [ -d "${target_dir}/.svn" ]; then
        print_status info "Updating ${name}..."
        if svn update "${SVN_AUTH_OPTS[@]}" "$target_dir" 2>&1; then
            print_status ok "${name} updated"
        else
            print_status warning "Failed to update ${name} (may not exist in this version)"
            return 1
        fi
    else
        print_status info "Checking out ${name}..."
        mkdir -p "$(dirname "$target_dir")"
        if svn checkout "${SVN_AUTH_OPTS[@]}" "$svn_url" "$target_dir" 2>&1; then
            print_status ok "${name} checked out"
        else
            print_status warning "Failed to checkout ${name} (may not exist in this version)"
            return 1
        fi
    fi
    return 0
}

# ============================================================
# v1.4 modules
# ============================================================
print_header "Checking out Nablarch v1.4 modules"

V14_DIR=".lw/nab-official/v1.4"
mkdir -p "$V14_DIR"

svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/06_Documentation/nablarch/branches/1.4_maintain" "${V14_DIR}/document"
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/biz_sample/branches/1.4_maintain" "${V14_DIR}/biz_sample"
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/nablarch_plugins_bundle/branches/1.4_maintain" "${V14_DIR}/ui_dev"
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/workflow/branches/1.4_maintain" "${V14_DIR}/workflow"
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/MessagingSimu/branches/1.4_maintain" "${V14_DIR}/MessagingSimu"
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/db/branches/1.4_maintain" "${V14_DIR}/fw-integration-db"
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/log4j/branches/1.4_maintain" "${V14_DIR}/fw-integration-log4j"
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/mail/branches/1.4_maintain" "${V14_DIR}/fw-integration-mail"
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/wmq/branches/1.4_maintain" "${V14_DIR}/fw-integration-wmq"
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/statistics_report/branches/1.4_maintain" "${V14_DIR}/statistics_report"
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/tutorial_project/branches/1.4_maintain" "${V14_DIR}/tutorial"

# ============================================================
# v1.3 modules (same structure as v1.4; skip if not exists)
# ============================================================
print_header "Checking out Nablarch v1.3 modules"

V13_DIR=".lw/nab-official/v1.3"
mkdir -p "$V13_DIR"

svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/06_Documentation/nablarch/branches/1.3_maintain" "${V13_DIR}/document" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/biz_sample/branches/1.3_maintain" "${V13_DIR}/biz_sample" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/nablarch_plugins_bundle/branches/1.3_maintain" "${V13_DIR}/ui_dev" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/workflow/branches/1.3_maintain" "${V13_DIR}/workflow" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/MessagingSimu/branches/1.3_maintain" "${V13_DIR}/MessagingSimu" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/db/branches/1.3_maintain" "${V13_DIR}/fw-integration-db" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/log4j/branches/1.3_maintain" "${V13_DIR}/fw-integration-log4j" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/mail/branches/1.3_maintain" "${V13_DIR}/fw-integration-mail" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/wmq/branches/1.3_maintain" "${V13_DIR}/fw-integration-wmq" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/statistics_report/branches/1.3_maintain" "${V13_DIR}/statistics_report" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/tutorial/branches/1.3_maintain" "${V13_DIR}/tutorial" || true

# ============================================================
# v1.2 modules (same structure as v1.4; skip if not exists)
# ============================================================
print_header "Checking out Nablarch v1.2 modules"

V12_DIR=".lw/nab-official/v1.2"
mkdir -p "$V12_DIR"

svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/06_Documentation/nablarch/branches/1.2_maintain" "${V12_DIR}/document" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/biz_sample/branches/1.2_maintain" "${V12_DIR}/biz_sample" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/nablarch_plugins_bundle/branches/1.2_maintain" "${V12_DIR}/ui_dev" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/workflow/branches/1.2_maintain" "${V12_DIR}/workflow" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/MessagingSimu/branches/1.2_maintain" "${V12_DIR}/MessagingSimu" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/db/branches/1.2_maintain" "${V12_DIR}/fw-integration-db" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/log4j/branches/1.2_maintain" "${V12_DIR}/fw-integration-log4j" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/mail/branches/1.2_maintain" "${V12_DIR}/fw-integration-mail" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/fw-integration/wmq/branches/1.2_maintain" "${V12_DIR}/fw-integration-wmq" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/statistics_report/branches/1.2_maintain" "${V12_DIR}/statistics_report" || true
svn_checkout "${SVN_BASE_URL}/Nablarch/02_ProjectOutput/05_SourceCode/sample/branches/1.2_maintain" "${V12_DIR}/tutorial" || true

print_header "SVN checkout completed"
echo "Checked out into:"
echo "  ${V14_DIR}/"
echo "  ${V13_DIR}/"
echo "  ${V12_DIR}/"
echo ""
echo "Next step: run knowledge-creator"
echo "  ./tools/knowledge-creator/kc.sh gen 1.4"
