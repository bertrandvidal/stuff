import test from 'node:test';
import assert from 'node:assert/strict';
import { makeChrome } from './mockchrome.mjs';

const decisions = {
  'medium.com': { folder_path: 'management/one-on-ones', confidence: 'high' },
  'blog.example': { folder_path: 'engineering/architecture', confidence: 'medium' },
  'vague.example': { folder_path: 'general', confidence: 'low' },
  'invented.example': { folder_path: 'engineering/observability', confidence: 'high' },
};
let failHost = true;
const m = makeChrome({ decide: async (job) => {
  const host = new URL(job.bookmark.url).hostname;
  if (host === 'flaky.example' && failHost) return { ok: false, error: 'Claude Code took longer than 240s' };
  const d = decisions[host] || { folder_path: 'general', confidence: 'high' };
  return { ok: true, decision: { is_career_relevant: true, clean_title: 'Clean ' + host, reason: 'because', new_folder_suggestion: host === 'invented.example' ? 'engineering/observability' : '', ...d } };
} });
globalThis.chrome = m.chrome;
globalThis.fetch = async (url) => {
  const h = new URL(url).hostname;
  if (h === 'medium.com') return { ok: false, status: 403, url, headers: new Map([['content-type', 'text/html']]), text: async () => '<title>Just a moment...</title>' };
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
  await send({ cmd: 'fileFromReview', id: 'c', folderId: 'car' });
  await settle();
  const { examples } = await chrome.storage.local.get('examples');
  assert.deepEqual(examples.map((e) => [e.path, e.note]), [
    ['career', 'suggested general'],
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
  assert.equal(parentOf('f'), 'gen');
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
