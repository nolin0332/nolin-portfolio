import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const res = await fetch('https://julio-modern.vercel.app/');
const ref = await res.text();
let local = fs.readFileSync(path.join(root, 'public/index.html'), 'utf8');

// Restore stepper HTML from reference (only if missing)
if (!local.includes('id="section-stepper"')) {
  const m = ref.match(/<div id="section-stepper">[\s\S]*?<\/div>\s*(?=<div id="sound">)/);
  if (m) {
    local = local.replace(/<div id="sound">/, m[0] + '<div id="sound">');
    console.log('Restored section-stepper HTML');
  }
}

// Remove permanent hide-all rule we added; use reference visibility pattern
local = local.replace(
  /#section-stepper,#nav-step-prev,#nav-step-next\{display:none!important;visibility:hidden!important;\}/,
  '',
);

if (!local.includes('body.experience-started #section-stepper{visibility:visible')) {
  const visRule =
    '#section-stepper{visibility:hidden;}body.experience-started #section-stepper{visibility:visible;}';
  local = local.replace('/* julio-overrides */', `/* julio-overrides */${visRule}`);
  console.log('Restored stepper visibility CSS');
}

fs.writeFileSync(path.join(root, 'public/index.html'), local);
console.log('has stepper div', local.includes('id="section-stepper"'));
