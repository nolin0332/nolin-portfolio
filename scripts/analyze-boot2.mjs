import fs from 'fs';
const s = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const i = s.indexOf('preload(');
console.log(s.slice(i, i + 800));
const j = s.indexOf('function init(');
console.log('\n--- init ---\n', s.slice(j, j + 1200));
