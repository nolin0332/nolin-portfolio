import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..', 'public');
const js = fs.readFileSync(path.join(root, '_astro/hoisted.jm-mpcuc8bi.js'), 'utf8');

const prefixes = {
  MODEL_PATH: 'assets/models/',
  IMAGE_PATH: 'assets/images/',
  TEXTURE_PATH: 'assets/textures/',
  VIDEO_PATH: 'assets/videos/',
};

const missing = [];
for (const [key, base] of Object.entries(prefixes)) {
  const re = new RegExp(`settings\\.${key}\\+[\`'"]([^\`'"]+)[\`'"]`, 'g');
  let m;
  while ((m = re.exec(js))) {
    let rel = base + m[1];
    if (rel.endsWith('_')) continue; // dynamic suffix
    const file = path.join(root, rel);
    if (!fs.existsSync(file) || fs.statSync(file).size < 50) missing.push(rel);
  }
}

console.log('Missing static assets:', missing.length);
missing.forEach((p) => console.log(' -', p));
