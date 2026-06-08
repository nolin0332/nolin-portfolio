import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const m = [...js.matchAll(/[a-zA-Z0-9_/.-]+\.buf/g)].map((x) => x[0]);
const unique = [...new Set(m)];
console.log(unique.join('\n'));
