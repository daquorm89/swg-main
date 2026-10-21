#!/bin/bash
# Installs the pre-push guard in swg-main and every initialised submodule. Re-run after fresh clones.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
for d in "$ROOT" "$ROOT"/dsrc "$ROOT"/serverdata "$ROOT"/src "$ROOT"/exe "$ROOT"/stationapi; do
  [ -e "$d/.git" ] || continue
  hook=$(git -C "$d" rev-parse --git-path hooks)/pre-push
  case "$hook" in /*) ;; *) hook="$d/$hook";; esac
  mkdir -p "$(dirname "$hook")"
  cp -f "$ROOT/utils/git_guard_prepush.sh" "$hook" && chmod +x "$hook"
  echo "installed: $hook"
done
