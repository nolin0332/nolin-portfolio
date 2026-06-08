import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const indexPath = path.join(root, 'public/index.html');
let html = fs.readFileSync(indexPath, 'utf8');

// Remove local-only boot redirect
html = html.replace(
  /<script>\s*\(function \(\) \{[\s\S]*?SKIP_ANIMATION[\s\S]*?\}\)\(\);\s*<\/script>\s*/i,
  '',
);
html = html.replace(/<script src="boot-fix\.js" defer><\/script>/, '');

// Remove custom PREV/NEXT stepper (not on julio-modern.vercel.app)
html = html.replace(
  /<div id="section-stepper">[\s\S]*?<\/div>\s*(?=<div id="sound">)/,
  '',
);

// Remove boot-force-enter overrides
html = html.replace(
  /body\.boot-force-enter #preloader\{[^}]*\}body\.boot-force-enter #ui\.is-hidden\{[^}]*\}body\.boot-force-enter #footer-hero-button\{[^}]*\}/,
  '',
);

// Remove all section-stepper / nav-step CSS blocks from julio-overrides
const cssChunks = [
  /#section-stepper\{[^}]*\}/g,
  /#section-stepper [^{]*\{[^}]*\}/g,
  /@media \(max-aspect-ratio: 1 \/ 1\)\{#section-stepper[^}]*\}/g,
  /body\.experience-started #section-stepper\{[^}]*\}/g,
  /#nav-step-next\{[^}]*\}/g,
  /#nav-step-prev\{[^}]*\}/g,
  /\/\*STEP-DIS\*\/#section-stepper[^]*?(?=\/\*SND-AL\*\/)/,
];
for (const re of cssChunks) {
  html = html.replace(re, '');
}

// Ensure stepper never appears if any fragment remains
if (!html.includes('#section-stepper{display:none')) {
  html = html.replace(
    '/* julio-overrides */',
    '/* julio-overrides */#section-stepper,#nav-step-prev,#nav-step-next{display:none!important;visibility:hidden!important;}',
  );
}

fs.writeFileSync(indexPath, html);
console.log('Fixed index.html');
console.log('section-stepper present:', html.includes('id="section-stepper"'));
console.log('boot-fix present:', html.includes('boot-fix'));
