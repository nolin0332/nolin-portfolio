import fs from 'fs';
const s = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
console.log(s.slice(338500, 339200));
const i = s.indexOf('spaaceLogoEntryPoint');
console.log('\n--- spaaceLogoEntryPoint ---\n', s.slice(i, i + 1500));
