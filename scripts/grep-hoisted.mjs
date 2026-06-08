import fs from 'fs';
const s = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
for (const t of [
  'class Loader',
  'loader.start',
  'properties.loader',
  'ChunkLoadError',
  'intro-hero',
  'spaaceLogoEntryPoint',
  'displayPercent',
  'LOGO',
  'SKIP_ANIMATION',
  'footer-loading-indicator',
]) {
  console.log(t, s.includes(t) ? s.indexOf(t) : -1);
}

// Footer update snippet
const i = s.indexOf('footer-loading-indicator');
if (i > 0) console.log('\n', s.slice(i - 200, i + 400));
