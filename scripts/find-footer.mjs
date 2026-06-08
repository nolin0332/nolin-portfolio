import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
for (const n of ['class Footer', 'hasStarted=!0', 'hasStarted=true', 'startButton', 'footer-button', 'id="footer"', 'Enter the experience']) {
  const i = js.indexOf(n);
  if (i >= 0) console.log('\n===', n, '===\n', js.slice(i, i + 600));
}
