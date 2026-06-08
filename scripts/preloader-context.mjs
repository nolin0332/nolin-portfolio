import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');

function ctx(needle, len = 800) {
  const idx = js.indexOf(needle);
  if (idx < 0) return console.log('not found', needle);
  console.log('\n===', needle, '===\n', js.slice(idx, idx + len));
}

ctx('class Preloader');
ctx('loader.start(');
ctx('onLoadComplete');
ctx('SKIP_ANIMATION');
ctx('julio-loader');
ctx('--jlp');
