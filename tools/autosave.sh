#!/usr/bin/env bash
# Commit + push any new/changed files every N seconds, so work survives container restarts.
# Usage: tools/autosave.sh [interval_seconds]
cd "$(dirname "$0")/.."
INTERVAL="${1:-240}"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
save() {
  flock /tmp/words-git.lock bash -c '
    git add -A 2>/dev/null
    if ! git diff --cached --quiet; then
      n=$(git diff --cached --name-only | wc -l)
      git commit -q -m "Auto-save: $n changed data files

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01RQ8Zv5bKNgmZsR1UXLpUWw"
    fi
    for i in 1 2 3 4; do git push -q -u origin '"$BRANCH"' 2>/dev/null && break; sleep $((2**i)); done
  '
}
while true; do save; sleep "$INTERVAL"; done
