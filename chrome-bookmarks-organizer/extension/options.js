import { DEFAULTS, getSettings } from './lib/config.js';

const $ = (id) => document.getElementById(id);
const send = (msg) => chrome.runtime.sendMessage(msg);

const fmtTime = (t) => (t ? new Date(t).toLocaleString() : 'never');

function el(tag, attrs = {}, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') e.className = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  }
  for (const c of children) if (c != null) e.append(c);
  return e;
}

async function render() {
  const o = await send({ cmd: 'overview' });
  const s = await getSettings();
  $('inboxPath').textContent = `${o.rootName || s.rootFolderName}/${s.inboxName}`;
  $('reviewPath').textContent = `${o.rootName || s.rootFolderName}/${s.reviewName}`;
  $('rootName').textContent = o.rootName || 'not found';
  $('inboxCount').textContent = String(o.inboxCount ?? 0);
  $('lastRun').textContent = fmtTime(o.status.lastRun);
  $('lastResult').textContent = o.status.lastResult || '';
  const problem = o.error || o.status.lastError || o.warning || '';
  $('lastError').textContent = problem || 'none';
  $('lastError').className = problem ? 'err' : 'ok';

  // Review queue
  const review = $('review');
  review.replaceChildren();
  $('reviewCount').textContent = String(o.reviewItems.length);
  if (!o.reviewItems.length) review.append(el('li', { class: 'empty' }, 'Nothing waiting.'));
  for (const it of o.reviewItems) {
    const sel = el('select');
    const suggested = o.folders.find((f) => f.path === it.suggestedPath);
    if (!suggested) sel.append(el('option', { value: '' }, it.suggestedPath ? `Choose a folder (Claude suggested "${it.suggestedPath}")` : 'Choose a folder…'));
    for (const f of o.folders) {
      const opt = el('option', { value: f.id }, f.path);
      if (suggested && f.id === suggested.id) opt.selected = true;
      sel.append(opt);
    }
    const fileBtn = el('button', { class: 'primary', onclick: async () => {
      if (!sel.value) return;
      fileBtn.disabled = true;
      await send({ cmd: 'fileFromReview', id: it.id, folderId: sel.value });
      render();
    } }, 'File here');
    const retryBtn = el('button', { onclick: async () => { await send({ cmd: 'retry', id: it.id }); render(); } }, 'Retry');
    review.append(el('li', {},
      el('a', { href: it.url, target: '_blank', rel: 'noopener' }, it.title || it.url),
      el('div', { class: 'reason' },
        it.confidence ? `${it.confidence} confidence. ` : '',
        it.reason || 'Moved here by hand.'),
      el('div', { class: 'row' }, sel, fileBtn, retryBtn)));
  }

  // Activity log
  const log = $('log');
  log.replaceChildren();
  if (!o.log.length) log.append(el('tr', {}, el('td', { class: 'empty' }, 'No activity yet.')));
  for (const e of o.log.slice(0, 60)) {
    const cls = e.level === 'error' ? 'err' : e.level === 'review' || e.level === 'warn' ? 'warn' : '';
    log.append(el('tr', {},
      el('td', { class: 'when' }, fmtTime(e.at)),
      el('td', {},
        el('div', { class: cls }, e.msg),
        e.title ? el('div', { class: 'muted' }, e.title) : null,
        e.reason ? el('div', { class: 'muted' }, `Why: ${e.reason}`) : null)));
  }

  // Learned examples
  const ex = $('examples');
  ex.replaceChildren();
  $('exampleCount').textContent = String(o.examples.length);
  if (!o.examples.length) ex.append(el('li', { class: 'empty' }, 'None yet.'));
  for (const e of o.examples) {
    ex.append(el('li', {}, el('a', { href: e.url, target: '_blank', rel: 'noopener' }, e.title), el('div', { class: 'reason' }, `→ ${e.path} (${e.note})`)));
  }

  $('tree').value = o.treeMarkdown || '';
}

async function loadSettings() {
  const s = await getSettings();
  for (const k of Object.keys(DEFAULTS)) {
    const input = $(k);
    if (!input) continue;
    if (input.type === 'checkbox') input.checked = !!s[k];
    else input.value = s[k];
  }
}

// Show each folder name's default next to its field.
for (const hint of document.querySelectorAll('[data-default-for]')) {
  hint.append(` Default: ${DEFAULTS[hint.dataset.defaultFor]}`);
}

function readForm() {
  const next = {};
  for (const [k, def] of Object.entries(DEFAULTS)) {
    const input = $(k);
    if (!input) continue;
    if (input.type === 'checkbox') next[k] = input.checked;
    else if (typeof def === 'number') {
      const n = Number(input.value);
      next[k] = Number.isFinite(n) && input.value !== '' ? Math.max(Number(input.min) || 0, n) : def;
    } else next[k] = input.value.trim();
  }
  return next;
}

async function save(next) {
  const out = $('saved');
  const r = await send({ cmd: 'saveSettings', settings: next });
  if (r?.error) {
    out.className = 'err';
    out.textContent = r.error;
    return;
  }
  out.className = 'ok';
  out.textContent = r.renamed?.length ? `Saved. Renamed ${r.renamed.join(', ')}.` : 'Saved';
  setTimeout(() => (out.textContent = ''), 4000);
  await loadSettings();
  render();
}

$('settings').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  await save(readForm());
});

$('resetNames').addEventListener('click', async () => {
  const next = { ...readForm(), rootFolderName: DEFAULTS.rootFolderName, inboxName: DEFAULTS.inboxName, reviewName: DEFAULTS.reviewName };
  await save(next);
});

$('runNow').addEventListener('click', async () => {
  const b = $('runNow');
  b.disabled = true;
  b.textContent = 'Filing… (Claude takes ~20s per link)';
  try {
    const r = await send({ cmd: 'sweep' });
    if (r?.skipped) $('testResult').textContent = `Skipped: ${r.skipped}`;
  } finally {
    b.disabled = false;
    b.textContent = 'File inbox now';
    render();
  }
});

$('test').addEventListener('click', async () => {
  const out = $('testResult');
  out.className = 'muted';
  out.textContent = 'Testing…';
  const r = await send({ cmd: 'ping' });
  if (r?.ok) {
    out.className = r.auth_ok && r.isolation_ok !== false ? 'ok' : 'warn';
    out.textContent = (r.auth_ok
      ? `Connected. Claude Code ${r.claude_version || ''} is signed in.`
      : `Host works, but Claude Code isn't signed in: ${r.auth_detail || 'run "claude auth login" in Terminal'}`)
      + (r.isolation ? ` ${r.isolation}` : '');
  } else {
    out.className = 'err';
    out.textContent = r?.error || 'No response from native host';
  }
});

$('clearLog').addEventListener('click', async () => { await send({ cmd: 'clearLog' }); render(); });
$('clearExamples').addEventListener('click', async () => {
  if (confirm('Forget every learned example?')) { await send({ cmd: 'clearExamples' }); render(); }
});
$('copyTree').addEventListener('click', async () => {
  await navigator.clipboard.writeText($('tree').value);
  $('copied').textContent = 'Copied';
  setTimeout(() => ($('copied').textContent = ''), 2000);
});

loadSettings();
render();
setInterval(render, 15000);
