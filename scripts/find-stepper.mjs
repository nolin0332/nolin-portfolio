import fs from 'fs';
const html = fs.readFileSync('public/index.html', 'utf8');
let i = 0;
while ((i = html.indexOf('section-stepper', i)) >= 0) {
  console.log('at', i, ':', html.slice(Math.max(0, i - 40), i + 120).replace(/\s+/g, ' '));
  i++;
}
