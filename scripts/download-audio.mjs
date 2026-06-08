import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const js = fs.readFileSync(path.join(root, 'public/_astro/hoisted.jm-mpcuc8bi.js'), 'utf8');

// Extract audio ids from scene config
const audioIds = new Set();
for (const m of js.matchAll(/[\w]+:\{[^}]*?(?:url|src|file|path)[^}]*?\}/g)) {
  /* skip huge */
}
for (const m of js.matchAll(/(?:id|name|key):[\`'"]([\w:]+)[\`'"]/g)) {
  const id = m[1];
  if (id.includes('wind') || id.includes('click') || id.includes('bgm') || id.includes('music') || id.includes('sound'))
    audioIds.add(id);
}

// Klang / plan8 audio chunk - search mp3 and ogg
for (const m of js.matchAll(/[\`'"]([a-zA-Z0-9_/-]+\.(?:mp3|ogg|wav))[\`'"]/g)) {
  audioIds.add(m[1]);
}

// common spaace audio names from triggers
['click', 'bgm', 'wind_loop', 'wind', 'whoosh', 'intro', 'ambient'].forEach((a) =>
  audioIds.add(a + '.mp3'),
);

const bases = ['https://julio-modern.vercel.app', 'https://vision.spaace.io'];

for (const file of audioIds) {
  const rel = file.startsWith('assets/') ? file : `assets/audios/${file}`;
  const out = path.join(root, 'public', rel);
  if (fs.existsSync(out) && fs.statSync(out).size > 1000) {
    console.log('skip', rel);
    continue;
  }
  let done = false;
  for (const base of bases) {
    try {
      const res = await fetch(`${base}/${rel}`);
      if (!res.ok) continue;
      const buf = Buffer.from(await res.arrayBuffer());
      if (buf.length < 500) continue;
      fs.mkdirSync(path.dirname(out), { recursive: true });
      fs.writeFileSync(out, buf);
      console.log('ok', rel, buf.length, base);
      done = true;
      break;
    } catch (e) {
      /* */
    }
  }
  if (!done) console.log('miss', rel);
}
