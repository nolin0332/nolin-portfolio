import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const fontsDir = path.join(ROOT, 'public/assets/fonts');
const extractDir = path.join(fontsDir, 'aptos-extract');

const FONT_FILES = {
  body: 'Aptos.ttf',
  medium: 'Aptos-Medium.ttf',
  semibold: 'Aptos-SemiBold.ttf',
  bold: 'Aptos-Bold.ttf',
};

function findFontTtf(dir, fileName) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      const found = findFontTtf(full, fileName);
      if (found) return found;
    } else if (entry.name.toLowerCase() === fileName.toLowerCase()) {
      return full;
    }
  }
  return null;
}

async function ensureExtracted() {
  fs.mkdirSync(fontsDir, { recursive: true });
  const zipPath = path.join(fontsDir, 'Microsoft-Aptos-Fonts.zip');

  if (!fs.existsSync(extractDir) || fs.readdirSync(extractDir).length === 0) {
    const zipUrl =
      'https://download.microsoft.com/download/8/6/0/860a94fa-7feb-44ef-ac79-c072d9113d69/Microsoft%20Aptos%20Fonts.zip';
    console.log('Downloading', zipUrl);
    const zipRes = await fetch(zipUrl);
    if (!zipRes.ok) {
      throw new Error(`Download failed: ${zipRes.status}`);
    }
    fs.writeFileSync(zipPath, Buffer.from(await zipRes.arrayBuffer()));
    fs.mkdirSync(extractDir, { recursive: true });
    execSync(
      `powershell -NoProfile -Command "Expand-Archive -Path '${zipPath.replace(/'/g, "''")}' -DestinationPath '${extractDir.replace(/'/g, "''")}' -Force"`,
      { stdio: 'inherit' },
    );
  }
}

async function copyFont(variant) {
  const fileName = FONT_FILES[variant];
  const outTtf = path.join(fontsDir, fileName);
  if (fs.existsSync(outTtf)) {
    console.log(`${fileName} already exists:`, outTtf);
    return outTtf;
  }

  await ensureExtracted();
  const source = findFontTtf(extractDir, fileName);
  if (!source) {
    throw new Error(`${fileName} not found inside Aptos font package`);
  }
  fs.copyFileSync(source, outTtf);
  console.log('Saved', outTtf);
  return outTtf;
}

const variant = process.argv[2] || 'bold';
if (!FONT_FILES[variant]) {
  console.error('Usage: node scripts/download-aptos-font.mjs [body|medium|semibold|bold]');
  process.exit(1);
}

await copyFont(variant);
