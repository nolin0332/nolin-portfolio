import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');
const js = fs.readFileSync(path.join(root, 'public/_astro/hoisted.jm-mpcuc8bi.js'), 'utf8');

const exts = ['glb', 'gltf', 'ktx2', 'ktx', 'basis', 'mp4', 'webm', 'ogg', 'mp3', 'wav', 'png', 'jpg', 'jpeg', 'webp', 'svg', 'hdr', 'woff', 'woff2'];
const re = new RegExp(`[a-zA-Z0-9_./-]+\\.(${exts.join('|')})`, 'gi');
const skip = /three|node_modules|vimeo|window\.|this\.|\.json$|api\/|Lusion_exported/i;
const files = new Set();
let m;
while ((m = re.exec(js))) {
  const v = m[0];
  if (skip.test(v) || v.length > 120 || v.startsWith('http')) continue;
  files.add(v.replace(/^\//, ''));
}

const pathMap = {
  MODEL_PATH: 'assets/models/',
  IMAGE_PATH: 'assets/images/',
  TEXTURE_PATH: 'assets/textures/',
  AUDIO_PATH: 'assets/audios/',
  VIDEO_PATH: 'assets/videos/',
};

const toTry = new Set();
for (const f of files) {
  if (f.startsWith('assets/')) {
    toTry.add(f);
    continue;
  }
  toTry.add(pathMap.TEXTURE_PATH + f);
  toTry.add(pathMap.IMAGE_PATH + f);
  toTry.add(pathMap.MODEL_PATH + f);
  toTry.add(pathMap.VIDEO_PATH + f);
  toTry.add(pathMap.AUDIO_PATH + f);
}

// known extras
[
  'assets/meta/cover.png',
  'assets/textures/LDR_RGB1_0.png',
  'assets/videos/test_trailer.mp4',
  'assets/videos/test_trailer_vertical.mp4',
].forEach((p) => toTry.add(p));

const bases = [
  'https://julio-modern.vercel.app',
  'https://vision.spaace.io',
];

async function download(rel) {
  const out = path.join(root, 'public', rel);
  if (fs.existsSync(out) && fs.statSync(out).size > 100) return 'skip';

  for (const base of bases) {
    const url = `${base}/${rel}`;
    try {
      const res = await fetch(url);
      if (!res.ok) continue;
      const buf = Buffer.from(await res.arrayBuffer());
      if (buf.length < 50) continue;
      fs.mkdirSync(path.dirname(out), { recursive: true });
      fs.writeFileSync(out, buf);
      return `ok ${buf.length} from ${base}`;
    } catch {
      /* try next */
    }
  }
  return 'miss';
}

const list = [...toTry].sort();
let ok = 0,
  miss = 0,
  skipped = 0;
const missed = [];

for (const rel of list) {
  const status = await download(rel);
  if (status === 'skip') skipped++;
  else if (status?.startsWith('ok')) {
    ok++;
    console.log('OK', rel, status);
  } else {
    miss++;
    missed.push(rel);
  }
}

console.log(`\ndone ok=${ok} skip=${skipped} miss=${miss} tried=${list.length}`);
if (missed.length) {
  fs.writeFileSync(path.join(root, 'scripts/missed-assets.txt'), missed.join('\n'));
  console.log('missed list -> scripts/missed-assets.txt');
}
