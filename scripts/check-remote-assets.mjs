import fs from 'fs';

const hoisted = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const res = await fetch('https://julio-modern.vercel.app/_astro/hoisted.jm-mpcuc8bi.js');
const remote = Buffer.from(await res.arrayBuffer());

const local = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js');
console.log('hoisted local', local.length, 'remote', remote.length, 'match', local.length === remote.length);
if (local.length !== remote.length) {
  console.log('HASH mismatch - need re-download');
}

// Test key assets from localhost
const base = 'http://127.0.0.1:5136/';
const tests = [
  'assets/models/logo/logo.buf',
  'assets/textures/logo.png',
  'assets/fonts/GolosText-Bold.woff2',
  '_astro/hoisted.jm-mpcuc8bi.js',
];
for (const t of tests) {
  try {
    const r = await fetch(base + t, { signal: AbortSignal.timeout(3000) });
    console.log(t, r.status, r.headers.get('content-length'));
  } catch (e) {
    console.log(t, 'ERR', e.message);
  }
}
