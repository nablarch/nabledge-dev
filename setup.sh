#!/bin/bash

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "Nabledge Development Setup"
echo "========================================"
echo ""

# Print status function
print_status() {
    local status="$1"
    local message="$2"

    case "$status" in
        ok)
            echo -e "${GREEN}✓${NC} $message"
            ;;
        error)
            echo -e "${RED}✗${NC} $message"
            ;;
        warning)
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
        info)
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
    esac
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

# Check prerequisites
print_header "1. Checking Prerequisites"

# Check if running on WSL/Ubuntu
if ! grep -qi microsoft /proc/version && ! grep -qi ubuntu /etc/os-release; then
    print_status warning "This script is designed for WSL/Ubuntu environment"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check CA certificate
CA_CERT_PATH="/usr/local/share/ca-certificates/ca.crt"
if [ -f "$CA_CERT_PATH" ]; then
    print_status ok "CA certificate found at $CA_CERT_PATH"
else
    print_status warning "CA certificate not found at $CA_CERT_PATH"
    echo ""
    echo "  If you are in a corporate proxy environment, please install CA certificate first:"
    echo "    sudo cp /path/to/your/ca.crt $CA_CERT_PATH"
    echo "    sudo update-ca-certificates"
    echo ""
    read -p "Continue without CA certificate? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check bash version
if [ "${BASH_VERSINFO[0]}" -ge 4 ]; then
    print_status ok "Bash ${BASH_VERSION}"
else
    print_status error "Bash ${BASH_VERSION} (>= 4.0 required)"
    exit 1
fi

# Check sudo access
if sudo -n true 2>/dev/null; then
    print_status ok "sudo access available"
else
    print_status info "sudo may require password"
fi

# Install system tools
print_header "2. Installing System Tools"

# Update package list
print_status info "Updating package list..."
sudo apt-get update

# Check if tools are already installed
TOOLS_MISSING=0
for tool in libreoffice pdftoppm pandoc jq python3 gh; do
    if ! command -v "$tool" &> /dev/null; then
        TOOLS_MISSING=1
        break
    fi
done

if [ $TOOLS_MISSING -eq 0 ]; then
    print_status ok "System tools already installed"
else
    print_status info "Installing LibreOffice, Poppler, Pandoc, jq, Python3..."
    if sudo apt-get install -y libreoffice poppler-utils pandoc jq python3 python3-venv; then
        print_status ok "System tools installed"
    else
        print_status error "Failed to install system tools"
        exit 1
    fi
fi

# Install GitHub CLI
print_status info "Installing GitHub CLI (gh)..."
if command -v gh &> /dev/null; then
    print_status ok "gh is already installed ($(gh --version | head -n 1))"
else
    # Install from official repository
    if (type -p wget >/dev/null || (sudo apt-get update && sudo apt-get install -y wget)) \
        && sudo mkdir -p -m 755 /etc/apt/keyrings \
        && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
        && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
        && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
        && sudo apt-get update \
        && sudo apt-get install -y gh; then
        print_status ok "gh installed successfully"
    else
        print_status error "Failed to install gh"
        exit 1
    fi
fi

# Setup environment variables
print_header "3. Setting Up Environment Variables"

BASHRC="$HOME/.bashrc"
ENV_VARS_MARKER="# Nabledge environment variables"

if grep -q "$ENV_VARS_MARKER" "$BASHRC"; then
    print_status ok "Environment variables already configured"
else
    print_status info "Adding environment variables to $BASHRC..."
    cat >> "$BASHRC" << 'EOF'

# Nabledge environment variables
export UV_CA_BUNDLE="/usr/local/share/ca-certificates/ca.crt"
export SSL_CERT_FILE="/usr/local/share/ca-certificates/ca.crt"
export NODE_EXTRA_CA_CERTS="/usr/local/share/ca-certificates/ca.crt"
export PATH="$HOME/venv/bin:$PATH"
EOF
    print_status ok "Environment variables added"
    print_status info "Sourcing $BASHRC..."
    source "$BASHRC" || true
fi

# Install uv if not present
print_header "4. Installing uv (Python Package Manager)"

if command -v uv &> /dev/null; then
    print_status ok "uv already installed"
else
    print_status info "Installing uv..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        source "$HOME/.cargo/env" || true
        print_status ok "uv installed"
    else
        print_status error "Failed to install uv"
        exit 1
    fi
fi

# Setup Python venv and install libraries
print_header "5. Setting Up Python Virtual Environment"

VENV_DIR="$HOME/venv"

if [ -d "$VENV_DIR" ]; then
    print_status ok "Python venv already exists at $VENV_DIR"
else
    print_status info "Creating Python venv at $VENV_DIR..."
    if uv venv "$VENV_DIR"; then
        print_status ok "Python venv created"
    else
        print_status error "Failed to create Python venv"
        exit 1
    fi
fi

print_status info "Installing Python libraries..."
if uv pip install --python "$VENV_DIR/bin/python" \
    pdfplumber reportlab pypdf pymupdf \
    python-pptx Pillow markitdown \
    openpyxl python-docx lxml pandas; then
    print_status ok "Python libraries installed"
else
    print_status error "Failed to install Python libraries"
    exit 1
fi

# Verify document tools installation
print_header "6. Verifying Document Tools"

if "$VENV_DIR/bin/python" -c "import pdfplumber, reportlab, pptx, openpyxl, docx; print('OK')" 2>/dev/null; then
    print_status ok "Python libraries verified"
else
    print_status error "Python library verification failed"
    exit 1
fi

if soffice --version &>/dev/null && pdftoppm -v &>/dev/null && pandoc --version &>/dev/null && jq --version &>/dev/null; then
    print_status ok "System tools verified"
else
    print_status error "System tools verification failed"
    exit 1
fi

# Setup Node.js and npm
print_header "7. Setting Up Node.js"

if command -v node &> /dev/null; then
    print_status ok "Node.js $(node --version) already installed"
else
    print_status info "Installing Node.js via nvm..."

    # Install nvm
    if [ ! -d "$HOME/.nvm" ]; then
        if curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash; then
            export NVM_DIR="$HOME/.nvm"
            [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
            print_status ok "nvm installed"
        else
            print_status error "Failed to install nvm"
            exit 1
        fi
    else
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        print_status ok "nvm already installed"
    fi

    # Install Node.js LTS
    if nvm install --lts; then
        print_status ok "Node.js LTS installed"
    else
        print_status error "Failed to install Node.js"
        exit 1
    fi
fi

# Install ajv-cli
print_header "8. Installing JSON Schema Validator (ajv-cli)"

if command -v ajv &> /dev/null; then
    print_status ok "ajv-cli already installed"
else
    print_status info "Installing ajv-cli and ajv-formats..."
    if npm install -g ajv-cli ajv-formats; then
        print_status ok "ajv-cli installed"
    else
        print_status error "Failed to install ajv-cli"
        exit 1
    fi
fi

# Clone Nablarch official repositories
print_header "9. Cloning Nablarch Official Repositories"

NAB_OFFICIAL_DIR=".lw/nab-official"

# Create directory if it doesn't exist
if [ ! -d "$NAB_OFFICIAL_DIR" ]; then
    print_status info "Creating $NAB_OFFICIAL_DIR directory..."
    mkdir -p "$NAB_OFFICIAL_DIR"
    print_status ok "Directory created"
fi

# Function to clone or update repository
clone_or_update_repo() {
    local repo_url="$1"
    local repo_name=$(basename "$repo_url" .git)
    local repo_path="$NAB_OFFICIAL_DIR/$repo_name"

    if [ -d "$repo_path" ]; then
        print_status info "Repository $repo_name already exists, updating..."
        if git -C "$repo_path" pull; then
            print_status ok "$repo_name updated"
        else
            print_status warning "Failed to update $repo_name"
        fi
    else
        print_status info "Cloning $repo_name..."
        if git clone "$repo_url" "$repo_path"; then
            print_status ok "$repo_name cloned"
        else
            print_status error "Failed to clone $repo_name"
            exit 1
        fi
    fi
}

# Clone repositories
clone_or_update_repo "https://github.com/nablarch/nablarch-document.git"
clone_or_update_repo "https://github.com/nablarch/nablarch-single-module-archetype.git"
clone_or_update_repo "https://github.com/Fintan-contents/nablarch-system-development-guide.git"

# Final summary
print_header "Setup Completed Successfully!"

echo "Next steps:"
echo "  1. Restart your shell or run: source ~/.bashrc"
echo "  2. Copy and edit .env file:"
echo "     cp .env.example .env"
echo "     # Edit .env and set your credentials"
echo ""
echo "  3. Load environment and start Claude Code:"
echo "     source .env"
echo "     claude"
echo ""
