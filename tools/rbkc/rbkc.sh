#!/usr/bin/env bash
# rbkc — Rule-Based Knowledge Creator
#
# Usage:
#   rbkc.sh create <version> [--output-dir DIR] [--state-dir DIR]
#   rbkc.sh update <version> [--output-dir DIR] [--state-dir DIR]
#   rbkc.sh delete <version> [--output-dir DIR] [--state-dir DIR]
#   rbkc.sh verify <version> [--output-dir DIR]
#
# Examples:
#   rbkc.sh create 6
#   rbkc.sh update 6 --output-dir /path/to/knowledge
#   rbkc.sh verify 6

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python -m scripts.run "$@"
