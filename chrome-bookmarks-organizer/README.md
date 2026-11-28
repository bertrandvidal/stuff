# Chrome Bookmarks Organizer

Bookmark a link into `worthy-reads/_inbox` from your phone. Chrome on your Mac picks it up through Chrome Sync, works out what the page is about, asks Claude Code which folder it belongs in, and moves it there. Links Claude isn't sure about wait in `worthy-reads/_review`. All three folder names are settings; these are the defaults.

```
Android Chrome ──(sync)──▶ worthy-reads/_inbox
                                  │  Mac Chrome extension (runs whenever Chrome is open)
                                  ▼
                read page: plain fetch ▶ hidden window if blocked ▶ title + URL only
                                  │
                                  ▼  native messaging
                     Claude Code (`claude -p`, your Pro plan)
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
     worthy-reads/engineering/...        worthy-reads/_review
```

## One-time setup on the Mac (about 5 minutes)

You need Chrome signed in with bookmark sync on, Claude Code installed and signed in to your Pro account (`claude auth login`), and Python 3 (`xcode-select --install` if `python3` doesn't run).

1. Clone the repo and run the installer:
   ```
   git clone https://github.com/bertrandvidal/stuff.git
   bash stuff/chrome-bookmarks-organizer/mac-host/install.sh
   ```
   It copies everything to `~/.chrome-bookmarks-organizer`, registers the bridge with Chrome, and checks Claude Code is signed in.
2. In Chrome open `chrome://extensions`, turn on **Developer mode**, click **Load unpacked**, and choose `~/.chrome-bookmarks-organizer/extension` (press Cmd+Shift+. in the picker to show hidden folders).
3. Click the extension's toolbar icon, then **Test Claude Code connection**.
4. Optional: `~/.chrome-bookmarks-organizer/run-host.sh --selftest` files a sample link against your real folders and prints Claude's answer.

The extension creates `_inbox` and `_review` inside `worthy-reads` on its first run. They sync to your phone within a minute or so. If you want different names, set them before step 3 (see Folder names below).

## Folder names

Change them on the extension's page (toolbar icon), under Settings. Matching ignores case, spaces and dashes, so "Worthy Reads" finds `worthy-reads`.

| Setting | Default | What it is |
|---|---|---|
| Root folder | `worthy-reads` | Your existing top folder. Everything is filed inside it. It must already exist. |
| Inbox folder | `_inbox` | Inside the root. Where you save new links. Created if missing. |
| Review folder | `_review` | Inside the root. Where unclear links wait. Created if missing. |

The leading underscore keeps the two system folders visually apart from your categories. Renaming the inbox or review folder in Settings also renames the existing folder in Chrome, so nothing is left behind and links already in them stay put. Settings refuses a name that another folder in the root already uses, a root folder that doesn't exist, the same name for inbox and review, or a name containing `/` (each setting names one folder, never a path, so it can't create subfolders). **Reset folder names to defaults** puts all three back. The Mac side picks up the new names the next time the extension talks to it, so `run-host.sh --tree` and `--selftest` match.

## Saving a link on Android

In Chrome, tap ⋮ then the star. In the "Bookmarked" message tap **Edit**, set the folder to `worthy-reads › _inbox`, and go back. Check whether Chrome reuses that folder for your next bookmark; if it does, saving is one tap from then on.

Filing happens the next time Chrome is open on your Mac: about 30 seconds after the bookmark syncs, plus a safety-net check every 15 minutes. Each link takes Claude roughly 10 to 30 seconds.

## Where links go

Links are only filed into **leaf folders below the top level**: folders with no subfolders of their own, such as `engineering/architecture`, never `engineering` itself. Claude is only offered those folders. If it still answers with a top-level folder, a folder that has subfolders, or one that doesn't exist, or if it isn't confident enough, the link goes to review. A top-level folder with no subfolders never receives links.

## Reviewing and teaching it

- The toolbar icon shows how many links are waiting in `_review`. Click it to see each one with Claude's suggestion and reason, then **File here** (pick another folder first if you disagree) or **Retry**.
- You can also move bookmarks yourself, on any device. If you move something the organizer placed, or file something out of `_review`, that choice is saved as an example and Claude follows it next time. The last 30 are kept; you can see and clear them on the same page.
- For recurring mistakes, add a line to `~/.chrome-bookmarks-organizer/folder-notes.md` explaining where a folder's boundary is. It applies to the next link.
- Settings on the same page: confidence needed to auto-file, model (Sonnet by default, Haiku is lighter on usage), check interval, page read timeout, title cleanup (on by default: "Title | by Author | Medium" becomes "Title").

## How Chrome runs the Mac bridge

The bridge is a Chrome native messaging host, not a server or a background service.

1. `install.sh` writes `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.bertrandvidal.chrome_bookmarks_organizer.json`. It names the program to run (`~/.chrome-bookmarks-organizer/run-host.sh`) and the one extension ID allowed to start it.
2. When a filing run starts, the extension calls `chrome.runtime.connectNative("com.bertrandvidal.chrome_bookmarks_organizer")`. Chrome finds that file, checks the extension's ID is allowed, and starts `run-host.sh` as a child process, as your macOS user.
3. `run-host.sh` just runs `host.py` with the Python found at install time. Chrome and `host.py` exchange JSON over the process's stdin and stdout. No port is opened.
4. For each link, `host.py` runs `claude -p ...` as its own child process, which reads your Claude login from the Keychain like it does in Terminal.
5. When the run ends, the extension disconnects, Chrome closes the pipe, and `host.py` exits. Nothing runs between runs, and nothing runs while Chrome is quit.

Chrome started from the Dock doesn't read your shell profile, so its PATH is the bare system one, not your Terminal's. That's why `install.sh` records the absolute paths of `python3` and `claude`, and `host.py` also checks `~/.local/bin`, `/opt/homebrew/bin` and `/usr/local/bin`. If you move or reinstall Claude Code, re-run `install.sh`.

## How it reads pages

1. Plain fetch from inside Chrome, with your cookies. Enough for most blogs. Only the first 300 KB of the page is read.
2. If that's blocked (Medium, Substack and Cloudflare-protected sites often block non-browser requests) or too thin, it opens the page in a minimized window for a few seconds, reads it like a normal visit, and closes it. You may briefly see it in the Dock. PDFs, downloads and dead links (404, 410) skip this step, since a window would only download the file again or show an error page.
3. If both fail, Claude gets the saved title and URL (the slug usually contains the title) and may run one web search on it.

Each of the first two steps gets the **page read timeout** (30 seconds by default, set on the extension's page). A page that never finishes loading is read as far as it got, its window is closed, and filing moves on.

The same link saved twice, even with different tracking parameters such as `?utm_source=`, is filed once; the copy goes to review as a duplicate.

Paywalled articles still categorize fine: the title, description and opening paragraphs are enough.

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Native host not installed" | Run `install.sh` again, then reload the extension on `chrome://extensions`. |
| "Native host refused this extension" | The extension ID differs from the default. Copy the ID from `chrome://extensions` and run `install.sh <that-id>`. |
| "Claude Code isn't signed in" | Run `claude auth login` in Terminal. If Terminal works but Chrome doesn't, run `claude setup-token` and put the token in `~/.chrome-bookmarks-organizer/config.json` as `"env": {"CLAUDE_CODE_OAUTH_TOKEN": "..."}`. |
| "Couldn't find a bookmark folder named ..." | Set your root folder's name in the extension settings. |
| Nothing happens | Check the bookmark reached the Mac's `_inbox` (sync), then click **File inbox now**. Details are in `~/.chrome-bookmarks-organizer/host.log`. |

## Updating

```
cd stuff && git pull && bash chrome-bookmarks-organizer/mac-host/install.sh
```

Then click the reload icon on the extension in `chrome://extensions`. Your folder notes and settings are kept.

## Development

From `chrome-bookmarks-organizer/`, `npm test` runs everything: Node tests for the extension against a simulated Chrome (`tests/*.test.mjs`), and Python tests for the Mac bridge against a fake `claude` binary and a fake Chrome profile (`tests/test_host.py`). No network, no real Claude calls, nothing to install beyond Node 20+ and Python 3.8+.

## Files

- `extension/`: the Chrome extension (Manifest V3).
- `mac-host/host.py`: the bridge Chrome launches; runs `claude -p` with web search as its only tool, no MCP servers, no CLAUDE.md, no saved sessions. The bookmark's title, URL and page text go to Claude inside a block whose tag is random on every request, with angle brackets neutralized, so web text can't break out of it.
  - Isolation: web search only, no MCP tools or servers, nothing outside pre-approved actions. These are never dropped; if Claude Code doesn't support one, filing pauses with "Update Claude Code" on the status card and links wait in the inbox. Two optional flags (`--safe-mode`, `--no-session-persistence`) are skipped for that run only if an older Claude Code rejects them. **Test Claude Code connection** shows which are active.
- `mac-host/rules.md`: how Claude decides. Shared with the chat skill.
- `mac-host/folder-notes.md`: your notes on what each folder means. Installed once, then yours to edit.
- `mac-host/uninstall.sh`: removes the bridge. Bookmarks are never deleted by any part of this.

Each link is one Claude Code request on your Pro plan, and the page excerpt (up to about 4,000 characters) is sent to Claude.
