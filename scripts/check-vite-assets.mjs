import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'public');
const js = fs.readFileSync(path.join(root, '_astro/hoisted.jm-mpcuc8bi.js'), 'utf8');
const base = process.env.BASE || 'http://127.0.0.1:5136';

const map = {
  MODEL_PATH: 'assets/models/',
  TEXTURE_PATH: 'assets/textures/',
  IMAGE_PATH: 'assets/images/',
  VIDEO_PATH: 'assets/videos/',
};

const paths = new Set();
for (const [key, prefix] of Object.entries(map)) {
  const re = new RegExp(`settings\\.${key}\\+[\`'"]([^\`'"]+)[\`'"]`, 'g');
  let m;
  while ((m = re.exec(js))) {
    const s = m[1];
    if (!s.endsWith('_') && !s.includes('${')) paths.add(prefix + s);
  }
}

const sounds = fs
  .readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)), 'sound-files.txt'), 'utf8')
  .trim()
  .split('\n')
  .filter(Boolean);
sounds.forEach((p) => paths.add(p));

const bad = [];
for (const rel of [...paths].sort()) {
  const res = await fetch(`${base}/${rel}`, { method: 'HEAD' });
  const ct = res.headers.get('content-type') || '';
  if (!res.ok || ct.includes('text/html')) {
    bad.push({ rel, status: res.status, ct });
  }
}

console.log('checked', paths.size, 'bad', bad.length);
for (const b of bad) console.log('BAD', b.status, b.ct, b.rel);
