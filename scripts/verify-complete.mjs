import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'public');
const js = fs.readFileSync(path.join(root, '_astro/hoisted.jm-mpcuc8bi.js'), 'utf8');

const sources = [...js.matchAll(/\{name:"([a-zA-Z0-9_]+)"\}/g)]
  .map((m) => m[1])
  .filter((name, i, arr) => arr.indexOf(name) === i);

const map = {
  MODEL_PATH: 'assets/models/',
  IMAGE_PATH: 'assets/images/',
  TEXTURE_PATH: 'assets/textures/',
  VIDEO_PATH: 'assets/videos/',
};

const missing = [];
for (const [key, base] of Object.entries(map)) {
  const re = new RegExp(`settings\\.${key}\\+[\`'"]([^\`'"]+)[\`'"]`, 'g');
  let m;
  while ((m = re.exec(js))) {
    const s = m[1];
    if (s.endsWith('_') || s.includes('${')) continue;
    const rel = base + s;
    const file = path.join(root, rel);
    if (!fs.existsSync(file) || fs.statSync(file).size < 50) missing.push(rel);
  }
}

const popupCards = ['like', 'comment', 'repost', 'follow'].map(
  (id) => `assets/textures/storyAirdropPreEngagement/card-${id}.jpg`,
);
missing.push(
  ...popupCards.filter((rel) => {
    const f = path.join(root, rel);
    return !fs.existsSync(f) || fs.statSync(f).size < 500;
  }),
);

const missingSounds = [];
for (const name of sources) {
  for (const ext of ['ogg', 'mp3']) {
    const rel = `assets/audios/${name}.${ext}`;
    const f = path.join(root, rel);
    if (!fs.existsSync(f) || fs.statSync(f).size < 500) missingSounds.push(rel);
  }
}

const files = [];
function walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) walk(p);
    else files.push(p);
  }
}
walk(root);
const totalMb = files.reduce((s, f) => s + fs.statSync(f).size, 0) / 1024 / 1024;

console.log('Files:', files.length);
console.log('Size MB:', totalMb.toFixed(2));
console.log('Missing loader assets:', missing.length, missing);
console.log('Missing sounds:', missingSounds.length, missingSounds.slice(0, 20));
if (missingSounds.length > 20) console.log('  … and', missingSounds.length - 20, 'more');
if (missing.length || missingSounds.length) process.exitCode = 1;
