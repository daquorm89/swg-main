#!/bin/bash
# Safe replacement for "git reset --hard origin/master" in serverdata (or dsrc).
# Usage: utils/safe_data_update.sh serverdata   |   utils/safe_data_update.sh dsrc
# Refuses to reset if origin/master is missing sentinel files or is much smaller than the current tree.
set -e
sub=${1:?usage: safe_data_update.sh serverdata|dsrc}
cd "$(cd "$(dirname "$0")/.." && pwd)/$sub"
git fetch origin
new=$(git ls-tree -r --name-only origin/master | wc -l)
cur=$(git ls-files | wc -l)
echo "$sub: current tracked files $cur, origin/master files $new"
if [ "$cur" -gt 100 ] && [ $((new*10)) -lt $((cur*9)) ]; then
  echo "REFUSING: origin/master is >10% smaller than the current tree. Not resetting."; exit 1; fi
case "$sub" in
  serverdata) S="appearance/defaultappearance.apt string/en/pet/pet_menu.stf datatables/combat/combat_data.iff" ;;
  dsrc)       S="sku.0/sys.server/compiled/game/script/ai/ai.java" ;;
esac
for f in $S; do git ls-tree -r --name-only origin/master | grep -qx "$f" || { echo "REFUSING: origin/master lacks $f"; exit 1; }; done
git checkout master
git reset --hard origin/master
echo "OK: $sub now at $(git log -1 --format='%h %s')"
