import fs from 'fs';
const s = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
let idx = 0;
let n = 0;
while ((idx = s.indexOf('loaderPercent', idx)) >= 0 && n < 8) {
  console.log('---', n, idx, '---');
  console.log(s.slice(idx - 120, idx + 200));
  idx++;
  n++;
}
