import fs from 'fs';
const css = fs.readFileSync('public/_astro/index.Ew-YyTBx.css', 'utf8');
const idx = css.indexOf('intro-hero');
console.log('matches:', [...css.matchAll(/#intro-hero[^{]*\{[^}]{0,400}\}/g)].slice(0, 5));
