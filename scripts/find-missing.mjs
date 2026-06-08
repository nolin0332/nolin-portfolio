import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');

const terrain = [...js.matchAll(/Terrain_[a-z_0-9]+/gi)].map((m) => m[0]);
console.log('terrain', [...new Set(terrain)]);

const ranks = [...js.matchAll(/fileName:"([^"]+)"/g)].map((m) => m[1]);
console.log('rank files', [...new Set(ranks)]);

const mp3 = [...js.matchAll(/[a-zA-Z0-9_/.-]+\.mp3/g)].map((m) => m[0]);
console.log('mp3', [...new Set(mp3)].slice(0, 30));
