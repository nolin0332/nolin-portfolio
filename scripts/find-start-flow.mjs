import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const terms = ['startButton', 'START', 'intro', 'hasInitialized', 'quickLoader', 'loadError', 'onError', 'footer.loader', 'spaaceLogoEntryPoint', 'startTimeAfterStartButtonClick', 'not-supported', 'WebGL'];
for (const t of terms) {
  const c = (js.match(new RegExp(t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
  if (c) console.log(t, c);
}
ctx = (n) => { const i = js.indexOf(n); console.log('\n', n, js.slice(i, i+500)); };
ctx('startTimeAfterStartButtonClick');
ctx('not-supported');
ctx('properties.hasInitialized');
