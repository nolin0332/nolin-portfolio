import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const matches = [...js.matchAll(/MODEL_PATH\+[`'"]([^`'"]+)[`'"]/g)];
console.log('count', matches.length);
for (const m of matches) console.log(m[1]);
