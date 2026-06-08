import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const idx = js.indexOf('Terrain_main_');
console.log('count', (js.match(/Terrain_main_/g) || []).length);
let pos = 0;
for (let i = 0; i < 5; i++) {
  pos = js.indexOf('Terrain_main_', pos);
  if (pos < 0) break;
  console.log(js.slice(pos, pos + 120));
  pos += 1;
}
