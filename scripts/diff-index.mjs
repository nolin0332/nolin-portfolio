import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const ref = fs.readFileSync(path.join(root, 'public/index.reference.html'), 'utf8');
const local = fs.readFileSync(path.join(root, 'public/index.html'), 'utf8');

console.log('sizes ref', ref.length, 'local', local.length);

const keys = [
  'boot-fix',
  'SKIP_ANIMATION',
  'section-stepper',
  'intro-hero-title',
  'julio-overrides',
  'jl-hint',
  'DOMContentLoaded',
  'nav-step',
];
for (const k of keys) {
  console.log(k, 'ref', ref.includes(k), 'local', local.includes(k));
}

// Find inline scripts only in local
const localScripts = local.match(/<script>[\s\S]*?<\/script>/g) || [];
const refScripts = ref.match(/<script>[\s\S]*?<\/script>/g) || [];
console.log('script blocks ref', refScripts.length, 'local', localScripts.length);
