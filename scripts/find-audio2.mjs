import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');

// look for wind_loop definition
let idx = 0;
while ((idx = js.indexOf('wind', idx)) !== -1 && idx < js.length) {
  const slice = js.slice(idx, idx + 60);
  if (slice.includes('loop') || slice.includes('.mp3') || slice.includes('audio'))
    console.log(slice);
  idx++;
}

// AudioManager or sounds config
for (const pat of ['sounds:', 'audio:', 'wind_loop', 'click', 'bgm']) {
  const i = js.indexOf(pat);
  if (i > 0) console.log('\n---', pat, '---\n', js.slice(i, i + 200));
}
