#!/usr/bin/env bash
# Retry a command on transient failures (e.g. GitHub API 5xx / network blips).
# Propagates the final exit code, so the caller decides fatal vs best-effort:
#   bash scripts/retry.sh gh pr merge ...        # fatal: fails if all retries fail
#   bash scripts/retry.sh gh pr comment ... || true   # best-effort narration
#
# Tunable via env: RETRIES (default 5), RETRY_DELAY seconds (default 3).
set -u
attempts=${RETRIES:-5}
delay=${RETRY_DELAY:-3}
i=1
while true; do
  if "$@"; then
    exit 0
  fi
  code=$?
  if [ "$i" -ge "$attempts" ]; then
    echo "retry: giving up after $i attempts (exit $code): $*" >&2
    exit "$code"
  fi
  echo "retry: attempt $i/$attempts failed (exit $code); retrying in ${delay}s…" >&2
  i=$((i + 1))
  sleep "$delay"
done
