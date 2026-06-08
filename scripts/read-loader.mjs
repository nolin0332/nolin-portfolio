import fs from 'fs';
const s = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const i = s.indexOf('properties.loader');
console.log(s.slice(366000, 368500));
