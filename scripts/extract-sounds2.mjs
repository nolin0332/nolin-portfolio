import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const idx = js.indexOf('{name:"wind_loop"');
const end = js.indexOf('}],bus:', idx);
const chunk = js.slice(idx - 5000, idx + 8000);

const sounds = new Set();
for (const m of chunk.matchAll(/\{name:"([^"]+)",sound:([^,}]+)/g)) {
  const name = m[1];
  let sound = m[2];
  if (sound.startsWith('[')) {
    for (const x of sound.matchAll(/"([^"]+)"/g)) sounds.add(x[1]);
  } else {
    sound = sound.replace(/[`'"]/g, '');
    sounds.add(sound);
  }
  sounds.add(name);
}

const list = [...sounds].filter((s) => !s.includes('bus') && !s.includes('gain') && s.length < 40).sort();
console.log(list.join('\n'));
fs.writeFileSync('scripts/sound-files.txt', list.map((s) => `assets/audios/${s}.mp3`).join('\n'));
