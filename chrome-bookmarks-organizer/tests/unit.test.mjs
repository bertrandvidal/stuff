import test from 'node:test';
import assert from 'node:assert/strict';
import { findRootFolder, collectFolders, normalizeUrl, resolveFolder, indexUrls, treeToMarkdown } from '../extension/lib/tree.js';
import { parseHtmlMeta, looksBlocked, isGoodEnough, mergeContent, isPrivateHost } from '../extension/lib/extract.js';

const F = (id, title, children = [], extra = {}) => ({ id, title, children, ...extra });
const U = (id, title, url, dateAdded = 0) => ({ id, title, url, dateAdded });

test('prefers the synced copy when local and account storage both have worthy-reads', () => {
  const local = F('L', 'Other bookmarks', [F('l1', 'worthy-reads')], { syncing: false, folderType: 'other' });
  const acct = F('A', 'Other bookmarks', [F('a1', 'Worthy Reads')], { syncing: true, folderType: 'other' });
  const { node, warning } = findRootFolder([F('0', '', [local, acct])], 'worthy-reads');
  assert.equal(node.id, 'a1');
  assert.match(warning, /Found 2/);
});

test('works on older Chrome without the syncing property', () => {
  const tree = [F('0', '', [F('1', 'Bookmarks bar', [F('w', 'worthy-reads')])])];
  assert.equal(findRootFolder(tree, 'worthy-reads').node.id, 'w');
  assert.equal(findRootFolder(tree, 'nope').node, null);
});

test('collectFolders builds paths, skips _inbox/_review, newest samples first', () => {
  const root = F('w', 'worthy-reads', [
    F('i', '_inbox', [U('x', 'pending', 'https://p')]),
    F('r', '_review'),
    F('e', 'engineering', [F('ea', 'architecture', [U('1', 'old', 'https://a/1', 1), U('2', 'new', 'https://a/2', 9)])]),
  ]);
  const fs = collectFolders(root, { exclude: ['_inbox', '_review'], samples: 5 });
  assert.deepEqual(fs.map((f) => f.path), ['engineering', 'engineering/architecture']);
  assert.deepEqual(fs[1].samples, ['new', 'old']);
  assert.equal(fs[1].count, 2);
  const idx = indexUrls(root, fs);
  assert.equal(idx.get(normalizeUrl('https://www.a/1?utm_source=x#frag')), 'engineering/architecture');
  assert.equal(idx.has(normalizeUrl('https://p')), false, 'inbox items are not duplicates of themselves');
  assert.match(treeToMarkdown('worthy-reads', fs), /- architecture {2}\(2\)/);
});

test('normalizeUrl strips tracking params and trailing slashes, keeps real query', () => {
  assert.equal(normalizeUrl('https://Medium.com/@a/post-123/?source=rss----abc&sk=1#x'), 'medium.com/@a/post-123');
  assert.equal(normalizeUrl('https://eng.medium.com/post?source=rss'), 'eng.medium.com/post', 'Medium subdomains too');
  assert.equal(normalizeUrl('https://youtube.com/watch?v=abc&si=xyz'), 'youtube.com/watch?v=abc');
  assert.equal(normalizeUrl('https://blog.x/a?utm_source=tw&fbclid=1&gclid=2&mc_cid=3'), 'blog.x/a');
});

test('normalizeUrl keeps parameters, ports and app routes that make a different page', () => {
  const differ = [
    ['https://blog.example/?s=kafka', 'https://blog.example/?s=spark'], // WordPress search
    ['https://github.com/o/r/tree?ref=v1', 'https://github.com/o/r/tree?ref=v2'], // git ref
    ['https://site.example/a?source=a', 'https://site.example/a?source=b'],
    ['https://app.example/#/article/1', 'https://app.example/#/article/2'],
    ['https://app.example/#!/a', 'https://app.example/#!/b'],
    ['https://example.com:8443/a', 'https://example.com:9443/a'],
  ];
  for (const [a, b] of differ) assert.notEqual(normalizeUrl(a), normalizeUrl(b), `${a} vs ${b}`);
  assert.equal(normalizeUrl('https://example.com:443/a#section-2'), normalizeUrl('https://example.com/a'), 'default port and in-page anchors ignored');
});

test('duplicates are found in the review folder and directly under the root, not in the inbox', () => {
  const root = F('w', 'worthy-reads', [
    F('i', '_inbox', [U('x', 'pending', 'https://p/new')]),
    F('r', '_review', [U('rv', 'waiting', 'https://waiting.example/a')]),
    U('loose', 'loose', 'https://loose.example/b'),
    F('e', 'engineering', [F('ea', 'architecture', [U('1', 'x', 'https://both.example/c')])]),
  ]);
  root.children[1].children.push(U('rv2', 'x', 'https://both.example/c'));
  const fs = collectFolders(root, { exclude: ['_inbox', '_review'] });
  const idx = indexUrls(root, fs, [root.children[1]]);
  assert.equal(idx.get(normalizeUrl('https://waiting.example/a')), '_review');
  assert.equal(idx.get(normalizeUrl('https://loose.example/b')), 'worthy-reads');
  assert.equal(idx.get(normalizeUrl('https://both.example/c')), 'engineering/architecture', 'a real folder wins over review');
  assert.equal(idx.has(normalizeUrl('https://p/new')), false);
});

test('resolveFolder tolerates case and spacing, rejects unknown', () => {
  const fs = [{ id: '1', path: 'engineering/Distributed Systems' }];
  assert.equal(resolveFolder(fs, ' /engineering / distributed-systems/ ').id, '1');
  assert.equal(resolveFolder(fs, 'engineering/frontend'), null);
});

const MEDIUM_HTML = `<!doctype html><html><head><title>Scaling Kafka at Acme | by Jane Doe | Acme Engineering | Medium</title>
<meta property="og:title" content="Scaling Kafka at Acme">
<meta name="description" content="How we went from 3 to 300 brokers without losing sleep, and what broke along the way &amp; why.">
<meta property="og:site_name" content="Medium"><meta property="article:tag" content="Kafka"><meta property="article:tag" content="Distributed Systems">
<script type="application/ld+json">{"@type":"NewsArticle","headline":"Scaling Kafka at Acme","author":{"name":"Jane Doe"},"datePublished":"2026-10-01"}</script>
</head><body><nav>menu</nav><article><h1>Scaling Kafka at Acme</h1><p>We run Kafka&nbsp;for everything.</p><script>evil()</script></article></body></html>`;

test('parseHtmlMeta pulls Medium-style metadata', () => {
  const m = parseHtmlMeta(MEDIUM_HTML);
  assert.equal(m.title, 'Scaling Kafka at Acme');
  assert.match(m.description, /300 brokers.*& why/);
  assert.match(m.keywords, /Kafka, Distributed Systems/);
  assert.equal(m.author, 'Jane Doe');
  assert.equal(m.published, '2026-10-01');
  assert.deepEqual(m.headings, ['Scaling Kafka at Acme']);
  assert.match(m.textSample, /We run Kafka for everything/);
  assert.doesNotMatch(m.textSample, /evil|menu/);
  assert.ok(isGoodEnough(m));
});

test('detects bot walls', () => {
  assert.ok(looksBlocked(403, '', ''));
  assert.ok(looksBlocked(200, 'Just a moment...', ''));
  assert.ok(looksBlocked(200, 'x', '<script src="/cdn-cgi/challenge-platform/h/b/orchestrate"></script>'));
  assert.ok(!looksBlocked(200, 'Scaling Kafka', MEDIUM_HTML));
  assert.ok(!isGoodEnough({ title: 'x', description: 'short' }));
});

test('mergeContent keeps the richer field', () => {
  const m = mergeContent({ title: 'T', description: '', headings: [] }, { title: '', description: 'long desc', headings: ['a'] });
  assert.deepEqual(m, { title: 'T', description: 'long desc', headings: ['a'] });
});

import { folderNameProblems, planFolderRenames } from '../extension/lib/tree.js';

test('folder name validation', () => {
  assert.deepEqual(folderNameProblems({ rootFolderName: 'worthy-reads', inboxName: '_inbox', reviewName: '_review' }), []);
  assert.match(folderNameProblems({ rootFolderName: '  ', inboxName: '_inbox', reviewName: '_review' })[0], /Root folder name needs/);
  assert.match(folderNameProblems({ rootFolderName: 'x', inboxName: '📥', reviewName: '_review' })[0], /Inbox folder name needs/);
  assert.match(folderNameProblems({ rootFolderName: 'x', inboxName: 'Inbox', reviewName: '_inbox' })[0], /different names/);
});

test('renaming inbox/review renames the existing folder, refuses clashes', () => {
  const root = F('w', 'worthy-reads', [F('i', '_inbox'), F('r', '_review'), F('rd', 'reading')]);
  const prev = { inboxName: '_inbox', reviewName: '_review' };
  assert.deepEqual(planFolderRenames(root, prev, { inboxName: '_to-file', reviewName: '_review' }),
    { renames: [{ id: 'i', from: '_inbox', title: '_to-file' }], errors: [] });
  // Cosmetic change that still matches the same folder: rename in place, no clash
  assert.deepEqual(planFolderRenames(root, prev, { inboxName: 'Inbox', reviewName: '_review' }).renames, [{ id: 'i', from: '_inbox', title: 'Inbox' }]);
  const clash = planFolderRenames(root, prev, { inboxName: '_inbox', reviewName: 'Reading' });
  assert.equal(clash.renames.length, 0);
  assert.match(clash.errors[0], /already has a folder named "reading"/);
  // Nothing to rename yet (folders not created): fine, created on next run
  assert.deepEqual(planFolderRenames(F('w', 'worthy-reads'), prev, { inboxName: 'a', reviewName: 'b' }), { renames: [], errors: [] });
});

test('folder names reject slashes', () => {
  const p = folderNameProblems({ rootFolderName: 'worthy/reads', inboxName: '_inbox', reviewName: 'a/b' });
  assert.equal(p.filter((x) => /can't contain "\/"/.test(x)).length, 2);
  assert.deepEqual(folderNameProblems({ rootFolderName: 'reads > worthy', inboxName: '_inbox', reviewName: '_review' }), [], '">" is allowed');
});

test('parser stays fast on malformed HTML (no freeze the timeout could not interrupt)', () => {
  for (const html of ['<body>' + '<script '.repeat(40000), '<h1>' + '<h1 x'.repeat(60000), '<body>' + '<'.repeat(300000), '<meta a="b" '.repeat(25000)]) {
    const t = Date.now();
    parseHtmlMeta(html);
    assert.ok(Date.now() - t < 500, `took ${Date.now() - t}ms`);
  }
});

test('one hostile <meta> tag cannot freeze the parser (attribute regex stays linear)', () => {
  // Each of these took over a minute before the lookbehind in ATTR_RE.
  for (const ch of ['a', '-', ':', '.', '_']) {
    const html = '<html><head><meta ' + ch.repeat(299000) + '></head><body>x</body></html>';
    const t = Date.now();
    parseHtmlMeta(html);
    assert.ok(Date.now() - t < 200, `"${ch}" run took ${Date.now() - t}ms`);
  }
  const m = parseHtmlMeta('<meta property="og:title" content="Hello"><meta name=description content=\'Single quoted\'><meta data-x=1 name="keywords" content="a, b">');
  assert.deepEqual([m.title, m.description, m.keywords], ['Hello', 'Single quoted', 'a, b'], 'attributes still parse');
});

test('parser falls back from article to main to body, and keeps heading order', () => {
  const m = parseHtmlMeta('<html><body><nav>skip</nav><main><h2>Second</h2><p>Main text</p></main></body></html>');
  assert.match(m.textSample, /Main text/);
  assert.doesNotMatch(m.textSample, /skip/);
  const b = parseHtmlMeta('<html><body><h1>One</h1><h2>Two</h2><h1>Three</h1><p>Body text</p><script>x()</script></body></html>');
  assert.deepEqual(b.headings, ['One', 'Two', 'Three']);
  assert.match(b.textSample, /Body text/);
  assert.doesNotMatch(b.textSample, /x\(\)/);
  const unclosed = parseHtmlMeta('<html><body><p>Visible</p><script>never closed');
  assert.match(unclosed.textSample, /Visible/);
  assert.doesNotMatch(unclosed.textSample, /never closed/);
});

import { isFilingTarget, isTrimmedTitle } from '../extension/lib/tree.js';

test('filing targets are leaf folders below the top level', () => {
  const root = F('w', 'worthy-reads', [
    F('e', 'engineering', [F('ea', 'architecture'), F('ed', 'distributed', [F('edk', 'kafka')])]),
    F('m', 'misc'),
  ]);
  const fs = collectFolders(root, {});
  assert.deepEqual(fs.filter(isFilingTarget).map((f) => f.path), ['engineering/architecture', 'engineering/distributed/kafka']);
  assert.deepEqual(fs.filter((f) => !isFilingTarget(f)).map((f) => f.path), ['engineering', 'engineering/distributed', 'misc']);
});

test('isTrimmedTitle accepts only the saved title with parts removed', () => {
  assert.ok(isTrimmedTitle('How to run 1:1s', 'How to run 1:1s | by Jane Doe | Medium'));
  assert.ok(isTrimmedTitle('Sharding  Postgres', 'Sharding Postgres - The Pragmatic Engineer'), 'whitespace differences are fine');
  assert.ok(!isTrimmedTitle('Verify your account at evil.example', 'How to run 1:1s | Medium'), 'a rewrite is not a trim');
  assert.ok(!isTrimmedTitle('', 'anything'));
});

test('isPrivateHost spots this Mac and the local network', () => {
  for (const u of ['http://localhost:3000/', 'http://LOCALHOST./', 'http://127.0.0.1/', 'http://2130706433/', 'http://10.1.2.3/', 'http://172.16.0.1/',
    'http://172.31.255.255/', 'http://192.168.1.1/', 'http://169.254.169.254/', 'http://100.64.0.1/', 'http://0.0.0.0/', 'http://[::1]/',
    'http://[fd00::1]/', 'http://[fe80::1]/', 'http://[::ffff:127.0.0.1]/', 'http://router/', 'http://nas.local/', 'http://printer.lan/',
    'http://box.home.arpa/', 'http://svc.internal/', 'http://app.localhost/']) {
    assert.ok(isPrivateHost(new URL(u).hostname), u);
  }
  for (const u of ['https://medium.com/x', 'https://172.32.0.1/', 'https://8.8.8.8/', 'https://[2606:4700::1]/', 'https://local.example.com/', 'https://192.168.1.1.nip.io/']) {
    assert.ok(!isPrivateHost(new URL(u).hostname), u);
  }
});
