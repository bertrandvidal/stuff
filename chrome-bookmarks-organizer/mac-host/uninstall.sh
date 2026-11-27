#!/bin/bash
# Removes the native messaging host registration and ~/.worthy-reads-filer.
# Your bookmarks are not touched. Remove the extension itself from chrome://extensions.
set -euo pipefail
NM="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.worthyreads.filer.json"
APP="$HOME/.worthy-reads-filer"
rm -f "$NM" && echo "Removed $NM"
if [ -d "$APP" ]; then
  read -r -p "Delete $APP (includes your folder-notes.md)? [y/N] " ans
  if [ "${ans:-n}" = "y" ]; then rm -rf "$APP" && echo "Removed $APP"; else echo "Kept $APP"; fi
fi
