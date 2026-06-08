import fs from 'fs';
const css = fs.readFileSync('public/_astro/index.Ew-YyTBx.css', 'utf8');
const urls = [...css.matchAll(/url\(([^)]+)\)/g)].map((m) => m[1].replace(/["']/g, '').trim());
console.log([...new Set(urls)].join('\n'));
