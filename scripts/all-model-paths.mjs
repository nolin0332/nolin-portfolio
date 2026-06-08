import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const re = /settings\.MODEL_PATH\+[`'"]([^`'"]+)[`'"]/g;
const paths = new Set();
let m;
while ((m = re.exec(js))) paths.add('assets/models/' + m[1]);
console.log([...paths].sort().join('\n'));
