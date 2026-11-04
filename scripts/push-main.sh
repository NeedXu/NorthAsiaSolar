#!/usr/bin/env bash
# Preserve history and fail visibly; never force-push or discard another writer's work.
set -euo pipefail
for attempt in 1 2 3 4; do
  if git push origin HEAD:main; then exit 0; fi
  if [ "$attempt" -eq 4 ]; then
    echo 'Git push failed after four attempts; state is not confirmed saved.' >&2
    exit 1
  fi
  echo "Push attempt $attempt failed; reconciling remote history before retry." >&2
  git fetch origin main
  if git merge-base --is-ancestor HEAD origin/main; then
    echo 'Remote already contains this commit; state was saved.'
    exit 0
  fi
  git rebase origin/main
  sleep "$((attempt * 2))"
done
