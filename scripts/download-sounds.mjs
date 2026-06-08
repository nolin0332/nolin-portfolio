/**
 * Download klang audio sources as .mp3 and .ogg.
 * Browsers that support OGG only request .ogg (no mp3 fallback) — both are required locally.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const publicRoot = path.join(root, 'public');
const js = fs.readFileSync(path.join(publicRoot, '_astro/hoisted.jm-mpcuc8bi.js'), 'utf8');

const sources = [...js.matchAll(/\{name:"([a-zA-Z0-9_]+)"\}/g)]
  .map((m) => m[1])
  .filter((name, i, arr) => arr.indexOf(name) === i);

const listPath = path.join(root, 'scripts/sound-files.txt');
const extra = fs
  .readFileSync(listPath, 'utf8')
  .trim()
  .split('\n')
  .filter(Boolean)
  .map((rel) => path.basename(rel, '.mp3'));

const names = [...new Set([...sources, ...extra])].sort();
const bases = ['https://vision.spaace.io', 'https://julio-modern.vercel.app'];
const exts = ['ogg', 'mp3'];
const minBytes = { ogg: 500, mp3: 500 };

let ok = 0;
let miss = 0;
const missing = [];

for (const name of names) {
  for (const ext of exts) {
    const rel = `assets/audios/${name}.${ext}`;
    const out = path.join(publicRoot, rel);
    if (fs.existsSync(out) && fs.statSync(out).size > minBytes[ext]) {
      ok++;
      continue;
    }
    let done = false;
    for (const base of bases) {
      try {
        const res = await fetch(`${base}/${rel}`);
        if (!res.ok) continue;
        const buf = Buffer.from(await res.arrayBuffer());
        if (buf.length < minBytes[ext]) continue;
        fs.mkdirSync(path.dirname(out), { recursive: true });
        fs.writeFileSync(out, buf);
        console.log('OK', rel, buf.length);
        ok++;
        done = true;
        break;
      } catch {
        /* try next base */
      }
    }
    if (!done) {
      miss++;
      missing.push(rel);
      console.log('MISS', rel);
    }
  }
}

// Alias files referenced elsewhere but not klang source names
const aliases = [
  ['enterVortex', 'enter_vortex'],
  ['loop1', 'loop_1'],
  ['loop2', 'loop_2'],
  ['loop3', 'loop_3'],
  ['loop4', 'loop_4'],
  ['subtleSwoosh', 'airdrop'],
];
for (const [dst, src] of aliases) {
  for (const ext of exts) {
    const from = path.join(publicRoot, `assets/audios/${src}.${ext}`);
    const to = path.join(publicRoot, `assets/audios/${dst}.${ext}`);
    if (fs.existsSync(from) && (!fs.existsSync(to) || fs.statSync(to).size < minBytes[ext])) {
      fs.copyFileSync(from, to);
      console.log('ALIAS', `${dst}.${ext} <- ${src}.${ext}`);
    }
  }
}

// Keep sound-files.txt in sync (mp3 paths only)
const mp3Lines = names.map((n) => `assets/audios/${n}.mp3`).join('\n') + '\n';
fs.writeFileSync(listPath, mp3Lines);

const stillMissing = [];
for (const name of sources) {
  for (const ext of exts) {
    const rel = `assets/audios/${name}.${ext}`;
    const out = path.join(publicRoot, rel);
    if (!fs.existsSync(out) || fs.statSync(out).size < minBytes[ext]) stillMissing.push(rel);
  }
}

console.log(`\nAudio: downloaded=${ok} klangSources=${sources.length}`);
if (stillMissing.length) {
  console.log('Missing klang audio:', stillMissing.join(', '));
  process.exitCode = 1;
}
