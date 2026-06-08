import fs from 'fs';
const j = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const start = j.indexOf('frag$8=`');
const end = j.indexOf('`,ShaderChunk.ufxVert', start);
const frag = j.slice(start, end);
const idx = frag.indexOf('texture2D(u_texture,v_uv)');
console.log('texture sample at', idx);
console.log(frag.slice(idx - 300, idx + 500));
