// Page content extraction. parseHtmlMeta runs in the service worker on fetched
// HTML (no DOM there). pageExtractor runs inside a real tab via
// chrome.scripting and must stay self-contained.
//
// parseHtmlMeta must stay fast on any input: it runs synchronously, so a slow
// parse would freeze the worker and no timeout could interrupt it. Everything
// below is a single forward scan (indexOf, or regexes that can't backtrack
// across '<'), so cost grows linearly with page size.

export const MAX_HTML = 300_000; // plenty for the head and the opening of any article

const ENTITY = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', '#39': "'" };

export function decodeEntities(s) {
  return String(s || '').replace(/&(#x[0-9a-f]{1,6}|#\d{1,7}|[a-z0-9]{1,10});/gi, (m, e) => {
    if (e[0] === '#') {
      const code = e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      // Not a character: past U+10FFFF (String.fromCodePoint throws, and that
      // threw away a page that had fetched fine), a lone surrogate half (the
      // host could not encode it for Claude Code), or NUL. Use U+FFFD, the
      // standard replacement character, as browsers do.
      if (!(code > 0 && code <= 0x10ffff) || (code >= 0xd800 && code <= 0xdfff)) return '\ufffd';
      return String.fromCodePoint(code);
    }
    return ENTITY[e.toLowerCase()] ?? m;
  });
}

const squash = (s) => decodeEntities(s).replace(/\s+/g, ' ').trim();

// Replace unpaired surrogate halves with U+FFFD. Cutting text at a fixed
// length can split an emoji in two, and the half left over can't be encoded
// as UTF-8 on the Mac side, which failed the whole request.
export function wellFormed(s) {
  s = String(s ?? '');
  return typeof s.toWellFormed === 'function' ? s.toWellFormed()
    : s.replace(/[\ud800-\udbff](?![\udc00-\udfff])|(?<![\ud800-\udbff])[\udc00-\udfff]/g, '\ufffd');
}

// The same, for every string inside a job sent to the Mac.
export function wellFormedDeep(v) {
  if (typeof v === 'string') return wellFormed(v);
  if (Array.isArray(v)) return v.map(wellFormedDeep);
  if (v && typeof v === 'object') return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, wellFormedDeep(x)]));
  return v;
}

// Attributes of one tag, e.g. <meta property="og:title" content="...">.
//
// The lookbehind (?<![a-zA-Z_:.-]) is what keeps this linear. Without it, a
// tag holding a long run of name characters and no "=" (for example
// `<meta aaaa…>`, 300 KB of "a") made the engine try a match from every
// position inside the run: each try reads to the end of the run, finds no
// "=", and gives up, so the cost grew with the square of the run's length
// (40 KB took 1.4 s, 300 KB about 75 s). This runs synchronously in the
// service worker, so no timeout could stop it, and the link froze every sweep.
// With the lookbehind, a name can only start where the previous character
// isn't a name character, so each run is scanned once.
const ATTR_RE = /(?<![a-zA-Z_:.-])([a-zA-Z_:.-]+)\s*=\s*("([^"]*)"|'([^']*)'|([^\s"'>]+))/g;

function parseAttrs(tag) {
  const attrs = {};
  const re = new RegExp(ATTR_RE); // fresh lastIndex for each tag
  let m;
  while ((m = re.exec(tag))) attrs[m[1].toLowerCase()] = m[3] ?? m[4] ?? m[5] ?? '';
  return attrs;
}

const isTagEnd = (ch) => ch === undefined || ch === '>' || ch === '/' || /\s/.test(ch);

// <tag ...>inner</tag> blocks, found by a forward scan. An unclosed tag ends
// the scan instead of being retried at every later position.
function blocks(html, lower, tag, limit = Infinity) {
  const out = [];
  const open = `<${tag}`;
  const close = `</${tag}`;
  let i = 0;
  while (out.length < limit) {
    const s = lower.indexOf(open, i);
    if (s < 0) break;
    if (!isTagEnd(lower[s + open.length])) { i = s + open.length; continue; }
    const gt = lower.indexOf('>', s);
    if (gt < 0) break;
    const e = lower.indexOf(close, gt);
    if (e < 0) break;
    out.push({ at: s, open: html.slice(s, gt + 1), inner: html.slice(gt + 1, e) });
    i = e + close.length;
  }
  return out;
}

const NOISE_TAGS = ['script', 'style', 'noscript', 'svg', 'nav', 'header', 'footer', 'form', 'aside'];

// Drop noise blocks entirely; an unclosed one drops the rest of the page.
function removeBlocks(html, tags) {
  for (const tag of tags) {
    const lower = html.toLowerCase();
    const open = `<${tag}`;
    const close = `</${tag}`;
    let out = '';
    let i = 0;
    for (;;) {
      const s = lower.indexOf(open, i);
      if (s < 0) { out += html.slice(i); break; }
      if (!isTagEnd(lower[s + open.length])) { out += html.slice(i, s + open.length); i = s + open.length; continue; }
      out += html.slice(i, s) + ' ';
      const e = lower.indexOf(close, s);
      if (e < 0) break;
      const gt = lower.indexOf('>', e);
      if (gt < 0) break;
      i = gt + 1;
    }
    html = out;
  }
  return html;
}

function stripToText(html) {
  return squash(
    removeBlocks(html, NOISE_TAGS)
      .replace(/<br\s*\/?>|<\/(p|div|h[1-6]|li|section)>/gi, ' ')
      .replace(/<[^<>]*>/g, ' ') // [^<>] stops at the next '<', so stray '<' can't cause rescans
  );
}

export function parseHtmlMeta(html) {
  html = String(html || '').slice(0, MAX_HTML);
  const lower = html.toLowerCase();
  const metas = {};
  const tags = [];
  for (const m of html.matchAll(/<meta\b[^<>]*>/gi)) {
    const a = parseAttrs(m[0]);
    const key = (a.property || a.name || a.itemprop || '').toLowerCase();
    if (key && a.content !== undefined) {
      if (key === 'article:tag') tags.push(squash(a.content));
      else if (!(key in metas)) metas[key] = squash(a.content);
    }
  }
  const titleTag = squash(blocks(html, lower, 'title', 1)[0]?.inner || '');

  let ld = {};
  for (const b of blocks(html, lower, 'script')) {
    if (!/application\/ld\+json/i.test(b.open)) continue;
    try {
      const j = JSON.parse(b.inner);
      const arr = Array.isArray(j) ? j : j['@graph'] || [j];
      const art = arr.find((x) => x && /Article|Posting|BlogPosting|WebPage/i.test(String(x['@type'])));
      if (art) { ld = art; break; }
    } catch { /* ignore bad JSON-LD */ }
  }
  const ldKeywords = Array.isArray(ld.keywords) ? ld.keywords.join(', ') : ld.keywords || '';

  const headings = [...blocks(html, lower, 'h1', 12), ...blocks(html, lower, 'h2', 12)]
    .sort((a, b) => a.at - b.at)
    .map((b) => stripToText(b.inner))
    .filter(Boolean)
    .slice(0, 12);

  const bodyStart = lower.indexOf('<body');
  const bodyEnd = lower.lastIndexOf('</body');
  const body =
    blocks(html, lower, 'article', 1)[0]?.inner ??
    blocks(html, lower, 'main', 1)[0]?.inner ??
    (bodyStart >= 0 ? html.slice(bodyStart, bodyEnd > bodyStart ? bodyEnd : undefined) : html);
  const textSample = stripToText(body).slice(0, 4000);

  return {
    title: metas['og:title'] || metas['twitter:title'] || squash(ld.headline || '') || titleTag,
    pageTitle: titleTag,
    description: metas['og:description'] || metas['description'] || metas['twitter:description'] || squash(ld.description || ''),
    siteName: metas['og:site_name'] || '',
    keywords: [metas['keywords'], ldKeywords, tags.join(', '), ld.articleSection].filter(Boolean).join(', ').slice(0, 400),
    author: metas['author'] || metas['article:author'] || (ld.author && (ld.author.name || ld.author[0]?.name)) || '',
    published: metas['article:published_time'] || ld.datePublished || '',
    headings,
    textSample,
  };
}

// Addresses on this Mac or its local network: localhost, private and
// link-local IP ranges, mDNS (.local) and other local-only names, and
// single-label names like "router". The extension can reach these (its host
// permissions bypass Chrome's local network protections), so a public page
// could redirect a read to a router or NAS admin page and its text would go
// to Claude. Pages at these addresses are never read. A public name that
// resolves to a private IP can't be seen from here; that case is not covered.
export function isPrivateHost(hostname) {
  let h = String(hostname || '').toLowerCase().replace(/\.$/, '');
  if (h.startsWith('[')) h = h.slice(1, -1);
  if (!h || !h.includes('.') && !h.includes(':')) return true; // "router", "nas", "localhost"
  if (/(^|\.)(localhost|local|internal|lan|home\.arpa)$/.test(h)) return true;
  const v4 = h.match(/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/);
  if (v4) return isPrivateV4(v4.slice(1).map(Number));
  if (h.includes(':')) {
    const mapped = h.match(/^::ffff:([0-9a-f]{1,4}):([0-9a-f]{1,4})$/); // URL writes ::ffff:127.0.0.1 this way
    if (mapped) {
      const [hi, lo] = mapped.slice(1).map((x) => parseInt(x, 16));
      return isPrivateV4([hi >> 8, hi & 255, lo >> 8, lo & 255]);
    }
    return h === '::' || h === '::1' || /^f[cd]/.test(h) || /^fe[89ab]/.test(h);
  }
  return false;
}

function isPrivateV4([a, b]) {
  return a === 0 || a === 10 || a === 127 || (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31)
    || (a === 192 && b === 168) || (a === 100 && b >= 64 && b <= 127);
}

export function isPrivateUrl(u) {
  try { return isPrivateHost(new URL(u).hostname); } catch { return false; }
}

export function looksBlocked(status, title, html) {
  if ([401, 403, 429, 503].includes(status)) return true;
  if (/just a moment|attention required|verify you are human|access denied|are you a robot|captcha/i.test(title || '')) return true;
  const head = String(html || '').slice(0, 50000);
  return /cf-chl-|challenge-platform|cf_chl_opt|px-captcha|_Incapsula_Resource/i.test(head);
}

export function isGoodEnough(c) {
  if (!c || !c.title) return false;
  return (c.description || '').length >= 60 || (c.textSample || '').length >= 600;
}

// Keep the richer value of each field from two extraction attempts.
export function mergeContent(a = {}, b = {}) {
  const out = { ...a };
  for (const [k, v] of Object.entries(b)) {
    const cur = out[k];
    const len = (x) => (Array.isArray(x) ? x.length : String(x ?? '').length);
    if (len(v) > len(cur)) out[k] = v;
  }
  return out;
}

// Runs inside the page (injected with chrome.scripting.executeScript).
export function pageExtractor() {
  const metas = {};
  const tags = [];
  for (const m of document.querySelectorAll('meta[content]')) {
    const k = (m.getAttribute('property') || m.getAttribute('name') || m.getAttribute('itemprop') || '').toLowerCase();
    if (!k) continue;
    if (k === 'article:tag') tags.push(m.getAttribute('content'));
    else if (!(k in metas)) metas[k] = m.getAttribute('content');
  }
  const root = document.querySelector('article') || document.querySelector('main') || document.body;
  const raw = (root && (root.innerText || root.textContent)) || '';
  const headings = [...document.querySelectorAll('h1, h2')]
    .map((e) => (e.innerText || e.textContent || '').trim())
    .filter(Boolean)
    .slice(0, 12);
  const blocked =
    /just a moment|attention required|verify you are human|access denied|are you a robot/i.test(document.title) ||
    !!document.querySelector('#challenge-form, #cf-challenge-running, [id^="cf-chl"], #px-captcha');
  return {
    title: metas['og:title'] || metas['twitter:title'] || document.title || '',
    pageTitle: document.title || '',
    description: metas['og:description'] || metas['description'] || metas['twitter:description'] || '',
    siteName: metas['og:site_name'] || '',
    keywords: [metas['keywords'], tags.join(', ')].filter(Boolean).join(', ').slice(0, 400),
    author: metas['author'] || metas['article:author'] || '',
    published: metas['article:published_time'] || '',
    headings,
    textSample: raw.replace(/\s+/g, ' ').trim().slice(0, 4000),
    finalUrl: location.href,
    blocked,
  };
}
