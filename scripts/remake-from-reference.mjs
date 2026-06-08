/**
 * Remake public/ to match https://julio-modern.vercel.app/
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const publicDir = path.join(root, 'public');
const REF = 'https://julio-modern.vercel.app/';

async function fetchText(url) {
  const res = await fetch(url, { signal: AbortSignal.timeout(120000) });
  if (!res.ok) throw new Error(`${url} → HTTP ${res.status}`);
  return await res.text();
}

async function fetchFile(url, out) {
  const res = await fetch(url, { signal: AbortSignal.timeout(120000) });
  if (!res.ok) throw new Error(`${url} → HTTP ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, buf);
  return buf.length;
}

function runNode(script) {
  return new Promise((resolve, reject) => {
    const p = spawn(process.execPath, [path.join(root, 'scripts', script)], {
      cwd: root,
      stdio: 'inherit',
    });
    p.on('exit', (code) => (code === 0 ? resolve() : reject(new Error(`${script} exit ${code}`))));
  });
}

console.log('Fetching live index.html from julio-modern.vercel.app …');
const indexHtml = await fetchText(REF);
fs.writeFileSync(path.join(publicDir, 'index.html'), indexHtml);
fs.writeFileSync(path.join(publicDir, 'index.reference.html'), indexHtml);
console.log('Wrote index.html', indexHtml.length, 'bytes');

// Sync core bundles
const hoisted = '_astro/hoisted.jm-mpcuc8bi.js';
const css = '_astro/index.Ew-YyTBx.css';
for (const rel of [hoisted, css]) {
  const n = await fetchFile(`${REF}${rel}`, path.join(publicDir, rel));
  console.log('Synced', rel, n, 'bytes');
}

// Remove boot-fix (not on reference site)
const bootFix = path.join(publicDir, 'boot-fix.js');
if (fs.existsSync(bootFix)) {
  fs.unlinkSync(bootFix);
  console.log('Removed boot-fix.js');
}

console.log('\nDownloading all assets (models, textures, audio, fonts) …');
await runNode('download-canonical.mjs');
await runNode('download-sounds.mjs');
try {
  await runNode('download-remaining.mjs');
} catch {
  console.warn('download-remaining.mjs had issues (optional)');
}

// Required by StoryAirdropPreEngagement (loader stalls ~41% without these)
const popupCards = ['like', 'comment', 'repost', 'follow'];
for (const id of popupCards) {
  const rel = `assets/textures/storyAirdropPreEngagement/card-${id}.jpg`;
  const n = await fetchFile(`${REF}${rel}`, path.join(publicDir, rel));
  console.log('Synced', rel, n, 'bytes');
}

await runNode('verify-complete.mjs');
console.log('\nRemake complete. Run: npm run dev');
