#!/usr/bin/env bash
set -e

if ! command -v git >/dev/null 2>&1; then
  echo "git is not installed. Install git first: https://git-scm.com/downloads" >&2
  exit 1
fi

REMOTE="$1"
BRANCH="${2:-main}"

if [ ! -d .git ]; then
  git init
  echo "Initialized new git repository."
fi

git add --all || true
if git commit -m "Initial import: Skill_Gap_Analyser" -q; then
  echo "Committed files."
else
  echo "Nothing to commit or commit failed (maybe already committed). Continuing."
fi

if [ -z "$REMOTE" ]; then
  echo "No remote provided. Run: ./scripts/push_to_github.sh https://github.com/username/repo.git" >&2
  exit 0
fi

if ! git remote | grep -q '^origin$'; then
  git remote add origin "$REMOTE"
  echo "Added remote origin -> $REMOTE"
else
  git remote set-url origin "$REMOTE"
  echo "Set origin -> $REMOTE"
fi

git branch -M "$BRANCH"
echo "Pushing to origin/$BRANCH..."
git push -u origin "$BRANCH"
