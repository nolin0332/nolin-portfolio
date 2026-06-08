import fs from 'fs';

function analyze(path) {
  const h = fs.readFileSync(path, 'utf8');
  const openDiv = (h.match(/<div[\s>]/g) || []).length;
  const closeDiv = (h.match(/<\/div>/g) || []).length;
  const storyFeatures = (h.match(/class="story-feature"/g) || []).length;
  const ids = [...h.matchAll(/\bid="(story-[^"]+)"/g)].map((m) => m[1]);
  const battle = h.match(/id="story-airdrops-post-battlepass"[\s\S]{0,2500}/)?.[0] || '';
  const skillsClose = (battle.match(/<\/div>/g) || []).length;
  return { path, len: h.length, openDiv, closeDiv, diff: openDiv - closeDiv, storyFeatures, ids: ids.length, battleSnippet: battle.slice(-400) };
}

for (const p of ['public/index.html', 'public/index.reference.html']) {
  const r = analyze(p);
  console.log(JSON.stringify(r, null, 2).slice(0, 2000));
  console.log('---');
}
