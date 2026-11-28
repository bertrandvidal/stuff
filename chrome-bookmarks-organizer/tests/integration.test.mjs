import test from 'node:test';
import assert from 'node:assert/strict';
import { makeChrome } from './mockchrome.mjs';

const decisions = {
  'medium.com': { folder_path: 'management/one-on-ones', confidence: 'high' },
  'blog.example': { folder_path: 'engineering/architecture', confidence: 'medium' },
  'vague.example': { folder_path: 'general/reading', confidence: 'low' },
  'parent.example': { folder_path: 'management', confidence: 'high' },
  'toplevel.example': { folder_path: 'misc', confidence: 'high' },
  'nested.example': { folder_path: 'engineering/data', confidence: 'high' },
  'invented.example': { folder_path: 'engineering/observability', confidence: 'high' },
};
let failHost = true;
let failSetup = false;
let hostGone = null; // a Chrome disconnect message, to simulate losing the bridge
const m = makeChrome({ decide: async (job) => {
  const host = new URL(job.bookmark.url).hostname;
  if (hostGone) return { disconnect: hostGone };
  if (host === 'flaky.example' && failHost) return { ok: false, error: 'Claude Code took longer than 240s' };
  if (failSetup) return { ok: false, systemic: true, error: "This Claude Code doesn't support --strict-mcp-config. Update Claude Code." };
  const d = decisions[host] || { folder_path: 'general/reading', confidence: 'high' };
  return { ok: true, decision: { is_career_relevant: true, clean_title: 'Clean ' + host, reason: 'because', new_folder_suggestion: host === 'invented.example' ? 'engineering/observability' : '', ...d } };
} });
globalThis.chrome = m.chrome;
globalThis.fetch = async (url) => {
  const h = new URL(url).hostname;
  if (h === 'medium.com') return { ok: false, status: 403, url, headers: new Map([['content-type', 'text/html']]), text: async () => '<title>Just a moment...</title>' };
  if (h === 'hang.example') return { ok: false, status: 403, url, headers: new Map([['content-type', 'text/html']]), text: async () => '<title>Just a moment...</title>' };
  if (h === 'files.example') return { ok: true, status: 200, url, headers: new Map([['content-type', 'application/pdf']]), text: async () => '%PDF-1.7' };
  if (h === 'gone.example') return { ok: false, status: 404, url, headers: new Map([['content-type', 'text/html']]), text: async () => '<title>Page not found</title>' };
  const html = `<title>${h} post</title><meta name="description" content="A long enough description of this ${h} article that clearly explains its topic.">`;
  return { ok: true, status: 200, url, headers: new Map([['content-type', 'text/html']]), text: async () => html };
};

// Synced tree: worthy-reads under Other bookmarks (syncing), plus a local decoy copy.
const { add, nodes, calls, send } = m;
add({ id: '0', title: '' });
add({ id: '1', parentId: '0', title: 'Other bookmarks', syncing: false, folderType: 'other' });
add({ id: '2', parentId: '0', title: 'Other bookmarks', syncing: true, folderType: 'other' });
add({ id: 'decoy', parentId: '1', title: 'worthy-reads' });
add({ id: 'wr', parentId: '2', title: 'worthy-reads' });
add({ id: 'inbox', parentId: 'wr', title: '_inbox' });
for (const [id, t] of [['eng', 'engineering'], ['mgmt', 'management'], ['car', 'career'], ['gen', 'general']]) add({ id, parentId: 'wr', title: t });
add({ id: 'arch', parentId: 'eng', title: 'architecture' });
add({ id: 'o3', parentId: 'mgmt', title: 'one-on-ones' });
add({ id: 'hire', parentId: 'mgmt', title: 'hiring' });
add({ id: 'cg', parentId: 'car', title: 'growth' });
add({ id: 'gr', parentId: 'gen', title: 'reading' });
add({ id: 'misc', parentId: 'wr', title: 'misc' }); // top-level folder with no subfolders
add({ id: 'old', parentId: 'arch', title: 'Existing post', url: 'https://dup.example/post' });
const links = { a: 'https://medium.com/@x/skip-levels-123?source=rss', b: 'https://blog.example/arch', c: 'https://vague.example/', d: 'https://www.dup.example/post/?utm_source=tw', e: 'https://invented.example/o11y', f: 'https://flaky.example/x' };
for (const [id, url] of Object.entries(links)) add({ id, parentId: 'inbox', title: id + ' title', url });

await import('../extension/background.js');
const { sweep } = await import('../extension/background.js');
const settle = () => new Promise((r) => setTimeout(r, 30));
const parentOf = (id) => nodes.get(id).parentId;
const folderNamed = (t) => [...nodes.values()].find((n) => n.parentId === 'wr' && n.title === t);

test('first sweep files, parks and retries the right items', async () => {
  const r = await sweep('test');
  await settle();
  assert.deepEqual({ filed: r.filed, review: r.review, failed: r.failed }, { filed: 2, review: 3, failed: 1 });
  const review = folderNamed('_review');
  assert.ok(review, '_review folder created in the synced worthy-reads');
  assert.equal(nodes.get('decoy').children.length, 0, 'local decoy untouched');
  assert.equal(parentOf('a'), 'o3', 'blocked Medium link filed via tab extraction');
  assert.equal(calls.windows, 1, 'only the blocked page needed a hidden window');
  assert.equal(parentOf('b'), 'arch', 'medium confidence auto-files by default');
  assert.equal(nodes.get('b').title, 'Clean blog.example', 'filed links get the clean title by default');
  assert.equal(nodes.get('c').title, 'c title', 'links sent to review keep their title');
  assert.equal(parentOf('c'), review.id, 'low confidence parked');
  assert.equal(parentOf('d'), review.id, 'duplicate parked');
  assert.equal(parentOf('e'), review.id, 'invented folder parked');
  assert.equal(parentOf('f'), 'inbox', 'failed item stays in inbox for retry');
  const job = calls.jobs.find((j) => j.bookmark.url === links.a);
  assert.equal(job.content.source, 'tab');
  assert.ok(job.folders.some((f) => f.path === 'architecture' || f.path === 'engineering/architecture'));
  assert.ok(!job.folders.some((f) => f.path.startsWith('_')), 'system folders hidden from Claude');
  assert.ok(!calls.jobs.some((j) => j.bookmark.url === links.d), 'duplicate skipped Claude entirely');
  assert.equal(calls.badge.at(-1), '3');
  const { review: rec, log } = await chrome.storage.local.get(['review', 'log']);
  assert.match(rec.d.reason, /Already bookmarked in engineering\/architecture/);
  assert.match(rec.e.reason, /isn't an existing folder.*Possible new folder: engineering\/observability/);
  assert.ok(log.some((e) => e.level === 'error' && /Attempt 1\/3/.test(e.msg)));
});

test('your manual corrections become examples for next time', async () => {
  await chrome.bookmarks.move('a', { parentId: 'hire' }); // Bert disagrees with the organizer
  await settle();
  const ov = await send({ cmd: 'overview' });
  assert.equal(ov.reviewItems.length, 3);
  assert.match((await send({ cmd: 'fileFromReview', id: 'c', folderId: 'car' })).error, /leaf folder/);
  await send({ cmd: 'fileFromReview', id: 'c', folderId: 'cg' });
  await settle();
  const { examples } = await chrome.storage.local.get('examples');
  assert.deepEqual(examples.map((e) => [e.path, e.note]), [
    ['career/growth', 'suggested general/reading'],
    ['management/hiring', 'corrected from management/one-on-ones'],
  ]);
});

test('next sweep sends examples to Claude, gives up on a persistently failing link', async () => {
  calls.jobs.length = 0;
  await sweep('t2'); await settle();
  await sweep('t3'); await settle();
  assert.equal(parentOf('f'), folderNamed('_review').id, 'parked after 3 failed attempts');
  assert.equal(calls.jobs.at(-1).examples.length, 2);
  const { review } = await chrome.storage.local.get('review');
  assert.match(review.f.reason, /Couldn't categorize after 3 tries/);
});

test('retry moves an item back to the inbox and it gets filed', async () => {
  failHost = false;
  await send({ cmd: 'retry', id: 'f' }); await settle();
  assert.equal(parentOf('f'), 'inbox');
  assert.ok(calls.alarms.includes('sweep-soon'));
  await sweep('t4'); await settle();
  assert.equal(parentOf('f'), 'gr');
});

test('folder names: rename existing folders, reject bad input, keep filing with custom names', async () => {
  const inboxId = 'inbox';
  const reviewId = folderNamed('_review').id;

  let r = await send({ cmd: 'saveSettings', settings: { rootFolderName: 'does-not-exist' } });
  assert.match(r.error, /No bookmark folder named "does-not-exist"/);
  r = await send({ cmd: 'saveSettings', settings: { inboxName: 'Inbox', reviewName: 'inbox' } });
  assert.match(r.error, /different names/);
  r = await send({ cmd: 'saveSettings', settings: { reviewName: 'Career' } });
  assert.match(r.error, /already has a folder named "career"/);
  assert.equal((await chrome.storage.local.get('settings')).settings, undefined, 'nothing saved on error');

  r = await send({ cmd: 'saveSettings', settings: { rootFolderName: 'Worthy Reads', inboxName: '  _to-file ', reviewName: '_needs-review' } });
  assert.equal(r.ok, true);
  assert.deepEqual(r.renamed, ['_inbox → _to-file', '_review → _needs-review']);
  assert.equal(nodes.get(inboxId).title, '_to-file', 'same folder, renamed (items keep their place)');
  assert.equal(nodes.get(reviewId).title, '_needs-review');
  const { settings } = await chrome.storage.local.get('settings');
  assert.equal(settings.inboxName, '_to-file', 'trimmed');
  assert.equal(settings.minConfidence, 'medium', 'other settings keep defaults');

  // New link from the phone lands in the renamed inbox and gets filed.
  add({ id: 'g', parentId: inboxId, title: 'g title', url: 'https://blog.example/new-post' });
  calls.jobs.length = 0;
  const s = await sweep('custom-names'); await settle();
  assert.equal(s.filed, 1);
  assert.equal(parentOf('g'), 'arch');
  assert.ok(!calls.jobs[0].folders.some((f) => /to-file|needs-review|_inbox|_review/.test(f.path)), 'system folders still hidden');
  assert.equal(folderNamed('_inbox'), undefined, 'no stray default folders created');
  assert.equal(folderNamed('_review'), undefined);
  const ov = await send({ cmd: 'overview' });
  assert.equal(ov.reviewItems.length, (await chrome.bookmarks.getChildren(reviewId)).length, 'review queue reads the renamed folder');
});

test('host is told the current folder names', () => {
  assert.deepEqual(calls.lastFolderNames, { root: 'Worthy Reads', inbox: '_to-file', review: '_needs-review' });
});

// ---------- review fixes: permissions, extraction, duplicates, timeout, names ----------

test('#13: commands are ignored unless they come from the options page', async () => {
  const listener = chrome.runtime.onMessage.ls[0];
  let replied = false;
  for (const sender of [
    { id: 'some-other-extension', url: 'chrome-extension://some-other-extension/options.html' },
    { id: 'testext', url: 'https://evil.example/', tab: { id: 3 } }, // e.g. a content script
    {},
  ]) {
    assert.equal(listener({ cmd: 'clearLog' }, sender, () => { replied = true; }), false);
  }
  await settle();
  assert.equal(replied, false);
  assert.ok((await chrome.storage.local.get('log')).log.length > 0, 'log not cleared');
});

test('#13: review actions refuse bookmarks that are not in the review folder', async () => {
  const r = await send({ cmd: 'fileFromReview', id: 'old', folderId: 'gen' });
  assert.match(r.error, /no longer in the review folder/);
  assert.equal(parentOf('old'), 'arch', 'not moved');
  assert.match((await send({ cmd: 'retry', id: 'old' })).error, /no longer in the review folder/);
});

test('#14 and #16: no window for PDFs or dead links; same link twice in one run is filed once', async () => {
  for (const [id, url] of [
    ['pdf', 'https://files.example/paper.pdf'],
    ['dead', 'https://gone.example/post'],
    ['tw1', 'https://twice.example/a'],
    ['tw2', 'https://twice.example/a?utm_source=newsletter'],
  ]) add({ id, parentId: 'inbox', title: `${id} title`, url });
  const windowsBefore = calls.windows;
  calls.jobs.length = 0;
  await sweep('fixes'); await settle();
  assert.equal(calls.windows, windowsBefore, 'no hidden window opened');
  const pdf = calls.jobs.find((j) => j.bookmark.url.includes('paper.pdf'));
  assert.match(pdf.content.note, /not a web page \(application\/pdf\)/);
  const dead = calls.jobs.find((j) => j.bookmark.url.includes('gone.example'));
  assert.equal(dead.content.source, 'unavailable');
  assert.match(dead.content.note, /dead link \(HTTP 404\)/);
  assert.equal(calls.jobs.filter((j) => j.bookmark.url.includes('twice.example')).length, 1, 'Claude asked once');
  assert.equal(parentOf('tw1'), 'gr');
  assert.equal(nodes.get(parentOf('tw2')).title, '_needs-review');
  const { review } = await chrome.storage.local.get('review');
  assert.match(review.tw2.reason, /Already bookmarked in general\/reading/);
});

test('#6: a page that never finishes loading is abandoned after the timeout and the window is closed', async () => {
  const { settings } = await chrome.storage.local.get('settings');
  await chrome.storage.local.set({ settings: { ...settings, pageTimeoutSeconds: 5 } });
  add({ id: 'hang', parentId: 'inbox', title: 'A page that never loads', url: 'https://hang.example/forever' });
  const closedBefore = calls.windowsClosed || 0;
  calls.jobs.length = 0;
  const t0 = Date.now();
  const r = await sweep('timeout'); await settle();
  const secs = (Date.now() - t0) / 1000;
  assert.ok(secs >= 4.5 && secs < 9, `took ${secs}s`);
  assert.equal((calls.windowsClosed || 0) - closedBefore, 1, 'window closed');
  assert.equal(r.failed, 0, 'still filed from title and URL');
  assert.equal(calls.jobs[0].content.source, 'unavailable');
  const { log } = await chrome.storage.local.get('log');
  assert.ok(log.some((e) => /didn't finish loading within 5s/.test(e.msg)));
});

test('folder names cannot contain a slash', async () => {
  const r = await send({ cmd: 'saveSettings', settings: { inboxName: 'reading/new' } });
  assert.match(r.error, /Inbox folder name can't contain "\/"/);
  assert.equal(nodes.get('inbox').title, '_to-file', 'nothing renamed or created');
});

test('links only go into leaf folders below the top level; anything else goes to review', async () => {
  add({ id: 'edata', parentId: 'eng', title: 'data' });
  add({ id: 'edb', parentId: 'edata', title: 'databases' });
  for (const [id, url] of [['par', 'https://parent.example/x'], ['top', 'https://toplevel.example/y'], ['nest', 'https://nested.example/z']]) add({ id, parentId: 'inbox', title: `${id} title`, url });
  calls.jobs.length = 0;
  await sweep('leaf'); await settle();
  const offered = calls.jobs[0].folders.map((f) => f.path).sort();
  assert.deepEqual(offered, ['career/growth', 'engineering/architecture', 'engineering/data/databases', 'management/hiring', 'management/one-on-ones', 'general/reading'].sort(),
    'Claude is only offered leaf folders below the top level');
  const reviewId = nodes.get(parentOf('par')).title === '_needs-review';
  assert.ok(reviewId, 'answer with a parent folder went to review');
  assert.equal(nodes.get(parentOf('top')).title, '_needs-review', 'answer with a top-level folder went to review');
  const { review } = await chrome.storage.local.get('review');
  assert.match(review.par.reason, /"management", which is a top-level folder; links only go into leaf folders/);
  assert.match(review.nest.reason, /"engineering\/data", which has subfolders/);
  assert.match(review.top.reason, /"misc", which is a top-level folder/);
  const ov = await send({ cmd: 'overview' });
  assert.ok(!ov.folders.some((f) => ['management', 'misc', 'general', 'engineering', 'career'].includes(f.path)), '"File here" offers leaf folders only');
});

test('moving a bookmark into a non-leaf folder is not learned as an example', async () => {
  const before = (await chrome.storage.local.get('examples')).examples.length;
  await chrome.bookmarks.move('par', { parentId: 'mgmt' }); // Bert drags it into "management" itself
  await settle();
  assert.equal((await chrome.storage.local.get('examples')).examples.length, before);
});

test('#1: a Claude Code setup problem pauses filing without counting failures', async () => {
  failSetup = true;
  add({ id: 'setup', parentId: 'inbox', title: 'setup title', url: 'https://setup.example/z' });
  const r = await sweep('setup'); await settle();
  assert.equal(r.paused, true);
  assert.equal(parentOf('setup'), 'inbox', 'link waits in the inbox');
  const { attempts, status, log } = await chrome.storage.local.get(['attempts', 'status', 'log']);
  assert.equal(attempts.setup, undefined, 'not counted as a failed attempt');
  assert.match(status.lastError, /doesn't support --strict-mcp-config/);
  assert.match(log[0].msg, /^Filing paused/);
  failSetup = false;
  await sweep('setup fixed'); await settle();
  assert.equal(parentOf('setup'), 'gr', 'filed normally once Claude Code is fixed');
});

test('signed out, usage limit or a lost bridge pause filing; three sweeps later nothing is in review', async () => {
  // The host reports account problems as systemic (see test_host.py); the
  // extension must also treat every kind of lost bridge as systemic.
  add({ id: 'acct1', parentId: 'inbox', title: 'acct1 title', url: 'https://acct.example/1' });
  add({ id: 'acct2', parentId: 'inbox', title: 'acct2 title', url: 'https://acct.example/2' });
  for (const gone of ['Error when communicating with the native messaging host.', 'Failed to start native messaging host.', 'Native host has exited.']) {
    hostGone = gone;
    const r = await sweep('bridge down'); await settle();
    assert.equal(r.paused, true, gone);
  }
  hostGone = null;
  failSetup = true; // what the host sends for "Not logged in · Please run /login"
  for (let i = 0; i < 3; i++) { await sweep('signed out'); await settle(); }
  failSetup = false;
  assert.equal(parentOf('acct1'), 'inbox', 'still waiting in the inbox, not parked');
  assert.equal(parentOf('acct2'), 'inbox');
  const { attempts, status } = await chrome.storage.local.get(['attempts', 'status']);
  assert.equal(attempts.acct1, undefined, 'no attempts counted');
  assert.match(status.lastError, /Update Claude Code|isn't signed in|Lost the connection/);
  await sweep('back'); await settle();
  assert.equal(parentOf('acct1'), 'gr', 'filed once Claude Code works again');
  assert.equal(parentOf('acct2'), 'gr');
});

test('two sweeps started together run once: Claude is asked once per link', async () => {
  add({ id: 'dup1', parentId: 'inbox', title: 'dup1 title', url: 'https://together.example/1' });
  add({ id: 'dup2', parentId: 'inbox', title: 'dup2 title', url: 'https://together.example/2' });
  calls.jobs.length = 0;
  const results = await Promise.all([sweep('alarm:sweep'), sweep('alarm:sweep-soon'), sweep('manual')]);
  await settle();
  assert.equal(results.filter((r) => r.skipped).length, 2, 'the other two were skipped');
  assert.equal(calls.jobs.length, 2, 'one Claude request per link');
  assert.equal(parentOf('dup1'), 'gr');
  assert.equal(parentOf('dup2'), 'gr');
  assert.equal((await chrome.storage.session.get('lock')).lock, undefined, 'lock released');
});
