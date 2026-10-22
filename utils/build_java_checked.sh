#!/bin/bash
# Builds one or more dsrc Java files and FAILS LOUDLY if nothing was really built.
# Usage (from ~/repos/swg-main):
#   ./utils/build_java_checked.sh dsrc/sku.0/sys.server/compiled/game/script/library/stationed_droid.java [more.java ...]
# Checks: build_java_single.sh is not empty, javac succeeds, and each .class is newer than its source.

cd "$(dirname "$0")/.." || exit 1
destination="data/sku.0/sys.server/compiled/game"
sourcepath="dsrc/sku.0/sys.server/compiled/game"

if [ $# -lt 1 ]; then
    echo "usage: $0 <path/to/file.java> [...]"
    exit 1
fi
if [ ! -s utils/build_java_single.sh ]; then
    echo "WARNING: utils/build_java_single.sh is empty or missing (restore with: git checkout -- utils/build_java_single.sh). Using javac directly."
fi

mkdir -p "$destination/script"
failed=0
for src in "$@"; do
    if [ ! -f "$src" ]; then
        echo "FAIL: source not found: $src"
        failed=1
        continue
    fi
    if ! javac -Xlint:-options -encoding utf8 -classpath "$destination" -d "$destination" -sourcepath "$sourcepath" -g -deprecation "$src"; then
        echo "FAIL: javac reported errors for $src"
        failed=1
        continue
    fi
    rel="${src#$sourcepath/}"
    cls="$destination/${rel%.java}.class"
    if [ ! -f "$cls" ] || [ "$cls" -ot "$src" ]; then
        echo "FAIL: $cls is missing or older than $src (nothing was built)"
        failed=1
        continue
    fi
    echo "OK: $cls built $(date -r "$cls" '+%Y-%m-%d %H:%M:%S')"
done

if [ $failed -ne 0 ]; then
    echo "BUILD FAILED - do not restart the server expecting new behaviour."
    exit 1
fi
echo "ALL OK. Restart the GameServer: Java classes only load at startup."
