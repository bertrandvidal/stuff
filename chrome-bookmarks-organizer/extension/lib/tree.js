// Pure helpers for working with chrome.bookmarks trees. No chrome.* calls here.

export function normalizeName(s) {
  return String(s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
}

export function truncate(s, n) {
  s = String(s || '').replace(/\s+/g, ' ').trim();
  return s.length > n ? s.slice(0, n - 1) + '…' : s;
}

// Chrome can now hold two copies of each top-level folder (synced account
// storage and local storage). Prefer a match that syncs, since that is the
// copy the phone writes to.
export function findRootFolder(tree, name) {
  const want = normalizeName(name);
  const hits = [];
  const walk = (node, ancestors) => {
    if (!node.url && node.title && normalizeName(node.title) === want) {
      hits.push({ node, ancestors });
    }
    for (const c of node.children || []) {
      if (!c.url) walk(c, ancestors.concat(node));
    }
  };
  for (const n of tree) walk(n, []);
  if (!hits.length) return { node: null, warning: null };

  const syncState = (h) => {
    if (typeof h.node.syncing === 'boolean') return h.node.syncing;
    for (let i = h.ancestors.length - 1; i >= 0; i--) {
      if (typeof h.ancestors[i].syncing === 'boolean') return h.ancestors[i].syncing;
    }
    return undefined;
  };
  const score = (h) => {
    const s = syncState(h);
    return (s === true ? 200 : s === undefined ? 100 : 0) - h.ancestors.length;
  };
  hits.sort((a, b) => score(b) - score(a));
  const warning = hits.length > 1
    ? `Found ${hits.length} folders named "${name}". Using the one that syncs to your phone.`
    : null;
  return { node: hits[0].node, warning };
}

export function findChildFolder(node, name) {
  const want = normalizeName(name);
  return (node.children || []).find((c) => !c.url && normalizeName(c.title) === want) || null;
}

// Every folder under root (except the top-level system folders like _inbox and
// _review), with its path and a few recent titles as examples.
export function collectFolders(root, { exclude = [], samples = 6 } = {}) {
  const ex = new Set(exclude.map(normalizeName));
  const out = [];
  const walk = (node, prefix) => {
    for (const c of node.children || []) {
      if (c.url) continue;
      if (prefix === '' && ex.has(normalizeName(c.title))) continue;
      const path = prefix ? `${prefix}/${c.title}` : c.title;
      const links = (c.children || []).filter((x) => x.url);
      const sampleTitles = links
        .slice()
        .sort((a, b) => (b.dateAdded || 0) - (a.dateAdded || 0))
        .slice(0, samples)
        .map((x) => truncate(x.title || x.url, 100));
      out.push({ id: c.id, path, title: c.title, count: links.length, samples: sampleTitles });
      walk(c, path);
    }
  };
  walk(root, '');
  return out;
}

const TRACKING_PARAMS = /^(utm_\w+|fbclid|gclid|mc_cid|mc_eid|ref|ref_src|source|sk|s|si)$/i;

export function normalizeUrl(u) {
  try {
    const url = new URL(u);
    url.hash = '';
    url.hostname = url.hostname.toLowerCase().replace(/^www\./, '');
    for (const k of [...url.searchParams.keys()]) {
      if (TRACKING_PARAMS.test(k)) url.searchParams.delete(k);
    }
    let path = url.pathname.replace(/\/+$/, '') || '/';
    const search = url.searchParams.toString();
    return `${url.hostname}${path}${search ? '?' + search : ''}`;
  } catch {
    return String(u || '').trim();
  }
}

// Map of normalized URL -> folder path, for every bookmark in the given folders.
export function indexUrls(root, folders) {
  const pathById = new Map(folders.map((f) => [f.id, f.path]));
  const idx = new Map();
  const walk = (node) => {
    for (const c of node.children || []) {
      if (c.url) {
        const p = pathById.get(node.id);
        if (p !== undefined) idx.set(normalizeUrl(c.url), p);
      } else if (pathById.has(c.id)) {
        walk(c);
      }
    }
  };
  walk(root);
  return idx;
}

export function cleanPath(p) {
  return String(p || '').trim().replace(/^\/+|\/+$/g, '').replace(/\s*\/\s*/g, '/');
}

// Resolve Claude's answer to a folder, tolerating case and spacing differences.
export function resolveFolder(folders, path) {
  const want = cleanPath(path);
  if (!want) return null;
  const exact = folders.find((f) => f.path === want);
  if (exact) return exact;
  const norm = (p) => p.split('/').map(normalizeName).join('/');
  const n = norm(want);
  return folders.find((f) => norm(f.path) === n) || null;
}

const NAME_FIELDS = [
  ['rootFolderName', 'Root folder'],
  ['inboxName', 'Inbox folder'],
  ['reviewName', 'Review folder'],
];

// Problems with a set of folder names, as user-facing sentences.
export function folderNameProblems(s) {
  const out = [];
  for (const [k, label] of NAME_FIELDS) {
    if (!normalizeName(s[k])) out.push(`${label} name needs at least one letter or number.`);
  }
  const inbox = normalizeName(s.inboxName);
  if (inbox && inbox === normalizeName(s.reviewName)) out.push('Inbox and review folders need different names.');
  return out;
}

// When the inbox or review name changes, rename the existing folder instead of
// leaving it behind. Refuses if another folder already has the new name.
export function planFolderRenames(root, prev, next) {
  const renames = [];
  const errors = [];
  for (const [key, label] of [['inboxName', 'inbox'], ['reviewName', 'review']]) {
    const from = prev[key];
    const to = String(next[key]).trim();
    if (from === to) continue;
    const existing = findChildFolder(root, from);
    const clash = findChildFolder(root, to);
    if (clash && (!existing || clash.id !== existing.id)) {
      errors.push(`"${root.title}" already has a folder named "${clash.title}". Pick another ${label} name, or rename that folder first.`);
      continue;
    }
    if (existing && existing.title !== to) renames.push({ id: existing.id, from: existing.title, title: to });
  }
  return { renames, errors };
}

// Markdown outline of the folder tree, for pasting into the Claude skill.
export function treeToMarkdown(rootName, folders) {
  const lines = [`${rootName}/`];
  for (const f of folders) {
    const depth = f.path.split('/').length;
    lines.push(`${'  '.repeat(depth)}- ${f.title}  (${f.count})`);
  }
  return lines.join('\n');
}
