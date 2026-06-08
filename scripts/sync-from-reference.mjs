import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const REF = 'https://julio-modern.vercel.app/';

async function main() {
  const res = await fetch(REF);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const ref = await res.text();
  fs.writeFileSync(path.join(root, 'public/index.reference.html'), ref);

  let local = fs.readFileSync(path.join(root, 'public/index.html'), 'utf8');

  // Strip local-only additions that break the intro hero flow
  local = local.replace(
    /<script>\s*\(function \(\) \{\s*if \(/SKIP_ANIMATION[\s\S]*?\}\)\(\);\s*<\/script>\s*/i,
    '',
  );
  local = local.replace(/<script src="boot-fix\.js" defer><\/script>/, '');
  local = local.replace(
    /body\.boot-force-enter[^}]*\}body\.boot-force-enter[^}]*\}body\.boot-force-enter[^}]*\}/,
    '',
  );

  // Remove section-stepper DOM block
  local = local.replace(/<div id="section-stepper">[\s\S]*?<\/div>\s*(?=<div id="|$)/i, '');

  // Remove section-stepper CSS chunks (multiple rules scattered in overrides)
  local = local.replace(/#section-stepper[^}]*\}/g, '');
  local = local.replace(/body\.experience-started #section-stepper[^}]*\}/g, '');
  local = local.replace(/#nav-step-next[^}]*\}/g, '');
  local = local.replace(/#nav-step-prev[^}]*\}/g, '');
  local = local.replace(/\/\*STEP-DIS\*\/[^]*?(?=\/\*SND-AL\*\/)/, '/*SND-AL*/');

  // Pull julio-overrides style from reference if present
  const refStyle = ref.match(/<style>\/\* julio-overrides \*\/[\s\S]*?<\/style>/i);
  const localStyle = local.match(/<style>\/\* julio-overrides \*\/[\s\S]*?<\/style>/i);
  if (refStyle && localStyle) {
    let cleanRefStyle = refStyle[0];
    cleanRefStyle = cleanRefStyle.replace(/#section-stepper[^}]*\}/g, '');
    cleanRefStyle = cleanRefStyle.replace(/body\.experience-started #section-stepper[^}]*\}/g, '');
    cleanRefStyle = cleanRefStyle.replace(/#nav-step-next[^}]*\}/g, '');
    cleanRefStyle = cleanRefStyle.replace(/#nav-step-prev[^}]*\}/g, '');
    cleanRefStyle = cleanRefStyle.replace(/\/\*STEP-DIS\*\/[\s\S]*?(?=\/\*SND-AL\*\/|$)/, '');
    local = local.replace(localStyle[0], cleanRefStyle);
  }

  fs.writeFileSync(path.join(root, 'public/index.html'), local);
  console.log('Synced index.html');
  console.log('reference has section-stepper:', ref.includes('section-stepper'));
  console.log('local has section-stepper:', local.includes('section-stepper'));
  console.log('local has boot-fix:', local.includes('boot-fix'));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
