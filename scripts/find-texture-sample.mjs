import fs from 'fs';
const j = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const start = j.indexOf('texture2D(u_texture');
let count = 0;
let i = start;
while (count < 5 && (i = j.indexOf('texture2D(u_texture', i)) >= 0) {
  console.log('\n---', count, '---\n', j.slice(i - 200, i + 400));
  i++;
  count++;
}
