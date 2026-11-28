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
      const leaf = !(c.children || []).some((x) => !x.url);
      const depth = path.split('/').length;
      out.push({ id: c.id, path, title: c.title, count: links.length, samples: sampleTitles, leaf, depth });
      walk(c, path);
    }
  };
  walk(root, '');
  return out;
}

// Links are only ever filed into a leaf folder (no subfolders) below the top
// level, e.g. engineering/architecture, never engineering itself.
export const isFilingTarget = (f) => f.leaf && f.depth >= 2;

// Query parameters that only track where a click came from, removed before
// comparing URLs. Only names that mean tracking on every site are global:
// short generic names such as `s` (WordPress search), `ref` (a git branch on
// GitHub and GitLab) or `source` are real parameters on some sites, and
// stripping them made different pages look like duplicates. Those are
// stripped only on the sites where they are known to be tracking.
const TRACKING_PARAMS = /^(utm_\w+|fbclid|gclid|dclid|gbraid|wbraid|msclkid|yclid|mc_cid|mc_eid|ref_src|igshid|_hsenc|_hsmi|mkt_tok)$/i;
const SITE_TRACKING_PARAMS = [
  [/(^|\.)medium\.com$/, /^(source|sk)$/i],
  [/(^|\.)(youtube\.com|youtu\.be|spotify\.com)$/, /^si$/i],
  [/^(x|twitter)\.com$/, /^(s|t)$/i],
];

// A comparable form of a URL, for duplicate detection: no scheme, no "www.",
// no tracking parameters, no trailing slash. The port is kept (different
// ports are different sites), and so is a hash that is an app route (#/ or
// #!), since single-page apps put the page in it; other hashes only point
// within a page.
export function normalizeUrl(u) {
  try {
    const url = new URL(u);
    if (!/^#[/!]/.test(url.hash)) url.hash = '';
    const host = url.host.toLowerCase().replace(/^www\./, '');
    const siteParams = SITE_TRACKING_PARAMS.filter(([site]) => site.test(url.hostname.toLowerCase().replace(/^www\./, ''))).map(([, p]) => p);
    for (const k of [...url.searchParams.keys()]) {
      if (TRACKING_PARAMS.test(k) || siteParams.some((p) => p.test(k))) url.searchParams.delete(k);
    }
    const path = url.pathname.replace(/\/+$/, '') || '/';
    const search = url.searchParams.toString();
    return `${host}${path}${search ? '?' + search : ''}${url.hash}`;
  } catch {
    return String(u || '').trim();
  }
}

// Map of normalized URL -> where it already is, for every bookmark under the
// root except the inbox: the given folders, links sitting directly in the
// root (labelled with the root's name), and `extra` folders such as the
// review folder (labelled with their title). Missing the review folder let a
// link re-saved while its first copy waited for review be filed again.
export function indexUrls(root, folders, extra = []) {
  const pathById = new Map(folders.map((f) => [f.id, f.path]));
  const realFolder = new Set(pathById.keys()); // a real folder wins over root or review
  for (const f of extra) if (f) pathById.set(f.id, f.title);
  pathById.set(root.id, root.title);
  const idx = new Map();
  const walk = (node) => {
    for (const c of node.children || []) {
      if (c.url) {
        const key = normalizeUrl(c.url);
        if (!idx.has(key) || realFolder.has(node.id)) idx.set(key, pathById.get(node.id));
      } else if (pathById.has(c.id)) {
        walk(c);
      }
    }
  };
  walk(root);
  return idx;
}

// True when `clean` is `saved`, or `saved` with parts removed (a site name,
// an author), which is all title cleanup should ever do.
export function isTrimmedTitle(clean, saved) {
  const norm = (x) => String(x || '').normalize('NFKC').replace(/\s+/g, ' ').trim();
  const c = norm(clean);
  return !!c && norm(saved).includes(c);
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
    // One folder, never a path: a slash would read as a subfolder in folder paths.
    if (String(s[k] || '').includes('/')) out.push(`${label} name can't contain "/". It names a single folder, not a path.`);
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
