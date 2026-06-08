import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const idx = js.indexOf('lens_dirt');
console.log('count', (js.match(/lens_dirt/g) || []).length);
console.log(js.slice(idx - 150, idx + 200));
