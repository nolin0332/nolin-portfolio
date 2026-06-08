import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');
const js = fs.readFileSync(path.join(root, 'public/_astro/hoisted.jm-mpcuc8bi.js'), 'utf8');

const exts = ['glb', 'gltf', 'ktx2', 'ktx', 'basis', 'mp4', 'webm', 'ogg', 'mp3', 'wav', 'png', 'jpg', 'jpeg', 'webp', 'svg', 'hdr', 'woff', 'woff2'];
const re = new RegExp(`[a-zA-Z0-9_./-]+\\.(${exts.join('|')})`, 'gi');
const skip = /three|node_modules|vimeo|window\.|this\.|\.json$/i;
const files = new Set();
let m;
while ((m = re.exec(js))) {
  const v = m[0];
  if (skip.test(v) || v.length > 100 || v.startsWith('http')) continue;
  files.add(v.replace(/^\//, ''));
}

const prefixes = [
  '',
  'assets/',
  'assets/textures/',
  'assets/models/',
  'assets/images/',
  'assets/videos/',
  'assets/audios/',
];

const base = 'https://julio-modern.vercel.app';
const toTry = new Set();

for (const f of files) {
  if (f.startsWith('assets/')) toTry.add(f);
  else {
    for (const p of prefixes) toTry.add(p + f);
  }
}

async function download(rel) {
  const url = `${base}/${rel}`;
  const out = path.join(root, 'public', rel);
  if (fs.existsSync(out) && fs.statSync(out).size > 0) return 'skip';
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const res = await fetch(url);
  if (!res.ok) return 'miss';
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(out, buf);
  return `ok ${buf.length}`;
}

const list = [...toTry].sort();
let ok = 0, miss = 0;
for (const rel of list) {
  const status = await download(rel);
  if (status === 'ok' || status?.startsWith('ok')) {
    ok++;
    console.log('OK', rel, status);
  } else if (status === 'skip') {
    // console.log('SKIP', rel);
  } else {
    miss++;
  }
}
console.log(`done ok=${ok} miss=${miss} tried=${list.length}`);
