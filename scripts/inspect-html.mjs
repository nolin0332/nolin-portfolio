import fs from 'fs';

const html = fs.readFileSync('public/index.html', 'utf8');
const htm = fs.readFileSync('public/index.htm', 'utf8');

for (const id of [
  'section-stepper',
  'footer-hero-button',
  'intro-hero-title',
  'boot-fix',
  'SKIP_ANIMATION',
  'LOGO',
  'julio-overrides',
  'boot-force-enter',
]) {
  console.log(id, 'html', html.includes(id), 'htm', htm.includes(id));
}

const idx = html.indexOf('id="footer');
console.log('\n--- footer snippet ---\n');
console.log(html.slice(idx, idx + 3000));

const idx2 = html.indexOf('section-stepper');
console.log('\n--- stepper snippet ---\n');
console.log(html.slice(idx2, idx2 + 1500));
