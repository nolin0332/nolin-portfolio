import fs from 'fs';
const css = fs.readFileSync('public/_astro/index.Ew-YyTBx.css', 'utf8');
const key = 'story-gamification-leaderboard-card';
let i = 0;
while ((i = css.indexOf(key, i)) >= 0) {
  console.log(css.slice(i, i + 180));
  i++;
}
