import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const idx = js.indexOf('Staking_eth_"+');
console.log(js.slice(idx, idx + 350));
