#!/usr/bin/env bash
set -euo pipefail

max_attempts="${NPM_AUDIT_MAX_ATTEMPTS:-3}"
delay_seconds="${NPM_AUDIT_RETRY_DELAY_SECONDS:-15}"

case "$max_attempts" in
  ''|*[!0-9]*) echo "ERROR NPM_AUDIT_MAX_ATTEMPTS must be a positive integer" >&2; exit 2 ;;
esac
case "$delay_seconds" in
  ''|*[!0-9]*) echo "ERROR NPM_AUDIT_RETRY_DELAY_SECONDS must be a non-negative integer" >&2; exit 2 ;;
esac
if [ "$max_attempts" -lt 1 ]; then
  echo "ERROR NPM_AUDIT_MAX_ATTEMPTS must be at least 1" >&2
  exit 2
fi

attempt=1
while [ "$attempt" -le "$max_attempts" ]; do
  output_file="$(mktemp)"
  set +e
  npm run security >"$output_file" 2>&1
  rc=$?
  set -e
  cat "$output_file"

  if [ "$rc" -eq 0 ]; then
    rm -f "$output_file"
    exit 0
  fi

  if grep -Eq 'audit endpoint returned an error|503 Service Unavailable|502 Bad Gateway|504 Gateway Timeout|500 Internal Server Error' "$output_file"; then
    rm -f "$output_file"
    if [ "$attempt" -lt "$max_attempts" ]; then
      echo "WARN npm audit advisory service unavailable; retrying attempt $((attempt + 1))/$max_attempts after ${delay_seconds}s" >&2
      sleep "$delay_seconds"
      attempt=$((attempt + 1))
      continue
    fi
    echo "ERROR npm audit advisory service unavailable after $max_attempts attempts; failing closed" >&2
    exit "$rc"
  fi

  rm -f "$output_file"
  echo "ERROR npm audit failed for a non-transient reason; failing without retry" >&2
  exit "$rc"
done

exit 1
