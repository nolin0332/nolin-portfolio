import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');

// audio paths
for (const m of js.matchAll(/AUDIO_PATH\+[`'"]([^`'"]+)[`'"]/g)) console.log('AUDIO', m[1]);
for (const m of js.matchAll(/audios\/[a-zA-Z0-9_./-]+/g)) {
  const v = m[0];
  if (v.length < 80) console.log(v);
}

// scene audio triggers
for (const m of js.matchAll(/trigger\([\`'"]([^`'"]+)[\`'"]/g)) {
  const t = m[1];
  if (t.includes('sound') || t.includes('audio') || t.includes('wind') || t.includes('music') || t.includes('loop'))
    console.log('trigger', t);
}

// mp3 in quotes
for (const m of js.matchAll(/[\`'"][a-zA-Z0-9_/-]+\.mp3[\`'"]/g)) console.log('mp3', m[0]);
