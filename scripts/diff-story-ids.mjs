import fs from 'fs';

function extract(path, sid) {
  const h = fs.readFileSync(path, 'utf8');
  const start = h.indexOf(`id="${sid}"`);
  const next = h.indexOf('id="story-', start + 10);
  return h.slice(start, next > start ? next : start + 4000);
}

for (const sid of ['story-airdrops-post-battlepass', 'story-airdrops-post-seasons']) {
  console.log('\n=== REF', sid, '===');
  console.log(extract('public/index.reference.html', sid));
}
