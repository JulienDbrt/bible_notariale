#!/bin/bash

# Script to install Git hooks for the project

echo "📦 Installing Git hooks..."

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Create hooks directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/.git/hooks"

# Copy pre-push hook
if [ -f "$SCRIPT_DIR/pre-push-hook" ]; then
    cp "$SCRIPT_DIR/pre-push-hook" "$PROJECT_ROOT/.git/hooks/pre-push"
    chmod +x "$PROJECT_ROOT/.git/hooks/pre-push"
    echo "✅ Pre-push hook installed"
else
    echo "⚠️  Pre-push hook template not found in scripts directory"
fi

# Copy pre-commit hook if it exists
if [ -f "$SCRIPT_DIR/pre-commit-hook" ]; then
    cp "$SCRIPT_DIR/pre-commit-hook" "$PROJECT_ROOT/.git/hooks/pre-commit"
    chmod +x "$PROJECT_ROOT/.git/hooks/pre-commit"
    echo "✅ Pre-commit hook installed"
fi

echo "🎉 Git hooks installation complete!"
echo ""
echo "The following hooks are now active:"
echo "  - pre-push: Runs tests and cleans temporary files before push"
echo ""
echo "To bypass hooks (not recommended), use --no-verify flag:"
echo "  git push --no-verify"