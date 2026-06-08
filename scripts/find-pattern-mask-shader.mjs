import fs from 'fs';
const j = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const marker = 'u_patternMaskTexture';
let idx = 0;
let n = 0;
while (n < 3 && (idx = j.indexOf(marker, idx)) >= 0) {
  console.log('\n===', n, '===\n', j.slice(idx, idx + 1200));
  idx++;
  n++;
}
