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

You need Chrome signed in with bookmark sync on, Claude Code installed and signed in to your Pro account (`claude auth login`), and Python 3.8 or later (`xcode-select --install` if `python3` doesn't run).

1. Clone the repo and run the installer:
   ```
   git clone https://github.com/bertrandvidal/stuff.git
   bash stuff/chrome-bookmarks-organizer/mac-host/install.sh
   ```
   It copies everything to `~/.chrome-bookmarks-organizer`, registers the bridge with Chrome, and checks Claude Code is signed in.
2. In Chrome open `chrome://extensions`, turn on **Developer mode**, click **Load unpacked**, and choose `~/.chrome-bookmarks-organizer/extension` (press Cmd+Shift+. in the picker to show hidden folders).
3. Click the extension's toolbar icon, then **Test Claude Code connection**.
4. Optional: `~/.chrome-bookmarks-organizer/run-host.sh --selftest` asks Claude where a sample link would go among your real folders and prints the answer. Nothing is moved.

The extension creates `_inbox` and `_review` inside `worthy-reads` on its first filing run, about a minute after you load it. They sync to your phone within a minute or so. If you want different names, set them before step 3 (see Folder names below).

## Folder names

Change them on the extension's page (toolbar icon), under Settings.

| Setting | Default | What it is |
|---|---|---|
| Root folder | `worthy-reads` | Your existing top folder. Everything is filed inside it. It must already exist. Matching ignores case, accents, spaces and punctuation, so "Worthy Reads" finds `worthy-reads`. |
| Inbox folder | `_inbox` | Inside the root. Where you save new links. Created if missing. Matched exactly, except for case and surrounding spaces. |
| Review folder | `_review` | Inside the root. Where unclear links wait. Created if missing. Matched like the inbox. |

The leading underscore keeps the two system folders visually apart from your categories. Because they are matched exactly, a category of yours named "Inbox" or "review" stays a category. Renaming the inbox or review folder in Settings also renames the existing folder in Chrome, so nothing is left behind and links already in them stay put. Settings refuses a name with no letters or digits, a name containing `/` (each setting names one folder, never a path), a root folder that doesn't exist, inbox and review names that are too alike, or an inbox or review name that another folder in the root already uses. **Reset folder names to defaults** puts all three back. The Mac side picks up the new names the next time the extension talks to it, so `run-host.sh --tree` and `--selftest` match.

## Saving a link on Android

In Chrome, tap ⋮ then the star. In the "Bookmarked" message tap **Edit**, set the folder to `worthy-reads › _inbox`, and go back. Check whether Chrome reuses that folder for your next bookmark; if it does, saving is one tap from then on.

Filing happens the next time Chrome is open on your Mac: about 30 seconds after the bookmark syncs, plus a safety-net check every 15 minutes. A link that syncs while a run is in progress is picked up about 30 seconds after that run ends. Each link takes Claude roughly 10 to 30 seconds.

## Where links go

Links are only filed into **leaf folders below the top level**: folders with no subfolders of their own, such as `engineering/architecture`, never `engineering` itself. Claude is only offered those folders. If it still answers with a top-level folder, a folder that has subfolders, or one that doesn't exist, or if it isn't confident enough, the link goes to review. An answer that fits more than one folder (two subfolders with the same name, say) also goes to review. A top-level folder with no subfolders never receives links.

## Reviewing and teaching it

- The toolbar icon shows how many links are waiting in `_review`. Click it to see each one with Claude's suggestion and reason, then **File here** (pick another folder first if you disagree) or **Retry**.
- You can also move bookmarks yourself, on any device. If you move something the organizer placed, or file something out of `_review`, that choice is saved as an example and Claude follows it next time. The last 30 are kept; you can see and clear them on the same page.
- For recurring mistakes, add a line to `~/.chrome-bookmarks-organizer/folder-notes.md` explaining where a folder's boundary is. It applies to the next link.
- Settings on the same page: confidence needed to auto-file, model (Sonnet by default, Haiku is lighter on usage), check interval, page read timeout, title cleanup.
- Title cleanup is on by default: when a link is filed, "Title | by Author | Medium" becomes "Title". Claude may only trim the saved title (drop a site name or author). If it suggests different wording, the saved title is kept. When the phone saved the URL as the title, the page's own title is trimmed instead. Links sent to review keep their saved title.

## How Chrome runs the Mac bridge

The bridge is a Chrome native messaging host, not a server or a background service.

1. `install.sh` writes `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.bertrandvidal.chrome_bookmarks_organizer.json`. It names the program to run (`~/.chrome-bookmarks-organizer/run-host.sh`) and the one extension ID allowed to start it.
2. When a filing run starts, the extension calls `chrome.runtime.connectNative("com.bertrandvidal.chrome_bookmarks_organizer")`. Chrome finds that file, checks the extension's ID is allowed, and starts `run-host.sh` as a child process, as your macOS user.
3. `run-host.sh` just runs `host.py` with the Python found at install time. Chrome and `host.py` exchange JSON over the process's stdin and stdout. No port is opened.
4. For each link, `host.py` runs `claude -p ...` as its own child process, which reads your Claude login from the Keychain like it does in Terminal.
5. When the run ends, the extension disconnects, Chrome closes the pipe, and `host.py` exits. Nothing runs between runs, and nothing runs while Chrome is quit.

Chrome started from the Dock doesn't read your shell profile, so its PATH is the bare system one, not your Terminal's. That's why `install.sh` records the absolute paths of `python3` and `claude`, and `host.py` also checks `~/.local/bin`, `~/.claude/local`, `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin` and `/bin`. If you move or reinstall Claude Code, re-run `install.sh`.

## How it reads pages

1. Plain fetch from inside Chrome, without your cookies. Enough for most blogs. Only the first 300,000 characters of the page are read.
2. If that's blocked (Medium, Substack and Cloudflare-protected sites often block non-browser requests) or too thin, it opens the page in a minimized window for a few seconds, reads it like a normal visit (with your logins), and closes it. You may briefly see it in the Dock. PDFs, downloads and dead links (404, 410) skip this step, since a window would only download the file again or show an error page.
3. If both fail, Claude gets the saved title and URL (the slug usually contains the title). Its instructions allow one web search, only when the title and URL are ambiguous.

Each of the first two steps gets the **page read timeout** (30 seconds by default, set on the extension's page). If the window hasn't produced a reading by then, it is closed and the link is filed from what the plain fetch got, or else from the title and URL.

Pages on your Mac or local network (localhost, private IP addresses, `.local` names, single-word names like `router`) are never read, including when a public page redirects there. Those links are filed from their title and URL.

The same link saved twice, even with different tracking parameters such as `?utm_source=`, is filed once; the copy goes to review as a duplicate. That includes a link whose first copy is still waiting in `_review` or sits directly in the root folder. Parameters that pick a different page, such as a search term or a git branch, are kept, so those links aren't mistaken for duplicates.

Paywalled articles usually categorize fine: the title, description and opening paragraphs are enough.

## When Claude Code can't run

If Claude Code is signed out, has hit your plan's usage limit, can't reach Claude (the Mac is offline), can't be found, or is too old, filing pauses. Links wait in the inbox, nothing counts against them, and the status card on the extension's page says what to do. The next run picks up where it left off.

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Native host not installed" | Run `install.sh` again, then reload the extension on `chrome://extensions`. |
| "Native host refused this extension" | The extension ID differs from the default. Copy the ID from `chrome://extensions` and run `install.sh <that-id>`. |
| "Lost the connection to the Mac bridge" or "Native host crashed" | Check `~/.chrome-bookmarks-organizer/host.log`, then click **File inbox now**. |
| "Claude Code isn't signed in" | Run `claude auth login` in Terminal. If Terminal works but Chrome doesn't, run `claude setup-token` and put the token in `~/.chrome-bookmarks-organizer/config.json` as `"env": {"CLAUDE_CODE_OAUTH_TOKEN": "..."}`. |
| "Claude usage limit reached" | Nothing to do: links wait in the inbox and are filed after the limit resets. Haiku (in Settings) uses less. |
| "Couldn't find a bookmark folder named ..." | Set your root folder's name in the extension settings. |
| Nothing happens | Check the bookmark reached the Mac's `_inbox` (sync), then click **File inbox now**. The extension's page shows the activity log; the Mac bridge logs to `~/.chrome-bookmarks-organizer/host.log`. |

## Updating

```
cd stuff && git pull && bash chrome-bookmarks-organizer/mac-host/install.sh
```

Then click the reload icon on the extension in `chrome://extensions`. Your folder notes, settings and `config.json` are kept. `rules.md` is replaced with the new version; if yours differed, the old copy is saved as `rules.md.bak`.

## Development

From `chrome-bookmarks-organizer/`, `npm test` runs everything: Node tests for the extension against a simulated Chrome (`tests/*.test.mjs`), and Python tests for the Mac bridge against a fake `claude` binary and a fake Chrome profile (`tests/test_host.py`). No network, no real Claude calls, nothing to install beyond Node 21+ (for the test file pattern) and Python 3.8+.

## Files

- `extension/`: the Chrome extension (Manifest V3).
- `mac-host/host.py`: the bridge Chrome launches; runs `claude -p` with web search as its only tool and no MCP servers. Text from the web goes to Claude inside blocks whose tag is random on every request, with angle brackets neutralized, so it can't break out of them: the bookmark's title, URL and page content, and also the titles of bookmarks already filed and of your past decisions, since those were saved from web pages too.
  - Isolation: web search only, no MCP tools or servers, nothing outside pre-approved actions. These are never dropped; if Claude Code doesn't support one, filing pauses with "Update Claude Code" on the status card and links wait in the inbox. Two more flags, `--safe-mode` (no CLAUDE.md, hooks, plugins or skills) and `--no-session-persistence` (no saved sessions), are used whenever Claude Code supports them, which current versions do; an older Claude Code that rejects one runs without it for that run only. **Test Claude Code connection** shows which are active.
  - Only your Claude subscription login is used: API credentials in the environment or in `config.json` are never passed to Claude Code.
  - Claude's answer is checked before use: every field is capped and stripped of control characters, and a folder it names must exist.
- `mac-host/rules.md`: how Claude decides. Shared with the chat skill.
- `mac-host/folder-notes.md`: your notes on what each folder means. Installed once, then yours to edit.
- `mac-host/uninstall.sh`: removes the bridge. Bookmarks are never deleted by any part of this.

Each link is one Claude Code run on your Pro plan, of up to 6 turns. Claude receives the page's title, description, headings and keywords, plus up to 3,500 characters of its text.
