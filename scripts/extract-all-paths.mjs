import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const js = fs.readFileSync(path.join(root, 'public/_astro/hoisted.jm-mpcuc8bi.js'), 'utf8');

const paths = new Set();

// settings.*_PATH + suffix
for (const key of ['MODEL_PATH', 'IMAGE_PATH', 'TEXTURE_PATH', 'AUDIO_PATH', 'VIDEO_PATH']) {
  const map = {
    MODEL_PATH: 'assets/models/',
    IMAGE_PATH: 'assets/images/',
    TEXTURE_PATH: 'assets/textures/',
    AUDIO_PATH: 'assets/audios/',
    VIDEO_PATH: 'assets/videos/',
  };
  const re = new RegExp(`settings\\.${key}\\+[\`'"]([^\`'"]+)[\`'"]`, 'g');
  let m;
  while ((m = re.exec(js))) {
    const s = m[1];
    if (!s.endsWith('_') && !s.includes('${')) paths.add(map[key] + s);
  }
}

// loader.add("assets/...")
for (const m of js.matchAll(/loader\.add\([\`'"](assets\/[^'"\`]+)[\`'"]/g)) {
  paths.add(m[1]);
}

// quoted /assets/ paths
for (const m of js.matchAll(/[\`'"]\/assets\/([^'"\`]+)[\`'"]/g)) {
  paths.add('assets/' + m[1]);
}

// relative texture filenames used with TEXTURE_PATH in template literals - expand known patterns
const ranks = ['1-bronze', '2-silver', '3-gold', '4-platinum', '5-diamond'];
ranks.forEach((f) => paths.add(`assets/textures/storyGamificationRanks/${f}.png`));

for (let i = 1; i <= 5; i++) paths.add(`assets/textures/storyAirdropPostAvatars/${i}.png`);
for (const id of ['like', 'comment', 'repost', 'follow']) {
  paths.add(`assets/textures/storyAirdropPreEngagement/card-${id}.jpg`);
}
['card1', 'card2', 'card3'].forEach((c) => paths.add(`assets/textures/storyRewardsCashback/${c}.png`));

for (let i = 0; i < 12; i++) {
  paths.add(`assets/models/Terrain_main_${i}.buf`);
  paths.add(`assets/models/Terrain_sided_${i}.buf`);
}

[
  'Staking_eth_tip_inner.buf',
  'Staking_eth_tip_outer.buf',
  'Staking_eth_rest_inner.buf',
  'Staking_eth_rest_outer.buf',
].forEach((f) => paths.add(`assets/models/staking_network/${f}`));

// From prior extract2 - texture filenames without path
const exts = ['png', 'jpg', 'jpeg', 'webp', 'svg', 'mp4', 'webm', 'ogg', 'mp3', 'wav', 'woff', 'woff2', 'buf', 'ktx2'];
const re = new RegExp(`[a-zA-Z0-9_./-]+\\.(${exts.join('|')})`, 'gi');
const skip = /three|node_modules|vimeo|window\.|this\.|api\/|Lusion_exported|test_trailer|smaa|LDR_RGB/i;
let m;
while ((m = re.exec(js))) {
  const v = m[0];
  if (skip.test(v) || v.length > 100) continue;
  if (v.includes('/')) {
    if (v.startsWith('assets/')) paths.add(v);
    else {
      paths.add('assets/textures/' + v);
      paths.add('assets/images/' + v);
      paths.add('assets/models/' + v);
    }
  }
}

const html = fs.readFileSync(path.join(root, 'public/index.html'), 'utf8');
for (const mm of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
  const u = mm[1];
  if (!/^https?:|mailto:|#|javascript:/.test(u)) paths.add(u.replace(/^\//, ''));
}

const css = fs.readFileSync(path.join(root, 'public/_astro/index.Ew-YyTBx.css'), 'utf8');
for (const mm of css.matchAll(/url\(([^)]+)\)/g)) {
  const u = mm[1].replace(/["']/g, '').trim().replace(/^\.\.\//, '');
  if (!u.startsWith('data:')) paths.add(u);
}

const out = [...paths].filter((p) => !p.includes('${')).sort();
fs.writeFileSync(path.join(root, 'scripts/all-asset-paths.txt'), out.join('\n'));
console.log('paths', out.length);
console.log(out.join('\n'));
