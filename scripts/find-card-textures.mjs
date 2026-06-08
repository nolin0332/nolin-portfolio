import fs from 'fs';
const js = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const idx = js.indexOf('StoryAirdropPreEngagementVisual');
console.log(js.slice(idx, idx + 3500));
