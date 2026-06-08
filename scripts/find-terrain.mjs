import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const m = js.match(/Terrain_main_[a-zA-Z0-9_.]+/g);
console.log([...new Set(m || [])]);
const m2 = js.match(/Terrain_sided_[a-zA-Z0-9_.]+/g);
console.log([...new Set(m2 || [])]);
const m3 = js.match(/Staking_eth_[a-zA-Z0-9_.]+/g);
console.log([...new Set(m3 || [])]);
