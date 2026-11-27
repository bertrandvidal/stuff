#!/bin/bash
# Installs the Worthy Reads Filer bridge between Chrome and Claude Code.
# Usage: bash install.sh [extension-id]
# Safe to re-run: it updates the code and keeps your folder-notes.md and config.
set -euo pipefail

HOST_NAME="com.worthyreads.filer"
EXT_ID="${1:-ihiohmhmhgmfdlgneaejjdbibocdhapp}"   # fixed by the key in manifest.json
SRC="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/.worthy-reads-filer"
NM_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }
die() { printf '\n\033[31mError:\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(uname)" = "Darwin" ] || die "This installer is for macOS."

say "1/5 Checking Python"
PY="$(command -v python3 || true)"
[ -n "$PY" ] || die "python3 not found. Run: xcode-select --install"
"$PY" -c 'import sys; assert sys.version_info >= (3, 8)' 2>/dev/null \
  || die "python3 at $PY doesn't run (or is older than 3.8). Run: xcode-select --install"
echo "Using $PY ($("$PY" --version 2>&1))"

say "2/5 Finding Claude Code"
CLAUDE="$(command -v claude || true)"
for c in "$HOME/.local/bin/claude" "$HOME/.claude/local/claude" /opt/homebrew/bin/claude /usr/local/bin/claude; do
  [ -z "$CLAUDE" ] && [ -x "$c" ] && CLAUDE="$c"
done
[ -n "$CLAUDE" ] || die "Claude Code not found. Install it (https://code.claude.com), run 'claude auth login', then re-run this script."
echo "Using $CLAUDE ($("$CLAUDE" --version 2>/dev/null | head -1))"

say "3/5 Installing files to $APP"
mkdir -p "$APP/workdir"
cp "$SRC/host.py" "$APP/host.py"
if [ -f "$APP/rules.md" ] && ! cmp -s "$SRC/rules.md" "$APP/rules.md"; then
  cp "$APP/rules.md" "$APP/rules.md.bak"
  echo "Updated rules.md (previous copy saved as rules.md.bak)"
fi
cp "$SRC/rules.md" "$APP/rules.md"
if [ -f "$APP/folder-notes.md" ]; then
  echo "Kept your existing folder-notes.md"
else
  cp "$SRC/folder-notes.md" "$APP/folder-notes.md"
fi
if [ -d "$SRC/../extension" ]; then
  rm -rf "$APP/extension"
  cp -R "$SRC/../extension" "$APP/extension"
fi

cat > "$APP/run-host.sh" <<EOF
#!/bin/bash
exec "$PY" "$APP/host.py" "\$@"
EOF
chmod 755 "$APP/run-host.sh" "$APP/host.py"

"$PY" - "$APP/config.json" "$CLAUDE" <<'PYEOF'
import json, sys
path, claude = sys.argv[1], sys.argv[2]
try:
    cfg = json.load(open(path))
except Exception:
    cfg = {}
cfg["claude_path"] = claude
cfg["compat"] = False  # re-detect on next run in case Claude Code was updated
json.dump(cfg, open(path, "w"), indent=2)
PYEOF
chmod 600 "$APP/config.json"

say "4/5 Registering native messaging host for extension $EXT_ID"
mkdir -p "$NM_DIR"
cat > "$NM_DIR/$HOST_NAME.json" <<EOF
{
  "name": "$HOST_NAME",
  "description": "Worthy Reads Filer: asks Claude Code where a bookmark belongs",
  "path": "$APP/run-host.sh",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://$EXT_ID/"]
}
EOF
echo "Wrote $NM_DIR/$HOST_NAME.json"

say "5/5 Checking Claude Code sign-in"
"$APP/run-host.sh" --ping || true

cat <<EOF

Done. Next:
  1. Chrome > chrome://extensions > turn on Developer mode > Load unpacked >
     choose: $APP/extension
     (press Cmd+Shift+. in the file picker to show hidden folders)
  2. Click the extension's icon > "Test Claude Code connection".
  3. Optional end-to-end check from Terminal:
     $APP/run-host.sh --selftest

Your folder notes: $APP/folder-notes.md
Logs:              $APP/host.log
EOF
