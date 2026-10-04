#!/usr/bin/env bash
# Serve docs/ locally for a preview of the online lookup.
#
# Cygnet's own run.sh picks the first free port from 8801 and prints an ssh -L
# line for remote access, so it is used when a sibling checkout is there. But
# serving docs/ needs nothing except a static file server -- the lookup is a
# single HTML file and two SQLite databases, all of it client-side -- so without
# Cygnet we fall back to Python's. Somebody who has cloned this repository to look
# at the wordnet should not need a second repository to do it.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-8801}"

if [[ ! -f "$SCRIPT_DIR/docs/hmong.db.gz" ]]; then
    echo "docs/hmong.db.gz is missing: the databases are not in the repository," >&2
    echo "because they are 35 MB. Either" >&2
    echo "  - download them from the latest release into docs/, or" >&2
    echo "  - build them with ./build.sh, which needs a ../cygnet checkout." >&2
    echo "See 'Hosting the lookup locally' in README.md." >&2
    exit 1
fi

if [[ -f "$SCRIPT_DIR/../cygnet/run.sh" ]]; then
    CYGNET_DIR="$(cd "$SCRIPT_DIR/../cygnet" && pwd)"
    exec bash "$CYGNET_DIR/run.sh" "$SCRIPT_DIR/docs"
fi

echo "no ../cygnet checkout; serving docs/ with python3 -m http.server" >&2
echo "  http://localhost:$PORT/" >&2
exec python3 -m http.server "$PORT" --directory "$SCRIPT_DIR/docs"
