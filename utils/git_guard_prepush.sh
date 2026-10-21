#!/bin/bash
# Pre-push guard (installed as .git hook in dsrc, serverdata, src, swg-main).
# Blocks pushes that delete many files or drop the tree size, or lose sentinel files.
# Override ONLY for a deliberate mass deletion:  GUARD_ALLOW_DELETIONS=1 git push ...
MAX_DELETED=${GUARD_MAX_DELETED:-25}
ZERO=0000000000000000000000000000000000000000
repo=$(basename "$(git rev-parse --show-toplevel)")
case "$repo" in
  serverdata) SENTINELS="appearance/defaultappearance.apt string/en/pet/pet_menu.stf datatables/combat/combat_data.iff" ;;
  dsrc)       SENTINELS="sku.0/sys.server/compiled/game/script/ai/ai.java" ;;
  *)          SENTINELS="" ;;
esac
fail=0
while read -r lref lsha rref rsha; do
  [ "$lsha" = "$ZERO" ] && continue                       # deleting a remote branch: ignore
  if [ "$rsha" != "$ZERO" ] && git cat-file -e "$rsha^{commit}" 2>/dev/null; then base=$rsha
  else base=$(git merge-base "$lsha" origin/master 2>/dev/null || true); fi
  [ -z "$base" ] && continue
  deleted=$(git diff --diff-filter=D --name-only "$base" "$lsha" | wc -l)
  before=$(git ls-tree -r --name-only "$base" | wc -l)
  after=$(git ls-tree -r --name-only "$lsha" | wc -l)
  if [ "$deleted" -gt "$MAX_DELETED" ] && [ "${GUARD_ALLOW_DELETIONS:-0}" != 1 ]; then
    echo "GUARD BLOCKED ($repo): $lref deletes $deleted files (limit $MAX_DELETED). Tree $before -> $after files."; fail=1; fi
  if [ "$before" -gt 100 ] && [ $((after*10)) -lt $((before*9)) ] && [ "${GUARD_ALLOW_DELETIONS:-0}" != 1 ]; then
    echo "GUARD BLOCKED ($repo): $lref shrinks the tree by more than 10% ($before -> $after)."; fail=1; fi
  for f in $SENTINELS; do
    if git ls-tree -r --name-only "$base" | grep -qx "$f" && ! git ls-tree -r --name-only "$lsha" | grep -qx "$f"; then
      echo "GUARD BLOCKED ($repo): sentinel file missing in $lref: $f"; fail=1; fi
  done
done
[ $fail = 1 ] && echo "Push refused. Inspect with: git diff --stat <base> $lref" && exit 1
exit 0
