import fs from 'fs';

const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const patterns = [
  /MODEL_PATH\+["'`]([^"'`]+)["'`]/g,
  /IMAGE_PATH\+["'`]([^"'`]+)["'`]/g,
  /TEXTURE_PATH\+["'`]([^"'`]+)["'`]/g,
  /AUDIO_PATH\+["'`]([^"'`]+)["'`]/g,
  /VIDEO_PATH\+["'`]([^"'`]+)["'`]/g,
  /loader\.add\(["'`](assets\/[^"'`]+)["'`]/g,
];

const paths = new Set();
for (const re of patterns) {
  let m;
  while ((m = re.exec(js))) {
    const p = m[1];
    if (p.includes('${')) continue;
    paths.add(p.startsWith('assets/') ? p : null);
    // relative to path prefix - reconstruct
    if (!p.startsWith('assets/')) {
      if (re.source.includes('MODEL')) paths.add('assets/models/' + p);
      else if (re.source.includes('IMAGE')) paths.add('assets/images/' + p);
      else if (re.source.includes('TEXTURE')) paths.add('assets/textures/' + p);
      else if (re.source.includes('AUDIO')) paths.add('assets/audios/' + p);
      else if (re.source.includes('VIDEO')) paths.add('assets/videos/' + p);
    }
  }
}

// also relative texture paths from TEXTURE_PATH+
const re2 = /TEXTURE_PATH\+[`'"]([^`'"]+)[`'"]/g;
let m;
while ((m = re2.exec(js))) paths.add('assets/textures/' + m[1]);

const re3 = /MODEL_PATH\+[`'"]([^`'"]+)[`'"]/g;
while ((m = re3.exec(js))) paths.add('assets/models/' + m[1]);

const re4 = /AUDIO_PATH\+[`'"]([^`'"]+)[`'"]/g;
while ((m = re4.exec(js))) paths.add('assets/audios/' + m[1]);

console.log([...paths].filter(Boolean).sort().join('\n'));
console.log('count', paths.size);
