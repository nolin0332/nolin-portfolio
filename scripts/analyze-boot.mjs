import fs from 'fs';
const s = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');

const snippets = [
  'initCallFuncList',
  '_startCallback',
  'hasStarted',
  'startTime=',
  'preloader.hide',
  'preloader.start',
  'class Preloader',
  'renderer.compile',
  'properties.hasInitialized',
  'footer-hero-button',
  'addEventListener("click"',
];

for (const t of snippets) {
  let i = 0, c = 0;
  while ((i = s.indexOf(t, i)) >= 0 && c < 2) {
    console.log('\n===', t, c, '@', i, '===');
    console.log(s.slice(i, i + 350));
    i++;
    c++;
  }
}
