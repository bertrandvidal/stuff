// Minimal in-memory Chrome for exercising background.js.
const ev = () => { const ls = []; return { addListener: (f) => ls.push(f), removeListener: (f) => { const i = ls.indexOf(f); if (i >= 0) ls.splice(i, 1); }, fire: (...a) => Promise.all(ls.map((f) => f(...a))), ls }; };
export function makeChrome({ decide }) {
  const nodes = new Map(); let seq = 100;
  const add = (n) => { nodes.set(n.id, { children: n.url ? undefined : [], dateAdded: Date.now(), ...n }); if (n.parentId) nodes.get(n.parentId).children.push(n.id); return nodes.get(n.id); };
  const view = (id) => { const n = nodes.get(id); const v = { ...n }; if (n.children) v.children = n.children.map(view); else delete v.children; return v; };
  const flat = (id) => { const n = nodes.get(id); const v = { ...n }; delete v.children; return v; };
  const store = (data = {}) => ({ data,
    async get(k) { const keys = k == null ? Object.keys(data) : Array.isArray(k) ? k : [k]; const o = {}; for (const key of keys) if (key in data) o[key] = structuredClone(data[key]); return o; },
    async set(o) { Object.assign(data, structuredClone(o)); }, async remove(k) { for (const key of [].concat(k)) delete data[key]; } });
  const bm = { onCreated: ev(), onMoved: ev(), onRemoved: ev(),
    async getTree() { return [view('0')]; },
    async getChildren(id) { return nodes.get(id).children.map(flat); },
    async get(id) { return [flat(id)]; },
    async create({ parentId, title, url, index }) { const n = add({ id: String(++seq), parentId, title, url }); if (index !== undefined) { const ch = nodes.get(parentId).children; ch.splice(ch.indexOf(n.id), 1); ch.splice(index, 0, n.id); } setTimeout(() => bm.onCreated.fire(n.id, flat(n.id))); return flat(n.id); },
    async move(id, { parentId }) { const n = nodes.get(id); const old = n.parentId; const ch = nodes.get(old).children; ch.splice(ch.indexOf(id), 1); nodes.get(parentId).children.push(id); n.parentId = parentId; setTimeout(() => bm.onMoved.fire(id, { parentId, oldParentId: old })); return flat(id); },
    async update(id, ch) { Object.assign(nodes.get(id), ch); return flat(id); } };
  const calls = { alarms: [], badge: [], windows: 0, jobs: [] };
  const portFactory = () => { const onMessage = ev(), onDisconnect = ev(); return { onMessage, onDisconnect,
    postMessage(m) { setTimeout(async () => { calls.lastFolderNames = m.folderNames; if (m.type === 'categorize') calls.jobs.push(m.job); const r = m.type === 'ping' ? { ok: true, auth_ok: true } : await decide(m.job);
      // decide() can simulate the bridge going away, the way Chrome reports it.
      if (r.disconnect) { chrome.runtime.lastError = { message: r.disconnect }; await onDisconnect.fire(); chrome.runtime.lastError = null; return; }
      onMessage.fire({ id: m.id, ...r }); }, 5); },
    disconnect() {} }; };
  const chrome = {
    bookmarks: bm,
    storage: { local: store(), session: store() },
    alarms: { onAlarm: ev(), async create(name, info) { calls.alarms.push(name); } },
    runtime: { id: 'testext', getURL: (p) => `chrome-extension://testext/${p}`, onInstalled: ev(), onStartup: ev(), onMessage: ev(), lastError: null, openOptionsPage() {}, connectNative: portFactory },
    action: { onClicked: ev(), async setBadgeText({ text }) { calls.badge.push(text); }, async setBadgeBackgroundColor() {} },
    tabs: { onUpdated: ev(), async get(id) { return { id, status: /hang/.test(calls.lastTabUrl) ? 'loading' : 'complete' }; }, async create() { return { id: 9 }; }, async remove() {} },
    windows: { async create({ url }) { calls.windows++; calls.lastTabUrl = url; return { id: 1, tabs: [{ id: 7 }] }; }, async remove() { calls.windowsClosed = (calls.windowsClosed || 0) + 1; } },
    scripting: { async executeScript() { if (/hang/.test(calls.lastTabUrl)) return new Promise(() => {}); return [{ result: { title: 'How to run skip-level 1:1s', description: 'A practical guide for managers of managers to running skip-level one-on-ones well.', textSample: 'Skip-levels...', blocked: false, finalUrl: /tabredirect/.test(calls.lastTabUrl) ? 'http://10.0.0.1/admin' : calls.lastTabUrl } }]; } },
  };
  return { chrome, nodes, add, calls, OPTIONS_SENDER: { id: 'testext', url: 'chrome-extension://testext/options.html' },
    send: (msg, sender = { id: 'testext', url: 'chrome-extension://testext/options.html' }) => new Promise((res) => chrome.runtime.onMessage.ls[0](msg, sender, res)) };
}
