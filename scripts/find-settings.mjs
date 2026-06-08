import fs from 'fs';

const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const idx = js.indexOf('TEXTURE_PATH');
console.log('indexes', idx);
for (let i = 0; i < 5; i++) {
  const pos = js.indexOf('TEXTURE_PATH', i ? js.indexOf('TEXTURE_PATH', js.indexOf('TEXTURE_PATH') + 1) : 0);
  if (pos < 0) break;
  console.log(js.slice(pos - 80, pos + 200));
  console.log('---');
}

const m = js.match(/TEXTURE_PATH:"[^"]+"/g);
console.log('matches', m);

const settingsMatch = js.match(/settings=\{[^}]{0,2000}\}/);
console.log('settings snippet', settingsMatch?.[0]?.slice(0, 500));
