import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
// find terrain loop
const idx = js.indexOf('Terrain_main_');
const chunk = js.slice(idx - 500, idx + 800);
console.log(chunk);

// search TERRAIN or terrain count
for (const pat of ['TERRAIN', 'terrainCount', 'terrain', 'NUM_TERRAIN', 'for(let o=0;o<']) {
  const i = js.indexOf(pat);
  if (i > 0) console.log(pat, js.slice(i, i + 80));
}
