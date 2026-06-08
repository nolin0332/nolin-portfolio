import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const i = js.indexOf('class Footer');
const chunk = js.slice(i, i + 8000);
const ui = chunk.indexOf('update(o)');
console.log(chunk.slice(ui, ui + 2000));
