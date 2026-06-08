import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const idx = js.indexOf('name:"wind_loop"');
const chunk = js.slice(idx - 2000, idx + 3000);
const sounds = new Set();
for (const m of chunk.matchAll(/sound:([\[`'"][^\]}\]]+[\]}\]]|"[^"]+"|'[^']+')/g)) {
  let s = m[1];
  if (s.startsWith('[')) {
    for (const x of s.matchAll(/"([^"]+)"/g)) sounds.add(x[1]);
  } else {
    s = s.replace(/[`'"]/g, '');
    sounds.add(s);
  }
}
for (const m of chunk.matchAll(/name:"([^"]+)"/g)) sounds.add(m[1]);
console.log([...sounds].sort().join('\n'));
