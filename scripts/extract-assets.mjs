import fs from 'fs';

const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const re = /["']([./]?assets\/[^"']+)["']/g;
const s = new Set();
let m;
while ((m = re.exec(js))) s.add(m[1].replace(/^\.\//, '').replace(/^\//, ''));
console.log([...s].sort().join('\n'));
console.log('count', s.size);

const re2 = /["']([^"']+\.(glb|gltf|ktx2|mp4|webm|woff2?))["']/gi;
const s2 = new Set();
while ((m = re2.exec(js))) s2.add(m[1]);
console.log('\next files:\n', [...s2].sort().join('\n'));
