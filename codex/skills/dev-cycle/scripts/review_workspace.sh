#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-}"

if [[ -z "$cmd" ]]; then
  echo "usage: review_workspace.sh init" >&2
  exit 2
fi

case "$cmd" in
  init)
    mkdir -p 00-review
    mkdir -p .git/info
    touch .git/info/exclude

    if ! grep -Fxq '00-review/' .git/info/exclude; then
      printf '\n00-review/\n' >> .git/info/exclude
    fi
    ;;
  *)
    echo "unknown command: $cmd" >&2
    exit 2
    ;;
esac
