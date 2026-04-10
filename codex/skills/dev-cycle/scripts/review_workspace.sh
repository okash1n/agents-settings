#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-}"

if [[ -z "$cmd" ]]; then
  echo "usage: review_workspace.sh init" >&2
  exit 2
fi

case "$cmd" in
  init)
    if [[ -e 00-review || -L 00-review ]]; then
      if [[ -d 00-review ]]; then
        exit 0
      fi

      echo "00-review exists but is not a directory: $(pwd)/00-review" >&2
      exit 1
    fi

    mkdir -p 00-review
    ;;
  *)
    echo "unknown command: $cmd" >&2
    exit 2
    ;;
esac
