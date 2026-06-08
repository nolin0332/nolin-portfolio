import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
let idx = 0;
let n = 0;
while (n < 10 && (idx = js.indexOf('properties.hasStarted', idx)) !== -1) {
  console.log('\n---', n, '---\n', js.slice(idx - 100, idx + 200));
  idx++;
  n++;
}
