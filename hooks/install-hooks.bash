#!/usr/bin/env bash
#
# Copy pre-commit.bash to .git/hooks/pre-commit hook

# Get git dir
GIT_DIR=$(git rev-parse --git-dir)

echo "Installing hooks..."

# Create symlink to pre-commit script
ln -s ../../hooks/pre-commit.bash "${GIT_DIR}"/hooks/pre-commit

echo "Done!"