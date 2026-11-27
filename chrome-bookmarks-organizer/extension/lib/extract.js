// Page content extraction. parseHtmlMeta runs in the service worker on fetched
// HTML (no DOM there, so it uses regexes). pageExtractor runs inside a real tab
// via chrome.scripting and must stay self-contained.

const ENTITY = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', '#39': "'" };

export function decodeEntities(s) {
  return String(s || '').replace(/&(#x[0-9a-f]+|#\d+|[a-z0-9]+);/gi, (m, e) => {
    if (e[0] === '#') {
      const code = e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      return Number.isFinite(code) ? String.fromCodePoint(code) : m;
    }
    return ENTITY[e.toLowerCase()] ?? m;
  });
}

const squash = (s) => decodeEntities(s).replace(/\s+/g, ' ').trim();

function parseAttrs(tag) {
  const attrs = {};
  const re = /([a-zA-Z_:.-]+)\s*=\s*("([^"]*)"|'([^']*)'|([^\s"'>]+))/g;
  let m;
  while ((m = re.exec(tag))) attrs[m[1].toLowerCase()] = m[3] ?? m[4] ?? m[5] ?? '';
  return attrs;
}

function stripToText(html) {
  return squash(
    html
      .replace(/<(script|style|noscript|svg|nav|header|footer|form|aside)\b[\s\S]*?<\/\1>/gi, ' ')
      .replace(/<br\s*\/?>|<\/(p|div|h[1-6]|li|section)>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
  );
}

export function parseHtmlMeta(html) {
  html = String(html || '');
  const metas = {};
  const tags = [];
  for (const m of html.matchAll(/<meta\b[^>]*>/gi)) {
    const a = parseAttrs(m[0]);
    const key = (a.property || a.name || a.itemprop || '').toLowerCase();
    if (key && a.content !== undefined) {
      if (key === 'article:tag') tags.push(squash(a.content));
      else if (!(key in metas)) metas[key] = squash(a.content);
    }
  }
  const titleTag = squash((html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i) || [])[1] || '');

  let ld = {};
  for (const m of html.matchAll(/<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)) {
    try {
      const j = JSON.parse(m[1]);
      const arr = Array.isArray(j) ? j : j['@graph'] || [j];
      const art = arr.find((x) => x && /Article|Posting|BlogPosting|WebPage/i.test(String(x['@type'])));
      if (art) { ld = art; break; }
    } catch { /* ignore bad JSON-LD */ }
  }
  const ldKeywords = Array.isArray(ld.keywords) ? ld.keywords.join(', ') : ld.keywords || '';

  const headings = [...html.matchAll(/<h([12])\b[^>]*>([\s\S]*?)<\/h\1>/gi)]
    .map((m) => stripToText(m[2]))
    .filter(Boolean)
    .slice(0, 12);

  const bodyMatch =
    html.match(/<article\b[\s\S]*?<\/article>/i) ||
    html.match(/<main\b[\s\S]*?<\/main>/i) ||
    html.match(/<body\b[\s\S]*<\/body>/i);
  const textSample = stripToText(bodyMatch ? bodyMatch[0] : html).slice(0, 4000);

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
