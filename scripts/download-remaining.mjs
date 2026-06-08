import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const bases = ['https://julio-modern.vercel.app', 'https://vision.spaace.io'];

const paths = [
  'assets/audios/click.mp3',
  'assets/audios/bgm.mp3',
  'assets/audios/wind.mp3',
  'assets/audios/wind_loop.mp3',
  'assets/audios/enterVortex.mp3',
  'assets/audios/subtleSwoosh.mp3',
  'assets/audios/endmusic.mp3',
  'assets/textures/lens_dirt.jpg',
  'assets/textures/self.webp',
  'assets/meta/cover.png',
  'favicon/browserconfig.xml',
  // StoryAirdropPreEngagement popup cards (required — loader stalls at ~41% without these)
  ...['like', 'comment', 'repost', 'follow'].map(
    (id) => `assets/textures/storyAirdropPreEngagement/card-${id}.jpg`,
  ),
  ...['4', '5'].map((n) => `assets/textures/storyAirdropPostAvatars/${n}.png`),
  // aliases for loops
  'assets/audios/loop1.mp3',
  'assets/audios/loop2.mp3',
];

async function download(rel) {
  const out = path.join(root, 'public', rel);
  if (fs.existsSync(out) && fs.statSync(out).size > 500) return 'skip';
  for (const base of bases) {
    try {
      const res = await fetch(`${base}/${rel}`);
      if (!res.ok) continue;
      const buf = Buffer.from(await res.arrayBuffer());
      if (buf.length < 100) continue;
      fs.mkdirSync(path.dirname(out), { recursive: true });
      fs.writeFileSync(out, buf);
      return `ok ${buf.length}`;
    } catch {
      /* */
    }
  }
  return 'miss';
}

for (const rel of paths) {
  const r = await download(rel);
  if (r !== 'skip') console.log(r === 'miss' ? 'MISS' : 'OK', rel, r);
}

// symlink-style copy: enterVortex -> enter_vortex if missing
const evortex = path.join(root, 'public/assets/audios/enterVortex.mp3');
const evortexSrc = path.join(root, 'public/assets/audios/enter_vortex.mp3');
if (!fs.existsSync(evortex) && fs.existsSync(evortexSrc)) {
  fs.copyFileSync(evortexSrc, evortex);
  console.log('COPY enterVortex from enter_vortex');
}
for (let i = 1; i <= 4; i++) {
  const dst = path.join(root, 'public/assets/audios', `loop${i}.mp3`);
  const src = path.join(root, 'public/assets/audios', `loop_${i}.mp3`);
  if (!fs.existsSync(dst) && fs.existsSync(src)) {
    fs.copyFileSync(src, dst);
    console.log(`COPY loop${i} from loop_${i}`);
  }
}
