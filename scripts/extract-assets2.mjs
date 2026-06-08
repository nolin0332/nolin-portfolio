import fs from 'fs';

const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const exts = ['glb', 'gltf', 'ktx2', 'ktx', 'basis', 'mp4', 'webm', 'ogg', 'mp3', 'wav', 'png', 'jpg', 'jpeg', 'webp', 'svg', 'hdr', 'exr', 'json', 'woff', 'woff2', 'wasm'];
const re = new RegExp(`[a-zA-Z0-9_./-]+\\.(${exts.join('|')})`, 'gi');
const s = new Set();
let m;
while ((m = re.exec(js))) {
  const v = m[0];
  if (v.includes('node_modules') || v.length > 120) continue;
  if (v.startsWith('http') || v.includes('three')) continue;
  s.add(v.replace(/^\//, ''));
}
const sorted = [...s].sort();
for (const p of sorted) console.log(p);
console.log('count', sorted.length);
