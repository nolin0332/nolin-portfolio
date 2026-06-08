import fs from 'fs';
const j = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
const i = j.indexOf('class StoryGamificationQuestsVisual');
console.log(j.slice(i, i + 5500));
