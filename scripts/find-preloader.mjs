import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const terms = ['preloader', 'Preloader', 'julio-loader', '--jlp', 'experience-started', 'loadComplete', 'hidePreloader', 'onLoadComplete', 'loaderComplete', 'isLoaded', 'introComplete'];
for (const t of terms) {
  const c = (js.match(new RegExp(t, 'g')) || []).length;
  if (c) console.log(t, c);
}
const idx = js.indexOf('preloader');
if (idx > 0) console.log('\n---sample---\n', js.slice(idx - 50, idx + 400));
