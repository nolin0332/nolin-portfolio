import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');
const css = fs.readFileSync(path.join(root, 'public/_astro/index.Ew-YyTBx.css'), 'utf8');
const urls = [...css.matchAll(/url\(([^)]+)\)/g)]
  .map((m) => m[1].replace(/["']/g, '').trim())
  .map((u) => u.replace(/^\.\.\//, ''));

const base = 'https://julio-modern.vercel.app';
for (const rel of [...new Set(urls)]) {
  const out = path.join(root, 'public', rel);
  if (fs.existsSync(out) && fs.statSync(out).size > 50) {
    console.log('skip', rel);
    continue;
  }
  const res = await fetch(`${base}/${rel}`);
  if (!res.ok) {
    console.log('miss', rel);
    continue;
  }
  const buf = Buffer.from(await res.arrayBuffer());
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, buf);
  console.log('ok', rel, buf.length);
}
