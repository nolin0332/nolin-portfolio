import fs from 'fs';
const j = fs.readFileSync('public/_astro/hoisted.jm-mpcuc8bi.js', 'utf8');
for (const name of ['StoryRewardsCashbackVisual', 'StoryAirdropPreEngagementVisual']) {
  const i = j.indexOf(`class ${name}`);
  console.log('\n===', name, '===\n', j.slice(i, i + 3500));
}
