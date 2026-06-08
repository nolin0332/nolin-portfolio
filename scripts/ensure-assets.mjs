import { existsSync, statSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const marker = join(root, 'public/assets/textures/LDR_RGB1_0.png');
const logoMarker = join(root, 'public/assets/logos/companies/cu-boulder.png');

function ok(path) {
  return existsSync(path) && statSync(path).size > 1000;
}

if (!ok(logoMarker)) {
  console.log('Company logos missing — running fetch-company-logos.py …');
  const logoRun = spawnSync('python', ['scripts/fetch-company-logos.py'], {
    cwd: root,
    stdio: 'inherit',
    shell: true,
  });
  if (logoRun.status !== 0) {
    process.exit(logoRun.status ?? 1);
  }
}

if (!ok(marker)) {
  console.log('3D assets missing — running npm run sync-assets …');
  const r = spawnSync('npm', ['run', 'sync-assets'], {
    cwd: root,
    stdio: 'inherit',
    shell: true,
  });
  if (r.status !== 0) {
    process.exit(r.status ?? 1);
  }
}
