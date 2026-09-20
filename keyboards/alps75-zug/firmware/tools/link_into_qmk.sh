#!/bin/sh
# Symlink this keyboard into your qmk_firmware clone so the QMK CLI can find it.
#
# QMK resolves keyboards only under $QMK_HOME/keyboards (see lib/python/qmk/path.py,
# is_keyboard()); an external userspace holds keymaps, not new keyboards. A symlink
# keeps the definition versioned here while satisfying that lookup, and keeps every
# build artifact inside $QMK_HOME rather than in this repository.
#
# Usage:  sh firmware/tools/link_into_qmk.sh
set -eu

kb_src=$(cd "$(dirname "$0")/../keyboards/alps75_zug" && pwd)
qmk_home=$(qmk config user.qmk_home | sed 's/^user.qmk_home=//; s/ .*//')

if [ -z "$qmk_home" ] || [ "$qmk_home" = "None" ]; then
    echo "qmk home is not configured. Run: qmk setup" >&2
    exit 1
fi
if [ ! -d "$qmk_home/keyboards" ]; then
    echo "$qmk_home does not look like a qmk_firmware clone" >&2
    exit 1
fi

ln -sfn "$kb_src" "$qmk_home/keyboards/alps75_zug"
echo "linked $qmk_home/keyboards/alps75_zug -> $kb_src"
qmk lint -kb alps75_zug -km zug --strict
