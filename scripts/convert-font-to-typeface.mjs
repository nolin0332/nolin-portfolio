import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { TTFLoader } from 'three/examples/jsm/loaders/TTFLoader.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

const variant = process.argv[2] || 'semibold';
const sources = {
  body: {
    ttf: path.join(ROOT, 'public/assets/fonts/Aptos.ttf'),
    out: path.join(ROOT, 'scripts/fonts/Aptos.typeface.json'),
  },
  medium: {
    ttf: path.join(ROOT, 'public/assets/fonts/Aptos-Medium.ttf'),
    out: path.join(ROOT, 'scripts/fonts/Aptos-Medium.typeface.json'),
  },
  semibold: {
    ttf: path.join(ROOT, 'public/assets/fonts/Aptos-SemiBold.ttf'),
    out: path.join(ROOT, 'scripts/fonts/Aptos-SemiBold.typeface.json'),
  },
  bold: {
    ttf: path.join(ROOT, 'public/assets/fonts/Aptos-Bold.ttf'),
    out: path.join(ROOT, 'scripts/fonts/Aptos-Bold.typeface.json'),
  },
};

const source = sources[variant];
if (!source) {
  console.error('Usage: node scripts/convert-font-to-typeface.mjs [body|medium|semibold|bold]');
  process.exit(1);
}

if (!fs.existsSync(source.ttf)) {
  console.error('Missing font file:', source.ttf);
  console.error(`Run: node scripts/download-aptos-font.mjs ${variant}`);
  process.exit(1);
}

const loader = new TTFLoader();
const json = loader.parse(fs.readFileSync(source.ttf).buffer);
fs.mkdirSync(path.dirname(source.out), { recursive: true });
fs.writeFileSync(source.out, JSON.stringify(json));
console.log('Wrote', source.out, `(${(fs.statSync(source.out).size / 1024).toFixed(1)} KB)`);
