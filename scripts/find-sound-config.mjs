import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const idx = js.indexOf('main:wind_loop');
console.log(js.slice(idx - 300, idx + 500));

// find audio scene definitions
const idx2 = js.indexOf('wind_loop');
let pos = 0;
let n = 0;
while (n < 8 && (pos = js.indexOf('wind_loop', pos)) !== -1) {
  console.log('\n---', n, '---\n', js.slice(pos - 80, pos + 120));
  pos++;
  n++;
}
