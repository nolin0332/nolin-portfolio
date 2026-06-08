import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'public');
const js = fs.readFileSync(path.join(root, '_astro/hoisted.jm-mpcuc8bi.js'), 'utf8');
const base = process.env.BASE || 'http://127.0.0.1:5136';

const paths = new Set();
for (const key of ['MODEL_PATH', 'TEXTURE_PATH', 'IMAGE_PATH', 'VIDEO_PATH', 'AUDIO_PATH']) {
  const map = {
    MODEL_PATH: 'assets/models/',
    TEXTURE_PATH: 'assets/textures/',
    IMAGE_PATH: 'assets/images/',
    VIDEO_PATH: 'assets/videos/',
    AUDIO_PATH: 'assets/audios/',
  };
  const re = new RegExp(`settings\\.${key}\\+[\`'"]([^\`'"]+)[\`'"]`, 'g');
  let m;
  while ((m = re.exec(js))) {
    const s = m[1];
    if (!s.endsWith('_') && !s.includes('${')) paths.add(map[key] + s);
  }
}

const sounds = fs.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'scripts/sound-files.txt'), 'utf8')
  .trim()
  .split('\n')
  .filter(Boolean);
sounds.forEach((p) => paths.add(p));

let fail = 0;
for (const rel of [...paths].sort()) {
  try {
    const res = await fetch(`${base}/${rel}`, { method: 'HEAD' });
    if (!res.ok) {
      fail++;
      console.log('FAIL', res.status, rel);
    }
  } catch (e) {
    fail++;
    console.log('ERR', rel, e.message);
  }
}
console.log('checked', paths.size, 'failed', fail);
