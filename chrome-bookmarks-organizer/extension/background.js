// Chrome Bookmarks Organizer: background service worker.
//
// Flow: a bookmark lands in the inbox folder (default worthy-reads/_inbox),
// usually via Chrome Sync from the phone -> we extract what the page is about
// -> Claude Code on this Mac picks a folder through the native messaging host
// -> we move the bookmark, or park it in the review folder (default
// worthy-reads/_review) when Claude isn't confident. Folder names are settings.

import { HOST_NAME, CONFIDENCE_RANK, DEFAULTS, getSettings } from './lib/config.js';
import {
  findRootFolder, findChildFolder, collectFolders, indexUrls, normalizeUrl,
  resolveFolder, treeToMarkdown, truncate, folderNameProblems, planFolderRenames,
} from './lib/tree.js';
import { parseHtmlMeta, looksBlocked, isGoodEnough, mergeContent, pageExtractor, MAX_HTML } from './lib/extract.js';

const MAX_LOG = 150;
const MAX_EXAMPLES = 30;
const LOCK_STALE_MS = 15 * 60 * 1000;

// Bookmark ids we are moving ourselves, so onMoved doesn't record them as corrections.
const selfMoves = new Set();
let sweeping = false;

// ---------- lifecycle ----------

chrome.runtime.onInstalled.addListener(() => setup());
chrome.runtime.onStartup.addListener(() => setup());
chrome.action.onClicked.addListener(() => chrome.runtime.openOptionsPage());

async function setup() {
  const s = await getSettings();
  await chrome.alarms.create('sweep', { periodInMinutes: Math.max(1, s.sweepMinutes), delayInMinutes: 1 });
  await updateBadge();
}

chrome.alarms.onAlarm.addListener((a) => {
  if (a.name === 'sweep' || a.name === 'sweep-soon') sweep(`alarm:${a.name}`);
});

function scheduleSoon() {
  // Debounced: sync often delivers several bookmarks in a burst.
  chrome.alarms.create('sweep-soon', { delayInMinutes: 0.5 });
}

chrome.bookmarks.onCreated.addListener(async (id, node) => {
  if (!node.url) return;
  const ctx = await getContext({ create: false });
  if (ctx.inbox && node.parentId === ctx.inbox.id) scheduleSoon();
});

chrome.bookmarks.onMoved.addListener(async (id, info) => {
  if (selfMoves.has(id)) { selfMoves.delete(id); return; }
  const ctx = await getContext({ create: false });
  if (ctx.inbox && info.parentId === ctx.inbox.id) scheduleSoon();
  await trackUserMove(id, info, ctx);
  if (ctx.review && (info.parentId === ctx.review.id || info.oldParentId === ctx.review.id)) updateBadge();
});

chrome.bookmarks.onRemoved.addListener(() => updateBadge());

// ---------- storage helpers ----------

async function getStore(keys) { return chrome.storage.local.get(keys); }
async function setStore(obj) { return chrome.storage.local.set(obj); }

async function log(entry) {
  const { log: entries = [] } = await getStore('log');
  entries.unshift({ at: Date.now(), level: 'info', ...entry });
  await setStore({ log: entries.slice(0, MAX_LOG) });
}

async function setStatus(patch) {
  const { status = {} } = await getStore('status');
  await setStore({ status: { ...status, ...patch } });
}

// ---------- folder context ----------

async function getContext({ create }) {
  const s = await getSettings();
  const tree = await chrome.bookmarks.getTree();
  const { node: root, warning } = findRootFolder(tree, s.rootFolderName);
  if (!root) return { s, error: `Couldn't find a bookmark folder named "${s.rootFolderName}". Check the name in settings.` };
  let inbox = findChildFolder(root, s.inboxName);
  let review = findChildFolder(root, s.reviewName);
  if (create && !inbox) inbox = await chrome.bookmarks.create({ parentId: root.id, title: s.inboxName, index: 0 });
  if (create && !review) review = await chrome.bookmarks.create({ parentId: root.id, title: s.reviewName, index: 1 });
  const folders = collectFolders(root, { exclude: [s.inboxName, s.reviewName], samples: s.samplesPerFolder });
  return { s, root, inbox, review, folders, warning };
}

// Sent with every host message so the Mac side's CLI tools (--tree, --selftest)
// use the same names as the extension.
const folderNames = (s) => ({ root: s.rootFolderName, inbox: s.inboxName, review: s.reviewName });

async function saveSettings(input) {
  const prev = await getSettings();
  const next = { ...DEFAULTS, ...prev, ...input };
  for (const k of ['rootFolderName', 'inboxName', 'reviewName']) next[k] = String(next[k] ?? '').trim();

  const problems = folderNameProblems(next);
  if (problems.length) return { error: problems.join(' ') };

  const tree = await chrome.bookmarks.getTree();
  const { node: root } = findRootFolder(tree, next.rootFolderName);
  if (!root) {
    return { error: `No bookmark folder named "${next.rootFolderName}" was found. Create it in Chrome first, or check the spelling.` };
  }
  const { renames, errors } = planFolderRenames(root, prev, next);
  if (errors.length) return { error: errors.join(' ') };

  for (const r of renames) {
    await chrome.bookmarks.update(r.id, { title: r.title });
    await log({ msg: `Renamed folder "${r.from}" to "${r.title}"` });
  }
  await chrome.storage.local.set({ settings: next });
  await setup();
  return { ok: true, renamed: renames.map((r) => `${r.from} → ${r.title}`) };
}

async function moveTo(id, parentId) {
  selfMoves.add(id);
  try {
    await chrome.bookmarks.move(id, { parentId });
  } catch (e) {
    selfMoves.delete(id);
    throw e;
  }
}

// ---------- native host (Claude Code) ----------

class HostClient {
  constructor(name) {
    this.name = name;
    this.pending = new Map();
    this.seq = 0;
    this.dead = null;
  }
  connect() {
    // An open native port keeps the service worker alive while Claude works.
    this.port = chrome.runtime.connectNative(this.name);
    this.port.onMessage.addListener((m) => {
      const p = this.pending.get(m.id);
      if (!p) return;
      this.pending.delete(m.id);
      clearTimeout(p.timer);
      p.resolve(m);
    });
    this.port.onDisconnect.addListener(() => {
      const raw = chrome.runtime.lastError?.message || 'Native host disconnected';
      if (/not found/i.test(raw)) {
        this.dead = `Native host not installed (${raw}) Run mac-host/install.sh.`;
      } else if (/forbidden/i.test(raw)) {
        this.dead = `Native host refused this extension (${raw}) Re-run install.sh with the ID shown on chrome://extensions.`;
      } else if (/exited/i.test(raw)) {
        this.dead = `Native host crashed (${raw}) Check ~/.chrome-bookmarks-organizer/host.log.`;
      } else {
        this.dead = raw;
      }
      for (const p of this.pending.values()) { clearTimeout(p.timer); p.reject(new Error(this.dead)); }
      this.pending.clear();
    });
  }
  request(type, payload = {}, timeoutMs = 300000) {
    if (this.dead) return Promise.reject(new Error(this.dead));
    const id = ++this.seq;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error('Timed out waiting for Claude Code'));
      }, timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
      try {
        this.port.postMessage({ id, type, ...payload });
      } catch (e) {
        clearTimeout(timer);
        this.pending.delete(id);
        reject(e);
      }
    });
  }
  disconnect() { try { this.port?.disconnect(); } catch { /* already closed */ } }
}

// ---------- content extraction ----------

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function withTimeout(promise, ms, message) {
  let timer;
  const timeout = new Promise((_, reject) => { timer = setTimeout(() => reject(new Error(message)), ms); });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

// Read at most `max` characters of the body, then stop the download.
async function readCapped(res, max) {
  if (!res.body?.getReader) return (await res.text()).slice(0, max);
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let out = '';
  try {
    while (out.length < max) {
      const { done, value } = await reader.read();
      if (done) break;
      out += decoder.decode(value, { stream: true });
    }
  } finally {
    reader.cancel().catch(() => {});
  }
  return out.slice(0, max);
}

async function fetchPage(url, timeoutMs) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      credentials: 'include',
      redirect: 'follow',
      signal: ctrl.signal,
      headers: { Accept: 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8' },
    });
    const ct = res.headers.get('content-type') || '';
    const download = /attachment/i.test(res.headers.get('content-disposition') || '');
    if (!/html|xml/i.test(ct) || download) {
      res.body?.cancel?.().catch?.(() => {});
      return { ok: res.ok, status: res.status, isHtml: false, content: { contentType: ct || 'unknown', finalUrl: res.url } };
    }
    const html = await readCapped(res, MAX_HTML);
    const content = { ...parseHtmlMeta(html), finalUrl: res.url };
    return { ok: res.ok, status: res.status, isHtml: true, blocked: looksBlocked(res.status, content.pageTitle, html), content };
  } catch (e) {
    return { ok: false, error: e.name === 'AbortError' ? `no response within ${timeoutMs / 1000}s` : e.message };
  } finally {
    clearTimeout(timer);
  }
}

function waitForComplete(tabId, timeoutMs) {
  return new Promise((resolve) => {
    let done = false;
    const finish = () => {
      if (done) return;
      done = true;
      chrome.tabs.onUpdated.removeListener(onUpd);
      clearTimeout(timer);
      resolve();
    };
    const onUpd = (id, info) => { if (id === tabId && info.status === 'complete') finish(); };
    const timer = setTimeout(finish, timeoutMs);
    chrome.tabs.onUpdated.addListener(onUpd);
    chrome.tabs.get(tabId).then((t) => { if (t.status === 'complete') finish(); }).catch(finish);
  });
}

async function runExtractor(tabId) {
  // injectImmediately: don't wait for the page to go idle, which a page that
  // keeps loading forever never does.
  const [{ result } = {}] = await chrome.scripting.executeScript({ target: { tabId }, func: pageExtractor, injectImmediately: true });
  return result;
}

// Real Chrome, with your cookies and a real rendering engine: gets past most
// bot walls (Medium, Substack, Cloudflare) that block a plain fetch. Bounded by
// timeoutMs from start to finish; the window is always closed afterwards.
async function extractViaTab(url, timeoutMs) {
  let win = null;
  let tabId = null;
  try {
    win = await chrome.windows.create({ url, state: 'minimized', focused: false });
    tabId = win.tabs?.[0]?.id;
  } catch {
    const tab = await chrome.tabs.create({ url, active: false });
    tabId = tab.id;
  }
  const work = (async () => {
    await waitForComplete(tabId, Math.max(3000, timeoutMs - 8000));
    await sleep(1500); // let client-rendered pages settle
    let result = await runExtractor(tabId);
    if (result?.blocked) {
      // Cloudflare's JS challenge usually clears itself in a few seconds in a real browser.
      await sleep(5000);
      result = await runExtractor(tabId);
    }
    return result || { error: 'no result' };
  })();
  work.catch(() => {}); // after a timeout, its later failure (window closed) is expected
  try {
    return await withTimeout(work, timeoutMs, `page didn't finish loading within ${timeoutMs / 1000}s`);
  } finally {
    if (win) await chrome.windows.remove(win.id).catch(() => {});
    else if (tabId) await chrome.tabs.remove(tabId).catch(() => {});
  }
}

async function extractContent(url, s) {
  if (!/^https?:/i.test(url)) return { source: 'none', note: 'not a web page' };
  const timeoutMs = Math.min(120, Math.max(5, Number(s.pageTimeoutSeconds) || DEFAULTS.pageTimeoutSeconds)) * 1000;
  const f = await fetchPage(url, timeoutMs);

  // A PDF, image or download: a window would only download it again, so go by the URL and type.
  if (f.ok && f.isHtml === false) {
    return { ...f.content, source: 'fetch', note: `not a web page (${f.content.contentType})` };
  }
  // A dead link: there's nothing for a window to read.
  if (f.status === 404 || f.status === 410) return { source: 'unavailable', note: `dead link (HTTP ${f.status})` };

  const fetched = f.ok && !f.blocked ? f.content : null;
  if (fetched && isGoodEnough(fetched)) return { ...fetched, source: 'fetch' };

  if (s.useTabFallback) {
    try {
      const t = await extractViaTab(url, timeoutMs);
      if (t && !t.error && !t.blocked) {
        return { ...mergeContent(fetched || {}, t), source: fetched ? 'fetch+tab' : 'tab' };
      }
    } catch (e) {
      await log({ level: 'warn', msg: `Couldn't read the page in a window (${e.message}); going by what's available`, url });
    }
  }
  if (fetched) return { ...fetched, source: 'fetch (thin)' };
  return { source: 'unavailable', note: f.error || (f.blocked ? `blocked (HTTP ${f.status})` : `HTTP ${f.status}`) };
}

// ---------- the sweep ----------

export async function sweep(reason = 'manual') {
  if (sweeping) return { skipped: 'already running' };
  const { lock } = await chrome.storage.session.get('lock');
  if (lock && Date.now() - lock < LOCK_STALE_MS) return { skipped: 'locked' };
  sweeping = true;
  await chrome.storage.session.set({ lock: Date.now() });
  try {
    return await doSweep(reason);
  } catch (e) {
    await setStatus({ lastRun: Date.now(), lastError: e.message });
    await log({ level: 'error', msg: `Sweep failed: ${e.message}` });
    return { error: e.message };
  } finally {
    sweeping = false;
    await chrome.storage.session.remove('lock');
    await updateBadge();
  }
}

async function doSweep(reason) {
  const ctx = await getContext({ create: true });
  const { s } = ctx;
  if (ctx.error) {
    await setStatus({ lastRun: Date.now(), lastError: ctx.error });
    return { error: ctx.error };
  }
  const items = (await chrome.bookmarks.getChildren(ctx.inbox.id)).filter((n) => n.url);
  if (!items.length) {
    await setStatus({ lastRun: Date.now(), lastResult: 'Inbox empty', lastError: ctx.warning || null });
    return { processed: 0 };
  }

  const urlIndex = indexUrls(ctx.root, ctx.folders);
  const store = await getStore(['attempts', 'examples']);
  const attempts = store.attempts || {};
  const examples = (store.examples || []).slice(0, MAX_EXAMPLES);

  const host = new HostClient(HOST_NAME);
  host.connect();
  const counts = { filed: 0, review: 0, failed: 0 };
  try {
    for (const item of items.slice(0, s.maxPerSweep)) {
      try {
        const dupPath = urlIndex.get(normalizeUrl(item.url));
        if (dupPath !== undefined) {
          await park(item, ctx, { suggestedPath: dupPath, confidence: 'high', reason: `Already bookmarked in ${dupPath}` });
          counts.review++;
          continue;
        }
        const content = await extractContent(item.url, s);
        const job = {
          bookmark: { title: item.title, url: item.url },
          content,
          rootName: ctx.root.title,
          folders: ctx.folders.map((f) => ({ path: f.path, count: f.count, samples: f.samples })),
          examples,
          model: s.model,
        };
        const resp = await host.request('categorize', { job, folderNames: folderNames(s) });
        if (!resp.ok) throw new Error(resp.error || 'Claude Code returned an error');
        const { outcome, path } = await applyDecision(item, resp.decision, content, ctx);
        counts[outcome]++;
        urlIndex.set(normalizeUrl(item.url), path); // a second copy later in this run is a duplicate
        delete attempts[item.id];
      } catch (e) {
        attempts[item.id] = (attempts[item.id] || 0) + 1;
        counts.failed++;
        await log({ level: 'error', msg: `Attempt ${attempts[item.id]}/${s.maxAttempts} failed: ${e.message}`, title: item.title, url: item.url });
        if (/Native host (not installed|refused|crashed)/.test(e.message)) {
          await setStatus({ lastRun: Date.now(), lastError: e.message });
          return { error: e.message };
        }
        if (attempts[item.id] >= s.maxAttempts) {
          await park(item, ctx, { suggestedPath: '', confidence: 'low', reason: `Couldn't categorize after ${s.maxAttempts} tries: ${e.message}` });
          urlIndex.set(normalizeUrl(item.url), ctx.review.title);
          delete attempts[item.id];
        }
      }
    }
  } finally {
    host.disconnect();
    await setStore({ attempts });
  }

  if (items.length > s.maxPerSweep) scheduleSoon();
  const summary = `Filed ${counts.filed}, sent ${counts.review} to review, ${counts.failed} failed (${reason})`;
  await setStatus({ lastRun: Date.now(), lastResult: summary, lastError: counts.failed ? 'Some items failed; see activity log' : ctx.warning || null });
  return { processed: counts.filed + counts.review, ...counts };
}

async function applyDecision(item, d, content, ctx) {
  const { s } = ctx;
  const target = resolveFolder(ctx.folders, d.folder_path);
  const confident = CONFIDENCE_RANK[d.confidence] >= CONFIDENCE_RANK[s.minConfidence];

  if (target && confident && d.is_career_relevant !== false) {
    await moveTo(item.id, target.id);
    const cleaned = (d.clean_title || '').trim();
    if (s.cleanTitles && cleaned && cleaned !== item.title) {
      await chrome.bookmarks.update(item.id, { title: cleaned });
    }
    const { filed = {} } = await getStore('filed');
    filed[item.id] = { path: target.path, at: Date.now() };
    await setStore({ filed: trimMap(filed, 500) });
    await log({ msg: `Filed in ${target.path} (${d.confidence})`, title: item.title, url: item.url, path: target.path, reason: d.reason, source: content.source });
    return { outcome: 'filed', path: target.path };
  }

  let why = d.reason || '';
  if (!target) why = `Suggested "${d.folder_path}", which isn't an existing folder. ${why}`;
  else if (d.is_career_relevant === false) why = `May not be career-related. ${why}`;
  if (d.new_folder_suggestion) why += ` Possible new folder: ${d.new_folder_suggestion}.`;
  await park(item, ctx, { suggestedPath: target ? target.path : d.folder_path, confidence: d.confidence, reason: why.trim(), source: content.source });
  return { outcome: 'review', path: ctx.review.title };
}

async function park(item, ctx, info) {
  await moveTo(item.id, ctx.review.id);
  const { review = {} } = await getStore('review');
  review[item.id] = { ...info, at: Date.now() };
  await setStore({ review: trimMap(review, 500) });
  await log({ level: 'review', msg: `Sent to review: ${info.reason}`, title: item.title, url: item.url, path: info.suggestedPath });
}

function trimMap(obj, max) {
  const entries = Object.entries(obj);
  if (entries.length <= max) return obj;
  entries.sort((a, b) => (b[1].at || 0) - (a[1].at || 0));
  return Object.fromEntries(entries.slice(0, max));
}

// ---------- learning from Bert's own moves ----------

// When Bert moves something we filed, or files something out of _review, that
// choice becomes an authoritative example in future prompts.
async function trackUserMove(id, info, ctx) {
  if (!ctx.root) return;
  const { filed = {}, review = {} } = await getStore(['filed', 'review']);
  const fromFiled = filed[id];
  const fromReview = review[id];
  if (!fromFiled && !fromReview) return;
  const dest = ctx.folders.find((f) => f.id === info.parentId);
  delete filed[id];
  delete review[id];
  await setStore({ filed, review });
  if (!dest) return; // moved back to inbox or out of the root folder

  const [node] = await chrome.bookmarks.get(id);
  const prior = fromFiled ? fromFiled.path : fromReview.suggestedPath;
  if (fromFiled && prior === dest.path) return;
  await addExample({
    title: truncate(node.title, 120),
    url: node.url,
    path: dest.path,
    note: fromFiled ? `corrected from ${prior}` : prior === dest.path ? 'confirmed suggestion' : `suggested ${prior || 'nothing'}`,
  });
}

async function addExample(ex) {
  const { examples = [] } = await getStore('examples');
  const next = [{ ...ex, at: Date.now() }, ...examples.filter((e) => e.url !== ex.url)].slice(0, MAX_EXAMPLES);
  await setStore({ examples: next });
}

// ---------- badge ----------

async function updateBadge() {
  try {
    const ctx = await getContext({ create: false });
    const n = ctx.review ? (await chrome.bookmarks.getChildren(ctx.review.id)).filter((x) => x.url).length : 0;
    await chrome.action.setBadgeBackgroundColor({ color: '#b45309' });
    await chrome.action.setBadgeText({ text: n ? String(n) : '' });
  } catch { /* badge is cosmetic */ }
}

// ---------- messages from the options page ----------

const OPTIONS_URL = chrome.runtime.getURL('options.html');

// Only this extension's own options page may send commands.
function fromOptionsPage(sender) {
  return sender?.id === chrome.runtime.id && String(sender.url || '').startsWith(OPTIONS_URL);
}

chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  if (!fromOptionsPage(sender)) return false;
  handle(msg).then(reply, (e) => reply({ error: e.message }));
  return true;
});

// Review actions only apply to bookmarks that are actually in the review folder.
async function reviewBookmark(ctx, id) {
  const [node] = await chrome.bookmarks.get(String(id)).catch(() => []);
  if (!node || !ctx.review || node.parentId !== ctx.review.id) {
    throw new Error('That bookmark is no longer in the review folder.');
  }
  return node;
}

async function handle(msg) {
  switch (msg.cmd) {
    case 'sweep':
      return sweep('manual');
    case 'saveSettings':
      return saveSettings(msg.settings || {});
    case 'ping': {
      const host = new HostClient(HOST_NAME);
      host.connect();
      const s = await getSettings();
      try { return await host.request('ping', { folderNames: folderNames(s) }, 60000); } finally { host.disconnect(); }
    }
    case 'overview': {
      const ctx = await getContext({ create: false });
      const store = await getStore(['review', 'status', 'log', 'examples']);
      const reviewItems = ctx.review
        ? (await chrome.bookmarks.getChildren(ctx.review.id)).filter((n) => n.url).map((n) => ({
            id: n.id, title: n.title, url: n.url, ...(store.review?.[n.id] || {}),
          }))
        : [];
      const inboxCount = ctx.inbox ? (await chrome.bookmarks.getChildren(ctx.inbox.id)).filter((n) => n.url).length : 0;
      return {
        error: ctx.error,
        warning: ctx.warning,
        rootName: ctx.root?.title,
        folders: (ctx.folders || []).map((f) => ({ id: f.id, path: f.path, count: f.count })),
        treeMarkdown: ctx.root ? treeToMarkdown(ctx.root.title, ctx.folders) : '',
        reviewItems,
        inboxCount,
        status: store.status || {},
        log: store.log || [],
        examples: store.examples || [],
      };
    }
    case 'fileFromReview': {
      const ctx = await getContext({ create: false });
      await reviewBookmark(ctx, msg.id);
      const dest = ctx.folders.find((f) => f.id === msg.folderId);
      if (!dest) throw new Error('Folder not found');
      const { review = {} } = await getStore('review');
      const rec = review[msg.id] || {};
      await moveTo(msg.id, dest.id);
      delete review[msg.id];
      await setStore({ review });
      const [node] = await chrome.bookmarks.get(msg.id);
      await addExample({
        title: truncate(node.title, 120), url: node.url, path: dest.path,
        note: rec.suggestedPath === dest.path ? 'confirmed suggestion' : `suggested ${rec.suggestedPath || 'nothing'}`,
      });
      await log({ msg: `Filed from review into ${dest.path}`, title: node.title, url: node.url, path: dest.path });
      await updateBadge();
      return { ok: true };
    }
    case 'retry': {
      const ctx = await getContext({ create: true });
      await reviewBookmark(ctx, msg.id);
      const { review = {} } = await getStore('review');
      delete review[msg.id];
      await setStore({ review });
      await moveTo(msg.id, ctx.inbox.id);
      scheduleSoon();
      await updateBadge();
      return { ok: true };
    }
    case 'clearExamples':
      await setStore({ examples: [] });
      return { ok: true };
    case 'clearLog':
      await setStore({ log: [] });
      return { ok: true };
    default:
      throw new Error(`Unknown command ${msg.cmd}`);
  }
}
