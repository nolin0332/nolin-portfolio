import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const REF = 'https://julio-modern.vercel.app/';

const res = await fetch(REF);
const ref = await res.text();
const local = fs.readFileSync(path.join(root, 'public/index.html'), 'utf8');

const refHoisted = ref.match(/hoisted\.[a-z0-9-]+\.js/)?.[0];
const localHoisted = local.match(/hoisted\.[a-z0-9-]+\.js/)?.[0];
const refCss = ref.match(/index\.[a-zA-Z0-9_-]+\.css/)?.[0];
const localCss = local.match(/index\.[a-zA-Z0-9_-]+\.css/)?.[0];

console.log('hoisted ref:', refHoisted, 'local:', localHoisted, 'match:', refHoisted === localHoisted);
console.log('css ref:', refCss, 'local:', localCss, 'match:', refCss === localCss);
console.log('boot-fix local:', local.includes('boot-fix'));
console.log('SKIP_ANIMATION in local URL scripts:', /SKIP_ANIMATION/.test(local));

// Extract script tags from ref
const scripts = [...ref.matchAll(/<script[^>]*src="([^"]+)"[^>]*>/g)].map((m) => m[1]);
console.log('ref scripts:', scripts);

// Check preloader markup
const refPre = ref.match(/<div id="preloader">[\s\S]*?<\/div>/)?.[0]?.slice(0, 300);
const localPre = local.match(/<div id="preloader">[\s\S]*?<\/div>/)?.[0]?.slice(0, 300);
console.log('\nref preloader:', refPre);
console.log('\nlocal preloader:', localPre);

// LOGO in ref html?
console.log('\nLOGO in ref html:', ref.includes('LOGO'));

fs.writeFileSync(path.join(root, 'public/index.reference.html'), ref);
console.log('\nWrote public/index.reference.html', ref.length, 'bytes');
