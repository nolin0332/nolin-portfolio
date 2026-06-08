import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import * as THREE from 'three';
import { FontLoader } from 'three/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import {
  buildAttributeMeta,
  readBuf,
  writeBuf,
} from './lib/buf-format.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const LOGO_DIR = path.join(ROOT, 'public/assets/models/logo');
const BACKUP_DIR = path.join(LOGO_DIR, 'julio-backup');

// Match reference: capital M + lowercase, Aptos SemiBold (lighter than Bold).
const NAME = 'Michael';
const LETTER_SPACING = 0.1;
const FONT_SIZE = 1.25;
const TARGET = {
  height: 0.305,
  depth: 0.045,
};

const fontPath = path.join(
  ROOT,
  'scripts/fonts/Aptos-SemiBold.typeface.json',
);
const font = new FontLoader().parse(JSON.parse(fs.readFileSync(fontPath, 'utf8')));

function createLetterGeometry(letter, options) {
  const geometry = new TextGeometry(letter, options);
  geometry.computeVertexNormals();
  return geometry;
}

function mergeLetterGeometries(letters, options) {
  const parts = [];
  let xCursor = 0;
  const spacing = options.letterSpacing ?? 0.015;

  for (let letterIndex = 0; letterIndex < letters.length; letterIndex++) {
    const geometry = createLetterGeometry(letters[letterIndex], options);
    geometry.computeBoundingBox();
    const box = geometry.boundingBox;
    const width = box.max.x - box.min.x;
    geometry.translate(xCursor - box.min.x, -box.min.y, -box.min.z);

    const count = geometry.getAttribute('position').count;
    geometry.setAttribute(
      'letter',
      new THREE.Float32BufferAttribute(new Float32Array(count).fill(letterIndex), 1),
    );

    const pos = geometry.getAttribute('position');
    let cx = 0;
    let cy = 0;
    let cz = 0;
    for (let i = 0; i < count; i++) {
      cx += pos.getX(i);
      cy += pos.getY(i);
      cz += pos.getZ(i);
    }
    cx /= count;
    cy /= count;
    cz /= count;

    const centroidArr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      centroidArr[i * 3] = cx;
      centroidArr[i * 3 + 1] = cy;
      centroidArr[i * 3 + 2] = cz;
    }
    geometry.setAttribute('centroid', new THREE.Float32BufferAttribute(centroidArr, 3));

    parts.push(ensureIndexed(geometry));
    xCursor += width + spacing;
  }

  const geometry = mergeGeometries(parts, false);
  if (!geometry) {
    throw new Error('Failed to merge letter geometries — check attribute compatibility');
  }
  parts.forEach((part) => part.dispose());
  return ensureIndexed(geometry);
}

function fitGeometryToTarget(geometry) {
  geometry.computeBoundingBox();
  const box = geometry.boundingBox;
  const size = new THREE.Vector3();
  box.getSize(size);
  const center = new THREE.Vector3();
  box.getCenter(center);

  geometry.translate(-center.x, -center.y, 0);

  const scale = TARGET.height / size.y;
  geometry.scale(scale, scale, scale);

  geometry.computeBoundingBox();
  const zSize = geometry.boundingBox.max.z - geometry.boundingBox.min.z;
  if (zSize > 0) {
    geometry.scale(1, 1, TARGET.depth / zSize);
  }

  geometry.computeBoundingBox();
  const fitted = geometry.boundingBox;
  geometry.translate(0, -(fitted.min.y + fitted.max.y) * 0.5, -fitted.min.z);
  geometry.computeBoundingBox();
}

function ensureIndexed(geometry) {
  if (!geometry.getIndex()) {
    const count = geometry.getAttribute('position').count;
    const arr = new Uint32Array(count);
    for (let i = 0; i < count; i++) {
      arr[i] = i;
    }
    geometry.setIndex(new THREE.BufferAttribute(arr, 1));
  }
  return geometry;
}

function writeLogoBuf(outputName, geometry, templatePath, includeCentroid) {
  ensureIndexed(geometry);
  const template = readBuf(templatePath);
  const pos = geometry.getAttribute('position').array;
  const nor = geometry.getAttribute('normal').array;
  const uv = geometry.getAttribute('uv').array;
  const letter = geometry.getAttribute('letter').array;
  const centroid = includeCentroid ? geometry.getAttribute('centroid').array : null;
  const indices = geometry.index.array;

  const attributes = {
    position: Float32Array.from(pos),
    normal: Float32Array.from(nor),
    uv: Float32Array.from(uv),
    letter: Float32Array.from(letter),
    indices: Float32Array.from(indices),
  };
  if (includeCentroid) {
    attributes.centroid = Float32Array.from(centroid);
  }

  const meta = {
    vertexCount: pos.length / 3,
    indexCount: indices.length,
    attributes: template.meta.attributes.map((attr) =>
      buildAttributeMeta(attr.id, attributes[attr.id], attr),
    ),
    meshType: 'Mesh',
  };

  writeBuf(path.join(LOGO_DIR, outputName), meta, attributes);
}

function backupOriginals() {
  fs.mkdirSync(BACKUP_DIR, { recursive: true });
  for (const file of ['logo.buf', 'logo_shell.buf']) {
    const src = path.join(LOGO_DIR, file);
    const dest = path.join(BACKUP_DIR, file);
    if (fs.existsSync(src) && !fs.existsSync(dest)) {
      fs.copyFileSync(src, dest);
    }
  }
}

function main() {
  backupOriginals();

  const letters = [...NAME];
  const shellGeometry = mergeLetterGeometries(letters, {
    font,
    size: FONT_SIZE,
    depth: TARGET.depth,
    curveSegments: 10,
    bevelEnabled: true,
    bevelThickness: 0.012,
    bevelSize: 0.008,
    bevelSegments: 4,
    letterSpacing: LETTER_SPACING,
  });
  fitGeometryToTarget(shellGeometry);

  const innerGeometry = mergeLetterGeometries(letters, {
    font,
    size: FONT_SIZE,
    depth: TARGET.depth,
    curveSegments: 4,
    bevelEnabled: true,
    bevelThickness: 0.012,
    bevelSize: 0.008,
    bevelSegments: 2,
    letterSpacing: LETTER_SPACING,
  });
  fitGeometryToTarget(innerGeometry);

  writeLogoBuf(
    'logo_shell.buf',
    shellGeometry,
    path.join(BACKUP_DIR, 'logo_shell.buf'),
    true,
  );
  writeLogoBuf(
    'logo.buf',
    innerGeometry,
    path.join(BACKUP_DIR, 'logo.buf'),
    false,
  );

  shellGeometry.computeBoundingBox();
  innerGeometry.computeBoundingBox();

  console.log('Generated Michael logo buffers:');
  console.log('  name:', NAME);
  console.log(
    '  logo_shell.buf',
    shellGeometry.getAttribute('position').count,
    'vertices,',
    shellGeometry.index.count,
    'indices',
  );
  console.log(
    '  logo.buf',
    innerGeometry.getAttribute('position').count,
    'vertices,',
    innerGeometry.index.count,
    'indices',
  );
  console.log('  shell bounds', shellGeometry.boundingBox);
  console.log('  inner bounds', innerGeometry.boundingBox);
  console.log('Original Julio files backed up to', BACKUP_DIR);
}

main();
