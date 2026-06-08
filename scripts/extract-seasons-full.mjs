import fs from 'fs';

function sectionSlice(h, sectionId) {
  const marker = `id="${sectionId}"`;
  const start = h.indexOf(marker);
  if (start < 0) return '';
  const childPrefix = `${sectionId}-`;
  let pos = start + marker.length;
  let end = Math.min(h.length, start + 15000);
  while (true) {
    const nextStory = h.indexOf('id="story-', pos);
    if (nextStory < 0) break;
    const idEnd = h.indexOf('"', nextStory + 4);
    const nextId = h.slice(nextStory + 4, idEnd);
    if (nextId !== sectionId && !nextId.startsWith(childPrefix)) {
      end = nextStory;
      break;
    }
    pos = nextStory + 10;
  }
  return h.slice(start, end);
}

const ref = fs.readFileSync('public/index.reference.html', 'utf8');
console.log(sectionSlice(ref, 'story-airdrops-post-seasons'));
