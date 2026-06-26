#!/usr/bin/env bash
# Install the Gemma prepare-commit-msg hook into a git repo.
#
# Usage:
#   ./install_hook.sh            # install into the current repo
#   ./install_hook.sh /path/repo # install into another repo
set -euo pipefail

# Where this tool lives (so the hook can import generate_doc.py)
TOOL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Target repo (default: current directory)
TARGET_REPO="${1:-$(pwd)}"
HOOKS_DIR="$TARGET_REPO/.git/hooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "Error: '$TARGET_REPO' is not a git repo (no .git/hooks). Run 'git init' first."
    exit 1
fi

DEST="$HOOKS_DIR/prepare-commit-msg"

# Copy the template and bake in the absolute path to this tool
sed "s|__TOOL_DIR__|$TOOL_DIR|g" "$TOOL_DIR/hooks/prepare-commit-msg" > "$DEST"
chmod +x "$DEST"

echo "Installed prepare-commit-msg hook into: $HOOKS_DIR"
echo "Now run 'git commit' (without -m) in that repo and Gemma will pre-fill the message."
