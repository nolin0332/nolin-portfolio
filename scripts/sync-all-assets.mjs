import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');
const js = fs.readFileSync(path.join(root, 'public/_astro/hoisted.jm-mpcuc8bi.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'public/_astro/index.Ew-YyTBx.css'), 'utf8');
const html = fs.readFileSync(path.join(root, 'public/index.html'), 'utf8');

const paths = new Set();

// HTML href/src
for (const m of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
  const u = m[1];
  if (!u.startsWith('http') && !u.startsWith('mailto:') && !u.startsWith('#') && !u.startsWith('javascript:'))
    paths.add(u.replace(/^\//, ''));
}

// CSS urls
for (const m of css.matchAll(/url\(([^)]+)\)/g)) {
  const u = m[1].replace(/["']/g, '').trim().replace(/^\.\.\//, '');
  if (!u.startsWith('data:')) paths.add(u);
}

// Loader paths from JS
const prefixKeys = ['MODEL_PATH', 'IMAGE_PATH', 'TEXTURE_PATH', 'AUDIO_PATH', 'VIDEO_PATH'];
for (const key of prefixKeys) {
  const re = new RegExp(`settings\\.${key}\\+[\`'"]([^\`'"]+)[\`'"]`, 'g');
  let m;
  while ((m = re.exec(js))) {
    const suffix = m[1];
    if (suffix.endsWith('_') || suffix.includes('${')) continue;
    const base = `assets/${key.replace('_PATH', '').toLowerCase()}s/`.replace('models', 'models').replace('audios', 'audios');
    const map = {
      MODEL_PATH: 'assets/models/',
      IMAGE_PATH: 'assets/images/',
      TEXTURE_PATH: 'assets/textures/',
      AUDIO_PATH: 'assets/audios/',
      VIDEO_PATH: 'assets/videos/',
    };
    paths.add(map[key] + suffix);
  }
}

// Dynamic expansions found in bundle
for (let i = 0; i < 8; i++) {
  paths.add(`assets/models/Terrain_main_${i}.buf`);
  paths.add(`assets/models/Terrain_sided_${i}.buf`);
}
for (const [a, l] of [
  ['tip', 'inner'],
  ['tip', 'outer'],
  ['rest', 'inner'],
  ['rest', 'outer'],
]) {
  paths.add(`assets/models/staking_network/Staking_eth_${a}_${l}.buf`);
}
for (let i = 1; i <= 5; i++) {
  paths.add(`assets/textures/storyGamificationRanks/${i}-bronze.png`.replace('1-bronze', `${i}-${['bronze', 'silver', 'gold', 'platinum', 'diamond'][i - 1]}`));
  paths.add(`assets/textures/storyAirdropPostAvatars/${i}.png`);
}
for (const id of ['like', 'comment', 'repost', 'follow']) {
  paths.add(`assets/textures/storyAirdropPreEngagement/card-${id}.jpg`);
}
for (const c of ['card1', 'card2', 'card3']) {
  paths.add(`assets/textures/storyRewardsCashback/${c}.png`);
}

// Rank files
['1-bronze', '2-silver', '3-gold', '4-platinum', '5-diamond'].forEach((f) =>
  paths.add(`assets/textures/storyGamificationRanks/${f}.png`),
);

const bases = ['https://julio-modern.vercel.app', 'https://vision.spaace.io'];

async function download(rel) {
  const out = path.join(root, 'public', rel);
  if (fs.existsSync(out) && fs.statSync(out).size > 100) return 'skip';
  for (const base of bases) {
    try {
      const res = await fetch(`${base}/${rel}`);
      if (!res.ok) continue;
      const buf = Buffer.from(await res.arrayBuffer());
      if (buf.length < 50) continue;
      fs.mkdirSync(path.dirname(out), { recursive: true });
      fs.writeFileSync(out, buf);
      return `ok ${buf.length} (${new URL(base).hostname})`;
    } catch {
      /* */
    }
  }
  return 'miss';
}

const list = [...paths].sort();
let ok = 0,
  miss = 0,
  skip = 0;
const missed = [];

for (const rel of list) {
  const r = await download(rel);
  if (r === 'skip') skip++;
  else if (r?.startsWith('ok')) {
    ok++;
    console.log('OK', rel, r);
  } else {
    miss++;
    missed.push(rel);
  }
}

fs.writeFileSync(path.join(root, 'scripts/missed-assets.txt'), missed.join('\n'));
console.log(`\nSync: ok=${ok} skip=${skip} miss=${miss} total=${list.length}`);
