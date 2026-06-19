#!/bin/bash
# Purge sensitive strings and files from git history using git-filter-repo.
# WARNING: Rewrites git history. Run only on a local clone and coordinate with your team.
# Install: pip install git-filter-repo

set -euo pipefail

echo "This script will assist in removing sensitive literals and files from git history."
echo "Edit the REPLACE_TEXT block below to include literals or patterns to remove."

# Example: replace known literal secrets with placeholder
# Format: literal:OLD==>NEW
cat > replace-text.txt <<'REPLACE'
# Replace literals here, one per line
literal:greenmind-super-secret-jwt-key-2026-hackathon-mvp==>REMOVED_SECRET
# literal:mongodb+srv://laxmi:laxmi9323@cluster0.f6keeyj.mongodb.net==>REMOVED_MONGODB_URI
REPLACE

read -p "Proceed to rewrite history (this will forcefully modify commits)? (y/N) " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborting. Edit scripts/purge_secrets_history.sh and replace replace-text.txt then run again."; exit 1
fi

# Ensure working tree is clean
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Please commit or stash changes before running this script."; exit 1
fi

# Run filter-repo to replace literals
git filter-repo --replace-text replace-text.txt

# Remove any committed .env files
if git rev-parse --verify --quiet refs/heads >/dev/null; then
  echo "Removing .env from history (if present)"
  git filter-repo --invert-paths --paths .env || true
fi

cat <<'POST'
History rewritten locally.
Review the repo. Then force-push to remote:
  git push --force --all
  git push --force --tags
After push, rotate any keys removed from history (regenerate API keys, DB credentials) and update GitHub/hosting secrets.
POST
