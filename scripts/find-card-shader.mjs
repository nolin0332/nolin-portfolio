import fs from 'fs';
const j = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const i = j.indexOf('frag$8=`');
console.log(j.slice(i, i + 2500));
