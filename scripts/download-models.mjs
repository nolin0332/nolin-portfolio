import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');

const staticPaths = [
  'assets/models/Hex_Ring.buf',
  'assets/models/Hex_Ring_New.buf',
  'assets/models/coin/coin_md.buf',
  'assets/models/end/astronaut.buf',
  'assets/models/end/astronaut_animation.buf',
  'assets/models/end/rock.buf',
  'assets/models/logo/logo.buf',
  'assets/models/logo/logo_shell.buf',
  'assets/models/staking_network/Network_point_ref.buf',
  'assets/models/staking_network/Network_segment_ref.buf',
  'assets/models/staking_network/Network_segments.buf',
  'assets/models/staking_network/Staking_eth_tip_points.buf',
  'assets/models/staking_network/Staking_trail.buf',
  'assets/textures/lens_dirt.jpg',
  'assets/textures/self.webp',
];

// terrain and staking variants from bundle patterns
for (let i = 0; i < 8; i++) {
  staticPaths.push(`assets/models/Terrain_main_${i}.buf`);
  staticPaths.push(`assets/models/Terrain_sided_${i}.buf`);
}
for (let i = 0; i < 6; i++) {
  staticPaths.push(`assets/models/staking_network/Staking_eth_${i}.buf`);
}

// story textures with numeric suffixes
for (let i = 1; i <= 5; i++) {
  staticPaths.push(`assets/textures/storyAirdropPostAvatars/${i}.png`);
}
for (const id of ['like', 'comment', 'repost', 'follow']) {
  staticPaths.push(`assets/textures/storyAirdropPreEngagement/card-${id}.jpg`);
}
for (const name of ['card1', 'card2', 'card3']) {
  staticPaths.push(`assets/textures/storyRewardsCashback/${name}.png`);
}
for (const f of ['1-bronze', '2-silver', '3-gold', '4-platinum', '5-diamond']) {
  staticPaths.push(`assets/textures/${f}.png`);
}

// rank images
for (const f of [
  'bronze',
  'silver',
  'gold',
  'platinum',
  'diamond',
  'unranked',
  'master',
  'grandmaster',
]) {
  staticPaths.push(`assets/textures/storyGamificationRanks/${f}.png`);
}

const base = 'https://julio-modern.vercel.app';

async function download(rel) {
  const out = path.join(root, 'public', rel);
  if (fs.existsSync(out) && fs.statSync(out).size > 50) return 'skip';
  const res = await fetch(`${base}/${rel}`);
  if (!res.ok) return 'miss';
  const buf = Buffer.from(await res.arrayBuffer());
  if (buf.length < 50) return 'miss';
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, buf);
  return `ok ${buf.length}`;
}

let ok = 0,
  miss = 0;
for (const rel of staticPaths) {
  const s = await download(rel);
  if (s?.startsWith('ok')) {
    ok++;
    console.log('OK', rel, s);
  } else if (s === 'skip') {
    /* */
  } else {
    miss++;
    console.log('MISS', rel);
  }
}
console.log(`done ok=${ok} miss=${miss}`);
